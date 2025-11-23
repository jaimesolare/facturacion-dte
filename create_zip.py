import zipfile
import os

def zip_project(output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Archivos raíz
        files_to_include = [
            'Dockerfile',
            'docker-compose.yml',
            'requirements.txt',
            'gunicorn_conf.py',
            'deploy.sh',
            '.env', # Opcional, pero útil si ya tiene config
            'README.md'
        ]
        
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file, arcname=file)
        
        # Directorio src
        for root, dirs, files in os.walk('src'):
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file_path)
                
        # Directorio certs (si existe)
        if os.path.exists('certs'):
             for root, dirs, files in os.walk('certs'):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=file_path)

if __name__ == "__main__":
    zip_project('facturacion_deploy.zip')
    print("ZIP creado exitosamente: facturacion_deploy.zip")
