from fastapi.testclient import TestClient

from app.main import app


def test_rule_profiles_crud():
    with TestClient(app) as client:
        listed = client.get('/api/v1/rule-profiles')
        assert listed.status_code == 200
        assert listed.json()['total'] >= 2

        created = client.post('/api/v1/rule-profiles?name=custom1&percent_upper_bound=700')
        assert created.status_code == 200
        assert created.json()['name'] == 'custom1'

        updated = client.patch('/api/v1/rule-profiles/custom1?percent_upper_bound=650&enabled=true')
        assert updated.status_code == 200
        assert updated.json()['percent_upper_bound'] == 650
