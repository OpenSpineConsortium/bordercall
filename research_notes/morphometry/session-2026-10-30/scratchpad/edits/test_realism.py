import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def sub(old, new, count=1):
    global src
    if src.count(old) != count:
        raise SystemExit("expected %d of %r, found %d" % (count, old[:70], src.count(old)))
    src = src.replace(old, new)

sub('''    def test_the_record_holds_every_orientation(self):''', '''    def test_the_camera_is_the_release_the_record_was_made_with(self):
        self.assertEqual(PJ.CHECKED, {k: RECORD["versions"][k] for k in ("flexray", "nanodrr")})

    def test_the_record_holds_every_orientation(self):''')
sub('''    def test_the_canvas_gives_the_place_back(self):''', '''    def test_the_commands_canvas_is_flexrays_default(self):
        # the canvas project places every end on unless told otherwise, square and padded to a
        # square as to_canvas takes it
        self.assertEqual(RECORD["canvas"]["image_size"], [PJ.CANVAS, PJ.CANVAS])
        self.assertTrue(RECORD["canvas"]["pad_to_square"])

    def test_the_canvas_gives_the_place_back(self):''')
sub('''            self.assertEqual(rec["labels"]["sha256"], sha256(self.mask))
            here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))''', '''            self.assertEqual(rec["labels"]["sha256"], sha256(self.mask))
            self.assertEqual(rec["canvas"], RECORD["canvas"]["image_size"][0])
            self.assertEqual(rec["flexray"], {"render": "not recorded", "camera": PJ.CHECKED})
            self.assertIsNone(rec["edits"])
            here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))''')
sub('''        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            MV.main(["project", "--lines", self.lines, "--manifest", manifest, "--out", out])
''', '''        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
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
''')
sub('''def manifest_of(tmp: str, name: str, view: PJ.View, crop: Optional[dict], subject: str,
                ray_samples: int) -> Tuple[str, str]:
    """A render manifest of SchwingNet's kind holding one view on a square detector, and the
    view's file as it names it."""''', '''def manifest_of(tmp: str, name: str, view: PJ.View, crop: Optional[dict], subject: str,
                ray_samples: int, flexray: Optional[str] = None) -> Tuple[str, str]:
    """A render manifest of SchwingNet's kind holding one view on a square detector, and the
    view's file as it names it; FleXray's release where one is given."""''')
sub('''    with open(path, "w", encoding="ascii") as fh:
        json.dump({"blocks": {"detector": view.width, "ray_samples": ray_samples}, "views": [row]}, fh)
    return path, row["file"]''', '''    doc = {"blocks": {"detector": view.width, "ray_samples": ray_samples}, "views": [row]}
    if flexray is not None:
        doc["flexray"] = flexray
    with open(path, "w", encoding="ascii") as fh:
        json.dump(doc, fh)
    return path, row["file"]''')
sub('''def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()
''', '''class Realism(unittest.TestCase):
    """A render of SchwingNet's realism programme, the image its fluoroscopic edit converts, read
    from its own records as tools/realism.py's render_one writes them: the sample's last row of
    manifest.jsonl for the pose and the pixels, recipe.json for the distance and the spacing, and
    the CT the row names by its sha256 for the isocentre, its volume's centre; with its edits'
    files and the filter's verdicts beside it."""

    SAMPLE, POSE = "s0001_p017", {"alpha": 90, "y": 900, "z": -100}

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
                fh.write(json.dumps({"sample_id": sample, "arm": arm, "seed": 100 + arm, "seconds": 1.0}) + "\\n")
            fh.write('{"sample_id": "%s", "arm"' % cls.SAMPLE)
        for arm, side in ((0, 256), (1, 256), (2, 128)):
            np.save(os.path.join(cls.edits, "edited", "%s__a%d.npy" % (cls.SAMPLE, arm)), np.zeros((side, side), np.float16))
        for name, arm in (("filter_kept.csv", 0), ("filter_dropped.csv", 1)):
            with open(os.path.join(cls.filter, name), "w", encoding="ascii") as fh:
                fh.write("sample_id,subject_id,pose_id\\n%s__a%d,0001,17\\n" % (cls.SAMPLE, arm))

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
                                         seconds=1.0, **digests), sort_keys=True) + "\\n")
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
        # through nanoDRR's AP turn, about the CT's volume centre, (shape - 1) / 2 in voxels
        got, rec, _ = self.project(self.folder, "--ct", self.ct)
        centre = self.aff @ np.array([(s - 1) / 2.0 for s in self.lab.shape] + [1.0])
        want = PJ.View(rot_deg=(90.0, 0.0, 0.0), xyz_mm=(0.0, 900.0, -100.0), isocentre_mm=tuple(centre[:3]), sdd=1250.0,
                       delx=0.6, height=256, width=256, orientation="AP")
        self.assertEqual(PJ.View(**rec["view"]), want)
        cam = PJ.Camera(want)
        for row, line in zip(self.rows, got):
            self.assertEqual([float(line["au"]), float(line["av"])], cam.project(point(row, "a")).uv[0].tolist())
        self.assertGreater(sum(line["a_in_beam"] == "True" for line in got), len(got) // 2)
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
''')
open(path, "w", encoding="ascii", newline="\n").write(src)
print("ok")
