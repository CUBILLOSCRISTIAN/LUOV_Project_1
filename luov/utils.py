# utils.py
import numpy as np
from constants import m, v, n

def SqueezePublicSeed(private_seed):
    """
    Extracts the public seed from the private seed.

    Args:
        private_seed (bytes): The private seed.

    Returns:
        bytes: The public seed derived from the private seed.
    """
    return private_seed[:m]

def SqueezePublicMap(public_seed):
    """
    Extracts public parameters (C, L, Q1) from the public seed.

    Args:
        public_seed (bytes): The public seed.

    Returns:
        tuple: Randomly generated public parameters (C, L, Q1).
    """
    np.random.seed(int.from_bytes(public_seed, 'big') % (2**32))  # Seed numpy RNG for reproducibility
    C = np.random.randint(0, 256, size=m, dtype=np.uint8)
    L = np.random.randint(0, 256, size=(m, n), dtype=np.uint8)
    Q1 = np.random.randint(0, 256, size=(m, (v * (v + 1)) // 2 + v * m), dtype=np.uint8)
    return C, L, Q1

def BuildAugmentedMatrix(C, L, Q1, T, h, vinegar_vector):
    """
    Constructs a valid augmented matrix for LUOV operations.
    Ensures the augmented matrix is logically consistent and Gaussian elimination-ready.
    """
    print("C shape:", C.shape)
    print("L shape:", L.shape)
    print("Q1 shape:", Q1.shape if Q1 is not None else "None")
    print("vinegar_vector shape before adjustment:", vinegar_vector.shape)

    # Adjust vinegar_vector to match L's columns
    if vinegar_vector.shape[0] != L.shape[1]:
        print(f"Adjusting vinegar_vector from {vinegar_vector.shape[0]} to {L.shape[1]}")
        if vinegar_vector.shape[0] > L.shape[1]:
            vinegar_vector = vinegar_vector[:L.shape[1]]  # Truncate if larger
        else:
            vinegar_vector = np.pad(vinegar_vector, (0, L.shape[1] - vinegar_vector.shape[0]))  # Pad if smaller

    # Convert C and h to numpy arrays
    C = np.asarray(C, dtype=np.int64)
    h = np.asarray(h, dtype=np.int64)

    # Compute RHS
    RHS = h - C - np.dot(L, vinegar_vector)
    print(f"Computed RHS shape: {RHS.shape}")

    # Compute LHS
    LHS = L
    if T is not None:
        if T.shape[0] != LHS.shape[0]:
            print(f"Adjusting T rows from {T.shape[0]} to {LHS.shape[0]}")
            T = T[:LHS.shape[0], :]
        LHS = np.hstack((LHS, -T))
    print(f"Computed LHS shape: {LHS.shape}")

    # Dynamically adjust LHS and RHS based on current shape
    min_dim = min(LHS.shape[0], LHS.shape[1])
    LHS = LHS[:min_dim, :min_dim]
    RHS = RHS[:min_dim]

    # Construct the augmented matrix for Gaussian elimination
    augmented_matrix = np.hstack((LHS, RHS[:, np.newaxis]))
    print(f"Final Augmented Matrix shape: {augmented_matrix.shape}")

    return augmented_matrix

def GaussianElimination(A):
    """
    Solves a system using Gaussian elimination.
    Validates the matrix dimensions before solving.
    """
    try:
        # Validate augmented matrix dimensions (n x (n+1) expected)
        if A.shape[1] != A.shape[0] + 1:
            raise ValueError(f"Matrix must have one additional column for RHS: {A.shape}")

        # Split augmented matrix into LHS and RHS
        LHS = A[:, :-1]  # First n columns
        RHS = A[:, -1]   # Last column (RHS)

        # Perform Gaussian elimination (solve the linear system)
        solution = np.linalg.solve(LHS, RHS)
        return solution

    except ValueError as ve:
        print(f"Gaussian elimination error: {ve}")
        return None
    except np.linalg.LinAlgError as e:
        print(f"Gaussian elimination failed: {e}")
        return None
