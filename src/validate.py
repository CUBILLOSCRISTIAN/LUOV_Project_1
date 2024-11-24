#validate.py
import numpy as np
from keygen import generate_private_seed, generate_keys, sign_message
from utils_for_verify import verify_signature, EvaluatePublicMap

def validate_key_generation_and_signature():
    # Paso 1: Generar semilla privada
    private_seed = generate_private_seed()
    print("Semilla privada generada.")

    # Paso 2: Generar claves pública y privada
    public_key, private_key = generate_keys(private_seed)
    print("Claves generadas (pública y privada).")
    
    # Mostrar detalles de la clave pública
    public_seed, Q2 = public_key
    print(f"Semilla pública: {public_seed.hex()}")
    print(f"Tamaño de Q2: {Q2.shape}")

    # Paso 3: Evaluar si la clave pública se comporta como se espera
    test_vector = np.random.randint(0, 2, size=(len(public_seed),), dtype=np.uint8)
    public_map_output = EvaluatePublicMap(public_seed, Q2, test_vector)
    print(f"Evaluación del mapa público: {public_map_output}")

    # Paso 4: Crear un mensaje para firmar
    message = b"Mensaje de prueba para firma y verificación"
    print(f"Mensaje: {message.decode()}")

    # Paso 5: Firmar el mensaje con la clave privada
    signature, salt = sign_message(private_key, message)
    print("Firma generada.")
    print(f"Firma (bytes): {signature}")
    print(f"Salt utilizado: {salt.hex()}")

    # Paso 6: Verificar la firma con la clave pública
    is_valid = verify_signature(public_key, message, signature)
    if is_valid:
        print("La firma es válida: la generación de la llave y el esquema son correctos.")
    else:
        print("La firma es inválida: hay un problema en la generación de la llave o el esquema.")

if __name__ == "__main__":
    validate_key_generation_and_signature()
