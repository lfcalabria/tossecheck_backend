from uuid import uuid4
from django.test import TestCase
from model_bakery import baker
from api.models import Veterinario, Observacao
from api.serializers import ObservacaoSerializer

class TestObservacaoSerializer(TestCase):
    def setUp(self):
        self.vet = baker.make(Veterinario)
        self.obs = baker.make(Observacao, veterinario=self.vet)

    def test_contains_expected_fields(self):
        serializer = ObservacaoSerializer(instance=self.obs)
        expected_fields = {'id', 'uuid', 'pet_uuid', 'veterinario', 'veterinario_nome',
                           'mensagem', 'data_cadastro'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = ObservacaoSerializer(instance=self.obs)
        self.assertIn('id', serializer.data)
        self.assertIn('uuid', serializer.data)
        self.assertIn('data_cadastro', serializer.data)

    def test_veterinario_nome_read_only(self):
        serializer = ObservacaoSerializer(instance=self.obs)
        self.assertEqual(serializer.data['veterinario_nome'], self.vet.nome)

    def test_create_valid(self):
        data = {
            'pet_uuid': str(uuid4()),
            'veterinario': self.vet.id,
            'mensagem': 'Observação de teste',
        }
        serializer = ObservacaoSerializer(data=data)
        self.assertTrue(serializer.is_valid())