from django.test import TestCase
from model_bakery import baker
from api.models import Usuario
from api.serializers import UsuarioSerializer

class TestUsuarioSerializer(TestCase):
    def setUp(self):
        self.usuario = baker.make(Usuario)

    def test_contains_expected_fields(self):
        serializer = UsuarioSerializer(instance=self.usuario)
        expected_fields = {'id', 'uuid', 'nome', 'cpf', 'telefone', 'bloqueado', 'liberado'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = UsuarioSerializer(instance=self.usuario)
        self.assertIn('id', serializer.data)
        self.assertIn('uuid', serializer.data)

    def test_nome_field(self):
        serializer = UsuarioSerializer(instance=self.usuario)
        self.assertEqual(serializer.data['nome'], self.usuario.nome)
        self.assertEqual(serializer.data['cpf'], self.usuario.cpf)