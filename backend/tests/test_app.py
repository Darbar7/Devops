import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    # Adjust status code based on your home route (e.g., 200 or 404)
    assert response.status_code in [200, 404]