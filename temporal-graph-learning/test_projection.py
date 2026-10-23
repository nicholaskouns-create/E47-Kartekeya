import unittest
import numpy as np
from projection import make_projector, project_embeddings


class ProjectionTests(unittest.TestCase):
    def test_rank_symmetry_idempotence(self):
        for d in (64, 128, 125):
            p = make_projector(d, seed=47)
            self.assertEqual(np.linalg.matrix_rank(p, tol=1e-8), int(d * 47 / 125))
            self.assertTrue(np.allclose(p, p.T, atol=1e-12))
            self.assertTrue(np.allclose(p @ p, p, atol=1e-12))

    def test_deterministic(self):
        self.assertTrue(np.array_equal(make_projector(64, 7), make_projector(64, 7)))

    def test_projection(self):
        h = np.arange(3 * 64).reshape(3, 64)
        p = make_projector(64)
        self.assertTrue(np.allclose(project_embeddings(h, p) @ p, project_embeddings(h, p)))


if __name__ == "__main__":
    unittest.main()
