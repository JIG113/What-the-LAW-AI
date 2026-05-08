from app.models.entities import Chunk
from app.services.analyzer import extract_items_from_chunks
from app.services.normalization import normalize_korean_public_notice_text


def test_regex_structured_extraction_for_project_overview():
    text = """
    사업명: 하남 A3 공공주택
    위치: 하남시 A3블록
    부지면적: 35,722㎡
    세대수: 1,100세대
    """
    chunks = [Chunk(document_id=1, page_start=1, page_end=1, chunk_text=text, section_title="본문", embedding_json="")]
    items, evidences = extract_items_from_chunks(1, chunks)

    keys = {i.item_key for i in items}
    assert "사업명" in keys
    assert "부지면적" in keys
    assert len(evidences) >= 2


def test_normalize_korean_public_notice_text():
    src = "제 출   서류\n\n\n사 업 명 m2"
    out = normalize_korean_public_notice_text(src)
    assert "제출" in out
    assert "사업" in out
    assert "㎡" in out
