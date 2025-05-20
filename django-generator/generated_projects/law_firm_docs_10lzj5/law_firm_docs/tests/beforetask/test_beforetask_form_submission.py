import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from law_firm_docs.models import Client, Document


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
def test_file():
    return SimpleUploadedFile(
        "test.pdf", b"file_content", content_type="application/pdf"
    )


@pytest.fixture
def existing_client():
    return Client.objects.create(reference_number="EXIST-001", name="Existing Client")


@pytest.mark.django_db
def test_existing_client_document_submission(
    authenticated_client, test_file, existing_client
):
    """Test submission of document for existing client"""
    data = {
        "client_id": existing_client.id,
        "title": "New Document",
        "document_type": "contract",
        "description": "Test description",
    }
    files = {"file": test_file}

    response = authenticated_client.post(
        reverse("law_firm_docs:create_document_api"), {**data, **files}
    )
    assert response.status_code == 200

    # Verify document creation
    document = Document.objects.get(client=existing_client)
    assert document.title == "New Document"


@pytest.mark.django_db
def test_invalid_submission(authenticated_client):
    """Test submission with invalid data"""
    data = {
        "client_id": 999,
        "title": "",
        "document_type": "invalid_type",
    }

    response = authenticated_client.post(
        reverse("law_firm_docs:create_document_api"), data
    )

    assert response.status_code == 400
