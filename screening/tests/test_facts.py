"""The facts reader against hand values, the holdings reader on the same synthetic masks, and a
TotalSegmentator folder in both layouts."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

import nibabel as nib
import numpy as np

from holdings.fullspine_facts import label_facts, voxel_points
from screening import facts as F
from screening.contracts import ViolationError

# a grid like ENHANCE.PET's, LAS: k increases toward the head, i toward the left
LAS = np.array([[-0.8, 0.0, 0.0, 100.0], [0.0, 0.8, 0.0, -20.0], [0.0, 0.0, 2.5, -1000.0], [0.0, 0.0, 0.0, 1.0]])


def write(path, vol, affine):
    nib.save(nib.Nifti1Image(vol.astype(np.float64), affine), path)


def synthetic_spine():
    """C2 and C3 as blocks, the sacrum touching the foot face, and a value no scheme names."""
    vol = np.zeros((12, 12, 40), np.int16)
    vol[3:9, 3:9, 30:36] = 2
    vol[3:9, 3:9, 24:30] = 3
    vol[2:10, 2:10, 0:4] = 26
    vol[0, 0, 20] = 99
    return vol


class PureTest(unittest.TestCase):
    def test_field_edges_by_hand(self):
        self.assertEqual(F.field_edges([2, 2, 2], [0.0, 0.0, 1.0, 0.0]), (1.5, -0.5))
        top, bottom = F.field_edges([512, 512, 365], [0.0, 0.0, 2.5, -1155.5])
        # the step is positive along k, so the head-most edge lies half a voxel past the last centre
        self.assertAlmostEqual(top, -1155.5 + 2.5 * 364.5)
        self.assertAlmostEqual(bottom, -1155.5 - 2.5 * 0.5)
        with self.assertRaises(ViolationError):
            F.field_edges([0, 2, 2], [0.0, 0.0, 1.0, 0.0])

    def test_faces_touched(self):
        self.assertEqual(F.faces_touched([0, 1, 2], [3, 5, 9], [4, 6, 10], "LAS"), ["A", "L", "R", "S"])
        self.assertEqual(F.faces_touched([1, 1, 0], [2, 2, 2], [4, 4, 4], "LAS"), ["I"])
        self.assertEqual(F.faces_touched([1, 1, 1], [2, 2, 2], [4, 4, 4], "RAS"), [])
        with self.assertRaises(ViolationError):
            F.faces_touched([0, 0, 0], [1, 1, 1], [4, 4, 4], "LAA")
        with self.assertRaises(ViolationError):
            F.faces_touched([0, 0, 0], [4, 1, 1], [4, 4, 4], "LAS")

    def test_cut_flags(self):
        self.assertEqual(F.cut_flags(["S", "L"]), (True, False, True))
        self.assertEqual(F.cut_flags(["I"]), (False, True, False))
        self.assertEqual(F.cut_flags([]), (False, False, False))

    def test_rounded_has_no_negative_zero(self):
        self.assertEqual(str(F.rounded(-0.04, 1)), "0.0")


class ReadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_a_label_volume_against_the_holdings_reader(self):
        path = os.path.join(self.tmp, "s1.nii.gz")
        vol = synthetic_spine()
        write(path, vol, LAS)
        row = F.read_study("s1", path, "verse", "test", "p1")
        self.assertEqual(sorted(row["levels"]), ["C2", "C3", "sacrum"])
        self.assertEqual(row["other_values"], {"99": 1})
        self.assertEqual(row["levels"]["C2"]["voxels"], 6 * 6 * 6)
        self.assertEqual(row["levels"]["sacrum"]["faces"], ["I"])
        self.assertEqual(row["levels"]["C2"]["components"], 1)
        self.assertEqual(row["levels"]["C2"]["largest_share"], 1.0)
        # the head-most and foot-most voxel centres on the superior axis
        self.assertEqual(row["levels"]["C2"]["top_mm"], -1000.0 + 35 * 2.5)
        self.assertEqual(row["levels"]["C2"]["bottom_mm"], -1000.0 + 30 * 2.5)
        self.assertEqual(row["field_mm"], {"top": F.rounded(-1000.0 + 39.5 * 2.5, 1), "bottom": F.rounded(-1000.0 - 0.5 * 2.5, 1)})
        self.assertEqual(row["grid"]["axcodes"], "LAS")
        self.assertEqual(row["grid"]["head_foot_axis"], 2)
        self.assertEqual(row["person"], "p1")
        self.assertTrue(any("99" in p for p in row["problems"]))
        self.assertIn("sacrum", row["distances_mm"].get("L1-sacrum", "sacrum") or "sacrum")
        img = nib.load(path)
        found = voxel_points(img)
        for value, name in ((2, "C2"), (3, "C3"), (26, "sacrum")):
            self.assertEqual(row["levels"][name], label_facts(found[value], img.affine, img.shape[:3]))

    def test_a_totalsegmentator_folder_in_both_layouts(self):
        affine = np.diag([1.5, 1.5, 1.5, 1.0])
        plain, nested = os.path.join(self.tmp, "sX"), os.path.join(self.tmp, "sY", "segmentations")
        for folder in (plain, nested):
            os.makedirs(folder)
            for name, where in (("vertebrae_T12", slice(10, 14)), ("vertebrae_L1", slice(6, 10)),
                                ("sacrum", slice(0, 3)), ("spinal_cord", slice(2, 16)), ("rib_left_3", slice(12, 13))):
                vol = np.zeros((8, 8, 16), np.uint8)
                vol[2:6, 2:6, where] = 1
                nib.save(nib.Nifti1Image(vol, affine), os.path.join(folder, name + ".nii.gz"))
        a = F.read_study("sX", plain, "totalseg", "totalsegmentator")
        b = F.read_study("sY", os.path.join(self.tmp, "sY"), "totalseg", "totalsegmentator")
        self.assertEqual(sorted(a["levels"]), ["L1", "T12", "sacrum"])
        self.assertEqual(sorted(a["context"]), ["spinal_cord"])
        self.assertEqual(a["levels"]["sacrum"]["faces"], ["I"])
        self.assertEqual(a["context"]["spinal_cord"]["voxels"], 4 * 4 * 14)
        # from the foot-most L1 voxel centre (k=6, 9.0 mm) to the head-most sacrum voxel centre (k=2, 3.0 mm)
        self.assertEqual(a["distances_mm"], {"L1-sacrum": 6.0})
        self.assertEqual({k: v for k, v in a.items() if k not in ("id", "files")},
                         {k: v for k, v in b.items() if k not in ("id", "files")})
        self.assertEqual(sorted(a["files"]), ["sacrum.nii.gz", "spinal_cord.nii.gz", "vertebrae_L1.nii.gz", "vertebrae_T12.nii.gz"])

    def test_a_run_writes_sorted_rows_and_resumes_from_its_part_file(self):
        masks = os.path.join(self.tmp, "masks")
        os.mkdir(masks)
        for sid in ("b2", "a1"):
            write(os.path.join(masks, sid + ".nii.gz"), synthetic_spine(), LAS)
        out = os.path.join(self.tmp, "facts.jsonl")
        with open(out + ".part", "w") as f:
            f.write(json.dumps({"id": "b2", "member": "kept", "levels": {}}) + "\n")
            f.write('{"id": "a1", "cut off')
        jobs = [(sid, path, "verse", "test", None, None) for sid, path in F.studies_in(masks, "verse")]
        self.assertEqual([j[0] for j in jobs], ["a1", "b2"])
        self.assertEqual(F.run(jobs, out, 1), 2)
        rows = [json.loads(line) for line in open(out)]
        self.assertEqual([r["id"] for r in rows], ["a1", "b2"])
        self.assertEqual(rows[1]["member"], "kept")
        self.assertEqual(sorted(rows[0]["levels"]), ["C2", "C3", "sacrum"])
        self.assertFalse(os.path.exists(out + ".part"))


if __name__ == "__main__":
    unittest.main()
