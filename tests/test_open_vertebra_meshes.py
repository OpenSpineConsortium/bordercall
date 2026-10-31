"""The scripts that bring the open vertebra models to the branch `meshes`
(research_notes/open-vertebra-meshes): fetch.py keeps an STL, binary or ASCII, as an indexed mesh
whose faces give back its triangles; extract_meng.py reads a pickle holding chumpy and scipy objects
with neither library imported, keeps a chumpy array's values and a sparse matrix's parts, cuts a
shape space to its first modes, leaves the pose correctives out and splits an array one file cannot
hold, and DESCRIBE.md names every key.

    python -m unittest tests.test_open_vertebra_meshes -v      # from the repository's root, in the venv

The pickles are written in a child process from stand-in packages named chumpy and scipy, so the
module and class names inside them are the real libraries' and this process imports neither.
"""
import os
import struct
import subprocess
import sys
import tempfile
import textwrap
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.join(os.path.dirname(HERE), "research_notes", "open-vertebra-meshes")
sys.path.insert(0, NOTE)

import extract_meng as E  # noqa: E402
import fetch as F  # noqa: E402

TETRAHEDRON = np.array([[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                        [[0, 0, 0], [0, 1, 0], [0, 0, 1]],
                        [[0, 0, 0], [0, 0, 1], [1, 0, 0]],
                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]], dtype=np.float32) * 12.5

STAND_INS = {
    "chumpy/__init__.py": "",
    "chumpy/ch.py": """
        class Ch(object):
            def __init__(self, x):
                self.x = x
                self._cache = {"r": None}
            def __getstate__(self):
                return {"x": self.x}
    """,
    "scipy/__init__.py": "",
    "scipy/sparse/__init__.py": "",
    "scipy/sparse/csc.py": """
        class csc_matrix(object):
            def __init__(self, data, indices, indptr, shape):
                self.data, self.indices, self.indptr, self._shape = data, indices, indptr, shape
                self.maxprint = 50
    """,
}

WRITER = """
import pickle, sys
import numpy as np
from chumpy.ch import Ch
from scipy.sparse.csc import csc_matrix
rng = np.random.default_rng(0)
dense = np.zeros((4, 50)); dense[0, 3] = 0.5; dense[2, 7] = 0.25; dense[3, 49] = 1.0
cols = dense.T
indptr = np.concatenate([[0], np.cumsum((dense != 0).sum(axis=0))])
indices = np.concatenate([np.nonzero(dense[:, j])[0] for j in range(50)])
data = np.concatenate([dense[np.nonzero(dense[:, j])[0], j] for j in range(50)])
smpl = {"v_template": rng.normal(size=(50, 3)), "f": np.arange(30).reshape(10, 3),
        "shapedirs": Ch(rng.normal(size=(50, 3, 60))), "posedirs": rng.normal(size=(50, 3, 9)),
        "J_regressor": csc_matrix(data, indices, indptr, (4, 50)), "bs_style": "lbs",
        "weights": rng.normal(size=(50000, 24))}
ppca = {"M_pp": rng.normal(size=(153,)), "C": rng.normal(size=(153, 55)), "extra": {"sigma": 0.25}}
with open(sys.argv[1], "wb") as fh:
    pickle.dump(smpl, fh, 2)
with open(sys.argv[2], "wb") as fh:
    pickle.dump(ppca, fh, 2)
np.save(sys.argv[3], dense)
"""


def binary_stl(triangles):
    head = b"binary STL".ljust(80, b" ") + struct.pack("<I", len(triangles))
    body = b"".join(struct.pack("<3f", 0, 0, 0) + t.astype("<f4").tobytes() + b"\0\0" for t in triangles)
    return head + body


def ascii_stl(triangles):
    lines = ["solid t"]
    for t in triangles:
        lines += ["facet normal 0 0 0", "outer loop"] + ["vertex %r %r %r" % tuple(map(float, p)) for p in t]
        lines += ["endloop", "endfacet"]
    return ("\n".join(lines + ["endsolid t"]) + "\n").encode("ascii")


class STLKeptAsMesh(unittest.TestCase):
    def check(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = os.path.join(tmp, "L1.stl"), os.path.join(tmp, "out", "p01", "L1.stl")
            with open(src, "wb") as fh:
                fh.write(data)
            F.keep_mesh(src, dest)
            mesh = np.load(os.path.join(tmp, "out", "p01", "L1.npz"))
            self.assertEqual(mesh["v"].shape, (4, 3))
            self.assertEqual(mesh["f"].shape, (4, 3))
            np.testing.assert_array_equal(mesh["v"][mesh["f"]], TETRAHEDRON)

    def test_binary(self):
        self.check(binary_stl(TETRAHEDRON))

    def test_ascii(self):
        self.check(ascii_stl(TETRAHEDRON))


class MengReduced(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.tmp.name
        for rel, text in STAND_INS.items():
            path = os.path.join(root, "standins", rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                fh.write(textwrap.dedent(text))
        models = os.path.join(root, "models")
        os.makedirs(models)
        writer = os.path.join(root, "writer.py")
        with open(writer, "w") as fh:
            fh.write(WRITER)
        env = dict(os.environ, PYTHONPATH=os.path.join(root, "standins"))
        subprocess.check_call([sys.executable, writer, os.path.join(models, E.PICKLES["smpl"]),
                               os.path.join(models, E.PICKLES["ppca"]), os.path.join(root, "dense.npy")],
                              env=env, cwd=root)
        cls.dense = np.load(os.path.join(root, "dense.npy"))
        cls.out = os.path.join(root, "out")
        saved = E.LIMIT, E.SINGLE
        E.LIMIT, E.SINGLE = 4 * 1024 * 1024, 1024 * 1024    # small, so the weights split and turn float32
        try:
            E.main(["extract_meng.py", models, cls.out])
        finally:
            E.LIMIT, E.SINGLE = saved

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def path(self, *parts):
        return os.path.join(self.out, *parts)

    def test_no_foreign_library_was_imported(self):
        self.assertNotIn("chumpy", sys.modules)

    def test_a_chumpy_array_keeps_its_values_cut_to_the_modes(self):
        shapedirs = np.load(self.path("smpl", "shapedirs.npy"))
        self.assertEqual(shapedirs.shape, (50, 3, E.MODES))

    def test_the_pose_correctives_are_left_out(self):
        self.assertFalse(os.path.exists(self.path("smpl", "posedirs.npy")))

    def test_a_sparse_matrix_keeps_its_parts(self):
        data, indices, indptr, shape = (np.load(self.path("smpl", "J_regressor.%s.npy" % s))
                                        for s in ("data", "indices", "indptr", "shape"))
        rebuilt = np.zeros(tuple(shape))
        for j in range(shape[1]):
            rebuilt[indices[indptr[j]:indptr[j + 1]], j] = data[indptr[j]:indptr[j + 1]]
        np.testing.assert_array_equal(rebuilt, self.dense)

    def test_a_large_array_splits_and_turns_float32(self):
        parts = sorted(n for n in os.listdir(self.path("smpl")) if n.startswith("weights.part"))
        self.assertGreater(len(parts), 1)
        joined = np.concatenate([np.load(self.path("smpl", n)) for n in parts])
        self.assertEqual(joined.shape, (50000, 24))
        self.assertEqual(joined.dtype, np.float32)

    def test_the_loadings_are_cut_and_nested_keys_kept(self):
        self.assertEqual(np.load(self.path("ppca", "C.npy")).shape, (153, E.MODES))
        self.assertEqual(np.load(self.path("ppca", "M_pp.npy")).shape, (153,))
        self.assertAlmostEqual(float(np.load(self.path("ppca", "extra.sigma.npy"))), 0.25)

    def test_describe_names_every_key(self):
        with open(self.path("DESCRIBE.md")) as fh:
            text = fh.read()
        for key in ("v_template", "f", "shapedirs", "posedirs", "J_regressor", "bs_style", "weights",
                    "M_pp", "C", "extra.sigma"):
            self.assertIn("| %s |" % key, text)
        self.assertIn("left out: not needed", text)
        self.assertIn("chumpy.ch.Ch", text)


if __name__ == "__main__":
    unittest.main()
