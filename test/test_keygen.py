import unittest
import numpy as np
from src.keygen import generate_private_seed, generate_keys, find_Q2, compute_Pk3
from src.utils import (
    InitializeAndAbsorb,
    SqueezePublicSeed,
    SqueezeT,
    SqueezePublicMap,
    FindPk1,
    FindPk2,
    flatten_upper_triangular,
)
from src.constants import m, v, SEED_SIZE, SECURITY_LEVEL


class TestLUOV(unittest.TestCase):

    def test_generate_private_seed(self):
        seed = generate_private_seed()
        self.assertEqual(len(seed), SEED_SIZE)
        self.assertIsInstance(seed, bytes)

    def test_initialize_and_absorb(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        self.assertEqual(len(sponge), SEED_SIZE)
        self.assertIsInstance(sponge, bytes)

    def test_squeeze_public_seed(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        public_seed = SqueezePublicSeed(sponge)
        self.assertEqual(len(public_seed), 32)
        self.assertIsInstance(public_seed, bytes)

    def test_squeeze_t(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        T = SqueezeT(sponge)
        self.assertEqual(T.shape, (v, m))
        self.assertTrue(np.all((T == 0) | (T == 1)))  # Check if T is binary

    def test_squeeze_public_map(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        public_seed = SqueezePublicSeed(sponge)
        C, L, Q1 = SqueezePublicMap(public_seed)
        self.assertEqual(C.shape, (m,))
        self.assertEqual(L.shape, (m, v))
        self.assertEqual(Q1.shape, (m, (v * (v + 1)) // 2 + v * m))

    def test_find_pk1(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        public_seed = SqueezePublicSeed(sponge)
        _, _, Q1 = SqueezePublicMap(public_seed)
        Pk1 = FindPk1(Q1, 0, v)
        self.assertEqual(Pk1.shape, (v, v))

    def test_find_pk2(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        public_seed = SqueezePublicSeed(sponge)
        _, _, Q1 = SqueezePublicMap(public_seed)
        Pk2 = FindPk2(Q1, 0, v, m)
        self.assertEqual(Pk2.shape, (v, m))

    def test_flatten_upper_triangular(self):
        matrix = np.array([[1, 2, 3], [0, 4, 5], [0, 0, 6]])
        flattened = flatten_upper_triangular(matrix)
        self.assertTrue(np.array_equal(flattened, [1, 2, 3, 4, 5, 6]))

    def test_compute_pk3(self):
        Pk1 = np.random.randint(0, 2, (v, v))
        Pk2 = np.random.randint(0, 2, (v, m))
        T = np.random.randint(0, 2, (v, m))
        Pk3 = compute_Pk3(Pk1, Pk2, T)
        self.assertEqual(Pk3.shape, (m, m))

    def test_find_q2(self):
        seed = generate_private_seed()
        sponge = InitializeAndAbsorb(seed)
        public_seed = SqueezePublicSeed(sponge)
        _, _, Q1 = SqueezePublicMap(public_seed)
        T = SqueezeT(sponge)
        Q2 = find_Q2(Q1, T)
        self.assertEqual(Q2.shape, (m, (m * (m + 1)) // 2//8))

    def test_keygen(self):
        seed = generate_private_seed()
        public_key, private_key, public_key_size_kb = generate_keys(seed)
        self.assertIsInstance(public_key, tuple)
        self.assertIsInstance(private_key, bytes)
        self.assertGreater(public_key_size_kb, 0)


if __name__ == "__main__":
    unittest.main()