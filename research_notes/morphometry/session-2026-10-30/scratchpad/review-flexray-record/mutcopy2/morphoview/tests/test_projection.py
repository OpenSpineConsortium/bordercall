"""The projection held to FleXray 1.0.2 (morphoview.projection): its camera, the beads and the
phantom FleXray rendered, its canvas, and where the lines of the export land on its renders.

fixtures/flexray.json is what FleXray made of the straight L2 to L4 phantom at 0.8 by 0.8 by 1 mm
(tests/flexray_record.py records it): in three views, a lateral cone beam, an oblique cone beam
with its principal point off the centre and pixels taller than wide, and a parallel beam from
behind, FleXray's own camera matrices and the rays nanoDRR casts through 41 pixels, the corners
among them, the centroid of each bead of 2.5 mm it rendered on the ends of the phantom's lines, and
where each vertebra's channel is above zero; the first view's camera under nanoDRR's other two
orientations; and where FleXray's canvas puts images and a spot on them. The phantom is built again
here and must be the one recorded. Where FleXray is installed, Live renders again."""
import contextlib
import csv
import dataclasses
import functools
import hashlib
import io
import json
import math
import os
import tempfile
import unittest

import nibabel as nib
import numpy as np
from scipy import ndimage

from morphometry import __main__ as RUN
from morphoview import __main__ as MV
from morphoview import projection as PJ
from morphoview import shapes as SH
from morphoview.tests import flexray_record as FR

with open(FR.FIXTURE, encoding="ascii") as fh:
    RECORD = json.load(fh)
EXACT_MM = 1e-9                 # FleXray's matrices and rays, in float64, and ours
BEAD_PX = 0.25                  # a bead's centre projected and FleXray's centroid of its render, at most
LAND_PX = 1.0                   # a line's end and its level's shadow on the render, at most
LATERAL = "lateral cone"
RERUN = ("the phantom is not the one fixtures/flexray.json was recorded from; record it again with "
         "python -m morphoview.tests.flexray_record where FleXray 1.0.2 is installed")


@functools.lru_cache(maxsize=None)
def phantom():
    """The phantom, built once for every class here, and whether it is the one recorded."""
    lab, aff = FR.phantom()
    return lab, aff, FR.digest(lab, aff) == RECORD["phantom"]["sha256"]


def recorded_views():
    """Each recorded view's name, its camera here and its record."""
    return [(v["name"], PJ.Camera(PJ.View(**v["view"])), v) for v in RECORD["views"]]


def support(v: dict, levels) -> np.ndarray:
    """FleXray's shadow of the levels on the view's render, where their channels are above zero."""
    shape = (v["view"]["height"], v["view"]["width"])
    return np.logical_or.reduce([FR.unpack(v["supports"][lv], shape) for lv in levels])


def off_px(shadow: np.ndarray, u: float, v: float) -> float:
    """How far, in pixels between centres, the pixel holding (u, v) lies from the shadow."""
    r, c = int(math.floor(v)), int(math.floor(u))
    return float(ndimage.distance_transform_edt(~shadow)[r, c])


def quiet(run, argv) -> str:
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        run(argv)
    return said.getvalue()


def read_csv(path: str):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def point(row: dict, prefix: str) -> np.ndarray:
    return np.array([float(row[prefix + k]) for k in "xyz"])


def construction(row: dict, end: str) -> bool:
    """A place Eisenstein's lateral construction puts at the midline between the facets, which a
    lateral film shows on the facets and another view need not: the canal line's posterior end, on
    the line joining the facets' apexes, and that line's two ends."""
    if row["key"] != "canal_ap_lateral_film":
        return False
    return row["part"] == "apex to apex" or end in ("a", "mid")


class FlexraysCamera(unittest.TestCase):
    def records(self):
        for v in RECORD["views"] + RECORD["orientations"]:
            yield v.get("name", "orientation %s" % v["view"]["orientation"]), PJ.Camera(PJ.View(**v["view"])), v["camera"]

    def test_the_record_holds_every_orientation(self):
        self.assertEqual({v["view"]["orientation"] for v in RECORD["views"] + RECORD["orientations"]},
                         set(PJ.ORIENTATIONS))

    def test_the_matrices_are_flexrays(self):
        for name, cam, rec in self.records():
            np.testing.assert_allclose(cam.to_world, rec["rt_inv"], rtol=0, atol=EXACT_MM, err_msg=name)
            np.testing.assert_allclose(np.linalg.inv(cam.intrinsics), rec["k_inv"], rtol=0, atol=1e-12, err_msg=name)

    def test_the_rays_are_nanodrrs_in_nanodrrs_order(self):
        # every pixel's ray here, picked out where nanoDRR's ray r W + c is pixel (r, c): the
        # corners of detectors that are not square tell rows from columns
        for name, cam, rec in self.records():
            src, det = cam.rays(cam.pixel_centres())
            n = [int(math.floor(v)) * cam.view.width + int(math.floor(u)) for u, v in rec["uv"]]
            np.testing.assert_allclose(src[n], rec["source"], rtol=0, atol=EXACT_MM, err_msg=name)
            np.testing.assert_allclose(det[n], rec["detector"], rtol=0, atol=EXACT_MM, err_msg=name)

    def test_a_point_on_a_pixels_ray_projects_to_the_pixels_centre(self):
        for name, cam, rec in self.records():
            src, det = np.array(rec["source"]), np.array(rec["detector"])
            for f in (0.05, 0.5, 0.95):
                got = cam.project(src + f * (det - src))
                np.testing.assert_allclose(got.uv, rec["uv"], rtol=0, atol=1e-9, err_msg=name)
                self.assertTrue(got.in_beam.all(), name)

    def test_a_point_the_render_did_not_sample_is_not_in_its_beam(self):
        for name, cam, rec in self.records():
            src, det = np.array(rec["source"]), np.array(rec["detector"])
            self.assertFalse(cam.project(src - 0.1 * (det - src)).in_beam.any(), name)
            self.assertFalse(cam.project(det + 0.1 * (det - src)).in_beam.any(), name)
            w, h = cam.view.width, cam.view.height
            outside = np.array([[-0.5, 3.0], [w + 0.5, 3.0], [3.0, -0.5], [3.0, h + 0.5]])
            a, b = cam.rays(outside)
            self.assertFalse(cam.project(0.5 * (a + b)).in_beam.any(), name)

    def test_beads_land_where_flexray_rendered_them(self):
        beads = np.array(RECORD["beads"]["centroids_mm"])
        for name, cam, v in recorded_views():
            self.assertTrue(all(c is not None for c in v["bead_centroids_uv"]), name)
            err = np.linalg.norm(cam.project(beads).uv - np.array(v["bead_centroids_uv"]), axis=1)
            self.assertLessEqual(float(err.max()), BEAD_PX, name)
            self.assertLessEqual(float(np.median(err)), 0.1, name)

    def test_the_beads_see_half_a_pixel(self):
        # a pixel's corner taken for its centre, the slip a projection most easily makes, is seen
        beads = np.array(RECORD["beads"]["centroids_mm"])
        for name, cam, v in recorded_views():
            seen = np.array(v["bead_centroids_uv"])
            for slip in ({"x0": cam.view.x0 + 0.5 * cam.view.delx}, {"y0": cam.view.y0 + 0.5 * cam.view.pixel_y}):
                wrong = PJ.Camera(dataclasses.replace(cam.view, **slip))
                err = np.linalg.norm(wrong.project(beads).uv - seen, axis=1)
                self.assertGreater(float(np.median(err)), 0.4, (name, slip))


class Geometry(unittest.TestCase):
    def camera(self, **more) -> PJ.Camera:
        view = dict(rot_deg=(20.0, -10.0, 5.0), xyz_mm=(-30.0, 650.0, 20.0), isocentre_mm=(1.0, 2.0, 3.0),
                    sdd=1180.0, delx=1.6, dely=1.7, x0=40.0, y0=-40.0, height=176, width=144)
        view.update(more)
        return PJ.Camera(PJ.View(**view))

    def test_a_length_across_the_beam_is_magnified_by_sdd_over_its_depth(self):
        for orthographic in (False, True):
            cam = self.camera(orthographic=orthographic)
            across, down = cam.to_world[:3, 0], cam.to_world[:3, 1]
            for depth in (500.0, 650.0, 900.0):
                p = cam.source + depth * cam.beam
                uv = cam.project(np.stack([p, p + 3.0 * across, p + 3.0 * down])).uv
                m = 1.0 if orthographic else 1180.0 / depth
                self.assertAlmostEqual(float(cam.magnification(depth)), m, places=12)
                np.testing.assert_allclose(uv[1] - uv[0], [3.0 * m / 1.6, 0.0], atol=1e-9)
                np.testing.assert_allclose(uv[2] - uv[0], [0.0, 3.0 * m / 1.7], atol=1e-9)

    def test_a_length_turned_out_of_the_detector_is_foreshortened(self):
        cam = self.camera(orthographic=True)
        p = cam.source + 600.0 * cam.beam
        for tilt in (0.0, 30.0, 75.0):
            t = math.radians(tilt)
            uv = cam.project(np.stack([p, p + 10.0 * (math.cos(t) * cam.to_world[:3, 0] + math.sin(t) * cam.beam)])).uv
            self.assertAlmostEqual(float(np.linalg.norm(uv[1] - uv[0])), 10.0 * math.cos(t) / 1.6, places=9)

    def test_the_beams_axis_meets_the_principal_point(self):
        cam = self.camera()
        uv = cam.project(cam.source + 700.0 * cam.beam).uv[0]
        np.testing.assert_allclose(uv, [40.0 / 1.6 + 72.0, -40.0 / 1.7 + 88.0], atol=1e-9)

    def test_a_manifest_row_is_the_view_its_request_was(self):
        row = {"file": "images/s_v0.png", "subject": "s", "isocentre": {"label": 5, "point_mm": [1.0, 2.0, 3.0]},
               "pose": {"rot_deg": [10.0, 20.0, 30.0], "xyz_mm": [0.0, 700.0, 5.0], "orthographic": False,
                        "sdd": 1200.0, "delx": 1.5, "grid": None}}
        view = PJ.View.from_manifest(row, 256)
        self.assertEqual(view, PJ.View(rot_deg=(10.0, 20.0, 30.0), xyz_mm=(0.0, 700.0, 5.0),
                                       isocentre_mm=(1.0, 2.0, 3.0), sdd=1200.0, delx=1.5, height=256, width=256))
        self.assertEqual(view.pixel_y, 1.5)
        row["pose"]["orthographic"] = True
        self.assertTrue(PJ.View.from_manifest(row, 256).orthographic)


class Canvas(unittest.TestCase):
    def test_an_image_lands_where_flexrays_content_box_puts_it(self):
        size = RECORD["canvas"]["image_size"][0]
        for box in RECORD["canvas"]["boxes"]:
            h, w = box["height"], box["width"]
            (left, top), (right, bottom) = PJ.to_canvas([[0.0, 0.0], [w, h]], h, w, size)
            t, lf = min(round(float(top)), size - 1), min(round(float(left)), size - 1)
            got = [t, lf, max(t + 1, round(float(bottom))), max(lf + 1, round(float(right)))]
            self.assertEqual(got, box["content_box"], (h, w))

    def test_a_spot_lands_where_flexrays_resize_carries_it(self):
        size = RECORD["canvas"]["image_size"][0]
        for spot in RECORD["canvas"]["spots"]:
            want = PJ.to_canvas(spot["uv"], spot["height"], spot["width"], size)[0]
            for path, got in spot["canvas_uv"].items():
                np.testing.assert_allclose(want, got, rtol=0, atol=0.01, err_msg=path)

    def test_the_canvas_gives_the_place_back(self):
        uv = np.random.default_rng(2).uniform(0.0, 300.0, size=(50, 2))
        for h, w in ((168, 136), (300, 97), (256, 256)):
            np.testing.assert_allclose(PJ.from_canvas(PJ.to_canvas(uv, h, w), h, w), uv, atol=1e-9)


class Shadows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lab, cls.aff, same = phantom()
        if not same:
            raise AssertionError(RERUN)

    def test_our_shadows_are_flexrays(self):
        for name, cam, v in recorded_views():
            for level, i in RECORD["phantom"]["ids"].items():
                ours = SH.Volume.from_labels(self.lab, self.aff, i, largest=False).silhouette(
                    cam, n_samples=RECORD["n_samples"])
                theirs = support(v, [level])
                differ = ours ^ theirs
                # FleXray samples in float32 and this in float64, so a sample within a float32
                # rounding of a voxel's half-way plane may take the voxel on either side: a pixel
                # or two at the shadow's edge, where a sampling shifted by any step moves hundreds
                edge = ndimage.binary_dilation(theirs ^ ndimage.binary_erosion(theirs))
                self.assertLessEqual(int(differ.sum()), 2, (name, level))
                self.assertTrue(bool((differ <= edge).all()), (name, level))
                self.assertGreater(int(theirs.sum()), 500, (name, level))

    def test_flexrays_label_mask_lies_within_the_shadow_and_drops_thin_bone(self):
        # FleXray's labels are its channels above 0.5, which bone thinner than a few mm along the
        # ray does not reach, so the lines are set against the shadow, never the mask
        for name, _, v in recorded_views():
            shape = (v["view"]["height"], v["view"]["width"])
            for level in RECORD["phantom"]["ids"]:
                mask = FR.unpack(v["masks"][level], shape)
                self.assertFalse(bool((mask & ~support(v, [level])).any()), (name, level))
            dropped = sum(int((support(v, [lv]) & ~FR.unpack(v["masks"][lv], shape)).sum())
                          for lv in RECORD["phantom"]["ids"])
            self.assertGreater(dropped, 0, name)


class Pieces(unittest.TestCase):
    def test_a_levels_shadow_takes_in_every_piece_of_its_label(self):
        # FleXray renders every voxel a label holds, so the command's shadow of a level takes in a
        # stray piece of it, which the measuring of the vertebra leaves out
        lab = np.zeros((40, 40, 40), np.int16)
        lab[8:20, 8:20, 8:20] = 22
        lab[30:33, 30:33, 30:33] = 22
        path = os.path.join(tempfile.mkdtemp(), "pieces.nii.gz")
        nib.save(nib.Nifti1Image(lab, np.eye(4)), path)
        cam = PJ.Camera(PJ.View(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=(20.0, 20.0, 20.0),
                                sdd=1200.0, delx=1.0, height=80, width=80))
        got = MV.shadows(path, "verse", cam, ["L3"], 500)["L3"]
        every = SH.Volume.from_labels(lab, np.eye(4), 22, largest=False).silhouette(cam, n_samples=500)
        main = SH.Volume.from_labels(lab, np.eye(4), 22).silhouette(cam, n_samples=500)
        np.testing.assert_array_equal(got, every)
        self.assertGreater(int((every & ~main).sum()), 0)


class Lines(unittest.TestCase):
    """The lines export of the phantom carried onto the three renders by python -m morphoview
    project, each end set against FleXray's own shadow of its level."""

    @classmethod
    def setUpClass(cls):
        lab, aff, same = phantom()
        if not same:
            raise AssertionError(RERUN)
        cls.tmp = tempfile.mkdtemp()
        masks = os.path.join(cls.tmp, "masks")
        os.makedirs(masks)
        cls.mask = os.path.join(masks, "0001.nii.gz")
        nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), cls.mask)
        run = os.path.join(cls.tmp, "run")
        quiet(RUN.main, ["run", "--masks", masks, "--scheme", "verse", "--out", run, "--workers", "1", "--lines"])
        cls.lines, cls.frames = os.path.join(run, "lines.csv"), os.path.join(run, "frames.csv")
        cls.rows = read_csv(cls.lines)
        cls.views = []
        for k, (name, cam, v) in enumerate(recorded_views()):
            path = os.path.join(cls.tmp, "view%d.json" % k)
            with open(path, "w", encoding="ascii") as fh:
                json.dump(dict(v["view"], n_samples=RECORD["n_samples"]), fh)
            out = os.path.join(cls.tmp, "projected%d" % k)
            said = quiet(MV.main, ["project", "--lines", cls.lines, "--frames", cls.frames, "--view", path,
                                   "--labels", cls.mask, "--scheme", "verse", "--out", out])
            cls.views.append({"name": name, "cam": cam, "record": v, "out": out, "said": said, "view_file": path,
                              "lines": read_csv(os.path.join(out, "lines2d.csv")),
                              "frames": read_csv(os.path.join(out, "frames2d.csv")),
                              "column": read_csv(os.path.join(out, "column2d.csv"))})

    def drawn(self, got: dict):
        rows = [(row, line) for row, line in zip(self.rows, got["lines"]) if row["status"] == "drawn"]
        self.assertEqual(len(rows), len(self.rows))
        return rows

    def test_every_line_is_carried_in_order(self):
        for got in self.views:
            self.assertEqual(len(got["lines"]), len(self.rows))
            for row, line in zip(self.rows, got["lines"]):
                self.assertEqual([line[k] for k in ("level", "key", "part", "a_end", "b_end")],
                                 [row[k] for k in ("level", "key", "part", "a_end", "b_end")])
            n = len(self.rows)
            self.assertIn("%d lines, %d drawn, %d of them with both ends on the render" % (n, n, n), got["said"])

    def test_the_ends_are_where_the_camera_puts_them(self):
        for got in self.views:
            cam, view = got["cam"], got["cam"].view
            for row, line in self.drawn(got):
                uv = []
                for e in "ab":
                    p = cam.project(point(row, e)[None])
                    uv.append(p.uv[0])
                    self.assertEqual([float(line[e + "u"]), float(line[e + "v"])], p.uv[0].tolist())
                    self.assertEqual(float(line[e + "_depth"]), float(p.depth[0]))
                    self.assertEqual(line[e + "_in_beam"], "True")
                    m = 1.0 if view.orthographic else view.sdd / float(p.depth[0])
                    self.assertEqual(float(line[e + "_magnification"]), m)
                    on = PJ.to_canvas(p.uv[0], view.height, view.width)[0]
                    self.assertEqual([float(line[e + "_canvas_u"]), float(line[e + "_canvas_v"])], on.tolist())
                self.assertAlmostEqual(float(line["length_px"]), float(np.linalg.norm(uv[1] - uv[0])), places=9)

    def test_every_drawn_line_lands_on_its_levels_shadow(self):
        # each end of every line on FleXray's own shadow of its level, a disc's on its two
        # vertebrae's; the lateral film's construction too on the lateral render, where it is read
        for got in self.views:
            for row, line in self.drawn(got):
                shadow = support(got["record"], row["level"].split("-"))
                for e in "ab":
                    if construction(row, e) and got["name"] != LATERAL:
                        continue
                    far = off_px(shadow, float(line[e + "u"]), float(line[e + "v"]))
                    self.assertLessEqual(far, LAND_PX, (got["name"], row["level"], row["key"], row["part"], e))

    def test_a_vertebras_lines_have_their_middles_on_it(self):
        for got in self.views:
            for row, line in self.drawn(got):
                if "-" in row["level"] or construction(row, "mid"):
                    continue
                mid = 0.5 * (np.array([float(line["au"]), float(line["av"])]) +
                             np.array([float(line["bu"]), float(line["bv"])]))
                self.assertLessEqual(off_px(support(got["record"], [row["level"]]), *mid), LAND_PX,
                                     (got["name"], row["level"], row["key"], row["part"]))

    def test_a_discs_middle_lies_in_the_disc_space_on_the_lateral_render(self):
        got = next(g for g in self.views if g["name"] == LATERAL)
        discs = [(row, line) for row, line in self.drawn(got) if "-" in row["level"]]
        self.assertEqual(len(discs), 6)
        for row, line in discs:
            self.assertGreater(float(line["mid_off_px"]), LAND_PX, (row["level"], row["key"]))

    def test_the_landing_is_measured_on_flexrays_shadow(self):
        # the command's shadows are its own, sampled as FleXray samples; set against FleXray's
        for got in self.views:
            for row, line in self.drawn(got):
                shadow = support(got["record"], row["level"].split("-"))
                for e in "ab":
                    self.assertEqual(float(line[e + "_off_px"]), off_px(shadow, float(line[e + "u"]),
                                                                         float(line[e + "v"])))

    def test_the_frames_and_the_column_are_carried_too(self):
        frames = read_csv(self.frames)
        for got in self.views:
            cam = got["cam"]
            self.assertEqual(len(got["frames"]), len(frames))
            origins = []
            for f, g in zip(frames, got["frames"]):
                o = point(f, "o")
                tips = cam.project(np.stack([o] + [o + MV.AXIS_MM * point(f, "e" + e) for e in "xyz"])).uv
                self.assertEqual([float(g["ou"]), float(g["ov"])], tips[0].tolist())
                for i, e in enumerate("xyz", start=1):
                    self.assertEqual([float(g[e + "u"]), float(g[e + "v"])], tips[i].tolist())
                self.assertEqual(g["axis"], f["axis"])
                origins.append(tips[0])
            column = np.array([[float(c["u"]), float(c["v"])] for c in got["column"]])
            for o in origins:
                self.assertLess(float(np.linalg.norm(column - o, axis=1).min()), 1e-9)
            np.testing.assert_allclose(column[[0, -1]], np.array(origins)[[0, -1]], atol=1e-9)

    def test_the_view_record_names_what_was_projected(self):
        for got in self.views:
            with open(os.path.join(got["out"], "VIEW.json"), encoding="ascii") as fh:
                rec = json.load(fh)
            self.assertEqual(PJ.View(**rec["view"]), got["cam"].view)
            self.assertEqual(rec["n_samples"], RECORD["n_samples"])
            self.assertEqual(rec["from"]["sha256"], sha256(got["view_file"]))
            self.assertEqual(rec["lines"]["sha256"], sha256(self.lines))
            self.assertEqual(rec["labels"]["sha256"], sha256(self.mask))
            here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for name, digest in rec["code"].items():
                self.assertEqual(digest, sha256(os.path.join(here, os.path.basename(name))))
            self.assertIn("morphoview/projection.py", rec["code"])

    def test_the_samples_a_ray_are_the_view_files(self):
        _, _, v = recorded_views()[1]
        path = os.path.join(self.tmp, "samples.json")
        with open(path, "w", encoding="ascii") as fh:
            json.dump(dict(v["view"], n_samples=450), fh)
        out = os.path.join(self.tmp, "samples")
        quiet(MV.main, ["project", "--lines", self.lines, "--view", path, "--out", out])
        with open(os.path.join(out, "VIEW.json"), encoding="ascii") as fh:
            self.assertEqual(json.load(fh)["n_samples"], 450)
        self.assertFalse(os.path.exists(os.path.join(out, "frames2d.csv")))

    def test_a_manifest_row_projects_as_its_view(self):
        _, cam, v = recorded_views()[0]
        row = {"file": "images/0001_v00.png", "subject": "0001",
               "isocentre": {"label": None, "point_mm": list(cam.view.isocentre_mm)},
               "pose": {"rot_deg": list(cam.view.rot_deg), "xyz_mm": list(cam.view.xyz_mm), "orthographic": False,
                        "sdd": cam.view.sdd, "delx": cam.view.delx, "grid": None}}
        manifest = os.path.join(self.tmp, "manifest.json")
        with open(manifest, "w", encoding="ascii") as fh:
            json.dump({"blocks": {"detector": 256, "ray_samples": 400}, "views": [row]}, fh)
        out = os.path.join(self.tmp, "from-manifest")
        quiet(MV.main, ["project", "--lines", self.lines, "--manifest", manifest, "--file", row["file"], "--out", out])
        want = PJ.Camera(PJ.View.from_manifest(row, 256))
        for r, line in zip(self.rows, read_csv(os.path.join(out, "lines2d.csv"))):
            self.assertEqual([float(line["au"]), float(line["av"])], want.project(point(r, "a")).uv[0].tolist())
        with open(os.path.join(out, "VIEW.json"), encoding="ascii") as fh:
            rec = json.load(fh)
        self.assertEqual((rec["n_samples"], rec["from"]["file"], rec["from"]["subject"]), (400, row["file"], "0001"))
        self.assertIsNone(rec["labels"])
        with self.assertRaises(SystemExit):
            quiet(MV.main, ["project", "--lines", self.lines, "--manifest", manifest, "--file", "images/x.png",
                            "--out", out])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            MV.main(["project", "--lines", self.lines, "--manifest", manifest, "--out", out])


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def flexray_here() -> bool:
    try:
        import fxr.drr  # noqa: F401
        import torch  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(flexray_here(), "FleXray and torch are not installed here; fixtures/flexray.json stands in")
class Live(unittest.TestCase):
    """FleXray itself: the record's views rendered again give the record, and beads rendered on a
    view the record does not hold, posterior to anterior on a square detector of 256 pixels as
    SchwingNet's renders are, land where they are projected."""

    @classmethod
    def setUpClass(cls):
        cls.lab, cls.aff, same = phantom()
        if not same:
            raise AssertionError(RERUN)

    def test_flexray_renders_the_record_again(self):
        bone = np.where(self.lab > 0, FR.BONE_HU, FR.AIR_HU)
        for name, cam, v in recorded_views():
            rendered = FR.render(bone, self.lab, self.aff, cam.view)
            for level, i in RECORD["phantom"]["ids"].items():
                np.testing.assert_array_equal(rendered[i] > 0, support(v, [level]), err_msg=name)
            again = FR.camera(cam.view, np.array(v["camera"]["uv"]))
            for key in ("rt_inv", "k_inv", "source", "detector"):
                np.testing.assert_allclose(again[key], v["camera"][key], rtol=0, atol=1e-12, err_msg=key)

    def test_beads_on_a_view_not_recorded_land_where_projected(self):
        view = PJ.View(rot_deg=(4.0, -6.0, 3.0), xyz_mm=(10.0, -700.0, -5.0), isocentre_mm=tuple(RECORD["isocentre_mm"]),
                       sdd=1200.0, delx=1.0, height=256, width=256, orientation="PA")
        cam = PJ.Camera(view)
        balls, centroids = FR.bead_labels(self.lab.shape, self.aff, np.array(RECORD["beads"]["centroids_mm"]))
        rendered = FR.render(np.where(balls > 0, FR.BONE_HU, FR.AIR_HU), balls, self.aff, view, FR.BEAD_SAMPLES)
        seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(centroids))]
        self.assertTrue(all(c is not None for c in seen))
        err = np.linalg.norm(cam.project(centroids).uv - np.array(seen), axis=1)
        self.assertLessEqual(float(err.max()), BEAD_PX)


if __name__ == "__main__":
    unittest.main()
