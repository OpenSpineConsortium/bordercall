"""The completion of a column by a segmenter's levels, on stacked boxes written to a temporary folder.

Each column is a stack of slots, one per body, head at the top: a slot is a body of BODY_SLICES slices
over one slice of disc. The release's and the segmenter's masks share the slots, so a test says which
slots each arm draws and what it calls them; the segmenter's subregion mask calls each of its vertebrae's
voxels body and puts a disc under each slot that has a level below it, unless a test says where the
discs lie. Run from the repository's root with `python -m unittest discover -s holdings/tests -t .`."""
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

SIDE, BODY, BODY_SLICES, MARGIN = 16, 12, 4, 3   # a body is 12 x 12 x 4 = 576 voxels, over the 200 floor
SLOT = BODY_SLICES + 1                            # and a slice of disc under it
LOW = (SIDE - BODY) // 2
AFFINE = np.diag([1.0, 1.0, 2.0, 1.0])            # RAS, the third axis rising to the head
ID = C.VERSE_IDS
FULL = ["C2", "C3", "C4", "C5", "C6", "C7", *[f"T{i}" for i in range(1, 13)], *[f"L{i}" for i in range(1, 6)]]
ARCH = 41                                         # a subregion that is neither body nor disc


def slot_top(height, i):
    """The slice above the head-most slice of slot i's body."""
    return height - MARGIN - SLOT * i


def blank(slots):
    return np.zeros((SIDE, SIDE, 2 * MARGIN + SLOT * len(slots)), np.uint8)


def stack(slots):
    """A mask with one body per slot, the first slot at the head; a slot is a VerSe id or 0 for none."""
    mask = blank(slots)
    for i, label in enumerate(slots):
        if label:
            top = slot_top(mask.shape[2], i)
            mask[LOW:LOW + BODY, LOW:LOW + BODY, top - BODY_SLICES:top] = label
    return mask


def disc_slice(mask, i):
    """The slice of disc under slot i's body."""
    return slot_top(mask.shape[2], i) - BODY_SLICES - 1


def subregion_mask(machine, slots, discs=None, arch=None):
    """The segmenter's subregion mask: its vertebrae's voxels as body, its sacrum's as sacrum, ARCH where
    arch is set, and a disc under each slot discs names (by default, every slot with a level below it)."""
    spine = np.where((machine > 0) & (machine != ID["sacrum"]), C.CORPUS, 0).astype(np.uint8)
    spine[machine == ID["sacrum"]] = ID["sacrum"]
    if arch is not None:
        spine[arch] = ARCH
    if discs is None:
        discs = [bool(slots[i]) and slots[i] != ID["sacrum"] and i + 1 < len(slots) and bool(slots[i + 1])
                 for i in range(len(slots))]
    for i, here in enumerate(discs):
        if here:
            spine[LOW:LOW + BODY, LOW:LOW + BODY, disc_slice(spine, i)] = C.DISC
    return spine


def ids(names):
    return [ID[name] if name else 0 for name in names]


def read(path, mode="rb"):
    with open(path, mode) as f:
        return f.read()


def write_json(value, path):
    with open(path, "w", encoding="ascii") as f:
        json.dump(value, f)


def save(path, mask):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(gzip.compress(nib.Nifti1Image(mask, AFFINE).to_bytes(), mtime=0))
    return path


def merge(mask, slots, label, first, second):
    """Slots first and second drawn as one level label, joined across the disc between them by a bar
    outside the body, as a segmenter's arch joins two vertebrae it merges; returns the bar."""
    height = mask.shape[2]
    for i in (first, second):
        top = slot_top(height, i)
        mask[LOW:LOW + BODY, LOW:LOW + BODY, top - BODY_SLICES:top] = label
        slots[i] = label
    bar = np.zeros(mask.shape, bool)
    bar[SIDE - LOW:, LOW:LOW + 2, slot_top(height, second) - BODY_SLICES:slot_top(height, first)] = True
    mask[bar] = label
    return bar


class Study:
    """A VerSe study in a temporary folder: the release's mask and the segmenter's two."""

    def __init__(self, folder, release, machine, sid="verse001", discs=None):
        release_mask = release if isinstance(release, np.ndarray) else stack(ids(release))
        if isinstance(machine, tuple):
            machine_mask, slots, arch = machine
        else:
            slots, arch = ids(machine), None
            machine_mask = stack(slots)
        self.release = save(os.path.join(folder, sid, "release.nii.gz"), release_mask)
        self.machine = save(os.path.join(folder, sid, "vert.nii.gz"), machine_mask)
        self.spine = save(os.path.join(folder, sid, "spine.nii.gz"),
                          subregion_mask(machine_mask, slots, discs, arch))

    def complete(self, asked=None):
        return C.complete_study("verse", self.release, self.machine, self.spine, asked)


def outcome(record, name):
    return next(o for o in record["targets"] if o["name"] == name)


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def study(self, release, machine, asked=None, discs=None):
        return Study(self.tmp.name, release, machine, discs=discs).complete(asked)

    def test_the_sacrum_below_a_matched_column_is_added_and_the_release_is_left_alone(self):
        record, levels, completed, arm, img = self.study(FULL + [None], FULL + ["sacrum"])
        self.assertEqual(record["added"], ["sacrum"])
        self.assertEqual(len(record["anchors"]), len(FULL))
        self.assertEqual(record["anchors"][0]["inside_machine"], 1.0)
        self.assertEqual(list(arm), ["sacrum"])
        self.assertEqual(len(arm["sacrum"]), BODY * BODY * BODY_SLICES)
        self.assertEqual(outcome(record, "sacrum")["body"]["discs_between"], 1)
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
        self.assertEqual(outcome(record, "T9")["body"]["discs_beyond"], 1)

    def test_a_gap_whose_count_differs_is_refused(self):
        release = [n if n not in ("T6", "T7") else None for n in FULL] + [None]
        machine = ["T6" if n == "T7" else n for n in FULL] + ["sacrum"]   # two bodies drawn as one
        record, *_ = self.study(release, machine)
        for name in ("T6", "T7"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED)
            self.assertIn("has 1 levels between T5 and T8", outcome(record, name)["reason"])

    def test_a_gap_with_more_segmenter_levels_than_names_is_refused(self):
        mask = stack(ids(FULL + ["sacrum"]))
        top = slot_top(mask.shape[2], FULL.index("T6"))
        mask[:, :, top - 2:top] = np.where(mask[:, :, top - 2:top] > 0, ID["T13"], 0)   # T6 split in two
        slots = ids(FULL + ["sacrum"])
        release = [n if n != "T6" else None for n in FULL] + [None]
        record, *_ = self.study(release, (mask, slots, None))
        self.assertIn("has 2 levels between T5 and T7", outcome(record, "T6")["reason"])

    def test_a_release_level_the_segmenter_misses_in_a_gap_blocks_the_gap(self):
        release = [n if n not in ("T6", "T8") else None for n in FULL] + [None]
        machine = [n if n != "T7" else None for n in FULL] + ["sacrum"]
        record, *_ = self.study(release, machine)
        for name in ("T6", "T8"):
            self.assertIn("draws T7 between T5 and T9", outcome(record, name)["reason"])

    def test_one_level_of_a_gap_failing_its_checks_refuses_the_gap(self):
        release = stack(ids([n if n not in ("T6", "T7") else None for n in FULL] + [None]))
        top = slot_top(release.shape[2], FULL.index("T7"))
        release[LOW:LOW + BODY, LOW:LOW + 7, top - BODY_SLICES] = ID["T8"]   # the release's T8 reaches into T7
        record, *_ = self.study(release, FULL + ["sacrum"])
        for name in ("T6", "T7"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED, name)
            self.assertIn("count names T7 between T5 and T8", outcome(record, name)["reason"])
            self.assertIn("so no level of the gap is taken", outcome(record, name)["reason"])

    def test_the_head_end_takes_levels_only_where_the_segmenter_names_them_alike(self):
        release = [None] * 6 + FULL[6:] + [None]
        record, *_ = self.study(release, FULL + ["sacrum"])
        self.assertEqual(record["refused"], [])
        self.assertEqual(outcome(record, "C2")["naming"], "above T1, named alike by the count and the segmenter")
        self.assertEqual(outcome(record, "C2")["body"]["step_ratio"], 1.0)

    def test_the_head_walk_stops_at_the_first_name_that_differs(self):
        release = [None] * 6 + FULL[6:] + [None]
        machine = ["C2", "C3", "C4", "C1", "C6", "C7"] + FULL[6:] + ["sacrum"]   # C5 called C1, the rest alike
        record, *_ = self.study(release, machine)
        self.assertEqual(outcome(record, "C7")["state"], C.ADDED)
        self.assertEqual(outcome(record, "C6")["state"], C.ADDED)
        for name in ("C5", "C4", "C3", "C2"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED, name)
            self.assertIn("gives C5 where the segmenter calls the level C1", outcome(record, name)["reason"])

    def test_an_unmatched_release_level_beyond_the_end_anchor_stops_the_walk(self):
        release = [None, "C3", None, None, None, None] + FULL[6:] + [None]
        machine = ["C2", None, "C4", "C5", "C6", "C7"] + FULL[6:] + ["sacrum"]
        record, *_ = self.study(release, machine, asked=["C2", "C4", "C5", "C6", "C7"])
        self.assertEqual(outcome(record, "C4")["state"], C.ADDED)
        self.assertIn("the release draws C3 above T1", outcome(record, "C2")["reason"])

    def test_the_walk_counts_through_names_not_asked_for(self):
        release = [None] * 2 + FULL[2:] + [None]                       # the release starts at C4
        machine = ["C1", "C2"] + FULL[2:] + ["sacrum"]                 # the segmenter one off above C4
        record, *_ = self.study(release, machine, asked=["C2"])
        self.assertEqual(outcome(record, "C2")["state"], C.REFUSED)
        self.assertIn("gives C3 where the segmenter calls the level C2", outcome(record, "C2")["reason"])

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
        self.assertIn("below the release's L4 L5, which the field test does not ask for",
                      outcome(record, "sacrum")["reason"])

    def test_the_sacrum_below_levels_the_foot_walk_named_is_added(self):
        release = [n if n not in ("L4", "L5") else None for n in FULL] + [None]   # the release stops at L3
        record, *_ = self.study(release, FULL + ["sacrum"])
        self.assertEqual(record["added"], ["L4", "L5", "sacrum"])
        self.assertEqual(outcome(record, "sacrum")["naming"], "the segmenter's sacrum, below L5")

    def test_a_sacrum_that_takes_in_the_body_below_the_release_s_l4_is_refused(self):
        release = FULL[:-1] + [None, None]
        mask, slots = stack(ids(FULL[:-1] + [None, None])), ids(FULL[:-1] + [None, None])
        bar = merge(mask, slots, ID["sacrum"], len(FULL) - 1, len(FULL))
        record, *_ = self.study(release, (mask, slots, bar), asked=["sacrum"])
        self.assertIn("directly under L4", outcome(record, "sacrum")["reason"])

    def test_a_sacrum_holding_a_second_disc_is_refused(self):
        mask, slots = stack(ids(FULL + [None, None])), ids(FULL + [None, None])
        bar = merge(mask, slots, ID["sacrum"], len(FULL), len(FULL) + 1)
        discs = [True] * (len(FULL) + 1) + [False]
        record, *_ = self.study(FULL + [None, None], (mask, slots, bar), discs=discs)
        self.assertIn("2 discs lie between the body above it and its foot", outcome(record, "sacrum")["reason"])

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

    def test_anchors_out_of_order_refuse_everything(self):
        self.assertFalse(C.in_order({"T1": 9, "T2": 8}, [8, 9]))
        self.assertTrue(C.in_order({"T1": 8, "T2": 9}, [8, 7, 9]))
        swap = {"T5": "T6", "T6": "T5"}
        release = [None] + [swap.get(n, n) for n in FULL[1:]] + [None]   # C2 undrawn, T5 and T6 swapped
        record, *_ = self.study(release, FULL + ["sacrum"])
        self.assertEqual(record["added"], [])
        self.assertEqual(record["refused"], ["C2", "sacrum"])
        for o in record["targets"]:
            self.assertIn("another order", o["reason"])

    def test_an_anchor_needs_each_level_mostly_inside_the_other(self):
        self.assertEqual(C.anchors({"L5": 100}, {24: 100}, {("L5", 24): 80}), {"L5": 24})
        self.assertEqual(C.anchors({"L5": 100}, {24: 100}, {("L5", 24): 79}), {})
        self.assertEqual(C.anchors({"L5": 100}, {24: 200}, {("L5", 24): 100}), {})   # a merge: Dice 0.67
        self.assertEqual(C.anchors({"L5": 200}, {24: 100}, {("L5", 24): 100}), {})   # a split
        self.assertEqual(C.anchors({"L5": 100}, {24: 100}, {}), {})

    def test_a_merged_end_anchor_stops_the_foot_walk(self):
        release = [n if n not in ("L4", "L5") else None for n in FULL] + [None]   # the release stops at L3
        mask, slots = stack(ids(FULL + ["sacrum"])), ids(FULL + ["sacrum"])
        bar = merge(mask, slots, ID["L3"], FULL.index("L3"), FULL.index("L4"))
        top = slot_top(mask.shape[2], FULL.index("L5"))
        mask[LOW:LOW + BODY, LOW:LOW + BODY, top - BODY_SLICES:top] = ID["L4"]   # the real L5 called L4
        slots[FULL.index("L5")] = ID["L4"]
        record, *_ = self.study(release, (mask, slots, bar))
        self.assertNotIn("L3", [a["release"] for a in record["anchors"]])
        self.assertEqual(record["added"], [])
        self.assertIn("the release draws L3 below L2", outcome(record, "L4")["reason"])

    def test_a_merged_head_anchor_stops_the_head_walk(self):
        release = [None] * 6 + FULL[6:] + [None]                         # the release starts at T1
        names = ["C3", "C4", "C5", "C6", "C7", None] + FULL[6:] + ["sacrum"]   # each cervical one off
        mask, slots = stack(ids(names)), ids(names)
        bar = merge(mask, slots, ID["T1"], FULL.index("C7"), FULL.index("T1"))
        record, *_ = self.study(release, (mask, slots, bar))
        self.assertNotIn("T1", [a["release"] for a in record["anchors"]])
        self.assertEqual(record["added"], ["sacrum"])
        for name in ("C7", "C6", "C5", "C4", "C3", "C2"):
            self.assertIn("the release draws T1 above T2", outcome(record, name)["reason"])

    def test_a_split_body_beyond_the_anchor_stops_the_walk(self):
        release = [None] * 6 + FULL[6:] + [None]
        names = ["C2", "C3", "C4", "C5", "C6", "C7"]
        mask, slots = stack(ids(names + FULL[6:] + ["sacrum"])), ids(names + FULL[6:] + ["sacrum"])
        height = mask.shape[2]
        relabel = {"C2": None, "C3": "C2", "C4": "C3"}                  # the C5 body cut in two below them
        for name, new in relabel.items():
            top = slot_top(height, FULL.index(name))
            mask[LOW:LOW + BODY, LOW:LOW + BODY, top - BODY_SLICES:top] = ID[new] if new else 0
        top = slot_top(height, FULL.index("C5"))
        mask[LOW:LOW + BODY, LOW:LOW + BODY, top - 2:top] = ID["C4"]
        record, *_ = self.study(release, (mask, slots, None))
        self.assertEqual(outcome(record, "C6")["state"], C.ADDED)
        self.assertEqual(outcome(record, "C5")["state"], C.REFUSED)
        self.assertIn("times its inner neighbour's height", outcome(record, "C5")["reason"])
        for name in ("C4", "C3", "C2"):
            self.assertEqual(outcome(record, name)["state"], C.REFUSED, name)

    def test_a_body_the_segmenter_missed_beyond_the_anchor_stops_the_walk(self):
        release = [None] * 6 + FULL[6:] + [None]
        machine = ["C3", None, "C4", "C5", "C6", "C7"] + FULL[6:] + ["sacrum"]   # no level on C3's body
        discs = [True] * (len(FULL)) + [False]
        record, *_ = self.study(release, machine, discs=discs)
        self.assertEqual(outcome(record, "C4")["state"], C.ADDED)
        self.assertEqual(outcome(record, "C3")["state"], C.REFUSED)
        self.assertIn("step from its neighbour", outcome(record, "C3")["reason"])
        self.assertEqual(outcome(record, "C2")["state"], C.REFUSED)

    def test_a_level_the_voxel_check_refuses_stops_the_walk_and_blocks_the_sacrum(self):
        release = stack(ids(FULL[:-1] + [None, None]))                  # the release stops at L4
        top = slot_top(release.shape[2], FULL.index("L5"))
        release[LOW:LOW + BODY, LOW:LOW + 6, top - 1] = ID["L4"]         # 72 voxels of L5 under its L4
        record, *_ = self.study(release, FULL + ["sacrum"], asked=["L5", "sacrum"])
        self.assertIn("over 10%", outcome(record, "L5")["reason"])
        self.assertEqual(outcome(record, "L5")["release_share"], 0.125)
        self.assertEqual(outcome(record, "L5")["added_voxels"], 504)
        self.assertEqual(outcome(record, "sacrum")["state"], C.REFUSED)
        self.assertIn("1 level(s) between the release's L4 and the sacrum", outcome(record, "sacrum")["reason"])

    def test_the_voxel_floor_and_share_apply_to_what_a_level_adds(self):
        numbers, reason = C.voxel_check(np.arange(300), np.arange(150), np.arange(0), None)
        self.assertIn("adds 150 voxels", reason)
        numbers, reason = C.voxel_check(np.arange(400), np.arange(50), np.arange(50), None)
        self.assertIn("lies under the release's other levels", reason)
        self.assertEqual(numbers["added_voxels"], 350)

    def test_a_release_fragment_is_kept_whole_and_the_arm_never_draws_over_the_release(self):
        mask = stack(ids(FULL + [None]))
        height = mask.shape[2]
        top = slot_top(height, 0)
        mask[:, :, top - BODY_SLICES:top] = 0
        mask[LOW:LOW + BODY, LOW:LOW + BODY, top - 1] = ID["C2"]         # a 144-voxel sliver of C2
        machine = stack(ids(FULL + ["sacrum"]))
        machine[:, :, top - 1] = 0                                       # the segmenter's C2 starts lower
        machine[LOW:LOW + BODY, LOW:LOW + 2, top - SLOT - 1] = ID["C2"]  # and reaches into C3's top slice
        slots = ids(FULL + ["sacrum"])
        record, levels, completed, arm, img = self.study(mask, (machine, slots, None))
        self.assertEqual(outcome(record, "C2")["state"], C.ADDED)
        self.assertEqual(outcome(record, "C2")["release_fragment_voxels"], 144)
        self.assertEqual(outcome(record, "C2")["release_fragment_inside"], 0)
        release_all = np.concatenate([C.flat(points, img.shape) for points in levels.values()])
        self.assertEqual(len(np.intersect1d(arm["C2"], release_all)), 0)
        self.assertEqual(len(np.intersect1d(completed["C2"], C.flat(levels["C2"], img.shape))), 144)
        self.assertEqual(len(np.intersect1d(completed["C2"], C.flat(levels["C3"], img.shape))), 0)

    def test_a_stray_label_under_the_floor_is_left_out_of_the_chain(self):
        release = [n if n not in ("T6", "T7") else None for n in FULL] + [None]
        machine = stack(ids(FULL + ["sacrum"]))
        machine[0:2, 0:2, slot_top(machine.shape[2], FULL.index("T7")) - 1] = ID["T13"]
        record, *_ = self.study(release, (machine, ids(FULL + ["sacrum"]), None))
        self.assertEqual(record["machine_small"], [{"label": ID["T13"], "voxels": 4}])
        self.assertEqual(outcome(record, "T7")["state"], C.ADDED)


class Bodies(unittest.TestCase):
    """The body checks of rule 6 on bodies placed by hand."""

    def body(self, low, high):
        points = np.array([[i, j, k] for i in range(12) for j in range(12) for k in range(low, high)])
        return C.placed(points, AFFINE)

    def check(self, slices, discs, name="T5"):
        bodies = {label: self.body(*span) for label, span in slices.items()}
        disc_points = np.array([[i, j, k] for i in range(12) for j in range(12) for k in discs]) if discs else C.NO_POINTS
        return C.body_check(name, 1, 2, (2, 3), None, bodies, C.placed(disc_points, AFFINE),
                            {1: 1.0, 2: 1.0, 3: 1.0}, C.cell_of(AFFINE))

    def test_one_body_one_disc_away_passes(self):
        numbers, reason = self.check({3: (0, 4), 2: (5, 9), 1: (10, 14)}, [4, 9])
        self.assertIsNone(reason)
        self.assertEqual(numbers["discs_between"], 1)

    def test_two_bodies_drawn_as_one_hold_a_disc_inside(self):
        numbers, reason = self.check({3: (0, 9), 2: (10, 19), 1: (20, 29)}, [9, 19, 24], name="C2")
        self.assertIn("a disc lies in the middle third of its body", reason)

    def test_no_disc_between_two_bodies_is_refused(self):
        numbers, reason = self.check({3: (0, 4), 2: (5, 9), 1: (10, 14)}, [4])
        self.assertIn("0 discs lie between", reason)

    def test_a_body_too_short_is_refused(self):
        numbers, reason = self.check({3: (0, 4), 2: (5, 9), 1: (10, 12)}, [4, 9])
        self.assertIn("times its inner neighbour's height", reason)

    def test_a_body_in_pieces_is_refused(self):
        bodies = {label: self.body(0, 4) for label in (1, 2, 3)}
        numbers, reason = C.body_check("T5", 1, 2, (2, 3), None, bodies, C.placed(C.NO_POINTS, AFFINE),
                                       {1: 0.6, 2: 1.0, 3: 1.0}, C.cell_of(AFFINE))
        self.assertIn("largest piece holds 60%", reason)


class Tilted(unittest.TestCase):
    """The body checks on a column tilted 35 degrees from the image's head-foot axis, as VerSe's
    sagittal necks are: boxes 12 mm wide and 16 mm deep, stacked along the column on a 1 mm grid."""

    ANGLE = 35.0

    def box(self, first, last):
        """The voxels of a box from first to last mm along the tilted column."""
        angle = np.radians(self.ANGLE)
        axis, depth = np.array([0.0, np.sin(angle), np.cos(angle)]), np.array([0.0, np.cos(angle), -np.sin(angle)])
        steps = np.arange(first, last, 0.5)[:, None, None] * axis + np.arange(-8, 8, 0.5)[None, :, None] * depth
        points = steps.reshape(-1, 3)[:, None, :] + np.array([[x, 0.0, 0.0] for x in range(12)])[None]
        return np.unique(np.round(points.reshape(-1, 3) + [20, 40, 40]).astype(np.int64), axis=0)

    def check(self, bodies, discs, name="T5"):
        placed = {label: C.placed(self.box(*span), np.eye(4)) for label, span in bodies.items()}
        disc_points = np.concatenate([self.box(*span) for span in discs])
        return C.body_check(name, 1, 2, (2, 3), None, placed, C.placed(disc_points, np.eye(4)),
                            {1: 1.0, 2: 1.0, 3: 1.0}, C.cell_of(np.eye(4)))

    def test_a_tilted_body_with_the_disc_beside_it_at_its_middle_height_passes(self):
        bodies = {3: (26, 36), 2: (13, 23), 1: (0, 10)}
        discs = [(10, 13), (23, 26)]
        body, disc = self.box(*bodies[1]), self.box(*discs[0])
        z, low, high = body[:, 2], body[:, 2].min(), body[:, 2].max()
        middle_height = (disc[:, 2] > low + (high - low) / 4) & (disc[:, 2] < high - (high - low) / 4)
        under = np.all((disc[:, :2] >= body[:, :2].min(0)) & (disc[:, :2] <= body[:, :2].max(0)), axis=1)
        self.assertGreater(int((middle_height & under).sum()), 0)
        numbers, reason = self.check(bodies, discs)
        self.assertIsNone(reason)
        self.assertEqual(numbers["discs_between"], 1)
        self.assertEqual(numbers["disc_voxels_middle"], 0)
        self.assertAlmostEqual(numbers["tilt_deg"], self.ANGLE, delta=1.0)

    def test_two_tilted_bodies_drawn_as_one_hold_a_disc_inside(self):
        bodies = {3: (52, 75), 2: (26, 49), 1: (0, 23)}
        discs = [(23, 26), (49, 52), (8, 11)]
        numbers, reason = self.check(bodies, discs)
        self.assertIn("a disc lies in the middle third of its body", reason)

    def test_a_body_missed_on_a_tilted_column_leaves_two_discs(self):
        bodies = {3: (52, 62), 2: (26, 36), 1: (0, 10)}
        discs = [(10, 13), (23, 26), (36, 39)]
        numbers, reason = self.check(bodies, discs)
        self.assertIn("2 discs lie between", reason)


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
        machine_mask = stack(ids(FULL + ["sacrum"]))
        machine = save(os.path.join(self.tmp.name, "s0001.nii.gz"), machine_mask)
        spine = save(os.path.join(self.tmp.name, "s0001_spine.nii.gz"),
                     subregion_mask(machine_mask, ids(FULL + ["sacrum"])))
        record, *_ = C.complete_study("totalsegmentator", folder, machine, spine)
        self.assertEqual(record["added"], ["T6"])
        self.assertEqual(len(record["files"]["release"]), len(FULL))

    def test_a_release_that_differs_from_its_facts_row_is_caught(self):
        levels = {"L5": np.zeros((5, 3), np.int32)}
        self.assertTrue(C.same_release(levels, {"levels": {"L5": {"voxels": 5}}}))
        self.assertFalse(C.same_release(levels, {"levels": {"L5": {"voxels": 6}}}))
        self.assertFalse(C.same_release(levels, {"levels": {"L5": {"voxels": 5}, "L4": {"voxels": 9}}}))


class CommandLine(unittest.TestCase):
    def test_records_masks_and_completed_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Study(tmp, FULL + [None], FULL + ["sacrum"])
            whole = Study(tmp, FULL + [None], FULL + [None], sid="verse002")
            rows = {}
            for sid, s in (("verse001", study), ("verse002", whole)):
                img = F.image_of(read(s.release))
                found = F.voxel_points(img)
                levels = {F.VERSE_NAMES[label]: points for label, points in found.items()}
                rows[sid] = F.study_row("verse", sid, {"release.nii.gz": read(s.release)},
                                        img, levels, {}, {})
            facts = os.path.join(tmp, "facts.jsonl")
            with open(facts, "w", encoding="ascii") as f:
                f.writelines(F.row_line(row) for row in rows.values())
            how = os.path.join(tmp, "input.json")
            write_json({"input": "as_is"}, how)
            spec = {"segmenter": {"name": "SPINEPS"}, "facts": {"verse": facts},
                    "studies": [{"id": "verse001", "member": "verse", "release": study.release,
                                 "machine": study.machine, "spine": study.spine, "input": how},
                                {"id": "verse002", "member": "verse", "release": whole.release,
                                 "machine": whole.machine, "spine": whole.spine}]}
            jobs = os.path.join(tmp, "jobs.json")
            write_json(spec, jobs)
            out = os.path.join(tmp, "out")
            os.makedirs(os.path.join(out, "masks"))
            stale = os.path.join(out, "masks", "verse002_machine.nii.gz")
            with open(stale, "wb"):                                     # an arm an earlier run left
                pass
            with redirect_stdout(io.StringIO()):
                C.main([jobs, out])
            records = [json.loads(line) for line in read(os.path.join(out, "records.jsonl"), "r").splitlines()]
            self.assertEqual([r["id"] for r in records], ["verse001", "verse002"])
            self.assertEqual(records[0]["input"], {"input": "as_is"})
            self.assertEqual(records[1]["refused"], ["sacrum"])
            completed = [json.loads(line) for line in read(os.path.join(out, "facts.jsonl"), "r").splitlines()]
            self.assertEqual(len(completed), 1)
            row = completed[0]
            self.assertIn("sacrum", row["levels"])
            self.assertEqual(list(row["machine_levels"]), ["sacrum"])
            self.assertIn("L5-sacrum", row["distances_mm"])
            name = "verse001_machine.nii.gz"
            data = read(os.path.join(out, "masks", name))
            self.assertEqual(row["machine_files"][name]["sha256"], hashlib.sha256(data).hexdigest())
            self.assertFalse(os.path.exists(stale))


if __name__ == "__main__":
    unittest.main()
