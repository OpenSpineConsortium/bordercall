"""The int16 converter held to small volumes written here: a float64 mask converted to the voxel,
a fractional voxel refused with no output left, a uint8 mask kept behind a symlink, and a
TotalSegmentator folder stacked into VerSe's ids with its overlap counted."""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import struct
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import nibabel as nib
import numpy as np

from screening import ORDER, convert
from screening.contracts import ViolationError

AFFINE = np.array([[0.0, 0.0, 2.0, -10.0], [0.0, 1.5, 0.0, 20.0], [-1.0, 0.0, 0.0, 30.0], [0.0, 0.0, 0.0, 1.0]])


def _volume(values, dtype):
    """An 8 x 8 x 8 grid holding each value in a block of its own."""
    data = np.zeros((8, 8, 8), dtype)
    for i, value in enumerate(values):
        data[i * 2:i * 2 + 2, :, :] = value
    return data


def _write(path, data):
    nib.save(nib.Nifti1Image(data, AFFINE), path)
    return path


def _mask(points):
    data = np.zeros((8, 8, 8), np.uint8)
    for p in points:
        data[p] = 1
    return data


class PureDecisions(unittest.TestCase):
    def test_verse_value_is_the_schemes_table(self):
        self.assertEqual(convert.verse_value("C1"), 1)
        self.assertEqual(convert.verse_value("C7"), 7)
        self.assertEqual(convert.verse_value("T1"), 8)
        self.assertEqual(convert.verse_value("T12"), 19)
        self.assertEqual(convert.verse_value("L1"), 20)
        self.assertEqual(convert.verse_value("L5"), 24)
        self.assertEqual(convert.verse_value("L6"), 25)
        self.assertEqual(convert.verse_value("sacrum"), 26)
        self.assertEqual(convert.verse_value("T13"), 28)
        self.assertEqual(len(ORDER), 27)
        self.assertEqual(sorted(convert.verse_value(level) for level in ORDER), sorted(set(range(1, 27)) | {28}))

    def test_verse_value_refuses_a_name_outside_the_order(self):
        with self.assertRaises(ViolationError):
            convert.verse_value("S1")
        with self.assertRaises(ViolationError):
            convert.verse_value("vertebrae_L1")

    def test_kept_as_is(self):
        self.assertTrue(convert.kept_as_is("u", 1))
        self.assertTrue(convert.kept_as_is("i", 2))
        self.assertTrue(convert.kept_as_is("u", 2))
        self.assertFalse(convert.kept_as_is("i", 4))
        self.assertFalse(convert.kept_as_is("u", 8))
        self.assertFalse(convert.kept_as_is("f", 2))
        self.assertFalse(convert.kept_as_is("f", 8))
        with self.assertRaises(ViolationError):
            convert.kept_as_is("int16", 2)

    def test_lossless(self):
        self.assertTrue(convert.lossless(0, 0, 26))
        self.assertTrue(convert.lossless(0, -32768, 32767))
        self.assertFalse(convert.lossless(1, 0, 26))
        self.assertFalse(convert.lossless(0, -32769, 0))
        self.assertFalse(convert.lossless(0, 0, 32768))
        with self.assertRaises(ViolationError):
            convert.lossless(0, 5, 4)
        with self.assertRaises(ViolationError):
            convert.lossless(-1, 0, 1)

    def test_action_for(self):
        self.assertEqual(convert.action_for("u", 1, True), "stacked")
        self.assertEqual(convert.action_for("u", 1, False), "kept")
        self.assertEqual(convert.action_for("f", 8, False), "converted")
        self.assertEqual(convert.action_for("i", 4, False), "converted")


class Volumes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_float64_converts_to_int16_to_the_voxel(self):
        data = _volume([0, 7, 20, 26], np.float64)
        src = _write(os.path.join(self.dir, "s1.nii.gz"), data)
        out = os.path.join(self.dir, "out", "s1.nii.gz")
        os.makedirs(os.path.dirname(out))
        manifest = os.path.join(self.dir, "s1.json")
        record = convert.convert(src, "verse", out, manifest)
        back = nib.load(out)
        self.assertEqual(back.get_data_dtype(), np.int16)
        self.assertTrue(np.array_equal(np.asarray(back.dataobj), data.astype(np.int16)))
        self.assertTrue(np.array_equal(back.affine, AFFINE))
        # on disk the slope is 1 and the intercept 0, which nibabel reads back as no scaling at all
        with gzip.open(out) as f:
            self.assertEqual(struct.unpack("<ff", f.read(348)[112:120]), (1.0, 0.0))
        self.assertEqual(back.header.get_slope_inter(), (None, None))
        self.assertEqual(record["action"], "converted")
        self.assertEqual(record["out"]["values"], [7, 20, 26])
        self.assertEqual(record["out"]["dtype"], "int16")
        self.assertEqual(record["out"]["path"], out)
        self.assertEqual(record["out"]["bytes"], os.path.getsize(out))
        self.assertEqual(record["problems"], [])
        self.assertEqual(list(record["source"]["files"]), ["s1.nii.gz"])
        self.assertEqual(record["source"]["files"]["s1.nii.gz"]["bytes"], os.path.getsize(src))
        with open(manifest, encoding="ascii") as f:
            self.assertEqual(json.load(f), record)
        self.assertFalse(os.path.exists(out + ".tmp.nii.gz"))

    def test_a_wide_integer_converts_too(self):
        data = _volume([0, 7, 20, 26], np.int32)
        src = _write(os.path.join(self.dir, "s2.nii.gz"), data)
        out = os.path.join(self.dir, "s2-int16.nii.gz")
        record = convert.convert(src, "verse", out)
        self.assertEqual(record["action"], "converted")
        self.assertTrue(np.array_equal(np.asarray(nib.load(out).dataobj), data.astype(np.int16)))

    def test_a_fractional_voxel_is_refused_and_leaves_no_output(self):
        data = _volume([0, 7, 20, 26], np.float64)
        data[3, 3, 3] = 20.5
        src = _write(os.path.join(self.dir, "s3.nii.gz"), data)
        out = os.path.join(self.dir, "s3-int16.nii.gz")
        with self.assertRaises(ValueError) as held:
            convert.convert(src, "verse", out)
        self.assertIn("1 voxels are not whole numbers", str(held.exception))
        self.assertFalse(os.path.lexists(out))
        self.assertEqual([n for n in os.listdir(self.dir) if n != "s3.nii.gz"], [])

    def test_a_value_beyond_int16_is_refused(self):
        data = _volume([0, 7, 40000], np.float64)
        src = _write(os.path.join(self.dir, "s4.nii.gz"), data)
        out = os.path.join(self.dir, "s4-int16.nii.gz")
        with self.assertRaises(ValueError):
            convert.convert(src, "verse", out)
        self.assertFalse(os.path.lexists(out))

    def test_uint8_is_kept_behind_a_symlink(self):
        data = _volume([0, 7, 20, 26], np.uint8)
        src = _write(os.path.join(self.dir, "s5.nii.gz"), data)
        before = os.path.getmtime(src)
        out = os.path.join(self.dir, "kept", "s5.nii.gz")
        os.makedirs(os.path.dirname(out))
        record = convert.convert(src, "verse", out)
        self.assertEqual(record["action"], "kept")
        self.assertTrue(os.path.islink(out))
        self.assertEqual(os.readlink(out), os.path.abspath(src))
        self.assertEqual(os.path.getmtime(src), before)
        self.assertEqual(record["out"]["path"], src)
        self.assertEqual(record["out"]["symlink"], out)
        self.assertEqual(record["out"]["dtype"], "uint8")
        self.assertEqual(record["out"]["values"], [7, 20, 26])
        self.assertIn("none", record["out"]["copy"])
        self.assertTrue(np.array_equal(np.asarray(nib.load(out).dataobj), data))

    def test_uint8_kept_in_place_makes_no_link(self):
        src = _write(os.path.join(self.dir, "s6.nii.gz"), _volume([0, 7], np.uint8))
        record = convert.convert(src, "verse", src)
        self.assertEqual(record["action"], "kept")
        self.assertNotIn("symlink", record["out"])
        self.assertFalse(os.path.islink(src))

    def test_a_totalseg_volume_and_a_verse_folder_are_refused(self):
        src = _write(os.path.join(self.dir, "s7.nii.gz"), _volume([0, 7], np.uint8))
        with self.assertRaises(ValueError):
            convert.convert(src, "totalseg", os.path.join(self.dir, "x.nii.gz"))
        with self.assertRaises(ValueError):
            convert.convert(self.dir, "verse", os.path.join(self.dir, "x.nii.gz"))
        self.assertFalse(os.path.lexists(os.path.join(self.dir, "x.nii.gz")))


class Folders(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _subject(self, folder):
        os.makedirs(folder, exist_ok=True)
        t12 = [(2, 2, 2), (2, 2, 3), (3, 3, 3)]
        l1 = [(3, 3, 3), (4, 4, 4), (4, 4, 5)]
        s1 = [(6, 6, 6), (6, 6, 7)]
        skull = [(0, 0, 0), (0, 0, 1)]
        for stem, points in (("vertebrae_T12", t12), ("vertebrae_L1", l1), ("vertebrae_S1", s1), ("skull", skull)):
            _write(os.path.join(folder, stem + ".nii.gz"), _mask(points))
        return t12, l1, s1

    def _check(self, record, out, t12, l1, s1):
        back = nib.load(out)
        data = np.asarray(back.dataobj)
        self.assertEqual(back.get_data_dtype(), np.int16)
        self.assertTrue(np.array_equal(back.affine, AFFINE))
        self.assertEqual(record["action"], "stacked")
        self.assertEqual(record["overlap_voxels"], 1)
        self.assertEqual(record["levels"], {"T12": 19, "L1": 20, "sacrum": 26})
        self.assertEqual(record["out"]["values"], [19, 20, 26])
        self.assertEqual(sorted(record["source"]["files"]),
                         ["vertebrae_L1.nii.gz", "vertebrae_S1.nii.gz", "vertebrae_T12.nii.gz"])
        for p in t12:
            self.assertEqual(data[p], 19)  # the shared voxel (3, 3, 3) goes to T12, the first in order
        for p in l1[1:]:
            self.assertEqual(data[p], 20)
        for p in s1:
            self.assertEqual(data[p], 26)
        self.assertEqual(data[0, 0, 0], 0)  # the skull is left out
        self.assertEqual(int(np.count_nonzero(data)), 7)

    def test_a_subject_folder_stacks_into_verse_ids(self):
        folder = os.path.join(self.dir, "s0001")
        t12, l1, s1 = self._subject(folder)
        out = os.path.join(self.dir, "s0001.nii.gz")
        manifest = os.path.join(self.dir, "s0001.json")
        record = convert.convert(folder, "totalseg", out, manifest)
        self._check(record, out, t12, l1, s1)
        with open(manifest, encoding="ascii") as f:
            self.assertEqual(json.load(f), record)

    def test_a_segmentations_subfolder_is_read_the_same(self):
        folder = os.path.join(self.dir, "s0002")
        t12, l1, s1 = self._subject(os.path.join(folder, "segmentations"))
        _write(os.path.join(folder, "ct.nii.gz"), np.zeros((8, 8, 8), np.int16))
        out = os.path.join(self.dir, "s0002.nii.gz")
        self._check(convert.convert(folder, "totalseg", out), out, t12, l1, s1)

    def test_a_mask_on_another_grid_is_refused(self):
        folder = os.path.join(self.dir, "s0003")
        self._subject(folder)
        nib.save(nib.Nifti1Image(_mask([(1, 1, 1)]), np.eye(4)), os.path.join(folder, "vertebrae_L2.nii.gz"))
        out = os.path.join(self.dir, "s0003.nii.gz")
        with self.assertRaises(ValueError):
            convert.convert(folder, "totalseg", out)
        self.assertFalse(os.path.lexists(out))

    def test_an_empty_folder_is_refused(self):
        folder = os.path.join(self.dir, "s0004")
        os.makedirs(folder)
        with self.assertRaises(ValueError):
            convert.convert(folder, "totalseg", os.path.join(self.dir, "s0004.nii.gz"))


class Command(unittest.TestCase):
    def test_the_subcommand_runs_and_prints_the_action(self):
        parser = argparse.ArgumentParser()
        convert.command(parser.add_subparsers(dest="command"))
        with tempfile.TemporaryDirectory() as d:
            src = _write(os.path.join(d, "a.nii.gz"), _volume([0, 7], np.float64))
            out = os.path.join(d, "a-int16.nii.gz")
            args = parser.parse_args(["int16", "--labels", src, "--out", out])
            self.assertEqual(args.scheme, "verse")
            self.assertIsNone(args.manifest)
            self.assertIs(args.run, convert.run)  # __main__.py dispatches through args.run
            printed = io.StringIO()
            with redirect_stdout(printed):
                self.assertEqual(convert.run(args), 0)
            self.assertEqual(printed.getvalue(), "converted %s\n" % out)
            bad = _write(os.path.join(d, "b.nii.gz"), _volume([0, 7.5], np.float64))
            args = parser.parse_args(["int16", "--labels", bad, "--out", os.path.join(d, "b-int16.nii.gz")])
            held = io.StringIO()
            with redirect_stderr(held):
                self.assertEqual(convert.run(args), 1)
            self.assertTrue(held.getvalue().startswith("failed "))


if __name__ == "__main__":
    unittest.main()
