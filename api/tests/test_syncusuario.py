from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestSyncUsuario(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/tutor/sync/usuario/'

    def test_create_new_usuario(self):
        """POST with valid data creates usuario and returns 201."""
        data = {'nome': 'Novo', 'cpf': '52998224725', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_sync_usuario_cpf_existente_dados_iguais(self):
        """POST with existing CPF and matching data returns 200."""
        baker.make(Usuario, cpf='52998224725', nome='Maria', telefone='81988888888')
        data = {'nome': 'Maria', 'cpf': '52998224725', 'telefone': '81988888888'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_sync_usuario_cpf_existente_dados_divergentes(self):
        """POST with existing CPF and different data returns 409."""
        baker.make(Usuario, cpf='52998224725', nome='Maria', telefone='81988888888')
        data = {'nome': 'OutroNome', 'cpf': '52998224725', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)

    def test_sync_usuario_cpf_invalido(self):
        """POST with invalid CPF returns 400."""
        data = {'nome': 'Teste', 'cpf': '12345678901', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('CPF inválido', response.json().get('erro', ''))

    def test_sync_usuario_missing_fields(self):
        """POST without required fields returns 400."""
        data = {'nome': 'Teste'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_sync_usuario_method_not_allowed_get(self):
        """GET returns 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_sync_usuario_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_sync_usuario_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_sync_usuario_cpf_curto(self):
        """POST with CPF shorter than 11 digits returns 400."""
        data = {'nome': 'Teste', 'cpf': '1234567', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('CPF inválido', response.json().get('erro', ''))

    def test_sync_usuario_cpf_longo(self):
        """POST with CPF longer than 11 digits returns 400."""
        data = {'nome': 'Teste', 'cpf': '123456789012', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('CPF inválido', response.json().get('erro', ''))

    def test_sync_usuario_cpf_repetido(self):
        """POST with all-same-digit CPF (e.g. 111.111.111-11) returns 400."""
        data = {'nome': 'Teste', 'cpf': '11111111111', 'telefone': '81999999999'}
        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('CPF inválido', response.json().get('erro', ''))

    def test_sync_usuario_malformed_json(self):
        """POST with malformed JSON returns 400 (except branch)."""
        response = self.client.post(
            self.url,
            '{{invalid json}}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_sync_usuario_get_retorna_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

