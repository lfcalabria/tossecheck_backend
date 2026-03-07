import os
import sys
from django.core.wsgi import get_wsgi_application

# Adiciona o projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tossecheck_web.settings')  # Ajuste o nome

application = get_wsgi_application()