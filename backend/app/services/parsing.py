from pathlib import Path


def parse_file(path: str) -> list[str]:
    """Return page-level text list.

    Stage 2 baseline parser:
    - txt/md/csv: split by line blocks
    - others: best-effort utf-8 decode fallback
    """
    p = Path(path)
    suffix = p.suffix.lower()
    raw = p.read_bytes()

    if suffix in {".txt", ".md", ".csv"}:
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = raw.decode("utf-8", errors="ignore")

    if not text.strip():
        return [""]

    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    pages = []
    page_size = 12
    for i in range(0, len(blocks), page_size):
        pages.append("\n\n".join(blocks[i : i + page_size]))
    return pages or [text]
