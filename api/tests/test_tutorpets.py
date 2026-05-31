from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestTutorPets(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/tutor/pets/'
        self.usuario = baker.make(Usuario)
        self.pet = baker.make(Pet, usuario_uuid=str(self.usuario.uuid))

    def test_tutor_pets_found(self):
        """GET with ?usuario_uuid= returns list of pets."""
        response = self.client.get(f'{self.url}?usuario_uuid={self.usuario.uuid}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pets', data)
        self.assertIsInstance(data['pets'], list)
        self.assertEqual(len(data['pets']), 1)

    def test_tutor_pets_not_found(self):
        """GET with nonexistent usuario_uuid returns empty list."""
        response = self.client.get(f'{self.url}?usuario_uuid={uuid4()}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['pets']), 0)

    def test_tutor_pets_missing_param(self):
        """GET without usuario_uuid returns 400."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_tutor_pets_method_not_allowed_post(self):
        """POST returns 405."""
        response = self.client.post(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_tutor_pets_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_tutor_pets_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)