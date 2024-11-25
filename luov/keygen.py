import os
import numpy as np
from constants import m, v, SEED_SIZE
from shared_utils import SqueezePublicSeed, SqueezePublicMap

def generate_private_seed():
    """Generates a secure private seed of at least 57 bytes."""
    return os.urandom(max(SEED_SIZE, 57))  # Ensure minimum size is 57 bytes


def generate_keys(private_seed):
    """Generates public and private keys."""
    public_seed = SqueezePublicSeed(private_seed)
    C, L, Q1 = SqueezePublicMap(public_seed)
    
    # Corrected expected columns calculation
    expected_columns = ((v * (v + 1)) // 2) + (v * m)  # Formula for expected dimensions
    Q2 = np.random.randint(0, 256, size=(57, expected_columns), dtype=np.uint8)
    
    # Debugging statements
    print(f"Generated Q2 Shape: {Q2.shape}")
    
    public_key = (public_seed, Q2)
    private_key = private_seed
    return public_key, private_key
