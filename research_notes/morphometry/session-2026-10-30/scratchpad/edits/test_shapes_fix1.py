import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''        # a point falling on another's place in the plane is left out of the triangles
        twice = SH.Surface.through(np.vstack([points, points[:1] + 3.0 * frame[:, 2]]))
        self.assertEqual(len(twice.vertices), len(points))''', '''        # a point given twice falls on its own place in the plane and is taken once
        twice = SH.Surface.through(np.vstack([points, points[:1]]))
        self.assertEqual(len(twice.vertices), len(points))''')
swap('''            SH.Surface.over(plane, lambda u, v: np.sqrt(u), 20.0, 12.0)''', '''            SH.Surface.over(plane, lambda u, v: np.where(u > 0.0, math.nan, 0.0), 20.0, 12.0)''')
open(path, "w", encoding="ascii").write(src)
print("ok")
