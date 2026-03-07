import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, '/home/tecnologia/repositories/tossecheck_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tossecheck_backend.settings')

import pymysql
pymysql.install_as_MySQLdb()
pymysql.version_info = (2, 2, 1, 'final', 0)

application = get_wsgi_application()