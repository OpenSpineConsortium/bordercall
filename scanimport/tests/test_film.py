"""One image with its corners or FleXray's masks to millimetres: the image's header sets the scale
and is compared with the annotation's, an annotation of another image is refused, what the caller
says is held to the annotation, FleXray names bodies only where it keeps to the reader's names and
never measures whole vertebrae, and masks of bodies alone give corners by the largest
quadrilateral."""
import itertools
import json
import os
import tempfile
import unittest

import numpy as np

from scanimport import film as F
from scanimport import radiograph as XR
from scanimport import readers as RD
from scanimport.tests import dicom_files as DF

H, W = 1000, 600                      # the image: side 1000, padded 200 on each side to a square


def rectangle(cx, cy, w, h, angle_deg, sub=4):
    """The share of each canvas pixel a rectangle of the image covers: FleXray's probabilities for
    a body drawn exactly."""
    side = max(H, W)
    pad = np.array([(side - W) // 2, (side - H) // 2])
    n = F.CANVAS * sub
    c = (np.arange(n) + 0.5) / sub
    u, v = np.meshgrid(c, c)
    x, y = u * side / F.CANVAS - pad[0], v * side / F.CANVAS - pad[1]
    a = np.radians(angle_deg)
    lx = (x - cx) * np.cos(a) + (y - cy) * np.sin(a)
    ly = -(x - cx) * np.sin(a) + (y - cy) * np.cos(a)
    inside = (np.abs(lx) <= w / 2) & (np.abs(ly) <= h / 2)
    return inside.reshape(F.CANVAS, sub, F.CANVAS, sub).mean(axis=(1, 3))


def corners_of(cx, cy, w, h, angle_deg):
    a = np.radians(angle_deg)
    ex, ey = np.array([np.cos(a), np.sin(a)]), np.array([-np.sin(a), np.cos(a)])
    c = np.array([cx, cy])
    return [list(c - ex * w / 2 - ey * h / 2), list(c + ex * w / 2 - ey * h / 2),
            list(c + ex * w / 2 + ey * h / 2), list(c - ex * w / 2 + ey * h / 2)]


BODIES = {"T12": 300.0, "L1": 435.0, "L2": 570.0}      # centre rows; 100 by 70 pixels, turned 10 degrees


def flexray_probabilities(levels=BODIES):
    prob = np.zeros((len(F.FLEXRAY_LABELS), F.CANVAS, F.CANVAS), np.float32)
    for lv, cy in levels.items():
        prob[F.FLEXRAY_LABELS.index("vertebra_%s" % lv.lower())] = rectangle(300.0, cy, 100.0, 70.0, 10.0)
    return prob


def masks_at(rows_by_level):
    """FleXray's probabilities with each level's channel the union of bodies drawn at the given
    centre rows: one mask over two bodies, or a mask over a body another level should cover."""
    prob = np.zeros((len(F.FLEXRAY_LABELS), F.CANVAS, F.CANVAS), np.float32)
    for lv, rows in rows_by_level.items():
        ch = F.FLEXRAY_LABELS.index("vertebra_%s" % lv.lower())
        for cy in rows:
            prob[ch] = np.maximum(prob[ch], rectangle(300.0, cy, 100.0, 70.0, 10.0))
    return prob


def annotation(names, sha="", width=W, height=H, pixel_mm=None, view="ap", modality="film", reader="r01"):
    bodies = [{"level": n, "corners": corners_of(300.0, cy, 100.0, 70.0, 10.0), "visible": [True] * 4}
              for n, cy in zip(names, BODIES.values())]
    image = {"sha256": sha, "width": width, "height": height, "view": view, "pixel_mm": pixel_mm}
    if modality is not None:
        image["modality"] = modality
    return {"format": XR.FORMAT, "image": image, "reader": {"id": reader}, "bodies": bodies}


def flexray_problems(col):
    return [q for q in col.study["problems"] if "FleXray" in q]


class Film(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.tmp.name
        cls.dicom = os.path.join(d, "ap.dcm")
        DF.write_projection(cls.dicom, np.zeros((H, W)), attrs={"ImagerPixelSpacing": [0.14, 0.14],
                                                                 "EstimatedRadiographicMagnificationFactor": 1.4,
                                                                 "PatientSex": "F", "PatientAge": "047Y"})
        cls.sha = RD.sha256_of(cls.dicom)
        from PIL import Image
        cls.png = os.path.join(d, "ap.png")
        Image.fromarray(np.zeros((H, W), np.uint8)).save(cls.png)
        cls.png_sha = RD.sha256_of(cls.png)
        cls.prob = os.path.join(d, "ap_probabilities.npy")
        np.save(cls.prob, flexray_probabilities())
        cls.fiducial = os.path.join(d, "fiducial.dcm")
        DF.write_projection(cls.fiducial, np.zeros((H, W)), attrs={"PixelSpacing": [0.1, 0.1],
                                                                   "PixelSpacingCalibrationType": "FIDUCIAL",
                                                                   "ImagerPixelSpacing": [0.14, 0.14]})
        cls.fiducial_alone = os.path.join(d, "fiducial_alone.dcm")
        DF.write_projection(cls.fiducial_alone, np.zeros((H, W)), attrs={"PixelSpacing": [0.1, 0.1],
                                                                         "PixelSpacingCalibrationType": "FIDUCIAL"})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def write(self, name, doc):
        p = os.path.join(self.tmp.name, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            json.dump(doc, fh)
        return p

    def arrays(self, name, prob):
        p = os.path.join(self.tmp.name, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        np.save(p, prob)
        return p

    def test_the_header_sets_the_scale(self):
        p = self.write("named.json", annotation(["T12", "L1", "L2"], sha=self.sha, pixel_mm=0.2))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p)
        self.assertEqual(col.levels, ["T12", "L1", "L2"])
        for b in col.bodies:
            self.assertAlmostEqual(b.values["endplate"], 100.0 * 0.1, places=6)
        self.assertEqual(col.study["annotation"], "human")
        self.assertEqual(col.study["covariates"]["sex"]["value"], "F")
        self.assertIn("Estimated Radiographic Magnification Factor", col.study["scale_basis"][0])
        self.assertTrue(any("differs from the image's 0.1400 at the detector" in q for q in col.study["problems"]))
        # the pixel the annotation states, beside the pixels the chords were actually scaled by
        self.assertEqual(col.study["pixel_mm_stated"], [0.2])
        self.assertAlmostEqual(col.study["pixel_mm_at_detector"][0], 0.14)
        self.assertAlmostEqual(col.study["pixel_mm_at_patient"][0], 0.1)

    def test_a_header_whose_pixel_is_at_the_patient_is_compared_where_it_can_be(self):
        p = self.write("fid.json", annotation(["T12", "L1", "L2"], pixel_mm=0.3))
        col = F.ingest_image(self.fiducial, "s1", "test", "human", corners=p)
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 100.0 * 0.1, places=6)
        self.assertTrue(any("differs from the image's 0.1400 at the detector" in q for q in col.study["problems"]))
        col = F.ingest_image(self.fiducial_alone, "s1", "test", "human", corners=p)
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 100.0 * 0.1, places=6)
        self.assertTrue(any("cannot be compared" in q for q in col.study["problems"]))

    def test_a_scale_that_leaves_out_the_detectors_pixel_is_said_not_compared(self):
        scale = {"pixel_mm": 0.1, "magnification": 1.0, "log_sd": 0.03, "basis": "a fiducial"}
        image = RD.Projection(size=(H, W), sha256="0" * 64, source="test", scale=scale)
        problems = []
        self.assertIs(F.scale_of(image, annotation(["L1"], pixel_mm=0.3), problems), scale)
        self.assertEqual(len(problems), 1)
        self.assertIn("cannot be compared", problems[0])
        self.assertIs(F.scale_of(image, annotation(["L1"]), []), scale)

    def test_a_picture_takes_the_annotations_pixel_size(self):
        p = self.write("png.json", annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2))
        col = F.ingest_image(self.png, "s1", "test", "human", corners=p)
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 100.0 * 0.2 / XR.M0, places=6)
        self.assertTrue(col.study["scale_known"])
        # the reader's word that the picture has no scale is moot once the annotation gives one
        self.assertEqual(col.study["problems"], [])
        self.assertEqual(col.study["pixel_mm_at_detector"], [0.2])

    def test_a_picture_with_no_pixel_size_anywhere_says_so_once(self):
        p = self.write("png_unscaled.json", annotation(["T12", "L1", "L2"], sha=self.png_sha))
        col = F.ingest_image(self.png, "s1", "test", "human", corners=p)
        self.assertFalse(col.study["scale_known"])
        self.assertEqual(sum("scale is unknown" in q for q in col.study["problems"]), 1)

    def test_an_annotation_of_another_image_is_refused(self):
        for doc in (annotation(["L1"], sha="ab" * 32), annotation(["L1"], width=W + 1)):
            with self.assertRaises(SystemExit):
                F.ingest_image(self.dicom, "s1", "t", "human", corners=self.write("other.json", doc))

    def test_a_digest_in_capitals_is_the_same_digest(self):
        p = self.write("upper.json", annotation(["T12", "L1", "L2"], sha=self.sha.upper()))
        self.assertEqual(F.ingest_image(self.dicom, "s1", "t", "human", corners=p).levels, ["T12", "L1", "L2"])

    def test_the_callers_modality_is_held_to_the_annotations(self):
        from scanimport import tiers as T
        silent = self.write("silent.json", annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2, modality=None))
        col = F.ingest_image(self.png, "s1", "t", "human", corners=silent, modality="drr")
        self.assertEqual(col.study["modality"], "drr")
        self.assertEqual(T.study_tier(col.study)[0], "none")
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=silent).study["modality"], "film")
        film = self.write("film.json", annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.png, "s1", "t", "human", corners=film, modality="drr")
        self.assertIn("--modality drr", str(e.exception))
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=film, modality="Film").study["modality"],
                         "film")
        masks = F.ingest_image(self.dicom, "s1", "t", None, flexray=self.prob, mask_content="body", view="ap",
                               modality="drr")
        self.assertEqual(masks.study["modality"], "drr")
        # a modality stated as null is no modality: the caller's fills it, and with none it is film, never "None"
        null = annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2)
        null["image"]["modality"] = None
        null = self.write("null.json", null)
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=null).study["modality"], "film")
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=null, modality="drr").study["modality"],
                         "drr")

    def test_a_blank_modality_of_spaces_is_filled_in_by_the_callers(self):
        blank = annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2, modality="  ")
        blank = self.write("blank_modality.json", blank)
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=blank).study["modality"], "film")
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=blank, modality="drr").study["modality"],
                         "drr")

    def test_the_callers_view_fills_in_what_the_annotation_leaves_out_and_is_held_to_what_it_states(self):
        for missing in ("absent", None, " "):
            doc = annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2)
            if missing == "absent":
                del doc["image"]["view"]
            else:
                doc["image"]["view"] = missing
            p = self.write("noview.json", doc)
            self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=p, view="ap").study["views"], ["ap"])
            with self.assertRaises(SystemExit) as e:
                F.ingest_image(self.png, "s1", "t", "human", corners=p)
            self.assertIn("view", str(e.exception))
        stated = self.write("apview.json", annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.png, "s1", "t", "human", corners=stated, view="lateral")
        self.assertIn("--view lateral", str(e.exception))
        self.assertEqual(F.ingest_image(self.png, "s1", "t", "human", corners=stated, view="pa").study["views"], ["ap"])

    def test_a_pixel_size_that_is_not_a_length_is_refused_beside_a_header_too(self):
        p = self.write("zero.json", annotation(["T12", "L1", "L2"], sha=self.sha, pixel_mm=0))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", "human", corners=p)
        self.assertIn("positive length", str(e.exception))

    def test_who_drew_the_corners_is_held_before_flexray_names_anything(self):
        model = self.write("model.json", annotation(["?", "?", "L2"], sha=self.sha, reader="model:run7"))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", "human", corners=model, flexray=self.prob)
        self.assertIn("model:run7", str(e.exception))
        person = self.write("person.json", annotation(["?", "?", "L2"], sha=self.sha))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", None, corners=person, flexray=self.prob)
        self.assertIn("--annotation", str(e.exception))
        col = F.ingest_image(self.dicom, "s1", "t", "machine", corners=model, flexray=self.prob)
        self.assertEqual(col.study["corners_drawn_by"], "machine")

    def test_an_image_alone_is_refused(self):
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", "human")
        self.assertIn("drawn on it", str(e.exception))

    def test_whole_vertebrae_alone_are_never_measured(self):
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", None, flexray=self.prob, view="ap")
        self.assertIn("whole vertebrae", str(e.exception))

    def test_flexray_names_unnamed_bodies_and_the_annotation_becomes_a_machines(self):
        p = self.write("unnamed.json", annotation(["?", "?", "L2"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=self.prob)
        self.assertEqual(col.levels, ["T12", "L1", "L2"])
        self.assertEqual(col.study["annotation"], "machine")
        self.assertEqual(col.study["flexray"]["named"], 2)
        self.assertEqual(col.study["corners_drawn_by"], "human")
        self.assertEqual(flexray_problems(col), [])

    def test_flexray_that_contradicts_a_readers_name_names_nothing(self):
        # FleXray calls the bodies T12, L1, L2; the reader calls the third L3, so FleXray's count is a body off
        p = self.write("shifted.json", annotation(["?", "?", "L3"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=self.prob)
        self.assertEqual(col.levels, ["L3", "?", "?"])
        self.assertEqual(col.study["annotation"], "human")
        self.assertEqual(col.study["flexray"]["named"], 0)
        self.assertTrue(any("named L3 by the annotation and L2 by FleXray" in q for q in col.study["problems"]))
        self.assertTrue(any("names none of the bodies the annotation left ? (2)" in q for q in col.study["problems"]))

    def test_flexray_never_repeats_a_name_the_reader_gave(self):
        # FleXray's L1 mask covers the unnamed top body as well as the body the reader named L1
        prob = self.arrays("repeat/p.npy", masks_at({"L1": [BODIES["T12"], BODIES["L1"]], "L2": [BODIES["L2"]]}))
        p = self.write("repeat.json", annotation(["?", "L1", "L2"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=prob)
        self.assertEqual(col.levels, ["L1", "L2", "?"])
        self.assertEqual(col.study["flexray"]["named"], 0)
        self.assertEqual(col.study["annotation"], "human")
        self.assertTrue(any("body 0" in q and "a name the annotation gives another body" in q
                            for q in col.study["problems"]))

    def test_flexray_never_breaks_the_order_of_the_readers_names(self):
        # FleXray covers only the top body, and calls it L3, above the reader's L1 and L2
        prob = self.arrays("order/p.npy", masks_at({"L3": [BODIES["T12"]]}))
        p = self.write("order.json", annotation(["?", "L1", "L2"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=prob)
        self.assertEqual(col.levels, ["L1", "L2", "?"])
        self.assertEqual(col.study["flexray"]["named"], 0)
        self.assertTrue(any("body 0" in q and "above body 1, which the annotation names L1" in q
                            for q in col.study["problems"]))

    def test_two_flexray_calls_that_cross_leave_both_unnamed(self):
        prob = self.arrays("cross/p.npy", masks_at({"L1": [BODIES["T12"]], "T12": [BODIES["L1"]]}))
        p = self.write("cross.json", annotation(["?", "?", "L3"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=prob)
        self.assertEqual(col.levels, ["L3", "?", "?"])
        self.assertEqual(col.study["flexray"]["named"], 0)
        self.assertEqual(sum("repeats or crosses" in q for q in col.study["problems"]), 2)

    def test_each_body_left_unnamed_that_flexray_does_not_call_says_why(self):
        # the top body has a hidden corner; the bottom one sits where no mask reaches
        doc = annotation(["?", "L1", "?"], sha=self.sha)
        doc["bodies"][0]["visible"] = [True, False, True, True]
        doc["bodies"][2]["corners"] = corners_of(300.0, 900.0, 100.0, 70.0, 10.0)
        p = self.write("misses.json", doc)
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=self.prob)
        self.assertEqual(col.study["flexray"]["named"], 0)
        said = [q for q in col.study["problems"] if "is not called by FleXray" in q]
        self.assertEqual(len(said), 2, msg=str(col.study["problems"]))
        self.assertTrue(any(q.startswith("body 0,") and "a corner is missing or hidden" in q for q in said))
        self.assertTrue(any(q.startswith("body 2,") and "no level's mask covers a quarter of it" in q for q in said))
        empty = self.arrays("none/p.npy", np.zeros((len(F.FLEXRAY_LABELS), F.CANVAS, F.CANVAS), np.float32))
        col = F.ingest_image(self.dicom, "s1", "test", "human", corners=p, flexray=empty)
        self.assertTrue(any(q.startswith("body 2,") and "hold no vertebra" in q for q in col.study["problems"]))

    def test_arrays_with_no_vertebra_channel_are_refused(self):
        # TotalSegmentator's spelling, not FleXray's: nothing would be named or found
        prob = self.arrays("ts/p.npy", np.zeros((4, F.CANVAS, F.CANVAS), np.float32))
        self.write("ts/label_names.json", ["background", "vertebrae_T12", "vertebrae_L1", "vertebrae_L2"])
        p = self.write("ts.json", annotation(["?", "L1", "L2"], sha=self.sha))
        for kw in ({"corners": p}, {"mask_content": "body", "view": "ap"}):
            with self.assertRaises(SystemExit) as e:
                F.ingest_image(self.dicom, "s1", "t", "human", flexray=prob, **kw)
            self.assertIn("as FleXray spells them", str(e.exception))

    def test_arrays_that_find_no_vertebra_are_said(self):
        prob = self.arrays("empty/p.npy", np.zeros((len(F.FLEXRAY_LABELS), F.CANVAS, F.CANVAS), np.float32))
        p = self.write("empty.json", annotation(["?", "L1", "L2"], sha=self.sha))
        col = F.ingest_image(self.dicom, "s1", "t", "human", corners=p, flexray=prob)
        self.assertTrue(any("hold no vertebra" in q for q in col.study["problems"]))
        with self.assertRaises(SystemExit) as e:
            F.ingest_image(self.dicom, "s1", "t", None, flexray=prob, mask_content="body", view="ap")
        self.assertIn("nothing to measure", str(e.exception))

    def test_the_names_file_is_the_one_given_else_the_one_beside_the_arrays(self):
        prob = self.arrays("named/p.npy", flexray_probabilities())
        self.assertIsNone(F.names_file(prob))
        beside = self.write("named/label_names.json", list(F.FLEXRAY_LABELS))
        self.assertEqual(F.names_file(prob), beside)
        with self.assertRaises(SystemExit):
            F.names_file(prob, os.path.join(self.tmp.name, "named", "missing.json"))

    def test_masks_and_logits_are_read_as_probabilities(self):
        prob = flexray_probabilities()
        for name, arr, kind in (("m.npy", (prob > 0.5).astype(np.uint8), "masks"),
                                ("l.npy", np.log(np.clip(prob, 1e-6, 1 - 1e-6) / np.clip(1 - prob, 1e-6, 1)), "logits")):
            path = os.path.join(self.tmp.name, name)
            np.save(path, arr)
            got, names, k = F.read_flexray(path)
            self.assertEqual(k, kind)
            self.assertEqual(sorted(F.vertebrae(got, names, k), key=F.LEVELS.index), ["T12", "L1", "L2"])

    def test_body_masks_give_corners_within_a_canvas_pixel(self):
        col = F.ingest_image(self.dicom, "s1", "t", None, flexray=self.prob, mask_content="body", view="ap")
        self.assertEqual(col.levels, ["T12", "L1", "L2"])
        canvas_px = max(H, W) / F.CANVAS
        canvas_px_mm = canvas_px * 0.1
        for b in col.bodies:
            self.assertLessEqual(abs(b.values["endplate"] - 10.0), canvas_px_mm)
            self.assertLessEqual(abs(b.values["endplate_lower"] - 10.0), canvas_px_mm)
        self.assertEqual(col.study["annotation"], "machine")
        # each corner, in the format's order, against the drawn rectangle's
        prob, names, kind = F.read_flexray(self.prob)
        for body in F.corners_from_masks(F.vertebrae(prob, names, kind), H, W):
            drawn = np.array(corners_of(300.0, BODIES[body["level"]], 100.0, 70.0, 10.0))
            off = np.linalg.norm(np.array(body["corners"]) - drawn, axis=1)
            self.assertLessEqual(float(off.max()), canvas_px, body["level"])

    def test_the_command_line_writes_the_column_and_hashes_every_input(self):
        import contextlib
        import io
        from scanimport.__main__ import main
        p = self.write("cli.json", annotation(["T12", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2))
        out = os.path.join(self.tmp.name, "out")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["ingest-image", "--image", self.png, "--corners", p, "--flexray", self.prob, "--study", "f1",
                  "--source", "test", "--annotation", "human", "--out", out])
        with open(os.path.join(out, "columns", "f1.json")) as fh:
            col = json.load(fh)
        self.assertEqual([b["level"] for b in col["bodies"]], ["T12", "L1", "L2"])
        # FleXray agreed with every name the reader gave and named nothing itself, so the names stay a person's
        self.assertEqual(col["study"]["annotation"], "human")
        self.assertEqual(col["study"]["flexray"]["named"], 0)
        with open(os.path.join(out, "MANIFEST.json")) as fh:
            manifest = fh.read()
        for path in (self.png, p, self.prob):
            self.assertIn(RD.sha256_of(path), manifest)

    def test_the_command_line_hashes_the_names_found_beside_the_arrays(self):
        import contextlib
        import io
        from scanimport.__main__ import main
        prob = self.arrays("fx/ap_probabilities.npy", flexray_probabilities())
        names = self.write("fx/label_names.json", list(F.FLEXRAY_LABELS))
        p = self.write("fx.json", annotation(["?", "L1", "L2"], sha=self.png_sha, pixel_mm=0.2))
        out = os.path.join(self.tmp.name, "out_fx")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["ingest-image", "--image", self.png, "--corners", p, "--flexray", prob, "--study", "f2",
                  "--source", "test", "--annotation", "human", "--out", out])
        with open(os.path.join(out, "columns", "f2.json")) as fh:
            col = json.load(fh)
        self.assertEqual(col["study"]["flexray"]["names"], "label_names.json")
        with open(os.path.join(out, "MANIFEST.json")) as fh:
            inputs = json.load(fh)["runs"][-1]["inputs"]
        self.assertEqual(inputs.get(names), RD.sha256_of(names))


class Geometry(unittest.TestCase):
    def test_canvas_and_image_coordinates(self):
        np.testing.assert_allclose(F.to_image(np.array([[0.0, 0.0], [256.0, 256.0]]), H, W), [[-200, 0], [800, 1000]])
        xy = np.array([[12.5, 700.25]])
        np.testing.assert_allclose(F.to_image(F.to_canvas(xy, H, W), H, W), xy)

    def test_the_largest_quadrilateral_is_the_exact_maximum(self):
        rng = np.random.default_rng(3)
        pts = rng.normal(size=(40, 2))
        quad = F.largest_quadrilateral(pts)

        def area(q):
            x, y = q[:, 0], q[:, 1]
            return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        from scipy.spatial import ConvexHull
        hull = pts[ConvexHull(pts).vertices]
        best = max(area(hull[list(c)]) for c in itertools.combinations(range(len(hull)), 4))
        self.assertAlmostEqual(area(quad), best, places=12)

    def test_corners_are_ordered_as_the_format_orders_them(self):
        quad = np.array([[10.0, 50.0], [0.0, 0.0], [10.0, 0.0], [0.0, 50.0]])
        np.testing.assert_array_equal(F.ordered(quad, np.array([0.0, -1.0])), [[0, 0], [10, 0], [10, 50], [0, 50]])
        # the head to the image's left: superior is the left side, and its left is the image's bottom
        np.testing.assert_array_equal(F.ordered(quad, np.array([-1.0, 0.0])), [[0, 50], [0, 0], [10, 0], [10, 50]])


if __name__ == "__main__":
    unittest.main()
