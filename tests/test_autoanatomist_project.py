"""The projection of the oracle's constructions into FleXray and FluXray views (project.py).

    python -m unittest discover -s tests -v          # from the repository's root, in the venv

The camera reproduces nanodrr's composition (camera-to-world = pose @ reorient, the source at
R t + iso, pixel centres at u + 1/2): the isocentre lands on the detector's centre at the
magnification SDD / SOD, an offset across the beam is magnified by it, alpha 0 is an AP view hung
as a film (head up, the patient's left on the image's right), alpha +90 and -90 are the two
laterals, beta tilts the beam along the column, an orthographic camera magnifies nothing, and
projecting then back-projecting returns the point. FluXray's index runs y, then z, then alpha,
and its stored 256-pixel image is the 1024-pixel detector with pixels four times as wide. A
chord across the beam keeps its length and one along the beam vanishes; the engine's lines, by
duck typing, and tuples project alike, with their extra lines; the readability rules and the
view named against a frame give what their definitions say; and a phantom read by the oracle
keeps its widths in the AP view and its depths in the lateral, by the measurements' own rules.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from types import SimpleNamespace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from autoanatomist import oracle as O                             # noqa: E402
from autoanatomist import phantom as PH                           # noqa: E402
from autoanatomist import project as PJ                           # noqa: E402
from autoanatomist import specs as S                              # noqa: E402

ISO = (10.0, -20.0, 30.0)
SOD, SDD, PITCH, SIZE = 800.0, 1200.0, 1.0, 256


def camera(alpha=0.0, beta=0.0, gamma=0.0, xyz=(0.0, SOD, 0.0), sdd=SDD, pitch=PITCH, size=SIZE, iso=ISO,
           orthographic=False, orientation="AP"):
    return PJ.Camera.flexray(alpha, beta, gamma, xyz, sdd, pitch, pitch, size, size, iso, orthographic, orientation)


def frame_at(origin):
    return SimpleNamespace(origin=np.asarray(origin, float), ex=np.array([1.0, 0.0, 0.0]),
                           ey=np.array([0.0, 1.0, 0.0]), ez=np.array([0.0, 0.0, 1.0]))


class TheCamera(unittest.TestCase):
    def test_the_isocentre_lands_on_the_detectors_centre(self):
        cam = camera()
        P = cam.project(np.array([ISO]))
        self.assertAlmostEqual(float(P.u[0]), SIZE / 2 - 0.5, places=9)
        self.assertAlmostEqual(float(P.v[0]), SIZE / 2 - 0.5, places=9)
        self.assertAlmostEqual(float(P.magnification[0]), SDD / SOD, places=12)
        self.assertAlmostEqual(float(P.depth[0]), SOD, places=9)
        self.assertTrue(bool(P.visible[0]))

    def test_an_offset_across_the_beam_is_magnified(self):
        cam = camera()
        across = cam.camera_axes[:, 0]                              # the camera's x in the world
        np.testing.assert_allclose(across, [-1.0, 0.0, 0.0], atol=1e-12)
        P = cam.project(np.array([np.asarray(ISO) + 10.0 * across]))
        self.assertAlmostEqual(float(P.mm_u[0]), 10.0 * SDD / SOD, places=9)
        self.assertAlmostEqual(float(P.u[0]), SIZE / 2 - 0.5 + 10.0 * SDD / SOD / PITCH, places=9)
        self.assertAlmostEqual(float(P.mm_v[0]), 0.0, places=9)

    def test_alpha_0_is_an_ap_view_hung_as_a_film(self):
        cam = camera()
        np.testing.assert_allclose(cam.source, np.asarray(ISO) + [0.0, SOD, 0.0], atol=1e-9)
        iso = np.asarray(ISO)
        centre = SIZE / 2 - 0.5
        up = cam.project(np.array([iso + [0.0, 0.0, 50.0]]))
        left = cam.project(np.array([iso + [-50.0, 0.0, 0.0]]))   # the patient's left is -x in RAS
        self.assertLess(float(up.v[0]), centre)                     # the head is up
        self.assertGreater(float(left.u[0]), centre)                # the patient's left on the image's right
        np.testing.assert_allclose(cam.beam(iso[None, :])[0], [0.0, -1.0, 0.0], atol=1e-12)

    def test_the_two_laterals(self):
        iso = np.asarray(ISO)
        centre = SIZE / 2 - 0.5
        from_left = camera(alpha=90.0)
        np.testing.assert_allclose(from_left.source, iso + [-SOD, 0.0, 0.0], atol=1e-9)
        front = from_left.project(np.array([iso + [0.0, 50.0, 0.0]]))
        self.assertLess(float(front.u[0]), centre)                  # the front of the body on the image's left
        from_right = camera(alpha=-90.0)
        np.testing.assert_allclose(from_right.source, iso + [SOD, 0.0, 0.0], atol=1e-9)
        front = from_right.project(np.array([iso + [0.0, 50.0, 0.0]]))
        self.assertGreater(float(front.u[0]), centre)
        for cam in (from_left, from_right):
            up = cam.project(np.array([iso + [0.0, 0.0, 50.0]]))
            self.assertLess(float(up.v[0]), centre)

    def test_beta_tilts_the_beam_along_the_column(self):
        cam = camera(beta=20.0)
        d = cam.beam(np.asarray(ISO)[None, :])[0]
        self.assertAlmostEqual(abs(float(d[2])), np.sin(np.radians(20.0)), places=9)
        self.assertNotAlmostEqual(float(cam.source[2]), ISO[2])
        np.testing.assert_allclose(PJ.rotation_zxy(30.0, 20.0, 10.0),
                                   PJ.rotation_z(30.0) @ PJ.rotation_x(20.0) @ PJ.rotation_y(10.0), atol=1e-12)

    def test_rt_inv_is_nanodrrs_composition(self):
        cam = camera(alpha=35.0, beta=-12.0, gamma=7.0, xyz=(30.0, 700.0, -40.0))
        R = PJ.rotation_zxy(35.0, -12.0, 7.0)
        pose = np.eye(4)
        pose[:3, :3] = R
        pose[:3, 3] = R @ np.array([30.0, 700.0, -40.0]) + np.asarray(ISO)
        reorient = np.eye(4)
        reorient[:3, :3] = PJ.REORIENT["AP"]
        np.testing.assert_allclose(cam.rt_inv, pose @ reorient, atol=1e-9)
        X = np.array([[12.0, -3.0, 44.0]])
        local = cam.to_camera(X)
        back = (cam.rt_inv @ np.append(local[0], 1.0))[:3]
        np.testing.assert_allclose(back, X[0], atol=1e-9)

    def test_orthographic_rays_are_parallel(self):
        cam = camera(orthographic=True)
        iso = np.asarray(ISO)
        across = cam.camera_axes[:, 0]
        along = cam.camera_axes[:, 2]
        P = cam.project(np.stack([iso + 10.0 * across, iso + 10.0 * across + 200.0 * along]))
        np.testing.assert_allclose(P.magnification, 1.0)
        self.assertAlmostEqual(float(P.u[0]), float(P.u[1]), places=9)
        self.assertAlmostEqual(float(P.mm_u[0]), 10.0, places=9)

    def test_project_and_back_project_agree(self):
        rng = np.random.default_rng(3)
        X = np.asarray(ISO) + rng.uniform(-80.0, 80.0, (20, 3))
        for cam in (camera(alpha=50.0, beta=10.0, gamma=-5.0), camera(orthographic=True, alpha=-20.0)):
            P = cam.project(X)
            np.testing.assert_allclose(cam.back_project(P.u, P.v, P.depth), X, atol=1e-8)

    def test_pixel_centres_follow_nanodrr(self):
        cam = camera()
        X = cam.back_project(np.array([0.0]), np.array([0.0]), np.array([SOD]))
        local = cam.to_camera(X)[0]
        self.assertAlmostEqual(float(local[0]), (0.5 - cam.cx) * PITCH * SOD / SDD, places=9)
        self.assertAlmostEqual(float(local[1]), (0.5 - cam.cy) * PITCH * SOD / SDD, places=9)

    def test_visibility(self):
        cam = camera()
        iso = np.asarray(ISO)
        behind = iso + [0.0, SOD + 10.0, 0.0]                        # behind the source
        off = iso + [500.0, 0.0, 0.0]                                 # beyond the detector's edge
        nan = np.full(3, np.nan)
        P = cam.project(np.stack([iso, behind, off, nan]))
        self.assertEqual(P.visible.tolist(), [True, False, False, False])

    def test_the_record_round_trips(self):
        cam = camera(alpha=35.0, beta=-12.0, gamma=7.0, xyz=(30.0, 700.0, -40.0), orthographic=True)
        again = PJ.Camera.from_record(json.loads(json.dumps(cam.record())))
        self.assertEqual(again, cam)
        rec = {"rot_deg": [35.0, -12.0, 7.0], "xyz_mm": [30.0, 700.0, -40.0], "orthographic": False,
               "sdd": SDD, "delx": PITCH, "grid": None}
        cam2 = PJ.camera_from_pose_record(rec, ISO, SIZE, SIZE)
        np.testing.assert_allclose(cam2.rt_inv, camera(alpha=35.0, beta=-12.0, gamma=7.0,
                                                       xyz=(30.0, 700.0, -40.0)).rt_inv, atol=1e-9)
        with self.assertRaises(ValueError):
            camera(orientation="LAT")

    def test_the_volume_centre(self):
        affine = np.array([[0.8, 0.0, 0.0, 5.0], [0.0, 0.8, 0.0, -2.0], [0.0, 0.0, 2.5, 7.0], [0.0, 0.0, 0.0, 1.0]])
        np.testing.assert_allclose(PJ.volume_centre(affine, (11, 21, 5)), [5.0 + 4.0, -2.0 + 8.0, 7.0 + 5.0])


class FluXray(unittest.TestCase):
    def test_the_pose_index(self):
        self.assertEqual(PJ.fluxray_pose(0), (0.0, 650.0, -300.0))
        self.assertEqual(PJ.fluxray_pose(1), (45.0, 650.0, -300.0))
        self.assertEqual(PJ.fluxray_pose(2), (-45.0, 650.0, -300.0))
        self.assertEqual(PJ.fluxray_pose(5), (0.0, 650.0, -200.0))
        self.assertEqual(PJ.fluxray_pose(30), (0.0, 900.0, -300.0))
        self.assertEqual(PJ.fluxray_pose(89), (-90.0, 1150.0, 200.0))
        self.assertEqual(PJ.FLUXRAY_POSES, 90)
        with self.assertRaises(ValueError):
            PJ.fluxray_pose(90)

    def test_the_grid_camera_and_its_stored_image(self):
        full = PJ.Camera.fluxray(7, ISO)
        stored = PJ.Camera.fluxray(7, ISO, PJ.FLUXRAY_STORED_PX)
        self.assertEqual((full.width, full.delx, full.sdd), (1024, 0.6, 1250.0))
        self.assertEqual((stored.width, stored.delx), (256, 2.4))
        alpha, y, z = PJ.fluxray_pose(7)
        self.assertEqual(full.rotation, (alpha, 0.0, 0.0))
        self.assertEqual(full.translation, (0.0, y, z))
        rng = np.random.default_rng(1)
        X = np.asarray(ISO) + rng.uniform(-150.0, 150.0, (12, 3))
        a, b = full.project(X), stored.project(X)
        np.testing.assert_allclose((a.u + 0.5) / 4.0 - 0.5, b.u, atol=1e-9)
        np.testing.assert_allclose((a.v + 0.5) / 4.0 - 0.5, b.v, atol=1e-9)
        np.testing.assert_allclose(a.magnification, b.magnification)
        np.testing.assert_allclose(full.project(np.array([ISO])).magnification, [1250.0 / y])


class FakeLine:
    def __init__(self, key, level, a, b, value, extra=None):
        self.key, self.level, self.a, self.b, self.value = key, level, np.asarray(a), np.asarray(b), value
        self.extra = extra or {}


class Segments(unittest.TestCase):
    def test_across_the_beam_keeps_its_length_and_along_it_vanishes(self):
        cam = camera()
        iso = np.asarray(ISO)
        width = PJ.project_pair(cam, "endplate", "L3", iso + [-20.0, 0.0, 0.0], iso + [20.0, 0.0, 0.0])
        self.assertAlmostEqual(width.detector_mm, 40.0 * SDD / SOD, places=9)
        self.assertAlmostEqual(width.object_mm, 40.0, places=9)
        self.assertAlmostEqual(width.foreshortening, 1.0, places=9)
        self.assertTrue(width.visible and width.readable)
        depth = PJ.project_pair(cam, "endplate_depth", "L3", iso + [0.0, -15.0, 0.0], iso + [0.0, 15.0, 0.0])
        self.assertAlmostEqual(depth.foreshortening, 0.0, places=9)
        self.assertFalse(depth.readable)
        self.assertEqual(depth.true_mm, 30.0)
        for cam2 in (cam, camera(alpha=90.0)):
            height = PJ.project_pair(cam2, "h_post", "L3", iso + [0.0, 0.0, -12.0], iso + [0.0, 0.0, 12.0])
            self.assertAlmostEqual(height.foreshortening, 1.0, places=9)
        lateral = PJ.project_pair(camera(alpha=90.0), "endplate_depth", "L3", iso + [0.0, -15.0, 0.0],
                                  iso + [0.0, 15.0, 0.0])
        self.assertAlmostEqual(lateral.foreshortening, 1.0, places=9)

    def test_lines_tuples_and_segments_project_alike(self):
        cam = camera()
        iso = np.asarray(ISO)
        a, b = iso + [-20.0, 0.0, 0.0], iso + [20.0, 0.0, 0.0]
        line = FakeLine("endplate", "L3", a, b, 40.0, {"lower plate": (a - [0.0, 0.0, 25.0], b - [0.0, 0.0, 25.0])})
        images = PJ.project_segments(cam, [line, ("endplate", "L3", a, b, 40.0), PJ.Segment("endplate", "L3", a, b)])
        for im in images:
            self.assertAlmostEqual(im.object_mm, 40.0, places=9)
            np.testing.assert_allclose(im.a_uv, images[0].a_uv)
        self.assertIn("lower plate", images[0].extra)
        self.assertGreater(float(images[0].extra["lower plate"].a_uv[1]), float(images[0].a_uv[1]))
        rows = PJ.truth_rows(images)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[1]["key"], "endplate: lower plate")
        json.dumps(rows)
        self.assertEqual(PJ.segments_from([line])[0].value, 40.0)
        self.assertTrue(np.isnan(PJ.segments_from([("k", "L1", a, b)])[0].value))


class ReadabilityRules(unittest.TestCase):
    def test_plane_tilt_and_area_factor(self):
        iso = np.asarray(ISO)
        sagittal_normal = np.array([1.0, 0.0, 0.0])
        self.assertAlmostEqual(PJ.plane_tilt_deg(camera(), sagittal_normal, iso), 90.0, places=9)
        self.assertAlmostEqual(PJ.plane_tilt_deg(camera(alpha=90.0), sagittal_normal, iso), 0.0, places=9)
        self.assertAlmostEqual(PJ.area_factor(camera(alpha=90.0), sagittal_normal, iso), 1.0, places=9)
        self.assertAlmostEqual(PJ.area_factor(camera(alpha=60.0), sagittal_normal, iso), np.sin(np.radians(60.0)),
                               places=9)
        self.assertTrue(PJ.readable_angle(10.0) and not PJ.readable_angle(20.0))
        self.assertTrue(PJ.readable_length(0.95) and not PJ.readable_length(0.5) and not PJ.readable_length(np.nan))
        self.assertTrue(PJ.readable_area(0.95) and not PJ.readable_area(0.8))

    def test_the_view_named_against_a_frame(self):
        f = frame_at(ISO)
        ap = PJ.view_in_frame(camera(), f)
        self.assertEqual((ap.axis, ap.name), ("y", "AP"))
        self.assertAlmostEqual(ap.obliquity_deg, 0.0, places=9)
        self.assertTrue(ap.frontal and not ap.lateral)
        self.assertEqual(PJ.view_in_frame(camera(alpha=180.0), f).name, "PA")
        self.assertEqual(PJ.view_in_frame(camera(alpha=90.0), f).name, "lateral from the left")
        self.assertEqual(PJ.view_in_frame(camera(alpha=-90.0), f).name, "lateral from the right")
        ob = PJ.view_in_frame(camera(alpha=30.0), f)
        self.assertEqual(ob.axis, "y")
        self.assertAlmostEqual(ob.obliquity_deg, 30.0, places=9)
        angles = PJ.beam_angles(camera(alpha=30.0), f)
        self.assertAlmostEqual(angles["y"], 30.0, places=9)
        self.assertAlmostEqual(angles["x"], 60.0, places=9)
        self.assertAlmostEqual(angles["z"], 90.0, places=9)


class AReadingInAView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        levels = PH.draw_levels("typical", seed=4, start="L1", count=2)
        cls.ph = PH.render(levels, spacing=(1.5,) * 3, sub=1)
        cls.readings = O.ChordOracle().read(cls.ph.labels, cls.ph.affine, cls.ph.names)
        cls.iso = PJ.volume_centre(cls.ph.affine, cls.ph.labels.shape)
        cls.keys = list(S.SPECS)

    def views(self):
        return {"AP": camera(iso=self.iso, size=512), "lateral": camera(alpha=90.0, iso=self.iso, size=512)}

    def test_widths_read_in_the_ap_view_and_depths_in_the_lateral(self):
        r = self.readings[0]
        got = {name: PJ.project_reading(cam, r, self.keys) for name, cam in self.views().items()}
        for name in got:
            for key, im in got[name].items():
                self.assertEqual(im.kind, S.SPECS[key].kind)
                if np.isfinite(im.value_3d):
                    self.assertTrue(im.visible, (name, key))
                    self.assertAlmostEqual(im.magnification, SDD / SOD, delta=0.2)
        self.assertGreater(got["AP"]["endplate"].ratio, 0.95)
        self.assertLess(got["AP"]["endplate_depth"].ratio, 0.3)
        self.assertGreater(got["AP"]["h_post"].ratio, 0.95)
        self.assertLess(got["lateral"]["endplate"].ratio, 0.3)
        self.assertGreater(got["lateral"]["endplate_depth"].ratio, 0.95)
        self.assertGreater(got["lateral"]["h_post"].ratio, 0.95)
        self.assertTrue(got["AP"]["endplate"].readable and not got["AP"]["endplate_depth"].readable)
        self.assertTrue(got["lateral"]["endplate_depth"].readable and not got["lateral"]["endplate"].readable)

    def test_the_views_rules_agree_with_the_lines(self):
        r = self.readings[1]
        cam = self.views()["AP"]
        by_rule = PJ.project_reading(cam, r, S.SEVEN)
        for key in S.SEVEN:
            m = r.measurements[key]
            if not m.taken:
                continue
            spec = S.SPECS[key]
            seg = PJ.project_pair(cam, key, r.level, m.points[spec.points[0]], m.points[spec.points[1]])
            self.assertAlmostEqual(seg.object_mm, by_rule[key].value_2d, delta=0.02 * max(1.0, seg.object_mm))
            np.testing.assert_allclose(seg.a_uv, by_rule[key].points_uv[0])

    def test_the_fluxray_grid_sees_the_phantom_at_its_own_height(self):
        r = self.readings[0]
        for index in (15, 16, 48, 79):          # z 0: y 650 at alpha 0 and 45, y 900 at alpha 90, y 1150 at -90
            cam = PJ.Camera.fluxray(index, self.iso)
            self.assertEqual(PJ.fluxray_pose(index)[2], 0.0)
            got = PJ.project_reading(cam, r, S.SEVEN)
            for key, im in got.items():
                if np.isfinite(im.value_3d):
                    self.assertTrue(im.visible, (index, key))
        view = PJ.view_in_frame(PJ.Camera.fluxray(15, self.iso), r.frame)
        self.assertEqual(view.axis, "y")
        self.assertLess(view.obliquity_deg, 30.0)
        # At z -300 the central ray passes 300 mm below the phantom's centre, and the field spans
        # only 160 mm either side of the isocentre at SOD 650 (614 mm of detector at 1.92 times),
        # so a short phantom falls out of the view: the grid walks a whole-body CT, not one level.
        got = PJ.project_reading(PJ.Camera.fluxray(0, self.iso), r, S.SEVEN)
        self.assertFalse(any(im.visible for im in got.values()))


if __name__ == "__main__":
    unittest.main()
