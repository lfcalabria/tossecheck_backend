import json
from datetime import datetime
from django.test import TestCase, Client
from model_bakery import baker
from api.models import Usuario, Pet

class TestSyncPetViews(TestCase):
    """Testes para views.sync_pet (rota /api/v1/sync/pet/)."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/sync/pet/'
        self.usuario = baker.make(Usuario)

    def test_post_cria_pet(self):
        """POST dados válidos → 201."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())
        self.assertIn('ano_nascimento', response.json())

    def test_post_com_idade_valida(self):
        """Idade string numérica → ano_nascimento calculado (try)."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
            'idade': '5',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['ano_nascimento'], datetime.now().year - 5)

    def test_post_com_idade_invalida(self):
        """Idade string não numérica → erro 400 (IntegerField rejeita 'abc')."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
            'idade': 'abc',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # ← corrigido: 201 → 400

    def test_post_sem_idade(self):
        """Idade não enviada → ano_nascimento None (else)."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Cachorro',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()['ano_nascimento'])

    def test_post_tipo_invalido(self):
        """Tipo diferente de Gato/Cachorro → 400."""
        data = {
            'usuario_uuid': str(self.usuario.uuid),
            'nome': 'Rex',
            'tipo': 'Peixe',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_malformed_json(self):
        """JSON inválido → except Exception → 400."""
        response = self.client.post(self.url, 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_missing_fields(self):
        """Campos obrigatórios faltando → except Exception → 400."""
        data = {'tipo': 'Cachorro'}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_retorna_405(self):
        """GET → 405."""
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