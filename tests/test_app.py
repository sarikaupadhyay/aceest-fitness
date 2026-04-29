import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_get_programs(client):
    response = client.get('/programs')
    assert response.status_code == 200
    assert 'Fat Loss (FL)' in response.json

def test_calculate_calories_valid(client):
    payload = {'program': 'Muscle Gain (MG)', 'weight': 80}
    response = client.post('/calories', json=payload)
    assert response.status_code == 200
    assert response.json['calories'] == 2800

def test_calculate_calories_invalid_program(client):
    payload = {'program': 'Invalid', 'weight': 70}
    response = client.post('/calories', json=payload)
    assert response.status_code == 400

def test_calculate_calories_fat_loss(client):
    payload = {'program': 'Fat Loss (FL)', 'weight': 70}
    response = client.post('/calories', json=payload)
    assert response.json['calories'] == 1540