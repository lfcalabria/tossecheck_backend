from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestApiPetDetail(TestCase):
    def setUp(self):
        self.client = Client()
        self.pet = baker.make(Pet)
        self.url = f'/api/v1/pets/{self.pet.uuid}/'

    def test_get_pet_detail(self):
        """GET returns pet data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['uuid'], str(self.pet.uuid))

    def test_get_pet_not_found(self):
        """GET with nonexistent UUID returns 404."""
        response = self.client.get(f'/api/v1/pets/{uuid4()}/')
        self.assertEqual(response.status_code, 404)

    def test_update_pet_method_not_allowed(self):
        """PUT returns 405 (view only accepts GET)."""
        data = {'nome': 'NovoNome', 'tipo': 'Gato'}
        response = self.client.put(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)  # ✅ view não aceita PUT

    def test_delete_pet_method_not_allowed(self):
        """DELETE returns 405 (view only accepts GET)."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)  # ✅ view não aceita DELETE

    def test_pet_detail_method_not_allowed_post(self):
        """POST returns 405."""
        response = self.client.post(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)