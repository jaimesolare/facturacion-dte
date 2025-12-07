import zipfile
import os

def zip_project(output_filename):
    # Lista de carpetas a excluir
    EXCLUDE_DIRS = {
        '.git', 'venv', '.venv', '.gemini', '__pycache__', 
        '.pytest_cache', '.genkit', '.specify', '.benchmarks', 'node_modules'
    }
    # Lista de extensiones o archivos a excluir
    EXCLUDE_FILES = {
        output_filename, 'test.db', 'app.db', '.DS_Store'
    }
    
    print(f"Creando archivo: {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Modificar dirs in-place para que os.walk no entre en carpetas excluidas
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or file.endswith('.pyc') or file.endswith('.log'):
                    continue
                
                file_path = os.path.join(root, file)
                # Guardar en el zip con la ruta relativa
                zipf.write(file_path, arcname=file_path)
                # print(f"Agregado: {file_path}")

if __name__ == "__main__":
    zip_project('facturacion_deploy.zip')
    print("ZIP creado exitosamente: facturacion_deploy.zip")
