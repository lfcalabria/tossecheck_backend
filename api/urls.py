from django.urls import path
from . import views
from . import views_tutor

urlpatterns = [
    # ====== SINCRONIZAÇÃO (mobile/offline) ======
    path("api/v1/sync/usuario/", views.sync_usuario, name="sync_usuario"),
    path("api/v1/sync/pet/", views.sync_pet, name="sync_pet"),

    # ====== UPLOAD ======
    path("api/v1/upload/video/", views.upload_video, name="upload_video"),

    # ====== AUTENTICAÇÃO ======
    path("api/v1/login/", views.api_login, name="api_login"),

    # ====== RESPONSÁVEIS ======
    path("api/v1/responsavel/", views.api_responsavel, name="api_responsavel"),
    path("api/v1/responsavel/<uuid:responsavel_uuid>/pets/", views.api_pets_responsavel, name="api_pets_responsavel"),

    # ====== PETS ======
    path("api/v1/pets/", views.api_pets, name="api_pets"),
    path("api/v1/pets/<uuid:pet_uuid>/", views.api_pet_detail, name="api_pet_detail"),
    path("api/v1/pets/<uuid:pet_uuid>/observacoes/", views.api_pet_observacao, name="api_pet_observacao"),

    # ====== Tutor (Flutter) ======
    path("api/v1/tutor/sync/usuario/", views_tutor.sync_usuario),
    path("api/v1/tutor/sync/pet/", views_tutor.sync_pet),
    path("api/v1/tutor/usuario/", views_tutor.tutor_status_por_cpf),

    # ✅ lista pets do tutor
    path("api/v1/tutor/pets/", views_tutor.tutor_pets),

    # ====== CLASSIFICAÇÃO DE VÍDEO ======
    path("api/v1/video/<uuid:video_uuid>/", views.api_video_detalhe, name="api_video_detalhe"),
    path("api/v1/video/<uuid:video_uuid>/classificacoes/", views.api_video_classificacoes, name="video_classificacoes"),
    path("api/v1/video/classificacao/", views.api_criar_classificacao, name="criar_classificacao"),

    # ====== ESQUECI MINHA SENHA ======
    path("api/v1/esqueci-senha/", views.api_esqueci_senha, name="api_esqueci_senha"),
    path("api/v1/redefinir-senha/", views.api_redefinir_senha, name="api_redefinir_senha"),

    # ====== EDITAR OBSERVAÇÃO ======
    path("api/v1/pets/<uuid:pet_uuid>/observacoes/<uuid:obs_uuid>/", views.api_editar_observacao, name="api_editar_observacao"),
]