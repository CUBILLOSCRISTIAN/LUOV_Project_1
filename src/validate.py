# validate.py
import numpy as np
from keygen import generate_private_seed, generate_keys
from sign import Sign
from utils_for_verify import verify_signature

def validate_key_generation_and_signature():
    # Paso 1: Generar semilla privada
    private_seed = generate_private_seed()
    print("Semilla privada generada.")

    # Paso 2: Generar claves pública y privada
    public_key, private_key, public_key_size_kb = generate_keys(private_seed)
    print(f"Claves generadas (pública y privada). Tamaño clave pública: {public_key_size_kb:.2f} KB")

    # Mostrar detalles de la clave pública
    public_seed, Q2 = public_key
    print(f"Semilla pública: {public_seed.hex()}")
    print(f"Tamaño de Q2: {Q2.shape}")

    # Paso 3: Crear un mensaje para firmar
    message = b"Mensaje de prueba para firma y verificación"
    print(f"Mensaje a firmar: {message.decode()}")

    # Paso 4: Firmar el mensaje con la clave privada
    signature, salt = Sign(private_key, message)
    print("Firma generada.")
    print(f"Salt utilizado: {salt.hex()}")

    # Paso 5: Verificar la firma con la clave pública
    is_valid = verify_signature(public_key, message, signature + salt)
    if is_valid:
        print("La firma es válida: la generación de la llave y el esquema son correctos.")
    else:
        print("La firma es inválida: hay un problema en la generación de la llave o el esquema.")

if __name__ == "__main__":
    validate_key_generation_and_signature()
