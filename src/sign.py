import hashlib
import numpy as np

from constants import  m, v, r
from utils import (
    FindPk1,
    FindPk2,
    SqueezePublicMap as G,
)


def BuildAugmentedMatrix(C, L, Q1, T, h, v):
    m = C.shape[0]
    n = L.shape[1]
    v_len = v.shape[0]

    # Inicializar RHS
    RHS = h - C - np.dot(L, np.concatenate((v, np.zeros(n - v_len))))

    # Inicializar LHS
    LHS = np.hstack((L, -T))

    for k in range(m):
        Pk1 = FindPk1(k, Q1)
        Pk2 = FindPk2(k, Q1)

        # Actualizar RHS[k]
        RHS[k] -= np.dot(v.T, np.dot(Pk1, v))

        # Calcular Fk,2
        Fk2 = -(Pk1 + Pk1.T) @ T + Pk2

        # Actualizar LHS[k]
        LHS[k] += np.dot(v, Fk2)

    # Construir la matriz aumentada
    A = np.hstack((LHS, RHS[:, np.newaxis]))
    return A


def GaussianElimination(A):
    rows, cols = A.shape
    for i in range(rows):
        # Hacer que el pivote sea 1
        A[i] = A[i] / A[i, i]

        # Hacer ceros en la columna i
        for j in range(i + 1, rows):
            A[j] = A[j] - A[j, i] * A[i]

    # Sustitución hacia atrás
    x = np.zeros(rows)
    for i in range(rows - 1, -1, -1):
        x[i] = A[i, -1] - np.dot(A[i, i + 1 : rows], x[i + 1 : rows])

    return x


def hash_message(message, salt, security_level):
    return hashlib.sha256(salt + message.encode()).digest()[: security_level // 8]


def Hash(data, length):
    # Calcular el hash SHA-256 del dato
    hash_digest = hashlib.sha256(data).digest()

    # Convertir el hash digest a un vector sobre F_{2^r} de longitud m
    bit_string = "".join(format(byte, "08b") for byte in hash_digest)
    bit_vector = [int(bit_string[i : i + r], 2) for i in range(0, length * r, r)]

    return np.array(bit_vector[:length])


def generate_public_seed_and_T(private_seed):
    # Calcular el número de bytes necesarios para T
    dm8e = (m + 7) // 8  # Redondear hacia arriba la división de m entre 8
    length = 32 + v * dm8e

    # Evaluar H(private_seed, length)
    hash_output = hashlib.sha256(private_seed).digest()[:length]

    # Los primeros 32 bytes forman la semilla pública
    public_seed = hash_output[:32]

    # Los bytes restantes forman la matriz T
    T_bytes = hash_output[32:]
    T = np.zeros((v, m), dtype=int)

    for i in range(v):
        row_bytes = T_bytes[i * dm8e : (i + 1) * dm8e]
        row_bits = "".join(format(byte, "08b") for byte in row_bytes)
        T[i, :] = [int(bit) for bit in row_bits[:m]]

    return public_seed, T


def RandomBytes(length):
    return np.random.bytes(length)


def Sign(private_seed, message):
    # Paso 1: Generar la semilla pública y la matriz T
    public_seed, T = generate_public_seed_and_T(private_seed)

    # Paso 2: Generar C, L y Q1 a partir de la semilla pública
    C, L, Q1 = G(public_seed)

    # Paso 3: Generar un salt aleatorio de 16 bytes
    salt = RandomBytes(16)

    # Paso 4: Calcular el hash h del mensaje concatenado con 0x00 y el salt
    h = Hash(message + b"\x00" + salt, salt)

    # Paso 5: Bucle hasta encontrar una solución
    while True:
        # Paso 6: Generar un vector v aleatorio
        V = RandomBytes(r * v // 8)

        # Paso 7: Construir la matriz aumentada A
        A = BuildAugmentedMatrix(C, L, Q1, T, h, V)

        # Paso 9: Aplicar eliminación gaussiana a A
        solution = GaussianElimination(A)

        # Paso 10: Verificar si el sistema tiene una solución única o
        if solution is not None:
            o = solution
            s0 = np.concatenate((v, o))
            break

    # Paso 14: Calcular s usando s0 y T
    s = np.dot(np.hstack((np.eye(v.shape[0]), -T)), s0)

    # Paso 15: Devolver s y salt
    return s, salt
