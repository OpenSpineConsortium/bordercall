import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''        surfaces = {"dome": SH.Surface.over(mid, lambda u, w: 4.0 - 0.01 * (u * u + w * w), 0.5 * a, 0.5 * b,
                                            toward=across),
                    "cap": SH.Surface.through(centre + np.array([[0.0, 0.0, 0.0]] + [
                        [r * math.cos(t), r * math.sin(t), 0.0] for r in (3.0, 6.0) for t in turn]) @ pl.R.T
                        + 2.0 * up)}
        return curves, surfaces''', '''        # a cap of a sphere of 20 mm cut to a disc of 6, facing along the body's diagonal so every
        # view sees it at a slant
        tilted = SH.Plane(centre + 2.0 * up, across + forward + up)
        e1, e2 = tilted.axes()
        ring = np.vstack([[0.0, 0.0]] + [6.0 * k / 8.0 * np.stack([np.cos(t), np.sin(t)], axis=1)
                                        for k in range(1, 9) for t in [np.arange(6 * k) * math.pi / (3 * k)]])
        rise = np.sqrt(400.0 - (ring ** 2).sum(axis=1)) - math.sqrt(400.0 - 36.0)
        surfaces = {"dome": SH.Surface.over(mid, lambda u, w: 4.0 - 0.01 * (u * u + w * w), 0.5 * a, 0.5 * b,
                                            toward=across),
                    "cap": SH.Surface.through(tilted.point + ring[:, :1] * e1 + ring[:, 1:] * e2
                                              + rise[:, None] * tilted.normal)}
        return curves, surfaces''')
open(path, "w", encoding="ascii").write(src)
print("ok")
