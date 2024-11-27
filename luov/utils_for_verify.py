import hashlib
import numpy as np
from utils import SqueezePublicMap, BuildAugmentedMatrix, GaussianElimination
from constants import m, v

def verify_signature(public_key, message, signature):
    public_seed, Q2 = public_key
    C, L, Q1 = SqueezePublicMap(public_seed)

    # Extract salt and s from the signature
    salt = signature[-16:]  # Last 16 bytes are the salt
    s = signature[:-16]     # Rest is the signature vector

    # Ensure the vinegar vector is correctly extracted
    if len(s) < v:
        raise ValueError(f"Signature is too short to extract a vinegar vector of size {v}.")
    vinegar_vector = s[:v]

    # Convert message to a numpy array (if it’s not already)
    if isinstance(message, str):
        message = np.array(list(message.encode("utf-8")), dtype=np.uint8)
    elif isinstance(message, bytes):
        message = np.array(list(message), dtype=np.uint8)

    # Ensure salt is a numpy array
    if isinstance(salt, np.ndarray):
        salt_array = salt
    else:
        salt_array = np.array(list(salt), dtype=np.uint8)

    # Debugging: Validate types before concatenation
    print(f"Message type: {type(message)}, Message shape: {message.shape}")
    print(f"Salt type: {type(salt_array)}, Salt shape: {salt_array.shape}")

    # Concatenate message and salt as numpy arrays
    combined = np.concatenate((message, np.array([0], dtype=np.uint8), salt_array))

    # Generate hash
    try:
        h = hashlib.shake_256(combined.tobytes()).digest(m)
        h = np.frombuffer(h, dtype=np.uint8)  # Convert hash to a NumPy array
    except Exception as e:
        raise ValueError(f"Error generating hash: {e}")

    # Debugging information
    print(f"Q2 shape: {Q2.shape}")
    print(f"C shape: {C.shape}, L shape: {L.shape}, Q1 shape: {Q1.shape}, h length: {len(h)}")
    print(f"Vinegar vector shape: {vinegar_vector.shape}")

    # Build the augmented matrix
    try:
        A = BuildAugmentedMatrix(C, L, Q1, None, h, vinegar_vector)
        print(f"Augmented matrix shape: {A.shape}")
    except Exception as e:
        raise ValueError(f"Error building augmented matrix: {e}")

    # Solve using Gaussian elimination
    try:
        solution = GaussianElimination(A)
        return solution is not None
    except Exception as e:
        raise ValueError(f"Error solving augmented matrix: {e}")
