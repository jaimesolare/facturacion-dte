# Guía de Despliegue a Producción

Esta guía detalla los pasos para desplegar la aplicación de Facturación DTE en un entorno de producción.

## Opción 1: Render.com (Recomendado para inicio rápido)

Render es una plataforma PaaS que facilita el despliegue de aplicaciones web y bases de datos.

### Prerrequisitos

- Cuenta en [Render.com](https://render.com).
- Código fuente subido a un repositorio de GitHub/GitLab.

### Pasos

1. **Crear Base de Datos PostgreSQL**:
   - En el dashboard de Render, crea un nuevo "PostgreSQL".
   - Nombre: `dte-db` (o el que prefieras).
   - Copia la `Internal Connection URL` (para uso interno) o `External Connection URL` (si necesitas acceder desde fuera).

2. **Crear Web Service**:
   - Crea un nuevo "Web Service" conectado a tu repositorio.
   - **Runtime**: Python 3.
   - **Build Command**: `pip install -r requirements.txt`.
   - **Start Command**: `gunicorn --config gunicorn_conf.py src.main:app`.
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.11.0`
     - `DATABASE_URL`: Pega la URL de conexión de tu base de datos creada en el paso 1.
     - `MH_NIT`: Tu NIT.
     - `MH_API_KEY`: Tu contraseña de API del MH.
     - `MH_PRIVATE_KEY_PASSWORD`: Contraseña de tu llave privada.
     - `ENCRYPTION_KEY`: Genera una clave segura (puedes usar `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).

3. **Archivos de Certificados**:
   - Render no permite subir archivos directamente de forma sencilla en el plan gratuito.
   - **Opción A (Recomendada)**: Codificar los archivos `.p12` y `.pem` en base64 y guardarlos como variables de entorno (`MH_PRIVATE_KEY_BASE64`, `MH_PUBLIC_KEY_BASE64`), luego decodificarlos en el código al iniciar.
   - **Opción B**: Usar un "Disk" (requiere plan de pago) para almacenar los certificados.

## Opción 2: Docker / VPS (Ubuntu/Debian)

Para un control total, puedes usar un servidor virtual (VPS) con Docker.

### Prerrequisitos

- Servidor con Docker y Docker Compose instalados.
- Dominio apuntando a la IP del servidor.

### Pasos

1. **Clonar el Repositorio**:

   ```bash
   git clone <tu-repo-url>
   cd facturacion
   ```

2. **Configurar Entorno**:
   - Copia el archivo de ejemplo: `cp .env.example .env`
   - Edita `.env` con tus credenciales de producción.

3. **Certificados**:
   - Asegúrate de que tus archivos de certificado (`private_key.p12`, `public_key.pem`) estén en la carpeta `certs/` (o la ruta que hayas definido en `.env`).

4. **Desplegar**:

   ```bash
   docker compose up -d --build
   ```

5. **Migraciones de Base de Datos**:
   - Ejecuta las migraciones para crear las tablas:

   ```bash
   docker compose exec web alembic upgrade head
   ```

6. **Verificación**:
   - La API estará disponible en el puerto 8000.
   - Se recomienda configurar Nginx como proxy inverso para manejar SSL (HTTPS) y redirigir el tráfico del puerto 80 al 8000.

## Notas Importantes

- **CORS**: Se ha configurado `src/main.py` para permitir todos los orígenes (`*`). Para mayor seguridad, edita la lista `allow_origins` con tu dominio real (ej: `["https://mi-facturacion.com"]`).
- **Seguridad**: Nunca subas tus archivos de certificados o claves privadas al repositorio de código.

7. **Reiniciar**:
   - Haz clic en **"Restart"** en la aplicación de Python.
   - Visita tu URL. Deberías ver la aplicación funcionando.

## Opción 3: Despliegue en cPanel (Hosting Compartido)

Esta opción es ideal si ya cuentas con un hosting que incluye cPanel y soporte para Python (CloudLinux/Litespeed).

### Prerrequisitos

- Hosting con cPanel y acceso a **"Setup Python App"**.
- Acceso a bases de datos **MySQL** (la mayoría de cPanels usan MySQL/MariaDB en lugar de PostgreSQL).

### Pasos

1. **Crear Base de Datos MySQL**:
   - Ve a "Bases de datos MySQL" en cPanel.
   - Crea una nueva base de datos (ej: `usuario_dtedb`).
   - Crea un usuario y asígnale **todos los privilegios** sobre esa base de datos.
   - **Nota**: El sistema soporta MySQL gracias al driver `pymysql` incluido.

2. **Configurar Python App**:
   - Ve a **"Setup Python App"**.
   - Haz clic en **"Create Application"**.
   - **Python Version**: Selecciona 3.11 o superior.
   - **Application root**: `facturacion` (o el nombre de la carpeta donde subirás los archivos).
   - **Application URL**: Selecciona tu dominio/subdominio (ej: `tudominio.com`).
   - **Application startup file**: `passenger_wsgi.py` (IMPORTANTE: dejar esto exacto).
   - **Application entry point**: `application` (IMPORTANTE: dejar esto exacto).
   - Haz clic en **Create**.

3. **Subir Archivos**:
   - Ve al **Administrador de Archivos** de cPanel.
   - Entra a la carpeta de tu aplicación (ej: `facturacion`).
   - Sube el archivo `facturacion_deploy.zip` generado.
   - Extrae el archivo ZIP dentro de esa carpeta.

4. **Instalar Dependencias**:
   - Regresa a "Setup Python App".
   - En la sección "Configuration files", escribe `requirements.txt` y dale "Add".
   - Haz clic en el botón **"Run Pip Install"**. Espera a que termine.

5. **Variables de Entorno**:
   - En la misma pantalla de configuración de la App, ve a "Environment variables".
   - Agrega las siguientes:
     - `DATABASE_URL`: `mysql+pymysql://USUARIO_DB:CONTRASEÑA@localhost/NOMBRE_DB`
     - `MH_NIT`: Tu NIT.
     - `MH_API_KEY`: Tu API Key.
     - `MH_PRIVATE_KEY_PASSWORD`: Password de tu .p12.
     - `ENCRYPTION_KEY`: Tu llave de encriptación.

6. **Certificados**:
   - Crea una carpeta `certs` dentro de tu aplicación en el Administrador de Archivos.
   - Sube tus archivos `.p12` y `.pem` ahí.
   - Asegúrate que las variables de entorno apunten a ellos o usa rutas absolutas si es necesario (`/home/usuario/facturacion/certs/...`).

7. **Reiniciar**:
   - Haz clic en el botón **"Restart"** en la configuración de la App.
