# utils.py

import hashlib
import numpy as np

def shake128(data, output_length):
    """Genera un valor hash de longitud output_length bytes utilizando SHAKE128."""
    shake = hashlib.shake_128()
    shake.update(data)
    return shake.digest(output_length)

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
