import sys
path = sys.argv[1]
src = open(path).read()
def swap(old, new):
    global src
    assert src.count(old) == 1, old[:60]
    src = src.replace(old, new)
swap('''    (column_height). Drawn in the cell whose height is nearest the median, at the cell's mean
    place across and up the wall line, so the ends lie the cell's height apart along z."""''',
'''    (column_height). Drawn in the cell whose height is nearest the median, the cell nearest the
    body's middle among those as near to the rows' rounding, at the cell's mean place across and
    up the wall line, so the ends lie the cell's height apart along z."""''')
swap('''    cell, lo, hi = min(runs, key=lambda r: abs((r[2] - r[1]) - value))
''', '''    cell, lo, hi = min(runs, key=lambda r: (round(abs((r[2] - r[1]) - value), ROWS_PLACES),
                                            abs(float(r[0][:, 0].mean()) - xm)))
''')
swap('''    section's reading (canal_walls). Each is drawn in the section whose reading is nearest the
    median, the width through the hole's middle and the depth down its midline, so neither
    drawn length need equal the median."""''', '''    section's reading (canal_walls). Each is drawn in the section whose reading is nearest the
    median, the one nearest the band's middle among those as near to the rows' rounding, the
    width through the hole's middle and the depth down its midline, so neither drawn length
    need equal the median."""''')
swap('''    rows = [(s, r) for s, r in rows if r is not None]
    out = []
    s, _ = min(rows, key=lambda sr: abs(sr[1][0] - canal["canal_w"]))
''', '''    rows = [(s, r) for s, r in rows if r is not None]
    mid = float(np.median([s.w for s, _ in rows]))
    nearest = lambda k, value: min(rows, key=lambda sr: (round(abs(sr[1][k] - value), ROWS_PLACES),  # noqa: E731
                                                         abs(sr[0].w - mid)))
    out = []
    s, _ = nearest(0, canal["canal_w"])
''')
swap('''    _, (_, _, wa, wp, xm, z) = min(rows, key=lambda sr: abs(sr[1][1] - canal["canal_ap"]))
''', '''    _, (_, _, wa, wp, xm, z) = nearest(1, canal["canal_ap"])
''')
open(path, "w").write(src)
print("ok")
