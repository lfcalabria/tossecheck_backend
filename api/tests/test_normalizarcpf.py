from django.test import TestCase
from api.views import normalizar_cpf, normalizar_telefone, normalizar_nome, calc_ano_nascimento

class TestNormalizarCpf(TestCase):
    def test_cpf_com_pontos_e_tracos(self):
        """CPF formatado retorna apenas dígitos."""
        self.assertEqual(normalizar_cpf('123.456.789-01'), '12345678901')

    def test_cpf_apenas_digitos(self):
        """CPF já limpo retorna igual."""
        self.assertEqual(normalizar_cpf('12345678901'), '12345678901')

    def test_cpf_none(self):
        """None retorna string vazia."""
        self.assertEqual(normalizar_cpf(None), '')          # ← cobre `return ''`

    def test_cpf_vazio(self):
        """String vazia retorna string vazia."""
        self.assertEqual(normalizar_cpf(''), '')

    def test_cpf_com_letras(self):
        """CPF com letras retorna apenas dígitos."""
        self.assertEqual(normalizar_cpf('abc123def456ghi'), '123456')
