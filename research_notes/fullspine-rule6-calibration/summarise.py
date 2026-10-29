"""The counts rule 6's calibration rests on, from calibrate_rule6.py's readings: per group of studies
(VerSe's adults, TotalSegmentator's children), how many readings of a body as it stands the disc
reading refuses and how far they range, how many altered bodies it refuses at each share, how the
height and step ratios of single bodies and of merged pairs fall against MERGED, and the sacrum's
disc runs.

    PYTHONPATH=. python research_notes/fullspine-rule6-calibration/summarise.py READINGS.json[.gz]
"""
import gzip
import json
import sys
from collections import defaultdict

from holdings import fullspine_complete as C


def group(row):
    return "verse" if row["id"].startswith("verse") else "totalsegmentator"


def as_stands(rows):
    out = {}
    for kind in ("one_inner", "one_outer"):
        part = [r for r in rows if r["kind"] == kind]
        found = [r for r in part if r.get("discs") == 1]
        out[kind] = {"readings": len(part), "refused": sum(r["refused"] for r in part),
                     "one_disc": len(found),
                     "max_overreach_share": max((r["overreach_share"] for r in found), default=None),
                     "gap_mm": [min((r["gap_mm"] for r in found), default=None),
                                max((r["gap_mm"] for r in found), default=None)],
                     "reasons": sorted({r["reason"].split(":")[0].split(",")[0] for r in part if r["refused"]})}
    return out


def altered(rows, kind, key):
    counts = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["kind"] == kind:
            counts[r[key]][0] += r["refused"]
            counts[r[key]][1] += 1
    return {str(k): "%d of %d" % tuple(v) for k, v in sorted(counts.items())}


def merged(rows):
    singles = [r for r in rows if r["kind"] == "one_inner" and "step_ratio" in r]
    pairs = [r for r in rows if r["kind"] == "discless" and "step_ratio" in r]
    high, step = C.MERGED
    return {
        "singles": len(singles),
        "singles_over_both": sum(r["height_ratio"] > high and r["step_ratio"] > step for r in singles),
        "max_step_where_height_over": max((r["step_ratio"] for r in singles if r["height_ratio"] > high), default=None),
        "max_height_where_step_over": max((r["height_ratio"] for r in singles if r["step_ratio"] > step), default=None),
        "pairs": len(pairs),
        "pairs_over_both": sum(r["height_ratio"] > high and r["step_ratio"] > step for r in pairs),
        "min_pair_height": min((r["height_ratio"] for r in pairs), default=None),
        "min_pair_step": min((r["step_ratio"] for r in pairs), default=None),
    }


def sacra(rows):
    return [{"id": r["id"], "above": r["level"], "refused": r["refused"], "reason": r["reason"],
             "discs": [(d["start_mm"], d["end_mm"], d["voxels"]) for d in r["discs"]]}
            for r in rows if r["kind"] == "sacrum"]


def main(path):
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        rows = json.load(f)
    out = {}
    for name in ("verse", "totalsegmentator"):
        part = [r for r in rows if group(r) == name]
        out[name] = {"studies": sorted({r["id"] for r in part}), "as_stands": as_stands(part),
                     "overreach": altered(part, "overreach", "share"),
                     "split_dropped": altered(part, "split_dropped", "keep"),
                     "merged": merged(part), "sacrum": sacra(part)}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main(sys.argv[1])
