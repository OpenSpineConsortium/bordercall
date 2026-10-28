# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/series_totals.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below.
#     python3 -I verify/series_totals.py SYNTHETIC_SPINE_DATA
"""Every distinct series in synthetic_spine's two tables, cadaveric or not, with its recorded n."""
import csv, os, re, sys
SS = os.path.join(sys.argv[1], '')
CAD = ('cadaver', 'dry bone', 'post-mortem')
def count(n):
    nums = [int(x) for x in re.findall(r'\d+', n or '')]
    return max(nums) if nums else None
series = {}
for r in csv.DictReader(open(SS + 'level_references.csv')):
    series.setdefault(r['series'], (r['cohort'], r['modality'], r['n']))
rows = [l for l in open(SS + 'pedicle_width_references.csv') if not l.startswith('#')]
for r in csv.DictReader(rows):
    name = 'Panjabi 1992' if r['series'] == 'Panjabi' else r['series'] + ' ' + r['year']
    series.setdefault(name, (r['cohort'], r['modality'], r['n']))
cad = {s: v for s, v in series.items() if any(k in (v[0] + ' ' + v[1]).lower() for k in CAD)}
print('distinct series', len(series), 'cadaveric', len(cad))
for s, v in cad.items():
    print('  ', s, v)
print('recorded cadaveric n, each series once:', sum(count(v[2]) or 0 for v in cad.values()),
      'blank:', [s for s, v in cad.items() if count(v[2]) is None])
