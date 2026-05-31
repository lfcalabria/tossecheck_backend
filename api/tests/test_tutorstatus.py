from uuid import uuid4
from django.test import TestCase, Client
from model_bakery import baker
import json
from api.models import *

class TestTutorStatusPorCpf(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/tutor/usuario/'
        self.usuario = baker.make(Usuario, cpf='52998224725', nome='Maria')

    def test_tutor_status_found(self):
        """GET with ?cpf= returns 200 and usuario data."""
        response = self.client.get(f'{self.url}?cpf={self.usuario.cpf}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nome'], self.usuario.nome)

    def test_tutor_status_not_found(self):
        """GET with nonexistent cpf returns 404."""
        response = self.client.get(f'{self.url}?cpf=00000000191')
        self.assertEqual(response.status_code, 404)

    def test_tutor_status_missing_cpf(self):
        """GET without cpf returns 400."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_tutor_status_method_not_allowed_post(self):
        """POST returns 405."""
        response = self.client.post(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_tutor_status_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(
            self.url,
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_tutor_status_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)