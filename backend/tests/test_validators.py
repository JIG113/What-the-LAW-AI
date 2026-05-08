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
