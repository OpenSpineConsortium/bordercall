"""How the lattice's freedom (the LP range where the mask parts, and the synthetic range of a clean
digitisation of the fitted surface, which exists on any mask) relates to the error of A_lts and
A_lts_plain, per spacing and alteration."""
import json, sys
import numpy as np
rows = json.load(open('var_0.json')) + json.load(open('var_1.json'))
def show(sel, rn, label):
    e = np.array([abs(r[rn]) for r in sel]); s = np.array([r.get(rn + '_synth_free_deg', np.nan) for r in sel])
    f = np.array([r.get(rn + '_free_deg', np.nan) for r in sel]); p = np.array([r.get(rn + '_parted', 0) for r in sel])
    ok = np.isfinite(e) & np.isfinite(s)
    print("  %-28s n %3d parted %3d | synth width med %.2f max %.2f | err<=synth/2 %3d err<=synth %3d | max err where synth<=2: %.2f, <=4: %.2f, >4: %.2f (n %d)" % (
        label, ok.sum(), int(np.nansum(p)), np.median(s[ok]), s[ok].max(), (e[ok] <= s[ok] / 2).sum(), (e[ok] <= s[ok]).sum(),
        e[ok & (s <= 2)].max() if (ok & (s <= 2)).any() else np.nan, e[ok & (s <= 4)].max() if (ok & (s <= 4)).any() else np.nan,
        e[ok & (s > 4)].max() if (ok & (s > 4)).any() else np.nan, (ok & (s > 4)).sum()))
    both = ok & np.isfinite(f)
    if both.any():
        print("  %-28s where the mask parts: LP width med %.2f, synth-LP width diff med %.2f max %.2f" % ("", np.median(f[both]), np.median(np.abs(s[both] - f[both])), np.abs(s[both] - f[both]).max()))
for sp in ("thin", "thick"):
    print("==", sp)
    for alt in ("clean", "notch_6x4x2", "notch_up_6x4x2", "holes", "flips_0.2", "scallop_axial_1", "bow_sagittal_0.8", "cut_top_30", "ragged_0.3_3"):
        for rn in ("A_lts", "A_lts_plain"):
            show([r for r in rows if r['spacing'] == sp and r['alt'] == alt], rn, alt + " " + rn)
