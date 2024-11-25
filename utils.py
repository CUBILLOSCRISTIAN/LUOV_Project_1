# utils.py
import numpy as np
from constants import m, v, n

def SqueezePublicSeed(private_seed):
    """Extracts the public seed from the private seed."""
    return private_seed[:m]

def SqueezePublicMap(public_seed):
    """Extracts public parameters (C, L, Q1) from the public seed."""
    C = np.random.randint(0, 256, size=m, dtype=np.uint8)
    L = np.random.randint(0, 256, size=(m, n), dtype=np.uint8)
    Q1 = np.random.randint(0, 256, size=(m, (v * (v + 1)) // 2 + v * m), dtype=np.uint8)
    return C, L, Q1

def FindPk1(Q1, k, v):
    """Finds the Pk1 matrix for the k-th row."""
    Pk1 = np.zeros((v, v), dtype=int)
    column = 0
    for i in range(v):
        for j in range(i, v):
            Pk1[i, j] = Q1[k, column]
            column += 1
    return Pk1

def FindPk2(Q1, k, v, m):
    """Finds the Pk2 matrix for the k-th row."""
    Pk2 = np.zeros((v, m), dtype=int)
    column = (v * (v + 1)) // 2
    for i in range(v):
        for j in range(m):
            Pk2[i, j] = Q1[k, column]
            column += 1
    return Pk2

def BuildAugmentedMatrix(C, L, Q1, T, h, vinegar_vector):
    """Builds the augmented matrix for signature verification."""
    RHS = h - C - np.dot(L, vinegar_vector)
    LHS = np.zeros_like(RHS)  # Placeholder for LHS logic
    return np.hstack((LHS, RHS[:, np.newaxis]))

def GaussianElimination(A):
    """Solves a system using Gaussian elimination."""
    try:
        return np.linalg.solve(A[:, :-1], A[:, -1])
    except np.linalg.LinAlgError:
        return None
