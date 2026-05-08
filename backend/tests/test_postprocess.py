from app.models.entities import ExtractedItem
from app.services.postprocess import deduplicate_items, normalize_item_value, recalculate_confidence


def test_normalize_item_value():
    assert normalize_item_value(" 12,000 m2 ") == "12,000 ㎡"


def test_recalculate_confidence_increase_with_units():
    item = ExtractedItem(document_id=1, category="사업개요", item_key="부지면적", item_value="35,722㎡", confidence=0.6)
    assert recalculate_confidence(item) > 0.6


def test_deduplicate_items():
    items = [
        ExtractedItem(document_id=1, category="사업개요", item_key="사업명", item_value="하남A3", confidence=0.6),
        ExtractedItem(document_id=1, category="사업개요", item_key="사업명", item_value="하남A3", confidence=0.7),
    ]
    out = deduplicate_items(items)
    assert len(out) == 1
