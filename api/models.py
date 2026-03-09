import uuid
from django.db import models


class Usuario(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nome


class Pet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario_uuid = models.CharField(max_length=100)  # Referência ao dono
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
    pet_uuid = models.CharField(max_length=100)  # Referência ao pet
    arquivo = models.FileField(upload_to='videos/')  # Salvará fisicamente em /media/videos/
    data_upload = models.DateTimeField(auto_now_add=True)