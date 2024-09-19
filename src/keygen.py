# keygen.py
import os
import numpy as np
import sys
from utils import shake128, extract_Pk1, extract_Pk2, flatten_upper_triangular
from constants import r, m, v, n, SEED_SIZE

def generate_private_seed():
    """Genera una semilla privada segura de SEED_SIZE bytes."""
    return os.urandom(SEED_SIZE)

def find_Q2(Q1, T):
    """Genera la matriz Q2 basada en la matriz T y Q1, ajustada al tamaño esperado."""
    # Inicializamos Q2 como una matriz binaria con el tamaño correcto
    Q2 = np.zeros((m, (m * (m + 1)) // 2), dtype=int)
    
    for k in range(m):
        Pk1 = extract_Pk1(Q1, k, v)
        Pk2 = extract_Pk2(Q1, k, v, m)
        Pk3 = compute_Pk3(Pk1, Pk2, T)
        Q2[k] = flatten_upper_triangular(Pk3)  # Aplanar la matriz para llenar Q2

    # Asegurarse de que Q2 sea binaria
    Q2 = np.mod(Q2, 2)
    
    # Compactar Q2 usando numpy.packbits
    Q2_packed = np.packbits(Q2, axis=1)
    
    return Q2_packed

def compute_Pk3(Pk1, Pk2, T):
    """Calcula la matriz Pk3 basada en Pk1, Pk2 y T."""
    return -T.T @ Pk1 @ T + T.T @ Pk2

def keygen():
    """Genera un par de claves (pública y privada) según el esquema LUOV."""
    # 1. Generar la semilla privada
    private_seed = generate_private_seed()

    # 2. Usar SHAKE128 para generar la semilla pública y la matriz T
    public_seed = shake128(private_seed, SEED_SIZE)
    
    # Generar la matriz T (v x m) con valores aleatorios
    T = np.random.randint(0, 2, (v, m))  # Matriz binaria

    # 3. Generar las matrices C, L y Q1 usando la semilla pública
    C = np.random.randint(0, 2, m)        # Parte constante
    L = np.random.randint(0, 2, (m, n))   # Parte lineal
    Q1 = np.random.randint(0, 2, (m, (v * (v + 1)) // 2 + v * m))  # Parte cuadrática inicial
    
    # 4. Generar la matriz cuadrática Q2 a partir de T y Q1
    Q2 = find_Q2(Q1, T)

    # Clave pública incluye la semilla pública y la matriz Q2
    public_key = (public_seed, Q2)

    # La clave privada es simplemente la semilla privada
    private_key = private_seed

    # Verificar el tamaño de la clave pública
    public_key_size = sys.getsizeof(public_seed) + sys.getsizeof(Q2)
    public_key_size_kb = public_key_size / 1024

    return public_key, private_key, public_key_size_kb

if __name__ == "__main__":
    public_key, private_key, public_key_size_kb = keygen()
    print("Clave pública:", public_key)
    print("Clave privada:", private_key)
    print(f"Tamaño de la clave pública: {public_key_size_kb:.2f} KB")