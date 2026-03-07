from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Usuario(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['username', 'telefone']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} - {self.cpf}'


class Pet(models.Model):
    TIPO_CHOICES = [
        ('Cachorro', 'Cachorro'),
        ('Gato', 'Gato'),
    ]

    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pets')
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    raca = models.CharField(max_length=100)
    altura = models.FloatField()
    peso = models.FloatField()
    data_nascimento = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    foto = models.ImageField(upload_to='pets/fotos/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pet'
        verbose_name_plural = 'Pets'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} ({self.tipo})'

    @property
    def idade(self):
        from datetime import date
        today = date.today()
        return today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='videos')
    arquivo = models.FileField(upload_to='pets/videos/')
    duracao = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Video de {self.pet.nome} - {self.criado_em}'


class Observacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='observacoes')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Observacao'
        verbose_name_plural = 'Observacoes'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Observacao - {self.criado_em}'