import re
from collections import defaultdict

from app.models.entities import Chunk, ExtractedItem, ItemEvidence

CATEGORY_RULES = {
    "사업개요": ["사업", "개요", "위치", "면적", "세대", "사업명"],
    "대지·법규": ["법", "규정", "건폐율", "용적률", "인허가", "용도지역"],
    "계획기준": ["계획", "기준", "배치", "시설", "친환경", "에너지"],
    "구조·설비": ["구조", "설비", "전기", "기계", "소방", "내진"],
    "제출·심의": ["제출", "심의", "서류", "기한", "평가", "접수"],
    "특이사항": ["특이", "유의", "예외", "민원", "주의"],
    "체크리스트": ["확인", "검토", "체크", "준비", "완료"],
}

FIELD_PATTERNS = {
    "사업개요": [
        ("사업명", re.compile(r"사업명[:\s]+([^\n]+)")),
        ("위치", re.compile(r"(위치|대상지)[:\s]+([^\n]+)")),
        ("부지면적", re.compile(r"(부지면적|대지면적)[:\s]*([\d,]+\s*㎡?)")),
        ("세대수", re.compile(r"(세대수|세대)[:\s]*([\d,]+\s*세대?)")),
    ],
    "제출·심의": [
        ("접수마감", re.compile(r"(접수마감|마감일|제출기한)[:\s]*([^\n]+)")),
        ("제출서류", re.compile(r"(제출서류|제출 문서)[:\s]*([^\n]+)")),
    ],
    "대지·법규": [
        ("용적률", re.compile(r"용적률[:\s]*([\d.]+\s*%)")),
        ("건폐율", re.compile(r"건폐율[:\s]*([\d.]+\s*%)")),
    ],
}


def _category_score(text: str, keywords: list[str]) -> int:
    score = 0
    for keyword in keywords:
        score += text.count(keyword)
    if re.search(r"\b\d+[,.]?\d*\s*(%|㎡|m2|세대)\b", text):
        score += 1
    return score


def _extract_structured_fields(category: str, text: str) -> list[tuple[str, str]]:
    patterns = FIELD_PATTERNS.get(category, [])
    found: list[tuple[str, str]] = []
    for field_name, pattern in patterns:
        m = pattern.search(text)
        if not m:
            continue
        value = m.group(m.lastindex).strip() if m.lastindex else m.group(0).strip()
        if value:
            found.append((field_name, value))
    return found


def extract_items_from_chunks(document_id: int, chunks: list[Chunk]) -> tuple[list[ExtractedItem], list[ItemEvidence]]:
    by_category: dict[str, list[tuple[Chunk, int]]] = defaultdict(list)
    for chunk in chunks:
        for category, keywords in CATEGORY_RULES.items():
            score = _category_score(chunk.chunk_text, keywords)
            if score > 0:
                by_category[category].append((chunk, score))

    items: list[ExtractedItem] = []
    evidences: list[ItemEvidence] = []

    for category, matches in by_category.items():
        top_chunk, top_score = sorted(matches, key=lambda x: x[1], reverse=True)[0]
        snippet = top_chunk.chunk_text[:260]

        structured_fields = _extract_structured_fields(category, top_chunk.chunk_text)
        if structured_fields:
            for field_name, value in structured_fields:
                confidence = min(0.995, 0.60 + top_score * 0.05)
                item = ExtractedItem(
                    document_id=document_id,
                    category=category,
                    item_key=field_name,
                    item_value=value,
                    confidence=round(confidence, 3),
                )
                items.append(item)
                evidences.append(
                    ItemEvidence(
                        extracted_item_id=0,
                        document_id=document_id,
                        page_no=top_chunk.page_start,
                        snippet_text=snippet,
                        retrieval_method="regex+keyword",
                        evidence_score=round(confidence, 3),
                    )
                )
        else:
            confidence = min(0.95, 0.45 + top_score * 0.07)
            item = ExtractedItem(
                document_id=document_id,
                category=category,
                item_key=f"{category} 자동추출",
                item_value=snippet,
                confidence=round(confidence, 3),
            )
            items.append(item)
            evidences.append(
                ItemEvidence(
                    extracted_item_id=0,
                    document_id=document_id,
                    page_no=top_chunk.page_start,
                    snippet_text=snippet,
                    retrieval_method="keyword_routing",
                    evidence_score=round(confidence, 3),
                )
            )

    return items, evidences
