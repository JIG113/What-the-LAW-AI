import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_rule_profiles_crud():
    profile_name = f"custom_{uuid.uuid4().hex[:8]}"
    with TestClient(app) as client:
        listed = client.get('/api/v1/rule-profiles')
        assert listed.status_code == 200
        assert listed.json()['total'] >= 2

        created = client.post(f'/api/v1/rule-profiles?name={profile_name}&percent_upper_bound=700')
        assert created.status_code == 200
        assert created.json()['name'] == profile_name

        updated = client.patch(f'/api/v1/rule-profiles/{profile_name}?percent_upper_bound=650&enabled=true')
        assert updated.status_code == 200
        assert updated.json()['percent_upper_bound'] == 650
