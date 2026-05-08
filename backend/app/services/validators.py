import re
from datetime import UTC, datetime

from app.models.entities import ExtractedItem, ValidationIssue


def _parse_percent(value: str) -> float | None:
    m = re.search(r"([\d.]+)\s*%", value)
    if not m:
        return None
    return float(m.group(1))


def _parse_korean_date(value: str) -> datetime | None:
    candidates = [
        r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})",
        r"(\d{2})[-./](\d{1,2})[-./](\d{1,2})",
    ]
    for pattern in candidates:
        m = re.search(pattern, value)
        if not m:
            continue
        y, mo, d = [int(x) for x in m.groups()]
        if y < 100:
            y += 2000
        try:
            return datetime(y, mo, d, tzinfo=UTC)
        except ValueError:
            return None
    return None


def _parse_number(value: str) -> float | None:
    m = re.search(r"([\d,]+(?:\.\d+)?)", value)
    if not m:
        return None
    return float(m.group(1).replace(",", ""))


def run_domain_validations(run_id: int, items: list[ExtractedItem], now_utc: datetime | None = None, percent_upper_bound: float = 1000.0) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    now_utc = now_utc or datetime.now(UTC)
    max_percent = percent_upper_bound

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
            elif val <= 0 or val > max_percent:
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

        if item.item_key in {"세대수", "세대"}:
            n = _parse_number(item.item_value)
            if n is None:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="HOUSEHOLD_FORMAT",
                        severity="warning",
                        message=f"세대수 숫자 형식을 해석할 수 없습니다: {item.item_value}",
                    )
                )
            elif n <= 0:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="HOUSEHOLD_RANGE",
                        severity="error",
                        message=f"세대수 값 범위가 비정상입니다: {item.item_value}",
                    )
                )

        if item.item_key in {"접수마감", "마감일", "제출기한"}:
            dt = _parse_korean_date(item.item_value)
            if dt is None:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="DATE_FORMAT",
                        severity="warning",
                        message=f"날짜 형식을 해석할 수 없습니다: {item.item_value}",
                    )
                )
            elif dt.date() < now_utc.date():
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        item_id=item.id,
                        rule_code="DATE_PAST",
                        severity="warning",
                        message=f"기한이 현재일보다 과거일 수 있습니다: {item.item_value}",
                    )
                )

    return issues
