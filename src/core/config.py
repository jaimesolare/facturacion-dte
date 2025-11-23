from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Carga las configuraciones de la aplicación desde variables de entorno o un archivo .env.
    """
    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost/facturacion"

    # Credenciales para la API del Ministerio de Hacienda
    MH_NIT: str = "TU_NIT"
    MH_API_KEY: str = "TU_API_KEY_PASSWORD"
    MH_PRIVATE_KEY_PASSWORD: str = "TU_CLAVE_P12"
    
    # Rutas a los archivos de firma (usar rutas absolutas o relativas al proyecto)
    MH_PRIVATE_KEY_PATH: str = "certs/private_key.p12"
    MH_PUBLIC_KEY_PATH: str = "certs/public_key.pem"

    # URLs de la API del Ministerio de Hacienda
    MH_AUTH_URL: str = "https://api.mh.gob.sv/seguridad/auth"
    MH_DTE_RECEPTION_URL: str = "https://api.mh.gob.sv/fesv/recepciondte"

    # Configuración para Pydantic-Settings
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    # Seguridad
    ENCRYPTION_KEY: str

# Se crea una instancia única que será importada por el resto de la aplicación
settings = Settings()
