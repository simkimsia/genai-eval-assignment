from django.test import TestCase, Client
from django.urls import reverse
from law_firm_docs.models import Client
import json

class ClientLookupTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test client
        self.test_client = Client.objects.create(
            reference_number="TEST-001",
            name="Test Client",
            email="test@example.com"
        )

    def test_existing_client_lookup(self):
        """Test lookup of existing client by reference number"""
        response = self.client.get(
            reverse('client_lookup'),
            {'reference_number': 'TEST-001'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Test Client')

    def test_new_client_lookup(self):
        """Test lookup of non-existent client"""
        response = self.client.get(
            reverse('client_lookup'),
            {'reference_number': 'NEW-001'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['exists'])

    def test_invalid_reference_format(self):
        """Test lookup with invalid reference number format"""
        response = self.client.get(
            reverse('client_lookup'),
            {'reference_number': 'invalid@format'}
        )
        self.assertEqual(response.status_code, 400)