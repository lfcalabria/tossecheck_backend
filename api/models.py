import uuid
from django.db import models
from django.contrib.auth.hashers import make_password

class Usuario(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, null=True, blank=True, unique=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    bloqueado = models.BooleanField(default=False)
    liberado = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Pet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario_uuid = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    sexo = models.CharField(max_length=20, null=True, blank=True)
    raca = models.CharField(max_length=100, null=True, blank=True)
    idade = models.IntegerField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    altura = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nome


class VideoPet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pet_uuid = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='videos/')
    data_upload = models.DateTimeField(auto_now_add=True)


class Veterinario(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    crmv = models.CharField(max_length=20, unique=True, help_text="Conselho Regional de Medicina Veterinária")
    senha = models.CharField(max_length=200)
    email = models.EmailField(null=False, blank=False, unique=True, max_length=200, default='noreplay@tecnologiasinternet.com')
    ativo = models.BooleanField(default=True, help_text="Desmarque para bloquear o acesso deste veterinário")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def set_senha(self, senha_plana):
        self.senha = make_password(senha_plana)
        self.save(update_fields=['senha'])

    def __str__(self):
        return f"Dr(a). {self.nome} - CRMV: {self.crmv}"

class RedefinicaoSenhaToken(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Token {self.token[:8]}... - {self.veterinario.nome}"

class Observacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pet_uuid = models.CharField(max_length=100)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    mensagem = models.TextField(help_text="Diagnóstico ou observação sobre a tosse")
    automatica = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Obs do Dr(a). {self.veterinario.nome} em {self.data_cadastro.strftime('%d/%m/%Y')}"

class VideoClassificacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    video_uuid = models.CharField(max_length=100)
    duracao = models.CharField(max_length=15)
    tipo_som = models.CharField(max_length=15)
    fator = models.CharField(max_length=25)
    estridor = models.BooleanField(default=False)
    estertor = models.BooleanField(default=False)
    obs = models.TextField(null=True, blank=True)
    veterinario_uuid = models.CharField(max_length=100)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Classificação {self.uuid} - Vídeo {self.video_uuid}"
