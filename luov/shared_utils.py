import numpy as np
from constants import m, v

def SqueezePublicSeed(private_seed):
    return private_seed[:32]

def SqueezePublicMap(public_seed):
    C = np.random.randint(0, 256, size=m, dtype=np.uint8)
    L = np.random.randint(0, 256, size=(m, 254), dtype=np.uint8)
    Q1 = np.random.randint(0, 256, size=(m, ((v * (v + 1)) // 2) + (v * m)), dtype=np.uint8)
    return C, L, Q1
