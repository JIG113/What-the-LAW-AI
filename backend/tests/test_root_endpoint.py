from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint_returns_service_metadata():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'running'
    assert payload['health'] == '/health'
    assert payload['docs'] == '/docs'
    assert payload['api_base'] == '/api/v1'
