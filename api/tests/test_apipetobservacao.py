from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestApiPetObservacao(TestCase):
    def setUp(self):
        self.client = Client()
        self.pet = baker.make(Pet)
        self.vet = baker.make(Veterinario, nome='Dr. Carlos')
        self.url = f'/api/v1/pets/{self.pet.uuid}/observacoes/'
        self.obs_data = {
            'texto': 'Observação de teste'
            # view pega o primeiro veterinário, não precisa enviar uuid
        }

    def test_create_observacao_success(self):
        """POST valid data creates observation and returns 201."""
        response = self.client.post(
            self.url,
            json.dumps(self.obs_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())

    def test_create_observacao_missing_texto(self):
        """POST without texto returns 400."""
        data = {}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_observacao_pet_not_found(self):
        """POST for nonexistent pet returns 404."""
        url = f'/api/v1/pets/{uuid4()}/observacoes/'
        response = self.client.post(
            url,
            json.dumps(self.obs_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_observacao_method_not_allowed_get(self):
        """GET returns 405 (view only accepts POST)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_observacao_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_observacao_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_observacao_json_invalido(self):
        """JSON malformado → except json.JSONDecodeError → 400."""
        response = self.client.post(
            self.url,
            'not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_observacao_json_decode_error(self):
        """JSON malformado → except json.JSONDecodeError → 400."""
        response = self.client.post(
            self.url,
            'not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('JSON inválido', response.json().get('erro', ''))

    def test_observacao_exception_generica(self):
        """Erro inesperado no POST → except Exception as e → 400."""
        from unittest.mock import patch
        data = {'texto': 'Observação'}
        with patch('api.views.Observacao.objects.create', side_effect=Exception('Erro inesperado')):
            response = self.client.post(
                self.url,
                json.dumps(data),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 400)

    def test_post_sem_veterinario(self):
        """Nenhum veterinário cadastrado → except → 400."""
        Veterinario.objects.all().delete()
        data = {'texto': 'Observação teste'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Nenhum veterinário cadastrado', response.json().get('erro', ''))
