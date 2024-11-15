 utils_for_verify.py

 def verify_signature(public_key, message, signature):
     public_seed, Q2 = public_key
     private_sponge = InitializeAndAbsorb(public_seed)

     C, L, Q1 = G(public_seed)

     salt = signature[-16:]
     h = hash_message(message, salt, SECURITY_LEVEL)

     V = signature[:-16]
     V = np.frombuffer(V, dtype=np.uint8)  # Convertir bytes a array de NumPy
     V = np.unpackbits(V)  # Desempaquetar bits para obtener un array de bits
     expected_length = (v * (v + 1)) // 2 + v * m
     V = V[:expected_length]

     A = BuildAugmentedMatrix(C, L, Q1, None, h, V)
     solution = GaussianElimination(A)

     # Verificar si la solución es válida
     if np.allclose(np.dot(A[:, :-1], solution), A[:, -1]):
         return True
     else:
         return False


 def EvaluatePublicMap(public_seed, Q2, s):
     # Paso 1: Generar C, L y Q1 a partir de la semilla pública
     C, L, Q1 = G(public_seed)

     # Paso 2: Concatenar Q1 y Q2 para formar Q
     Q = np.hstack((Q1, Q2))

     # Paso 3: Inicializar e con C y agregar la parte lineal Ls
     e = C + np.dot(L, s)

     # Paso 4: Inicializar la columna
     column = 0

     # Paso 5: Iterar sobre los índices i y j para evaluar las partes cuadráticas de P en s
     for i in range(len(s)):
         for j in range(i, len(s)):
             for k in range(len(C)):
                 e[k] += Q[k, column] * s[i] * s[j]
             column += 1

     # Paso 6: Devolver e
     return e
