import os
import sys
import subprocess

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
