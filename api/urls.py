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

    # ✅ NOVA ROTA: lista pets do tutor
    path("api/v1/tutor/pets/", views_tutor.tutor_pets),
]