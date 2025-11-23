#!/bin/bash

# Script de despliegue para Facturación DTE
# Uso: ./deploy.sh

set -e

echo "--- Iniciando despliegue de Facturación DTE ---"

# 1. Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no encontrado. Intentando instalar..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "Docker instalado correctamente."
else
    echo "Docker ya está instalado."
fi

# 2. Verificar Docker Compose
if ! docker compose version &> /dev/null; then
    echo "Docker Compose plugin no encontrado. Intentando instalar..."
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin || echo "No se pudo instalar automáticamente docker-compose-plugin. Verifica tu distribución."
fi

# 3. Configurar variables de entorno si no existen
if [ ! -f .env ]; then
    echo "ADVERTENCIA: No se encontró archivo .env."
    echo "Creando archivo .env de ejemplo..."
    cat <<EOF > .env
DATABASE_URL=postgresql://postgres:postgres@db:5432/dte_db
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "CAMBIAME_POR_CLAVE_FERNET_VALIDA")
MH_NIT=00000000000000
MH_API_KEY=tu_api_key
MH_PRIVATE_KEY_PASSWORD=tu_password
MH_PRIVATE_KEY_PATH=certs/private_key.p12
MH_PUBLIC_KEY_PATH=certs/public_key.pem
EOF
    echo "Archivo .env creado. POR FAVOR EDÍTALO con tus credenciales reales."
fi

# 4. Crear directorios necesarios
mkdir -p certs

# 5. Construir y levantar servicios
echo "Construyendo y levantando contenedores..."
docker compose up -d --build

echo "--- Despliegue finalizado ---"
echo "La API debería estar corriendo en el puerto 8000."
echo "Verifica los logs con: docker compose logs -f"
