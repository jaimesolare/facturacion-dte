# Usar una imagen base oficial de Python ligera
FROM python:3.11-slim

# Establecer variables de entorno
# PYTHONDONTWRITEBYTECODE: Evita que Python escriba archivos .pyc
# PYTHONUNBUFFERED: Asegura que los logs de Python se envíen directamente al terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (si las hay)
# Por ejemplo, para psycopg2-binary a veces se necesitan librerías de postgres, 
# pero la versión binary ya trae lo necesario.
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Crear un usuario no root para ejecutar la aplicación
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación usando Gunicorn
CMD ["gunicorn", "--config", "gunicorn_conf.py", "src.main:app"]
