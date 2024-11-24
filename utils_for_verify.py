# utils_for_verify.py
import hashlib
import numpy as np
from utils import SqueezePublicMap, BuildAugmentedMatrix, GaussianElimination
from constants import m, v

def verify_signature(public_key, message, signature):
    """Verifies a signature."""
    public_seed, Q2 = public_key
    C, L, Q1 = SqueezePublicMap(public_seed)
    salt = signature[-16:]
    h = hashlib.sha256(message + salt).digest()[:m]

    s = signature[:-16]
    vinegar_vector = s[:v]
    A = BuildAugmentedMatrix(C, L, Q1, None, h, vinegar_vector)
    solution = GaussianElimination(A)

    return solution is not None
