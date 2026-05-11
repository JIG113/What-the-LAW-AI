import re

from app.models.entities import ExtractedItem


def normalize_item_value(value: str) -> str:
    v = value.strip()
    v = re.sub(r"\s+", " ", v)
    v = v.replace("m2", "㎡")
    v = v.replace("세대 ", "세대")
    return v


def recalculate_confidence(item: ExtractedItem) -> float:
    conf = float(item.confidence)

    if re.search(r"\d", item.item_value):
        conf += 0.05
    if re.search(r"(㎡|%|세대|\d{4}[-./]\d{1,2}[-./]\d{1,2})", item.item_value):
        conf += 0.06
    if len(item.item_value) < 4:
        conf -= 0.1

    return max(0.1, min(0.995, round(conf, 3)))


def deduplicate_items(items: list[ExtractedItem]) -> list[ExtractedItem]:
    seen = set()
    out: list[ExtractedItem] = []
    for item in items:
        key = (item.category, item.item_key, normalize_item_value(item.item_value))
        if key in seen:
            continue
        seen.add(key)
        item.item_value = key[2]
        item.confidence = recalculate_confidence(item)
        out.append(item)
    return out
