"""
import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Usuario, Pet, VideoPet, Veterinario, Observacao


# ==========================================
# APIS DO APLICATIVO FLUTTER (TUTORES)
# ==========================================

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
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@csrf_exempt
def sync_pet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            idade = data.get('idade')
            ano_nascimento = None
            if idade is not None:
                ano_nascimento = datetime.now().year - int(idade)

            tipo = data.get('tipo')
            if tipo not in ['Gato', 'Cachorro']:
                return JsonResponse({'erro': 'Tipo inválido. Use Gato ou Cachorro.'}, status=400)

            novo_pet = Pet.objects.create(
                usuario_uuid=data.get('usuario_uuid'),
                nome=data.get('nome'),
                tipo=tipo,
                sexo=data.get('sexo'),
                raca=data.get('raca'),
                idade=idade,
                peso=data.get('peso'),
                altura=data.get('altura')
            )

            return JsonResponse({
                'uuid': str(novo_pet.uuid),
                'usuario_uuid': str(novo_pet.usuario_uuid),
                'nome': novo_pet.nome,
                'tipo': novo_pet.tipo,
                'sexo': novo_pet.sexo,
                'raca': novo_pet.raca,
                'idade': novo_pet.idade,
                'ano_nascimento': ano_nascimento,
                'peso': novo_pet.peso,
                'altura': novo_pet.altura,
            }, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


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
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


# ==========================================
# APIS DO PORTAL WEB (VETERINÁRIOS)
# ==========================================

@csrf_exempt
def api_vet_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            crmv_informado = data.get('username')
            senha_informada = data.get('password')

            vet = Veterinario.objects.filter(
                crmv=crmv_informado,
                senha=senha_informada,
                ativo=True
            ).first()

            if vet:
                return JsonResponse({
                    'status': 'success',
                    'vet_uuid': str(vet.uuid),
                    'vet_nome': vet.nome
                }, status=200)
            else:
                vet_inativo = Veterinario.objects.filter(
                    crmv=crmv_informado,
                    senha=senha_informada,
                    ativo=False
                ).first()

                if vet_inativo:
                    return JsonResponse(
                        {'erro': 'Acesso bloqueado. Este cadastro de veterinário está inativo.'},
                        status=403
                    )

                return JsonResponse({'erro': 'CRMV ou senha inválidos'}, status=401)

        except Exception as e:
            return JsonResponse({'erro': f'Erro interno da API: {str(e)}'}, status=400)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            crmv = data.get('crmv')
            senha = data.get('senha')

            if not crmv or not senha:
                return JsonResponse({'erro': 'CRMV e senha são obrigatórios.'}, status=400)

            try:
                vet = Veterinario.objects.get(crmv=crmv, ativo=True)

                if senha == vet.senha:
                    return JsonResponse({
                        'token': str(vet.uuid),
                        'veterinario': {
                            'nome': vet.nome,
                            'crmv': vet.crmv,
                            'uuid': str(vet.uuid)
                        }
                    }, status=200)
                else:
                    return JsonResponse({'erro': 'Senha incorreta.'}, status=401)

            except Veterinario.DoesNotExist:
                return JsonResponse({'erro': 'CRMV não encontrado ou inativo.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Formato de dados inválido.'}, status=400)

    return JsonResponse({'erro': 'Método não permitido.'}, status=405)


def normalizar_cpf(valor):
    if valor is None:
        return ''
    return ''.join(ch for ch in str(valor) if ch.isdigit())


@csrf_exempt
def api_responsaveis(request):
    if request.method == 'GET':
        cpf_digitado = request.GET.get('q', '').strip()

        if not cpf_digitado:
            return JsonResponse({'erro': 'CPF não informado.'}, status=400)

        cpf_normalizado = normalizar_cpf(cpf_digitado)

        if not cpf_normalizado:
            return JsonResponse({'erro': 'CPF inválido.'}, status=400)

        try:
            usuario = Usuario.objects.get(cpf=cpf_normalizado)
        except Usuario.DoesNotExist:
            return JsonResponse({'erro': 'Responsável não encontrado.'}, status=404)

        return JsonResponse({
            'id': usuario.id,
            'uuid': str(usuario.uuid),
            'nome': usuario.nome,
            'cpf': usuario.cpf,
            'telefone': usuario.telefone,
            'bloqueado': usuario.bloqueado,
            'liberado': usuario.liberado,
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            cpf = data.get('cpf')
            telefone = data.get('telefone')

            if not nome or not cpf or not telefone:
                return JsonResponse({'erro': 'Nome, CPF e telefone são obrigatórios.'}, status=400)

            cpf_norm = normalizar_cpf(cpf)

            novo_usuario = Usuario.objects.create(
                nome=nome,
                cpf=cpf_norm,
                telefone=telefone,
                bloqueado=False,
                liberado=True
            )

            return JsonResponse({
                'id': novo_usuario.id,
                'uuid': str(novo_usuario.uuid),
                'nome': novo_usuario.nome,
                'cpf': novo_usuario.cpf,
                'telefone': novo_usuario.telefone,
                'bloqueado': novo_usuario.bloqueado,
                'liberado': novo_usuario.liberado,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Formato JSON inválido.'}, status=400)

    return JsonResponse({'erro': 'Método não permitido.'}, status=405)


@csrf_exempt
def api_pets_responsavel(request, responsavel_uuid):
    if request.method != 'GET':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        usuario = Usuario.objects.get(uuid=responsavel_uuid)
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Responsável não encontrado.'}, status=404)

    pets = Pet.objects.filter(usuario_uuid=usuario.uuid)

    lista_pets = []
    for pet in pets:
        ano_nascimento = None
        if pet.idade is not None:
            ano_nascimento = datetime.now().year - int(pet.idade)

        lista_pets.append({
            'uuid': str(pet.uuid),
            'usuario_uuid': str(pet.usuario_uuid),
            'nome': pet.nome,
            'tipo': pet.tipo,
            'sexo': pet.sexo,
            'raca': pet.raca,
            'idade': pet.idade,
            'ano_nascimento': ano_nascimento,
            'peso': pet.peso,
            'altura': pet.altura,
        })

    return JsonResponse({
        'responsavel_uuid': str(usuario.uuid),
        'responsavel_nome': usuario.nome,
        'pets': lista_pets,
    }, status=200)


@csrf_exempt
def api_pets(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body)

        responsavel_uuid = data.get('usuario_uuid') or data.get('responsavel_uuid')
        nome = data.get('nome')
        tipo = data.get('tipo')
        sexo = data.get('sexo')
        raca = data.get('raca')
        peso = data.get('peso')
        altura = data.get('altura')
        idade = data.get('idade')

        if not responsavel_uuid:
            return JsonResponse({'erro': 'Usuário responsável não informado.'}, status=400)

        if not nome:
            return JsonResponse({'erro': 'Nome é obrigatório.'}, status=400)

        if not tipo:
            return JsonResponse({'erro': 'Tipo é obrigatório.'}, status=400)

        if tipo not in ['Gato', 'Cachorro']:
            return JsonResponse({'erro': 'Tipo inválido. Use Gato ou Cachorro.'}, status=400)

        try:
            usuario = Usuario.objects.get(uuid=responsavel_uuid)
        except Usuario.DoesNotExist:
            return JsonResponse({'erro': 'Responsável não encontrado.'}, status=404)

        if idade is not None:
            idade = int(idade)

        novo_pet = Pet.objects.create(
            usuario_uuid=usuario.uuid,
            nome=nome,
            tipo=tipo,
            sexo=sexo if sexo else None,
            raca=raca if raca else None,
            peso=peso if peso != '' else None,
            altura=altura if altura != '' else None,
            idade=idade
        )

        ano_nascimento = None
        if novo_pet.idade is not None:
            ano_nascimento = datetime.now().year - int(novo_pet.idade)

        return JsonResponse({
            'uuid': str(novo_pet.uuid),
            'usuario_uuid': str(usuario.uuid),
            'nome': novo_pet.nome,
            'tipo': novo_pet.tipo,
            'sexo': novo_pet.sexo,
            'raca': novo_pet.raca,
            'peso': novo_pet.peso,
            'altura': novo_pet.altura,
            'idade': novo_pet.idade,
            'ano_nascimento': ano_nascimento,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=400)
"""
import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Usuario, Pet, VideoPet, Veterinario, Observacao


# ============================================================
# UTILITÁRIOS (evitam repetição e deixam o código mais robusto)
# ============================================================

def json_body(request):
    """
    Lê o corpo JSON da requisição e retorna um dict.
    Se não for JSON válido, levanta ValueError.
    """
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        data = json.loads(body)
        if not isinstance(data, dict):
            raise ValueError("JSON deve ser um objeto (dict).")
        return data
    except json.JSONDecodeError:
        raise ValueError("Formato JSON inválido.")

def error(message, status=400):
    """Resposta padrão de erro."""
    return JsonResponse({"erro": message}, status=status)

def ok(data, status=200):
    """Resposta padrão de sucesso."""
    return JsonResponse(data, status=status, safe=isinstance(data, dict))

def normalizar_cpf(valor):
    """Remove caracteres não numéricos do CPF."""
    if valor is None:
        return ""
    return "".join(ch for ch in str(valor) if ch.isdigit())

def calc_ano_nascimento(idade):
    """Calcula ano de nascimento aproximado a partir da idade."""
    if idade is None or idade == "":
        return None
    try:
        return datetime.now().year - int(idade)
    except (ValueError, TypeError):
        return None


# ============================================================
# APIS DO APLICATIVO FLUTTER (TUTORES)
# ============================================================

@csrf_exempt
def sync_usuario(request):
    """
    POST /sync/usuario
    Cria um usuário e retorna o UUID.
    """
    if request.method != "POST":
        return error("Método não permitido", status=405)

    try:
        data = json_body(request)

        nome = data.get("nome")
        cpf = normalizar_cpf(data.get("cpf"))
        telefone = data.get("telefone")

        if not nome or not cpf or not telefone:
            return error("Campos obrigatórios: nome, cpf, telefone.", status=400)

        novo_usuario = Usuario.objects.create(
            nome=nome,
            cpf=cpf,
            telefone=telefone
        )
        return ok({"uuid": str(novo_usuario.uuid)}, status=201)

    except ValueError as e:
        return error(str(e), status=400)
    except Exception as e:
        return error(str(e), status=400)


@csrf_exempt
def sync_pet(request):
    """
    POST /sync/pet
    Cria um pet associado ao usuário (usuario_uuid).
    """
    if request.method != "POST":
        return error("Método não permitido", status=405)

    try:
        data = json_body(request)

        usuario_uuid = data.get("usuario_uuid")
        nome = data.get("nome")
        tipo = data.get("tipo")
        sexo = data.get("sexo")
        raca = data.get("raca")
        idade = data.get("idade")
        peso = data.get("peso")
        altura = data.get("altura")

        if not usuario_uuid:
            return error("usuario_uuid é obrigatório.", status=400)
        if not nome:
            return error("nome é obrigatório.", status=400)
        if not tipo:
            return error("tipo é obrigatório.", status=400)

        if tipo not in ["Gato", "Cachorro"]:
            return error("Tipo inválido. Use Gato ou Cachorro.", status=400)

        # Se você quiser garantir que o usuário existe:
        try:
            usuario = Usuario.objects.get(uuid=usuario_uuid)
        except Usuario.DoesNotExist:
            return error("Usuário responsável não encontrado.", status=404)

        # Normalização da idade
        if idade is not None and idade != "":
            try:
                idade = int(idade)
            except ValueError:
                return error("idade deve ser um inteiro.", status=400)

        novo_pet = Pet.objects.create(
            usuario_uuid=usuario.uuid,  # mantém como UUID (conforme seu modelo aparenta usar)
            nome=nome,
            tipo=tipo,
            sexo=sexo if sexo else None,
            raca=raca if raca else None,
            idade=idade,
            peso=peso if peso not in [None, ""] else None,
            altura=altura if altura not in [None, ""] else None
        )

        return ok({
            "uuid": str(novo_pet.uuid),
            "usuario_uuid": str(novo_pet.usuario_uuid),
            "nome": novo_pet.nome,
            "tipo": novo_pet.tipo,
            "sexo": novo_pet.sexo,
            "raca": novo_pet.raca,
            "idade": novo_pet.idade,
            "ano_nascimento": calc_ano_nascimento(novo_pet.idade),
            "peso": novo_pet.peso,
            "altura": novo_pet.altura,
        }, status=201)

    except ValueError as e:
        return error(str(e), status=400)
    except Exception as e:
        return error(str(e), status=400)


@csrf_exempt
def upload_video(request):
    """
    POST /upload/video
    Espera multipart/form-data:
      - pet_uuid (campo do form)
      - file (arquivo em request.FILES)
    """
    if request.method != "POST":
        return error("Método não permitido", status=405)

    try:
        pet_uuid = request.POST.get("pet_uuid")
        arquivo_fisico = request.FILES.get("file")

        if not pet_uuid:
            return error("pet_uuid é obrigatório.", status=400)
        if not arquivo_fisico:
            return error("Arquivo 'file' é obrigatório.", status=400)

        # Se quiser garantir que o pet existe:
        try:
            Pet.objects.get(uuid=pet_uuid)
        except Pet.DoesNotExist:
            return error("Pet não encontrado.", status=404)

        novo_video = VideoPet.objects.create(
            pet_uuid=pet_uuid,
            arquivo=arquivo_fisico
        )

        return ok({"uuid": str(novo_video.uuid)}, status=201)

    except Exception as e:
        return error(str(e), status=400)


# ============================================================
# APIS DO PORTAL WEB (VETERINÁRIOS)
# ============================================================

@csrf_exempt
def api_login(request):
    """
    POST /api/login/
    Body JSON:
      - crmv
      - senha
    Retorna um "token" simples (uuid do veterinário) e dados do veterinário.
    """
    if request.method != "POST":
        return error("Método não permitido.", status=405)

    try:
        data = json_body(request)
        crmv = data.get("crmv")
        senha = data.get("senha")

        if not crmv or not senha:
            return error("CRMV e senha são obrigatórios.", status=400)

        try:
            vet = Veterinario.objects.get(crmv=crmv, ativo=True)
        except Veterinario.DoesNotExist:
            return error("CRMV não encontrado ou inativo.", status=404)

        if senha != vet.senha:
            return error("Senha incorreta.", status=401)

        return ok({
            "token": str(vet.uuid),
            "veterinario": {
                "nome": vet.nome,
                "crmv": vet.crmv,
                "uuid": str(vet.uuid)
            }
        }, status=200)

    except ValueError as e:
        return error(str(e), status=400)
    except Exception as e:
        return error(f"Erro interno da API: {str(e)}", status=400)


@csrf_exempt
def api_responsavel(request):
    """
    GET /api/responsaveis/?q=CPF
      - Busca usuário por CPF (normalizado)
    POST /api/responsaveis/
      - Cria usuário (nome, cpf, telefone)
    """
    if request.method == "GET":
        cpf_digitado = (request.GET.get("q") or "").strip()
        if not cpf_digitado:
            return error("CPF não informado.", status=400)

        cpf_normalizado = normalizar_cpf(cpf_digitado)
        if not cpf_normalizado:
            return error("CPF inválido.", status=400)

        try:
            usuario = Usuario.objects.get(cpf=cpf_normalizado)
        except Usuario.DoesNotExist:
            return error("Responsável não encontrado.", status=404)

        return ok({
            "id": usuario.id,
            "uuid": str(usuario.uuid),
            "nome": usuario.nome,
            "cpf": usuario.cpf,
            "telefone": usuario.telefone,
            "bloqueado": usuario.bloqueado,
            "liberado": usuario.liberado,
        }, status=200)

    elif request.method == "POST":
        try:
            data = json_body(request)
            nome = data.get("nome")
            cpf = data.get("cpf")
            telefone = data.get("telefone")

            if not nome or not cpf or not telefone:
                return error("Nome, CPF e telefone são obrigatórios.", status=400)

            cpf_norm = normalizar_cpf(cpf)
            if not cpf_norm:
                return error("CPF inválido.", status=400)

            novo_usuario = Usuario.objects.create(
                nome=nome,
                cpf=cpf_norm,
                telefone=telefone,
                bloqueado=False,
                liberado=True
            )

            return ok({
                "id": novo_usuario.id,
                "uuid": str(novo_usuario.uuid),
                "nome": novo_usuario.nome,
                "cpf": novo_usuario.cpf,
                "telefone": novo_usuario.telefone,
                "bloqueado": novo_usuario.bloqueado,
                "liberado": novo_usuario.liberado,
            }, status=201)

        except ValueError as e:
            return error(str(e), status=400)
        except Exception as e:
            return error(str(e), status=400)

    return error("Método não permitido.", status=405)


@csrf_exempt
def api_pets_responsavel(request, responsavel_uuid):
    """
    GET /api/responsaveis/<uuid:responsavel_uuid>/pets/
    Lista pets de um responsável.
    """
    if request.method != "GET":
        return error("Método não permitido.", status=405)

    try:
        usuario = Usuario.objects.get(uuid=responsavel_uuid)
    except Usuario.DoesNotExist:
        return error("Responsável não encontrado.", status=404)

    pets = Pet.objects.filter(usuario_uuid=usuario.uuid)

    lista_pets = []
    for pet in pets:
        lista_pets.append({
            "uuid": str(pet.uuid),
            "usuario_uuid": str(pet.usuario_uuid),
            "nome": pet.nome,
            "tipo": pet.tipo,
            "sexo": pet.sexo,
            "raca": pet.raca,
            "idade": pet.idade,
            "ano_nascimento": calc_ano_nascimento(pet.idade),
            "peso": pet.peso,
            "altura": pet.altura,
        })

    return ok({
        "responsavel_uuid": str(usuario.uuid),
        "responsavel_nome": usuario.nome,
        "pets": lista_pets,
    }, status=200)


@csrf_exempt
def api_pets(request):
    """
    POST /api/pets/
    Cria um pet a partir do portal.
    Body JSON:
      - usuario_uuid (ou responsavel_uuid)
      - nome, tipo, sexo?, raca?, peso?, altura?, idade?
    """
    if request.method != "POST":
        return error("Método não permitido.", status=405)

    try:
        data = json_body(request)

        responsavel_uuid = data.get("usuario_uuid") or data.get("responsavel_uuid")
        nome = data.get("nome")
        tipo = data.get("tipo")
        sexo = data.get("sexo")
        raca = data.get("raca")
        peso = data.get("peso")
        altura = data.get("altura")
        idade = data.get("idade")

        if not responsavel_uuid:
            return error("Usuário responsável não informado.", status=400)
        if not nome:
            return error("Nome é obrigatório.", status=400)
        if not tipo:
            return error("Tipo é obrigatório.", status=400)
        if tipo not in ["Gato", "Cachorro"]:
            return error("Tipo inválido. Use Gato ou Cachorro.", status=400)

        try:
            usuario = Usuario.objects.get(uuid=responsavel_uuid)
        except Usuario.DoesNotExist:
            return error("Responsável não encontrado.", status=404)

        if idade is not None and idade != "":
            try:
                idade = int(idade)
            except ValueError:
                return error("idade deve ser um inteiro.", status=400)

        novo_pet = Pet.objects.create(
            usuario_uuid=usuario.uuid,
            nome=nome,
            tipo=tipo,
            sexo=sexo if sexo else None,
            raca=raca if raca else None,
            peso=peso if peso not in [None, ""] else None,
            altura=altura if altura not in [None, ""] else None,
            idade=idade
        )

        return ok({
            "uuid": str(novo_pet.uuid),
            "usuario_uuid": str(usuario.uuid),
            "nome": novo_pet.nome,
            "tipo": novo_pet.tipo,
            "sexo": novo_pet.sexo,
            "raca": novo_pet.raca,
            "peso": novo_pet.peso,
            "altura": novo_pet.altura,
            "idade": novo_pet.idade,
            "ano_nascimento": calc_ano_nascimento(novo_pet.idade),
        }, status=201)

    except ValueError as e:
        return error(str(e), status=400)
    except Exception as e:
        return error(str(e), status=400)


# ============================================================
# (Opcional) API alternativa de login (se você quiser manter)
# ============================================================
@csrf_exempt
def api_vet_login(request):
    """
    POST /api/vet/login/ (não está no seu urls.py atual)
    Body JSON:
      - username (CRMV)
      - password
    """
    if request.method != "POST":
        return error("Método não permitido", status=405)

    try:
        data = json_body(request)
        crmv_informado = data.get("username")
        senha_informada = data.get("password")

        vet = Veterinario.objects.filter(
            crmv=crmv_informado,
            senha=senha_informada
        ).first()

        if not vet:
            return error("CRMV ou senha inválidos", status=401)

        if not vet.ativo:
            return error("Acesso bloqueado. Este cadastro de veterinário está inativo.", status=403)

        return ok({
            "status": "success",
            "vet_uuid": str(vet.uuid),
            "vet_nome": vet.nome
        }, status=200)

    except ValueError as e:
        return error(str(e), status=400)
    except Exception as e:
        return error(f"Erro interno da API: {str(e)}", status=400)

@csrf_exempt
def api_pet_detail(request, pet_uuid):
    """
    GET /api/v1/pets/<uuid>/
    Retorna dados do pet, vídeos e prontuário (observações).
    """

    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    try:
        pet = Pet.objects.get(uuid=pet_uuid)
    except Pet.DoesNotExist:
        return JsonResponse({"erro": "Pet não encontrado."}, status=404)

    # Vídeos do pet
    videos = VideoPet.objects.filter(pet_uuid=str(pet.uuid))

    # ✅ Agora funciona: Observacao tem pet_uuid
    observacoes = Observacao.objects.filter(
        pet_uuid=str(pet.uuid)
    ).order_by("-data_cadastro")

    return JsonResponse({
        "uuid": str(pet.uuid),
        "usuario_uuid": str(pet.usuario_uuid),
        "nome": pet.nome,
        "tipo": pet.tipo,
        "sexo": pet.sexo,
        "raca": pet.raca,
        "idade": pet.idade,
        "peso": pet.peso,
        "altura": pet.altura,

        "videos": [
            {
                "uuid": str(v.uuid),
                "url": v.arquivo.url,
                "data_upload": v.data_upload.strftime("%d/%m/%Y %H:%M")
            } for v in videos
        ],

        "prontuario": [
            {
                "uuid": str(o.uuid),
                "texto": o.mensagem,
                "data": o.data_cadastro.strftime("%d/%m/%Y %H:%M"),
                "veterinario": o.veterinario.nome
            } for o in observacoes
        ]
    }, status=200)

@csrf_exempt
def api_pet_observacao(request, pet_uuid):
    """
    POST /api/v1/pets/<uuid>/observacoes/
    Cria uma observação ligada diretamente ao PET.
    """

    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    try:
        data = json.loads(request.body)
        texto = data.get("texto", "").strip()

        if not texto:
            return JsonResponse({"erro": "Observação vazia."}, status=400)

        try:
            pet = Pet.objects.get(uuid=pet_uuid)
        except Pet.DoesNotExist:
            return JsonResponse({"erro": "Pet não encontrado."}, status=404)

        # OBSERVAÇÃO LIGADA AO PET (modelo corrigido)
        obs = Observacao.objects.create(
            pet_uuid=str(pet.uuid),
            veterinario=Veterinario.objects.first(),  # ajuste depois para auth real
            mensagem=texto
        )

        return JsonResponse({
            "uuid": str(obs.uuid),
            "texto": obs.mensagem,
            "data": obs.data_cadastro.strftime("%d/%m/%Y %H:%M"),
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)