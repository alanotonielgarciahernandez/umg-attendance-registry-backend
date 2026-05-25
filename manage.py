# manage.py
# Herramienta de línea de comandos para tareas administrativas de Django.

# Importar módulos de Python.
import os
import sys

# Importar función para cargar variables de entorno.
from helpers.env_helpers import load_env_file

def main():
    """Run administrative tasks."""
    os.environ.setdefault( 'DJANGO_SETTINGS_MODULE', 'settings' )

    # Cargar variables de entorno desde el archivo .env antes de ejecutar cualquier comando.
    load_env_file()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Verificar que las variables de entorno necesarias estén configuradas.
    required_env_vars = [
        'DJANGO_SECRET_KEY',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'EMAIL_EMISOR',
    ]
    for var in required_env_vars:
        if not os.getenv( var ):
            print( f"Error: La variable de entorno '{ var }' no está configurada." )
            return

    execute_from_command_line( sys.argv )

if __name__ == '__main__':
    main()
