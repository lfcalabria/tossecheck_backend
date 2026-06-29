import os
import sys
import django

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tossecheck_backend.settings')
django.setup()

from api.models import Veterinario
from django.contrib.auth.hashers import make_password

vets = Veterinario.objects.all()
for vet in vets:
    if not vet.senha.startswith('pbkdf2_'):
        vet.senha = make_password(vet.senha)
        vet.save(update_fields=['senha'])
        print(f"✓ {vet.nome} ({vet.crmv})")

print("Migração concluída!")