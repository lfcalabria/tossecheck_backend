from django.urls import path
from . import views

urlpatterns = [
    path('sync/usuario', views.sync_usuario, name='sync_usuario'),
    path('sync/pet', views.sync_pet, name='sync_pet'),
    path('upload/video', views.upload_video, name='upload_video'),
]