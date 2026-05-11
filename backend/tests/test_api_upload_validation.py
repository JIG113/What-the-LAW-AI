from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_upload_rejects_unsupported_extension(tmp_path: Path):
    client = TestClient(app)
    sample = tmp_path / "notice.hwp"
    sample.write_bytes(b"dummy")

    with sample.open("rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            params={"project_id": "p1", "rule_profile": "default"},
            files={"file": ("notice.hwp", f, "application/haansofthwp")},
        )

    assert response.status_code == 400
    assert "지원하지 않는 파일 형식" in response.json()["detail"]
