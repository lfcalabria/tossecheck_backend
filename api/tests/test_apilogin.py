from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestApiLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/login/'
        self.password = 'senha123'
        self.vet = baker.make(Veterinario, crmv='CRMV001', senha=self.password, ativo=True)

    def test_login_success(self):
        """POST with valid credentials returns 200 and token."""
        data = {'crmv': self.vet.crmv, 'senha': self.password}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['token'], str(self.vet.uuid))
        self.assertEqual(body['veterinario']['nome'], self.vet.nome)

    def test_login_invalid_credentials(self):
        """POST with wrong senha returns 401."""
        data = {'crmv': self.vet.crmv, 'senha': 'wrong'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)  # ✅ 401, não 400

    def test_login_missing_fields(self):
        """POST missing crmv or senha returns 400."""
        data = {'crmv': self.vet.crmv}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_nonexistent_crmv(self):
        """POST with nonexistent crmv returns 404."""
        data = {'crmv': 'NADA', 'senha': 'x'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)  # ✅ 404, não 400

    def test_login_method_not_allowed_get(self):
        """GET returns 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_login_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(self.url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_login_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_login_malformed_json(self):
        """POST with malformed JSON returns 400."""
        response = self.client.post(self.url, 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_exception_generica(self):
        """Erro inesperado → except Exception → 400."""
        from unittest.mock import patch
        data = {'crmv': '12345', 'senha': 'senha123'}
        with patch('api.views.Veterinario.objects.get', side_effect=Exception('Erro inesperado')):
            response = self.client.post(
                self.url,
                json.dumps(data),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Erro interno da API', response.json().get('erro', ''))

        