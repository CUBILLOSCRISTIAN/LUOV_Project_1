import hashlib
import os
import numpy as np
from constants import m, v, n
from utils import SqueezePublicSeed, SqueezePublicMap, BuildAugmentedMatrix, GaussianElimination

def generate_public_seed_and_T(private_seed):
    """Generates the public seed and T matrix from the private seed."""
    public_seed = private_seed[:32]  # Extract the first 32 bytes as the public seed
    T = np.random.randint(0, 256, size=(v, m), dtype=np.uint8)  # Generate a random T matrix
    return public_seed, T


def Hash(message, length):
    """Generate a hash of the given message using SHAKE256."""
    import hashlib
    shake = hashlib.shake_256()
    shake.update(message)
    digest = shake.digest(length)
    # Convert the hash to a numeric numpy array
    return np.frombuffer(digest, dtype=np.uint8)

def Sign(private_seed, message):
    """Signs a message."""
    public_seed, T = generate_public_seed_and_T(private_seed)
    C, L, Q1 = SqueezePublicMap(public_seed)

    # Debugging: Log shapes
    print(f"Initial T shape: {T.shape}, L shape: {L.shape}")

    salt = os.urandom(16)  # Generate random salt
    h = Hash(message + b"\x00" + salt, m)

    while True:
        vinegar_vector = np.random.randint(0, 256, size=v, dtype=np.uint8)
        try:
            A = BuildAugmentedMatrix(C, L, Q1, T, h, vinegar_vector)
            solution = GaussianElimination(A)
            if solution is not None:
                oil_vector = solution
                break
        except ValueError as e:
            print(f"Error in BuildAugmentedMatrix: {e}")
            continue

    s = np.concatenate((vinegar_vector, oil_vector))
    return s, salt
