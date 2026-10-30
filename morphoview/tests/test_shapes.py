"""The shapes beside the straight lines (morphoview.shapes), on cameras of FleXray's kind.

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
FleXray rendered."""
import itertools
import math
import unittest

import numpy as np

from morphometry.tests import phantom as P
from morphoview import projection as PJ
from morphoview import shapes as SH

TOL = SH.TOLERANCE_MM
EXACT = 1e-9


def distance_to_polyline(q: np.ndarray, pts: np.ndarray, closed: bool, chunk: int = 2000) -> np.ndarray:
    """Each point's distance from the nearest place on the polyline through pts, in the world or
    on a render."""
    ring = np.vstack([pts, pts[:1]]) if closed else pts
    a, ab = ring[:-1], np.diff(ring, axis=0)
    out = []
    for i in range(0, len(q), chunk):
        part = q[i:i + chunk]
        t = np.clip(((part[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0.0, 1.0)
        out.append(np.linalg.norm(part[:, None, :] - (a[None] + t[..., None] * ab[None]), axis=-1).min(axis=1))
    return np.concatenate(out)


def cone(**more) -> PJ.Camera:
    """A cone beam with its source 800 mm in front of the isocentre at the origin, looking along
    the world's -y."""
    view = dict(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=(0.0, 0.0, 0.0), sdd=1200.0,
                delx=1.0, height=200, width=240)
    view.update(more)
    return PJ.Camera(PJ.View(**view))


def parallel(**more) -> PJ.Camera:
    return cone(orthographic=True, **more)


def enlargement(cam: PJ.Camera, world: np.ndarray) -> float:
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
    side = np.stack([cross2(b - a, q - a) for a, b in zip(ring, np.roll(ring, -1, axis=0))], axis=1)
    return (side >= -1e-9).all(axis=1) | (side <= 1e-9).all(axis=1)


def cross2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
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


def catmull_rom_span(p: np.ndarray, alpha: float, s: np.ndarray) -> np.ndarray:
    """The Catmull-Rom span from p[1] to p[2] at s in 0 to 1, in Hermite form, its knots each
    chord's length to the power alpha apart: the centripetal span at 1/2, the uniform at 0 and the
    chordal at 1."""
    t = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1) ** alpha)])
    h = t[2] - t[1]
    m1 = h * ((p[1] - p[0]) / (t[1] - t[0]) - (p[2] - p[0]) / (t[2] - t[0]) + (p[2] - p[1]) / (t[2] - t[1]))
    m2 = h * ((p[2] - p[1]) / (t[2] - t[1]) - (p[3] - p[1]) / (t[3] - t[1]) + (p[3] - p[2]) / (t[3] - t[2]))
    s = s[:, None]
    return ((2 * s ** 3 - 3 * s ** 2 + 1) * p[1] + (s ** 3 - 2 * s ** 2 + s) * m1
            + (3 * s ** 2 - 2 * s ** 3) * p[2] + (s ** 3 - s ** 2) * m2)


class Curves(unittest.TestCase):
    def test_an_arc_keeps_within_its_tolerance_and_turns_the_right_handed_way(self):
        c, n = np.array([1.0, 2.0, 3.0]), SH.unit([0.3, -0.2, 0.9])
        start = c + 10.0 * SH.across(n)[0]
        arc = SH.arc(c, n, start, 250.0)
        e1 = (arc.points[0] - c) / 10.0
        e2 = np.cross(n, e1)
        t = np.linspace(0.0, math.radians(250.0), 20001)
        true = c + 10.0 * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
        self.assertLessEqual(distance_to_polyline(true, arc.points, False).max(), TOL)
        np.testing.assert_allclose(np.linalg.norm(arc.points - c, axis=1), 10.0, atol=EXACT)
        np.testing.assert_allclose(arc.points[0], start, atol=EXACT)
        np.testing.assert_allclose(arc.points[-1], true[-1], atol=EXACT)
        quarter = SH.arc([0, 0, 0], [0, 0, 1], [5, 0, 0], 90.0)
        np.testing.assert_allclose(quarter.points[-1], [0, 5, 0], atol=EXACT)

    def test_a_circle_and_an_ellipse_keep_within_their_tolerance(self):
        c, n = np.array([1.0, 2.0, 3.0]), np.array([0.3, -0.2, 0.9])
        circle = SH.circle(c, n, 12.0)
        self.assertTrue(circle.closed)
        e1, e2 = SH.across(n)
        t = np.linspace(0.0, 2.0 * math.pi, 20001)
        true = c + 12.0 * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
        self.assertLessEqual(distance_to_polyline(true, circle.points, True).max(), TOL)
        a, b = np.array([20.0, 0.0, 0.0]), np.array([0.0, 3.0, 0.0])
        ellipse = SH.ellipse(c, a, b)
        true = c + np.cos(t)[:, None] * a + np.sin(t)[:, None] * b
        self.assertLessEqual(distance_to_polyline(true, ellipse.points, True).max(), TOL)
        # every sample lies on the ellipse itself
        local = np.linalg.lstsq(np.stack([a, b], axis=1), (ellipse.points - c).T, rcond=None)[0]
        np.testing.assert_allclose((local ** 2).sum(axis=0), 1.0, atol=EXACT)
        with self.assertRaises(ValueError):
            SH.ellipse(c, a, [1.0, 3.0, 0.0])
        for radius in (-12.0, 0.0, math.nan):
            with self.assertRaises(ValueError):
                SH.circle(c, n, radius)

    def test_a_spline_passes_through_its_points_within_its_tolerance(self):
        rng = np.random.default_rng(3)
        pts = np.cumsum(rng.normal(size=(7, 3)) * [5.0, 5.0, 30.0], axis=0)
        for closed in (False, True):
            spline = SH.spline(pts, closed=closed)
            for p in pts:
                self.assertLess(np.linalg.norm(spline.points - p, axis=1).min(), EXACT)
            ext = (np.vstack([pts[-1:], pts, pts[:2]]) if closed
                   else np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]))
            spans = len(pts) if closed else len(pts) - 1
            dense = np.vstack([SH.catmull_rom(ext[i:i + 4], np.linspace(0.0, 1.0, 4001)) for i in range(spans)])
            self.assertLessEqual(distance_to_polyline(dense, spline.points, closed).max(), TOL)
        with self.assertRaises(ValueError):
            SH.spline([[0, 0, 0], [1, 1, 1], [1, 1, 1], [2, 0, 0]])

    def test_the_spline_is_the_centripetal_one(self):
        # The test above reads the spans from the module itself; here each of the spline's points
        # lies on the span its four points give in Hermite form, the knots the square root of each
        # chord apart, and half a millimetre or more off the uniform and the chordal spans.
        from scipy.spatial import cKDTree
        pts = np.array([[0.0, 0.0, 0.0], [30.0, 4.0, 0.0], [31.0, 9.0, 2.0], [60.0, 10.0, -3.0],
                        [62.0, 40.0, 1.0]])
        s = np.linspace(0.0, 1.0, 20001)
        for closed in (False, True):
            got = SH.spline(pts, closed=closed).points
            ext = (np.vstack([pts[-1:], pts, pts[:2]]) if closed
                   else np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]))
            spans = len(pts) if closed else len(pts) - 1
            off = {}
            for alpha in (0.5, 0.0, 1.0):
                dense = np.vstack([catmull_rom_span(ext[i:i + 4], alpha, s) for i in range(spans)])
                off[alpha] = float(cKDTree(dense).query(got)[0].max())
            self.assertLess(off[0.5], 1e-3)
            self.assertGreater(min(off[0.0], off[1.0]), 0.5)

    def test_a_straight_segment_stays_straight_on_the_render(self):
        a, b = np.array([-30.0, 40.0, -20.0]), np.array([25.0, -60.0, 35.0])
        for cam in (cone(rot_deg=(20.0, -10.0, 5.0)), parallel(rot_deg=(20.0, -10.0, 5.0))):
            inner = cam.project(a + np.linspace(0.0, 1.0, 50)[:, None] * (b - a)).uv
            ends = cam.project(np.stack([a, b])).uv
            d = (ends[1] - ends[0]) / np.linalg.norm(ends[1] - ends[0])
            off = (inner - ends[0]) @ np.array([-d[1], d[0]])
            self.assertLess(np.abs(off).max(), EXACT)

    def test_a_resampled_curve_keeps_its_corners_at_most_the_step_apart(self):
        corners = np.array([[-30.0, 40.0, -20.0], [25.0, -60.0, 35.0], [-30.0, 40.0, 10.0]])
        for closed in (False, True):
            curve = SH.Curve(corners, closed)
            fine = curve.resampled(0.7)
            self.assertEqual(fine.closed, closed)
            self.assertAlmostEqual(fine.length(), curve.length(), places=9)
            steps = np.linalg.norm(fine.segments()[:, 1] - fine.segments()[:, 0], axis=1)
            sides = np.linalg.norm(curve.segments()[:, 1] - curve.segments()[:, 0], axis=1)
            self.assertLessEqual(float(steps.max()), 0.7 + EXACT)
            self.assertEqual(len(steps), int(np.ceil(sides / 0.7).sum()))
            for p in corners:
                self.assertLess(float(np.linalg.norm(fine.points - p, axis=1).min()), EXACT)

    def test_a_curve_cut_by_the_source_plane_keeps_its_pieces_in_front(self):
        cam = cone()
        source = cam.source
        # a circle in a plane holding the beam, about a point 10 mm in front of the source, its
        # first point in front: the part in front runs through the first point and is one piece,
        # from one cut to the other
        ring = SH.circle(source + 10.0 * cam.beam, [1.0, 0.0, 0.0], 50.0)
        self.assertGreater(float(cam.camera_points(ring.points[:1])[0, 2]), SH.NEAR)
        got = ring.project(cam)
        self.assertFalse(got.closed)
        self.assertEqual(len(got.pieces()), 1)
        self.assertTrue((got.depth >= SH.NEAR * 0.999).all())
        front = ring.points[cam.camera_points(ring.points)[:, 2] > SH.NEAR]
        self.assertEqual(len(got.uv), len(front) + 2)
        self.assertGreater(len(front), len(ring.points) // 2)
        np.testing.assert_allclose(got.depth[[0, -1]], SH.NEAR, atol=1e-9)
        # an open curve dipping behind the source in its middle comes back in two pieces
        line = SH.Curve(np.stack([source + [-40.0, -100.0, 0.0], source + [0.0, 50.0, 0.0], source + [40.0, -100.0, 0.0]]))
        self.assertEqual(len(line.project(cam).pieces()), 2)
        with self.assertRaises(ValueError):
            SH.Curve(np.stack([source + [0.0, 10.0, 0.0], source + [5.0, 30.0, 0.0]])).project(cam)
        # under parallel rays nothing is cut
        self.assertEqual(len(line.project(parallel()).pieces()), 1)

    def test_a_ring_cut_three_times_keeps_each_piece_whole(self):
        # a ring about the beam's axis at the source, dipping behind the source's plane three
        # times: each piece left runs from one cut to the next through the points in front between
        # them, the one through the ring's first point joined across the ring's end, and nothing
        # else is left; with the first point behind, no piece runs across the end
        cam = cone()
        e1, e2 = SH.across(cam.beam)
        phi = np.radians(np.arange(0.0, 360.0, 20.0))
        for turn in (0.0, math.pi):
            depth = 10.0 * np.cos(3.0 * phi + turn)
            ring = SH.Curve(cam.source + 50.0 * (np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2)
                            + depth[:, None] * cam.beam, closed=True)
            got = ring.project(cam)
            self.assertFalse(got.closed)
            ends = list(got.starts[1:]) + [len(got.depth)]
            pieces = [got.depth[s:e] for s, e in zip(got.starts, ends)]
            self.assertEqual([len(p) for p in pieces], [5, 5, 5], turn)
            for piece in pieces:
                np.testing.assert_allclose(piece[[0, -1]], SH.NEAR, atol=1e-9)
                self.assertTrue(bool((piece[1:-1] > SH.NEAR).all()), turn)
            np.testing.assert_allclose(np.sort(np.concatenate([p[1:-1] for p in pieces])),
                                       np.sort(depth[depth > SH.NEAR]), atol=1e-9)
            self.assertEqual(len(got.world), len(got.uv))

    def test_a_circle_seen_through_parallel_rays_encloses_the_ellipses_area(self):
        cam = parallel(delx=0.8, dely=1.1)
        for tilt in (0.0, 30.0, 60.0):
            t = math.radians(tilt)
            # the beam runs along -y; the circle's normal turned tilt degrees from it towards x
            ring = SH.circle([3.0, -5.0, 2.0], [math.sin(t), math.cos(t), 0.0], 20.0, tolerance=0.001)
            area = ring.project(cam).area_px() * 0.8 * 1.1
            self.assertAlmostEqual(area / (math.pi * 400.0 * math.cos(t)), 1.0, delta=1e-4)


    def test_a_squares_length_and_area_on_the_render(self):
        # a square of 20 mm facing the beam at the isocentre, 800 mm from the source: 30 px a side
        # under the cone beam's magnification of 1.5 and 20 under parallel rays, at 1 mm a pixel
        corners = np.array([[-10.0, 0.0, -10.0], [10.0, 0.0, -10.0], [10.0, 0.0, 10.0], [-10.0, 0.0, 10.0]])
        for cam, side in ((cone(), 30.0), (parallel(), 20.0)):
            square = SH.Curve(corners, closed=True).project(cam)
            self.assertAlmostEqual(square.length_px(), 4.0 * side, places=9)
            self.assertAlmostEqual(square.area_px(), side * side, places=9)
            open_ = SH.Curve(corners).project(cam)
            self.assertAlmostEqual(open_.length_px(), 3.0 * side, places=9)
            with self.assertRaises(ValueError):
                open_.area_px()


class Planes(unittest.TestCase):
    def test_a_fitted_plane_is_the_plane_its_points_lie_on(self):
        rng = np.random.default_rng(5)
        n = SH.unit([0.2, -0.5, 0.8])
        e1, e2 = SH.across(n)
        p0 = np.array([4.0, -2.0, 7.0])
        uv = rng.uniform(-20.0, 20.0, size=(400, 2))
        noise = rng.normal(scale=0.3, size=400)
        pts = p0 + uv[:, :1] * e1 + uv[:, 1:] * e2 + noise[:, None] * n
        plane, rms = SH.Plane.fit(pts)
        self.assertLess(math.degrees(math.acos(min(1.0, abs(float(plane.normal @ n))))), 0.5)
        self.assertAlmostEqual(rms, float(np.sqrt(np.mean((noise - noise.mean()) ** 2))), delta=0.02)
        self.assertLess(abs(float(plane.distance(p0)[0])), 0.1)
        with self.assertRaises(ValueError):
            SH.Plane.fit([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        # four points 1 mm off the plane z = 0, above and below it in turn
        square, rms = SH.Plane.fit([[10, 10, 1], [-10, -10, 1], [10, -10, -1], [-10, 10, -1]])
        np.testing.assert_allclose(np.abs(square.normal), [0.0, 0.0, 1.0], atol=EXACT)
        self.assertAlmostEqual(rms, 1.0, places=12)

    def test_where_a_line_meets_a_plane_and_the_angle_between_planes(self):
        plane = SH.Plane([0.0, 0.0, 5.0], [0.0, 0.0, 2.0])
        np.testing.assert_allclose(plane.meet([1.0, 2.0, 0.0], [1.0, 2.0, 1.0]), [1.0, 2.0, 5.0], atol=EXACT)
        self.assertIsNone(plane.meet([0.0, 0.0, 0.0], [1.0, 0.0, 0.0]))
        self.assertAlmostEqual(plane.angle_deg(SH.Plane([0, 0, 0], [0.0, 1.0, 1.0])), 45.0, places=9)
        self.assertAlmostEqual(float(plane.distance([[0.0, 0.0, 8.0]])[0]), 3.0, places=12)

    def test_how_the_render_sees_a_plane(self):
        for cam in (cone(), parallel()):
            point = [0.0, 0.0, 0.0]
            beam = cam.ray_direction(point)[0]
            self.assertAlmostEqual(SH.Plane(point, beam).seen_at_deg(cam), 90.0, places=5)
            self.assertAlmostEqual(SH.Plane(point, np.cross(beam, [0.0, 0.0, 1.0])).seen_at_deg(cam), 0.0, places=5)

    def test_a_plane_off_the_beams_axis_is_seen_along_its_own_ray(self):
        # 18 degrees off the axis the cone beam's ray through the plane's point leaves the axis by
        # as much, so a plane facing the axis is seen at 72 degrees and one holding the axis's
        # direction at 18; parallel rays all run along the axis
        cone_, flat = cone(delx=4.0), parallel(delx=4.0)
        np.testing.assert_allclose(cone_.source, [0.0, 800.0, 0.0], atol=EXACT)
        np.testing.assert_allclose(cone_.beam, [0.0, -1.0, 0.0], atol=EXACT)
        point = np.array([800.0 * math.tan(math.radians(18.0)), 0.0, 0.0])
        for cam, facing, holding in ((cone_, 72.0, 18.0), (flat, 90.0, 0.0)):
            self.assertTrue(bool(cam.project(point[None]).in_beam.all()))
            self.assertAlmostEqual(SH.Plane(point, [0.0, 1.0, 0.0]).seen_at_deg(cam), facing, places=9)
            self.assertAlmostEqual(SH.Plane(point, [1.0, 0.0, 0.0]).seen_at_deg(cam), holding, places=9)

    def test_a_patch_is_the_rectangle_it_is_asked_for(self):
        plane = SH.Plane([1.0, 2.0, 3.0], [0.0, 0.0, 1.0])
        patch = plane.patch(4.0, 2.5, toward=[1.0, 1.0, 9.0])
        self.assertAlmostEqual(patch.area(), 4 * 4.0 * 2.5, places=9)
        sides = np.diff(np.vstack([patch.corners, patch.corners[:1]]), axis=0)
        np.testing.assert_allclose(np.linalg.norm(sides, axis=1), [8.0, 5.0, 8.0, 5.0], atol=EXACT)
        np.testing.assert_allclose(sides[0] / 8.0, SH.unit([1.0, 1.0, 0.0]), atol=EXACT)
        np.testing.assert_allclose(patch.corners.mean(axis=0), plane.point, atol=EXACT)
        np.testing.assert_allclose(np.abs(patch.plane().normal), [0.0, 0.0, 1.0], atol=EXACT)
        triangle = SH.Polygon([[0, 0, 0], [3, 0, 0], [0, 4, 0]])
        self.assertAlmostEqual(triangle.area(), 6.0, places=12)


class OnTheRender(unittest.TestCase):
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
            SH.Surface.over(plane, lambda u, v: np.where(u > 0.0, math.nan, 0.0), 20.0, 12.0)

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
        # a point given twice falls on its own place in the plane and is taken once
        twice = SH.Surface.through(np.vstack([points, points[:1]]))
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
            # no centre so near the rim that rounding could put it either side
            self.assertGreater(float(distance_to_polyline(centres, rim.uv, True).min()), 1e-6)
        # a flat one shades what the patch it is encloses
        cam = cone(**small)
        plane = SH.Plane(on_axis(cam, 790.0), SH.unit(cam.beam + [0.2, 0.1, -0.3]))
        flat = SH.Surface.over(plane, lambda u, v: 0.0 * u, 14.0, 9.0, toward=[1.0, 0.0, 0.0])
        patch = plane.patch(14.0, 9.0, toward=[1.0, 0.0, 0.0]).project(cam)
        self.assertAlmostEqual(flat.project(cam).area_px() / patch.area_px(), 1.0, places=9)
        inside = in_convex(cam.pixel_centres(), patch.uv).reshape(cam.view.height, cam.view.width)
        np.testing.assert_array_equal(flat.silhouette(cam), inside)

    def test_a_surface_reaching_behind_the_source_is_refused(self):
        # a surface 5 mm in front of the source is drawn; one whose plane holds the source,
        # across its plane, is refused, but not under parallel rays, which reach behind nothing
        # they render and see it edge on, as a line that shades no pixel
        cam = cone()
        ahead = SH.Surface.over(SH.Plane(cam.source, cam.beam), lambda u, v: 5.0 + 0.0 * u, 10.0, 10.0)
        self.assertTrue(bool((ahead.project(cam).depth > SH.NEAR).all()))
        across = SH.Surface.over(SH.Plane(cam.source, cam.to_world[:3, 0]), lambda u, v: 0.0 * u, 10.0, 10.0)
        with self.assertRaises(ValueError):
            across.project(cam)
        with self.assertRaises(ValueError):
            across.silhouette(cam)
        self.assertEqual(int(across.silhouette(parallel()).sum()), 0)


class Volumes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = 0.5
        cls.R = 10.0
        cls.centre = np.array([12.1, 11.9, 12.05])
        grid = np.indices((48, 48, 48)).reshape(3, -1).T * cls.h
        cls.mask = (np.linalg.norm(grid - cls.centre, axis=1) <= cls.R).reshape(48, 48, 48)
        cls.affine = np.diag([cls.h, cls.h, cls.h, 1.0])
        cls.ball = SH.Volume(cls.mask, cls.affine)

    def camera(self, orthographic: bool, **more) -> PJ.Camera:
        view = dict(rot_deg=(10.0, 20.0, 5.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=tuple(self.centre),
                    sdd=1200.0, delx=0.7, height=48, width=48, orthographic=orthographic)
        view.update(more)
        return PJ.Camera(PJ.View(**view))

    def oblique(self) -> PJ.Camera:
        """A cone beam whose ray to the ball's centre leaves its axis by 18 degrees, the source
        moved across the axis and the principal point moved so the ball's shadow stays on the
        detector."""
        more = dict(xyz_mm=(800.0 * math.tan(math.radians(18.0)), 800.0, 0.0), height=56, width=56)
        uv = self.camera(False, **more).project(self.centre[None]).uv[0]
        return self.camera(False, x0=(28.0 - float(uv[0])) * 0.7, y0=(28.0 - float(uv[1])) * 0.7, **more)

    def chords(self, cam: PJ.Camera, radius: float) -> np.ndarray:
        src, det = cam.rays(cam.pixel_centres())
        d = (det - src) / np.linalg.norm(det - src, axis=1, keepdims=True)
        w = self.centre - src
        perp = np.linalg.norm(w - (w * d).sum(axis=1, keepdims=True) * d, axis=1)
        return 2.0 * np.sqrt(np.clip(radius ** 2 - perp ** 2, 0.0, None))

    def test_a_balls_fine_path_lengths_are_its_chords_through_its_voxels(self):
        # a point's nearest voxel centre lies within half a voxel's diagonal of it, so the voxels
        # of the ball hold the ball shrunk by that much and lie within it grown by that much; the
        # fine sampling counts each step of half a voxel by its midpoint
        step = 0.5 * self.h
        slack = math.sqrt(3.0) / 2.0 * self.h
        oblique = self.oblique()
        towards = SH.unit(self.centre - oblique.source)
        self.assertAlmostEqual(math.degrees(math.acos(float(towards @ oblique.beam))), 18.0, delta=0.01)
        for cam in (self.camera(True), self.camera(False), oblique):
            got = self.ball.path_length(cam).ravel()
            np.testing.assert_array_equal(got, self.ball.path_length(cam, step=step).ravel())
            self.assertGreater(int((got > 0).sum()), 500)
            low = self.chords(cam, self.R - slack) - step
            high = self.chords(cam, self.R + slack) + step
            self.assertTrue((got >= low - EXACT).all() and (got <= high + EXACT).all())
            inner = self.chords(cam, self.R - 1.0) > 0
            self.assertLess(float(np.median(np.abs(got - self.chords(cam, self.R))[inner])), self.h)

    def test_parallel_path_lengths_sum_to_the_volume(self):
        cam = self.camera(True, delx=0.3, height=110, width=110)
        total = float(self.ball.path_length(cam).sum()) * 0.3 * 0.3
        self.assertAlmostEqual(total / self.ball.volume_mm3(), 1.0, delta=0.005)

    def test_flexrays_window_over_each_ray_skips_none_of_nanodrrs_points(self):
        # the module reads only a ray's points within a step of the volume's box; here every one
        # of nanoDRR's n points from the source to the detector is counted, so a point the window
        # left out is seen, on the ball and on a block, whose shadow fills the outline of its
        # box, so a ray left out at the outline's edge is seen too; tests/test_projection.py
        # holds the counts to FleXray's own
        block = np.zeros_like(self.mask)
        block[14:34, 16:30, 18:32] = True
        for volume, orthographic in itertools.product((self.ball, SH.Volume(block, self.affine)), (True, False)):
            cam = self.camera(orthographic, height=40, width=36, x0=3.0)
            for n in (500, 77):
                got = volume.path_length(cam, n_samples=n)
                src, det = cam.rays(cam.pixel_centres())
                to_voxel = np.linalg.inv(self.affine)
                a = src @ to_voxel[:3, :3].T + to_voxel[:3, 3]
                b = det @ to_voxel[:3, :3].T + to_voxel[:3, 3]
                t = np.arange(n) / (n - 1.0)
                pts = a[:, None, :] + t[None, :, None] * (b - a)[:, None, :]
                hits = volume.inside(pts).sum(axis=1)
                want = hits * np.linalg.norm(det - src, axis=1) / (n - 1)
                np.testing.assert_allclose(got.ravel(), want, rtol=0, atol=1e-9)
                if n == 500:
                    self.assertGreater(int((want > 0).sum()), 100)

    def test_a_rays_samples_are_the_same_either_way_along_it(self):
        # the fine sampling reads the middles of its steps and FleXray's points run evenly from end
        # to end, so a ray run the other way reads the same points, where taking each step at its
        # start would move a point in half a step; but a ray that crosses the box from one face to
        # the face opposite runs a whole number of voxels along that axis, so a middle can fall on
        # a voxel's face to the last bit, and the two ways' rounding can put it either side: no
        # more than one ray in fifty, by one step
        step = 0.5 * self.h
        cam = self.oblique()
        src, det = cam.rays(cam.pixel_centres())
        to_voxel = np.linalg.inv(self.affine)
        a, b = (p @ to_voxel[:3, :3].T + to_voxel[:3, 3] for p in (src, det))
        length = np.linalg.norm(det - src, axis=1)
        lo, hi = self.ball.box()
        forth = self.ball.fine_samples(a, b, length, lo, hi, step)
        moved = np.abs(self.ball.fine_samples(b, a, length, lo, hi, step) - forth)
        self.assertGreater(int((forth > 0).sum()), 1000)
        self.assertLess(int((moved > EXACT).sum()), int((forth > 0).sum()) // 50)
        self.assertLessEqual(float(moved.max()), step + EXACT)
        forth = self.ball.flexray_samples(a, b, length, 500, lo, hi)
        np.testing.assert_allclose(self.ball.flexray_samples(b, a, length, 500, lo, hi), forth, rtol=0, atol=1e-9)

    def test_the_largest_piece_and_the_box(self):
        lab = np.zeros((20, 20, 20), np.int16)
        lab[2:5, 2:5, 2:5] = 7
        lab[10:18, 10:18, 10:18] = 7
        lab[0, 19, 0] = 8
        big = SH.Volume.from_labels(lab, np.eye(4), 7)
        self.assertEqual(int(big.mask.sum()), 512)
        both = SH.Volume.from_labels(lab, np.eye(4), [7, 8], largest=False)
        self.assertEqual(int(both.mask.sum()), 27 + 512 + 1)
        lo, hi = big.box()
        np.testing.assert_allclose(lo, [9.5, 9.5, 9.5])
        np.testing.assert_allclose(hi, [17.5, 17.5, 17.5])
        with self.assertRaises(ValueError):
            SH.Volume.from_labels(lab, np.eye(4), 9)
        # two blocks meeting only along an edge are two pieces, so the larger single block is taken
        edge = np.zeros((20, 20, 20), np.int16)
        edge[0:2, 0:3, 0:5] = 7
        edge[10:12, 10:12, 10:15] = 7
        edge[12:14, 12:14, 10:15] = 7
        self.assertEqual(int(SH.Volume.from_labels(edge, np.eye(4), 7).mask.sum()), 30)

    def test_a_volume_behind_the_source_is_refused(self):
        cam = self.camera(False, xyz_mm=(0.0, 5.0, 0.0))
        with self.assertRaises(ValueError):
            self.ball.path_length(cam)


class Identity(unittest.TestCase):
    def test_a_shape_is_equal_only_to_itself(self):
        pts = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [0.0, 0.0, 10.0]])
        mask = np.zeros((4, 4, 4), bool)
        mask[1, 1, 1] = True
        makers = [lambda: SH.Curve(pts), lambda: SH.Curve(pts).project(cone()), lambda: SH.Plane(pts[0], [0, 1, 0]),
                  lambda: SH.Polygon(pts), lambda: SH.Volume(mask, np.eye(4)), lambda: cone().project(pts),
                  lambda: SH.Surface(pts, [[0, 1, 2]]), lambda: SH.Surface(pts, [[0, 1, 2]]).project(cone())]
        for make in makers:
            one, other = make(), make()
            self.assertTrue(one == one and one != other and one in [other, one])
            self.assertEqual(len({one, other, one}), 2)


class Points(unittest.TestCase):
    def test_a_points_pixel_is_the_cell_it_falls_in(self):
        got = PJ.Projected(uv=np.array([[0.0, 0.0], [3.99, 7.01], [10.5, 2.5]]), depth=np.ones(3),
                           in_beam=np.ones(3, bool))
        np.testing.assert_array_equal(got.pixels(), [[0, 0], [7, 3], [2, 10]])


if __name__ == "__main__":
    unittest.main()
