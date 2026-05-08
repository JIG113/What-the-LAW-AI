from app.services.chunking import chunk_pages
from app.services.ocr import run_ocr_if_needed


def test_chunk_pages_splits_long_text():
    pages = [(1, "a" * 2500)]
    chunks = chunk_pages(pages, max_chars=1000)
    assert len(chunks) == 3
    assert chunks[0]["page_start"] == 1


def test_ocr_gate_confidence():
    text, conf = run_ocr_if_needed("짧음")
    assert text == "짧음"
    assert conf < 0.5

    text2, conf2 = run_ocr_if_needed("충분히 긴 문자열입니다. " * 5)
    assert conf2 > 0.9
