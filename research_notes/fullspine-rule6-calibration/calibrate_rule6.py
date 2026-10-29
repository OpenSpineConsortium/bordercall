"""Calibrate rule 6 as holdings.fullspine_complete ships it, on real SPINEPS output, reading only the
segmenter's own masks and calling the module's own readers (column_of, side_reading, sacrum_check), so
the numbers its docstring gives are the code's and not a copy's.

For each study, along the segmenter's column head to foot and foot to head, each body v beside the
level n it is reached from and the level o beyond it:

- one_inner, one_outer: v read against n and against o, as they stand;
- overreach: v with the part of o's body nearest it taken in (5, 10, 20, 30% of o's height), read
  against the rest of o, as a body that reaches across the disc into its neighbour;
- split_dropped: v cut short at its outer end (60, 70, 80, 90% of its height kept, the rest dropped),
  read against o;
- ratios and discless: v's height and step ratios as body_check reads them, and those of v and o
  joined with the disc between them deleted, as two bodies the segmenter merged with no disc drawn;
- sacrum: sacrum_check of the sacrum below the foot-most vertebra.

Reads only; writes one JSON row per case.

    PYTHONPATH=. python research_notes/fullspine-rule6-calibration/calibrate_rule6.py OUT.json STUDY_FOLDER...

(run from the repository's root; each folder holds SPINEPS's ctgrid/vert.nii.gz and ctgrid/spine.nii.gz)
"""
import json
import os
import sys
from types import SimpleNamespace

import numpy as np

from holdings import fullspine_complete as C
from holdings import fullspine_facts as F

OVERREACH = (0.05, 0.1, 0.2, 0.3)
KEEP = (0.6, 0.7, 0.8, 0.9)


def take_near(other, body, share):
    """The part of other's body within share of its height from its end nearest body, and the rest."""
    centre, axis, _ = C.axis_between(body, other)
    position = C.along(other["world"], centre, axis)[0]
    near = position <= position.min() + share * (position.max() - position.min())
    return ({"world": other["world"][near], "points": other["points"][near]},
            {"world": other["world"][~near], "points": other["points"][~near]})


def joined(first, second):
    return {key: np.concatenate([first[key], second[key]]) for key in ("world", "points")}


def reading(body, other, column, high=None):
    numbers, reason = C.side_reading(body, other, column, high)
    return dict(numbers, refused=reason is not None, reason=reason)


def ratios(body, near, farther, column):
    """The height and step ratios body_check reads: body against near, its step against near's to
    farther (the next level inwards)."""
    centre, axis, step = C.axis_between(body, near)
    voxel = C.reach(column.cell, axis)
    tall = np.subtract(*C.extent(body, centre, axis)[::-1]) + voxel
    near_tall = np.subtract(*C.extent(near, centre, axis)[::-1]) + voxel
    out = {"height_ratio": float(tall / near_tall)}
    if farther is not None:
        out["step_ratio"] = float(step / C.axis_between(near, farther)[2])
    return out


def without_discs_between(column, first, second):
    """The column with every disc voxel between two bodies' centres, inside their cylinder, deleted."""
    centre, axis, distance = C.axis_between(first, second)
    radius = max(C.radius_of(first, centre, axis), C.radius_of(second, centre, axis))
    position, distance_from = C.along(column.discs["world"], centre, axis)
    keep = ~((distance_from <= radius) & (position > 0) & (position < distance))
    return {key: column.discs[key][keep] for key in ("world", "points")}


def study(folder, out):
    sid = os.path.basename(folder.rstrip("/"))
    grid, machine, _ = C.machine_levels(os.path.join(folder, "ctgrid", "vert.nii.gz"))
    _, corpus, disc, _ = C.subregions(os.path.join(folder, "ctgrid", "spine.nii.gz"))
    chain, sacrum, _, _ = C.chain_of(machine, grid.affine)
    atlas = {label for label in chain if F.VERSE_NAMES[label] == C.ATLAS}
    column = C.column_of(machine, corpus, disc, grid, chain, sacrum, atlas)
    names = column.names
    seq = [label for label in chain if C.usable(label, column)]
    base = {"id": sid}
    for direction, order in (("down", seq), ("up", seq[::-1])):
        for i in range(1, len(order)):
            v, n = order[i], order[i - 1]
            o = order[i + 1] if i + 1 < len(order) else None
            nn = order[i - 2] if i >= 2 else None
            bv, bn = column.bodies[v], column.bodies[n]
            row = dict(base, kind="one_inner", dir=direction, level=names[v], **reading(bv, bn, column))
            row.update(ratios(bv, bn, column.bodies[nn] if nn else None, column))
            out.append(row)
            if o is None:
                continue
            bo = column.bodies[o]
            out.append(dict(base, kind="one_outer", dir=direction, level=names[v], **reading(bv, bo, column)))
            merged = joined(bv, bo)
            row = dict(base, kind="discless", dir=direction, level=names[v] + "+" + names[o],
                       **ratios(merged, bn, column.bodies[nn] if nn else None, column))
            changed = SimpleNamespace(**vars(column))
            changed.discs = without_discs_between(column, bv, bo)
            row.update({"inner_" + key: value for key, value in reading(merged, bn, changed).items()})
            out.append(row)
            for share in OVERREACH:
                near, rest = take_near(bo, bv, share)
                out.append(dict(base, kind="overreach", share=share, dir=direction, level=names[v],
                                **reading(joined(bv, near), rest, column)))
            for keep in KEEP:
                kept, _ = take_near(bv, bn, keep)
                out.append(dict(base, kind="split_dropped", keep=keep, dir=direction, level=names[v],
                                **reading(kept, bo, column)))
    if sacrum is not None and seq:
        numbers, reason, against = C.sacrum_check(sacrum, seq[-1], column)
        out.append(dict(base, kind="sacrum", level=names[seq[-1]], refused=reason is not None, reason=reason,
                        against=against, **numbers))


if __name__ == "__main__":
    out = []
    for folder in sys.argv[2:]:
        study(folder, out)
        print(os.path.basename(folder.rstrip("/")), "done", len(out), flush=True)
        with open(sys.argv[1], "w") as f:
            json.dump(out, f)
