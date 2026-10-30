"""The median lines' test in morphoview, and code_stamp's files closed."""
import sys
root = sys.argv[1]

def edit(rel, pairs):
    path = root + "/" + rel
    src = open(path).read()
    for old, new in pairs:
        assert src.count(old) == 1, (rel, old[:70], src.count(old))
        src = src.replace(old, new)
    open(path, "w").write(src)

edit("morphoview/tests/test_lines.py", [
('''Every line built for L3 and its two discs must give the value the measuring code gives, so all are
drawn; each length's ends must lie on the surface it is said to end at, a step inward on one side
of it and a step outward on the other, the step under a voxel's diagonal; a value off by more than
the rows' rounding is withheld; and the four panels draw with one key line for each drawn line."""''',
'''Every line built for L3 and its two discs must give the value the measuring code gives, so all are
drawn; each length's ends must lie on the surface it is said to end at, a step inward on one side
of it and a step outward on the other, the step under a voxel's diagonal; a median is drawn in the
reading nearest it; a value off by more than the rows' rounding is withheld; and the four panels
draw with one key line for each drawn line."""'''),
('''CANAL_WITHIN = ("canal_ap_min", "interpedicular", "canal_w", "canal_ap")
''', '''CANAL_WITHIN = ("canal_ap_min", "interpedicular", "canal_w", "canal_ap")
# a median is drawn in the row, cell or section whose reading is nearest it: on this phantom the
# canal's depth runs from 16.0 to 19.5 mm over the band it is read in and the section drawn reads
# 0.07 mm over the median, the furthest of any median's line from its value
MEDIAN_MM = 0.1
'''),
('''    def test_a_disc_runs_from_the_plate_below_to_the_plate_above(self):''',
'''    def test_a_median_is_drawn_in_the_reading_nearest_it(self):
        medians = [ln for ln in self.lines if ln.rule == "median"]
        self.assertTrue({"h_post", "canal_w", "canal_ap"} <= {ln.key for ln in medians})
        for ln in medians:
            self.assertLessEqual(abs(ln.drawn - ln.value), MEDIAN_MM, ln.key)

    def test_a_disc_runs_from_the_plate_below_to_the_plate_above(self):'''),
])

edit("morphometry/__main__.py", [
('''            if name.endswith(".py"):
                h.update(name.encode() + b"\\0" + open(os.path.join(folder, name), "rb").read())
    if lines:
        h.update(LINES_SOURCE.encode() + b"\\0" + open(os.path.join(here, LINES_SOURCE), "rb").read())
    return h.hexdigest()[:16]''',
'''            if name.endswith(".py"):
                h.update(name.encode() + b"\\0" + read_bytes(os.path.join(folder, name)))
    if lines:
        h.update(LINES_SOURCE.encode() + b"\\0" + read_bytes(os.path.join(here, LINES_SOURCE)))
    return h.hexdigest()[:16]


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()'''),
])
print("ok")
