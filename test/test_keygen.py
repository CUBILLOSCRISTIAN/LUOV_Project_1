# test_keygen.py

import unittest
from src.keygen import keygen

class TestKeyGen(unittest.TestCase):
    
    def test_keygen_output(self):
        """Prueba que el algoritmo KeyGen retorne claves válidas."""
        public_key, private_key = keygen()
        self.assertEqual(len(private_key), 32, "La clave privada debe tener 32 bytes.")
        self.assertIsInstance(public_key, tuple, "La clave pública debe ser una tupla.")
        self.assertEqual(len(public_key[0]), 32, "La semilla pública debe tener 32 bytes.")
    
if __name__ == '__main__':
    unittest.main()
