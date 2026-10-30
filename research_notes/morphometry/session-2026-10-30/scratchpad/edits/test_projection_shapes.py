import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''support on it; the first view's camera under nanoDRR's other two orientations; and where FleXray's canvas
puts images and a spot on them. The phantom is built again here and must be the one recorded.
Where FleXray is installed, Live renders again."""''', '''support on it; the first view's camera under nanoDRR's other two orientations; and where FleXray's canvas
puts images and a spot on them. The phantom is built again here and must be the one recorded.
Curves and surfaces drawn in the phantom's vertebral bodies, from the frames the phantom placed
them in, land on FleXray's shadows of them too. Where FleXray is installed, Live renders again."""''')

swap('''class Crops(unittest.TestCase):''', '''class Shapes(unittest.TestCase):
    """Curves and surfaces of morphoview.shapes drawn in each vertebral body of the phantom, from
    the frame the phantom placed the vertebra in (morphometry/tests/phantom.py: the body an
    elliptic cylinder W wide and D deep from its posterior wall, its mid-height at z = 0), carried
    onto the three renders. Every shape inside a body keeps 5 mm or more from its cortex, more than
    a voxel's half diagonal, the half pixel a pixel's ray may pass the point at and a step of
    FleXray's sampling together, so each point lands on a pixel of FleXray's own shadow of the
    vertebra, and a surface's shadow lies within it; the body's outline, on the cortex, lands within
    LAND_PX of it, as the lines' ends do."""

    @classmethod
    def setUpClass(cls):
        lab, aff, same = phantom()
        if not same:
            raise AssertionError(RERUN)
        cls.placed = FR.placed()

    def inside(self, pl) -> Tuple[dict, dict]:
        """The curves and the surfaces drawn inside one vertebra's body, in the world."""
        v = pl.v
        across, forward, up = pl.R.T
        centre = pl.c + pl.R @ np.array([0.0, v.D / 2.0, 0.0])
        a, b = v.W / 2.0, v.D / 2.0
        turn = np.radians(np.arange(0.0, 360.0, 60.0))
        knots = (centre + 0.6 * (a * np.cos(turn)[:, None] * across + b * np.sin(turn)[:, None] * forward)
                 + 5.0 * np.array([1.0, -1.0] * 3)[:, None] * up)
        mid = SH.Plane(centre, up)
        curves = {"ellipse": SH.ellipse(centre, 0.7 * a * across, 0.7 * b * forward),
                  "arc": SH.arc(centre, across, centre + 8.0 * up, 300.0),
                  "spline": SH.spline(knots, closed=True),
                  "patch": mid.patch(0.55 * a, 0.55 * b, toward=across).outline()}
        surfaces = {"dome": SH.Surface.over(mid, lambda u, w: 4.0 - 0.01 * (u * u + w * w), 0.5 * a, 0.5 * b,
                                            toward=across),
                    "cap": SH.Surface.through(centre + np.array([[0.0, 0.0, 0.0]] + [
                        [r * math.cos(t), r * math.sin(t), 0.0] for r in (3.0, 6.0) for t in turn]) @ pl.R.T
                        + 2.0 * up)}
        return curves, surfaces

    def test_a_shape_inside_a_body_lands_on_flexrays_shadow_of_it(self):
        for name, cam, v in recorded_views():
            for pl in self.placed:
                shadow = support(v, [pl.level])
                curves, surfaces = self.inside(pl)
                for kind, curve in curves.items():
                    got = curve.resampled(0.5).project(cam)
                    self.assertTrue(bool(got.in_beam.all()), (name, pl.level, kind))
                    r, c = got.uv[:, 1].astype(int), got.uv[:, 0].astype(int)
                    self.assertTrue(bool(shadow[r, c].all()), (name, pl.level, kind))
                for kind, surface in surfaces.items():
                    shade = surface.silhouette(cam)
                    self.assertGreater(int(shade.sum()), 10, (name, pl.level, kind))
                    self.assertFalse(bool((shade & ~shadow).any()), (name, pl.level, kind))

    def test_a_bodys_outline_lands_on_flexrays_shadow_of_it(self):
        for name, cam, v in recorded_views():
            for pl in self.placed:
                across, forward, _ = pl.R.T
                centre = pl.c + pl.R @ np.array([0.0, pl.v.D / 2.0, 0.0])
                outline = SH.ellipse(centre, pl.v.W / 2.0 * across, pl.v.D / 2.0 * forward).resampled(0.5)
                shadow = support(v, [pl.level])
                far = ndimage.distance_transform_edt(~shadow)
                got = outline.project(cam)
                self.assertLessEqual(float(far[got.uv[:, 1].astype(int), got.uv[:, 0].astype(int)].max()), LAND_PX,
                                     (name, pl.level))


class Crops(unittest.TestCase):''')
open(path, "w", encoding="ascii").write(src)
print("ok")
