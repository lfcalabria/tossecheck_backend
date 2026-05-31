from django.test import TestCase
from api.views import normalizar_cpf, normalizar_telefone, normalizar_nome, calc_ano_nascimento

class TestNormalizarTelefone(TestCase):
    def test_telefone_formatado(self):
        """Telefone com máscara retorna apenas dígitos."""
        self.assertEqual(normalizar_telefone('(81) 99999-9999'), '81999999999')

    def test_telefone_none(self):
        """None retorna string vazia."""
        self.assertEqual(normalizar_telefone(None), '')

    def test_telefone_vazio(self):
        """String vazia retorna string vazia."""
        self.assertEqual(normalizar_telefone(''), '')

    def test_telefone_ja_limpo(self):
        """Telefone já sem formatação retorna igual."""
        self.assertEqual(normalizar_telefone('81999999999'), '81999999999')
