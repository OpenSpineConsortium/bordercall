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
        col = R.ingest([ap, lat], "f1", "test", magnification=1.25)
        self.assertEqual(col.levels, ["L1", "L2"])
        l1, l2 = col.bodies
        self.assertAlmostEqual(l2.values["endplate"], 250 * 0.2 / 1.25)
        self.assertAlmostEqual(l2.values["canal_w"], 125 * 0.2 / 1.25)
        self.assertAlmostEqual(l1.values["endplate_depth"], 200 * 0.2 / 1.25)
        self.assertAlmostEqual(l1.values["h_post"], 175 * 0.2 / 1.25)
        self.assertEqual(col.study["views"], ["ap", "lateral"])
        self.assertTrue(col.study["scale_known"])
        self.assertAlmostEqual(col.study["scale_log_sd"], 0.02)

    def test_the_default_magnification_is_recorded(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)]))], "f1", "t")
        self.assertAlmostEqual(col.bodies[0].values["endplate"], 230 * 0.2 / R.M0)
        self.assertEqual(col.study["magnification"], R.M0)
        self.assertEqual(col.study["scale_log_sd"], R.M_LOG_SD)

    def test_no_side_no_posterior_height(self):
        col = R.ingest([self.write("l.json", annotation("lateral", [body("L3", 0, 0, 200, 150)]))], "f1", "t")
        self.assertTrue(math.isnan(col.bodies[0].values["h_post"]))
        self.assertIn("anterior", col.bodies[0].flags["h_post"])
        right = R.ingest([self.write("r.json", annotation("lateral", [body("L3", 0, 0, 200, 150)]))], "f1", "t",
                         anterior="right")
        self.assertAlmostEqual(right.bodies[0].values["h_post"], 150 * 0.2 / R.M0)

    def test_a_hidden_corner_gives_no_chord(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100, (True, False, True, True))]))],
                       "f1", "t")
        self.assertTrue(math.isnan(col.bodies[0].values["endplate"]))
        self.assertFalse(math.isnan(col.bodies[0].values["endplate_lower"]))

    def test_no_pixel_size_leaves_pixels_and_an_unknown_scale(self):
        col = R.ingest([self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)], pixel_mm=None))], "f1", "t")
        self.assertEqual(col.bodies[0].values["endplate"], 230.0)
        self.assertFalse(col.study["scale_known"])
        self.assertIsNone(col.study["scale_log_sd"])

    def test_refusals(self):
        a = self.write("a.json", annotation("ap", [body("L3", 0, 0, 230, 100)]))
        b = self.write("b.json", annotation("lateral", [body("L3", 0, 0, 230, 100)], pixel_mm=None))
        with self.assertRaises(SystemExit):
            R.ingest([a, b], "f1", "t")
        with self.assertRaises(SystemExit):
            R.ingest([a, a], "f1", "t")
        bad = self.write("c.json", {"format": "other"})
        with self.assertRaises(SystemExit):
            R.ingest([bad], "f1", "t")

    def test_unnamed_bodies_and_model_readers(self):
        doc = annotation("ap", [body("?", 0, 0, 230, 100), body("L9", 0, 200, 230, 100)], reader="model:run7")
        col = R.ingest([self.write("a.json", doc)], "f1", "t")
        self.assertEqual(col.levels, ["?", "?"])
        self.assertEqual(col.study["annotation"], "machine")
        self.assertTrue(col.study["problems"])


if __name__ == "__main__":
    unittest.main()
