from django.test import TestCase
from model_bakery import baker
from api.models import Pet
from api.serializers import PetSerializer

class TestPetSerializer(TestCase):
    def setUp(self):
        self.pet = baker.make(Pet)

    def test_contains_expected_fields(self):
        serializer = PetSerializer(instance=self.pet)
        expected_fields = {'id', 'uuid', 'usuario_uuid', 'nome', 'tipo', 'sexo', 'raca',
                           'idade', 'peso', 'altura'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = PetSerializer(instance=self.pet)
        self.assertIn('id', serializer.data)
        self.assertIn('uuid', serializer.data)

    def test_serialize_values(self):
        serializer = PetSerializer(instance=self.pet)
        self.assertEqual(serializer.data['nome'], self.pet.nome)
        self.assertEqual(serializer.data['tipo'], self.pet.tipo)