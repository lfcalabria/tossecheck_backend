import json
from django.test import TestCase, Client
from model_bakery import baker
from api.models import Usuario
from django.db import IntegrityError
from unittest.mock import patch

class TestSyncUsuarioViews(TestCase):
    """Testes para views.sync_usuario (rota /api/v1/sync/usuario/)."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/sync/usuario/'

    def test_post_cria_usuario(self):
        """POST dados válidos + CPF novo → 201 (cria)."""
        data = {'nome': 'Novo', 'cpf': '12345678901', 'telefone': '81999999999'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())

    def test_post_cpf_existente_dados_iguais(self):
        """POST CPF existente + dados iguais → 200 (libera)."""
        baker.make(Usuario, cpf='12345678901', nome='Maria', telefone='81988888888')
        data = {'nome': 'Maria', 'cpf': '12345678901', 'telefone': '81988888888'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_post_cpf_existente_dados_divergentes(self):
        """POST CPF existente + dados diferentes → 409 (bloqueia)."""
        baker.make(Usuario, cpf='12345678901', nome='Maria', telefone='81988888888')
        data = {'nome': 'OutroNome', 'cpf': '12345678901', 'telefone': '81999999999'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.json().get('bloqueado'))

    def test_post_campos_faltando(self):
        """POST sem campos obrigatórios → 400."""
        data = {'nome': 'Teste'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_malformed_json(self):
        """JSON inválido → except Exception → 400."""
        response = self.client.post(self.url, 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_retorna_405(self):
        """GET → 405 (cobre if request.method != POST)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put_retorna_405(self):
        """PUT → 405."""
        response = self.client.put(self.url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_delete_retorna_405(self):
        """DELETE → 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_integrity_error(self):
        """IntegrityError ao criar → 409."""
        with patch('api.views.Usuario.objects.create', side_effect=IntegrityError):
            data = {'nome': 'Novo', 'cpf': '12345678901', 'telefone': '81999999999'}
            response = self.client.post(
                self.url,
                json.dumps(data),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 409)
        self.assertIn('Conflito de CPF', response.json().get('erro', ''))
