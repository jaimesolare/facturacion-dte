import os
import sys

# 1. Agregar el directorio actual al path de Python
# Esto es necesario para que Python encuentre el módulo 'src'
sys.path.insert(0, os.path.dirname(__file__))

# 2. Importar la aplicación FastAPI y el adaptador
from src.main import app as application_asgi
from a2wsgi import ASGIMiddleware

# 3. Crear la aplicación WSGI compatible con Passenger
# 'application' es el nombre estándar que busca Passenger
application = ASGIMiddleware(application_asgi)
