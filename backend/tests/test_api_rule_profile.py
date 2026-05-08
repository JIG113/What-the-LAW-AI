from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_rule_profile_update_and_strict_validation(tmp_path: Path):
    with TestClient(app) as client:
        sample = tmp_path / "strict_profile.txt"
        sample.write_text("용적률: 800%", encoding="utf-8")
        with sample.open("rb") as fp:
            up = client.post(
                "/api/v1/documents/upload?project_id=p6&rule_profile=strict",
                files={"file": ("strict_profile.txt", fp, "text/plain")},
            )
        doc_id = up.json()["document_id"]

        patch = client.patch(f"/api/v1/documents/{doc_id}/rule-profile?rule_profile=strict")
        assert patch.status_code == 200

        run = client.post("/api/v1/analysis/run", json={"document_id": doc_id})
        run_id = run.json()["id"]

        issues = client.get(f"/api/v1/analysis/runs/{run_id}/validation-issues")
        assert issues.status_code == 200
        codes = {i["rule_code"] for i in issues.json()["items"]}
        assert "PERCENT_RANGE" in codes
