from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_validation_issues_api(tmp_path: Path):
    with TestClient(app) as client:
        sample = tmp_path / "validation_issue.txt"
        sample.write_text("용적률: 1200%\n\n부지면적: 35722", encoding="utf-8")
        with sample.open("rb") as fp:
            up = client.post("/api/v1/documents/upload?project_id=p5", files={"file": ("validation_issue.txt", fp, "text/plain")})
        doc_id = up.json()["document_id"]

        run = client.post("/api/v1/analysis/run", json={"document_id": doc_id})
        run_id = run.json()["id"]

        res = client.get(f"/api/v1/analysis/runs/{run_id}/validation-issues")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] >= 1
