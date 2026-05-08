from collections import defaultdict

from app.models.entities import Chunk, ExtractedItem, ItemEvidence

CATEGORY_RULES = {
    "사업개요": ["사업", "개요", "위치", "면적", "세대"],
    "대지·법규": ["법", "규정", "건폐율", "용적률", "인허가"],
    "계획기준": ["계획", "기준", "배치", "시설", "친환경"],
    "구조·설비": ["구조", "설비", "전기", "기계", "소방"],
    "제출·심의": ["제출", "심의", "서류", "기한", "평가"],
    "특이사항": ["특이", "유의", "예외", "민원"],
    "체크리스트": ["확인", "검토", "체크", "준비"],
}


def _category_score(text: str, keywords: list[str]) -> int:
    return sum(text.count(keyword) for keyword in keywords)


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
        snippet = top_chunk.chunk_text[:220]
        confidence = min(0.99, 0.45 + top_score * 0.08)
        item = ExtractedItem(
            document_id=document_id,
            category=category,
            item_key=f"{category} 자동추출",
            item_value=snippet,
            confidence=round(confidence, 2),
        )
        items.append(item)
        evidences.append(
            ItemEvidence(
                extracted_item_id=0,
                document_id=document_id,
                page_no=top_chunk.page_start,
                snippet_text=snippet,
                retrieval_method="keyword_routing",
                evidence_score=round(confidence, 2),
            )
        )

    return items, evidences
