import pytest
import requests

@pytest.fixture
def create_item_payload():
    return {
        "name": "Wireless Keyboard",
        "price": 75.99
    }

@pytest.fixture
def item_url():
    return "http://127.0.0.1:8000/items/"

def test_create_new_item(create_item_payload, item_url):
    response = requests.post(item_url, json=create_item_payload)
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_requested_items(item_url):
    response = requests.get(item_url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)