import numpy as np
from constants import m, v, n

def SqueezePublicSeed(private_seed):
    return private_seed[:32]


def SqueezePublicMap(public_seed):
    """Generates public map parameters."""
    C = np.random.randint(0, 256, size=57, dtype=np.uint8)
    L = np.random.randint(0, 256, size=(57, 254), dtype=np.uint8)
    Q1 = np.random.randint(0, 256, size=(57, ((197 * (197 + 1)) // 2) + (197 * 57)), dtype=np.uint8)
    return C, L, Q1

