from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.entities import Document, ExtractedItem
from app.schemas.api import AnalyzeRequest, OpenTargetResponse
from app.services.analyzer import run_stage1_analysis

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
    saved_path = UPLOAD_DIR / file.filename
    saved_path.write_bytes(content)

    doc = Document(
        project_id=project_id,
        file_name=file.filename,
        file_type=(file.filename.split(".")[-1] if "." in file.filename else "unknown"),
        storage_path=str(saved_path),
        parse_status="uploaded",
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return {"document_id": doc.id, "status": doc.parse_status}


@router.post("/analysis/run")
def run_analysis(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    doc = session.get(Document, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    items = run_stage1_analysis(doc)
    for item in items:
        session.add(item)
    session.commit()
    return {"document_id": doc.id, "items_created": len(items)}


@router.get("/analysis/items")
def list_items(document_id: int, category: str | None = None, session: Session = Depends(get_session)):
    query = select(ExtractedItem).where(ExtractedItem.document_id == document_id)
    if category:
        query = query.where(ExtractedItem.category == category)
    rows = session.exec(query).all()
    return rows


@router.get("/evidences/open-target", response_model=OpenTargetResponse)
def open_target(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ExtractedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return OpenTargetResponse(document_id=item.document_id, page=1, snippet=item.item_value)
