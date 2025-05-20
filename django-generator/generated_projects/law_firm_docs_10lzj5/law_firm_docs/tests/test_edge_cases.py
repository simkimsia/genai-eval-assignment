from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from law_firm_docs.models import Client, Document
import json

class EdgeCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test files
        self.pdf_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.txt_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )
        self.large_file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (10 * 1024 * 1024),  # 10MB file
            content_type="application/pdf"
        )

    def test_duplicate_client_reference(self):
        """Test submission with duplicate client reference"""
        # Create existing client
        Client.objects.create(
            reference_number="DUPE-001",
            name="First Client"
        )

        data = {
            'reference_number': 'DUPE-001',  # Duplicate reference
            'name': 'Second Client',
            'email': 'second@example.com',
            'document_title': 'Test Document',
            'document_type': 'contract'
        }
        files = {'file': self.pdf_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('reference_number', json.loads(response.content))

    def test_invalid_file_type(self):
        """Test submission with invalid file type"""
        data = {
            'reference_number': 'NEW-001',
            'name': 'New Client',
            'document_title': 'Test Document',
            'document_type': 'contract'
        }
        files = {'file': self.txt_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('file', json.loads(response.content))

    def test_large_file_upload(self):
        """Test submission with large file"""
        data = {
            'reference_number': 'NEW-001',
            'name': 'New Client',
            'document_title': 'Test Document',
            'document_type': 'contract'
        }
        files = {'file': self.large_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('file', json.loads(response.content))

    def test_special_characters(self):
        """Test submission with special characters in fields"""
        data = {
            'reference_number': 'SPEC-001',
            'name': 'Client & Co. (Special)',
            'email': 'special@example.com',
            'document_title': 'Document #123',
            'document_type': 'contract',
            'description': 'Special chars: @#$%^&*()'
        }
        files = {'file': self.pdf_file}

        response = self.client.post(
            reverse('create_document'),
            {**data, **files}
        )
        self.assertEqual(response.status_code, 200)

        # Verify data was saved correctly
        client = Client.objects.get(reference_number='SPEC-001')
        self.assertEqual(client.name, 'Client & Co. (Special)')
        document = Document.objects.get(client=client)
        self.assertEqual(document.title, 'Document #123')