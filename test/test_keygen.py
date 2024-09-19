import unittest
import os
import numpy as np
from src import compute_Pk3

from src.utils import (
    generate_private_seed,
    InitializeAndAbsorb,
    SqueezePublicSeed,
    SqueezeT,
    SqueezePublicMap,
    find_Q2,
    sign_message,
    verify_signature,
)
from src.constants import SEED_SIZE, SECURITY_LEVEL


class TestLUOV(unittest.TestCase):
    def setUp(self):
        self.private_seed = generate_private_seed()
        self.message = "Este es el mensaje que estamos firmando"

    def test_generate_private_seed(self):
        seed = generate_private_seed()
        self.assertEqual(len(seed), SEED_SIZE)

    def test_keygen(self):
        private_sponge = InitializeAndAbsorb(self.private_seed)
        public_seed = SqueezePublicSeed(private_sponge)
        T = SqueezeT(private_sponge)
        C, L, Q1 = SqueezePublicMap(public_seed)
        Q2 = find_Q2(Q1, T)
        self.assertIsNotNone(public_seed)
        self.assertIsNotNone(T)
        self.assertIsNotNone(C)
        self.assertIsNotNone(L)
        self.assertIsNotNone(Q1)
        self.assertIsNotNone(Q2)

    def test_sign_and_verify(self):
        public_key, private_key, _ = keygen(self.private_seed)
        signature, salt = sign_message(private_key, self.message)
        is_valid = verify_signature(
            public_key, self.message, signature, salt, SECURITY_LEVEL
        )
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()
