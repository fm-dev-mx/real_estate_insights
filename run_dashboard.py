import os
import sys
import subprocess
import logging
from logging.handlers import RotatingFileHandler

# --- LOGGING CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'src', 'data_collection', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# Configurar el logger principal
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # Nivel mínimo de captura

# Formateador
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Manejador de archivo rotativo
file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1024*1024*5, backupCount=2, encoding='utf-8')
file_handler.setLevel(logging.INFO) # Nivel para el archivo
file_handler.setFormatter(formatter)

# Manejador de consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG) # Nivel para la consola
console_handler.setFormatter(formatter)

# Añadir manejadores al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def run_streamlit():
    """
    Ejecuta la aplicación Streamlit desde el directorio raíz del proyecto,
    asegurando que los imports desde el directorio `src` funcionen correctamente.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(project_root, "src")
    app_path = os.path.join(src_path, "visualization", "dashboard_app.py")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path
    ]

    # Crear una copia del entorno actual y añadir src_path a PYTHONPATH
    # Esto asegura que los módulos dentro de 'src' sean encontrados por Python.
    env = os.environ.copy()
    env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')

    print(f"Project Root: {project_root}")
    print(f"Python Path: {env['PYTHONPATH']}")
    print(f"Running command: {' '.join(command)}")

    try:
        # Ejecutar el comando con el entorno modificado y el directorio de trabajo correcto
        subprocess.run(command, check=True, cwd=project_root, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
    except FileNotFoundError:
        print("Error: 'streamlit' command not found.")
        print("Please make sure Streamlit is installed in your environment.")
        print("You can install it with: pip install streamlit")

if __name__ == "__main__":
    run_streamlit()
