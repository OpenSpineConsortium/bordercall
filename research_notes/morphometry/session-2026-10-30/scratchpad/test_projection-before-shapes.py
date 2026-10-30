"""The projection held to FleXray 1.0.2 (morphoview.projection): its camera, the beads and the
phantom FleXray rendered, its canvas, and where the lines of the export land on its renders.

fixtures/flexray.json is what FleXray made of the straight L2 to L4 phantom at 0.8 by 0.8 by 1 mm
(tests/flexray_record.py records it): in three views, a lateral cone beam, an oblique cone beam
with its principal point off the centre and pixels taller than wide, and a parallel beam from
behind, FleXray's own camera matrices and the rays nanoDRR casts through 41 pixels, the corners
among them, the centroid of each bead of 2.5 mm it rendered on the ends of the phantom's lines,
FleXray's labels of each vertebra at the threshold of its training profile, 0.0, where the
vertebra's channel is above zero, and at a bare request's 0.5, and each vertebra's channel over a
volume of one attenuation as a count of nanoDRR's steps at every pixel; a fourth view, of a crop
of the phantom's slices as SchwingNet's render cuts the CT for each view, and each vertebra's
support on it; the first view's camera under nanoDRR's other two orientations; and where FleXray's canvas
puts images and a spot on them. The phantom is built again here and must be the one recorded.
Where FleXray is installed, Live renders again."""
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
from typing import Optional, Tuple

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


@functools.lru_cache(maxsize=None)
def exported():
    """The phantom saved as a mask and its lines export, made once for every class here: the
    folder, the mask, lines.csv, frames.csv and the lines' rows."""
    lab, aff, same = phantom()
    if not same:
        raise AssertionError(RERUN)
    tmp = tempfile.mkdtemp()
    masks = os.path.join(tmp, "masks")
    os.makedirs(masks)
    mask = os.path.join(masks, "0001.nii.gz")
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), mask)
    run = os.path.join(tmp, "run")
    quiet(RUN.main, ["run", "--masks", masks, "--scheme", "verse", "--out", run, "--workers", "1", "--lines"])
    lines = os.path.join(run, "lines.csv")
    return tmp, mask, lines, os.path.join(run, "frames.csv"), read_csv(lines)


def recorded_views():
    """Each recorded view's name, its camera here and its record."""
    return [(v["name"], PJ.Camera(PJ.View(**v["view"])), v) for v in RECORD["views"]]


def support(v: dict, levels) -> np.ndarray:
    """FleXray's shadow of the levels on the view's render, its labels of them at its training
    profile's threshold, 0.0, where their channels are above zero."""
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


def manifest_of(tmp: str, name: str, view: PJ.View, crop: Optional[dict], subject: str,
                ray_samples: int, flexray: Optional[str] = None) -> Tuple[str, str]:
    """A render manifest of SchwingNet's kind holding one view on a square detector, and the
    view's file as it names it; FleXray's release where one is given."""
    row = {"file": "images/%s_v00.png" % subject, "subject": subject,
           "isocentre": {"label": None, "point_mm": list(view.isocentre_mm)},
           "pose": {"rot_deg": list(view.rot_deg), "xyz_mm": list(view.xyz_mm), "orthographic": view.orthographic,
                    "sdd": view.sdd, "delx": view.delx, "grid": None}}
    if crop is not None:
        row["crop"] = dict(crop)
    path = os.path.join(tmp, name)
    doc = {"blocks": {"detector": view.width, "ray_samples": ray_samples}, "views": [row]}
    if flexray is not None:
        doc["flexray"] = flexray
    with open(path, "w", encoding="ascii") as fh:
        json.dump(doc, fh)
    return path, row["file"]


def construction(row: dict, end: str) -> bool:
    """A place Eisenstein's lateral construction puts at the midline between the facets, which a
    lateral film shows on the facets and another view need not. On the phantom the one that falls
    off the bone in the two other views is the inferior apex, the end b of the line joining the
    facets' apexes, 3 to 7 px from the shadow; the canal line's ends, the superior apex and every
    midpoint land on it."""
    return row["key"] == "canal_ap_lateral_film" and row["part"] == "apex to apex" and end == "b"


class FlexraysCamera(unittest.TestCase):
    def records(self):
        for v in RECORD["views"] + RECORD["orientations"]:
            yield v.get("name", "orientation %s" % v["view"]["orientation"]), PJ.Camera(PJ.View(**v["view"])), v["camera"]

    def test_the_camera_is_the_release_the_record_was_made_with(self):
        self.assertEqual(PJ.CHECKED, {k: RECORD["versions"][k] for k in ("flexray", "nanodrr")})

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

    def test_the_commands_canvas_is_flexrays_default(self):
        # the canvas project places every end on unless told otherwise, square and padded to a
        # square as to_canvas takes it
        self.assertEqual(RECORD["canvas"]["image_size"], [PJ.CANVAS, PJ.CANVAS])
        self.assertTrue(RECORD["canvas"]["pad_to_square"])

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

    def test_our_path_lengths_are_flexrays_counts_point_by_point(self):
        # over a volume of one attenuation FleXray's channel for a vertebra is the attenuation times
        # its step times the samples whose nearest voxel the vertebra holds, which the record keeps
        # as counts: the path length here, over the step, is that count at every pixel
        for name, cam, v in recorded_views():
            src, det = cam.rays(cam.pixel_centres())
            step = (np.linalg.norm(det - src, axis=1) / (RECORD["n_samples"] - 1)).reshape(cam.view.height, cam.view.width)
            for level, i in RECORD["phantom"]["ids"].items():
                ours = SH.Volume.from_labels(self.lab, self.aff, i, largest=False).path_length(
                    cam, n_samples=RECORD["n_samples"]) / step
                theirs = FR.unpack_counts(v["counts"][level], step.shape)
                np.testing.assert_allclose(ours, np.rint(ours), rtol=0, atol=1e-6, err_msg=name)
                differ = np.rint(ours).astype(np.int64) != theirs
                self.assertLessEqual(int(differ.sum()), 2, (name, level))
                self.assertLessEqual(int(np.abs(np.rint(ours) - theirs).max()), 1, (name, level))
                self.assertTrue(bool(((theirs > 0) == support(v, [level])).all()), (name, level))
                self.assertGreater(int(theirs.max()), 10, (name, level))

    def test_flexrays_labels_at_a_bare_requests_threshold_need_9_mm_of_bone(self):
        # at a bare request's 0.5, at which SchwingNet's realism programme renders its truth masks,
        # FleXray's label of a vertebra is its channel above 0.5. The channel is at most the bone's
        # attenuation, 0.0573 per mm at 1000 HU, times the step times the samples the vertebra
        # holds, our path length a step short at most, so the mask lies where our path length
        # reaches 0.5 over the attenuation, about 9 mm, and drops thinner bone: the lines are set
        # against the shadow, never the mask
        mu, cut = RECORD["uniform"]["mu_per_mm"], RECORD["label_thresholds"]
        self.assertEqual(cut, {"supports": 0.0, "masks": 0.5})
        for name, cam, v in recorded_views():
            shape = (cam.view.height, cam.view.width)
            src, det = cam.rays(cam.pixel_centres())
            step = (np.linalg.norm(det - src, axis=1) / (RECORD["n_samples"] - 1)).reshape(shape)
            dropped = 0
            for level, i in RECORD["phantom"]["ids"].items():
                mask = FR.unpack(v["masks"][level], shape)
                ours = SH.Volume.from_labels(self.lab, self.aff, i, largest=False).path_length(
                    cam, n_samples=RECORD["n_samples"])
                self.assertFalse(bool((mask & (mu * (ours + step) <= cut["masks"])).any()), (name, level))
                dropped += int(((ours > 0) & ~mask).sum())
            self.assertGreater(dropped, 100, name)


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
        got = MV.shadows(MV.read_mask(path, "verse"), None, cam, ["L3"], 500)["L3"]
        every = SH.Volume.from_labels(lab, np.eye(4), 22, largest=False).silhouette(cam, n_samples=500)
        main = SH.Volume.from_labels(lab, np.eye(4), 22).silhouette(cam, n_samples=500)
        np.testing.assert_array_equal(got, every)
        self.assertGreater(int((every & ~main).sum()), 0)


class Lines(unittest.TestCase):
    """The lines export of the phantom carried onto the three renders by python -m morphoview
    project, each end set against FleXray's own shadow of its level."""

    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.mask, cls.lines, cls.frames, cls.rows = exported()
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
            n, study = len(self.rows), self.rows[0]["study"]
            self.assertIn("%d lines of %s, %d drawn, %d of them with both ends on the render,"
                          % (n, study, n, n), got["said"])
            self.assertNotIn("not given", got["said"])

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
                if "-" in row["level"]:
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
            self.assertEqual(rec["canvas"], RECORD["canvas"]["image_size"][0])
            self.assertEqual(rec["flexray"], {"render": "not recorded", "camera": PJ.CHECKED})
            self.assertIsNone(rec["edits"])
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

    def test_a_render_of_another_flexray_is_projected_with_a_warning(self):
        _, cam, _ = recorded_views()[0]
        square = dataclasses.replace(cam.view, height=cam.view.width)
        for made, warned in ((PJ.CHECKED["flexray"], False), ("9.9.9", True)):
            manifest, file = manifest_of(self.tmp, "made-%s.json" % made, square, None, self.rows[0]["study"], 500,
                                         flexray=made)
            out = os.path.join(self.tmp, "made-%s" % made)
            said = io.StringIO()
            with contextlib.redirect_stderr(said):
                quiet(MV.main, ["project", "--lines", self.lines, "--manifest", manifest, "--file", file, "--out", out])
            self.assertEqual("FleXray 9.9.9" in said.getvalue(), warned, made)
            with open(os.path.join(out, "VIEW.json"), encoding="ascii") as fh:
                self.assertEqual(json.load(fh)["flexray"], {"render": made, "camera": PJ.CHECKED})


class Crops(unittest.TestCase):
    """A render of a crop of the CT's slices, as SchwingNet's render cuts one for each view: the
    shadows cut to the crop are what FleXray rendered of the cut phantom, an end beyond the crop
    is said to lie outside what the render was made of, and the crop is placed on the CT's grid,
    which the labels must share."""

    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.mask, cls.lines, cls.frames, cls.rows = exported()
        cls.lab, cls.aff, _ = phantom()
        cls.rec = RECORD["crop"]
        cls.crop = PJ.Crop.from_record(cls.rec["crop"])
        cls.cam = PJ.Camera(PJ.View(**cls.rec["view"]))
        cls.manifest, cls.file = manifest_of(cls.tmp, "crop-manifest.json", cls.cam.view, cls.rec["crop"],
                                             cls.rows[0]["study"], RECORD["n_samples"])
        cls.out = os.path.join(cls.tmp, "crop")
        cls.said = quiet(MV.main, ["project", "--lines", cls.lines, "--frames", cls.frames, "--manifest", cls.manifest,
                                   "--file", cls.file, "--labels", cls.mask, "--scheme", "verse", "--out", cls.out])
        cls.got = read_csv(os.path.join(cls.out, "lines2d.csv"))

    def test_the_manifest_row_gives_the_recorded_view_and_its_crop(self):
        with open(os.path.join(self.out, "VIEW.json"), encoding="ascii") as fh:
            rec = json.load(fh)
        self.assertEqual(PJ.View(**rec["view"]), self.cam.view)
        self.assertEqual(rec["crop"], self.rec["crop"])
        self.assertEqual((rec["ct_grid"]["from"], rec["ct_grid"]["shape"]), ("labels", list(self.lab.shape)))

    def test_the_shadows_of_a_crop_are_flexrays(self):
        mask = MV.read_mask(self.mask, "verse")
        ours = MV.shadows(mask, self.crop, self.cam, list(RECORD["phantom"]["ids"]), RECORD["n_samples"])
        for level in RECORD["phantom"]["ids"]:
            theirs = support(self.rec, [level])
            differ = ours[level] ^ theirs
            edge = ndimage.binary_dilation(theirs ^ ndimage.binary_erosion(theirs))
            self.assertLessEqual(int(differ.sum()), 2, level)
            self.assertTrue(bool((differ <= edge).all()), level)
        # L4 lies wholly outside the crop, L2 within it, and the crop cuts L3
        whole = MV.shadows(mask, None, self.cam, ["L3"], RECORD["n_samples"])["L3"]
        self.assertFalse(bool(support(self.rec, ["L4"]).any()))
        self.assertGreater(int(support(self.rec, ["L2"]).sum()), 500)
        self.assertGreater(int((whole & ~support(self.rec, ["L3"])).sum()), 100)

    def test_an_end_beyond_the_crop_lies_outside_what_was_rendered(self):
        to_voxel = np.linalg.inv(self.aff)
        said = {"True": 0, "False": 0}
        for row, line in zip(self.rows, self.got):
            for e in "ab":
                k = int(np.rint(to_voxel[:3, :3] @ point(row, e) + to_voxel[:3, 3])[2])
                inside = str(self.crop.z_start <= k < self.crop.z_stop)
                self.assertEqual(line[e + "_in_volume"], inside, (row["level"], row["key"], e))
                said[inside] += 1
                if row["level"] in ("L2", "L4"):
                    self.assertEqual(inside, str(row["level"] == "L2"), (row["level"], row["key"], e))
        self.assertGreater(min(said.values()), 10)
        both = sum(line["a_in_volume"] == line["b_in_volume"] == "True" for line in self.got)
        self.assertLess(both, len(self.got))
        self.assertIn("%d of them with both ends on the render," % both, self.said)

    def test_an_end_in_the_crop_lands_on_flexrays_shadow_of_it(self):
        # the crop is seen from the side, so the lateral film's construction is held too
        for row, line in zip(self.rows, self.got):
            shadow = support(self.rec, row["level"].split("-"))
            for e in "ab":
                if line[e + "_in_volume"] != "True":
                    continue
                far = off_px(shadow, float(line[e + "u"]), float(line[e + "v"]))
                self.assertLessEqual(far, LAND_PX, (row["level"], row["key"], row["part"], e))
                self.assertEqual(float(line[e + "_off_px"]), far)

    def test_a_crop_is_placed_on_the_cts_grid(self):
        # the CT's header places the crop as the labels' grid does; a CT on another grid than the
        # labels', or with fewer slices than the crop runs to, refuses; with neither, no end is
        # said to be in or out
        def ct(name, shape, affine):
            path = os.path.join(self.tmp, name)
            nib.save(nib.Nifti1Image(np.zeros(shape, np.uint8), affine), path)
            return path

        def project(out, *more):
            return quiet(MV.main, ["project", "--lines", self.lines, "--manifest", self.manifest, "--file", self.file,
                                   "--out", os.path.join(self.tmp, out)] + list(more))

        flags = lambda out: [(g["a_in_volume"], g["b_in_volume"])
                             for g in read_csv(os.path.join(self.tmp, out, "lines2d.csv"))]
        said = project("crop-ct", "--ct", ct("ct-same.nii.gz", self.lab.shape, self.aff))
        self.assertEqual(flags("crop-ct"), [(g["a_in_volume"], g["b_in_volume"]) for g in self.got])
        self.assertNotIn("not given", said)
        moved = self.aff.copy()
        moved[0, 3] += 0.5
        with self.assertRaises(SystemExit):
            project("crop-moved", "--ct", ct("ct-moved.nii.gz", self.lab.shape, moved), "--labels", self.mask,
                    "--scheme", "verse")
        with self.assertRaises(SystemExit):
            project("crop-short", "--ct", ct("ct-short.nii.gz", self.lab.shape[:2] + (200,), self.aff))
        said = project("crop-alone")
        self.assertEqual(set(flags("crop-alone")), {("", "")})
        self.assertIn("the CT's grid not given", said)


class Studies(unittest.TestCase):
    """A render shows one subject, so one study's lines go onto it: the one asked for, the lines'
    only study, or the one the manifest's row names as its subject; lines of several studies with
    none of these refuse."""

    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.mask, cls.lines, cls.frames, cls.rows = exported()
        cls.study = cls.rows[0]["study"]
        cls.two = os.path.join(cls.tmp, "two-studies.csv")
        with open(cls.lines, newline="") as fh:
            fields = csv.DictReader(fh).fieldnames
        with open(cls.two, "w", newline="", encoding="ascii") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(cls.rows + [dict(r, study="0002") for r in cls.rows])
        _, cam, v = recorded_views()[0]
        cls.square = dataclasses.replace(cam.view, height=cam.view.width)
        cls.view = os.path.join(cls.tmp, "studies-view.json")
        with open(cls.view, "w", encoding="ascii") as fh:
            json.dump(v["view"], fh)

    def project(self, lines, *more):
        out = tempfile.mkdtemp(dir=self.tmp)
        quiet(MV.main, ["project", "--lines", lines, "--out", out] + list(more))
        with open(os.path.join(out, "VIEW.json"), encoding="ascii") as fh:
            rec = json.load(fh)
        return read_csv(os.path.join(out, "lines2d.csv")), rec["lines"]

    def test_the_lines_only_study_needs_no_naming(self):
        got, rec = self.project(self.lines, "--view", self.view)
        self.assertEqual((rec["study"], rec["chosen_by"], len(got)), (self.study, "the lines' only study", len(self.rows)))

    def test_lines_of_several_studies_go_onto_a_render_one_study_at_a_time(self):
        with self.assertRaises(SystemExit):
            self.project(self.two, "--view", self.view)
        with self.assertRaises(SystemExit):
            self.project(self.two, "--view", self.view, "--study", "0003")
        got, rec = self.project(self.two, "--view", self.view, "--study", "0002")
        self.assertEqual(({g["study"] for g in got}, len(got)), ({"0002"}, len(self.rows)))
        self.assertEqual((rec["study"], rec["chosen_by"]), ("0002", "--study"))

    def test_a_manifest_rows_subject_names_its_study(self):
        manifest, file = manifest_of(self.tmp, "studies-manifest.json", self.square, None, self.study, 500)
        got, rec = self.project(self.two, "--manifest", manifest, "--file", file)
        self.assertEqual(({g["study"] for g in got}, len(got)), ({self.study}, len(self.rows)))
        self.assertEqual(rec["chosen_by"], "the manifest row's subject")
        manifest, file = manifest_of(self.tmp, "nobody-manifest.json", self.square, None, "0009", 500)
        with self.assertRaises(SystemExit):
            self.project(self.two, "--manifest", manifest, "--file", file)


class Realism(unittest.TestCase):
    """A render of SchwingNet's realism programme, the image its fluoroscopic edit converts, read
    from its own records as tools/realism.py's render_one writes them: the sample's last row of
    manifest.jsonl for the pose and the pixels, recipe.json for the distance and the spacing, and
    the CT the row names by its sha256 for the isocentre, its volume's centre; with its edits'
    files and the filter's verdicts beside it."""

    SAMPLE, POSE = "s0001_p018", {"alpha": 90, "y": 900, "z": 0}

    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.mask, cls.lines, cls.frames, cls.rows = exported()
        cls.lab, cls.aff, _ = phantom()
        cls.ct = os.path.join(cls.tmp, "realism-ct.nii.gz")
        nib.save(nib.Nifti1Image(np.where(cls.lab > 0, 1000, -1000).astype(np.int16), cls.aff), cls.ct)
        cls.folder = cls.render_folder("realism", cls.POSE, 256)
        cls.edits, cls.filter = os.path.join(cls.tmp, "realism-edits"), os.path.join(cls.tmp, "realism-filter")
        os.makedirs(os.path.join(cls.edits, "edited"))
        os.makedirs(cls.filter)
        with open(os.path.join(cls.edits, "edits.jsonl"), "w", encoding="ascii") as fh:
            for sample, arm in ((cls.SAMPLE, 0), (cls.SAMPLE, 1), ("s0002_p001", 0), (cls.SAMPLE, 2), (cls.SAMPLE, 3)):
                fh.write(json.dumps({"sample_id": sample, "arm": arm, "seed": 100 + arm, "seconds": 1.0}) + "\n")
            fh.write('{"sample_id": "%s", "arm"' % cls.SAMPLE)
        for arm, side in ((0, 256), (1, 256), (2, 128)):
            np.save(os.path.join(cls.edits, "edited", "%s__a%d.npy" % (cls.SAMPLE, arm)), np.zeros((side, side), np.float16))
        for name, arm in (("filter_kept.csv", 0), ("filter_dropped.csv", 1)):
            with open(os.path.join(cls.filter, name), "w", encoding="ascii") as fh:
                fh.write("sample_id,subject_id,pose_id\n%s__a%d,0001,17\n" % (cls.SAMPLE, arm))

    @classmethod
    def render_folder(cls, name, pose, pixels, raw_side=None, isocentre="volume-centre", ct_sha256=None):
        """A realism render folder holding the sample, an earlier row of it at another height
        written first, so the last row is the one read."""
        folder = os.path.join(cls.tmp, name)
        os.makedirs(os.path.join(folder, "raw"))
        with open(os.path.join(folder, "recipe.json"), "w", encoding="ascii") as fh:
            json.dump({"model": "klein-9b", "render_pixels": pixels, "render_sdd_mm": 1250.0, "render_spacing_mm": 0.6,
                       "isocentre": isocentre, "stored_pixels": 256}, fh)
        digests = {"ct_sha256": ct_sha256 or sha256(cls.ct), "truth_sha256": {"Vertebrae": sha256(cls.mask)}}
        rows = [dict(pose, y=650, pixels=pixels), dict(pose, pixels=pixels)]
        with open(os.path.join(folder, "manifest.jsonl"), "w", encoding="ascii") as fh:
            for row in rows:
                fh.write(json.dumps(dict(row, sample_id=cls.SAMPLE, subject_id=cls.rows[0]["study"], grid_pose=17,
                                         seconds=1.0, **digests), sort_keys=True) + "\n")
        np.save(os.path.join(folder, "raw", "%s.npy" % cls.SAMPLE), np.zeros((raw_side or pixels,) * 2, np.float16))
        return folder

    def project(self, folder, *more, sample=None):
        out = tempfile.mkdtemp(dir=self.tmp)
        said = quiet(MV.main, ["project", "--lines", self.lines, "--realism", folder, "--sample", sample or self.SAMPLE,
                               "--out", out] + list(more))
        with open(os.path.join(out, "VIEW.json"), encoding="ascii") as fh:
            return read_csv(os.path.join(out, "lines2d.csv")), json.load(fh), said

    def test_the_view_is_the_one_render_one_requested(self):
        # render_one's request: rot (alpha, 0, 0), xyz (0, y, z), the recipe's distance and
        # spacing on a square detector of the row's pixels, the principal point at the centre,
        # through nanoDRR's AP turn, about the CT's volume centre, (shape - 1) / 2 in voxels by the
        # affine its file holds
        got, rec, _ = self.project(self.folder, "--ct", self.ct)
        centre = nib.load(self.ct).affine @ np.array([(s - 1) / 2.0 for s in self.lab.shape] + [1.0])
        want = PJ.View(rot_deg=(90.0, 0.0, 0.0), xyz_mm=(0.0, 900.0, 0.0), isocentre_mm=tuple(centre[:3]), sdd=1250.0,
                       delx=0.6, height=256, width=256, orientation="AP")
        self.assertEqual(PJ.View(**rec["view"]), want)
        cam = PJ.Camera(want)
        for row, line in zip(self.rows, got):
            self.assertEqual([float(line["au"]), float(line["av"])], cam.project(point(row, "a")).uv[0].tolist())
        # about the volume's centre at 1.4 times, 110 mm of the phantom's middle fill the detector
        self.assertGreater(sum(line[e + "_in_beam"] == "True" for line in got for e in "ab"), 0.9 * 2 * len(got))
        self.assertEqual((rec["crop"], rec["from"]["sample"], rec["from"]["file"], rec["from"]["ct_sha256"]),
                         (None, self.SAMPLE, "raw/%s.npy" % self.SAMPLE, sha256(self.ct)))
        self.assertEqual((rec["lines"]["chosen_by"], rec["flexray"]["render"]), ("the lines' only study", "not recorded"))

    def test_the_labels_are_named_where_the_render_holds_them(self):
        _, rec, said = self.project(self.folder, "--ct", self.ct, "--labels", self.mask, "--scheme", "verse")
        self.assertEqual(rec["labels"]["rendered_as"], "Vertebrae")
        self.assertIn("with both ends on their level's shadow", said)

    def test_the_edits_of_the_render_are_listed_with_the_filters_verdicts(self):
        _, rec, said = self.project(self.folder, "--ct", self.ct, "--edits", self.edits, "--filter", self.filter)
        self.assertEqual([(e["arm"], e["seed"], e["pixels_kept"], e["filter"]) for e in rec["edits"]],
                         [(0, 100, True, "kept"), (1, 101, True, "dropped"), (2, 102, False, "not scored"),
                          (3, 103, "missing", "not scored")])
        self.assertEqual(rec["edits"][0]["file"], "edited/%s__a0.npy" % self.SAMPLE)
        self.assertIn("4 edits of the render, 2 holding its pixels, 1 kept by the filter", said)
        _, rec, said = self.project(self.folder, "--ct", self.ct, "--edits", self.edits)
        self.assertEqual({e["filter"] for e in rec["edits"]}, {"not given"})
        self.assertNotIn("kept by the filter", said)

    def test_a_render_the_records_do_not_bear_out_refuses(self):
        other = os.path.join(self.tmp, "realism-other-ct.nii.gz")
        nib.save(nib.Nifti1Image(np.where(self.lab > 0, 900, -1000).astype(np.int16), self.aff), other)
        refused = [((self.folder,), {}), ((self.folder, "--ct", other), {}),
                   ((self.folder, "--ct", self.ct), {"sample": "s0009_p001"}),
                   ((self.render_folder("realism-raw", self.POSE, 256, raw_side=512), "--ct", self.ct), {}),
                   ((self.render_folder("realism-iso", self.POSE, 256, isocentre="sampled"), "--ct", self.ct), {})]
        for args, more in refused:
            with self.assertRaises(SystemExit, msg=args):
                self.project(*args, **more)
        with contextlib.redirect_stderr(io.StringIO()):
            for argv in (["--realism", self.folder, "--ct", self.ct],
                         ["--view", os.path.join(self.tmp, "view0.json"), "--filter", self.filter]):
                with self.assertRaises(SystemExit, msg=argv):
                    MV.main(["project", "--lines", self.lines, "--out", self.tmp] + argv)
        _, cam, v = recorded_views()[0]
        view = os.path.join(self.tmp, "realism-view.json")
        with open(view, "w", encoding="ascii") as fh:
            json.dump(v["view"], fh)
        with self.assertRaises(SystemExit):
            quiet(MV.main, ["project", "--lines", self.lines, "--view", view, "--edits", self.edits, "--out", self.tmp])


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
    """FleXray itself: the record's views rendered again give its labels at both thresholds, its
    supports where the channels are above zero, its counts and its camera, its crop rendered again gives the crop's supports, and beads rendered on two views the
    record does not hold land where they are projected, each from behind on a square detector of
    256 pixels as SchwingNet's are: one through nanoDRR's AP turn half round, as SchwingNet poses
    its posterior views, and one through its PA turn, which SchwingNet does not use."""

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
            for key, threshold in RECORD["label_thresholds"].items():
                got = FR.labels(bone, self.lab, self.aff, cam.view, threshold)
                for level, i in RECORD["phantom"]["ids"].items():
                    np.testing.assert_array_equal(got[i], FR.unpack(v[key][level], got.shape[1:]), err_msg=(name, key))
            self.assertEqual(FR.counts_of(self.lab, self.aff, cam.view, RECORD["phantom"]["ids"]), v["counts"], name)
            again = FR.camera(cam.view, np.array(v["camera"]["uv"]))
            for key in ("rt_inv", "k_inv", "source", "detector"):
                np.testing.assert_allclose(again[key], v["camera"][key], rtol=0, atol=1e-12, err_msg=key)

    def test_flexray_renders_the_crop_again(self):
        again = FR.crop_record(self.lab, self.aff, np.array(RECORD["isocentre_mm"]), RECORD["phantom"]["ids"])
        self.assertEqual(PJ.View(**again["view"]), PJ.View(**RECORD["crop"]["view"]))
        self.assertEqual((again["crop"], again["supports"]), (RECORD["crop"]["crop"], RECORD["crop"]["supports"]))

    def test_beads_on_views_not_recorded_land_where_projected(self):
        iso = tuple(RECORD["isocentre_mm"])
        views = [PJ.View(rot_deg=(184.0, -6.0, 3.0), xyz_mm=(10.0, 700.0, -5.0), isocentre_mm=iso, sdd=1200.0,
                         delx=1.0, height=256, width=256, orientation="AP"),
                 PJ.View(rot_deg=(4.0, -6.0, 3.0), xyz_mm=(10.0, -700.0, -5.0), isocentre_mm=iso, sdd=1200.0,
                         delx=1.0, height=256, width=256, orientation="PA")]
        balls, centroids = FR.bead_labels(self.lab.shape, self.aff, np.array(RECORD["beads"]["centroids_mm"]))
        for view in views:
            cam = PJ.Camera(view)
            self.assertGreater(float(cam.beam[1]), 0.9, view.orientation)
            rendered = FR.render(np.where(balls > 0, FR.BONE_HU, FR.AIR_HU), balls, self.aff, view, FR.BEAD_SAMPLES)
            seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(centroids))]
            self.assertTrue(all(c is not None for c in seen), view.orientation)
            err = np.linalg.norm(cam.project(centroids).uv - np.array(seen), axis=1)
            self.assertLessEqual(float(err.max()), BEAD_PX, view.orientation)


if __name__ == "__main__":
    unittest.main()
