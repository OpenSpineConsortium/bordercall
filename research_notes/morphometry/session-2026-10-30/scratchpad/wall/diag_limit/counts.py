"""Totals over the cache from limit.json: where the readers fall against the mask's range."""
import json
import sys

import numpy as np

rows = json.load(open(sys.argv[1]))


def inside(x, f):
    return f["lo_deg"] - 1e-6 <= x <= f["hi_deg"] + 1e-6


for sp in ("thin", "thick", None):
    sel = [r for r in rows if sp is None or r["cfg"][5] == sp]
    n = len(sel)
    cu = [r["fits"]["mask_curved"] for r in sel]
    print("== %s: %d configs" % (sp or "all", n))
    print("  curved range holds the truth: %d/%d; line parts %d, plane parts %d, curved parts %d" % (
        sum(f["truth_inside"] for f in cu), n, sum(r["fits"]["mask_line"]["parts"] for r in sel),
        sum(r["fits"]["mask_plane"]["parts"] for r in sel), sum(f["parts"] for f in cu)))
    print("  line range holds the truth %d/%d, plane %d/%d" % (
        sum(r["fits"]["mask_line"]["truth_inside"] for r in sel), n, sum(r["fits"]["mask_plane"]["truth_inside"] for r in sel), n))
    nonpart = [-r["fits"][k]["margin"] for r in sel for k in ("mask_line", "mask_plane") if not r["fits"][k]["parts"]]
    if nonpart:
        print("  line/plane misfit where they part nothing: max %.3f mm median %.3f mm" % (max(nonpart), np.median(nonpart)))
    print("  current reader outside the curved range: %d/%d; reader on the uncut points outside: %d/%d" % (
        sum(not inside(r["reader_deg"], f) for r, f in zip(sel, cu)), n,
        sum(not inside(r["reader_uncut_deg"], f) for r, f in zip(sel, cu)), n))
    print("  canal line (anatomy.wall_slope) outside the curved range: %d/%d" % (
        sum(not inside(r["canal_line_deg"], f) for r, f in zip(sel, cu)), n))
    cut = [r for r in sel if r["bone_not_body"] > 0]
    print("  body cut takes bone off the band: %d/%d configs (max %d centres)" % (len(cut), n, max([r["bone_not_body"] for r in sel])))
    print("    of these the reader within 0.3 deg of the canal line: %d; cut range excludes truth in all configs: %d/%d" % (
        sum(abs(r["reader_deg"] - r["canal_line_deg"]) < 0.3 for r in cut), sum(not r["fits"]["cut_curved"]["truth_inside"] for r in sel), n))
    t = np.array([r["truth_dir_deg"] for r in sel])
    e_cur = np.abs(np.array([r["reader_deg"] for r in sel]) - t)
    e_unc = np.abs(np.array([r["reader_uncut_deg"] for r in sel]) - t)
    e_mm = np.abs(np.array([f["mm_err"] for f in cu]))
    e_mid = np.abs(np.array([f["mid_err"] for f in cu]))
    half = np.array([0.5 * f["width_deg"] for f in cu])
    print("  |err| max/median: current %.2f/%.2f  uncut %.2f/%.2f  max-margin curved %.2f/%.2f  range middle %.2f/%.2f" % (
        e_cur.max(), np.median(e_cur), e_unc.max(), np.median(e_unc), e_mm.max(), np.median(e_mm), e_mid.max(), np.median(e_mid)))
    print("  half-width of the curved range (the least worst case any reader of this region can promise): max %.2f median %.2f" % (
        half.max(), np.median(half)))
    print("  current |err| above that half-width: %d/%d" % ((e_cur > half + 1e-6).sum(), n))
    for k in ("mask_curved", "mask_curved_x3_h80", "mask_curved_x6_h60", "mask_curved_x6_h80"):
        w = np.array([r["fits"][k]["width_deg"] for r in sel])
        mm = np.abs(np.array([r["fits"][k]["mm_err"] for r in sel]))
        print("  %-20s width max %.2f median %.2f; max-margin |err| max %.2f median %.2f; truth in %d/%d" % (
            k, w.max(), np.median(w), mm.max(), np.median(mm), sum(r["fits"][k]["truth_inside"] for r in sel), n))
