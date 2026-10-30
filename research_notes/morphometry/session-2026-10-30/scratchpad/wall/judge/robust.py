"""One harness for every reader: the cached phantom L3s altered as a real mask may differ from a
clean digitisation, the same alterations and seeds for each reader.

  PYTHONPATH=<bordercall> python robust.py <out.json> [<index> <count>]

Each alteration keeps the wall's true slope (the phantom's lean, in the measured frame), so the
error is read against the same truth as score.py. The vertebra is rebuilt from the altered label:
its voxel list, its frame coordinates and its body (the same cut, connected_front at the canal's
wall line, the line itself held fixed). The canal's slabs, the frame and the wall line are not
re-read: an alteration of the wall would move the canal's anterior wall too, which is not
modelled. Phantoms only; no real mask is read.
"""
import copy
import importlib.util
import json
import math
import os
import pickle
import sys
import time
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)
sys.path.insert(0, os.path.join(WALL, "diag_limit"))
import score as S  # noqa: E402
import limit as L  # noqa: E402
from morphometry import anatomy as A, body as BODY  # noqa: E402
from scanimport import geometry as G  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location("m_" + os.path.basename(os.path.dirname(path)), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, name)


READERS = {
    "current": lambda v, B, xc: BODY.posterior_wall_slope(v, B, xc),
    "A": load(os.path.join(WALL, "cand_lattice", "cand.py"), "slope"),
    "A_plain": load(os.path.join(WALL, "cand_lattice", "cand.py"), "slope_plain"),
    "B": load(os.path.join(WALL, "cand_parting", "cand.py"), "slope"),
    "C": load(os.path.join(WALL, "cand_boundary", "cand.py"), "slope"),
}
for _n in ("A_trim", "A_bw", "A_lts", "A_lts_plain", "A_lts_det"):
    READERS[_n] = load(os.path.join(HERE, "variants.py"), _n)
READERS["proposed"] = load(os.path.join(HERE, "proposed.py"), "posterior_wall")
if os.environ.get("READERS"):
    READERS = {k: READERS[k] for k in os.environ["READERS"].split(",")}


def field(seed, sd, ell, n=64):
    """A smooth random displacement (mm) over (x, z) with Gaussian covariance of length ell."""
    r = np.random.default_rng(seed)
    k = r.normal(0.0, 1.0 / ell, size=(n, 2))
    ph = r.uniform(0, 2 * math.pi, n)

    def f(x, z):
        return sd * math.sqrt(2.0 / n) * np.cos(np.outer(x, k[:, 0]) + np.outer(z, k[:, 1]) + ph).sum(1)
    return f


TILT = {}


def altered(rec, name):
    v = rec["vert"]
    box, lo = v.mask_box()
    pad = 3
    box2 = np.zeros(tuple(np.array(box.shape) + 2 * pad), bool)
    box2[pad:-pad, pad:-pad, pad:-pad] = box
    lo2 = lo - pad
    ijk = np.argwhere(np.ones(box2.shape, bool)) + lo2
    q = v.frame.local(v.grid.world(ijk.astype(float)))
    tp = L.truth_plane(rec)
    w = q[:, 1] - (tp["a"] + tp["b"] * q[:, 2] + tp["c"] * q[:, 0])     # + in front of the wall
    B = v.body_pts
    xc = rec["xc"]
    strip = B[np.abs(B[:, 0] - xc) <= 3.0]
    z0, z1 = strip[:, 2].min(), strip[:, 2].max()
    zm, H = 0.5 * (z0 + z1), 0.5 * (z1 - z0)
    win = 0.6 * H
    dx, dz = q[:, 0] - xc, q[:, 2] - zm
    flat = box2.reshape(-1)
    seed = zlib.crc32(repr(rec["cfg"]).encode())
    step = max(v.fy, 0.5)
    if name == "notch_6x4x2":            # a basivertebral notch at mid-height
        flat[(np.abs(dx) <= 3) & (np.abs(dz) <= 2) & (w >= 0) & (w <= 2.0)] = False
    elif name == "notch_5x6x4":          # a deeper basivertebral foramen
        flat[(np.abs(dx) <= 2.5) & (np.abs(dz) <= 3) & (w >= 0) & (w <= 4.0)] = False
    elif name == "notch_up_6x4x2":       # the notch half-way to the window's top
        flat[(np.abs(dx) <= 3) & (np.abs(dz - 0.5 * win) <= 2) & (w >= 0) & (w <= 2.0)] = False
    elif name == "lip_top_1.5":          # a lip 1.5 mm proud from 3 mm inside the window's top up
        flat[(np.abs(dx) <= 8) & (dz >= win - 3) & (dz <= H + 2) & (w < 0) & (w >= -1.5)] = True
    elif name == "osteophyte_end_3":     # a posterior osteophyte at the upper end-plate, outside the window
        flat[(np.abs(dx) <= 8) & (dz >= win + 1.5) & (dz <= H + 2) & (w < 0) & (w >= -3.0)] = True
    elif name == "scallop_axial_1":      # the wall recessed 1 mm at the midline, a cosine across 16 mm
        prof = 1.0 * np.cos(np.clip(np.pi * dx / 16.0, -np.pi / 2, np.pi / 2)) ** 2
        flat[(np.abs(dx) <= 8) & (w >= 0) & (w < prof) & (np.abs(dz) <= H + 1)] = False
    elif name == "bow_sagittal_0.8":     # the wall concave along z, 0.8 mm deep at mid-height
        bow = 0.8 * np.clip(1.0 - (dz / H) ** 2, 0.0, None)
        flat[(np.abs(dx) <= 9) & (w >= 0) & (w < bow)] = False
    elif name == "holes":                # six voids of 1 mm radius 0.8 to 3 mm inside the wall
        r = np.random.default_rng(seed)
        for _ in range(6):
            c = np.array([r.uniform(-5, 5), r.uniform(0.8, 3.0), r.uniform(-win, win)])
            d2 = (dx - c[0]) ** 2 + (w - c[1]) ** 2 + (dz - c[2]) ** 2
            flat[d2 <= 1.0] = False
    elif name.startswith("ragged_"):    # a segmenter's edge: the wall moved by a smooth field
        sd, ell = {"ragged_0.3_3": (0.3, 3.0), "ragged_0.5_4": (0.5, 4.0)}[name]
        f = field(seed, sd, ell)
        TILT.clear()
        for half in (3.0, 6.0):           # the field's own lean over a reader's region: no reader of the label can tell it from the wall
            gx, gz = np.meshgrid(np.linspace(-half, half, 25), np.linspace(-win, win, 81))
            gx, gz = gx.ravel(), gz.ravel()
            X = np.column_stack([np.ones(len(gx)), gz, gx, gx * gx])
            bf = np.linalg.lstsq(X, -f(gx, gz), rcond=None)[0][1]
            TILT["tilt%d" % half] = math.degrees(math.atan(tp["b"] + bf)) - math.degrees(math.atan(tp["b"]))
        zone = (np.abs(w) <= 2.5) & (np.abs(dx) <= 9) & (np.abs(dz) <= H + 1)
        qs = q[zone].copy()
        qs[:, 1] -= f(dx[zone], dz[zone])
        flat[zone] = L.true_inside(rec, qs)
    elif name == "flips_0.2":            # independent flips of the wall's boundary layer
        r = np.random.default_rng(seed)
        zone = (np.abs(w) <= 0.5 * step + 0.4) & (np.abs(dx) <= 9) & (np.abs(dz) <= H + 1)
        flip = zone & (r.uniform(size=len(flat)) < 0.2)
        flat[flip] = ~flat[flip]
    elif name == "cut_top_30":           # the volume's last slice falls 30 per cent below the body's top
        a = int(np.argmax(np.abs(v.grid.axes.T @ v.frame.ez)))
        up = 1 if v.grid.axes[:, a] @ v.frame.ez > 0 else -1
        k = ijk[:, a] * up
        ref = (np.abs(dx) <= 2) & (np.abs(w) <= 2) & (np.abs(dz - 0.4 * H) <= 0.6 * max(v.fz, 1.0))
        flat[k > np.median(k[ref])] = False
    else:
        raise KeyError(name)
    v2 = copy.copy(v)
    v2._box = (box2, lo2)
    v2.idx = np.argwhere(box2) + lo2
    v2.loc = v.frame.local(v.grid.world(v2.idx.astype(float)))
    v2.body = G.connected_front(v2.idx, A.square_to_wall(v2, v2.loc), v.wall_y0, v.grid.shape)
    v2.touching = np.zeros(len(v2.idx), bool)
    return v2


ALTERATIONS = ["clean", "notch_6x4x2", "notch_5x6x4", "notch_up_6x4x2", "lip_top_1.5", "osteophyte_end_3",
               "scallop_axial_1", "bow_sagittal_0.8", "holes", "ragged_0.3_3", "ragged_0.5_4", "flips_0.2",
               "cut_top_30"]


def main():
    out = sys.argv[1]
    keys = sorted(f[:-4] for f in os.listdir(os.path.join(WALL, "cache")) if f.endswith(".pkl"))
    if len(sys.argv) > 3:
        i, n = int(sys.argv[2]), int(sys.argv[3])
        keys = keys[i::n]
    rows = []
    for key in keys:
        rec = pickle.load(open(os.path.join(WALL, "cache", key + ".pkl"), "rb"))
        t = S.wall_truth_in_frame(rec)
        for alt in (os.environ["ALTS"].split(",") if os.environ.get("ALTS") else ALTERATIONS):
            v = rec["vert"] if alt == "clean" else altered(rec, alt)
            B = v.body_pts
            xc = rec["xc"] if alt == "clean" else 0.5 * (B[:, 0].min() + B[:, 0].max())
            row = {"key": key, "alt": alt, "spacing": rec["cfg"][5], "grid": rec["cfg"][2], "truth": t}
            if alt.startswith("ragged_"):
                row.update(TILT)
            for rn, fn in READERS.items():
                t0 = time.perf_counter()
                try:
                    got = fn(v, B, xc)
                except Exception as e:  # recorded, not hidden
                    got = (float("nan"), {"why": "raised " + repr(e)})
                dt = time.perf_counter() - t0
                info = {}
                if isinstance(got, tuple):
                    got, info = got
                deg = math.degrees(math.atan(got)) if got is not None and np.isfinite(got) else float("nan")
                row[rn] = deg - t
                row[rn + "_why"] = str(info.get("why", ""))
                row[rn + "_s"] = dt
                for k in ("free_deg", "width_deg", "range_deg", "dropped", "trimmed", "across", "synth_free_deg", "parted", "fitted_deg", "rms_over_step", "edges"):
                    if k in info:
                        row[rn + "_" + k] = float(info[k])
            rows.append(row)
            print("%-36s %-18s " % (key, alt) + " ".join("%s %+6.2f" % (rn, row[rn]) for rn in READERS), flush=True)
    with open(out, "w") as f:
        json.dump(rows, f, indent=0, default=float)


if __name__ == "__main__":
    main()
