from sqlmodel import Session, SQLModel, create_engine

from app.models.entities import Chunk
from app.services.embedding import dumps_embedding, embed_text
from app.services.search import hybrid_search_chunks


def test_hybrid_search_chunks():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        t1 = "사업개요 및 면적 정보"
        t2 = "제출 서류 및 심의 일정"
        session.add(Chunk(document_id=1, page_start=1, page_end=1, chunk_text=t1, section_title="본문", embedding_json=dumps_embedding(embed_text(t1))))
        session.add(Chunk(document_id=1, page_start=2, page_end=2, chunk_text=t2, section_title="본문", embedding_json=dumps_embedding(embed_text(t2))))
        session.commit()

        rows = hybrid_search_chunks(session, document_id=1, query="사업개요 면적")
        assert len(rows) >= 1
        assert rows[0][0].page_start == 1
        assert rows[0][3] > 0
