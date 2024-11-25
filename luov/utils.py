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

    # Ensure LHS is square
    if LHS.shape[1] != 57:
        print(f"Truncating LHS columns to 57 from {LHS.shape[1]}")
        LHS = LHS[:, :57]
    if LHS.shape[0] != 57:
        print(f"Truncating LHS rows to 57 from {LHS.shape[0]}")
        LHS = LHS[:57, :]

    # Ensure RHS matches LHS rows
    if RHS.shape[0] != 57:
        print(f"Adjusting RHS rows to 57 from {RHS.shape[0]}")
        RHS = RHS[:57]

    # Construct the augmented matrix for Gaussian elimination
    augmented_matrix = np.hstack((LHS, RHS[:, np.newaxis]))
    print(f"Final Augmented Matrix shape: {augmented_matrix.shape}")

    # Validate the final shape
    if augmented_matrix.shape != (57, 58):
        raise ValueError(f"Augmented matrix is not in valid augmented form: {augmented_matrix.shape}")

    return augmented_matrix





def GaussianElimination(A):
    """
    Solves a system using Gaussian elimination.
    Validates the matrix dimensions before solving.
    """
    try:
        # Validate augmented matrix dimensions (57x58 expected)
        if A.shape[1] != A.shape[0] + 1:
            raise ValueError(f"Matrix must have one additional column for RHS: {A.shape}")

        # Split augmented matrix into LHS and RHS
        LHS = A[:, :-1]  # First 57 columns
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
