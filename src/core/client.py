import httpx
from typing import Dict, Any

from src.core.config import settings

class MHClient:
    """
    Cliente para interactuar con los endpoints de la API del Ministerio de Hacienda.
    """
    async def transmitir_dte(self, jws_firmado: str, token: str) -> Dict[str, Any]:
        """
        Transmite un DTE firmado al endpoint de recepción del MH.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # El cuerpo de la petición es un JSON que envuelve al JWS
        # La estructura exacta puede variar, pero esta es una implementación común.
        request_body = {
            "nit": settings.MH_NIT,
            "documento": jws_firmado,
            # "tipoDte": "01", # A veces se requiere, depende de la API
            # "version": 3
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"Transmitiendo DTE a: {settings.MH_DTE_RECEPTION_URL}")
                response = await client.post(
                    settings.MH_DTE_RECEPTION_URL,
                    headers=headers,
                    json=request_body,
                    timeout=30.0 # Es bueno tener un timeout
                )
                
                # Lanza una excepción si la respuesta es 4xx o 5xx
                response.raise_for_status()
                
                # Devuelve la respuesta JSON del MH
                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"Error en la respuesta del MH: {e.response.status_code} - {e.response.text}")
                # Re-lanzar la excepción para que el servicio la maneje
                raise
            except httpx.RequestError as e:
                print(f"Error de conexión al transmitir DTE: {e}")
                # Re-lanzar la excepción para que el servicio la maneje
                raise