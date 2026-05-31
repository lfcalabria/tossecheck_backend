from datetime import datetime
from django.test import TestCase
from model_bakery import baker
from api.models import *

class ModelStrTests(TestCase):
    def test_usuario_str(self):
        """Test that Usuario.__str__ returns the nome."""
        usuario = baker.make(Usuario, nome='João Silva')
        self.assertEqual(str(usuario), 'João Silva')

    def test_pet_str(self):
        """Test that Pet.__str__ returns the nome."""
        pet = baker.make(Pet, nome='Rex')
        self.assertEqual(str(pet), 'Rex')

    def test_veterinario_str(self):
        """Test that Veterinario.__str__ returns the formatted string."""
        vet = baker.make(Veterinario, nome='Maria', crmv='12345')
        self.assertEqual(str(vet), 'Dr(a). Maria - CRMV: 12345')

    def test_observacao_str(self):
        """Test that Observacao.__str__ returns the observation info."""
        vet = baker.make(Veterinario, nome='Carlos')
        obs = baker.make(
            Observacao,
            veterinario=vet,
            data_cadastro=datetime(2025, 1, 1, 10, 0)  # ✅ datetime object
        )
        expected = "Obs do Dr(a). Carlos em 01/01/2025"
        self.assertEqual(str(obs), expected)
