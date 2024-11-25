import hashlib
import numpy as np
from constants import m, v, r, SEED_SIZE

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


# sign.py (Corrected Hash function)
def Hash(message, length):
    """Generates a hash of the given message."""
    if not isinstance(length, int):
        raise TypeError(f"Expected integer for 'length', got {type(length).__name__}")

    # Use SHAKE256 to generate an extensible output hash
    hasher = hashlib.shake_256()
    hasher.update(message)
    bit_string = bin(int.from_bytes(hasher.digest((length * r + 7) // 8), "big"))[2:]
    bit_string = bit_string.zfill(length * r)
    bit_vector = [int(bit_string[i : i + r], 2) for i in range(0, length * r, r)]
    return np.array(bit_vector, dtype=np.uint8)



def generate_public_seed_and_T(private_seed):
    """Generates public seed and T matrix."""
    public_seed = private_seed[:SEED_SIZE]

    # Calculate the total number of bits required for T
    total_bits_needed = v * m
    total_bytes_needed = (total_bits_needed + 7) // 8  # Round up to nearest byte

    # Simulate sufficient output for T matrix
    shake_output = np.random.randint(0, 256, size=(total_bytes_needed,), dtype=np.uint8)
    shake_bits = np.unpackbits(shake_output)

    # Ensure we have enough bits for the entire matrix
    if len(shake_bits) < total_bits_needed:
        raise ValueError(f"SHAKE output insufficient: needed {total_bits_needed} bits, got {len(shake_bits)} bits")

    T = np.zeros((v, m), dtype=np.uint8)

    # Populate T matrix
    for i in range(v):
        start_index = i * m
        end_index = start_index + m
        row_bits = shake_bits[start_index:end_index]
        if len(row_bits) < m:
            raise ValueError(f"Not enough bits to populate row {i} of T: needed {m}, got {len(row_bits)}")
        T[i, :] = row_bits

    return public_seed, T



def RandomBytes(length):
    return np.random.bytes(length)


def Sign(private_seed, message):
    """Signs a message."""
    public_seed, T = generate_public_seed_and_T(private_seed)
    C, L, Q1 = SqueezePublicMap(public_seed)
    salt = os.urandom(16)  # Generate random salt
    h = Hash(message + b"\x00" + salt, m)  # Correctly pass m as length

    while True:
        vinegar_vector = np.random.randint(0, 256, size=v, dtype=np.uint8)
        A = BuildAugmentedMatrix(C, L, Q1, T, h, vinegar_vector)
        solution = GaussianElimination(A)
        if solution is not None:
            oil_vector = solution
            break

    s = np.concatenate((vinegar_vector, oil_vector))
    return s, salt
