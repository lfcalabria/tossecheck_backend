import json
import re
import uuid
import os
from datetime import datetime

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password

import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import *

# ============================================================
# UTILITÁRIOS
# ============================================================

def normalizar_cpf(valor):
    if valor is None:
        return ''
    return ''.join(ch for ch in str(valor) if ch.isdigit())

def normalizar_telefone(valor):
    if valor is None:
        return ""
    return re.sub(r"\D", "", str(valor))

def normalizar_nome(valor):
    if valor is None:
        return ""
    s = str(valor).strip().lower()
    # normalização simples (sem unicodedata aqui para manter compat)
    s = re.sub(r"\s+", " ", s)
    return s

def calc_ano_nascimento(idade):
    try:
        return datetime.now().year - int(idade)
    except Exception:
        return None


# ============================================================
# APIS DO APLICATIVO FLUTTER (TUTORES) - LEGADO (se existir)
# ============================================================

@csrf_exempt
def sync_usuario(request):
    """
    Cria usuário OU valida usuário existente.
    CPF duplicado + dados diferentes => 409
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")

        nome = data.get("nome")
        cpf = normalizar_cpf(data.get("cpf"))
        telefone = data.get("telefone")

        if not nome or not cpf or not telefone:
            return JsonResponse({"erro": "Campos obrigatórios: nome, cpf, telefone"}, status=400)

        existente = Usuario.objects.filter(cpf=cpf).first()

        if existente:
            nome_ok = normalizar_nome(existente.nome) == normalizar_nome(nome)
            tel_ok = normalizar_telefone(existente.telefone) == normalizar_telefone(telefone)

            if nome_ok and tel_ok:
                existente.bloqueado = False
                existente.liberado = True
                existente.save(update_fields=["bloqueado", "liberado"])
                return JsonResponse({"uuid": str(existente.uuid)}, status=200)

            existente.bloqueado = True
            existente.liberado = False
            existente.save(update_fields=["bloqueado", "liberado"])

            return JsonResponse(
                {
                    "uuid": str(existente.uuid),
                    "bloqueado": True,
                    "liberado": False,
                    "erro": "CPF já existe com dados divergentes.",
                },
                status=409,
            )

        novo = Usuario.objects.create(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            bloqueado=False,
            liberado=True,
        )

        return JsonResponse({"uuid": str(novo.uuid)}, status=201)

    except IntegrityError:
        return JsonResponse({"erro": "Conflito de CPF"}, status=409)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)


@csrf_exempt
def sync_pet(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body or "{}")

        idade = data.get('idade')
        ano_nascimento = None
        if idade is not None and str(idade) != "":
            try:
                ano_nascimento = datetime.now().year - int(idade)
            except Exception:
                ano_nascimento = None

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


# ============================================================
# ✅ UPLOAD DE VÍDEO (CORRIGIDO: RENOMEIA PARA UUID)
# ============================================================

@csrf_exempt
def upload_video(request):
    """
    POST /api/v1/upload/video/
    multipart/form-data:
      - pet_uuid
      - file

    ✅ Agora o backend renomeia o arquivo para UUID para evitar colisão.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    try:
        pet_uuid = request.POST.get('pet_uuid')
        arquivo_fisico = request.FILES.get('file')

        if not pet_uuid:
            return JsonResponse({'erro': 'pet_uuid é obrigatório'}, status=400)
        if not arquivo_fisico:
            return JsonResponse({'erro': 'Arquivo "file" é obrigatório'}, status=400)

        # ✅ Renomeia o arquivo para UUID + extensão
        original_name = arquivo_fisico.name or ""
        _, ext = os.path.splitext(original_name)
        if not ext:
            ext = ".mp4"  # fallback seguro

        novo_nome = f"{uuid.uuid4()}{ext.lower()}"
        arquivo_fisico.name = novo_nome  # IMPORTANTÍSSIMO: sem pasta aqui (upload_to já resolve)

        novo_video = VideoPet.objects.create(
            pet_uuid=pet_uuid,
            arquivo=arquivo_fisico
        )

        # Retorna uuid do registro (como já fazia) — compatível com o app/portal
        return JsonResponse({'uuid': str(novo_video.uuid)}, status=201)

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=400)


# ============================================================
# APIS DO PORTAL WEB (VETERINÁRIOS)
# ============================================================

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body or "{}")
        crmv = data.get('crmv')
        senha = data.get('senha')

        if not crmv or not senha:
            return JsonResponse({'erro': 'CRMV e senha são obrigatórios.'}, status=400)

        try:
            vet = Veterinario.objects.get(crmv=crmv, ativo=True)
        except Veterinario.DoesNotExist:
            return JsonResponse({'erro': 'CRMV não encontrado ou inativo.'}, status=404)

        if not check_password(senha, vet.senha):
            return JsonResponse({'erro': 'Senha incorreta.'}, status=401)

        return JsonResponse({
            'token': str(vet.uuid),
            'veterinario': {
                'nome': vet.nome,
                'crmv': vet.crmv,
                'uuid': str(vet.uuid)
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato de dados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno da API: {str(e)}'}, status=400)


@csrf_exempt
def api_responsavel(request):
    """
    Compatibilidade com seu urls.py:
    GET /api/v1/responsavel/?q=CPF
    POST /api/v1/responsavel/
    """
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
        }, status=200)

    if request.method == 'POST':
        try:
            data = json.loads(request.body or "{}")
            nome = data.get('nome')
            cpf = normalizar_cpf(data.get('cpf'))
            telefone = data.get('telefone')

            if not nome or not cpf or not telefone:
                return JsonResponse({'erro': 'Nome, CPF e telefone são obrigatórios.'}, status=400)

            novo_usuario = Usuario.objects.create(
                nome=nome,
                cpf=cpf,
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
        lista_pets.append({
            'uuid': str(pet.uuid),
            'usuario_uuid': str(pet.usuario_uuid),
            'nome': pet.nome,
            'tipo': pet.tipo,
            'sexo': pet.sexo,
            'raca': pet.raca,
            'idade': pet.idade,
            'ano_nascimento': calc_ano_nascimento(pet.idade),
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
        data = json.loads(request.body or "{}")

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

        if idade is not None and idade != "":
            try:
                idade = int(idade)
            except Exception:
                idade = None

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
            'ano_nascimento': calc_ano_nascimento(novo_pet.idade),
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=400)


@csrf_exempt
def api_pet_detail(request, pet_uuid):
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    try:
        pet = Pet.objects.get(uuid=pet_uuid)
    except Pet.DoesNotExist:
        return JsonResponse({"erro": "Pet não encontrado."}, status=404)

    videos = VideoPet.objects.filter(pet_uuid=str(pet.uuid)).order_by("-id")
    observacoes = Observacao.objects.filter(pet_uuid=str(pet.uuid)).order_by("-data_cadastro")

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
                "data_upload": getattr(v, "data_upload", datetime.now()).strftime("%d/%m/%Y %H:%M")
            } for v in videos
        ],
        "prontuario": [
            {
                "uuid": str(o.uuid),
                "texto": o.mensagem,
                "data": o.data_cadastro.strftime("%d/%m/%Y %H:%M"),
                "veterinario": o.veterinario.nome,
                "automatica": o.automatica
            } for o in observacoes
        ]
    }, status=200)


@csrf_exempt
def api_pet_observacao(request, pet_uuid):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    try:
        data = json.loads(request.body or "{}")
        texto = (data.get("texto") or "").strip()

        if not texto:
            return JsonResponse({"erro": "Observação vazia."}, status=400)

        try:
            pet = Pet.objects.get(uuid=pet_uuid)
        except Pet.DoesNotExist:
            return JsonResponse({"erro": "Pet não encontrado."}, status=404)

        vet = Veterinario.objects.first()
        if not vet:
            return JsonResponse({"erro": "Nenhum veterinário cadastrado."}, status=400)

        obs = Observacao.objects.create(
            pet_uuid=str(pet.uuid),
            veterinario=vet,
            mensagem=texto
        )

        return JsonResponse({
            "uuid": str(obs.uuid),
            "texto": obs.mensagem,
            "data": obs.data_cadastro.strftime("%d/%m/%Y %H:%M"),
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)
@csrf_exempt
def api_video_detalhe(request, video_uuid):
    """GET /api/v1/video/<uuid>/ — retorna detalhes do vídeo (url, data_upload, pet_uuid)"""
    if request.method != 'GET':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        video = VideoPet.objects.get(uuid=video_uuid)
        return JsonResponse({
            'uuid': str(video.uuid),
            'pet_uuid': video.pet_uuid,
            'url': video.arquivo.url,
            'data_upload': video.data_upload.strftime("%d/%m/%Y %H:%M") if video.data_upload else "",
        }, status=200)
    except VideoPet.DoesNotExist:
        return JsonResponse({'erro': 'Vídeo não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=400)

@csrf_exempt
def api_video_classificacoes(request, video_uuid):
    """GET /api/v1/video/<uuid>/classificacoes/ — retorna classificações de um vídeo"""
    if request.method != 'GET':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        classificacoes = VideoClassificacao.objects.filter(video_uuid=video_uuid).order_by('-data_cadastro')
        dados = []
        for c in classificacoes:
            dados.append({
                'uuid': str(c.uuid),
                'video_uuid': c.video_uuid,
                'duracao': c.duracao,
                'tipo_som': c.tipo_som,
                'fator': c.fator,
                'estridor': c.estridor,
                'estertor': c.estertor,
                'obs': c.obs,
                'veterinario_uuid': c.veterinario_uuid,
                'data_cadastro': c.data_cadastro.strftime("%d/%m/%Y %H:%M"),
            })
        return JsonResponse({'classificacoes': dados}, status=200)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=400)

@csrf_exempt
def api_criar_classificacao(request):
    """POST /api/v1/video/classificacao/ — cria classificação + observação automática"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        data = json.loads(request.body or "{}")
        video_uuid = data.get('video_uuid')
        if not video_uuid:
            return JsonResponse({'erro': 'video_uuid é obrigatório'}, status=400)

        # Cria a classificação
        classificacao = VideoClassificacao.objects.create(
            video_uuid=video_uuid,
            duracao=data.get('duracao', ''),
            tipo_som=data.get('tipo_som', ''),
            fator=data.get('fator', ''),
            estridor=data.get('estridor', False),
            estertor=data.get('estertor', False),
            obs=data.get('obs', ''),
            automatica=True,
            veterinario_uuid=data.get('veterinario_uuid', ''),
        )

        # Busca o vídeo para descobrir o pet_uuid e data de gravação
        pet_uuid = None
        data_gravacao = "data desconhecida"
        try:
            video = VideoPet.objects.get(uuid=video_uuid)
            pet_uuid = video.pet_uuid
            data_gravacao = video.data_upload.strftime("%d/%m/%Y %H:%M") if video.data_upload else "data desconhecida"
        except VideoPet.DoesNotExist:
            pass

        # Mapeia valores para exibição na observação
        duracao_map = {
            'aguda': 'Aguda (<3s)',
            'subaguda': 'Subaguda (3-8s)',
            'cronica': 'Crônica (>8s)',
        }
        tipo_map = {
            'aspera_alta': 'Áspera/Alta',
            'ganso': 'Ganso',
            'sibilante': 'Sibilante',
            'suave_inspiracao': 'Suave com Inspiração',
            'engasgo_degluticao': 'Engasgo/Deglutição Final',
        }

        estridor_texto = "Sim" if classificacao.estridor else "Não"
        estertor_texto = "Sim" if classificacao.estertor else "Não"
        obs_texto = classificacao.obs or "Sem observações"

        duracao_exib = duracao_map.get(classificacao.duracao, classificacao.duracao)
        tipo_exib = tipo_map.get(classificacao.tipo_som, classificacao.tipo_som)

        mensagem = (
            f"O vídeo gravado em {data_gravacao} foi classificado como uma tosse de duração "
            f"{duracao_exib}, o tipo de som é {tipo_exib} gerado por "
            f"{classificacao.fator}; Estridor: {estridor_texto}, Ester tor: {estertor_texto}, "
            f"{obs_texto}"
        )

        # Cria a observação automática
        if pet_uuid and data.get('veterinario_uuid'):
            try:
                vet = Veterinario.objects.get(uuid=data['veterinario_uuid'])
                Observacao.objects.create(
                    pet_uuid=pet_uuid,
                    veterinario=vet,
                    mensagem=mensagem,
                )
            except (Veterinario.DoesNotExist, ValueError):
                pass

        return JsonResponse({'uuid': str(classificacao.uuid)}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato de dados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=400)

@csrf_exempt
def api_esqueci_senha(request):
    """POST /api/v1/esqueci-senha/ — recebe CRMV, gera token e retorna o link"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body or "{}")
        crmv = (data.get('crmv') or '').strip()

        if not crmv:
            return JsonResponse({'erro': 'CRMV é obrigatório.'}, status=400)

        try:
            vet = Veterinario.objects.get(crmv=crmv, ativo=True)
        except Veterinario.DoesNotExist:
            # Não revela se o CRMV existe ou não (segurança)
            return JsonResponse({'mensagem': 'Se o CRMV estiver cadastrado, você receberá um link de redefinição no email cadastrado.'}, status=200)

        # Gera token seguro
        token = secrets.token_urlsafe(32)
        expiracao = timezone.now() + timedelta(hours=1)

        # Invalida tokens anteriores do mesmo veterinário
        RedefinicaoSenhaToken.objects.filter(
            veterinario=vet, usado=False
        ).update(usado=True)

        # Cria novo token
        RedefinicaoSenhaToken.objects.create(
            veterinario=vet,
            token=token,
            expira_em=expiracao
        )

        # Monta link de redefinição
        link = f"https://portal.tecnologiasinternet.com.br/portal/redefinir-senha/?token={token}"

        # TODO: Enviar email com o link
        # Por enquanto, retorna o link direto (apenas para desenvolvimento)
        print(f"[ESQUECI SENHA] CRMV: {crmv} - Link: {link}")

        return JsonResponse({
            'mensagem': 'Se o CRMV estiver cadastrado, você receberá um link de redefinição no email cadastrado.',
            'link': link  # REMOVA em produção
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato de dados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=400)

@csrf_exempt
def api_redefinir_senha(request):
    """POST /api/v1/redefinir-senha/ — recebe token + nova senha, atualiza"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body or "{}")
        token = (data.get('token') or '').strip()
        nova_senha = data.get('nova_senha')

        if not token or not nova_senha:
            return JsonResponse({'erro': 'Token e nova senha são obrigatórios.'}, status=400)

        if len(nova_senha) < 6:
            return JsonResponse({'erro': 'A senha deve ter no mínimo 6 caracteres.'}, status=400)

        try:
            registro = RedefinicaoSenhaToken.objects.get(token=token, usado=False)
        except RedefinicaoSenhaToken.DoesNotExist:
            return JsonResponse({'erro': 'Token inválido ou já utilizado.'}, status=400)

        if timezone.now() > registro.expira_em:
            registro.usado = True
            registro.save(update_fields=['usado'])
            return JsonResponse({'erro': 'Token expirado. Solicite uma nova redefinição.'}, status=400)

        # Atualiza a senha com hash
        vet = registro.veterinario
        vet.set_senha(nova_senha)

        # Marca token como usado
        registro.usado = True
        registro.save(update_fields=['usado'])

        return JsonResponse({'mensagem': 'Senha redefinida com sucesso.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'Formato de dados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=400)
