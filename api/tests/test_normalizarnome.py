from django.test import TestCase
from api.views import normalizar_cpf, normalizar_telefone, normalizar_nome, calc_ano_nascimento

class TestNormalizarNome(TestCase):
    def test_nome_com_espacos_extras(self):
        """Nome com espaços extras retorna normalizado."""
        self.assertEqual(normalizar_nome('  Maria  Silva  '), 'maria silva')

    def test_nome_maiusculo(self):
        """Nome em maiúsculo retorna minúsculo."""
        self.assertEqual(normalizar_nome('MARIA'), 'maria')

    def test_nome_none(self):
        """None retorna string vazia."""
        self.assertEqual(normalizar_nome(None), '')

    def test_nome_vazio(self):
        """String vazia retorna string vazia."""
        self.assertEqual(normalizar_nome(''), '')

    def test_nome_ja_normalizado(self):
        """Nome já normalizado retorna igual."""
        self.assertEqual(normalizar_nome('joao'), 'joao')

