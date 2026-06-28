from django.contrib import admin
from .models import *

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Colunas que vão aparecer na lista
    list_display = ('nome', 'cpf', 'telefone', 'uuid')
    # Barra de pesquisa
    search_fields = ('nome', 'cpf', 'uuid')
    # O UUID não pode ser editado manualmente
    readonly_fields = ('uuid',)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'raca', 'idade', 'usuario_uuid', 'uuid')
    # Filtros laterais super úteis para analisar os dados
    list_filter = ('tipo', 'raca', 'sexo')
    search_fields = ('nome', 'usuario_uuid', 'uuid')
    readonly_fields = ('uuid',)

@admin.register(VideoPet)
class VideoPetAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_uuid', 'arquivo', 'data_upload', 'uuid')
    list_filter = ('data_upload',)
    search_fields = ('pet_uuid', 'uuid')
    readonly_fields = ('uuid', 'data_upload')


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    # Mostra a bolinha verde/vermelha e as datas na lista
    list_display = ('nome', 'crmv', 'ativo', 'data_criacao')
    # Cria um filtro lateral para buscar só os ativos ou inativos
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'crmv')
    # Impede edição manual do uuid e das datas geradas pelo sistema
    readonly_fields = ('uuid', 'data_criacao', 'data_alteracao')

@admin.register(VideoClassificacao)
class VideoClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'video_uuid', 'tipo_som', 'fator', 'estridor', 'estertor', 'data_cadastro']
    list_filter = ['tipo_som', 'fator', 'estridor', 'estertor']
    search_fields = ['video_uuid', 'veterinario_uuid', 'obs']
    readonly_fields = ['uuid', 'data_cadastro']