import httpx
from datetime import datetime, timedelta
from src.core.config import settings

class AuthManager:
    def __init__(self):
        self._token_cache = {"jwt": None, "expiration": None}

    async def get_mh_token(self) -> str:
        """
        Retrieves a JWT from the Ministry of Finance API using credentials from settings.
        Uses a simple in-memory cache.
        """
        now = datetime.utcnow()
        if self._token_cache["jwt"] and self._token_cache["expiration"] > now:
            return self._token_cache["jwt"]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.MH_AUTH_URL, 
                    json={"user": settings.MH_NIT, "pwd": settings.MH_API_KEY}
                )
                response.raise_for_status()
                data = response.json()
                
                # TODO: Add robust validation for the response structure
                token = data.get("body", {}).get("token")
                if not token:
                    raise ValueError("Token no encontrado en la respuesta de la API de autenticación.")

                self._token_cache["jwt"] = token
                # La documentación indica que el token dura 24 horas
                self._token_cache["expiration"] = now + timedelta(hours=24)
                return token
        except httpx.HTTPStatusError as e:
            # Log the error properly in a real app
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except (ValueError, KeyError) as e:
            print(f"Error procesando la respuesta de autenticación: {e}")
            raise
