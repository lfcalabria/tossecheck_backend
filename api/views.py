from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import Usuario, Pet, Video, Observacao
from .serializers import (
    UsuarioSerializer, UsuarioRegistroSerializer,
    PetSerializer, VideoSerializer, ObservacaoSerializer
)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Usuario.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Video.objects.filter(pet__usuario=self.request.user)


class ObservacaoViewSet(viewsets.ModelViewSet):
    queryset = Observacao.objects.all()
    serializer_class = ObservacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Observacao.objects.filter(video__pet__usuario=self.request.user)


# Sincronização endpoints (para o app Flutter)
@api_view(['POST'])
@permission_classes([AllowAny])
def sync_usuario(request):
    """
    Sincroniza usuário do app Flutter com o backend.
    Recebe dados do usuário e retorna UUID do servidor.
    """
    cpf = request.data.get('cpf')

    if not cpf:
        return Response({'error': 'CPF é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar se usuário já existe pelo CPF
    usuario = Usuario.objects.filter(cpf=cpf).first()

    if usuario:
        # Atualizar dados existentes
        usuario.nome = request.data.get('nome', usuario.username)
        usuario.telefone = request.data.get('telefone', usuario.telefone)
        usuario.save()
    else:
        # Criar novo usuário
        serializer = UsuarioRegistroSerializer(data={
            'username': request.data.get('nome', cpf),
            'cpf': cpf,
            'telefone': request.data.get('telefone', ''),
            'password': cpf  # Senha temporária
        })

        if serializer.is_valid():
            usuario = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'uuid': str(usuario.uuid)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def sync_pet(request):
    """
    Sincroniza pet do app Flutter com o backend.
    """
    usuario_uuid = request.data.get('usuario_uuid')
    cpf = request.data.get('cpf')

    if not usuario_uuid and not cpf:
        return Response({'error': 'UUID do usuário ou CPF é obrigatório'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Buscar usuário
    if usuario_uuid:
        usuario = get_object_or_404(Usuario, uuid=usuario_uuid)
    else:
        usuario = get_object_or_404(Usuario, cpf=cpf)

    # Criar ou atualizar pet
    pet_uuid = request.data.get('uuid')

    if pet_uuid:
        pet = Pet.objects.filter(uuid=pet_uuid, usuario=usuario).first()
        if pet:
            # Atualizar pet existente
            pet.nome = request.data.get('nome', pet.nome)
            pet.sexo = request.data.get('sexo', pet.sexo)
            pet.raca = request.data.get('raca', pet.raca)
            pet.altura = request.data.get('altura', pet.altura)
            pet.peso = request.data.get('peso', pet.peso)
            pet.tipo = request.data.get('tipo', pet.tipo)
            pet.save()
            return Response({'uuid': str(pet.uuid)}, status=status.HTTP_200_OK)

    # Criar novo pet
    from datetime import datetime
    data_nascimento = request.data.get('dataNascimento')
    if isinstance(data_nascimento, str):
        data_nascimento = datetime.fromisoformat(data_nascimento.replace('Z', '+00:00')).date()

    pet = Pet.objects.create(
        usuario=usuario,
        nome=request.data.get('nome'),
        sexo=request.data.get('sexo'),
        raca=request.data.get('raca'),
        altura=request.data.get('altura', 0),
        peso=request.data.get('peso', 0),
        data_nascimento=data_nascimento or datetime.now().date(),
        tipo=request.data.get('tipo', 'Cachorro')
    )

    return Response({'uuid': str(pet.uuid)}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_video(request):
    """
    Upload de vídeo do app Flutter.
    """
    pet_uuid = request.data.get('pet_uuid')

    if not pet_uuid:
        return Response({'error': 'UUID do pet é obrigatório'},
                        status=status.HTTP_400_BAD_REQUEST)

    pet = get_object_or_404(Pet, uuid=pet_uuid)

    if 'file' not in request.FILES:
        return Response({'error': 'Arquivo de vídeo é obrigatório'},
                        status=status.HTTP_400_BAD_REQUEST)

    video = Video.objects.create(
        pet=pet,
        arquivo=request.FILES['file'],
        duracao=request.data.get('duracao', 0)
    )

    return Response({'uuid': str(video.uuid)}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def sync_observacao(request):
    """
    Sincroniza observação do app Flutter.
    """
    video_uuid = request.data.get('video_uuid')
    texto = request.data.get('texto')

    if not video_uuid or not texto:
        return Response({'error': 'UUID do vídeo e texto são obrigatórios'},
                        status=status.HTTP_400_BAD_REQUEST)

    video = get_object_or_404(Video, uuid=video_uuid)

    observacao = Observacao.objects.create(
        video=video,
        texto=texto
    )

    return Response({'uuid': str(observacao.uuid)}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint para verificar se o backend está online.
    """
    return Response({'status': 'ok', 'message': 'TosseCheck API is running'},
                    status=status.HTTP_200_OK)