# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/median-shift-check/pooled_shift.py,
# 2026-10-28. Changed: bordercall's checkout is the first argument in place of a fixed path, and it imports
# the note's cadaver_power.py from the folder above in place of the reviewer's copy of it (cp_orig.py, the
# same file before this note's edits, whose tables() and DISAGREEMENTS this note left as they were). Not rerun
# for the note: the reviewer ran it as below for 3 bodies, and likewise for 9 bodies with 8 fresh tables and for
# 1 body with 4, and its .npz outputs (fresh_w1, fresh_w3 and fresh_w9) are read by pooled_shift_read.py.
#     python3 -I -B verify/pooled_shift.py BORDERCALL 3 0.7355 8 R/fresh_w3.npz [processes]
"""The note's seven-r0 tables (shift 0.57, level-by-level 0) against the same tables with the shift
scaled to the df-pooled value, on the note's 300 columns, nominal rule. Common random numbers: the
pooled table is mu + (tmu - mu) * (pooled / 0.57), which is exact because the level-by-level part
of seven-r0 is zero. Extra fresh tables (seed given) are drawn the way tables() draws them.

    python3 -I -B pooled_shift.py BORDERCALL WIDTH POOLED N_FRESH OUT.npz [processes]
"""
import importlib.util, math, multiprocessing, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("cadaver_power", os.path.join(HERE, "cadaver_power.py"))
CP = importlib.util.module_from_spec(spec); spec.loader.exec_module(CP)
LEVELS, C, MS, R, S = CP.load(sys.argv[1])
width, pooled, n_fresh, out = int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
procs = int(sys.argv[6]) if len(sys.argv) > 6 else 1
pool = MS.select(MS.SPINEPS_7)
keys = [MS.archive_key(m) for m in pool]
cols = C.draw_columns(MS.reference(pool), ["typical"], CP.COLUMN_SEED, 300, keys,
                      noise_mm=MS.errors(pool), power=MS.powers(pool))
tabs = CP.tables(MS, C, LEVELS, pool, False)
mu, sd = MS.arrays(pool)
region = np.array(["CTL".index(name[0]) for name in LEVELS])
sel = {"true": [t for t in tabs if t[0] == "true"][0],
       "p2000": [t for t in tabs if t[0] == "people-2000" and t[1] == "nominal" and t[2] == 0][0]}
r0 = [t for t in tabs if t[0] == "seven-r0" and t[1] == "nominal"]
assert len(r0) == 4 and r0[0][5]["shift"] == 0.57 and r0[0][5]["level_by_level"] == 0.0
mine = []
for t in r0:
    d = (t[3] - mu) / sd                         # = 0.57 * z[:, region]
    # level-by-level part zero: constant within a measure and region
    for g in range(3):
        blk = d[:, region == g]
        assert np.allclose(blk, blk[:, :1]), "not a pure shift"
    mine.append(("note-median", t[2], t[3]))
    mine.append(("note-pooled", t[2], mu + (t[3] - mu) * (pooled / 0.57)))
rng = np.random.default_rng(9090)
for k in range(n_fresh):
    z = rng.normal(size=(mu.shape[0], 3))
    z[:, 2] = 0.7 * z[:, 1] + math.sqrt(1 - 0.49) * z[:, 2]
    mine.append(("fresh-median", k, mu + sd * (0.57 * z[:, region])))
    mine.append(("fresh-pooled", k, mu + sd * (pooled * z[:, region])))
jobs = [("true", 0, sel["true"][3]), ("p2000", 0, sel["p2000"][3])] + mine
SDS = {"true": sel["true"][4], "p2000": sel["p2000"][4]}
noise, power = MS.errors(pool), MS.powers(pool)
def run(i):
    from threadpoolctl import threadpool_limits
    name, draw, tmu = jobs[i]
    tsd = SDS.get(name, sd)                      # every disagreement table keeps the true SD, as tables() does (nominal)
    offsets = np.arange(width)
    X, start, col = C.fields(cols.values, offsets)
    with threadpool_limits(1):
        post = R.name(X, offsets, tmu, tsd, R.SYNTH, noise=noise, power=power)["all"]
    return i, post.argmax(1) == start, post.max(1), col
t0 = time.time()
res = {}
with multiprocessing.get_context("fork").Pool(procs) as p:
    for i, hit, top, col in p.imap_unordered(run, range(len(jobs))):
        res[i] = (hit, top, col)
        print("  %d of %d, %.0f s" % (len(res), len(jobs), time.time() - t0), flush=True)
np.savez(out, names=np.array([j[0] for j in jobs]), draws=np.array([j[1] for j in jobs]),
         hit=np.array([res[i][0] for i in range(len(jobs))]), top=np.array([res[i][1] for i in range(len(jobs))]),
         col=res[0][2], width=width, pooled=pooled)
print("saved", out, "%.0f s" % (time.time() - t0))
