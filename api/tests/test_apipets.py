from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestApiPets(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/pets/'
        self.usuario = baker.make(Usuario)
        self.valid_pet_data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
        }

    def test_create_pet_success(self):
        """POST with valid data creates a pet and returns 201."""
        response = self.client.post(
            self.url,
            json.dumps(self.valid_pet_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)  # ✅ view retorna 201
        self.assertIn('uuid', response.json())

    def test_create_pet_missing_fields(self):
        """POST missing required fields returns 400."""
        data = {'nome': 'Rex'}  # sem usuario_uuid e tipo
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_pet_invalid_tipo(self):
        """POST with invalid tipo returns 400."""
        data = self.valid_pet_data.copy()
        data['tipo'] = 'Peixe'
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_pets_method_not_allowed_get(self):
        """GET returns 405 (view only accepts POST)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # ✅ view só aceita POST

    def test_pets_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_pets_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_pets_malformed_json(self):
        """POST with malformed JSON returns 400."""
        response = self.client.post(
            self.url,
            'invalid',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_post_idade_string_nao_numerica(self):
        """Idade 'abc' → except Exception → idade = None."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Gato',
            'idade': 'abc',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()['idade'])

    def test_post_usuario_nao_encontrado(self):
        """UUID inexistente → except Usuario.DoesNotExist → 404."""
        data = {
            'usuario_uuid': '00000000-0000-0000-0000-000000000000',
            'nome': 'Rex',
            'tipo': 'Gato',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('Responsável não encontrado', response.json().get('erro', ''))

    def test_post_sem_nome(self):
        """POST sem nome → 400."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'tipo': 'Gato',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Nome é obrigatório', response.json().get('erro', ''))

    def test_post_sem_tipo(self):
        """POST sem tipo → 400."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
        }
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Tipo é obrigatório', response.json().get('erro', ''))

    def test_post_exception_generica(self):
        """Erro inesperado → except Exception → 400."""
        from unittest.mock import patch
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Gato',
        }
        with patch('api.views.Pet.objects.create', side_effect=Exception('Erro inesperado')):
            response = self.client.post(
                self.url,
                json.dumps(data),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 400)

