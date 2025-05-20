import pytest
from django.urls import reverse
from law_firm_docs.models import Client
import json

@pytest.fixture
def client():
    from django.test import Client
    return Client()

@pytest.fixture
def test_client():
    return Client.objects.create(
        reference_number="TEST-001",
        name="Test Client",
        email="test@example.com"
    )

def test_existing_client_lookup(client, test_client):
    """Test lookup of existing client by reference number"""
    response = client.get(
        reverse('client_lookup'),
        {'reference_number': 'TEST-001'}
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['name'] == 'Test Client'

def test_new_client_lookup(client):
    """Test lookup of non-existent client"""
    response = client.get(
        reverse('client_lookup'),
        {'reference_number': 'NEW-001'}
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert not data['exists']

def test_invalid_reference_format(client):
    """Test lookup with invalid reference number format"""
    response = client.get(
        reverse('client_lookup'),
        {'reference_number': 'invalid@format'}
    )
    assert response.status_code == 400