from sqlmodel import Session, select

from app.models.entities import Chunk
from app.services.embedding import cosine_similarity, embed_text, loads_embedding


def hybrid_search_chunks(session: Session, document_id: int, query: str, limit: int = 20):
    tokens = [t.strip() for t in query.split() if t.strip()]
    if not tokens:
        return []

    q_vec = embed_text(query)
    chunks = session.exec(select(Chunk).where(Chunk.document_id == document_id)).all()
    scored = []
    for chunk in chunks:
        keyword_score = sum(chunk.chunk_text.count(token) for token in tokens)
        vector_score = cosine_similarity(q_vec, loads_embedding(chunk.embedding_json))
        hybrid = keyword_score + max(0.0, vector_score) * 5.0
        if hybrid > 0:
            scored.append((chunk, keyword_score, round(vector_score, 4), round(hybrid, 4)))

    scored.sort(key=lambda x: x[3], reverse=True)
    return scored[:limit]
