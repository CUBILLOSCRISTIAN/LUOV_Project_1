# utils_for_verify.py

import hashlib
import os
import numpy as np

from constants import SECURITY_LEVEL, m, v, r
from utils import (
    FindPk1,
    FindPk2,
    InitializeAndAbsorb,
    SqueezePublicMap,
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


def H(data):
    # Implementar la función hash H
    pass


def G(public_seed):
    # Implementar la función G que genera C, L y Q1 a partir de la semilla pública
    pass


def RandomBytes(length):
    return np.random.bytes(length)


def Sign(private_seed, message):
    # Paso 1: Generar la semilla pública y la matriz T
    public_seed, T = H(private_seed)

    # Paso 2: Generar C, L y Q1 a partir de la semilla pública
    C, L, Q1 = G(public_seed)

    # Paso 3: Generar un salt aleatorio de 16 bytes
    salt = RandomBytes(16)

    # Paso 4: Calcular el hash h del mensaje concatenado con 0x00 y el salt
    h = hash_message(message + b"\x00" + salt, salt, SECURITY_LEVEL)

    # Paso 5: Bucle hasta encontrar una solución
    while True:
        # Paso 6: Generar un vector v aleatorio
        v = RandomBytes(r * v // 8)

        # Paso 7: Construir la matriz aumentada A
        A = BuildAugmentedMatrix(C, L, Q1, T, h, v)

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


def verify_signature(public_key, message, signature):
    public_seed, Q2 = public_key
    private_sponge = InitializeAndAbsorb(public_seed)

    C, L, Q1 = SqueezePublicMap(public_seed)

    salt = signature[-16:]
    h = hash_message(message, salt, SECURITY_LEVEL)

    V = signature[:-16]
    V = np.frombuffer(V, dtype=np.uint8)  # Convertir bytes a array de NumPy
    V = np.unpackbits(V)  # Desempaquetar bits para obtener un array de bits
    expected_length = (v * (v + 1)) // 2 + v * m
    V = V[:expected_length]

    A = BuildAugmentedMatrix(C, L, Q1, None, h, V)
    solution = GaussianElimination(A)

    # Verificar si la solución es válida
    if np.allclose(np.dot(A[:, :-1], solution), A[:, -1]):
        return True
    else:
        return False


def evaluate_public_map(Q2, z, public_seed):
    """Evalúa el polinomio cuadrático P en el punto z utilizando la clave pública."""
    # Inicializar con el término constante de C
    P_z = np.zeros(len(Q2[0]), dtype=int)

    # Evaluar la parte lineal y cuadrática (matrices Q2 y L)
    for i in range(len(Q2)):
        P_z[i] = np.dot(z, Q2[i])  # Evaluar el polinomio cuadrático en z

    return P_z
