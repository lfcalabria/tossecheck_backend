from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UsuarioViewSet, PetViewSet, VideoViewSet, ObservacaoViewSet,
    sync_usuario, sync_pet, upload_video, sync_observacao, health_check
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'observacoes', ObservacaoViewSet, basename='observacao')

urlpatterns = [
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Health check
    path('health', health_check, name='health_check'),

    # Sincronização (para o app Flutter)
    path('sync/usuario', sync_usuario, name='sync_usuario'),
    path('sync/pet', sync_pet, name='sync_pet'),
    path('upload/video', upload_video, name='upload_video'),
    path('sync/observacao', sync_observacao, name='sync_observacao'),

    # ViewSets
    path('', include(router.urls)),
]