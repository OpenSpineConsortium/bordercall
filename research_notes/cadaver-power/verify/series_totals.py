# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/series_totals.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below; 'skeleton' joined the cadaveric words, for
# the corrected tables' "dry skeletons"; and --sum-sexes (2026-10-29) gives a series split by sex the sum of its
# sexes' counts, since spine-program #241 made each sex's row carry its own count, where the copy's carried the
# whole sample in each (the copy's counts are unchanged by both).
#     python3 -I verify/series_totals.py SYNTHETIC_SPINE_DATA [--sum-sexes]
"""Every distinct series in synthetic_spine's two tables, cadaveric or not, with its recorded n."""
import csv, os, re, sys
SS = os.path.join(sys.argv[1], '')
CAD = ('cadaver', 'dry bone', 'post-mortem', 'skeleton')
def count(n):
    nums = [int(x) for x in re.findall(r'\d+', n or '')]
    return max(nums) if nums else None
SUM_SEXES = '--sum-sexes' in sys.argv
series = {}
by_sex = {}    # series -> (measure, level) -> {sex: count}
for r in csv.DictReader(open(SS + 'level_references.csv')):
    series.setdefault(r['series'], (r['cohort'], r['modality'], r['n']))
    by_sex.setdefault(r['series'], {}).setdefault((r['measure'], r['level']), {})[r['sex']] = count(r['n'])
rows = [l for l in open(SS + 'pedicle_width_references.csv') if not l.startswith('#')]
for r in csv.DictReader(rows):
    name = 'Panjabi 1992' if r['series'] == 'Panjabi' else r['series'] + ' ' + r['year']
    series.setdefault(name, (r['cohort'], r['modality'], r['n']))
cad = {s: v for s, v in series.items() if any(k in (v[0] + ' ' + v[1]).lower() for k in CAD)}
print('distinct series', len(series), 'cadaveric', len(cad))
for s, v in cad.items():
    print('  ', s, v)
def total(s, v):
    """A series' count: its first row's, or with --sum-sexes its largest cell's sum over its sexes."""
    if not SUM_SEXES or s not in by_sex:
        return count(v[2])
    sums = [sum(n for n in cell.values() if n) for cell in by_sex[s].values()
            if any(n is not None for n in cell.values())]
    return max(sums) if sums else None
if SUM_SEXES:
    for s, v in cad.items():
        print('  ', s, 'summed over its sexes:', total(s, v))
print('recorded cadaveric n, each series once:', sum(total(s, v) or 0 for s, v in cad.items()),
      'blank:', [s for s, v in cad.items() if total(s, v) is None])
