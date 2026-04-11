import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Usuario, Pet


# ============================================================
# UTILITÁRIOS
# ============================================================

def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")

def normalizar_nome(nome: str) -> str:
    return (nome or "").strip().lower()

def normalizar_telefone(tel: str) -> str:
    return re.sub(r"\D", "", tel or "")

def cpf_valido(cpf: str) -> bool:
    cpf = limpar_cpf(cpf)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    def calc_digito(nums, peso):
        soma = sum(int(n) * p for n, p in zip(nums, range(peso, 1, -1)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    d1 = calc_digito(cpf[:9], 10)
    d2 = calc_digito(cpf[:9] + str(d1), 11)
    return cpf[-2:] == f"{d1}{d2}"


# ============================================================
# TUTOR – SYNC USUÁRIO (POST)
# ============================================================

@csrf_exempt
def sync_usuario(request):
    """
    POST /api/v1/tutor/sync/usuario/

    Regras:
    - CPF inválido -> 400
    - CPF novo -> cria -> 201
    - CPF existente + dados iguais -> libera -> 200
    - CPF existente + dados diferentes -> bloqueia -> 409
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")

        nome = (data.get("nome") or "").strip()
        cpf = (data.get("cpf") or "").strip()
        telefone = (data.get("telefone") or "").strip()

        if not nome or not cpf or not telefone:
            return JsonResponse({"erro": "nome, cpf e telefone são obrigatórios"}, status=400)

        if not cpf_valido(cpf):
            return JsonResponse({"erro": "CPF inválido"}, status=400)

        cpf = limpar_cpf(cpf)

        usuario = Usuario.objects.filter(cpf=cpf).first()

        # CPF não existe -> cria
        if not usuario:
            novo = Usuario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                liberado=True,
                bloqueado=False,
            )
            return JsonResponse({"uuid": str(novo.uuid)}, status=201)

        # CPF existe -> valida identidade
        nome_ok = normalizar_nome(usuario.nome) == normalizar_nome(nome)
        tel_ok = normalizar_telefone(usuario.telefone) == normalizar_telefone(telefone)

        if nome_ok and tel_ok:
            usuario.bloqueado = False
            usuario.liberado = True
            usuario.save(update_fields=["bloqueado", "liberado"])
            return JsonResponse({"uuid": str(usuario.uuid)}, status=200)

        # Divergiu -> bloqueia
        usuario.bloqueado = True
        usuario.liberado = False
        usuario.save(update_fields=["bloqueado", "liberado"])
        return JsonResponse(
            {"erro": "CPF já cadastrado com dados diferentes", "bloqueado": True},
            status=409,
        )

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)


# ============================================================
# TUTOR – STATUS CANÔNICO (GET)
# ============================================================

@csrf_exempt
def tutor_status_por_cpf(request):
    """
    GET /api/v1/tutor/usuario/?cpf=...
    Retorna dados CANÔNICOS do backend.
    """
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    cpf = limpar_cpf(request.GET.get("cpf", ""))
    if not cpf:
        return JsonResponse({"erro": "CPF não informado"}, status=400)

    usuario = Usuario.objects.filter(cpf=cpf).first()
    if not usuario:
        return JsonResponse({"erro": "Usuário não encontrado"}, status=404)

    return JsonResponse({
        "uuid": str(usuario.uuid),
        "nome": usuario.nome,
        "cpf": usuario.cpf,
        "telefone": usuario.telefone,
        "bloqueado": usuario.bloqueado,
        "liberado": usuario.liberado,
    }, status=200)


# ============================================================
# TUTOR – SYNC PET (POST)  ✅ UPSERT PARA NÃO DUPLICAR
# ============================================================

@csrf_exempt
def sync_pet(request):
    """
    POST /api/v1/tutor/sync/pet/

    UPSERT:
    - Se vier uuid e existir -> ATUALIZA
    - Se não vier uuid (ou não existir) -> CRIA
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")

        usuario_uuid = data.get("usuario_uuid")
        pet_uuid = (data.get("uuid") or "").strip()
        nome = (data.get("nome") or "").strip()
        tipo = (data.get("tipo") or "").strip()

        if not usuario_uuid or not nome or not tipo:
            return JsonResponse({"erro": "usuario_uuid, nome e tipo são obrigatórios."}, status=400)

        if tipo not in ["Gato", "Cachorro"]:
            return JsonResponse({"erro": "Tipo inválido. Use Gato ou Cachorro."}, status=400)

        if not Usuario.objects.filter(uuid=usuario_uuid).exists():
            return JsonResponse({"erro": "Usuário responsável não encontrado."}, status=404)

        sexo = data.get("sexo") or None
        raca = data.get("raca") or None
        idade = data.get("idade")
        peso = data.get("peso")
        altura = data.get("altura")

        # normaliza idade
        if idade is not None and idade != "":
            try:
                idade = int(idade)
            except Exception:
                idade = None
        else:
            idade = None

        # ✅ Se veio uuid, tenta atualizar
        if pet_uuid:
            existente = Pet.objects.filter(uuid=pet_uuid).first()
            if existente:
                existente.usuario_uuid = usuario_uuid
                existente.nome = nome
                existente.tipo = tipo
                existente.sexo = sexo
                existente.raca = raca
                existente.idade = idade
                existente.peso = peso
                existente.altura = altura
                existente.save()

                return JsonResponse({"uuid": str(existente.uuid)}, status=200)

        # ✅ Caso contrário, cria
        novo = Pet.objects.create(
            usuario_uuid=usuario_uuid,
            nome=nome,
            tipo=tipo,
            sexo=sexo,
            raca=raca,
            idade=idade,
            peso=peso,
            altura=altura,
        )
        return JsonResponse({"uuid": str(novo.uuid)}, status=201)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)


# ============================================================
# TUTOR – LISTA PETS (GET)  ✅ PARA O FLUTTER BAIXAR
# ============================================================

@csrf_exempt
def tutor_pets(request):
    """
    GET /api/v1/tutor/pets/?usuario_uuid=...
    """
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    usuario_uuid = (request.GET.get("usuario_uuid") or "").strip()
    if not usuario_uuid:
        return JsonResponse({"erro": "usuario_uuid obrigatório"}, status=400)

    pets = Pet.objects.filter(usuario_uuid=usuario_uuid)

    return JsonResponse({
        "pets": [
            {
                "uuid": str(p.uuid),
                "usuario_uuid": str(p.usuario_uuid),
                "nome": p.nome,
                "tipo": p.tipo,
                "sexo": p.sexo or "",
                "raca": p.raca or "",
                "idade": p.idade or 0,
                "peso": float(p.peso or 0),
                "altura": float(p.altura or 0),
            }
            for p in pets
        ]
    }, status=200)
