from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *
from unittest.mock import patch

class TestApiResponsavel(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/responsavel/'
        self.usuario = baker.make(Usuario, cpf='12345678901', nome='Maria')

    def test_responsavel_found_by_cpf(self):
        """GET with ?q=CPF returns 200 and usuario data."""
        response = self.client.get(f'{self.url}?q={self.usuario.cpf}')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['nome'], self.usuario.nome)

    def test_responsavel_not_found(self):
        """GET with nonexistent cpf returns 404."""
        response = self.client.get(f'{self.url}?q=00000000000')
        self.assertEqual(response.status_code, 404)

    def test_responsavel_missing_cpf(self):
        """GET without q param returns 400."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_responsavel_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(self.url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_responsavel_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_responsavel_found_returns_expected_keys(self):
        """Verifica se o body contém as chaves esperadas."""
        response = self.client.get(f'{self.url}?q={self.usuario.cpf}')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('nome', body)
        self.assertIn('cpf', body)
        self.assertIn('uuid', body)

    def test_responsavel_not_found_message(self):
        """Verifica mensagem de erro no 404."""
        response = self.client.get(f'{self.url}?q=00000000000')
        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertIn('erro', body)

    def test_responsavel_post_cria_usuario(self):
        """POST dados válidos → 201."""
        data = {'nome': 'João', 'cpf': '98765432100', 'telefone': '81999999999'}
        response = self.client.post(
            '/api/v1/responsavel/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())
        self.assertEqual(response.json()['nome'], 'João')

    def test_responsavel_post_campos_faltando(self):
        """POST sem campos obrigatórios → 400."""
        data = {'nome': 'João'}
        response = self.client.post(
            '/api/v1/responsavel/',
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_responsavel_post_json_invalido(self):
        """JSON inválido → except json.JSONDecodeError → 400."""
        response = self.client.post(
            '/api/v1/responsavel/',
            'not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_cpf_invalido(self):
        """GET com CPF inválido (só não-dígitos) → 400."""
        response = self.client.get(f'{self.url}?q=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIn('CPF inválido', response.json().get('erro', ''))

    