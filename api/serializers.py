from rest_framework import serializers
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'uuid', 'nome', 'cpf', 'telefone', 'bloqueado', 'liberado']
        read_only_fields = ['id', 'uuid']

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'uuid', 'usuario_uuid', 'nome', 'tipo', 'sexo', 'raca',
                  'idade', 'peso', 'altura']
        read_only_fields = ['id', 'uuid']

class VideoPetSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPet
        fields = ['id', 'uuid', 'pet_uuid', 'arquivo', 'data_upload']
        read_only_fields = ['id', 'uuid', 'data_upload']

class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = ['id', 'uuid', 'nome', 'crmv', 'email', 'ativo',
                  'data_criacao', 'data_alteracao']
        read_only_fields = ['id', 'uuid', 'data_criacao', 'data_alteracao']

class ObservacaoSerializer(serializers.ModelSerializer):
    veterinario_nome = serializers.ReadOnlyField(source='veterinario.nome')

    class Meta:
        model = Observacao
        fields = ['id', 'uuid', 'pet_uuid', 'veterinario', 'veterinario_nome',
                  'mensagem', 'data_cadastro']
        read_only_fields = ['id', 'uuid', 'data_cadastro']

class VideoClassificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoClassificacao
        fields = ['id', 'uuid', 'video_uuid', 'duracao', 'tipo_som', 'fator',
                  'estridor', 'estertor', 'obs', 'veterinario_uuid', 'data_cadastro']
        read_only_fields = ['id', 'uuid', 'data_cadastro']