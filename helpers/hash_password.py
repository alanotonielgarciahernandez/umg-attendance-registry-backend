# hash_password.py
# Script para hashear contraseñas.

# Importar módulos de Python.
import base64
import hashlib
import secrets

# Constantes para el hashing.
ITERACIONES = 10000
KEY_LENGTH = 256 // 8 # 256 bits = 32 bytes
ALGORITMO = 'sha256'

def _decode_base64( value: str ) -> bytes:
    # Normalizar el padding para soportar valores base64 almacenados sin '=' al final.
    padding = '=' * ( -len( value ) % 4 )
    return base64.b64decode( value + padding )


def verify_password( password: str, stored_password: str ) -> bool:
    # Validar que la contraseña almacenada tenga el formato esperado.
    if ':' not in stored_password:
        return False

    # Separar salt y hash almacenados.
    salt_b64, hash_b64 = stored_password.split( ':', 1 )
    salt = _decode_base64( salt_b64 )
    expected_hash = _decode_base64( hash_b64 )

    # Recalcular el hash para comparar contra el valor almacenado.
    computed_hash = hashlib.pbkdf2_hmac(
        ALGORITMO, password.encode( 'utf-8' ), salt, ITERACIONES, KEY_LENGTH
    )

    return secrets.compare_digest( computed_hash, expected_hash )
