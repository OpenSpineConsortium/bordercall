import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''            np.testing.assert_array_equal(cap.silhouette(cam), inside)
            self.assertGreater(int(inside.sum()), 300)
            self.assertLess(float(distance_to_polyline(centres, rim.uv, True).min()), 0.5)''', '''            np.testing.assert_array_equal(cap.silhouette(cam), inside)
            self.assertGreater(int(inside.sum()), 300)
            # no centre so near the rim that rounding could put it either side
            self.assertGreater(float(distance_to_polyline(centres, rim.uv, True).min()), 1e-6)''')
open(path, "w", encoding="ascii").write(src)

rec = sys.argv[2]
src = open(rec, encoding="ascii").read()
swap('''def phantom() -> Tuple[np.ndarray, np.ndarray]:
    """The straight L2 to L4 phantom the lines export's tests measure."""
    from morphometry.tests import phantom as P
    return P.draw(P.straight(LEVELS, P.Vert()), spacing=SPACING)''', '''def placed() -> list:
    """The phantom's vertebrae as it places them, each with its own frame in the world
    (morphometry/tests/phantom.py, Placed)."""
    from morphometry.tests import phantom as P
    return P.straight(LEVELS, P.Vert())


def phantom() -> Tuple[np.ndarray, np.ndarray]:
    """The straight L2 to L4 phantom the lines export's tests measure."""
    from morphometry.tests import phantom as P
    return P.draw(placed(), spacing=SPACING)''')
open(rec, "w", encoding="ascii").write(src)
print("ok")
