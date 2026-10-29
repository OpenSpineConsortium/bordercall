"""Complete a full-spine CT's column with a segmenter's levels, kept as a machine arm of its own.

Confidential, like the rest of this repository: nothing here, and nothing it writes, goes to a
public place, and no mask or CT is ever copied into the repository.

The owner's words of 2026-10-29 03:32 UTC, on the CTs of the gold tier 3 dataset whose field shows C2
and the sacrum while the release masks stop short of them: "segment the c2 and sacrums which are on ct
volumes they just lack the masks and convert them all to gold tier 3 data"; and his choice that morning
to run SPINEPS's CT models in a cloud container rather than wait for the grid. SPINEPS draws every
vertebra it finds and the sacrum, each under a name of its own labelling model; this module decides
which of those levels may stand for a level the release does not draw, and writes them as a mask of
their own on the CT's grid, beside the release's and never over it, so the two arms are never pooled.

A segmenter's name is not trusted alone, since a labelling model can be off by a level, and a count
from a level the release names is not trusted alone either, since a segmenter can merge two bodies or
split one. So a level is taken only where the two agree, or where the release names the levels on both
sides of it:

1. Anchors. A release level drawn with at least MIN_VOXELS voxels and a segmenter level that are each
   the other's best match by Dice, at MATCH_DICE or more, are one body. The anchors must run in the same
   order, head to foot, in both arms, or nothing is taken.
2. Between two anchors, the release's names leave a gap; where the segmenter has exactly as many levels
   between the same two bodies as the gap has names, and the release draws none of them, they take the
   gap's names in order.
3. Above the head-most anchor and below the foot-most, the count runs from one side only: each level
   takes the next name outwards only where the segmenter's own name for it is that name too, and the
   walk stops at the first that is not.
4. The sacrum is the segmenter's sacrum, taken only where the release's foot-most drawn level is an
   anchor and every segmenter level between that anchor and the sacrum has been named.
5. Every level so named holds at least MIN_VOXELS voxels outside the release's own, and no more than
   MAX_RELEASE_SHARE of it lies under another of the release's levels.

A target the rules do not take is refused, with the reason, and stays undrawn: a level the field test
asked for that no rule names is left to a person, never guessed.

    python -m holdings.fullspine_complete JOBS.json OUT [--workers N]

JOBS.json holds {"segmenter": {...}, "facts": {member: FACTS.jsonl}, "studies": [{"id", "member",
"release", "machine", "input", "targets"}]}: the segmenter's record copied into every row, each member's facts
from holdings.fullspine_facts, and per study the release mask (VerSe's one file) or folder (Total-
Segmentator's vertebrae_*.nii.gz and sacrum.nii.gz), the segmenter's vertebra mask on the CT's grid and,
where there is one, a JSON file saying how the CT went into the segmenter. OUT receives:

    records.jsonl  one row per study: the files read and written, the anchors, the segmenter's levels
                   head to foot, and each target with its state (added or refused) and the numbers it
                   rests on;
    facts.jsonl    for each study with a level added, its facts row with those levels drawn: the
                   level's facts read from its voxels in either arm, distances_mm read again, and
                   machine_levels saying which levels came from the segmenter; the ribs are left as
                   the release's levels read them;
    masks/         <id>_machine.nii.gz, the added levels in VerSe's ids on the CT's grid, written
                   byte for byte the same on every run.

A study's targets are the names it asks for, in its job's "targets": SchwingNet's field test lists
the levels each admitted study must have added (admission.json, complete), and C2 down to the head-most
drawn level where it holds the head end for a look. A name the field test does not ask for is never
added, so a body the release leaves unnamed above the sacrum (no_l5, which may be a transitional
vertebra the count is to read) is never named L5 here; a segmenter's level there is a level no name
accounts for, and the sacrum below it is refused. With no "targets", every name from C2 to L5 and the
sacrum that the release does not draw is a target, T13 and L6 never among them.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys

import nibabel as nib
import numpy as np

from holdings import fullspine_facts as F
from holdings.count_enhance_pet import MIN_VOXELS

MATCH_DICE = 0.5
MAX_RELEASE_SHARE = 0.10
VERSE_IDS = {name: label for label, name in F.VERSE_NAMES.items()}
TARGET_NAMES = tuple(name for name in F.COLUMN_NAMES if name not in ("C1", "T13", "L6"))
SACRUM = "sacrum"
ADDED, REFUSED = "added", "refused"


# ---------------------------------------------------------------- reading the two arms

def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def release_levels(member: str, release: str):
    """(grid image, {name: points}, {file: record}) of a study's release masks."""
    if member == "verse":
        data = read_bytes(release)
        img = F.image_of(data)
        found = F.voxel_points(img)
        levels = {F.VERSE_NAMES[label]: points for label, points in found.items() if label in F.VERSE_NAMES}
        return img, levels, {os.path.basename(release): F.file_record(data)}
    img, levels, files = None, {}, {}
    for base in sorted(os.listdir(release)):
        if base not in F.TS_LEVEL_FILES:
            continue
        data = read_bytes(os.path.join(release, base))
        files[base] = F.file_record(data)
        level_img = F.image_of(data)
        if img is None:
            img = level_img
        elif not F.same_grid(img, level_img):
            raise ValueError("%s lies on another grid" % base)
        points = F.voxel_points(level_img).get(1)
        if points is not None and len(points):
            levels[F.TS_LEVEL_FILES[base]] = points
    return img, levels, files


def machine_levels(path: str):
    """(image, {VerSe id: points}, record) of the segmenter's vertebra mask; its discs and endplates
    (100 and above) and any label outside VerSe's scheme are left out."""
    data = read_bytes(path)
    img = F.image_of(data)
    found = F.voxel_points(img)
    return img, {label: points for label, points in found.items() if label in F.VERSE_NAMES}, F.file_record(data)


# ---------------------------------------------------------------- voxels as sets

def flat(points: np.ndarray, shape) -> np.ndarray:
    return np.sort(np.ravel_multi_index(points.T, shape))


def common(first: np.ndarray, second: np.ndarray) -> int:
    return int(len(np.intersect1d(first, second, assume_unique=True)))


def height(points: np.ndarray, affine) -> float:
    """The mean head-foot position of a level, superior positive."""
    return float(F.world_points(points, affine)[:, 2].mean())


# ---------------------------------------------------------------- the rules

def anchors(release: dict, machine: dict, overlap: dict) -> dict:
    """{release name: segmenter label} for each pair that are each other's best match, at MATCH_DICE
    or more. release and machine give each level's voxel count, overlap {(name, label): shared}."""
    def dice(name, label):
        return 2.0 * overlap.get((name, label), 0) / (release[name] + machine[label])
    best_label = {name: max(machine, key=lambda label: dice(name, label)) for name in release} if machine else {}
    best_name = {label: max(release, key=lambda name: dice(name, label)) for label in machine} if release else {}
    return {name: label for name, label in best_label.items()
            if best_name.get(label) == name and dice(name, label) >= MATCH_DICE}


def in_order(pairs: dict, chain: list) -> bool:
    """The anchors run head to foot in the same order in both arms."""
    names = sorted(pairs, key=F.COLUMN_NAMES.index)
    places = [chain.index(pairs[name]) for name in names]
    return places == sorted(places) and len(set(places)) == len(places)


def refuse(name: str, reason: str) -> dict:
    return {"name": name, "state": REFUSED, "reason": reason}


def take(name: str, label: int, naming: str, machine_names: dict) -> dict:
    return {"name": name, "state": ADDED, "machine_label": label, "machine_name": machine_names[label],
            "naming": naming}


def between(upper: str, lower: str, names: list, places: list, drawn: set, machine_names: dict) -> list:
    """The gap between two anchors: names the release's gap, places the segmenter's levels there."""
    targets = [name for name in names if name not in drawn]
    unmatched = [name for name in names if name in drawn]
    if unmatched:
        reason = "the release draws %s between %s and %s and the segmenter matches none of it" % (
            ", ".join(unmatched), upper, lower)
        return [refuse(name, reason) for name in targets]
    if len(places) != len(names):
        reason = "the segmenter has %d levels between %s and %s, where the release's names leave %d" % (
            len(places), upper, lower, len(names))
        return [refuse(name, reason) for name in targets]
    return [take(name, label, "between %s and %s" % (upper, lower), machine_names)
            for name, label in zip(names, places)]


def outwards(anchor: str, names: list, places: list, drawn: set, machine_names: dict, side: str) -> tuple:
    """Names beyond the end anchor, walked outwards one level at a time: (outcomes, levels named)."""
    out, named, stopped = [], 0, None
    for i, name in enumerate(names):
        if stopped:
            if name not in drawn:
                out.append(refuse(name, stopped))
            continue
        if name in drawn:
            stopped = "the release draws %s %s %s and the segmenter matches none of it" % (name, side, anchor)
            continue
        if i >= len(places):
            stopped = "the segmenter has no level %s %s for %s" % (side, anchor, name)
            out.append(refuse(name, stopped))
            continue
        label = places[i]
        if machine_names[label] != name:
            stopped = "the count %s %s gives %s where the segmenter calls the level %s" % (
                side, anchor, name, machine_names[label])
            out.append(refuse(name, stopped))
            continue
        out.append(take(name, label, "%s %s, named alike by the count and the segmenter" % (side, anchor),
                        machine_names))
        named += 1
    return out, named


def sacrum_outcome(pairs: dict, drawn: set, chain: list, named_below: int, sacrum, heights: dict) -> dict:
    """The segmenter's sacrum, where the release's foot-most level is an anchor and every segmenter
    level from that anchor down to the sacrum has a name."""
    if sacrum is None:
        return refuse(SACRUM, "the segmenter draws no sacrum")
    column = [name for name in drawn if name != SACRUM]
    last = max(column, key=F.COLUMN_NAMES.index) if column else None
    if last is None or last not in pairs:
        return refuse(SACRUM, "the release's foot-most level %s is not matched by the segmenter" % last)
    after = chain[chain.index(pairs[last]) + 1 + named_below:]
    unnamed = [label for label in after if heights[label] > heights[sacrum]]
    if unnamed:
        return refuse(SACRUM, "the segmenter has %d level(s) between the release's %s and the sacrum that no "
                              "name accounts for" % (len(unnamed), last))
    return {"name": SACRUM, "state": ADDED, "machine_label": sacrum, "machine_name": SACRUM,
            "naming": "the segmenter's sacrum, below the release's %s" % last}


def plan(drawn: set, targets: list, chain: list, machine_names: dict, pairs: dict, sacrum, heights: dict) -> list:
    """Each target's outcome, before the voxel checks: drawn is the release's drawn names, chain the
    segmenter's vertebra labels head to foot, pairs the anchors."""
    if not pairs:
        return [refuse(name, "no release level is matched by the segmenter") for name in targets]
    if not in_order(pairs, chain):
        return [refuse(name, "the anchors run in another order in the segmenter's column") for name in targets]
    wanted = [name for name in targets if name != SACRUM]
    names = sorted((set(drawn) | set(wanted)) - {SACRUM}, key=F.COLUMN_NAMES.index)
    ends = sorted(pairs, key=F.COLUMN_NAMES.index)
    out = []
    for upper, lower in zip(ends, ends[1:]):
        gap = [n for n in names if F.COLUMN_NAMES.index(upper) < F.COLUMN_NAMES.index(n) < F.COLUMN_NAMES.index(lower)]
        places = chain[chain.index(pairs[upper]) + 1:chain.index(pairs[lower])]
        if gap:
            out += between(upper, lower, gap, places, drawn, machine_names)
    first, last = ends[0], ends[-1]
    above = [n for n in names if F.COLUMN_NAMES.index(n) < F.COLUMN_NAMES.index(first)][::-1]
    head, _ = outwards(first, above, chain[:chain.index(pairs[first])][::-1], drawn, machine_names, "above")
    below = [n for n in names if F.COLUMN_NAMES.index(n) > F.COLUMN_NAMES.index(last)]
    foot, named_below = outwards(last, below, chain[chain.index(pairs[last]) + 1:], drawn, machine_names, "below")
    out += head + foot
    if SACRUM in targets:
        out.append(sacrum_outcome(pairs, drawn, chain, named_below, sacrum, heights))
    order = {name: i for i, name in enumerate(targets)}
    return sorted((o for o in out if o["name"] in order), key=lambda o: order[o["name"]])


def voxel_check(outcome: dict, level: np.ndarray, release_all: np.ndarray, others: np.ndarray,
                fragment) -> dict:
    """The voxels a named level adds and how much of it the release's other levels hold."""
    own = len(level)
    added = own - common(level, release_all)
    share = common(level, others) / own if own else 1.0
    checked = dict(outcome, voxels=int(own), added_voxels=int(added),
                   release_share=F.rounded(share, F.SHARE_DECIMALS))
    if fragment is not None:
        checked["release_fragment_voxels"] = int(len(fragment))
        checked["release_fragment_inside"] = common(fragment, level)
    if added < MIN_VOXELS:
        return dict(checked, state=REFUSED, reason="it adds %d voxels outside the release's, under %d" % (added, MIN_VOXELS))
    if share > MAX_RELEASE_SHARE:
        return dict(checked, state=REFUSED,
                    reason="%.1f%% of it lies under the release's other levels, over %d%%" % (100 * share, 100 * MAX_RELEASE_SHARE))
    return checked


# ---------------------------------------------------------------- one study

def targets_of(drawn: set, asked=None) -> list:
    """The names to add, in the column's order: those asked for, else every one from C2 to L5 and the
    sacrum; a name the release draws is never a target."""
    wanted = TARGET_NAMES if asked is None else asked
    unknown = sorted(set(wanted) - set(F.COLUMN_NAMES))
    if unknown:
        raise ValueError("targets outside the column: %s" % ", ".join(unknown))
    return [name for name in F.COLUMN_NAMES if name in wanted and name not in drawn]


def chain_of(machine: dict, affine) -> tuple:
    """The segmenter's vertebrae of at least MIN_VOXELS head to foot, its sacrum, and the levels
    left out for size."""
    kept = {label: points for label, points in machine.items() if len(points) >= MIN_VOXELS}
    heights = {label: height(points, affine) for label, points in kept.items()}
    sacrum = VERSE_IDS[SACRUM] if VERSE_IDS[SACRUM] in kept else None
    chain = sorted((label for label in kept if label != VERSE_IDS[SACRUM]), key=lambda label: -heights[label])
    small = sorted(label for label in machine if label not in kept)
    return chain, sacrum, heights, small


def complete_study(member: str, release: str, machine_path: str, asked=None):
    """(record, completed levels {name: points}, arm {name: points}, grid image) of one study."""
    img, levels, release_files = release_levels(member, release)
    machine_img, machine, machine_file = machine_levels(machine_path)
    if not F.same_grid(img, machine_img):
        raise ValueError("the segmenter's mask lies on another grid than the release's")
    shape, affine = img.shape[:3], img.affine
    sets = {name: flat(points, shape) for name, points in levels.items()}
    machine_sets = {label: flat(points, shape) for label, points in machine.items()}
    drawn = {name for name, points in levels.items() if len(points) >= MIN_VOXELS}
    chain, sacrum, heights, small = chain_of(machine, affine)
    machine_names = {label: F.VERSE_NAMES[label] for label in machine}
    overlap = {(name, label): common(sets[name], machine_sets[label])
               for name in drawn - {SACRUM} for label in chain}
    pairs = anchors({name: len(sets[name]) for name in drawn - {SACRUM}},
                    {label: len(machine_sets[label]) for label in chain}, overlap)
    targets = targets_of(drawn, asked)
    release_all = np.unique(np.concatenate(list(sets.values()))) if sets else np.zeros(0, np.int64)
    outcomes, arm, completed = [], {}, {}
    for outcome in plan(drawn, targets, chain, machine_names, pairs, sacrum, heights):
        if outcome["state"] == ADDED:
            name, label = outcome["name"], outcome["machine_label"]
            others = [s for n, s in sets.items() if n != name]
            others = np.unique(np.concatenate(others)) if others else np.zeros(0, np.int64)
            outcome = voxel_check(outcome, machine_sets[label], release_all, others, sets.get(name))
            if outcome["state"] == ADDED:
                level = np.setdiff1d(machine_sets[label], others, assume_unique=True)
                completed[name] = level
                arm[name] = np.setdiff1d(level, release_all, assume_unique=True)
        outcomes.append(outcome)
    record = {"files": {"release": release_files, "machine": {os.path.basename(machine_path): machine_file}},
              "anchors": [{"release": name, "machine_label": pairs[name], "machine_name": machine_names[pairs[name]],
                           "dice": F.rounded(2.0 * overlap[(name, pairs[name])]
                                             / (len(sets[name]) + len(machine_sets[pairs[name]])), F.SHARE_DECIMALS)}
                          for name in sorted(pairs, key=F.COLUMN_NAMES.index)],
              "machine_column": [{"label": label, "name": machine_names[label], "voxels": int(len(machine[label])),
                                  "height_mm": F.rounded(heights[label], F.MM_DECIMALS)}
                                 for label in chain + ([sacrum] if sacrum else [])],
              "machine_small": [{"label": label, "voxels": int(len(machine[label]))} for label in small],
              "drawn": sorted(drawn, key=F.COLUMN_NAMES.index),
              "asked": None if asked is None else [n for n in F.COLUMN_NAMES if n in asked],
              "targets": outcomes,
              "added": [o["name"] for o in outcomes if o["state"] == ADDED],
              "refused": [o["name"] for o in outcomes if o["state"] == REFUSED]}
    return record, levels, completed, arm, img


def points_of(indices: np.ndarray, shape) -> np.ndarray:
    return np.stack(np.unravel_index(indices, shape), axis=1).astype(np.int32)


def arm_image(arm: dict, img):
    """The added levels in VerSe's ids, on the release's grid, as an unsigned byte NIfTI."""
    shape = img.shape[:3]
    volume = np.zeros(shape, np.uint8, order="F")
    for name, indices in arm.items():
        volume[np.unravel_index(indices, shape)] = VERSE_IDS[name]
    out = nib.Nifti1Image(volume, img.affine)
    out.set_qform(img.affine, code=1)
    out.set_sform(img.affine, code=1)
    return out


def arm_bytes(arm: dict, img) -> bytes:
    """The arm's .nii.gz bytes, the same on every run: gzip is given no time and no file name."""
    return gzip.compress(arm_image(arm, img).to_bytes(), compresslevel=6, mtime=0)


def completed_row(row: dict, levels: dict, completed: dict, arm: dict, img, record: dict, arm_file: dict) -> dict:
    """The facts row with the added levels drawn, read as holdings.fullspine_facts reads a level."""
    shape, affine = img.shape[:3], img.affine
    out = json.loads(json.dumps(row))
    points = dict(levels)
    for name, indices in completed.items():
        points[name] = points_of(indices, shape)
        out["levels"][name] = F.label_facts(points[name], affine, shape)
    out["levels"] = {name: out["levels"][name] for name in F.COLUMN_NAMES if name in out["levels"]}
    out["distances_mm"] = F.lumbosacral_distances(points, affine)
    out["machine_levels"] = {o["name"]: {"machine_label": o["machine_label"], "naming": o["naming"],
                                         "voxels": o["voxels"], "added_voxels": o["added_voxels"]}
                             for o in record["targets"] if o["state"] == ADDED}
    out["machine_files"] = arm_file
    return out


def study_job(job) -> dict:
    sid, member, release, machine, how, asked, segmenter, row, masks = job
    record, levels, completed, arm, img = complete_study(member, release, machine, asked)
    out = {"id": sid, "member": member, "segmenter": segmenter, "input": how, **record}
    if arm:
        name = "%s_machine.nii.gz" % sid
        data = arm_bytes(arm, img)
        with open(os.path.join(masks, name + ".tmp"), "wb") as f:
            f.write(data)
        os.replace(os.path.join(masks, name + ".tmp"), os.path.join(masks, name))
        out["files"]["arm"] = {name: F.file_record(data)}
        out["completed_facts"] = completed_row(row, levels, completed, arm, img, out, out["files"]["arm"])
    return out


def study_safe(job):
    return F.safe(study_job)(job)


# ---------------------------------------------------------------- running

def facts_rows(path: str) -> dict:
    with open(path, encoding="ascii") as f:
        return {row["id"]: row for row in map(json.loads, f)}


def jobs_of(spec: dict, masks: str) -> list:
    facts = {member: facts_rows(path) for member, path in spec["facts"].items()}
    out = []
    for study in spec["studies"]:
        how = json.loads(read_bytes(study["input"])) if study.get("input") else None
        out.append((study["id"], study["member"], study["release"], study["machine"], how, study.get("targets"),
                    spec["segmenter"], facts[study["member"]][study["id"]], masks))
    return out


def split_out(records: str, facts: str) -> int:
    """facts.jsonl from the records' completed rows, sorted by id."""
    rows = []
    with open(records, encoding="ascii") as f:
        for record in map(json.loads, f):
            if "completed_facts" in record:
                rows.append(record["completed_facts"])
    return F.write_rows(rows, facts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("jobs")
    parser.add_argument("out")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args(argv)
    masks = os.path.join(args.out, "masks")
    os.makedirs(masks, exist_ok=True)
    spec = json.loads(read_bytes(args.jobs))
    n = F.run(study_safe, jobs_of(spec, masks), os.path.join(args.out, "records.jsonl"), args.workers)
    m = split_out(os.path.join(args.out, "records.jsonl"), os.path.join(args.out, "facts.jsonl"))
    print("%d records, %d completed facts rows" % (n, m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
