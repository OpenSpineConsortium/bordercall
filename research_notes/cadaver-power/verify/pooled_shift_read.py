# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/median-shift-check/analyse.py,
# 2026-10-28. Changed: bordercall's checkout is the first argument in place of a fixed path, and the
# .npz files follow it. It scores nothing: it reads the per-field results that pooled_shift.py saved and
# prints them the way part_b() summarises a table. It also prints each table's own row (share named
# exactly, share answered at 0.99, precision of those answers), which the original did not, so that
# summarise_runs.py can set these tables beside the others. Those .npz files (1.0 to 1.5 MB each) are not
# in this folder; they are in the reviewer's folder, and pooled_shift.py makes them again. Run with -B so
# that importing bordercall's score module writes nothing into the checkout.
#     python3 -I -B verify/pooled_shift_read.py BORDERCALL R/fresh_w1.npz R/fresh_w3.npz R/fresh_w9.npz > verify/pooled_shift_read.log
"""Summaries the way part_b() makes them, plus paired median-vs-pooled differences per table."""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from schwingcheck import score as S
CLAIM = 0.99
def rates(hit, top, col):
    said = top >= CLAIM
    inv = np.unique(col, return_inverse=True)[1]
    wrong = np.bincount(inv, weights=said & ~hit); answered = np.bincount(inv, weights=said)
    return dict(exact=hit.mean(), prec=hit[said].mean() if said.any() else np.nan, ans=said.mean(),
                prec_se=S.ratio_se(wrong, answered), n_ans=int(said.sum()), wrong=int(wrong.sum()))
for path in sys.argv[2:]:
    d = np.load(path)
    names, draws, hit, top, col = d["names"], d["draws"], d["hit"], d["top"], d["col"]
    ref = hit[list(names).index("p2000")]
    print("%s  width %d  pooled %.4f  fields %d" % (path.rsplit("/", 1)[1], d["width"], d["pooled"], hit.shape[1]))
    for nm in dict.fromkeys(names):
        idx = [i for i, n in enumerate(names) if n == nm]
        rows = [rates(hit[i], top[i], col) for i in idx]
        m2 = [(hit[i].astype(float) - ref).mean() for i in idx]
        print("  %-13s tables %d  exact %.2f%%  vs2000 %+.2f (table sd %.2f)  prec@.99 %.2f%%  worst %.2f%%  answered %.1f%%  wrong/answered %s"
              % (nm, len(idx), 100 * np.mean([r["exact"] for r in rows]), 100 * np.mean(m2), 100 * np.std(m2, ddof=1) if len(m2) > 1 else 0,
                 100 * np.mean([r["prec"] for r in rows]), 100 * np.min([r["prec"] for r in rows]),
                 100 * np.mean([r["ans"] for r in rows]), [(r["wrong"], r["n_ans"]) for r in rows]))
        if nm not in ("true", "p2000"):
            for i, r in zip(idx, rows):
                print("    w%d:%s %d exact %.4f ans %.4f prec %.4f" % (d["width"], nm, draws[i], r["exact"], r["ans"], r["prec"]))
    for base in ("note", "fresh"):
        a = [i for i, n in enumerate(names) if n == base + "-median"]; b = [i for i, n in enumerate(names) if n == base + "-pooled"]
        if not a: continue
        dd = [(hit[j].astype(float) - hit[i].astype(float)) for i, j in zip(a, b)]
        per = [100 * x.mean() for x in dd]
        ses = [100 * S.clustered_se(x, col) for x in dd]
        # pooled-over-tables precision: total wrong / total answered
        tot = lambda ids: (sum(int(((top[i] >= CLAIM) & ~hit[i]).sum()) for i in ids), sum(int((top[i] >= CLAIM).sum()) for i in ids))
        wa, na = tot(a); wb, nb = tot(b)
        print("  %s: pooled minus median, per table %s points (column-clustered SE %s); mean %+.2f, across-table SE %.2f"
              % (base, ["%+.2f" % x for x in per], ["%.2f" % x for x in ses], np.mean(per), np.std(per, ddof=1) / np.sqrt(len(per)) if len(per) > 1 else 0))
        print("  %s: errors among 0.99 answers, all tables together: median %d/%d = %.2f%% right, pooled %d/%d = %.2f%% right"
              % (base, wa, na, 100 * (1 - wa / na), wb, nb, 100 * (1 - wb / nb)))
