# utils.py

import hashlib
import os
import sys
import numpy as np

from constants import SECURITY_LEVEL, m, v, n, SEED_SIZE


def InitializeAndAbsorb(private_seed):
    """Inicializa y absorbe la semilla privada para generar el estado del SHAKE128."""
    shake_function = select_shake_function(SECURITY_LEVEL)
    return shake_function(private_seed).digest(SEED_SIZE)


def SqueezePublicSeed(private_sponge):
    """Extrae la semilla pública del estado del SHAKE128."""
    public_seed = private_sponge[:32]
    print(len(public_seed))
    return public_seed


def FindPk1(Q1, k, v):
    """Extrae la submatriz Pk1 de Q1, que representa los términos cuadráticos en variables de vinagre."""
    Pk1 = np.zeros((v, v), dtype=int)
    column = 1  # El primer término cuadrático empieza en la columna 0 de Q1
    # Recorremos la mitad superior de la matriz cuadrada de vinagre
    for i in range(1,v):
        for j in range(i, v):
            Pk1[i, j] = Q1[k, column]
            # Pk1[j, i] = Pk1[i, j]  # Simetría de los términos cuadráticos
            column += 1
        column += m
    return Pk1


def FindPk2(Q1, k, v, m):
    """Extrae la submatriz Pk2 de Q1, que representa los términos bilineales entre vinagre y aceite."""
    Pk2 = np.zeros((v, m), dtype=int)
    column = 1  # Empieza después de los términos cuadráticos en vinagre

    # Recorremos los términos bilineales
    for i in range(1,v):
        column += v-i+1
        for j in range(1,m):
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
    elif security_level in [3, 5]:
        return hashlib.shake_256
    else:
        raise ValueError("Nivel de seguridad no soportado")


def SqueezeT(private_sponge):
    """Genera la matriz T (v x m) a partir de la semilla privada."""
    shake_function = select_shake_function(SECURITY_LEVEL)
    num_bits = v * m
    num_bytes = (
        num_bits + 7
    ) // 8  # Redondear hacia arriba para obtener el número de bytes necesarios
    shake_output = shake_function(private_sponge).digest(num_bytes)
    T_bits = squeeze_bits_from_shake(shake_output, num_bits)
    return np.array(T_bits).reshape(v, m)


def squeeze_bits_from_shake(shake_output, num_bits):
    """Convert SHAKE output into a list of bits."""
    bits = []
    for byte in shake_output:
        bits.extend([int(bit) for bit in format(byte, "08b")])
    return bits[:num_bits]


def SqueezePublicMap(public_seed):
    """Genera las matrices C, L, y Q1 a partir de la semilla pública usando SHAKE128."""
    # C necesita m bits, L necesita m * n bits, y Q1 necesita m * (v * (v + 1) // 2 + v * m) bits
    C_bits_needed = m
    L_bits_needed = m * n
    Q1_bits_needed = m * (((v * (v + 1)) // 2) + v * m)

    total_bits_needed = C_bits_needed + L_bits_needed + Q1_bits_needed

    # Aquí generamos la cantidad correcta de bits, dividiendo entre 8 para convertir bits a bytes
    shake_function = select_shake_function(SECURITY_LEVEL)
    shake_output = shake_function(public_seed).digest((total_bits_needed + 7) // 8)

    bits = squeeze_bits_from_shake(shake_output, total_bits_needed)

    # Separar los bits en las matrices correspondientes
    C_bits = bits[:C_bits_needed]
    L_bits = bits[C_bits_needed : C_bits_needed + L_bits_needed]
    Q1_bits = bits[C_bits_needed + L_bits_needed :]

    # Convertir a matrices
    C = np.array(C_bits)
    L = np.array(L_bits).reshape(m, n)
    Q1 = np.array(Q1_bits).reshape(m, (v * (v + 1)) // 2 + v * m)

    return C, L, Q1
