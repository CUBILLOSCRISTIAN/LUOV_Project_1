import hashlib
import numpy as np
from utils import SqueezePublicMap, BuildAugmentedMatrix, GaussianElimination
from constants import m, v

def verify_signature(public_key, message, signature):
    """Verifies a signature."""
    public_seed, Q2 = public_key
    C, L, Q1 = SqueezePublicMap(public_seed)

    # Extract salt and s from the signature
    salt = signature[-16:]
    s = signature[:-16]

    # Ensure s has enough elements for the vinegar vector
    if len(s) < v:
        raise ValueError(f"Signature is too short to extract a vinegar vector of size {v}.")
    vinegar_vector = s[:v]

    # Generate hash h
    h = hashlib.shake_256(message + b"\x00" + salt).digest(m)

    # Debug dimensions before building matrix
    print(f"Q2 shape: {Q2.shape}, C shape: {C.shape}, L shape: {L.shape}, Q1 shape: {Q1.shape}, h shape: {h.shape}")
    print(f"Vinegar vector shape: {vinegar_vector.shape}")

    # Build the augmented matrix
    A = BuildAugmentedMatrix(C, L, Q1, None, h, vinegar_vector)

    # Debug the augmented matrix shape
    print(f"Augmented matrix shape: {A.shape}")

    # Solve using Gaussian elimination
    solution = GaussianElimination(A)
    return solution is not None
