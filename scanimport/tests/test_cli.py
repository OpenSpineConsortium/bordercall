"""The command line end to end: a CT's labels and a film's corners in, every file out, every input
that changes a column hashed, a counted synthetic study scored."""
import contextlib
import csv
import io
import json
import os
import tempfile
import unittest

import numpy as np

from scanimport import RULE_LEVELS, SEVEN, schemes
from scanimport.__main__ import main
from scanimport.column import Body, Column, facts_from_levels, write_column
from scanimport.tests import phantom as PH
from scanimport.tests.test_radiograph import annotation, body
import exact as EX
import panjabi as P


def run(argv):
    out = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out):
        try:
            main(argv)
        except SystemExit as e:
            code = e.code or 0
    return code, out.getvalue()


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def p(self, *a):
        return os.path.join(self.d, *a)

    def test_ct_and_film_of_one_person(self):
        levels = ["T12", "L1", "L2"]
        lab, aff, _, _ = PH.column(levels, {lv: v for v, lv in schemes.VERSE.items() if lv in levels}, margin=12.0,
                                   spacing=(1.2, 1.2, 1.8))
        PH.save(self.p("seg.nii.gz"), lab, aff)
        code, text = run(["ingest-ct", "--labels", self.p("seg.nii.gz"), "--scheme", "verse", "--study", "ct1",
                          "--subject", "p1", "--source", "phantom", "--annotation", "human", "--out", self.p("imp")])
        self.assertEqual(code, 0, text)
        self.assertIn("3 bodies (T12 L1 L2)", text)
        with open(self.p("fx.json"), "w") as fh:
            json.dump(annotation("ap", [body("L1", 0, 0, 230, 100), body("L2", 0, 120, 240, 100)]), fh)
        code, text = run(["ingest-xr", "--xr", self.p("fx.json"), "--study", "xr1", "--subject", "p1",
                          "--source", "phantom", "--annotation", "human", "--out", self.p("imp")])
        self.assertEqual(code, 0, text)
        for f in ("columns/ct1.json", "columns/xr1.json", "fields/ct1.csv", "bodies.csv", "studies.csv",
                  "tiers.csv", "MANIFEST.json"):
            self.assertTrue(os.path.exists(self.p("imp", f)), f)
        with open(self.p("imp", "tiers.csv")) as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tier_as_pair"], "silver 1")
        with open(self.p("imp", "MANIFEST.json")) as fh:
            man = json.load(fh)
        self.assertEqual(man["studies"], 2)
        self.assertEqual(len(man["runs"]), 2)
        self.assertEqual(run(["check", self.p("imp")])[0], 0)
        code, text = run(["compare", self.p("imp"), "--all", "--out", self.p("cmp")])
        self.assertEqual(code, 0, text)
        with open(self.p("cmp", "compare.csv")) as fh:
            self.assertEqual(fh.readline().strip(), "# bodies every_named_body")
            cmp = {(r["measure"], r["level"]): r for r in csv.DictReader(fh)}
        self.assertEqual(cmp[("endplate", "L1")]["bodies"], "2")
        code, text = run(["name", self.p("imp", "fields", "ct1.csv")])
        self.assertEqual(code, 0, text)
        self.assertIn("named", text)

    def test_check_fails_on_a_recorded_problem(self):
        with open(self.p("bad.json"), "w") as fh:
            json.dump(annotation("ap", [body("L9", 0, 0, 230, 100), body("L1", 0, 200, 230, 100)]), fh)
        code, text = run(["ingest-xr", "--xr", self.p("bad.json"), "--study", "b1", "--source", "t",
                          "--annotation", "human", "--out", self.p("badimp")])
        self.assertEqual(code, 0, text)
        code, text = run(["check", self.p("badimp")])
        self.assertEqual(code, 1, text)
        self.assertIn("problem:", text)

    def test_a_picture_whose_annotation_gives_the_scale_passes_check(self):
        from PIL import Image
        from scanimport.readers import sha256_of
        Image.fromarray(np.zeros((300, 200), np.uint8)).save(self.p("ap.png"))
        doc = annotation("ap", [body("L1", 20, 20, 120, 60), body("L2", 20, 120, 125, 60)])
        doc["image"].update({"sha256": sha256_of(self.p("ap.png")), "width": 200, "height": 300})
        with open(self.p("ap.json"), "w") as fh:
            json.dump(doc, fh)
        code, text = run(["ingest-image", "--image", self.p("ap.png"), "--corners", self.p("ap.json"), "--study", "f1",
                          "--source", "t", "--annotation", "human", "--out", self.p("pic")])
        self.assertEqual(code, 0, text)
        code, text = run(["check", self.p("pic")])
        self.assertEqual(code, 0, text)

    def test_a_nifti_sidecar_is_hashed_with_the_volume(self):
        import nibabel as nib
        hu = np.full((40, 40, 12), 40.0, np.float32)
        hu[:3] = -1000.0
        nib.save(nib.Nifti1Image(hu, np.eye(4)), self.p("ct.nii.gz"))
        with open(self.p("ct.json"), "w") as fh:
            json.dump({"PatientSex": "F"}, fh)
        code, text = run(["ingest-raw-ct", "--volume", self.p("ct.nii.gz"), "--study", "r1", "--source", "t",
                          "--out", self.p("raw")])
        self.assertEqual(code, 0, text)
        with open(self.p("raw", "columns", "r1.json")) as fh:
            self.assertEqual(json.load(fh)["study"]["covariates"]["sex"]["value"], "F")
        with open(self.p("raw", "MANIFEST.json")) as fh:
            inputs = json.load(fh)["runs"][-1]["inputs"]
        from scanimport.readers import sha256_of
        self.assertEqual(inputs, {self.p("ct.nii.gz"): sha256_of(self.p("ct.nii.gz")),
                                  self.p("ct.json"): sha256_of(self.p("ct.json"))})

    def test_a_dicom_folder_is_hashed_by_every_file_under_it_and_the_run_records_its_versions(self):
        import hashlib
        from scanimport import column as C
        from scanimport.tests import dicom_files as DF
        hu = np.full((40, 40, 12), 40.0, np.float32)
        hu[:3] = -1000.0
        folder = self.p("series")
        DF.write_ct_series(folder, hu, np.eye(4))
        code, text = run(["ingest-raw-ct", "--volume", folder, "--study", "r2", "--source", "t", "--out", self.p("rawd")])
        self.assertEqual(code, 0, text)
        with open(self.p("rawd", "MANIFEST.json")) as fh:
            manifest = json.load(fh)
        files = sorted(os.listdir(folder))
        self.assertEqual(manifest["runs"][-1]["inputs"], {"%s/ (%d files)" % (folder, len(files)): C.sha256_of(folder)})
        self.assertEqual(manifest["digests"], C.DIGESTS)
        lines = "".join("%s %s\n" % (f, C.file_sha256(os.path.join(folder, f))) for f in files)
        self.assertEqual(C.sha256_of(folder), hashlib.sha256(lines.encode()).hexdigest())
        versions = manifest["runs"][-1]["versions"]
        self.assertTrue({"python", "numpy", "scipy", "pydicom"} <= set(versions), versions)
        # one byte of one slice, or a file added in a subfolder, gives the folder another digest
        before = C.sha256_of(folder)
        with open(os.path.join(folder, files[0]), "r+b") as fh:
            fh.seek(-1, os.SEEK_END)
            last = fh.read(1)
            fh.seek(-1, os.SEEK_END)
            fh.write(bytes([last[0] ^ 1]))
        changed = C.sha256_of(folder)
        self.assertNotEqual(changed, before)
        os.makedirs(os.path.join(folder, "more"))
        with open(os.path.join(folder, "more", "note.txt"), "w") as fh:
            fh.write("x")
        self.assertNotEqual(C.sha256_of(folder), changed)
        self.assertEqual(list(C.digests(folder)), ["%s/ (%d files)" % (folder, len(files) + 1)])

    def test_the_command_line_hashes_the_sidecar_the_reader_reads(self):
        from scanimport.__main__ import nifti_sidecar
        from scanimport.readers import sidecar_path
        for name in ("ct.nii.gz", "ct.nii", "CT.NII.GZ"):
            path = self.p(name)
            open(path, "wb").close()
            self.assertIsNone(nifti_sidecar(path), name)
            with open(sidecar_path(path), "w") as fh:
                json.dump({"PatientSex": "F"}, fh)
            self.assertEqual(nifti_sidecar(path), sidecar_path(path), name)
            os.remove(sidecar_path(path))
        self.assertIsNone(nifti_sidecar(self.d))

    def test_score_a_counted_study(self):
        ref = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
        rng = np.random.default_rng(3)
        V = EX.column_values([P.synthesize(ref, "typical", rng, measures=SEVEN)], SEVEN)[0]
        levels = ["C1", "C2"] + RULE_LEVELS + ["sacrum"]
        bodies = [Body(lv) for lv in levels]
        for j in range(len(RULE_LEVELS)):
            bodies[j + 2].values = {m: float(V[i, j]) for i, m in enumerate(SEVEN)}
        study = {"study_id": "syn1", "subject_id": "syn1", "source": "panjabi", "modality": "synthetic",
                 "annotation": "machine", "scale_log_mean": 0.0, "scale_log_sd": 0.0}
        study.update(facts_from_levels(levels, {"L6": True, "T13": True}))
        write_column(Column(study, bodies), self.p("syn"))
        code, text = run(["score", self.p("syn"), "--n", "1", "9", "--out", self.p("scores")])
        self.assertEqual(code, 0, text)
        self.assertIn("typical n=9", text)
        with open(self.p("scores", "scores.json")) as fh:
            res = json.load(fh)
        self.assertEqual({s["n"] for s in res["summary"]}, {1, 9})
        with open(self.p("scores", "RUNS.json")) as fh:
            self.assertEqual(json.load(fh)["runs"][0]["command"][3], "score")
        code, text = run(["name", self.p("syn", "fields", "syn1.csv"), "--json"])
        out = json.loads(text)
        self.assertEqual(out["bodies"], 22)
        self.assertEqual(out["names"][0], "C3")


if __name__ == "__main__":
    unittest.main()
