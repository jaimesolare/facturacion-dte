# Script de despliegue para Facturación DTE (Windows/PowerShell)
# Uso: .\deploy.ps1

Write-Host "--- Iniciando despliegue de Facturación DTE (Local) ---" -ForegroundColor Cyan

# 1. Verificar Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker no encontrado. Por favor instala Docker Desktop para Windows."
    exit 1
}

# 2. Configurar variables de entorno si no existen
if (-not (Test-Path ".env")) {
    Write-Host "Creando archivo .env de ejemplo..." -ForegroundColor Yellow
    $envContent = @"
DATABASE_URL=postgresql://postgres:postgres@db:5432/dte_db
ENCRYPTION_KEY=8TRMxPaCBjYkfRngic51U85BGBm-d_HzbctvzSNZuKE=
MH_NIT=00000000000000
MH_API_KEY=tu_api_key
MH_PRIVATE_KEY_PASSWORD=tu_password
MH_PRIVATE_KEY_PATH=certs/private_key.p12
MH_PUBLIC_KEY_PATH=certs/public_key.pem
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Host "Archivo .env creado."
}

# 3. Crear directorios
if (-not (Test-Path "certs")) {
    New-Item -ItemType Directory -Force -Path "certs" | Out-Null
}

# 4. Construir y levantar
Write-Host "Construyendo y levantando contenedores..." -ForegroundColor Cyan
docker compose up -d --build

Write-Host "--- Despliegue finalizado ---" -ForegroundColor Green
Write-Host "La API está corriendo en http://localhost:8000"
Write-Host "Ver logs: docker compose logs -f"
