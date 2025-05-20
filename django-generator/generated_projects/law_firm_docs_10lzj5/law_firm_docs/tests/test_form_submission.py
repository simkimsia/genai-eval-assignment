from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from law_firm_docs.models import Client, Document
import json

class FormSubmissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test PDF file
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_new_client_document_submission(self):
        """Test submission of new client with document"""
        data = {
            'reference_number': 'NEW-001',
            'name': 'New Client',
            'email': 'new@example.com',
            'document_title': 'Test Document',
            'document_type': 'contract',
            'description': 'Test description'
        }
        files = {'file': self.test_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 200)

        # Verify client creation
        client = Client.objects.get(reference_number='NEW-001')
        self.assertEqual(client.name, 'New Client')

        # Verify document creation
        document = Document.objects.get(client=client)
        self.assertEqual(document.title, 'Test Document')

    def test_existing_client_document_submission(self):
        """Test submission of document for existing client"""
        # Create existing client
        existing_client = Client.objects.create(
            reference_number="EXIST-001",
            name="Existing Client"
        )

        data = {
            'reference_number': 'EXIST-001',
            'document_title': 'New Document',
            'document_type': 'contract',
            'description': 'Test description'
        }
        files = {'file': self.test_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 200)

        # Verify document creation
        document = Document.objects.get(client=existing_client)
        self.assertEqual(document.title, 'New Document')

    def test_invalid_submission(self):
        """Test submission with invalid data"""
        data = {
            'reference_number': 'INVALID',
            'document_title': '',  # Empty title
            'document_type': 'invalid_type'
        }

        response = self.client.post(
            reverse('create_document'),
            data
        )
        self.assertEqual(response.status_code, 400)