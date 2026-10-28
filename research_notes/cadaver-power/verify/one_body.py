# Copied for the cadaver-power note from the third check's folder, power-check3/onebody2.py, 2026-10-28.
# Unchanged: it already took its inputs as arguments. The note takes from it the answers, the wrong answers
# and the binomial tail for one typical table, and none of its table-SD SEs or t tests: the tables are scored
# on the same 300 columns, so their SD can be 0, as it is for the two 2,000-person tables at 1 body, each
# right on 50 of its 51, which no SE from that SD can read against 99%.
#     python3 -I verify/one_body.py seven/part_b_seven*.json > verify/one_body.log
"""Whether a row's one-body 0.99 answers read against 99%: the mean precision over the row's tables, its
SE from the table SD (tables taken as independent draws), a one-sided t test against 0.99 on tables - 1
degrees of freedom, and the binomial tail for one typical table's wrong answers at a true 1% error rate."""
import json, math, sys
from scipy import stats

def row(arm, s):
    n_tab = s['tables']
    ans = s['answered'] * 6600
    prec = s['precision']
    wrong = ans * (1 - prec)
    sd = s['precision_table_sd']
    out = '%-24s tables %d  answered/table %.2f  precision %.2f%%  table SD %.2f  wrong/table %.2f' % (
        arm, n_tab, ans, 100 * prec, 100 * sd, wrong)
    if n_tab > 1 and sd > 0:
        se = sd / math.sqrt(n_tab)
        t = (0.99 - prec) / se
        p = stats.t.sf(t, n_tab - 1)
        out += '  SE %.2f  (99%% - mean)/SE %.2f  one-sided t p %.3g' % (100 * se, t, p)
    a1, w1 = round(ans), math.floor(wrong)
    if w1 >= 1:
        out += '  P(>=%d wrong of %d | 1%%) %.3g' % (w1, a1, stats.binom.sf(w1 - 1, a1, 0.01))
    return out

for path in sys.argv[1:]:
    d = json.load(open(path))
    print('==', path.split('/')[-1])
    for arm, w in d['arms'].items():
        print(row(arm, w['1']))
