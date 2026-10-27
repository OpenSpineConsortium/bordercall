"""Four corners per body to millimetres, view by view."""
import json
import math
import os
import tempfile
import unittest

from scanimport import radiograph as R


def body(level, x, y, w, h, visible=(True, True, True, True), chords=None):
    b = {"level": level, "corners": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], "visible": list(visible),
         "findings": []}
    if chords:
        b["chords"] = chords
    return b


def annotation(view, bodies, pixel_mm=0.2, anterior=None, reader="r01"):
    image = {"sha256": "0" * 64, "width": 2000, "height": 3000, "view": view, "modality": "film", "pixel_mm": pixel_mm}
    if anterior:
        image["anterior"] = anterior
    return {"format": R.FORMAT, "image": image, "reader": {"id": reader, "role": "annotator"},
            "column": {"call": "T12L5", "basis": "counted from C2", "confidence": "sure"}, "bodies": bodies}


class Corners(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, doc):
        p = os.path.join(self.tmp.name, name)
        with open(p, "w") as fh:
            json.dump(doc, fh)
        return p

    def test_ap_and_lateral_merge_into_one_column_in_millimetres(self):
        # 0.2 mm pixels and magnification 1.25: a 250-pixel line is 40 mm at the body
        ap = self.write("ap.json", annotation("AP", [body("L2", 100, 900, 250, 150,
                                                          chords={"canal_w": [[160, 950], [285, 950]]}),
                                                     body("L1", 100, 700, 240, 150)]))
        lat = self.write("lat.json", annotation("lateral", [body("L1", 100, 700, 200, 175)], anterior="left"))
        col = R.ingest([ap, lat], "f1", "test", "human", magnification=1.25)
        self.assertEqual(col.levels, ["L1", "L2"])
        l1, l2 = col.bodies
        self.assertAlmostEqual(l2.values["endplate"], 250 * 0.2 / 1.25)
        self.assertAlmostEqual(l2.values["canal_w"], 125 * 0.2 / 1.25)
        self.assertAlmostEqual(l1.values["endplate_depth"], 200 * 0.2 / 1.25)
        self.assertAlmostEqual(l1.values["h_post"], 175 * 0.2 / 1.25)
        self.assertEqual(col.study["views"], ["ap", "lateral"])
        self.assertTrue(col.study["scale_known"])
        # a stated magnification carries the spread a header's stated factor does, whichever route states it
        from scanimport import readers as RD
        self.assertAlmostEqual(col.study["scale_log_sd"], RD.STATED_LOG_SD)

    def test_a_callers_magnification_and_spread_are_held_to_their_bounds(self):
        doc = annotation("ap", [body("L3", 0, 0, 230, 100)])
        for bad in (0.0, 0.8, -1.2, float("nan"), float("inf")):
            with self.assertRaises(SystemExit, msg=str(bad)) as e:
                R.doc_scale(doc, bad, None)
            self.assertIn("--magnification", str(e.exception))
        for bad in (-0.3, float("nan")):
            with self.assertRaises(SystemExit, msg=str(bad)) as e:
                R.doc_scale(doc, None, bad)
            self.assertIn("--magnification-sd", str(e.exception))
        # a magnification of 1 says the pixel is already at the patient, and a spread of 0 that it is exact
        sc = R.doc_scale(doc, 1.0, 0.0)
        self.assertEqual((sc["pixel_mm"], sc["magnification"], sc["log_sd"]), (0.2, 1.0, 0.0))
        self.assertEqual(R.doc_scale(doc, None, 0.07)["log_sd"], 0.07)

    def test_chords_carry_any_measure_the_corners_do_not_give_on_a_view_that_shows_it(self):
        ap = self.write("ap.json", annotation("ap", [body("L2", 100, 900, 250, 150, chords={
            "tp_span": [[0, 950], [400, 950]], "endplate": [[0, 0], [9, 0]], "canal_ap": [[0, 0], [0, 9]]})]))
        b = R.ingest([ap], "f1", "t", "human", magnification=1.25).bodies[0]
        self.assertAlmostEqual(b.values["tp_span"], 400 * 0.2 / 1.25)
        self.assertAlmostEqual(b.values["endplate"], 250 * 0.2 / 1.25)          # the corners', never the chord's
        self.assertIn("not read", b.flags["endplate"])
        self.assertNotIn("canal_ap", b.values)                                  # a lateral measure on an AP
        self.assertIn("not read", b.flags["canal_ap"])
        lat = self.write("lat.json", annotation("lateral", [body("L2", 100, 900, 200, 150, chords={
            "spinous_length": [[300, 975], [420, 975]]})], anterior="left"))
        b = R.ingest([lat], "f1", "t", "human", magnification=1.25).bodies[0]
        self.assertAlmostEqual(b.values["spinous_length"], 120 * 0.2 / 1.25)

    def test_the_default_magnification_is_recorded(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)]))], "f1", "t", "human")
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 230 * 0.2 / R.M0)
        self.assertEqual(col.study["magnification"], R.M0)
        self.assertEqual(col.study["scale_log_sd"], R.M_LOG_SD)

    def test_the_default_magnification_is_the_readers_and_sits_in_the_measured_range(self):
        # One default for an annotation's pixel and a header's, sourced in readers.py: midway between
        # Ravi and Rampersaud's cervical and lumbar means, 1.21 and 1.31, with their measured extremes,
        # 1.06 and 1.63, under two spreads below it and three above it.
        from scanimport import readers as RD
        self.assertEqual((R.M0, R.M_LOG_SD), (RD.DEFAULT_MAGNIFICATION, RD.DEFAULT_MAGNIFICATION_LOG_SD))
        self.assertAlmostEqual(R.M0, (1.21 + 1.31) / 2)
        self.assertLess(math.log(R.M0 / 1.06), 2 * R.M_LOG_SD)
        self.assertLess(math.log(1.63 / R.M0), 3 * R.M_LOG_SD)

    def test_no_side_no_posterior_height(self):
        col = R.ingest([self.write("l.json", annotation("lateral", [body("L3", 0, 0, 200, 150)]))], "f1", "t", "human")
        self.assertTrue(math.isnan(col.bodies[0].values["h_post"]))
        self.assertIn("anterior", col.bodies[0].flags["h_post"])
        right = R.ingest([self.write("r.json", annotation("lateral", [body("L3", 0, 0, 200, 150)]))], "f1", "t", "human",
                         anterior="right")
        self.assertAlmostEqual(right.bodies[0].values["h_post"], 150 * 0.2 / R.M0)

    def test_a_hidden_corner_gives_no_chord(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100, (True, False, True, True))]))],
                       "f1", "t", "human")
        self.assertTrue(math.isnan(col.bodies[0].values["endplate"]))
        self.assertFalse(math.isnan(col.bodies[0].values["endplate_lower"]))

    def test_no_pixel_size_leaves_pixels_and_an_unknown_scale(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)], pixel_mm=None))], "f1", "t", "human")
        self.assertEqual(col.bodies[0].values["endplate"], 230.0)
        self.assertFalse(col.study["scale_known"])
        self.assertIsNone(col.study["scale_log_sd"])
        for key in ("pixel_mm_stated", "pixel_mm_at_detector", "pixel_mm_at_patient"):
            self.assertEqual(col.study[key], [None], key)

    def test_the_pixel_used_is_recorded_beside_the_pixel_stated(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)]))], "f1", "t", "human")
        self.assertEqual(col.study["pixel_mm_stated"], [0.2])
        self.assertEqual(col.study["pixel_mm_at_detector"], [0.2])
        self.assertAlmostEqual(col.study["pixel_mm_at_patient"][0], 0.2 / R.M0)
        # a scale other than the annotation's (the image's header, on film.py's route) is what is recorded as used
        header = {"pixel_mm": 0.1, "pixel_mm_at_detector": 0.14, "magnification": 1.4, "log_sd": 0.05, "basis": "header"}
        col = R.ingest_docs([annotation("ap", [body("L3", 0, 0, 230, 100)])], [header], "f1", "t", "human")
        self.assertEqual(col.study["pixel_mm_stated"], [0.2])
        self.assertEqual(col.study["pixel_mm_at_detector"], [0.14])
        self.assertEqual(col.study["pixel_mm_at_patient"], [0.1])
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 230 * 0.1)

    def test_a_pixel_size_that_is_not_a_length_is_refused(self):
        # zero would put every chord at 0 mm, and a negative one below it, with the scale called known
        for bad in (0, -0.2, "abc", float("nan")):
            p = self.write("bad.json", annotation("ap", [body("L3", 0, 0, 230, 100)], pixel_mm=bad))
            with self.assertRaises(SystemExit) as e:
                R.ingest([p], "f1", "t", "human")
            self.assertIn("positive length", str(e.exception))
        p = self.write("str.json", annotation("ap", [body("L3", 0, 0, 230, 100)], pixel_mm="0.2"))
        self.assertAlmostEqual(R.ingest([p], "f1", "t", "human").bodies[0].values["endplate"], 230 * 0.2 / R.M0)

    def test_an_unstated_modality_is_read_as_film(self):
        for said, read in ((None, "film"), ("", "film"), ("  ", "film"), (" DRR ", "DRR"), ("film", "film")):
            doc = annotation("ap", [body("L3", 0, 0, 230, 100)])
            doc["image"]["modality"] = said
            self.assertEqual(R.ingest([self.write("m.json", doc)], "f1", "t", "human").study["modality"], read, said)
        doc = annotation("ap", [body("L3", 0, 0, 230, 100)])
        del doc["image"]["modality"]
        self.assertEqual(R.ingest([self.write("m.json", doc)], "f1", "t", "human").study["modality"], "film")

    def test_refusals(self):
        a = self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)]))
        b = self.write("b.json", annotation("lateral", [body("L3", 0, 0, 230, 100)], pixel_mm=None))
        with self.assertRaises(SystemExit):
            R.ingest([a, b], "f1", "t", "human")
        with self.assertRaises(SystemExit):
            R.ingest([a, a], "f1", "t", "human")
        bad = self.write("c.json", {"format": "other"})
        with self.assertRaises(SystemExit):
            R.ingest([bad], "f1", "t", "human")

    def test_unnamed_bodies_and_model_readers(self):
        doc = annotation("ap", [body("?", 0, 0, 230, 100), body("L9", 0, 200, 230, 100)], reader="model:run7")
        col = R.ingest([self.write("a.json", doc)], "f1", "t", "machine")
        self.assertEqual(col.levels, ["?", "?"])
        self.assertEqual(col.study["annotation"], "machine")
        self.assertTrue(col.study["problems"])
        with self.assertRaises(SystemExit):             # a model's reader id beside a claim of human
            R.ingest([self.write("b.json", doc)], "f1", "t", "human")
        with self.assertRaises(SystemExit):             # who drew it is never inferred
            R.ingest([self.write("c.json", doc)], "f1", "t", None)

    def test_the_posterior_side_is_read_on_a_wedge(self):
        # a wedge: the left wall 150 pixels, the right wall 120, so h_post depends on the side
        wedge = {"level": "L1", "corners": [[0, 0], [200, 15], [200, 135], [0, 150]], "visible": [True] * 4}
        left = R.ingest([self.write("l.json", annotation("lateral", [wedge], anterior="left"))], "f1", "t", "human")
        right = R.ingest([self.write("r.json", annotation("lateral", [wedge], anterior="right"))], "f1", "t", "human")
        self.assertAlmostEqual(left.bodies[0].values["h_post"], 120 * 0.2 / R.M0)    # anterior left: right wall
        self.assertAlmostEqual(right.bodies[0].values["h_post"], 150 * 0.2 / R.M0)   # anterior right: left wall

    def test_c2_and_the_sacrum_are_named_not_measured(self):
        doc = annotation("ap", [body("L5", 0, 400, 230, 100), body("sacrum", 0, 520, 260, 120), body("C2", 0, 0, 90, 60)])
        col = R.ingest([self.write("a.json", doc)], "f1", "t", "human")
        self.assertEqual(col.levels, ["C2", "L5", "sacrum"])
        for b in (col.bodies[0], col.bodies[2]):
            self.assertFalse(any(math.isfinite(v) for v in b.values.values()))
            self.assertIn("not measured", b.flags["all"])

    def test_two_unscaled_views_are_refused(self):
        a = self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)], pixel_mm=None))
        b = self.write("b.json", annotation("lateral", [body("L3", 0, 0, 200, 100)], pixel_mm=None))
        with self.assertRaises(SystemExit):
            R.ingest([a, b], "f1", "t", "human")

    def test_unnamed_bodies_keep_their_place_on_the_view(self):
        doc = annotation("ap", [body("L2", 0, 400, 230, 100), body("?", 0, 100, 220, 100), body("L1", 0, 250, 225, 100)])
        listed, problems = R.view_bodies(doc, "ap")
        self.assertEqual([lv for lv, _ in listed], ["?", "L1", "L2"])       # top down by the corners' rows
        self.assertEqual(problems, [])

    def test_a_level_named_twice_on_a_view_is_kept_as_unnamed(self):
        doc = annotation("ap", [body("L3", 0, 0, 200, 100), body("L3", 0, 200, 260, 100)])
        col = R.ingest([self.write("a.json", doc)], "f1", "t", "human")
        self.assertEqual(col.levels, ["?", "?"])
        self.assertTrue(any("named 2 times" in p for p in col.study["problems"]))


if __name__ == "__main__":
    unittest.main()
