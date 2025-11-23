import os
import sys
from cryptography.fernet import Fernet

# Configurar entorno
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
print(f"Generated Key: {os.environ['ENCRYPTION_KEY']}")

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["MH_NIT"] = "00000000000000"
os.environ["MH_API_KEY"] = "test"
os.environ["MH_PRIVATE_KEY_PASSWORD"] = "test"
os.environ["MH_PRIVATE_KEY_PATH"] = "dummy_path.p12"
os.environ["MH_PUBLIC_KEY_PATH"] = "dummy_path.pem"

# Añadir src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

print("Intentando importar dte_service...")
try:
    from src.services import dte_service
    print("Importación exitosa!")
except Exception as e:
    print(f"Error de importación: {e}")
    import traceback
    traceback.print_exc()
