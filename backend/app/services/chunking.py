def chunk_pages(pages: list[tuple[int, str]], max_chars: int = 1200) -> list[dict]:
    chunks: list[dict] = []
    for page_no, text in pages:
        t = text.strip()
        if not t:
            continue
        for i in range(0, len(t), max_chars):
            body = t[i : i + max_chars]
            chunks.append(
                {
                    "page_start": page_no,
                    "page_end": page_no,
                    "chunk_text": body,
                    "section_title": "본문",
                }
            )
    return chunks
