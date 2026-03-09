import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Pet, VideoPet


@csrf_exempt
def sync_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            novo_usuario = Usuario.objects.create(
                nome=data.get('nome'),
                cpf=data.get('cpf'),
                telefone=data.get('telefone')
            )
            return JsonResponse({'uuid': str(novo_usuario.uuid)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)


@csrf_exempt
def sync_pet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            novo_pet = Pet.objects.create(
                usuario_uuid=data.get('usuario_uuid'),
                nome=data.get('nome'),
                tipo=data.get('tipo'),
                sexo=data.get('sexo'),
                raca=data.get('raca'),
                idade=data.get('idade'),
                peso=data.get('peso'),
                altura=data.get('altura')
            )
            return JsonResponse({'uuid': str(novo_pet.uuid)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)


@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        try:
            pet_uuid = request.POST.get('pet_uuid')
            arquivo_fisico = request.FILES.get('file')

            novo_video = VideoPet.objects.create(
                pet_uuid=pet_uuid,
                arquivo=arquivo_fisico
            )
            return JsonResponse({'uuid': str(novo_video.uuid)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)