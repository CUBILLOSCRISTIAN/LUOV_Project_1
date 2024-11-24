# keygen.py
import os
import numpy as np
from utils import SqueezePublicSeed, SqueezePublicMap
from constants import m, v, SEED_SIZE

def generate_private_seed():
    """Generates a secure private seed."""
    return os.urandom(SEED_SIZE)

def generate_keys(private_seed):
    """Generates public and private keys."""
    public_seed = SqueezePublicSeed(private_seed)
    C, L, Q1 = SqueezePublicMap(public_seed)
    Q2 = np.random.randint(0, 256, size=(m, (v * (v + 1)) // 2 + v * m), dtype=np.uint8)
    public_key = (public_seed, Q2)
    private_key = private_seed
    return public_key, private_key

if __name__ == "__main__":
    private_seed = generate_private_seed()
    print(f"Private Seed: {private_seed.hex()}")

    public_key, private_key = generate_keys(private_seed)
    print(f"Public Key: {public_key}")
    print(f"Private Key: {private_key.hex()}")
