from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.entities import Chunk, Document, DocumentPage, ExtractedItem, ItemEvidence
from app.schemas.api import AnalysisRunResponse, AnalyzeRequest, OpenTargetResponse
from app.services.analyzer import extract_items_from_chunks
from app.services.chunking import chunk_pages
from app.services.ocr import run_ocr_if_needed
from app.services.parsing import parse_file

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


@router.post("/analysis/run", response_model=AnalysisRunResponse)
def run_analysis(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    doc = session.get(Document, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    pages = parse_file(doc.storage_path)

    page_rows: list[DocumentPage] = []
    page_payload_for_chunk: list[tuple[int, str]] = []
    for idx, page_text in enumerate(pages, start=1):
        merged, confidence = run_ocr_if_needed(page_text)
        row = DocumentPage(document_id=doc.id, page_no=idx, merged_text=merged, ocr_confidence=confidence)
        page_rows.append(row)
        page_payload_for_chunk.append((idx, merged))

    for row in page_rows:
        session.add(row)

    chunk_dicts = chunk_pages(page_payload_for_chunk)
    chunk_rows = [Chunk(document_id=doc.id, **chunk_data) for chunk_data in chunk_dicts]
    for chunk in chunk_rows:
        session.add(chunk)
    session.flush()

    items, evidences = extract_items_from_chunks(doc.id, chunk_rows)

    for item in items:
        session.add(item)
    session.flush()

    for idx, ev in enumerate(evidences):
        ev.extracted_item_id = items[idx].id
        session.add(ev)

    doc.parse_status = "parsed"
    doc.ocr_status = "done"
    doc.indexed_status = "done"

    session.add(doc)
    session.commit()

    return AnalysisRunResponse(
        document_id=doc.id,
        pages=len(page_rows),
        chunks=len(chunk_rows),
        items_created=len(items),
        evidences_created=len(evidences),
    )


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

    evidence = session.exec(
        select(ItemEvidence).where(ItemEvidence.extracted_item_id == item.id)
    ).first()
    if evidence:
        return OpenTargetResponse(document_id=item.document_id, page=evidence.page_no, snippet=evidence.snippet_text)

    return OpenTargetResponse(document_id=item.document_id, page=1, snippet=item.item_value)
