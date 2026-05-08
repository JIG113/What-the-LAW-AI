from datetime import datetime, UTC

from sqlmodel import Session, delete

from app.models.entities import AnalysisEvent, AnalysisRun, Chunk, Document, DocumentPage, ExtractedItem, ItemEvidence
from app.services.analyzer import extract_items_from_chunks
from app.services.chunking import chunk_pages
from app.services.embedding import dumps_embedding, embed_text
from app.services.ocr import run_ocr_if_needed
from app.services.parsing import parse_file




def _log_event(session: Session, run_id: int, step: str, message: str, level: str = "info") -> None:
    session.add(AnalysisEvent(run_id=run_id, level=level, step=step, message=message))
    session.commit()

def _check_cancel(session: Session, run: AnalysisRun) -> bool:
    session.refresh(run)
    if run.cancel_requested:
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
        run.cancelled_at = datetime.now(UTC)
        session.add(run)
        session.commit()
        return True
    return False


def execute_analysis(session: Session, doc: Document, run: AnalysisRun) -> AnalysisRun:
    try:
        run.status = "running"
        session.add(run)
        session.commit()
        _log_event(session, run.id, "start", "analysis started")

        if _check_cancel(session, run):
            return run

        bg_delete = [
            delete(DocumentPage).where(DocumentPage.document_id == doc.id),
            delete(Chunk).where(Chunk.document_id == doc.id),
            delete(ExtractedItem).where(ExtractedItem.document_id == doc.id),
            delete(ItemEvidence).where(ItemEvidence.document_id == doc.id),
        ]
        for stmt in bg_delete:
            session.exec(stmt)
        session.commit()
        _log_event(session, run.id, "cleanup", "previous artifacts cleared")

        pages = parse_file(doc.storage_path)
        _log_event(session, run.id, "parse", f"parsed pages={len(pages)}")
        if _check_cancel(session, run):
            return run
        page_rows: list[DocumentPage] = []
        page_payload_for_chunk: list[tuple[int, str]] = []
        for idx, page_text in enumerate(pages, start=1):
            merged, confidence = run_ocr_if_needed(page_text)
            page_rows.append(DocumentPage(document_id=doc.id, page_no=idx, merged_text=merged, ocr_confidence=confidence))
            page_payload_for_chunk.append((idx, merged))

        for row in page_rows:
            session.add(row)

        chunk_rows = []
        for c in chunk_pages(page_payload_for_chunk):
            embedding = dumps_embedding(embed_text(c["chunk_text"]))
            chunk_rows.append(Chunk(document_id=doc.id, embedding_json=embedding, **c))
        for c in chunk_rows:
            session.add(c)
        session.flush()
        _log_event(session, run.id, "chunk", f"chunks={len(chunk_rows)}")

        if _check_cancel(session, run):
            return run

        items, evidences = extract_items_from_chunks(doc.id, chunk_rows)
        for item in items:
            session.add(item)
        session.flush()
        _log_event(session, run.id, "extract", f"items={len(items)} evidences={len(evidences)}")

        for idx, ev in enumerate(evidences):
            ev.extracted_item_id = items[idx].id
            page_text = chunk_rows[idx].chunk_text if idx < len(chunk_rows) else ev.snippet_text
            start = page_text.find(ev.snippet_text)
            ev.char_start = max(0, start)
            ev.char_end = max(0, start + len(ev.snippet_text))
            session.add(ev)

        doc.parse_status = "parsed"
        doc.ocr_status = "done"
        doc.indexed_status = "done"

        run.status = "completed"
        run.pages = len(page_rows)
        run.chunks = len(chunk_rows)
        run.items_created = len(items)
        run.evidences_created = len(evidences)
        run.finished_at = datetime.now(UTC)

        session.add(doc)
        session.add(run)
        session.commit()
        session.refresh(run)
        _log_event(session, run.id, "complete", "analysis completed")
        return run
    except Exception as exc:  # noqa: BLE001
        run.status = "failed"
        run.error_message = str(exc)
        _log_event(session, run.id, "error", str(exc), level="error")
        run.finished_at = datetime.now(UTC)
        session.add(run)
        session.commit()
        session.refresh(run)
        _log_event(session, run.id, "complete", "analysis completed")
        return run
