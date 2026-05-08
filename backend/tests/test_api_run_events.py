from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_run_events_api(tmp_path: Path):
    with TestClient(app) as client:
        sample = tmp_path / "run_events.txt"
        sample.write_text("사업개요\n\n면적 1000", encoding="utf-8")
        with sample.open("rb") as fp:
            up = client.post("/api/v1/documents/upload?project_id=p4", files={"file": ("run_events.txt", fp, "text/plain")})
        doc_id = up.json()["document_id"]

        run = client.post("/api/v1/analysis/run", json={"document_id": doc_id})
        run_id = run.json()["id"]

        events = client.get(f"/api/v1/analysis/runs/{run_id}/events")
        assert events.status_code == 200
        body = events.json()
        assert body["total"] >= 1
        assert any(e["step"] == "complete" for e in body["items"])
