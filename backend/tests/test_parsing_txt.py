from pathlib import Path

from app.services.parsing import parse_file


def test_parse_file_txt(tmp_path: Path):
    f = tmp_path / "sample.txt"
    f.write_text("사업개요\n\n대지법규\n\n제출심의", encoding="utf-8")
    pages = parse_file(str(f))
    assert len(pages) >= 1
    assert "사업개요" in pages[0]
