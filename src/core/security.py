from cryptography.fernet import Fernet
from src.core.config import settings

# La clave de encriptación DEBE venir de la configuración.
# Si no está configurada, Pydantic lanzará un error al inicio.
ENCRYPTION_KEY = settings.ENCRYPTION_KEY

fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    """Encrypts a string."""
    if not data:
        return data
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string."""
    if not encrypted_data:
        return encrypted_data
    return fernet.decrypt(encrypted_data.encode()).decode()
