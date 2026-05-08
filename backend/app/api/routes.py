import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.entities import AnalysisRun, Document, ExtractedItem, ItemEvidence
from app.schemas.api import AnalysisRunResponse, AnalyzeRequest, OpenTargetResponse
from app.services.pipeline import execute_analysis

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/documents/upload")
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    exists = session.exec(select(Document).where(Document.file_hash == file_hash, Document.project_id == project_id)).first()
    if exists:
        return {"document_id": exists.id, "status": "duplicate", "file_hash": file_hash}

    saved_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{file.filename}"
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
    return {"document_id": doc.id, "status": doc.parse_status, "file_hash": file_hash}


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


@router.get("/evidences/open-target", response_model=OpenTargetResponse)
def open_target(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ExtractedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    evidence = session.exec(select(ItemEvidence).where(ItemEvidence.extracted_item_id == item.id)).first()
    if evidence:
        return OpenTargetResponse(document_id=item.document_id, page=evidence.page_no, snippet=evidence.snippet_text)
    return OpenTargetResponse(document_id=item.document_id, page=1, snippet=item.item_value)
