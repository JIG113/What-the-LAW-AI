from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def _upload(client: TestClient, tmp_path: Path) -> int:
    sample = tmp_path / "run_control.txt"
    sample.write_text("사업개요\n\n면적 1000\n\n제출 서류", encoding="utf-8")
    with sample.open("rb") as fp:
        res = client.post("/api/v1/documents/upload?project_id=p2", files={"file": ("run_control.txt", fp, "text/plain")})
    assert res.status_code == 200
    return res.json()["document_id"]


def test_retry_and_cancel_endpoints(tmp_path: Path):
    with TestClient(app) as client:
        doc_id = _upload(client, tmp_path)

        r1 = client.post("/api/v1/analysis/run", json={"document_id": doc_id})
        assert r1.status_code == 200
        run_id = r1.json()["id"]

        retry = client.post(f"/api/v1/analysis/runs/{run_id}/retry")
        assert retry.status_code == 200
        retry_id = retry.json()["id"]

        cancel = client.post(f"/api/v1/analysis/runs/{retry_id}/cancel")
        assert cancel.status_code == 200
        assert cancel.json()["status"] in {"cancelling", "cancelled", "completed"}
