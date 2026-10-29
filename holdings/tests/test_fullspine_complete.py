"""The completion of a column by a segmenter's levels, on stacked boxes written to a temporary folder.

Each column is a stack of boxes, one slot per body, head at the top; the release's and the segmenter's
masks share the slots, so a test says which slots each arm draws and what it calls them. Run from the
repository's root with `python -m unittest discover -s holdings/tests -t .`."""
import gzip
import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import nibabel as nib
import numpy as np

from holdings import fullspine_complete as C
from holdings import fullspine_facts as F

SIDE, BODY, SLICES, MARGIN = 12, 8, 5, 3   # a box is 8 x 8 x 5 = 320 voxels, over the 200 floor
AFFINE = np.diag([1.0, 1.0, 2.0, 1.0])     # RAS, the third axis rising to the head
ID = C.VERSE_IDS
FULL = ["C2", "C3", "C4", "C5", "C6", "C7", *[f"T{i}" for i in range(1, 13)], *[f"L{i}" for i in range(1, 6)]]


def stack(slots):
    """A mask with one box per slot, the first slot at the head; a slot is a VerSe id or 0 for none."""
    height = 2 * MARGIN + SLICES * len(slots)
    mask = np.zeros((SIDE, SIDE, height), np.uint8)
    low = (SIDE - BODY) // 2
    top = height - MARGIN
    for label in slots:
        if label:
            mask[low:low + BODY, low:low + BODY, top - SLICES:top] = label
        top -= SLICES
    return mask


def ids(names):
    return [ID[name] if name else 0 for name in names]


def save(path, mask):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(gzip.compress(nib.Nifti1Image(mask, AFFINE).to_bytes(), mtime=0))
    return path


class Study:
    """A VerSe study in a temporary folder: the release's and the segmenter's masks."""

    def __init__(self, folder, release, machine, sid="verse001"):
        self.release = save(os.path.join(folder, sid, "release.nii.gz"), stack(ids(release)))
        self.machine = save(os.path.join(folder, sid, "machine.nii.gz"), stack(ids(machine)))

    def complete(self, asked=None):
        return C.complete_study("verse", self.release, self.machine, asked)


def outcome(record, name):
    return next(o for o in record["targets"] if o["name"] == name)


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def study(self, release, machine, asked=None):
        return Study(self.tmp.name, release, machine).complete(asked)

    def test_the_sacrum_below_a_matched_column_is_added_and_the_release_is_left_alone(self):
        record, levels, completed, arm, img = self.study(FULL + [None], FULL + ["sacrum"])
        self.assertEqual(record["added"], ["sacrum"])
        self.assertEqual(len(record["anchors"]), len(FULL))
        self.assertEqual(list(arm), ["sacrum"])
        self.assertEqual(len(arm["sacrum"]), BODY * BODY * SLICES)
        released = np.concatenate([F.voxel_points(img)[label] for label in F.voxel_points(img)])
        self.assertEqual(len(np.intersect1d(arm["sacrum"], C.flat(released, img.shape))), 0)

    def test_a_gap_between_anchors_is_named_by_the_count_whatever_the_segmenter_calls_it(self):
        release = [n if n not in ("T6", "T7", "T8", "T9") else None for n in FULL] + [None]
        shifted = {name: FULL[i + 1] for i, name in enumerate(FULL[:-1])}
        machine = [shifted.get(n, "L6") for n in FULL] + ["sacrum"]
        record, *_ = self.study(release, machine)
        for name in ("T6", "T7", "T8", "T9"):
            self.assertEqual(outcome(record, name)["state"], C.ADDED, name)
            self.assertEqual(outcome(record, name)["naming"], "between T5 and T10")
        self.assertEqual(outcome(record, "T6")["machine_name"], "T7")

    def test_a_gap_whose_count_differs_is_refused(self):
        release = [n if n not in ("T6", "T7") else None for n in FULL] + [None]
        machine = ["T6" if n == "T7" else n for n in FULL] + ["sacrum"]   # two bodies drawn as one
        record, *_ = self.study(release, machine)
        for name in ("T6", "T7"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED)
            self.assertIn("has 1 levels between T5 and T8", outcome(record, name)["reason"])

    def test_a_release_level_the_segmenter_misses_in_a_gap_blocks_the_gap(self):
        release = [n if n not in ("T6", "T8") else None for n in FULL] + [None]
        machine = [n if n != "T7" else None for n in FULL] + ["sacrum"]
        record, *_ = self.study(release, machine)
        for name in ("T6", "T8"):
            self.assertIn("draws T7 between T5 and T9", outcome(record, name)["reason"])

    def test_the_head_end_takes_levels_only_where_the_segmenter_names_them_alike(self):
        release = [None] * 6 + FULL[6:] + [None]
        record, *_ = self.study(release, FULL + ["sacrum"])
        self.assertEqual(record["refused"], [])
        self.assertEqual(outcome(record, "C2")["naming"], "above T1, named alike by the count and the segmenter")

    def test_the_head_walk_stops_at_the_first_name_that_differs(self):
        release = [None] * 6 + FULL[6:] + [None]
        machine = ["C1", "C2", "C3", "C4", "C6", "C7"] + FULL[6:] + ["sacrum"]
        record, *_ = self.study(release, machine)
        self.assertEqual(outcome(record, "C7")["state"], C.ADDED)
        self.assertEqual(outcome(record, "C6")["state"], C.ADDED)
        self.assertIn("calls the level C4", outcome(record, "C5")["reason"])
        for name in ("C4", "C3", "C2"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED, name)

    def test_the_sacrum_is_refused_past_a_level_no_name_accounts_for(self):
        release = FULL[:-1] + [None, None]
        machine = FULL[:-1] + ["L6", "sacrum"]
        record, *_ = self.study(release, machine)
        self.assertIn("calls the level L6", outcome(record, "L5")["reason"])
        self.assertIn("1 level(s) between the release's L4 and the sacrum", outcome(record, "sacrum")["reason"])

    def test_a_body_the_field_test_does_not_ask_for_is_never_named_and_blocks_the_sacrum(self):
        release = FULL[:-1] + [None, None]                  # no_l5: the release stops at L4
        record, *_ = self.study(release, FULL + ["sacrum"], asked=["sacrum"])
        self.assertEqual([o["name"] for o in record["targets"]], ["sacrum"])
        self.assertIn("1 level(s) between the release's L4 and the sacrum", outcome(record, "sacrum")["reason"])

    def test_a_name_asked_for_that_the_release_draws_is_no_target(self):
        record, *_ = self.study(FULL + [None], FULL + ["sacrum"], asked=["L5", "sacrum"])
        self.assertEqual(record["added"], ["sacrum"])
        self.assertEqual(record["asked"], ["L5", "sacrum"])
        with self.assertRaises(ValueError):
            C.targets_of(set(), ["S1"])

    def test_the_sacrum_is_refused_where_the_release_s_last_level_is_unmatched(self):
        release = FULL + [None]
        machine = FULL[:-1] + [None, "sacrum"]
        record, *_ = self.study(release, machine)
        self.assertIn("foot-most level L5 is not matched", outcome(record, "sacrum")["reason"])

    def test_a_level_lying_under_the_release_is_refused(self):
        release = FULL + [None]
        machine = FULL[:-1] + ["sacrum", None]   # the segmenter's sacrum where the release has L5
        record, *_ = self.study(release, machine)
        self.assertEqual(outcome(record, "sacrum")["state"], C.REFUSED)

    def test_anchors_out_of_order_refuse_everything(self):
        self.assertFalse(C.in_order({"T1": 9, "T2": 8}, [8, 9]))
        self.assertTrue(C.in_order({"T1": 8, "T2": 9}, [8, 7, 9]))

    def test_the_voxel_floor_applies_to_what_a_level_adds(self):
        level = np.arange(300)
        checked = C.voxel_check({"name": "T6", "state": C.ADDED}, level, np.arange(150), np.arange(0), None)
        self.assertEqual(checked["state"], C.REFUSED)
        self.assertIn("adds 150 voxels", checked["reason"])


class Arm(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_the_arm_is_written_byte_for_byte_the_same_and_holds_verse_ids(self):
        study = Study(self.tmp.name, FULL + [None], FULL + ["sacrum"])
        _, _, _, arm, img = study.complete()
        first, second = C.arm_bytes(arm, img), C.arm_bytes(arm, img)
        self.assertEqual(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())
        written = F.image_of(first)
        self.assertTrue(F.same_grid(written, img))
        self.assertEqual(sorted(np.unique(np.asanyarray(written.dataobj))), [0, ID["sacrum"]])

    def test_a_totalsegmentator_folder_is_read_level_by_level(self):
        folder = os.path.join(self.tmp.name, "s0001")
        release = [n if n not in ("T6",) else None for n in FULL] + ["sacrum"]
        for name in set(release) - {None}:
            mask = (stack(ids(release)) == ID[name]).astype(np.uint8)
            base = "sacrum.nii.gz" if name == "sacrum" else "vertebrae_%s.nii.gz" % name
            save(os.path.join(folder, base), mask)
        machine = save(os.path.join(self.tmp.name, "s0001.nii.gz"), stack(ids(FULL + ["sacrum"])))
        record, *_ = C.complete_study("totalsegmentator", folder, machine)
        self.assertEqual(record["added"], ["T6"])
        self.assertEqual(len(record["files"]["release"]), len(FULL))


class CommandLine(unittest.TestCase):
    def test_records_masks_and_completed_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Study(tmp, FULL + [None], FULL + ["sacrum"])
            whole = Study(tmp, FULL + [None], FULL + [None], sid="verse002")
            rows = {}
            for sid, s in (("verse001", study), ("verse002", whole)):
                img = F.image_of(open(s.release, "rb").read())
                found = F.voxel_points(img)
                levels = {F.VERSE_NAMES[label]: points for label, points in found.items()}
                rows[sid] = F.study_row("verse", sid, {"release.nii.gz": open(s.release, "rb").read()},
                                        img, levels, {}, {})
            facts = os.path.join(tmp, "facts.jsonl")
            with open(facts, "w", encoding="ascii") as f:
                f.writelines(F.row_line(row) for row in rows.values())
            how = os.path.join(tmp, "input.json")
            json.dump({"input": "as_is"}, open(how, "w"))
            spec = {"segmenter": {"name": "SPINEPS"}, "facts": {"verse": facts},
                    "studies": [{"id": "verse001", "member": "verse", "release": study.release,
                                 "machine": study.machine, "input": how},
                                {"id": "verse002", "member": "verse", "release": whole.release,
                                 "machine": whole.machine}]}
            jobs = os.path.join(tmp, "jobs.json")
            json.dump(spec, open(jobs, "w"))
            out = os.path.join(tmp, "out")
            with redirect_stdout(io.StringIO()):
                C.main([jobs, out])
            records = [json.loads(line) for line in open(os.path.join(out, "records.jsonl"))]
            self.assertEqual([r["id"] for r in records], ["verse001", "verse002"])
            self.assertEqual(records[0]["input"], {"input": "as_is"})
            self.assertEqual(records[1]["refused"], ["sacrum"])
            completed = [json.loads(line) for line in open(os.path.join(out, "facts.jsonl"))]
            self.assertEqual(len(completed), 1)
            row = completed[0]
            self.assertIn("sacrum", row["levels"])
            self.assertEqual(list(row["machine_levels"]), ["sacrum"])
            self.assertIn("L5-sacrum", row["distances_mm"])
            name = "verse001_machine.nii.gz"
            data = open(os.path.join(out, "masks", name), "rb").read()
            self.assertEqual(row["machine_files"][name]["sha256"], hashlib.sha256(data).hexdigest())
            self.assertFalse(os.path.exists(os.path.join(out, "masks", "verse002_machine.nii.gz")))


if __name__ == "__main__":
    unittest.main()
