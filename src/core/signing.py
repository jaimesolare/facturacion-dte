import json
import hashlib
import base64
from typing import Tuple, Optional
from jose import jws
from jose.constants import ALGORITHMS
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import Certificate

from src.core.config import settings

# Variables globales para caché
_PRIVATE_KEY: Optional[rsa.RSAPrivateKey] = None
_CERTIFICATE: Optional[Certificate] = None

def load_signing_credentials() -> Tuple[rsa.RSAPrivateKey, Certificate]:
    """
    Carga y cachea la llave privada y el certificado desde el archivo P12.
    """
    global _PRIVATE_KEY, _CERTIFICATE
    
    if _PRIVATE_KEY is not None and _CERTIFICATE is not None:
        return _PRIVATE_KEY, _CERTIFICATE

    try:
        # Cargar el contenido del archivo P12
        with open(settings.MH_PRIVATE_KEY_PATH, "rb") as f:
            p12_data = f.read()
        
        password = settings.MH_PRIVATE_KEY_PASSWORD.encode('utf-8')

        # Extraer llave privada y certificado del archivo P12
        _PRIVATE_KEY, _CERTIFICATE, _ = pkcs12.load_key_and_certificates(
            p12_data, password
        )
        return _PRIVATE_KEY, _CERTIFICATE
    except FileNotFoundError:
        raise Exception(f"No se encontró el archivo de llave privada en: {settings.MH_PRIVATE_KEY_PATH}")
    except Exception as e:
        raise Exception(f"Error al cargar el certificado P12: {e}")

def firmar_documento(payload_dict: dict) -> str:
    """
    Firma un diccionario de payload DTE y devuelve el JWS compacto.
    Usa credenciales cacheadas para mejor rendimiento.
    """
    private_key, certificate = load_signing_credentials()

    # Convertir el payload a una cadena JSON sin espacios y ordenada
    payload_str = json.dumps(payload_dict, separators=(',', ':'), sort_keys=True)

    # Calcular el hash SHA-256 del string JSON
    payload_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    # Obtener el certificado en formato Base64 para el header 'x5c'
    # Esto también podría cachearse si se optimiza más, pero es rápido en memoria.
    cert_b64 = base64.b64encode(
        certificate.public_bytes(serialization.Encoding.DER)
    ).decode('utf-8')

    # Definir los headers para el JWS
    jws_headers = {
        "alg": ALGORITHMS.RS256,
        "x5c": [cert_b64]
    }

    # Firmar el HASH del payload
    signed_jws = jws.sign(
        payload_hash,
        private_key,
        headers=jws_headers,
        algorithm=ALGORITHMS.RS256
    )

    return signed_jws