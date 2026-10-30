"""Build phantom L3s that are not in the cache, to read candidate A out of sample: the test
suite's Overhang and ThickSlices phantoms, tilts the cache does not hold, and the cache's own
configs drawn with the phantom moved by a fraction of a voxel (another phase of the lattice).
  held_out.py <out_dir> [<index> <count>]"""
import os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_cache as BC
from morphometry.tests import phantom as P

BC.PHANTOMS["overhang"] = dict(sap_x=19.0, sap_y=-10.0, facet=0.0, sap_thk=3.5, sap_len=14.0)
BC.LEANS["overhang"] = (0.0,)
X20, X3, X7 = ((1.0, 0.0, 0.0), 20.0), ((1.0, 0.0, 0.0), 3.0), ((1.0, 0.0, 0.0), 7.0)
SHIFTS = {"phaseA": (0.31, 0.47, 0.23), "phaseB": (0.11, 0.19, 0.83)}
CONFIGS = [
    ("thickslices", ("straight", 0.0, "x20", X20, 0.0, "thick"), None),
    ("overhang", ("overhang", 0.0, "suite18", ((1.0, 0.3, 0.0), 18.0), 7.0, "thin"), None),
]
for name, lean in (("straight", 5.0), ("pitched", 0.0)):
    for g, tilt, turn in (("x3", X3, 0.0), ("x7", X7, 3.0)):
        for sp in ("thin", "thick"):
            CONFIGS.append(("%s_lean%+.0f_%s_%s" % (name, lean, g, sp), (name, lean, g, tilt, turn, sp), None))
for ph in SHIFTS:
    for name, lean, g, tilt, sp in (("straight", 0.0, "x2", ((1.0, 0.0, 0.0), 2.0), "thin"),
                                    ("straight", 0.0, "x2", ((1.0, 0.0, 0.0), 2.0), "thick"),
                                    ("straight", 5.0, "aligned", ((1.0, 0.0, 0.0), 0.0), "thick")):
        CONFIGS.append(("%s_lean%+.0f_%s_%s_%s" % (name, lean, g, sp, ph), (name, lean, g, tilt, 0.0, sp), SHIFTS[ph]))

_straight = P.straight


def build(cfg, shift):
    if shift is None:
        return BC.build(cfg)
    def moved(levels, v=None, joint=None, tilt=((1.0, 0.3, 0.0), 18.0)):
        v = v or P.Vert()
        j = joint or P.Joint()
        return P.chain(levels, {lv: v for lv in levels}, {lv: j for lv in levels[1:]}, R0=P.rotation(*tilt), c0=shift)
    BC.P.straight = moved
    try:
        return BC.build(cfg)
    finally:
        BC.P.straight = _straight


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    todo = CONFIGS if len(sys.argv) < 4 else CONFIGS[int(sys.argv[2])::int(sys.argv[3])]
    for key, cfg, shift in todo:
        path = os.path.join(out, key + ".pkl")
        if os.path.exists(path):
            continue
        rec = build(cfg, shift)
        rec["shift"] = shift
        with open(path + ".tmp", "wb") as f:
            pickle.dump(rec, f)
        os.replace(path + ".tmp", path)
        print(key, "built", flush=True)
