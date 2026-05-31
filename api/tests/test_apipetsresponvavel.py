from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestApiPetsResponsavel(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = baker.make(Usuario)
        self.url = f'/api/v1/responsavel/{self.usuario.uuid}/pets/'
        self.pet = baker.make(Pet, usuario_uuid=str(self.usuario.uuid))

    def test_list_pets_for_responsavel(self):
        """GET returns pets list for the given responsavel UUID."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pets', data)                    # ✅ chave 'pets' existe
        self.assertIsInstance(data['pets'], list)      # ✅ é uma lista
        self.assertEqual(len(data['pets']), 1)         # ✅ tem 1 pet
        self.assertEqual(data['responsavel_nome'], self.usuario.nome)  # ✅ nome do responsável

    def test_list_pets_not_found(self):
        """GET for nonexistent responsavel UUID returns 404."""
        fake_uuid = uuid4()
        response = self.client.get(f'/api/v1/responsavel/{fake_uuid}/pets/')
        self.assertEqual(response.status_code, 404)

    def test_pets_responsavel_method_not_allowed_post(self):
        """POST returns 405."""
        response = self.client.post(self.url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_pets_responsavel_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(self.url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_pets_responsavel_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)