"""The shapes review's tests, each an exact replacement in morphoview/tests/test_shapes.py."""
import sys

path = sys.argv[1]
text = open(path, encoding="ascii").read()
EDITS = [
    # the module docstring
    ("""points is the plane they lie on; a circle seen through parallel rays encloses the ellipse's area;
and a volume's path lengths are its chords through its voxels, by the fine sampling and by
FleXray's, the latter counted again here point by point.\"\"\"""",
     """points is the plane they lie on, and a plane off the beam's axis is seen along its own ray; a
circle seen through parallel rays encloses the ellipse's area; a volume's path lengths are its
chords through its voxels, on oblique rays too, by the fine sampling and by FleXray's, the latter
counted again here point by point, and both samplings read a ray the same either way along it; and
a shape is equal only to itself.\"\"\""""),
    # a circle of no radius
    ("""        with self.assertRaises(ValueError):
            SH.ellipse(c, a, [1.0, 3.0, 0.0])
""",
     """        with self.assertRaises(ValueError):
            SH.ellipse(c, a, [1.0, 3.0, 0.0])
        for radius in (-12.0, 0.0, math.nan):
            with self.assertRaises(ValueError):
                SH.circle(c, n, radius)
"""),
    # resampling, taken out of the straight segment's test into one of its own
    ("""            self.assertLess(np.abs(off).max(), EXACT)
        curve = SH.Curve(np.stack([a, b, a + [0.0, 0.0, 30.0]]))
        self.assertAlmostEqual(curve.resampled(0.7).length(), curve.length(), places=9)
""",
     """            self.assertLess(np.abs(off).max(), EXACT)

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
"""),
    # a ring cut three times
    ("""        # under parallel rays nothing is cut
        self.assertEqual(len(line.project(parallel()).pieces()), 1)
""",
     """        # under parallel rays nothing is cut
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
"""),
    # a square's length and area on the render
    ("""class Planes(unittest.TestCase):""",
     """    def test_a_squares_length_and_area_on_the_render(self):
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


class Planes(unittest.TestCase):"""),
    # a plane fitted exactly
    ("""        with self.assertRaises(ValueError):
            SH.Plane.fit([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
""",
     """        with self.assertRaises(ValueError):
            SH.Plane.fit([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        # four points 1 mm off the plane z = 0, above and below it in turn
        square, rms = SH.Plane.fit([[10, 10, 1], [-10, -10, 1], [10, -10, -1], [-10, 10, -1]])
        np.testing.assert_allclose(np.abs(square.normal), [0.0, 0.0, 1.0], atol=EXACT)
        self.assertAlmostEqual(rms, 1.0, places=12)
"""),
    # a plane off the beam's axis
    ("""            self.assertAlmostEqual(SH.Plane(point, np.cross(beam, [0.0, 0.0, 1.0])).seen_at_deg(cam), 0.0, places=5)
""",
     """            self.assertAlmostEqual(SH.Plane(point, np.cross(beam, [0.0, 0.0, 1.0])).seen_at_deg(cam), 0.0, places=5)

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
"""),
    # the patch's sides
    ("""        self.assertAlmostEqual(patch.area(), 4 * 4.0 * 2.5, places=9)
        side = patch.corners[1] - patch.corners[0]
        np.testing.assert_allclose(side / np.linalg.norm(side), SH.unit([1.0, 1.0, 0.0]), atol=EXACT)
""",
     """        self.assertAlmostEqual(patch.area(), 4 * 4.0 * 2.5, places=9)
        sides = np.diff(np.vstack([patch.corners, patch.corners[:1]]), axis=0)
        np.testing.assert_allclose(np.linalg.norm(sides, axis=1), [8.0, 5.0, 8.0, 5.0], atol=EXACT)
        np.testing.assert_allclose(sides[0] / 8.0, SH.unit([1.0, 1.0, 0.0]), atol=EXACT)
        np.testing.assert_allclose(patch.corners.mean(axis=0), plane.point, atol=EXACT)
"""),
    # an oblique camera for the ball
    ("""    def chords(self, cam: PJ.Camera, radius: float) -> np.ndarray:""",
     """    def oblique(self) -> PJ.Camera:
        \"\"\"A cone beam whose ray to the ball's centre leaves its axis by 18 degrees, the source
        moved across the axis and the principal point moved so the ball's shadow stays on the
        detector.\"\"\"
        more = dict(xyz_mm=(800.0 * math.tan(math.radians(18.0)), 800.0, 0.0), height=56, width=56)
        uv = self.camera(False, **more).project(self.centre[None]).uv[0]
        return self.camera(False, x0=(28.0 - float(uv[0])) * 0.7, y0=(28.0 - float(uv[1])) * 0.7, **more)

    def chords(self, cam: PJ.Camera, radius: float) -> np.ndarray:"""),
    ("""        step = 0.5 * self.h
        slack = math.sqrt(3.0) / 2.0 * self.h
        for cam in (self.camera(True), self.camera(False)):
            got = self.ball.path_length(cam).ravel()
""",
     """        step = 0.5 * self.h
        slack = math.sqrt(3.0) / 2.0 * self.h
        oblique = self.oblique()
        towards = SH.unit(self.centre - oblique.source)
        self.assertAlmostEqual(math.degrees(math.acos(float(towards @ oblique.beam))), 18.0, delta=0.01)
        for cam in (self.camera(True), self.camera(False), oblique):
            got = self.ball.path_length(cam).ravel()
            np.testing.assert_array_equal(got, self.ball.path_length(cam, step=step).ravel())
            self.assertGreater(int((got > 0).sum()), 1000)
"""),
    # both samplings either way along a ray
    ("""    def test_the_largest_piece_and_the_box(self):""",
     """    def test_a_rays_samples_are_the_same_either_way_along_it(self):
        # the fine sampling reads the middles of its steps and FleXray's points run evenly from end
        # to end, so a ray run the other way reads the same points; the starts of the steps would not
        cam = self.oblique()
        src, det = cam.rays(cam.pixel_centres())
        to_voxel = np.linalg.inv(self.affine)
        a, b = (p @ to_voxel[:3, :3].T + to_voxel[:3, 3] for p in (src, det))
        length = np.linalg.norm(det - src, axis=1)
        lo, hi = self.ball.box()
        forth = self.ball.fine_samples(a, b, length, lo, hi, 0.5 * self.h)
        np.testing.assert_allclose(self.ball.fine_samples(b, a, length, lo, hi, 0.5 * self.h), forth, rtol=0, atol=1e-9)
        self.assertGreater(int((forth > 0).sum()), 1000)
        forth = self.ball.flexray_samples(a, b, length, 500, lo, hi)
        np.testing.assert_allclose(self.ball.flexray_samples(b, a, length, 500, lo, hi), forth, rtol=0, atol=1e-9)

    def test_the_largest_piece_and_the_box(self):"""),
    # face-connected pieces
    ("""        with self.assertRaises(ValueError):
            SH.Volume.from_labels(lab, np.eye(4), 9)
""",
     """        with self.assertRaises(ValueError):
            SH.Volume.from_labels(lab, np.eye(4), 9)
        # two blocks meeting only along an edge are two pieces, so the larger single block is taken
        edge = np.zeros((20, 20, 20), np.int16)
        edge[0:2, 0:3, 0:5] = 7
        edge[10:12, 10:12, 10:15] = 7
        edge[12:14, 12:14, 10:15] = 7
        self.assertEqual(int(SH.Volume.from_labels(edge, np.eye(4), 7).mask.sum()), 30)
"""),
    # identity
    ("""class Points(unittest.TestCase):""",
     """class Identity(unittest.TestCase):
    def test_a_shape_is_equal_only_to_itself(self):
        pts = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [0.0, 0.0, 10.0]])
        mask = np.zeros((4, 4, 4), bool)
        mask[1, 1, 1] = True
        makers = [lambda: SH.Curve(pts), lambda: SH.Curve(pts).project(cone()), lambda: SH.Plane(pts[0], [0, 1, 0]),
                  lambda: SH.Polygon(pts), lambda: SH.Volume(mask, np.eye(4)), lambda: cone().project(pts)]
        for make in makers:
            one, other = make(), make()
            self.assertTrue(one == one and one != other and one in [other, one])
            self.assertEqual(len({one, other, one}), 2)


class Points(unittest.TestCase):"""),
]
for old, new in EDITS:
    if text.count(old) != 1:
        sys.exit("not found once: %r" % old[:80])
    text = text.replace(old, new)
open(path, "w", encoding="ascii", newline="\n").write(text)
print("test_shapes.py: %d edits" % len(EDITS))
