"""Complete a full-spine CT's column with a segmenter's levels, kept as a machine arm of its own.

Confidential, like the rest of this repository: nothing here, and nothing it writes, goes to a
public place, and no mask or CT is ever copied into the repository.

The owner's words of 2026-10-29 03:32 UTC, on the CTs of the gold tier 3 dataset whose field shows C2
and the sacrum while the release masks stop short of them: "segment the c2 and sacrums which are on ct
volumes they just lack the masks and convert them all to gold tier 3 data"; and his choice that morning
to run SPINEPS's CT models in a cloud container rather than wait for the grid. SPINEPS draws every
vertebra it finds and the sacrum, each under a name of its own labelling model, and a subregion mask
that tells a vertebra's body from its arch and marks the discs; this module decides which of those
levels may stand for a level the release does not draw, and writes them as a mask of their own on the
CT's grid, beside the release's and never over it, so the two arms are never pooled.

A segmenter's name is not trusted alone, since a labelling model can be off by a level, and a count
from a level the release names is not trusted alone either, since a segmenter can merge two bodies,
split one or miss one, and a labeller that names its own levels in sequence then shifts its names with
the count. So a level is taken only where the count and the segmenter's name agree, or where the
release names the levels on both sides of it, and only where the segmenter's own bodies and discs show
one body there, read from its subregion mask and not from its names:

1. Anchors. A release level drawn with at least MIN_VOXELS voxels and a segmenter level that are each
   the other's best match by Dice, with at least MATCH_INSIDE of each lying inside the other, are one
   body; the second test refuses a segmenter level that takes in a neighbour the release leaves
   undrawn, which Dice alone lets pass (two bodies merged give 0.67). The anchors must run in the same
   order, head to foot, in both arms, or nothing is taken.
2. Between two anchors, the release's names leave a gap; where the segmenter has exactly as many levels
   between the same two bodies as the gap has names, the release draws none of them and every one of
   them passes the checks of rules 5 and 6, they take the gap's names in order; if any fails, none is
   taken, since the count that named the others ran through it.
3. Above the head-most anchor and below the foot-most, the count runs from one side only, over every
   name of the column from C2 to L5 and every name the release draws, whether asked for or not: each
   level takes the next name outwards only where the segmenter's own name for it is that name too and
   it passes the checks of rules 5 and 6, and the walk stops at the first that does not, refusing every
   name beyond it.
4. The sacrum is the segmenter's sacrum, taken only where the release's foot-most drawn level is an
   anchor, every segmenter level between that anchor and the sacrum was taken by the walk and asked
   for, the level directly above the sacrum is L5 or L6, exactly one disc lies between that level's
   body and the sacrum's far end, read as rule 6 reads a disc, and it passes rule 5.
5. Every level so named holds at least MIN_VOXELS voxels outside the release's own, and no more than
   MAX_RELEASE_SHARE of it lies under another of the release's levels.
6. Every vertebra so named is one body in the segmenter's subregion mask: its largest 26-connected
   piece holds LARGEST_SHARE of it, its body holds at least MIN_VOXELS voxels, its body's height is
   within HEIGHT_BAND of its inner neighbour's (C2's within C2_HEIGHT_BAND, for the dens), the step
   from its inner neighbour's body centre to its own is within STEP_BAND of the step from that
   neighbour to the next level inwards, exactly one disc lies between the two bodies' centres, and the
   disc in the middle third of its body holds less than MERGED_DISC_SHARE of the disc between it and
   its neighbour. A body split in two halves the height and the step and leaves no disc between the
   halves; two merged double them and hold a whole disc inside; a body the segmenter missed doubles
   the step and leaves two discs between its neighbours. Heights and discs are read along the column's
   own axis, from the inner neighbour's body centre to the level's, inside a cylinder about it as wide
   as the bodies, and steps are the distances between centres: the image's head-foot axis parts from
   the column's by 30 degrees and more in a sagittal CT's neck, where read along the image the disc
   beside a body stands at the height of the body's middle. On VerSe's verse018, verse033, verse558
   and verse559 (2026-10-29), each of the segmenter's 77 bodies beside its upper neighbour had one disc
   between them and at most 0.055 of it in its own middle third; each of the 73 pairs of consecutive
   bodies joined as one had two discs between it and its neighbour and at least 0.47 in its middle
   third; and each of the 73 bodies left out left two discs between its neighbours.

A target the rules do not take is refused, with the reason, and stays undrawn: a level the field test
asked for that no rule names is left to a person, never guessed.

    python -m holdings.fullspine_complete JOBS.json OUT [--workers N]

JOBS.json holds {"segmenter": {...}, "facts": {member: FACTS.jsonl}, "studies": [{"id", "member",
"release", "machine", "spine", "input", "targets"}]}: the segmenter's record copied into every row, each
member's facts from holdings.fullspine_facts, and per study the release mask (VerSe's one file) or
folder (TotalSegmentator's vertebrae_*.nii.gz and sacrum.nii.gz), the segmenter's vertebra mask and its
subregion mask on the CT's grid and, where there is one, a JSON file saying how the CT went into the
segmenter. A study whose release, read again, differs from its facts row in any level's voxel count is
an error row, since its completed row would mix two readings. OUT receives:

    records.jsonl  one row per study: the files read and written, the anchors, the segmenter's levels
                   head to foot, and each target with its state (added or refused) and the numbers it
                   rests on;
    facts.jsonl    for each study with a level added, its facts row with those levels drawn: the
                   level's facts read from its voxels in either arm, distances_mm read again, and
                   machine_levels saying which levels came from the segmenter; the ribs are left as
                   the release's levels read them;
    masks/         <id>_machine.nii.gz, the added levels in VerSe's ids on the CT's grid, written
                   byte for byte the same on every run; a mask no record vouches for is removed.

A study's targets are the names it asks for, in its job's "targets": SchwingNet's field test lists
the levels each admitted study must have added (admission.json, complete), and C2 down to the head-most
drawn level where it holds the head end for a look. A name the field test does not ask for is never
added, so a body the release leaves unnamed above the sacrum (no_l5, which may be a transitional
vertebra the count is to read) is never named L5 here, and the sacrum below it is refused. With no
"targets", every name from C2 to L5 and the sacrum that the release does not draw is a target, T13 and
L6 never among them.
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

MATCH_INSIDE = 0.8
MAX_RELEASE_SHARE = 0.10
LARGEST_SHARE = 0.9
HEIGHT_BAND = (0.6, 1.6)
C2_HEIGHT_BAND = (0.6, 2.5)
STEP_BAND = (0.6, 1.5)
DISC_FLOOR = 20          # voxels: a run of disc fewer than this is a speck, not a disc
DISC_GAP_MM = 2.5        # mm along the column that part one run of disc from the next, at least 1.5 voxels
RADIUS_PERCENTILE = 90   # a body's cylinder reaches as far from the column's axis as this share of its voxels
MERGED_DISC_SHARE = 0.2  # disc in a body's middle third, as a share of the disc beside it, that makes it two
CORPUS, DISC = 49, 100   # SPINEPS's subregion labels for a vertebra's body and for a disc
VERSE_IDS = {name: label for label, name in F.VERSE_NAMES.items()}
TARGET_NAMES = tuple(name for name in F.COLUMN_NAMES if name not in ("C1", "T13", "L6"))
SACRUM = "sacrum"
LAST_LUMBAR = ("L5", "L6")
ADDED, REFUSED = "added", "refused"
NO_POINTS = np.zeros((0, 3), np.int32)


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


def subregions(path: str):
    """(image, body points, disc points, record) of the segmenter's subregion mask."""
    data = read_bytes(path)
    img = F.image_of(data)
    found = F.voxel_points(img, {CORPUS, DISC})
    return img, found.get(CORPUS, NO_POINTS), found.get(DISC, NO_POINTS), F.file_record(data)


def same_release(levels: dict, row: dict) -> bool:
    """The release read for the matcher is the one the facts row was read from, level by level."""
    return ({name: int(len(points)) for name, points in levels.items()}
            == {name: entry["voxels"] for name, entry in row["levels"].items()})


# ---------------------------------------------------------------- voxels as sets

def flat(points: np.ndarray, shape) -> np.ndarray:
    return np.sort(np.ravel_multi_index(points.T, shape))


def common(first: np.ndarray, second: np.ndarray) -> int:
    return int(len(np.intersect1d(first, second, assume_unique=True)))


def height(points: np.ndarray, affine) -> float:
    """The mean head-foot position of a level, superior positive."""
    return float(F.world_points(points, affine)[:, 2].mean())


# ---------------------------------------------------------------- the segmenter's bodies and discs
#
# Every check below reads the column along its own axis, the line from one body's centre to its
# neighbour's, inside a cylinder about that line as wide as the bodies, and never along the image's
# head-foot axis: in VerSe's sagittal neck and upper thoracic CTs the two part by 30 degrees and more,
# and read along the image the disc beside a body stands at the height of the body's middle.

def placed(points: np.ndarray, affine) -> dict:
    """A set of voxels as the checks read it: its points in world mm."""
    return {"world": F.world_points(points, affine)}


def bodies_of(machine: dict, corpus: np.ndarray, affine, shape) -> dict:
    """{label: placed body}: each segmenter vertebra's voxels its subregion mask calls body, and the
    whole sacrum, whose subregions are not read."""
    body = flat(corpus, shape)
    out = {}
    for label, points in machine.items():
        if label != VERSE_IDS[SACRUM]:
            points = points[np.isin(np.ravel_multi_index(points.T, shape), body)]
        out[label] = placed(points, affine)
    return out


def cell_of(affine) -> np.ndarray:
    """The grid's three voxel edges in world mm, one per column."""
    return np.asarray(affine, float)[:3, :3]


def reach(cell: np.ndarray, axis: np.ndarray) -> float:
    """How far one voxel reaches along a unit axis, in mm."""
    return float(np.abs(cell.T @ axis).sum())


def axis_between(body: dict, other: dict) -> tuple:
    """(centre, unit axis, distance in mm) of the column from body's centre toward other's; the axis is
    None where the two centres meet."""
    centre = body["world"].mean(0)
    step = other["world"].mean(0) - centre
    distance = float(np.linalg.norm(step))
    return centre, (step / distance if distance else None), distance


def along(points: np.ndarray, centre: np.ndarray, axis: np.ndarray) -> tuple:
    """(position along the axis, distance from it) of each point, in mm."""
    offset = points - centre
    position = offset @ axis
    return position, np.linalg.norm(offset - np.outer(position, axis), axis=1)


def extent(body: dict, centre: np.ndarray, axis: np.ndarray) -> tuple:
    """(first, last) position of a body along the axis, in mm."""
    position = along(body["world"], centre, axis)[0]
    return float(position.min()), float(position.max())


def radius_of(body: dict, centre: np.ndarray, axis: np.ndarray) -> float:
    """How far a body reaches from the axis: the RADIUS_PERCENTILE of its voxels' distances, in mm."""
    return float(np.percentile(along(body["world"], centre, axis)[1], RADIUS_PERCENTILE))


def disc_runs(discs: dict, centre: np.ndarray, axis: np.ndarray, radius: float, low: float, high: float,
              voxel: float) -> list:
    """The runs of disc inside the cylinder of the radius about the axis, between low and high mm
    along it, each (start, end, voxels); voxels further apart along the axis than DISC_GAP_MM, or 1.5
    voxels, part two runs, and a run under DISC_FLOOR voxels is left out."""
    position, distance = along(discs["world"], centre, axis)
    position = np.sort(position[(distance <= radius) & (position > low) & (position < high)])
    if not len(position):
        return []
    cuts = np.flatnonzero(np.diff(position) > max(DISC_GAP_MM, 1.5 * voxel)) + 1
    runs = [(float(part[0]), float(part[-1]), int(len(part))) for part in np.split(position, cuts)]
    return [run for run in runs if run[2] >= DISC_FLOOR]


def discs_apart(body: dict, other: dict, discs: dict, cell: np.ndarray) -> list:
    """The runs of disc between two bodies' centres, inside the cylinder that holds them both."""
    centre, axis, distance = axis_between(body, other)
    if axis is None:
        return []
    radius = max(radius_of(body, centre, axis), radius_of(other, centre, axis))
    return disc_runs(discs, centre, axis, radius, 0.0, distance, reach(cell, axis))


def middle_disc(body: dict, discs: dict, centre: np.ndarray, axis: np.ndarray) -> int:
    """The disc voxels in the middle third of a body's length, inside its own cylinder."""
    first, last = extent(body, centre, axis)
    third = (last - first) / 3
    position, distance = along(discs["world"], centre, axis)
    inside = (distance <= radius_of(body, centre, axis)) & (position > first + third) & (position < last - third)
    return int(inside.sum())


def tilt_deg(axis: np.ndarray) -> float:
    """The angle between the column's axis and the image's head-foot axis, in degrees."""
    return float(np.degrees(np.arccos(min(1.0, abs(float(axis[2]))))))


def within(value: float, band: tuple) -> bool:
    return band[0] <= value <= band[1]


def body_check(name: str, label: int, inner: int, reference, outer, bodies: dict, discs: dict, shares: dict,
               cell: np.ndarray) -> tuple:
    """(numbers, reason or None) of rule 6 for the segmenter's level label, which the rules would name
    name, beside its inner neighbour inner; reference is the pair of levels whose step the level's own
    step is read against (None where the segmenter has none), outer a level beyond it that must also
    lie one disc away (the lower anchor of a gap), or None; cell is the grid's voxel edges."""
    if shares[label] < LARGEST_SHARE:
        return {"largest_share": F.rounded(shares[label], F.SHARE_DECIMALS)}, (
            "its largest piece holds %.0f%% of it, under %.0f%%" % (100 * shares[label], 100 * LARGEST_SHARE))
    body, near = bodies[label], bodies[inner]
    if len(body["world"]) < MIN_VOXELS or len(near["world"]) < MIN_VOXELS:
        return {"body_voxels": int(len(body["world"]))}, (
            "the segmenter's subregion mask gives it or its inner neighbour fewer than %d voxels of body" % MIN_VOXELS)
    centre, axis, step = axis_between(body, near)
    if axis is None:
        return {"body_voxels": int(len(body["world"]))}, "its body's centre is its inner neighbour's"
    voxel = reach(cell, axis)
    tall = np.subtract(*extent(body, centre, axis)[::-1]) + voxel
    near_tall = np.subtract(*extent(near, centre, axis)[::-1]) + voxel
    between = discs_apart(body, near, discs, cell)
    middle = middle_disc(body, discs, centre, axis)
    beside = sum(run[2] for run in between)
    numbers = {"body_voxels": int(len(body["world"])), "body_height_mm": F.rounded(tall, F.MM_DECIMALS),
               "height_ratio": F.rounded(tall / near_tall, F.SHARE_DECIMALS),
               "step_mm": F.rounded(step, F.MM_DECIMALS), "tilt_deg": F.rounded(tilt_deg(axis), F.MM_DECIMALS),
               "discs_between": len(between), "disc_voxels_between": int(beside),
               "disc_voxels_middle": middle, "largest_share": F.rounded(shares[label], F.SHARE_DECIMALS)}
    band = C2_HEIGHT_BAND if name == "C2" else HEIGHT_BAND
    if not within(tall / near_tall, band):
        return numbers, "its body is %.2f times its inner neighbour's height, outside %.1f to %.1f" % (
            tall / near_tall, band[0], band[1])
    if reference is None or any(len(bodies[other]["world"]) < MIN_VOXELS for other in reference):
        return numbers, "the segmenter has no pair of bodies beside it to compare its step with"
    against = axis_between(bodies[reference[0]], bodies[reference[1]])[2]
    numbers["step_ratio"] = F.rounded(step / against, F.SHARE_DECIMALS) if against else None
    if not against or not within(step / against, STEP_BAND):
        return numbers, "its step from its neighbour is %.1f mm against %.1f mm beside it, outside %.1f to %.1f times" % (
            step, against, STEP_BAND[0], STEP_BAND[1])
    if len(between) != 1:
        return numbers, "%d discs lie between its body and its neighbour's, where one should" % len(between)
    if middle >= MERGED_DISC_SHARE * beside:
        return numbers, "a disc lies in the middle third of its body: %d voxels against %d between it and its neighbour" % (
            middle, beside)
    if outer is not None:
        beyond = discs_apart(body, bodies[outer], discs, cell)
        numbers["discs_beyond"] = len(beyond)
        if len(beyond) != 1:
            return numbers, "%d discs lie between its body and the next anchor's, where one should" % len(beyond)
    return numbers, None


def sacrum_check(sacrum: int, above: int, bodies: dict, discs: dict, cell: np.ndarray) -> tuple:
    """(numbers, reason or None): exactly one disc lies between the body above the sacrum and the
    sacrum's far end, along the axis from that body's centre to the sacrum's and inside that body's
    cylinder; a second is a disc inside what the segmenter calls the sacrum."""
    body = bodies[above]
    if len(body["world"]) < MIN_VOXELS:
        return {}, "the segmenter's subregion mask gives the level above the sacrum fewer than %d voxels of body" % MIN_VOXELS
    centre, axis, _ = axis_between(body, bodies[sacrum])
    if axis is None:
        return {}, "the sacrum's centre is the body above it's"
    runs = disc_runs(discs, centre, axis, radius_of(body, centre, axis), 0.0,
                     extent(bodies[sacrum], centre, axis)[1], reach(cell, axis))
    numbers = {"discs_between": len(runs), "tilt_deg": F.rounded(tilt_deg(axis), F.MM_DECIMALS)}
    if len(runs) != 1:
        return numbers, "%d discs lie between the body above it and its foot, where one should" % len(runs)
    return numbers, None


# ---------------------------------------------------------------- the rules

def anchors(release: dict, machine: dict, overlap: dict) -> dict:
    """{release name: segmenter label} for each pair that are each other's best match by Dice, with
    at least MATCH_INSIDE of each inside the other. release and machine give each level's voxel count,
    overlap {(name, label): shared}."""
    def dice(name, label):
        return 2.0 * overlap.get((name, label), 0) / (release[name] + machine[label])

    def inside(name, label):
        shared = overlap.get((name, label), 0)
        return shared >= MATCH_INSIDE * release[name] and shared >= MATCH_INSIDE * machine[label]
    best_label = {name: max(machine, key=lambda label: dice(name, label)) for name in release} if machine else {}
    best_name = {label: max(release, key=lambda name: dice(name, label)) for label in machine} if release else {}
    return {name: label for name, label in best_label.items()
            if best_name.get(label) == name and inside(name, label)}


def in_order(pairs: dict, chain: list) -> bool:
    """The anchors run head to foot in the same order in both arms."""
    names = sorted(pairs, key=F.COLUMN_NAMES.index)
    places = [chain.index(pairs[name]) for name in names]
    return places == sorted(places) and len(set(places)) == len(places)


def refuse(name: str, reason: str, numbers=None) -> dict:
    return dict(numbers or {}, name=name, state=REFUSED, reason=reason)


def take(name: str, label: int, naming: str, machine_names: dict, numbers: dict) -> dict:
    return dict(numbers, name=name, state=ADDED, machine_label=label, machine_name=machine_names[label],
                naming=naming)


def between(upper: str, lower: str, names: list, places: list, drawn: set, machine_names: dict,
            fits, ends: tuple) -> list:
    """The gap between two anchors: names the release's gap, places the segmenter's levels there, ends
    ([the upper anchor's label, the level above it or None], the lower anchor's label)."""
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
    above, below = ends
    chain = [label for label in above[::-1] if label is not None] + list(places) + [below]
    first = len(chain) - len(places) - 1
    out, failed = [], None
    for i, (name, label) in enumerate(zip(names, places)):
        at = first + i
        reference = (chain[at - 1], chain[at - 2]) if at >= 2 else (label, chain[at + 1])
        outer = below if i == len(places) - 1 else None
        numbers, reason = fits(name, label, chain[at - 1], reference, outer)
        out.append((name, label, numbers))
        if reason and not failed:
            failed = "the segmenter's level the count names %s between %s and %s: %s; so no level of the gap is taken" % (
                name, upper, lower, reason)
    if failed:
        return [refuse(name, failed, numbers) for name, _, numbers in out]
    return [take(name, label, "between %s and %s" % (upper, lower), machine_names, numbers)
            for name, label, numbers in out]


def outwards(anchor: str, names: list, places: list, drawn: set, machine_names: dict, side: str,
             fits, inward: list) -> tuple:
    """Names beyond the end anchor, walked outwards one level at a time, places the segmenter's levels
    beyond it, nearest first, inward [anchor's label, the level inward of it or None]: (outcomes,
    [(name, label)] of the levels the walk took, in order)."""
    out, walked, stopped = [], [], None
    chain = list(inward)
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
        numbers, reason = fits(name, label, chain[0], (chain[0], chain[1]) if len(chain) > 1 else None, None)
        if reason:
            stopped = "the segmenter's level the count %s %s names %s: %s" % (side, anchor, name, reason)
            out.append(refuse(name, stopped, numbers))
            continue
        out.append(take(name, label, "%s %s, named alike by the count and the segmenter" % (side, anchor),
                        machine_names, numbers))
        walked.append((name, label))
        chain.insert(0, label)
    return out, walked


def sacrum_outcome(pairs: dict, drawn: set, chain: list, walked: list, targets: list, sacrum, heights: dict,
                   fits_sacrum) -> dict:
    """The segmenter's sacrum, where the release's foot-most level is an anchor, every segmenter level
    from that anchor down to the sacrum was taken by the walk and asked for, and the level directly
    above it is the last lumbar."""
    if sacrum is None:
        return refuse(SACRUM, "the segmenter draws no sacrum")
    column = [name for name in drawn if name != SACRUM]
    last = max(column, key=F.COLUMN_NAMES.index) if column else None
    if last is None or last not in pairs:
        return refuse(SACRUM, "the release's foot-most level %s is not matched by the segmenter" % last)
    after = chain[chain.index(pairs[last]) + 1 + len(walked):]
    unnamed = [label for label in after if heights[label] > heights[sacrum]]
    if unnamed:
        return refuse(SACRUM, "the segmenter has %d level(s) between the release's %s and the sacrum that no "
                              "name accounts for" % (len(unnamed), last))
    unasked = [name for name, _ in walked if name not in targets]
    if unasked:
        return refuse(SACRUM, "the count names the segmenter's level(s) below the release's %s %s, which the "
                              "field test does not ask for, so the sacrum would lie under a body no "
                              "arm draws" % (last, ", ".join(unasked)))
    above, label = walked[-1] if walked else (last, pairs[last])
    if above not in LAST_LUMBAR:
        return refuse(SACRUM, "the sacrum would lie directly under %s, and a body the segmenter folds into "
                              "its sacrum cannot be told from a spine with fewer lumbar levels" % above)
    numbers, reason = fits_sacrum(SACRUM, sacrum, label)
    if reason:
        return refuse(SACRUM, "the segmenter's sacrum below %s: %s" % (above, reason), numbers)
    return take(SACRUM, sacrum, "the segmenter's sacrum, below %s" % above, {sacrum: SACRUM}, numbers)


def plan(drawn: set, targets: list, chain: list, machine_names: dict, pairs: dict, sacrum, heights: dict,
         fits, fits_sacrum) -> list:
    """Each target's outcome: drawn is the release's drawn names, chain the segmenter's vertebra labels
    head to foot, pairs the anchors; fits(name, label, inner, reference, outer), read as body_check
    reads them, and fits_sacrum(name, label, above) give (numbers, reason or None) of rules 5 and 6 and
    of rules 4 and 5."""
    if not pairs:
        return [refuse(name, "no release level is matched by the segmenter") for name in targets]
    if not in_order(pairs, chain):
        return [refuse(name, "the anchors run in another order in the segmenter's column") for name in targets]
    names = sorted((set(drawn) | set(TARGET_NAMES)) - {SACRUM}, key=F.COLUMN_NAMES.index)
    ends = sorted(pairs, key=F.COLUMN_NAMES.index)
    out = []
    for upper, lower in zip(ends, ends[1:]):
        gap = [n for n in names if F.COLUMN_NAMES.index(upper) < F.COLUMN_NAMES.index(n) < F.COLUMN_NAMES.index(lower)]
        top, foot = chain.index(pairs[upper]), chain.index(pairs[lower])
        if gap:
            out += between(upper, lower, gap, chain[top + 1:foot], drawn, machine_names, fits,
                           ([chain[top], chain[top - 1] if top else None], chain[foot]))
    first, last = ends[0], ends[-1]
    head_at, foot_at = chain.index(pairs[first]), chain.index(pairs[last])
    above = [n for n in names if F.COLUMN_NAMES.index(n) < F.COLUMN_NAMES.index(first)][::-1]
    head, _ = outwards(first, above, chain[:head_at][::-1], drawn, machine_names, "above", fits,
                       chain[head_at:head_at + 2])
    below = [n for n in names if F.COLUMN_NAMES.index(n) > F.COLUMN_NAMES.index(last)]
    foot, walked = outwards(last, below, chain[foot_at + 1:], drawn, machine_names, "below", fits,
                            chain[max(0, foot_at - 1):foot_at + 1][::-1])
    out += head + foot
    if SACRUM in targets:
        out.append(sacrum_outcome(pairs, drawn, chain, walked, targets, sacrum, heights, fits_sacrum))
    order = {name: i for i, name in enumerate(targets)}
    return sorted((o for o in out if o["name"] in order), key=lambda o: order[o["name"]])


def voxel_check(level: np.ndarray, release_all: np.ndarray, others: np.ndarray, fragment) -> tuple:
    """(numbers, reason or None) of rule 5: the voxels a named level adds and how much of it the
    release's other levels hold."""
    own = len(level)
    added = own - common(level, release_all)
    share = common(level, others) / own if own else 1.0
    numbers = {"voxels": int(own), "added_voxels": int(added), "release_share": F.rounded(share, F.SHARE_DECIMALS)}
    if fragment is not None:
        numbers["release_fragment_voxels"] = int(len(fragment))
        numbers["release_fragment_inside"] = common(fragment, level)
    if added < MIN_VOXELS:
        return numbers, "it adds %d voxels outside the release's, under %d" % (added, MIN_VOXELS)
    if share > MAX_RELEASE_SHARE:
        return numbers, "%.1f%% of it lies under the release's other levels, over %d%%" % (
            100 * share, 100 * MAX_RELEASE_SHARE)
    return numbers, None


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


def others_of(sets: dict, name: str) -> np.ndarray:
    rest = [indices for other, indices in sets.items() if other != name]
    return np.unique(np.concatenate(rest)) if rest else np.zeros(0, np.int64)


def checkers(sets, machine, machine_sets, release_all, bodies, discs, cell):
    """fits and fits_sacrum for plan(): rule 5 for every level, then rule 6 for a vertebra or rule 4's
    disc for the sacrum."""
    shares = {label: F.pieces(points)[1] for label, points in machine.items()}

    def voxels(name, label):
        return voxel_check(machine_sets[label], release_all, others_of(sets, name), sets.get(name))

    def fits(name, label, inner, reference, outer):
        numbers, reason = voxels(name, label)
        if reason:
            return numbers, reason
        body, reason = body_check(name, label, inner, reference, outer, bodies, discs, shares, cell)
        return dict(numbers, body=body), reason

    def fits_sacrum(name, label, above):
        numbers, reason = voxels(name, label)
        if reason:
            return numbers, reason
        body, reason = sacrum_check(label, above, bodies, discs, cell)
        return dict(numbers, body=body), reason
    return fits, fits_sacrum


def anchor_rows(pairs: dict, overlap: dict, sets: dict, machine_sets: dict, machine_names: dict) -> list:
    rows = []
    for name in sorted(pairs, key=F.COLUMN_NAMES.index):
        label = pairs[name]
        shared, r, m = overlap[(name, label)], len(sets[name]), len(machine_sets[label])
        rows.append({"release": name, "machine_label": label, "machine_name": machine_names[label],
                     "dice": F.rounded(2.0 * shared / (r + m), F.SHARE_DECIMALS),
                     "inside_release": F.rounded(shared / r, F.SHARE_DECIMALS),
                     "inside_machine": F.rounded(shared / m, F.SHARE_DECIMALS)})
    return rows


def complete_study(member: str, release: str, machine_path: str, spine_path: str, asked=None):
    """(record, release levels {name: points}, completed levels {name: indices}, arm {name: indices},
    grid image) of one study."""
    img, levels, release_files = release_levels(member, release)
    machine_img, machine, machine_file = machine_levels(machine_path)
    spine_img, corpus, disc, spine_file = subregions(spine_path)
    if not F.same_grid(img, machine_img) or not F.same_grid(img, spine_img):
        raise ValueError("the segmenter's masks lie on another grid than the release's")
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
    fits, fits_sacrum = checkers(sets, machine, machine_sets, release_all,
                                 bodies_of(machine, corpus, affine, shape), placed(disc, affine), cell_of(affine))
    outcomes = plan(drawn, targets, chain, machine_names, pairs, sacrum, heights, fits, fits_sacrum)
    arm, completed = {}, {}
    for outcome in outcomes:
        if outcome["state"] == ADDED:
            name = outcome["name"]
            level = np.setdiff1d(machine_sets[outcome["machine_label"]], others_of(sets, name), assume_unique=True)
            arm[name] = np.setdiff1d(level, release_all, assume_unique=True)
            completed[name] = np.union1d(arm[name], sets[name]) if name in sets else arm[name]
    record = {"files": {"release": release_files,
                        "machine": {os.path.basename(machine_path): machine_file,
                                    os.path.basename(spine_path): spine_file}},
              "anchors": anchor_rows(pairs, overlap, sets, machine_sets, machine_names),
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


def completed_row(row: dict, levels: dict, completed: dict, img, record: dict, arm_file: dict) -> dict:
    """The facts row with the added levels drawn, each read as holdings.fullspine_facts reads a level
    from its voxels in both arms: the release's own fragment of it, if any, and the segmenter's."""
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
    sid, member, release, machine, spine, how, asked, segmenter, row, masks = job
    record, levels, completed, arm, img = complete_study(member, release, machine, spine, asked)
    if not same_release(levels, row):
        raise ValueError("the release read here differs from the one its facts row was read from")
    out = {"id": sid, "member": member, "segmenter": segmenter, "input": how, **record}
    if arm:
        name = "%s_machine.nii.gz" % sid
        data = arm_bytes(arm, img)
        with open(os.path.join(masks, name + ".tmp"), "wb") as f:
            f.write(data)
        os.replace(os.path.join(masks, name + ".tmp"), os.path.join(masks, name))
        out["files"]["arm"] = {name: F.file_record(data)}
        out["completed_facts"] = completed_row(row, levels, completed, img, out, out["files"]["arm"])
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
        out.append((study["id"], study["member"], study["release"], study["machine"], study["spine"], how,
                    study.get("targets"), spec["segmenter"], facts[study["member"]][study["id"]], masks))
    return out


def read_records(records: str) -> list:
    with open(records, encoding="ascii") as f:
        return [json.loads(line) for line in f]


def split_out(records: list, facts: str) -> int:
    """facts.jsonl from the records' completed rows, sorted by id."""
    return F.write_rows([record["completed_facts"] for record in records if "completed_facts" in record], facts)


def sweep_masks(records: list, masks: str) -> list:
    """Remove every file in masks/ that no record names as its arm, a study refused, failed or dropped
    since an earlier run among them, so masks/ holds only what records.jsonl vouches for."""
    kept = {name for record in records for name in record.get("files", {}).get("arm", {})}
    removed = sorted(name for name in os.listdir(masks) if name not in kept)
    for name in removed:
        os.remove(os.path.join(masks, name))
    return removed


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
    records = read_records(os.path.join(args.out, "records.jsonl"))
    m = split_out(records, os.path.join(args.out, "facts.jsonl"))
    removed = sweep_masks(records, masks)
    print("%d records, %d completed facts rows, %d stale masks removed" % (n, m, len(removed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
