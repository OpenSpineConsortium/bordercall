# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/recorded_counts.py, 2026-10-28.
# Changed: the absolute paths became the arguments below, and its last line, which called
# the median of Panjabi's worth one over the 675 cells where his series is alone while taking it
# over all 704, now gives both.
# On 2026-10-29 'skeleton' joined the cadaveric words, for the corrected tables' "dry skeletons", and --sum-sexes
# gives a series split by sex the sum of its sexes' counts in a cell, since spine-program #241 made each sex's row
# carry its own count, where the copy's carried the whole sample in each (the copy's counts are unchanged by both).
#     python3 -I verify/recorded_counts.py SYNTHETIC_SPINE_DATA BORDERCALL [--sum-sexes]
"""Recorded specimen counts per pool cell (synthetic_spine) and what they are worth at f = 0."""
import csv, collections, os, re, sys
sys.path.insert(0, sys.argv[2])
import numpy as np
from schwingcheck import measures as MS, LEVELS

SS = os.path.join(sys.argv[1], '')
CAD = ('cadaver', 'dry bone', 'post-mortem', 'skeleton')
MAP = {'endplate': 'endplate', 'h_post': 'h_post', 'canal_w': 'canal_w', 'canal_ap': 'canal_ap',
       'pedicle': 'pedicle', 'PDW': 'pedicle'}

def count(n):
    """The largest whole number in the n field, or None."""
    nums = [int(x) for x in re.findall(r'\d+', n or '')]
    return max(nums) if nums else None

def iscad(cohort, modality):
    text = (cohort + ' ' + modality).lower()
    return any(k in text for k in CAD)

SUM_SEXES = '--sum-sexes' in sys.argv
sexes = collections.defaultdict(dict)      # (archive key, level, series) -> {sex: n}
cells = collections.defaultdict(dict)       # (archive key, level) -> {series: (cadaveric, n)}
for r in csv.DictReader(open(SS + 'level_references.csv')):
    if r['measure'] in MAP:
        key = (MAP[r['measure']], r['level'])
        n = count(r['n'])
        if SUM_SEXES:
            sexes[key + (r['series'],)][r['sex']] = n
            known = [m for m in sexes[key + (r['series'],)].values() if m is not None]
            n = sum(known) if known else None
        cells[key][r['series']] = (iscad(r['cohort'], r['modality']), n)
rows = [l for l in open(SS + 'pedicle_width_references.csv') if not l.startswith('#')]
for r in csv.DictReader(rows):
    s = r['series'] + ' ' + r['year']
    if s.startswith('Panjabi'):
        s = 'Panjabi 1992'
    cells[(MAP[r['measure']], r['level'])][s] = (iscad(r['cohort'], r['modality']), count(r['n']))

pool = MS.pool()
mu, sd = MS.arrays(pool)
e = MS.errors(pool)
keys = [MS.archive_key(m) for m in pool]
total = len(pool) * len(LEVELS)
others = 0
alone = np.ones((len(pool), len(LEVELS)), bool)
print('cell | series | cadaveric series | cadaveric n (blank n counted 0) | worth in scans at f=0 | all-series n')
best = []
for i, k in enumerate(keys):
    for j, lev in enumerate(LEVELS):
        d = cells.get((k, lev), {'Panjabi 1992': (True, 12)})
        if 'Panjabi 1992' not in d:
            d = dict(d); d['Panjabi 1992'] = (True, 12)
        if len(d) > 1:
            others += 1
            alone[i, j] = False
            ncad = sum(n or 0 for c, n in d.values() if c)
            nall = sum(n or 0 for c, n in d.values())
            r = 1 + (e[i] / sd[i, j]) ** 2
            best.append((ncad * r, k, lev, ncad))
            print(k, lev, len(d), sum(1 for c, n in d.values() if c), ncad,
                  round(ncad * r), nall, 'blank n:', [s for s, (c, n) in d.items() if n is None])
print('cells', total, 'with a series beside Panjabi', others, 'Panjabi alone', total - others)
print('largest worth at f=0 of the recorded cadaveric counts:', max(best))
r_all = 1 + (e[:, None] / sd) ** 2
print('worth of Panjabi 12 alone at f=0, median over all %d cells:' % r_all.size, np.median(12 * r_all))
print('worth of Panjabi 12 alone at f=0, median over the %d cells where his is the only series:' % alone.sum(),
      np.median(12 * r_all[alone]))
