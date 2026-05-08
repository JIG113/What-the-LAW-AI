import re

from app.models.entities import ExtractedItem, ValidationIssue


def _parse_percent(value: str) -> float | None:
    m = re.search(r"([\d.]+)\s*%", value)
    if not m:
        return None
    return float(m.group(1))


def run_domain_validations(run_id: int, items: list[ExtractedItem]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for item in items:
        if item.item_key in {"용적률", "건폐율"}:
            val = _parse_percent(item.item_value)
            if val is None:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="PERCENT_FORMAT",
                        severity="warning",
                        message=f"{item.item_key} 값에서 % 형식을 찾지 못했습니다: {item.item_value}",
                    )
                )
            elif val <= 0 or val > 1000:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="PERCENT_RANGE",
                        severity="error",
                        message=f"{item.item_key} 값 범위가 비정상입니다: {item.item_value}",
                    )
                )

        if item.item_key in {"부지면적", "대지면적"} and "㎡" not in item.item_value:
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    item_id=item.id,
                    rule_code="AREA_UNIT_MISSING",
                    severity="warning",
                    message=f"{item.item_key} 단위(㎡)가 누락되었을 수 있습니다: {item.item_value}",
                )
            )

    return issues
