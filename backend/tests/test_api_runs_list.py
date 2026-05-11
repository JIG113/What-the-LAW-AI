from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_list_runs_with_pagination(tmp_path: Path):
    with TestClient(app) as client:
        sample = tmp_path / "runs_list.txt"
        sample.write_text("사업개요\n\n면적 1000", encoding="utf-8")
        with sample.open("rb") as fp:
            up = client.post("/api/v1/documents/upload?project_id=p3", files={"file": ("runs_list.txt", fp, "text/plain")})
        doc_id = up.json()["document_id"]

        client.post("/api/v1/analysis/run", json={"document_id": doc_id})
        client.post("/api/v1/analysis/run", json={"document_id": doc_id})

        res = client.get(f"/api/v1/analysis/runs?document_id={doc_id}&offset=0&limit=1")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] >= 2
        assert len(body["items"]) == 1
