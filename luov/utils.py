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

def FindPk1(Q1, k, v):
    """
    Finds the Pk1 matrix for the k-th row.

    Args:
        Q1 (numpy.ndarray): The Q1 matrix.
        k (int): The row index.
        v (int): Number of vinegar variables.

    Returns:
        numpy.ndarray: The Pk1 matrix for the k-th row.
    """
    Pk1 = np.zeros((v, v), dtype=int)
    column = 0
    for i in range(v):
        for j in range(i, v):
            Pk1[i, j] = Q1[k, column]
            column += 1
    return Pk1

def FindPk2(Q1, k, v, m):
    """
    Finds the Pk2 matrix for the k-th row.

    Args:
        Q1 (numpy.ndarray): The Q1 matrix.
        k (int): The row index.
        v (int): Number of vinegar variables.
        m (int): Number of oil variables.

    Returns:
        numpy.ndarray: The Pk2 matrix for the k-th row.
    """
    Pk2 = np.zeros((v, m), dtype=int)
    column = (v * (v + 1)) // 2
    for i in range(v):
        for j in range(m):
            Pk2[i, j] = Q1[k, column]
            column += 1
    return Pk2


def BuildAugmentedMatrix(C, L, Q1, T, h, vinegar_vector):
    """
    Builds the augmented matrix for signature generation and verification.
    Ensures dimensions of LHS and RHS match, and the resulting augmented matrix is square.
    """
    print("C shape:", C.shape)
    print("L shape:", L.shape)
    print("Q1 shape:", Q1.shape if Q1 is not None else "None")
    print("vinegar_vector shape before adjustment:", vinegar_vector.shape)

    # Adjust vinegar_vector to match L's columns
    if vinegar_vector.shape[0] != L.shape[1]:
        print(f"Adjusting vinegar_vector from {vinegar_vector.shape[0]} to {L.shape[1]}")
        vinegar_vector = np.resize(vinegar_vector, (L.shape[1],))

    # Adjust T to match L's rows, if provided
    if T is not None:
        T = T[:L.shape[0], :]

    # Convert C and h to numpy arrays if necessary
    C = np.asarray(C, dtype=np.int64)
    h = np.asarray(h, dtype=np.int64)

    # Compute RHS
    RHS = h - C - np.dot(L, vinegar_vector)
    print(f"Computed RHS shape: {RHS.shape}")

    # Compute LHS
    LHS = np.hstack((L, -T)) if T is not None else L
    print(f"Computed LHS shape: {LHS.shape}")

    # Ensure LHS is square by truncating columns
    if LHS.shape[1] > LHS.shape[0]:
        print(f"Truncating LHS columns from {LHS.shape[1]} to {LHS.shape[0]}")
        LHS = LHS[:, :LHS.shape[0]]
    elif LHS.shape[0] > LHS.shape[1]:
        print(f"Padding LHS columns from {LHS.shape[1]} to {LHS.shape[0]}")
        padding = np.zeros((LHS.shape[0], LHS.shape[0] - LHS.shape[1]), dtype=LHS.dtype)
        LHS = np.hstack((LHS, padding))

    # Ensure RHS matches LHS row count
    if RHS.shape[0] != LHS.shape[0]:
        print(f"Adjusting RHS size from {RHS.shape[0]} to {LHS.shape[0]}")
        RHS = RHS[:LHS.shape[0]]

    # Construct the augmented matrix
    augmented_matrix = np.hstack((LHS, RHS[:, np.newaxis]))
    print(f"Final Augmented Matrix shape: {augmented_matrix.shape}")

    # Ensure square matrix and raise an error if not
    if augmented_matrix.shape[0] != augmented_matrix.shape[1]:
        raise ValueError(f"Augmented matrix is not square after adjustment: {augmented_matrix.shape}")

    return augmented_matrix


def GaussianElimination(A):
    """
    Solves a system using Gaussian elimination.
    Ensures A is square before solving.
    """
    try:
        # Validate matrix dimensions
        if A.shape[0] != A.shape[1]:
            raise ValueError(f"Matrix is not square: {A.shape}")
        return np.linalg.solve(A[:, :-1], A[:, -1])
    except ValueError as ve:
        print(f"Gaussian elimination error: {ve}")
        return None
    except np.linalg.LinAlgError as e:
        print(f"Gaussian elimination failed: {e}")
        return None
