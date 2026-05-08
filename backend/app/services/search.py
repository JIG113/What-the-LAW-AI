from sqlmodel import Session, select

from app.models.entities import Chunk


def keyword_search_chunks(session: Session, document_id: int, query: str, limit: int = 20):
    tokens = [t.strip() for t in query.split() if t.strip()]
    if not tokens:
        return []

    chunks = session.exec(select(Chunk).where(Chunk.document_id == document_id)).all()
    scored = []
    for chunk in chunks:
        score = sum(chunk.chunk_text.count(token) for token in tokens)
        if score > 0:
            scored.append((chunk, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]
