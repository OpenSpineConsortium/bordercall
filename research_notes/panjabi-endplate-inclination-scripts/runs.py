"""Longest run of equal consecutive values between any lumbar series and any cervical or
thoracic series of bordercall's long table (means and SEMs alike), at every alignment."""
import csv, sys, collections

series = collections.defaultdict(list)
for r in csv.reader(l for l in open(sys.argv[1]) if not l.startswith('#')):
    if len(r) < 11 or r[0] == 'measure':
        continue
    measure, side, level, mnem, stat, value, region = r[0], r[1], r[2], r[3], r[4], r[5], r[10]
    series[(region, mnem, side, stat)].append((level, float(value)))


def longest(a, b):
    best = (0, None)
    for off in range(-len(a) + 1, len(b)):
        run = 0
        for i in range(len(a)):
            j = i + off
            if 0 <= j < len(b) and a[i][1] == b[j][1]:
                run += 1
                if run > best[0]:
                    best = (run, (a[i - run + 1][0], a[i][0], b[j - run + 1][0], b[j][0]))
            else:
                run = 0
    return best


hits = collections.Counter()
for ka, va in series.items():
    if ka[0] != 'lumbar':
        continue
    for kb, vb in series.items():
        if kb[0] not in ('cervical', 'thoracic'):
            continue
        for seq in (va, va[::-1]):
            n, where = longest(seq, vb)
            hits[n] += 1
            if n >= 3:
                print(n, ka, kb, where)
print('pairs by longest run:', dict(sorted(hits.items())))
print('series:', collections.Counter(k[0] for k in series))
