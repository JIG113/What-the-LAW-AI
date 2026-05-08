from app.models.entities import Document, ExtractedItem

CATEGORIES = [
    "사업개요",
    "대지·법규",
    "계획기준",
    "구조·설비",
    "제출·심의",
    "특이사항",
    "체크리스트",
]


def run_stage1_analysis(document: Document) -> list[ExtractedItem]:
    demo_value = f"{document.file_name}에서 자동 추출(초기 MVP 더미)"
    items = []
    for category in CATEGORIES:
        items.append(
            ExtractedItem(
                document_id=document.id,
                category=category,
                item_key=f"{category} 기본항목",
                item_value=demo_value,
                confidence=0.51,
            )
        )
    return items
