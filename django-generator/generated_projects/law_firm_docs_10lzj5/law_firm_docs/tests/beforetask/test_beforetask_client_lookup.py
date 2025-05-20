import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from law_firm_docs.models import Client


@pytest.fixture
def client():
    from django.test import Client

    return Client()


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client"""
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")
    return client


@pytest.fixture
def test_client():
    return Client.objects.create(
        reference_number="TEST-001", name="Test Client", email="test@example.com"
    )


@pytest.mark.django_db
def test_existing_client_lookup(authenticated_client, test_client):
    """Test lookup of existing client by reference number"""
    response = authenticated_client.get(
        reverse("law_firm_docs:client_lookup", kwargs={"reference_number": "TEST-001"})
    )
    print("\nResponse status code:", response.status_code)
    print("Response content:", response.content)
    data = json.loads(response.content)
    print("Parsed data:", data)

    assert response.status_code == 200
    assert "exists" in data
    assert "client" in data
    assert "name" in data["client"]
    client_data = data["client"]
    assert client_data["name"] == "Test Client"


@pytest.mark.django_db
def test_new_client_lookup(authenticated_client):
    """Test lookup of non-existent client"""
    response = authenticated_client.get(
        reverse("law_firm_docs:client_lookup", kwargs={"reference_number": "NEW-001"})
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert not data["exists"]


@pytest.mark.django_db
def test_invalid_reference_format(authenticated_client):
    """Test lookup with invalid reference number format"""
    response = authenticated_client.get(
        reverse(
            "law_firm_docs:client_lookup", kwargs={"reference_number": "invalid@format"}
        )
    )

    assert response.status_code == 200
    data = json.loads(response.content)
    assert not data["exists"]
