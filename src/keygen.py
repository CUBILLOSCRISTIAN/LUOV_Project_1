# keygen.py
import os
import numpy as np
import sys
from utils import (
    FindPk1,
    FindPk2,
    flatten_upper_triangular,
    InitializeAndAbsorb,
    SqueezePublicSeed,
    SqueezeT,
    SqueezePublicMap,
)
from constants import m, v, SEED_SIZE


def generate_private_seed():
    """Genera una semilla privada segura de SEED_SIZE bytes."""
    return os.urandom(SEED_SIZE)


def find_Q2(Q1, T):
    """Genera la matriz Q2 basada en la matriz T y Q1, ajustada al tamaño esperado."""
    # Inicializamos Q2 como una matriz binaria con el tamaño correcto
    Q2 = np.zeros((m, (m * (m + 1)) // 2), dtype=int)

    for k in range(1, m):
        Pk1 = FindPk1(Q1, k, v)
        Pk2 = FindPk2(Q1, k, v, m)
        Pk3 = compute_Pk3(Pk1, Pk2, T)
        column = 1
        for i in range(1,m):
            Q2[k,column]= Pk3[i,i]
            column+=1
            for j in range (i+1,m):
                Q2[k,column]= Pk3[i,j]+Pk3[j,i]
                column +=1

    # # Asegurarse de que Q2 sea binaria
    # Q2 = np.mod(Q2, 2)

    # Compactar Q2 usando numpy.packbits
    Q2_packed = np.packbits(Q2, axis=1)

    return Q2_packed


def compute_Pk3(Pk1, Pk2, T):
    """Calcula la matriz Pk3 basada en Pk1, Pk2 y T."""
    # Calcula una combinación de formas cuadráticas:
    # La primera parte (-T.T @ Pk1 @ T) evalúa una forma cuadrática negativa,
    # mientras que la segunda parte (T.T @ Pk2) suma un término lineal.
    # En resumen, la expresión devuelve un escalar o matriz que depende de 
    # las interacciones entre las matrices T, Pk1, y Pk2.
    return -T.T @ Pk1 @ T + T.T @ Pk2


def generate_keys(private_seed):
    """Genera un par de claves (pública y privada) según el esquema LUOV."""

    private_sponge = InitializeAndAbsorb(private_seed)

    public_seed = SqueezePublicSeed(private_sponge)

    # Generar la matriz T (v x m) con valores aleatorios
    T = SqueezeT(private_sponge)

    # 3. Generar las matrices C, L y Q1 usando la semilla pública
    C, L, Q1 = SqueezePublicMap(public_seed)

    Q2 = find_Q2(Q1, T)
    public_key = (public_seed, Q2)
    private_key = private_seed

    public_key_size = sys.getsizeof(public_seed) + sys.getsizeof(Q2)
    public_key_size_kb = public_key_size / 1024

    return public_key, private_key, public_key_size_kb


def main():
    # Generar una semilla privada
    private_seed = generate_private_seed()

    # Generar claves pública y privada
    public_key, private_key, public_key_size_kb = generate_keys(private_seed)

    print(f"Tamaño de la clave pública: {public_key_size_kb:.2f} KB")

    # Mensaje a firmar
    # message = "Este es el mensaje que estamos firmando"

    # # Firmar el mensaje
    # signature, salt = sign_message(private_key, message)
    # print(f"Firma: {signature}")
    # print(f"Salt: {salt}")

    # # Verificar la firma
    # is_valid = verify_signature(public_key, message, signature)
    # if is_valid:
    #     print("Firma válida")
    # else:
    #     print("Firma inválida")


if __name__ == "__main__":
    main()
