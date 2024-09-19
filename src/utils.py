# utils.py

import hashlib
import numpy as np

from constants import SECURITY_LEVEL

def extract_Pk1(Q1, k, v):
    """Extrae la submatriz Pk1 de Q1 (términos cuadráticos en variables de vinagre)."""
    Pk1 = np.zeros((v, v), dtype=int)
    column = 0
    for i in range(v):
        for j in range(i, v):
            Pk1[i, j] = Q1[k, column]
            column += 1
    return Pk1

def extract_Pk2(Q1, k, v, m):
    """Extrae la submatriz Pk2 de Q1 (términos bilineales entre vinagre y aceite)."""
    Pk2 = np.zeros((v, m), dtype=int)
    column = v * (v + 1) // 2  # Empieza después de los términos de vinagre
    for i in range(v):
        for j in range(m):
            Pk2[i, j] = Q1[k, column]
            column += 1
    return Pk2

def flatten_upper_triangular(matrix):
    """Aplana una matriz triangular superior en un vector de acuerdo al orden lexicográfico."""
    flattened = []
    for i in range(matrix.shape[0]):
        for j in range(i, matrix.shape[1]):
            flattened.append(matrix[i, j])
    return np.array(flattened)

def select_shake_function(security_level):
    """Selecciona la función SHAKE adecuada según el nivel de seguridad."""
    if security_level == 1:
        return hashlib.shake_128
    elif security_level in [3,5]:
        return hashlib.shake_256
    else:
        raise ValueError("Nivel de seguridad no soportado")


def sign_message(private_key, message):
    """Genera una firma digital para un mensaje usando la clave privada."""
    shake_function = select_shake_function(SECURITY_LEVEL)
    message_hash = shake_function(message.encode()).digest(32)
    signature = shake_function(private_key + message_hash).digest(32)
    
    return signature

def verify_signature(public_key, message, signature):
    """Verifica una firma digital usando la clave pública."""
    public_seed, Q2 = public_key
    shake_function = select_shake_function(SECURITY_LEVEL)
    message_hash = shake_function(message.encode()).digest(32)
    expected_signature = shake_function(public_seed + message_hash).digest(32)
    
    return expected_signature == signature
