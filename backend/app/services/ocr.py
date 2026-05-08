def run_ocr_if_needed(page_text: str) -> tuple[str, float]:
    """Stage 2 placeholder OCR gate.

    If page has enough text, keep it with high confidence.
    Otherwise, mark low confidence and return empty text.
    """
    normalized = (page_text or "").strip()
    if len(normalized) > 20:
        return normalized, 0.95
    return normalized, 0.35
