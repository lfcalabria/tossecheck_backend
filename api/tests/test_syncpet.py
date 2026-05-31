from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestSyncPet(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/tutor/sync/pet/'
        self.usuario = baker.make(Usuario)

    def test_create_new_pet(self):
        """POST valid data creates pet and returns 201."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())

    def test_update_existing_pet(self):
        """POST with existing pet uuid updates pet and returns 200."""
        pet = baker.make(
            Pet,
            usuario_uuid=str(self.usuario.uuid),
            nome='Antigo',
            tipo='Gato'
        )
        data = {
            'uuid': str(pet.uuid),
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Atualizado',
            'tipo': 'Gato',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        pet.refresh_from_db()
        self.assertEqual(pet.nome, 'Atualizado')

    def test_sync_pet_missing_required_fields(self):
        """POST missing required fields returns 400."""
        data = {'nome': 'Rex'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_sync_pet_invalid_tipo(self):
        """POST with invalid tipo returns 400."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Peixe',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_sync_pet_usuario_not_found(self):
        """POST with nonexistent usuario_uuid returns 404."""
        data = {
            'usuario_uuid': str(uuid4()),
            'nome': 'Rex',
            'tipo': 'Cachorro',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_sync_pet_method_not_allowed_get(self):
        """GET returns 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_sync_pet_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_sync_pet_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_sync_pet_idade_valida(self):
        """POST with numeric idade string converts to int (try branch)."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
            'idade': '5',  # string numérica → int(5)
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        pet = Pet.objects.last()
        self.assertEqual(pet.idade, 5)

    def test_sync_pet_idade_invalida(self):
        """POST with non-numeric idade string sets idade=None (except branch)."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
            'idade': 'abc',  # string não numérica → int('abc') lança exceção
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        pet = Pet.objects.last()
        self.assertIsNone(pet.idade)

    def test_sync_pet_idade_vazia(self):
        """POST with empty idade string sets idade=None (else branch)."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
            'idade': '',  # string vazia → else → idade = None
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        pet = Pet.objects.last()
        self.assertIsNone(pet.idade)

    def test_sync_pet_malformed_json(self):
        """POST with malformed JSON returns 400 (except Exception branch)."""
        response = self.client.post(
            self.url,
            '{{invalid json}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    