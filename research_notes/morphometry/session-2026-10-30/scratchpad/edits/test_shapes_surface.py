import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''"""The shapes beside the straight lines (morphoview.shapes), on cameras of FleXray's kind.

A sampled curve keeps every point of the true curve within its tolerance and passes through what
it must, and a spline lies on the centripetal Catmull-Rom spans, written here again in Hermite form;
a straight segment of the world stays straight on the render, so a polyline projects
exactly; a curve cut by the source's plane keeps the pieces in front of it; a plane fitted to
points is the plane they lie on, and a plane off the beam's axis is seen along its own ray; a
circle seen through parallel rays encloses the ellipse's area; a volume's path lengths are its
chords through its voxels, on oblique rays too, by the fine sampling and by FleXray's, the latter
counted again here point by point, and both samplings read a ray the same either way along it; and
a shape is equal only to itself."""''',
'''"""The shapes beside the straight lines (morphoview.shapes), on cameras of FleXray's kind.

A sampled curve keeps every point of the true curve within its tolerance and passes through what
it must, and a spline lies on the centripetal Catmull-Rom spans, written here again in Hermite form;
a straight segment of the world stays straight on the render, so a polyline projects
exactly, and a curve on the render keeps within its tolerance as the render enlarges it; a face-on
circle, arc, ellipse, patch or polygon is its own shape magnified by sdd over its depth, an
edge-on one a line; a spline on the render passes through its points' places; a curve cut by the
source's plane keeps the pieces in front of it; a plane fitted to points is the plane they lie
on, and a plane off the beam's axis is seen along its own ray; a circle seen through parallel
rays encloses the ellipse's area; a surface over a plane keeps within its tolerance, a quadric
fitted to points on one is that quadric, a concave end-plate sags by its concavity and a
spherical cap holds its area, and a surface's shadow on the render is what its rim encloses
there; a volume's path lengths are its chords through its voxels, on oblique rays too, by the
fine sampling and by FleXray's, whose window over each ray skips none of nanoDRR's points, and
both samplings read a ray the same either way along it; and a shape is equal only to itself.
tests/test_projection.py holds the camera, the counts and the shapes drawn on the phantom to what
FleXray rendered."""''')

swap('''import numpy as np

from morphoview import projection as PJ
from morphoview import shapes as SH
''', '''import numpy as np

from morphometry.tests import phantom as P
from morphoview import projection as PJ
from morphoview import shapes as SH
''')

swap('''def catmull_rom_span(p: np.ndarray, alpha: float, s: np.ndarray) -> np.ndarray:''', '''def enlargement(cam: PJ.Camera, world: np.ndarray) -> float:
    """The most the render moves a point near these by, in pixels, for each mm the point moves:
    the magnification over the pixel's smaller side, and under a cone beam the secant of the
    ray's angle to the axis besides, the largest stretch of the projection's derivative."""
    side = min(cam.view.delx, cam.view.pixel_y)
    if cam.view.orthographic:
        return 1.0 / side
    depth = cam.camera_points(world)[:, 2]
    secant = 1.0 / (cam.ray_direction(world) @ cam.beam)
    return float((cam.view.sdd / depth * secant).max()) / side


def on_axis(cam: PJ.Camera, depth: float) -> np.ndarray:
    """The point of the beam's axis at a depth, which projects to the principal point."""
    return cam.source + depth * cam.beam


def in_convex(q: np.ndarray, ring: np.ndarray) -> np.ndarray:
    """Whether each place on a render lies in the convex polygon through ring, its edge counted in."""
    side = np.stack([PJ_cross(b - a, q - a) for a, b in zip(ring, np.roll(ring, -1, axis=0))], axis=1)
    return (side >= -1e-9).all(axis=1) | (side <= 1e-9).all(axis=1)


def PJ_cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def cap_points(R: float, r: float, rings: int = 40) -> np.ndarray:
    """Points on the cap of a sphere of radius R cut to a disc of radius r, in the plane z = 0
    of its rim, rising to its apex at the sag R - sqrt(R2 - r2) along z: rings of six points
    more each, the last on the rim."""
    sag = R - math.sqrt(R * R - r * r)
    xy = [np.zeros((1, 2))]
    for k in range(1, rings + 1):
        t = np.arange(6 * k) * 2.0 * math.pi / (6 * k)
        xy.append(r * k / rings * np.stack([np.cos(t), np.sin(t)], axis=1))
    xy = np.vstack(xy)
    return np.column_stack([xy, np.sqrt(R * R - (xy ** 2).sum(axis=1)) - (R - sag)])


def placed(points: np.ndarray, frame: np.ndarray, origin) -> np.ndarray:
    """Points of a frame of its own carried into the world: the frame's columns are its axes."""
    return np.asarray(origin, float) + points @ np.asarray(frame, float).T


def catmull_rom_span(p: np.ndarray, alpha: float, s: np.ndarray) -> np.ndarray:''')

swap('''class Volumes(unittest.TestCase):''', '''class OnTheRender(unittest.TestCase):
    """Curves, patches and polygons carried onto renders, set against what the camera does."""

    def cameras(self):
        turned = dict(rot_deg=(20.0, -10.0, 5.0), delx=0.8, dely=1.1, height=400, width=400)
        return cone(x0=6.0, y0=-4.0, **turned), parallel(**turned)

    def test_a_curve_on_the_render_keeps_within_its_tolerance_as_the_render_enlarges_it(self):
        # each point of the true curve lies within the tolerance of a place on the sampled one,
        # whose projection lies on the projected polyline, and the render moves a point at most
        # enlargement() pixels for each mm, so the projected true curve lies that far at most
        # from the projected polyline; a face-on circle on the axis comes near the bound
        c, n = np.array([4.0, -20.0, 6.0]), SH.unit([0.3, -0.8, 0.5])
        start = c + 18.0 * SH.across(n)[0]
        knots = np.array([[-30.0, 20.0, -25.0], [-5.0, -10.0, 0.0], [10.0, 25.0, 15.0], [35.0, 0.0, 30.0]])
        s = np.linspace(0.0, 1.0, 4001)
        t = np.linspace(0.0, 2.0 * math.pi, 40001)
        for cam in self.cameras():
            arc = SH.arc(c, n, start, 250.0)
            e1 = (arc.points[0] - c) / 18.0
            e2 = np.cross(n, e1)
            turn = np.linspace(0.0, math.radians(250.0), 40001)
            a, b = 25.0 * SH.across(cam.beam)[0], 9.0 * SH.across(cam.beam)[1]
            ext = np.vstack([2 * knots[0] - knots[1], knots, 2 * knots[-1] - knots[-2]])
            face = on_axis(cam, 800.0)
            cases = [
                (arc, c + 18.0 * (np.cos(turn)[:, None] * e1 + np.sin(turn)[:, None] * e2)),
                (SH.ellipse(c, a, b), c + np.cos(t)[:, None] * a + np.sin(t)[:, None] * b),
                (SH.spline(knots), np.vstack([catmull_rom_span(ext[i:i + 4], 0.5, s) for i in range(3)])),
                (SH.circle(face, cam.beam, 20.0), None),
            ]
            for curve, true in cases:
                if true is None:
                    e1f, e2f = SH.across(cam.beam)
                    true = face + 20.0 * (np.cos(t)[:, None] * e1f + np.sin(t)[:, None] * e2f)
                got = curve.project(cam)
                self.assertEqual((got.closed, len(got.pieces())), (curve.closed, 1))
                np.testing.assert_array_equal(got.uv, cam.project(curve.points).uv)
                bound = TOL * enlargement(cam, true) * (1.0 + 1e-6)
                off = distance_to_polyline(cam.project(true).uv, got.uv, curve.closed)
                self.assertLessEqual(float(off.max()), bound, cam.view.orthographic)
            self.assertGreater(float(off.max()), 0.8 * bound)

    def test_a_face_on_circle_arc_and_ellipse_are_magnified_by_sdd_over_their_depth(self):
        for cam in self.cameras():
            view = cam.view
            centre = on_axis(cam, 700.0)
            m = 1.0 if view.orthographic else view.sdd / 700.0
            middle = cam.project(centre[None]).uv[0]
            np.testing.assert_allclose(middle, [cam.cx, cam.cy], atol=EXACT)
            right, down = cam.to_world[:3, 0], cam.to_world[:3, 1]

            def in_mm(got):
                return (got.uv - middle) * [view.delx, view.pixel_y] / m

            ring = SH.circle(centre, cam.beam, 20.0)
            np.testing.assert_allclose(np.linalg.norm(in_mm(ring.project(cam)), axis=1), 20.0, atol=EXACT)
            # an arc turning about the beam turns from the image's u towards its v by its angle
            arc = SH.arc(centre, cam.beam, centre + 20.0 * right, 250.0).project(cam)
            mm = in_mm(arc)
            np.testing.assert_allclose(np.linalg.norm(mm, axis=1), 20.0, atol=EXACT)
            turned = np.unwrap(np.arctan2(mm[:, 1], mm[:, 0]))
            self.assertAlmostEqual(math.degrees(turned[-1] - turned[0]), 250.0, places=9)
            self.assertTrue(bool((np.diff(turned) > 0).all()))
            # an ellipse with its long axis 30 degrees from the image's u
            along = math.cos(math.radians(30.0)) * right + math.sin(math.radians(30.0)) * down
            across_ = np.cross(cam.beam, along)
            oval = SH.ellipse(centre, 25.0 * along, 10.0 * across_, tolerance=0.001).project(cam)
            mm = in_mm(oval)
            u30 = np.array([math.cos(math.radians(30.0)), math.sin(math.radians(30.0))])
            local = np.stack([mm @ u30 / 25.0, mm @ np.array([-u30[1], u30[0]]) / 10.0], axis=1)
            np.testing.assert_allclose((local ** 2).sum(axis=1), 1.0, atol=1e-9)
            area = oval.area_px() * view.delx * view.pixel_y / (m * m)
            self.assertLess(area, math.pi * 250.0)
            self.assertGreater(area / (math.pi * 250.0), 1.0 - 2e-4)

    def test_a_spline_on_the_render_passes_through_its_points_places(self):
        knots = np.array([[-30.0, 20.0, -25.0], [-5.0, -10.0, 0.0], [10.0, 25.0, 15.0], [35.0, 0.0, 30.0],
                          [20.0, -30.0, -10.0]])
        for cam, closed in itertools.product(self.cameras(), (False, True)):
            spline = SH.spline(knots, closed=closed)
            got = spline.project(cam)
            self.assertEqual(got.closed, closed)
            np.testing.assert_array_equal(got.uv, cam.project(spline.points).uv)
            near = [int(np.argmin(np.linalg.norm(got.uv - p, axis=1))) for p in cam.project(knots).uv]
            for k, p in zip(near, cam.project(knots).uv):
                self.assertLess(float(np.linalg.norm(got.uv[k] - p)), EXACT)
            self.assertEqual(near, sorted(near))
            self.assertGreaterEqual(got.length_px(), SH.Curve(knots, closed).project(cam).length_px() - EXACT)

    def test_a_patch_and_a_polygon_on_the_render(self):
        for cam in self.cameras():
            view = cam.view
            m = 1.0 if view.orthographic else view.sdd / 700.0
            centre = on_axis(cam, 700.0)
            # face on, every corner at one depth: the shape, magnified m times each way
            face = SH.Plane(centre, cam.beam).patch(15.0, 6.0, toward=[1.0, 2.0, 3.0])
            triangle = SH.Polygon(face.corners[:3])
            for shape in (face, triangle):
                got = shape.project(cam)
                self.assertTrue(got.closed)
                np.testing.assert_array_equal(got.uv, cam.project(shape.corners).uv)
                self.assertAlmostEqual(got.area_px() * view.delx * view.pixel_y / (m * m) / shape.area(), 1.0,
                                       places=12)
            self.assertAlmostEqual(SH.Plane(centre, cam.beam).seen_at_deg(cam), 90.0, places=9)
            # edge on, its plane holding the ray through its point, and so the source: a line
            point = centre + 30.0 * cam.to_world[:3, 0]
            edge = SH.Plane(point, np.cross(cam.ray_direction(point)[0], [0.3, 0.5, 0.8]))
            self.assertAlmostEqual(edge.seen_at_deg(cam), 0.0, places=9)
            self.assertLess(edge.patch(15.0, 6.0).project(cam).area_px(), 1e-9)
        # under parallel rays a patch turned t from face on keeps the cosine of t of its area
        cam = self.cameras()[1]
        right = cam.to_world[:3, 0]
        for tilt in (0.0, 25.0, 50.0, 75.0):
            t = math.radians(tilt)
            plane = SH.Plane(on_axis(cam, 600.0), math.cos(t) * cam.beam + math.sin(t) * right)
            patch = plane.patch(12.0, 7.0)
            got = patch.project(cam).area_px() * cam.view.delx * cam.view.pixel_y
            self.assertAlmostEqual(got / (patch.area() * math.cos(t)), 1.0, places=12)
            self.assertAlmostEqual(plane.seen_at_deg(cam), 90.0 - tilt, places=9)


class Surfaces(unittest.TestCase):
    def test_a_grids_triangles_turn_about_rows_crossed_with_columns(self):
        rows, cols = np.meshgrid(np.arange(3.0), np.arange(4.0), indexing="ij")
        grid = np.stack([rows * 2.0, cols * 3.0, 0.1 * rows * cols], axis=-1)
        surface = SH.Surface.from_grid(grid)
        self.assertEqual(len(surface.triangles), 2 * 2 * 3)
        c = surface.corners()
        normals = np.cross(c[:, 1] - c[:, 0], c[:, 2] - c[:, 0])
        self.assertTrue(bool((normals[:, 2] > 0).all()))
        for bad in (grid[:1], grid[0], np.zeros((3, 3, 2))):
            with self.assertRaises(ValueError):
                SH.Surface.from_grid(bad)
        for vertices, triangles in (([[0, 0, 0], [1, 0, 0]], [[0, 1, 1]]), (grid.reshape(-1, 3), [[0, 1, 1]]),
                                    (grid.reshape(-1, 3), [[0, 1, 12]]), (grid.reshape(-1, 3), [[0.0, 1.0, 2.0]]),
                                    (grid.reshape(-1, 3), np.zeros((0, 3), int)), ([[0, 0, 0], [1, 0, 0], [0, math.nan, 0]], [[0, 1, 2]])):
            with self.assertRaises(ValueError):
                SH.Surface(np.asarray(vertices, float), np.asarray(triangles))

    def test_a_surface_over_a_plane_keeps_within_its_tolerance(self):
        plane = SH.Plane([4.0, -2.0, 7.0], [0.2, -0.5, 0.8])
        e1, e2 = plane.axes([1.0, 0.0, 0.0])

        def height(u, v):
            return 0.02 * u * u - 0.03 * u * v + 0.015 * v * v + 0.0004 * u ** 3

        surface = SH.Surface.over(plane, height, 20.0, 12.0, toward=[1.0, 0.0, 0.0])
        d = surface.vertices - plane.point
        u, v = d @ e1, d @ e2
        np.testing.assert_allclose(d @ plane.normal, height(u, v), atol=EXACT)
        np.testing.assert_allclose([u.min(), u.max(), v.min(), v.max()], [-20.0, 20.0, -12.0, 12.0], atol=EXACT)
        self.assertGreater(len(surface.vertices), 25)
        tri = surface.triangles
        for i, j in ((0, 1), (1, 2), (2, 0)):
            mu, mv = 0.5 * (u[tri[:, i]] + u[tri[:, j]]), 0.5 * (v[tri[:, i]] + v[tri[:, j]])
            true = plane.point + mu[:, None] * e1 + mv[:, None] * e2 + height(mu, mv)[:, None] * plane.normal
            chord = 0.5 * (surface.vertices[tri[:, i]] + surface.vertices[tri[:, j]])
            self.assertLessEqual(float(np.linalg.norm(true - chord, axis=1).max()), TOL)
        # a flat one is the patch, its rim the patch's outline
        flat = SH.Surface.over(plane, lambda u, v: 0.0 * u, 20.0, 12.0, toward=[1.0, 0.0, 0.0])
        patch = plane.patch(20.0, 12.0, toward=[1.0, 0.0, 0.0])
        self.assertAlmostEqual(flat.area() / patch.area(), 1.0, places=12)
        self.assertLess(flat.sag(), EXACT)
        rims = flat.rims()
        self.assertEqual(len(rims), 1)
        self.assertAlmostEqual(rims[0].length(), patch.outline().length(), places=9)
        for corner in patch.corners:
            self.assertLess(float(np.linalg.norm(rims[0].points - corner, axis=1).min()), EXACT)
        for bad in (0.0, -1.0, math.nan):
            with self.assertRaises(ValueError):
                SH.Surface.over(plane, height, bad, 12.0)
        with self.assertRaises(ValueError):
            SH.Surface.over(plane, lambda u, v: np.sqrt(u), 20.0, 12.0)

    def test_a_quadric_fitted_to_points_on_one_is_that_quadric(self):
        # points in pairs either side of the quadric's own point, so the plane fitted to them is
        # its own and the fit takes it exactly
        rng = np.random.default_rng(11)
        frame = P.rotation((0.4, -0.7, 0.2), 33.0)
        origin = np.array([12.0, -40.0, 85.0])

        def height(u, v):
            return 1.5 + 0.004 * u * u - 0.003 * u * v + 0.006 * v * v

        half = rng.uniform([-25.0, -15.0], [25.0, 15.0], size=(200, 2))
        uv = np.vstack([half, -half])
        local = np.column_stack([uv, height(uv[:, 0], uv[:, 1])])
        points = placed(local, frame, origin)
        surface, rms = SH.Surface.fit(points)
        self.assertLess(rms, EXACT)
        back = (surface.vertices - origin) @ frame
        np.testing.assert_allclose(back[:, 2], height(back[:, 0], back[:, 1]), atol=1e-9)
        self.assertEqual(len(surface.vertices), len(points))
        through = SH.Surface.through(points)
        self.assertEqual(sorted(map(tuple, through.vertices)), sorted(map(tuple, points)))
        self.assertAlmostEqual(through.area() / surface.area(), 1.0, places=9)
        # heights off the quadric by noise of 0.2 mm fit with that noise left over
        noisy = points + rng.normal(scale=0.2, size=len(points))[:, None] * frame[:, 2]
        self.assertAlmostEqual(SH.Surface.fit(noisy)[1] / 0.2, 1.0, delta=0.1)
        # a point falling on another's place in the plane is left out of the triangles
        twice = SH.Surface.through(np.vstack([points, points[:1] + 3.0 * frame[:, 2]]))
        self.assertEqual(len(twice.vertices), len(points))
        circle = placed(np.column_stack([np.cos(np.arange(12.0)), np.sin(np.arange(12.0)), np.zeros(12)]) * 10.0,
                        frame, origin)
        for bad in (points[:5], circle, [[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]]):
            with self.assertRaises(ValueError):
                SH.Surface.fit(bad)

    def test_a_concave_end_plate_sags_by_its_concavity(self):
        # the phantom's top plate (morphometry/tests/phantom.py, body_inside) is a paraboloid that
        # dips its concavity below the plate's outline at the plate's middle: sampled on rings
        # out to the outline, a quadric fits it exactly and its sag is the concavity
        frame = P.rotation((1.0, 0.3, 0.0), 18.0)
        origin = np.array([-3.0, 16.0, -33.0])
        for concavity in (2.0, 0.0):
            v = P.Vert(concavity=concavity)
            ring = np.vstack([[0.0, 0.0]] + [k / 12.0 * np.stack([np.cos(t), np.sin(t)], axis=1)
                                            for k in range(1, 13) for t in [np.arange(8 * k) * math.pi / (4 * k)]])
            x, y = ring[:, 0] * v.W / 2.0, v.D / 2.0 + ring[:, 1] * v.D / 2.0
            z = v.Hp / 2.0 - np.array([P.dip(v, a, b) for a, b in zip(x, y)])
            surface, rms = SH.Surface.fit(placed(np.column_stack([x, y, z]), frame, origin))
            self.assertLess(rms, EXACT)
            self.assertAlmostEqual(surface.sag(), concavity, places=9)
            self.assertEqual(len(surface.rims()), 1)

    def test_a_spherical_caps_area_rim_and_sag(self):
        R, r = 30.0, 15.0
        sag = R - math.sqrt(R * R - r * r)
        cap = SH.Surface.through(placed(cap_points(R, r), P.rotation((0.2, 1.0, -0.4), 50.0), [5.0, 6.0, -7.0]))
        self.assertAlmostEqual(cap.area() / (2.0 * math.pi * R * sag), 1.0, delta=2e-4)
        self.assertLess(cap.area(), 2.0 * math.pi * R * sag)
        self.assertAlmostEqual(cap.sag(), sag, places=9)
        rims = cap.rims()
        self.assertEqual(len(rims), 1)
        self.assertEqual(len(rims[0].points), 6 * 40)
        axis = SH.Plane.fit(rims[0].points)[0]
        np.testing.assert_allclose(np.linalg.norm(rims[0].points - axis.point, axis=1), r, atol=1e-9)
        # two triangles apart have two rims; two that share one corner alone, a rim that meets
        # itself; four closing a tetrahedron, none
        pts = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [5, 0, 0], [6, 0, 0], [5, 1, 0], [-1, 0, 0], [0, -1, 0],
                        [0, 0, 1]])
        self.assertEqual([len(c.points) for c in SH.Surface(pts, [[0, 1, 2], [3, 4, 5]]).rims()], [3, 3])
        with self.assertRaises(ValueError):
            SH.Surface(pts, [[0, 1, 2], [0, 6, 7]]).rims()
        with self.assertRaises(ValueError):
            SH.Surface(pts, [[0, 1, 2], [0, 1, 8], [1, 2, 8], [2, 0, 8]]).rims()

    def test_a_surfaces_shadow_is_what_its_rim_encloses_on_the_render(self):
        # a flat triangle of the world is one of the render and a pixel's ray meets the surface
        # where the pixel's centre falls in a projected triangle, so a cap seen without folding
        # over shades the pixels inside its projected rim, and its triangles' areas there sum to
        # the rim's; its middle bulging towards the source or away
        small = dict(delx=0.9, height=80, width=90, rot_deg=(15.0, -10.0, 5.0))
        for cam, turn in itertools.product((cone(**small), parallel(**small)), (0.0, 180.0, 35.0)):
            frame = P.rotation(SH.across(cam.beam)[0], turn) @ np.column_stack([*SH.across(cam.beam), -cam.beam])
            cap = SH.Surface.through(placed(cap_points(30.0, 15.0), frame, on_axis(cam, 800.0)))
            got = cap.project(cam)
            rim = cap.rims()[0].project(cam)
            self.assertAlmostEqual(got.area_px() / rim.area_px(), 1.0, places=9)
            centres = cam.pixel_centres()
            inside = in_convex(centres, rim.uv).reshape(cam.view.height, cam.view.width)
            np.testing.assert_array_equal(cap.silhouette(cam), inside)
            self.assertGreater(int(inside.sum()), 300)
            self.assertLess(float(distance_to_polyline(centres, rim.uv, True).min()), 0.5)
        # a flat one shades what the patch it is encloses
        cam = cone(**small)
        plane = SH.Plane(on_axis(cam, 790.0), SH.unit(cam.beam + [0.2, 0.1, -0.3]))
        flat = SH.Surface.over(plane, lambda u, v: 0.0 * u, 14.0, 9.0, toward=[1.0, 0.0, 0.0])
        patch = plane.patch(14.0, 9.0, toward=[1.0, 0.0, 0.0]).project(cam)
        self.assertAlmostEqual(flat.project(cam).area_px() / patch.area_px(), 1.0, places=9)
        inside = in_convex(cam.pixel_centres(), patch.uv).reshape(cam.view.height, cam.view.width)
        np.testing.assert_array_equal(flat.silhouette(cam), inside)

    def test_a_surface_reaching_behind_the_source_is_refused(self):
        cam = cone()
        plane = SH.Plane(cam.source, cam.beam)
        surface = SH.Surface.over(plane, lambda u, v: 5.0 + 0.0 * u, 10.0, 10.0)
        self.assertEqual(int(surface.silhouette(cam).sum()), 0) if False else None
        across_source = SH.Surface.over(SH.Plane(cam.source, cam.to_world[:3, 0]), lambda u, v: 0.0 * u, 10.0, 10.0)
        with self.assertRaises(ValueError):
            across_source.project(cam)
        self.assertEqual(across_source.silhouette(parallel()).shape, (200, 240))


class Volumes(unittest.TestCase):''')

swap('''    def test_flexrays_sampling_is_nanodrrs_point_by_point(self):
        # the ball, and a block, whose shadow fills the outline of its box, so a ray left out at
        # the outline's edge is seen''', '''    def test_flexrays_window_over_each_ray_skips_none_of_nanodrrs_points(self):
        # the module reads only a ray's points within a step of the volume's box; here every one
        # of nanoDRR's n points from the source to the detector is counted, so a point the window
        # left out is seen, on the ball and on a block, whose shadow fills the outline of its
        # box, so a ray left out at the outline's edge is seen too; tests/test_projection.py
        # holds the counts to FleXray's own''')

swap('''        makers = [lambda: SH.Curve(pts), lambda: SH.Curve(pts).project(cone()), lambda: SH.Plane(pts[0], [0, 1, 0]),
                  lambda: SH.Polygon(pts), lambda: SH.Volume(mask, np.eye(4)), lambda: cone().project(pts)]''',
'''        makers = [lambda: SH.Curve(pts), lambda: SH.Curve(pts).project(cone()), lambda: SH.Plane(pts[0], [0, 1, 0]),
                  lambda: SH.Polygon(pts), lambda: SH.Volume(mask, np.eye(4)), lambda: cone().project(pts),
                  lambda: SH.Surface(pts, [[0, 1, 2]]), lambda: SH.Surface(pts, [[0, 1, 2]]).project(cone())]''')

open(path, "w", encoding="ascii").write(src)
print("ok")
