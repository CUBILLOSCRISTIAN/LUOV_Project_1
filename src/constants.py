# constants.py

# Parámetros del esquema LUOV-7-57-197 (nivel de seguridad 1)
r = 7   # Grado de la extensión del campo F2 -> F2^r
m = 57  # Número de variables "oil"
v = 197 # Número de variables "vinegar"
n = m + v  # Número total de variables

# Tamaño de las semillas (32 bytes según la especificación)
SEED_SIZE = 32
SECURITY_LEVEL = 1  # Nivel de seguridad: 1, 3 o 5