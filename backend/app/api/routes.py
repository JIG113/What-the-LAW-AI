import hashlib
from datetime import datetime, UTC
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.entities import AnalysisRun, Document, ExtractedItem, ItemEvidence, UserEdit
from app.schemas.api import (
    AnalysisRunResponse,
    AnalyzeRequest,
    ItemEditRequest,
    OpenTargetResponse,
    SearchResponse,
)
from app.services.pipeline import execute_analysis
from app.services.search import hybrid_search_chunks

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def _save_single_file(project_id: str, file: UploadFile, session: Session):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    exists = session.exec(select(Document).where(Document.file_hash == file_hash, Document.project_id == project_id)).first()
    if exists:
        return {"document_id": exists.id, "status": "duplicate", "file_hash": file_hash, "file_name": file.filename}

    saved_path = UPLOAD_DIR / f"{datetime.now(UTC).timestamp()}_{file.filename}"
    saved_path.write_bytes(content)

    doc = Document(
        project_id=project_id,
        file_name=file.filename,
        file_type=(file.filename.split(".")[-1] if "." in file.filename else "unknown"),
        storage_path=str(saved_path),
        file_hash=file_hash,
        parse_status="uploaded",
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return {"document_id": doc.id, "status": doc.parse_status, "file_hash": file_hash, "file_name": file.filename}


@router.post("/documents/upload")
async def upload_document(project_id: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    return await _save_single_file(project_id, file, session)


@router.post("/documents/upload-batch")
async def upload_documents_batch(project_id: str, files: list[UploadFile] = File(...), session: Session = Depends(get_session)):
    results = []
    for f in files:
        results.append(await _save_single_file(project_id, f, session))
    return {"count": len(results), "results": results}


@router.post("/analysis/run", response_model=AnalysisRunResponse)
def run_analysis(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    doc = session.get(Document, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    run = AnalysisRun(document_id=doc.id, status="queued")
    session.add(run)
    session.commit()
    session.refresh(run)

    run = execute_analysis(session, doc, run)
    return AnalysisRunResponse(**run.model_dump())


@router.get("/analysis/runs/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: int, session: Session = Depends(get_session)):
    run = session.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return AnalysisRunResponse(**run.model_dump())


@router.get("/analysis/items")
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


@router.get("/evidences/open-target", response_model=OpenTargetResponse)
def open_target(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ExtractedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    evidence = session.exec(select(ItemEvidence).where(ItemEvidence.extracted_item_id == item.id)).first()
    if evidence:
        return OpenTargetResponse(document_id=item.document_id, page=evidence.page_no, snippet=evidence.snippet_text)
    return OpenTargetResponse(document_id=item.document_id, page=1, snippet=item.item_value)
