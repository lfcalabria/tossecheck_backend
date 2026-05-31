from datetime import datetime
from django.test import TestCase
from api.views import normalizar_cpf, normalizar_telefone, normalizar_nome, calc_ano_nascimento

class TestCalcAnoNascimento(TestCase):
    def test_idade_valida(self):
        """Idade 5 retorna ano atual - 5."""
        self.assertEqual(calc_ano_nascimento(5), datetime.now().year - 5)

    def test_idade_string_numerica(self):
        """String '5' é convertida para int."""
        self.assertEqual(calc_ano_nascimento('5'), datetime.now().year - 5)

    def test_idade_string_nao_numerica(self):
        """String não numérica retorna None (except)."""
        self.assertIsNone(calc_ano_nascimento('abc'))

    def test_idade_none(self):
        """None retorna None (except)."""
        self.assertIsNone(calc_ano_nascimento(None))

    def test_idade_zero(self):
        """Idade 0 retorna ano atual."""
        self.assertEqual(calc_ano_nascimento(0), datetime.now().year)