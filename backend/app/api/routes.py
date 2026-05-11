import hashlib
from datetime import datetime, UTC
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session as SQLSession
from sqlmodel import Session, select

from app.core.db import engine, get_session
from app.models.entities import AnalysisEvent, AnalysisRun, Document, ExtractedItem, ItemEvidence, RuleProfile, UserEdit, ValidationIssue
from app.schemas.api import (
    AnalysisRunResponse,
    AnalyzeRequest,
    ItemEditRequest,
    OpenTargetResponse,
    SearchResponse,
    RunListResponse,
    AnalysisEventResponse,
    RunEventListResponse,
    ValidationIssueListResponse,
    ValidationIssueResponse,
    RuleProfileListResponse,
    RuleProfileResponse,
)
from app.services.job_runner import executor, futures
from app.services.pipeline import execute_analysis
from app.services.search import hybrid_search_chunks

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx", "txt"}


def _to_run_response(run: AnalysisRun) -> AnalysisRunResponse:
    return AnalysisRunResponse(
        id=run.id,
        document_id=run.document_id,
        status=run.status,
        pages=run.pages,
        chunks=run.chunks,
        items_created=run.items_created,
        evidences_created=run.evidences_created,
        error_message=run.error_message,
    )


def _run_analysis_task(document_id: int, run_id: int):
    with SQLSession(engine) as bg_session:
        doc = bg_session.get(Document, document_id)
        run = bg_session.get(AnalysisRun, run_id)
        if not doc or not run:
            return
        execute_analysis(bg_session, doc, run)


async def _save_single_file(project_id: str, file: UploadFile, session: Session, rule_profile: str = "default"):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_ext = (file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "unknown")

    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: .{file_ext}. 지원 형식: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    exists = session.exec(select(Document).where(Document.file_hash == file_hash, Document.project_id == project_id)).first()
    if exists:
        return {"document_id": exists.id, "status": "duplicate", "file_hash": file_hash, "file_name": file.filename}

    saved_path = UPLOAD_DIR / f"{datetime.now(UTC).timestamp()}_{file.filename}"
    saved_path.write_bytes(content)

    doc = Document(
        project_id=project_id,
        file_name=file.filename,
        file_type=file_ext,
        storage_path=str(saved_path),
        file_hash=file_hash,
        parse_status="uploaded",
        rule_profile=rule_profile,
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return {"document_id": doc.id, "status": doc.parse_status, "file_hash": file_hash, "file_name": file.filename}




def _to_rule_profile_response(p: RuleProfile) -> RuleProfileResponse:
    return RuleProfileResponse(id=p.id, name=p.name, percent_upper_bound=p.percent_upper_bound, enabled=p.enabled)


@router.get("/rule-profiles", response_model=RuleProfileListResponse)
def list_rule_profiles(session: Session = Depends(get_session)):
    rows = session.exec(select(RuleProfile)).all()
    rows = sorted(rows, key=lambda r: r.id)
    return RuleProfileListResponse(total=len(rows), items=[_to_rule_profile_response(r) for r in rows])


@router.post("/rule-profiles", response_model=RuleProfileResponse)
def create_rule_profile(name: str, percent_upper_bound: float = 1000.0, enabled: bool = True, session: Session = Depends(get_session)):
    exists = session.exec(select(RuleProfile).where(RuleProfile.name == name)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Rule profile already exists")
    rp = RuleProfile(name=name, percent_upper_bound=percent_upper_bound, enabled=enabled)
    session.add(rp)
    session.commit()
    session.refresh(rp)
    return _to_rule_profile_response(rp)


@router.patch("/rule-profiles/{name}", response_model=RuleProfileResponse)
def update_rule_profile(name: str, percent_upper_bound: float | None = None, enabled: bool | None = None, session: Session = Depends(get_session)):
    rp = session.exec(select(RuleProfile).where(RuleProfile.name == name)).first()
    if not rp:
        raise HTTPException(status_code=404, detail="Rule profile not found")
    if percent_upper_bound is not None:
        rp.percent_upper_bound = percent_upper_bound
    if enabled is not None:
        rp.enabled = enabled
    session.add(rp)
    session.commit()
    session.refresh(rp)
    return _to_rule_profile_response(rp)


@router.post("/documents/upload", summary="문서 업로드", description="분석할 문서 1개를 업로드합니다.")
async def upload_document(project_id: str, rule_profile: str = "default", file: UploadFile = File(...), session: Session = Depends(get_session)):
    return await _save_single_file(project_id, file, session, rule_profile=rule_profile)


@router.post("/documents/upload-batch", summary="문서 일괄 업로드", description="분석할 문서 여러 개를 한 번에 업로드합니다.")
async def upload_documents_batch(project_id: str, rule_profile: str = "default", files: list[UploadFile] = File(...), session: Session = Depends(get_session)):
    results = []
    for f in files:
        results.append(await _save_single_file(project_id, f, session, rule_profile=rule_profile))
    return {"count": len(results), "results": results}




@router.patch("/documents/{document_id}/rule-profile")
def update_document_rule_profile(document_id: int, rule_profile: str, session: Session = Depends(get_session)):
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.rule_profile = rule_profile
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return {"document_id": doc.id, "rule_profile": doc.rule_profile}

@router.post("/analysis/run-async", response_model=AnalysisRunResponse, summary="분석 실행(백그라운드)")
def run_analysis_async(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    doc = session.get(Document, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    run = AnalysisRun(document_id=doc.id, status="queued")
    session.add(run)
    session.commit()
    session.refresh(run)

    futures[run.id] = executor.submit(_run_analysis_task, doc.id, run.id)
    return _to_run_response(run)


@router.post("/analysis/run", response_model=AnalysisRunResponse, summary="분석 실행")
def run_analysis(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    doc = session.get(Document, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    run = AnalysisRun(document_id=doc.id, status="queued")
    session.add(run)
    session.commit()
    session.refresh(run)

    run = execute_analysis(session, doc, run)
    return _to_run_response(run)




@router.post("/analysis/runs/{run_id}/cancel", response_model=AnalysisRunResponse)
def cancel_analysis_run(run_id: int, session: Session = Depends(get_session)):
    run = session.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status in {"completed", "failed", "cancelled"}:
        return _to_run_response(run)

    run.cancel_requested = True
    run.status = "cancelling"
    session.add(run)
    session.commit()
    session.refresh(run)

    future = futures.get(run.id)
    if future and future.cancel():
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
        run.cancelled_at = datetime.now(UTC)
        session.add(run)
        session.commit()
        session.refresh(run)

    return _to_run_response(run)


@router.post("/analysis/runs/{run_id}/retry", response_model=AnalysisRunResponse)
def retry_analysis_run(run_id: int, session: Session = Depends(get_session)):
    prev = session.get(AnalysisRun, run_id)
    if not prev:
        raise HTTPException(status_code=404, detail="Run not found")

    doc = session.get(Document, prev.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    run = AnalysisRun(document_id=doc.id, status="queued")
    session.add(run)
    session.commit()
    session.refresh(run)

    futures[run.id] = executor.submit(_run_analysis_task, doc.id, run.id)
    return _to_run_response(run)



@router.get("/analysis/runs", response_model=RunListResponse)
def list_analysis_runs(document_id: int | None = None, offset: int = 0, limit: int = 20, session: Session = Depends(get_session)):
    query = select(AnalysisRun)
    if document_id is not None:
        query = query.where(AnalysisRun.document_id == document_id)

    rows = session.exec(query).all()
    rows = sorted(rows, key=lambda r: r.id, reverse=True)
    sliced = rows[offset: offset + limit]
    return RunListResponse(total=len(rows), items=[_to_run_response(r) for r in sliced])

@router.get("/analysis/runs/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: int, session: Session = Depends(get_session)):
    run = session.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _to_run_response(run)




@router.get("/analysis/runs/{run_id}/events", response_model=RunEventListResponse)
def list_run_events(run_id: int, offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    run = session.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rows = session.exec(select(AnalysisEvent).where(AnalysisEvent.run_id == run_id)).all()
    rows = sorted(rows, key=lambda r: r.id)
    sliced = rows[offset: offset + limit]
    return RunEventListResponse(total=len(rows), items=[AnalysisEventResponse(id=r.id, run_id=r.run_id, level=r.level, step=r.step, message=r.message) for r in sliced])



@router.get("/analysis/runs/{run_id}/validation-issues", response_model=ValidationIssueListResponse)
def list_validation_issues(run_id: int, offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    run = session.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rows = session.exec(select(ValidationIssue).where(ValidationIssue.run_id == run_id)).all()
    rows = sorted(rows, key=lambda r: r.id)
    sliced = rows[offset: offset + limit]
    return ValidationIssueListResponse(
        total=len(rows),
        items=[
            ValidationIssueResponse(
                id=r.id, run_id=r.run_id, item_id=r.item_id, rule_code=r.rule_code, severity=r.severity, message=r.message
            )
            for r in sliced
        ],
    )

@router.get("/analysis/items", summary="분석 결과 조회")
def list_items(document_id: int, category: str | None = None, session: Session = Depends(get_session)):
    query = select(ExtractedItem).where(ExtractedItem.document_id == document_id)
    if category:
        query = query.where(ExtractedItem.category == category)
    return session.exec(query).all()


@router.patch("/analysis/items/{item_id}")
def edit_item(item_id: int, payload: ItemEditRequest, session: Session = Depends(get_session)):
    item = session.get(ExtractedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    history = UserEdit(
        item_id=item.id,
        editor=payload.editor,
        old_category=item.category,
        new_category=payload.category,
        old_value=item.item_value,
        new_value=payload.item_value,
        reason=payload.reason,
    )
    item.category = payload.category
    item.item_value = payload.item_value

    session.add(history)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/analysis/items/{item_id}/history")
def item_edit_history(item_id: int, session: Session = Depends(get_session)):
    return session.exec(select(UserEdit).where(UserEdit.item_id == item_id)).all()


@router.get("/search/chunks", response_model=list[SearchResponse])
def search_chunks(document_id: int, q: str, limit: int = 20, session: Session = Depends(get_session)):
    rows = hybrid_search_chunks(session, document_id=document_id, query=q, limit=limit)
    return [
        SearchResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            page_start=chunk.page_start,
            keyword_score=keyword_score,
            vector_score=vector_score,
            hybrid_score=hybrid_score,
            snippet=chunk.chunk_text[:220],
        )
        for chunk, keyword_score, vector_score, hybrid_score in rows
    ]


@router.get("/evidences/open-target", response_model=OpenTargetResponse, summary="근거 원문 위치 열기")
def open_target(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ExtractedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    evidence = session.exec(select(ItemEvidence).where(ItemEvidence.extracted_item_id == item.id)).first()
    if evidence:
        return OpenTargetResponse(document_id=item.document_id, page=evidence.page_no, snippet=evidence.snippet_text)
    return OpenTargetResponse(document_id=item.document_id, page=1, snippet=item.item_value)
