"""The end-name test knows each pair of names either way round, so an end named the wrong way
fails on where it lies rather than on a name the table lacks."""
import sys
path = sys.argv[1] + "/morphometry/tests/test_lines_export.py"
src = open(path).read()
pairs = [
('''# which way each end's name lies along the frame's axes: (axis, sign of b less a)
ORDER = {("inferior", "superior"): (2, 1), ("superior", "inferior"): (2, -1), ("posterior", "anterior"): (1, 1),
         ("anterior", "posterior"): (1, -1), ("left", "right"): (0, 1), ("canal", "tip"): (1, -1)}
''', '''# which way each end's name lies along the frame's axes, either way round: (axis, sign of b less a)
ORDER = {("inferior", "superior"): (2, 1), ("posterior", "anterior"): (1, 1), ("left", "right"): (0, 1),
         ("tip", "canal"): (1, 1)}
ORDER.update({(b, a): (axis, -sign) for (a, b), (axis, sign) in list(ORDER.items())})
'''),
('''                if names == ("medial", "lateral"):
                    self.assertGreater(abs(b[0]), abs(a[0]), where)
                else:
                    axis, sign = ORDER[names]
                    self.assertGreater(sign * (b[axis] - a[axis]), 0.0, where)
''', '''                if set(names) == {"medial", "lateral"}:
                    medial, lateral = (a, b) if names[0] == "medial" else (b, a)
                    self.assertGreater(abs(lateral[0]), abs(medial[0]), where)
                else:
                    self.assertIn(names, ORDER, where)
                    axis, sign = ORDER[names]
                    self.assertGreater(sign * (b[axis] - a[axis]), 0.0, where)
'''),
]
for old, new in pairs:
    assert src.count(old) == 1, (old[:70], src.count(old))
    src = src.replace(old, new)
open(path, "w").write(src)
print("ok")
