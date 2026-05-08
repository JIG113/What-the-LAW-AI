from datetime import UTC, datetime

from app.models.entities import ExtractedItem
from app.services.validators import run_domain_validations


def test_validation_detects_missing_area_unit_and_bad_percent():
    items = [
        ExtractedItem(id=1, document_id=1, category="대지·법규", item_key="용적률", item_value="1200%", confidence=0.9),
        ExtractedItem(id=2, document_id=1, category="사업개요", item_key="부지면적", item_value="35722", confidence=0.8),
    ]
    issues = run_domain_validations(run_id=1, items=items)
    codes = {i.rule_code for i in issues}
    assert "PERCENT_RANGE" in codes
    assert "AREA_UNIT_MISSING" in codes


def test_validation_detects_date_and_household_issues():
    items = [
        ExtractedItem(id=3, document_id=1, category="제출·심의", item_key="접수마감", item_value="2020-01-01", confidence=0.9),
        ExtractedItem(id=4, document_id=1, category="사업개요", item_key="세대수", item_value="0세대", confidence=0.9),
        ExtractedItem(id=5, document_id=1, category="제출·심의", item_key="제출기한", item_value="형식없음", confidence=0.9),
    ]
    issues = run_domain_validations(run_id=1, items=items, now_utc=datetime(2026, 5, 8, tzinfo=UTC))
    codes = {i.rule_code for i in issues}
    assert "DATE_PAST" in codes
    assert "HOUSEHOLD_RANGE" in codes
    assert "DATE_FORMAT" in codes


def test_strict_profile_percent_threshold():
    items = [
        ExtractedItem(id=10, document_id=1, category="대지·법규", item_key="용적률", item_value="800%", confidence=0.9),
    ]
    issues = run_domain_validations(run_id=1, items=items, percent_upper_bound=500)
    codes = {i.rule_code for i in issues}
    assert "PERCENT_RANGE" in codes
