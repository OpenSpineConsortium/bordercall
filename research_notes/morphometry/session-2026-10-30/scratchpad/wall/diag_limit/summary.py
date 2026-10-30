"""Tables of the information limit by grid and spacing, from limit.py's JSON.

  python summary.py limit.json
"""
import json
import sys

import numpy as np

GRIDS = ["aligned", "x2", "x5", "x10", "y12", "suite18", "t25"]


def fmt(x):
    return "%6.2f" % x


def table(rows, fit, title):
    print("\n== %s (fit %s): per grid, spacing; width = degrees of slope the mask leaves free" % (title, fit))
    print("%-8s %-5s %3s | %-17s | %-6s | %-6s | %-13s | %-13s | %-13s | %-11s | %-15s" % (
        "grid", "sp", "n", "width min/med/max", "parts", "t in", "maxmarg|err| max", "mid |err| max",
        "worst-any max", "mm_pos med", "reader in / unc in"))
    for sp in ("thin", "thick"):
        for g in GRIDS:
            sel = [r for r in rows if r["cfg"][2] == g and r["cfg"][5] == sp]
            if not sel:
                continue
            f = [r["fits"][fit] for r in sel]
            w = np.array([x["width_deg"] for x in f])
            parts = sum(x["parts"] for x in f)
            tin = sum(x["truth_inside"] for x in f)
            mm = np.array([abs(x["mm_err"]) for x in f])
            mid = np.array([abs(x["mid_err"]) for x in f])
            worst = np.array([x["worst_any_reader"] for x in f])
            pos = np.array([x["mm_pos"] for x in f])
            rin = sum(x["lo_deg"] - 1e-6 <= r["reader_deg"] <= x["hi_deg"] + 1e-6 for x, r in zip(f, sel))
            uin = sum(x["lo_deg"] - 1e-6 <= r["reader_uncut_deg"] <= x["hi_deg"] + 1e-6 for x, r in zip(f, sel))
            print("%-8s %-5s %3d | %5.2f %5.2f %5.2f | %3d/%-2d | %3d/%-2d | %5.2f        | %5.2f        | %5.2f        | %5.2f       | %2d/%-2d  %2d/%-2d" % (
                g, sp, len(sel), w.min(), np.median(w), w.max(), parts, len(sel), tin, len(sel), mm.max(), mid.max(),
                worst.max(), np.nanmedian(pos), rin, len(sel), uin, len(sel)))


def readers(rows):
    print("\n== readers' |error| against the frame-relative truth, degrees, max per grid and spacing")
    print("%-8s %-5s | %-8s %-8s %-8s %-8s %-8s | %s" % ("grid", "sp", "current", "uncut", "canal", "maxmarg", "mid",
                                                         "bone cut off the body in the band (max count)"))
    for sp in ("thin", "thick"):
        for g in GRIDS:
            sel = [r for r in rows if r["cfg"][2] == g and r["cfg"][5] == sp]
            if not sel:
                continue
            t = np.array([r["truth_dir_deg"] for r in sel])
            cur = np.abs(np.array([r["reader_deg"] for r in sel]) - t)
            unc = np.abs(np.array([r["reader_uncut_deg"] for r in sel]) - t)
            can = np.abs(np.array([r["canal_line_deg"] for r in sel]) - t)
            mm = np.array([abs(r["fits"]["mask_curved"]["mm_err"]) for r in sel])
            mid = np.array([abs(r["fits"]["mask_curved"]["mid_err"]) for r in sel])
            bnb = max(r["bone_not_body"] for r in sel)
            print("%-8s %-5s | %s   %s   %s   %s   %s | %d" % (g, sp, fmt(cur.max()), fmt(unc.max()), fmt(can.max()),
                                                           fmt(mm.max()), fmt(mid.max()), bnb))


def extras(rows):
    print("\n== width of the curved family's range (degrees, median / max) over larger regions")
    keys = ["mask_curved", "mask_curved_x3_h80", "mask_curved_x6_h60", "mask_curved_x6_h80"]
    print("%-8s %-5s | %s" % ("grid", "sp", " | ".join("%-18s" % k.replace("mask_curved", "c") for k in keys)))
    for sp in ("thin", "thick"):
        for g in GRIDS:
            sel = [r for r in rows if r["cfg"][2] == g and r["cfg"][5] == sp]
            if not sel:
                continue
            cells = []
            for k in keys:
                w = np.array([r["fits"][k]["width_deg"] for r in sel])
                tin = sum(r["fits"][k]["truth_inside"] for r in sel)
                cells.append("%5.2f %5.2f in %2d/%-2d" % (np.median(w), w.max(), tin, len(sel)))
            print("%-8s %-5s | %s" % (g, sp, " | ".join(cells)))


def main():
    rows = json.load(open(sys.argv[1]))
    print("%d configs" % len(rows))
    chk = max(abs(r["reader_deg"] - r["reader_check_deg"]) for r in rows)
    print("reader recomputed against the cache's wall_now: max diff %.2e deg" % chk)
    print("label against the phantom's own inside test, centres that differ: max %d" % max(r["label_vs_true_inside"] for r in rows))
    print("frame-relative truth by direction vs by the plane's dy/dz at fixed x: max diff %.4f deg" % max(
        abs(r["truth_dir_deg"] - r["truth_plane_deg"]) for r in rows))
    print("true plane: air centres ahead of it up to %.3f mm, bone behind it up to %.3f mm (the wall's curve across x)" % (
        max(r["true_plane_air_ahead_mm"] for r in rows), max(r["true_plane_bone_behind_mm"] for r in rows)))
    for fit, title in (("mask_line", "line y = a + b z"), ("mask_plane", "plane y = a + b z + c x"),
                       ("mask_curved", "curved y = a + b z + c x + d x^2"),
                       ("body_curved", "curved, body label vs air, cut-off bone left out"),
                       ("cut_curved", "curved, body label vs all else (what the reader is handed)")):
        table(rows, fit, title)
    readers(rows)
    extras(rows)


if __name__ == "__main__":
    main()
