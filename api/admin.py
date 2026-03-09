from django.contrib import admin
from .models import Usuario, Pet, VideoPet

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