from rest_framework import serializers
from .models import Usuario, Pet, Video, Observacao


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'uuid', 'username', 'cpf', 'telefone', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'uuid', 'criado_em', 'atualizado_em']


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'cpf', 'telefone', 'password']

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user


class PetSerializer(serializers.ModelSerializer):
    idade = serializers.ReadOnlyField()
    usuario_nome = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Pet
        fields = [
            'id', 'uuid', 'usuario', 'usuario_nome', 'nome', 'sexo', 'raca',
            'altura', 'peso', 'data_nascimento', 'idade', 'tipo', 'foto',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'uuid', 'usuario', 'criado_em', 'atualizado_em']


class VideoSerializer(serializers.ModelSerializer):
    pet_nome = serializers.ReadOnlyField(source='pet.nome')

    class Meta:
        model = Video
        fields = ['id', 'uuid', 'pet', 'pet_nome', 'arquivo', 'duracao', 'criado_em']
        read_only_fields = ['id', 'uuid', 'criado_em']


class ObservacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observacao
        fields = ['id', 'uuid', 'video', 'texto', 'criado_em']
        read_only_fields = ['id', 'uuid', 'criado_em']