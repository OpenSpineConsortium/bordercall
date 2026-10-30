import sys
path, ppath = sys.argv[1], sys.argv[2]
src = open(path, encoding="ascii").read()
psrc = open(ppath, encoding="ascii").read()

def sub(old, new, count=1, which="main"):
    global src, psrc
    text = src if which == "main" else psrc
    if text.count(old) != count:
        raise SystemExit("expected %d of %r in %s, found %d" % (count, old[:70], which, text.count(old)))
    text = text.replace(old, new)
    if which == "main":
        src = text
    else:
        psrc = text

# ---- projection.py: the releases the camera was checked against, and the canvas's words
sub('''CANVAS = 256                    # the side of FleXray's inference canvas, in pixels
''', '''CANVAS = 256                    # the side of FleXray's inference canvas, in pixels
# the releases whose camera this module copies and whose renders tests/fixtures/flexray.json holds
CHECKED = {"flexray": "1.0.2", "nanodrr": "0.1.5"}
''', which="proj")
sub('''FleXray's segmentation reads an image on a canvas of 256 pixels, the image padded to a square at
its centre and resized (fxr/inference/preprocessing.py, ImagePreprocessing.content_box and
_pad_to_square; scanimport.film, CANVAS); to_canvas and from_canvas carry a point between the
render and that canvas.
''', '''FleXray's segmentation reads an image on the canvas its model's preprocessing.json names, at
FleXray's defaults, which its training renders keep, a square of 256 pixels, the image padded to a
square at its centre and resized (fxr/inference/preprocessing.py, ImagePreprocessing.from_metadata,
content_box and _pad_to_square; scanimport.film, CANVAS); to_canvas and from_canvas carry a point
between the render and a square canvas so padded, of any side.
''', which="proj")

# ---- __main__.py
sub('''GRID_MM = 1e-3                  # how far two affines' entries may differ for one grid, in mm
''', '''GRID_MM = 1e-3                  # how far two affines' entries may differ for one grid, in mm
ARM_MARK = "__a"                # an edit's name is its sample's, this and its arm (tools/realism.py, edit_name)
''')
sub('''def view_from(a) -> Tuple[PJ.View, Optional[PJ.Crop], dict, int]:
    """The view to project onto, the crop of the CT it rendered (none where the record names none:
    the whole CT), the record of where it was read, and the samples a ray the render took: a view
    file of View's fields and a crop, or a row of SchwingNet's render manifest named by its image
    file, its crop, and the detector and the ray samples its blocks record."""
    if a.view:
        doc = read_json(a.view)
        view = PJ.View(**{k: doc[k] for k in VIEW_FIELDS if k in doc})
        source = {"view": os.path.basename(a.view), "sha256": sha256_of(a.view)}
        return view, PJ.Crop.from_record(doc.get("crop")), source, int(doc.get("n_samples", a.samples))
    manifest = read_json(a.manifest)
    row = next((r for r in manifest.get("views", []) if r.get("file") == a.file), None)
    if row is None:
        raise SystemExit("%s holds no view of the file %s" % (a.manifest, a.file))
    blocks = manifest.get("blocks", {})
    view = PJ.View.from_manifest(row, int(blocks["detector"]))
    source = {"manifest": os.path.basename(a.manifest), "sha256": sha256_of(a.manifest), "file": a.file,
              "subject": row.get("subject"), "blocks": blocks}
    return view, PJ.Crop.from_record(row.get("crop")), source, int(blocks.get("ray_samples", a.samples))
''', '''def view_from(a) -> Tuple[PJ.View, Optional[PJ.Crop], dict, int]:
    """The view to project onto, the crop of the CT it rendered (none where the record names none:
    the whole CT), the record of where it was read, and the samples a ray the render took: a view
    file of View's fields and a crop; a row of SchwingNet's render manifest named by its image
    file, its crop, and the detector and the ray samples its blocks record; or a render of the
    realism programme (realism_view)."""
    if a.realism:
        return realism_view(a)
    if a.view:
        doc = read_json(a.view)
        view = PJ.View(**{k: doc[k] for k in VIEW_FIELDS if k in doc})
        source = {"view": os.path.basename(a.view), "sha256": sha256_of(a.view), "flexray": doc.get("flexray")}
        return view, PJ.Crop.from_record(doc.get("crop")), source, int(doc.get("n_samples", a.samples))
    manifest = read_json(a.manifest)
    row = next((r for r in manifest.get("views", []) if r.get("file") == a.file), None)
    if row is None:
        raise SystemExit("%s holds no view of the file %s" % (a.manifest, a.file))
    blocks = manifest.get("blocks", {})
    view = PJ.View.from_manifest(row, int(blocks["detector"]))
    source = {"manifest": os.path.basename(a.manifest), "sha256": sha256_of(a.manifest), "file": a.file,
              "subject": row.get("subject"), "blocks": blocks, "flexray": manifest.get("flexray")}
    return view, PJ.Crop.from_record(row.get("crop")), source, int(blocks.get("ray_samples", a.samples))


def json_rows(path: str) -> List[dict]:
    """The rows of a JSON-lines log, a line a cut tore off passed over, as the realism programme
    reads its own (tools/realism.py, json_lines)."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def realism_view(a) -> Tuple[PJ.View, Optional[PJ.Crop], dict, int]:
    """A render of SchwingNet's realism programme, the image its fluoroscopic edit converts, which
    names no camera (tools/realism.py, render_one): the sample's row of the render's manifest.jsonl,
    the last written for it, gives the pose, alpha about the first axis and the source at (0, y, z)
    from the isocentre through nanoDRR's AP turn, and the detector's pixels; recipe.json the
    source-to-detector distance and the pixel spacing; and the CT given with --ct, which must be
    the one the row's sha256 names, the isocentre, the volume's centre (volume_centre_mm). It
    renders the whole CT, so no crop."""
    if not a.ct:
        raise SystemExit("a realism render is centred on its CT, so --realism takes --ct, the CT it was rendered from")
    recipe = read_json(os.path.join(a.realism, "recipe.json"))
    log = os.path.join(a.realism, "manifest.jsonl")
    row = next((r for r in reversed(json_rows(log)) if r.get("sample_id") == a.sample), None)
    if row is None:
        raise SystemExit("%s holds no render of the sample %s" % (log, a.sample))
    if recipe.get("isocentre", "volume-centre") != "volume-centre":
        raise SystemExit("%s centres its renders on %r, not the CT's volume centre" % (a.realism, recipe["isocentre"]))
    digest = sha256_of(a.ct)
    if digest != row.get("ct_sha256"):
        raise SystemExit("%s is not the CT the sample %s was rendered from: its sha256 is not the row's" % (a.ct, a.sample))
    affine, shape = ct_header(a.ct)
    centre = affine @ np.array([(s - 1) / 2.0 for s in shape] + [1.0])
    pixels = int(row.get("pixels", recipe["render_pixels"]))
    raw = os.path.join(a.realism, "raw", "%s.npy" % a.sample)
    if os.path.exists(raw) and tuple(np.load(raw, mmap_mode="r").shape) != (pixels, pixels):
        raise SystemExit("%s is not %d pixels square, as the row says the sample was rendered" % (raw, pixels))
    view = PJ.View(rot_deg=(float(row["alpha"]), 0.0, 0.0), xyz_mm=(0.0, float(row["y"]), float(row["z"])),
                   isocentre_mm=tuple(centre[:3]), sdd=float(recipe["render_sdd_mm"]),
                   delx=float(recipe["render_spacing_mm"]), height=pixels, width=pixels, orientation="AP")
    source = {"realism": os.path.basename(os.path.normpath(a.realism)), "sha256": sha256_of(log),
              "recipe_sha256": sha256_of(os.path.join(a.realism, "recipe.json")), "sample": a.sample,
              "file": "raw/%s.npy" % a.sample, "subject": row.get("subject_id"), "ct_sha256": digest,
              "isocentre": "the CT's volume centre", "truth_sha256": row.get("truth_sha256") or {},
              "flexray": None}
    return view, None, source, a.samples


def edits_of(a, source: dict, view: PJ.View) -> Optional[List[dict]]:
    """The fluoroscopic edits of a realism render, where the edit run's folder is given
    (tools/realism.py, run_edit: edits.jsonl and edited/<sample>__a<arm>.npy): each arm's file, its
    seed, whether it holds the render's pixels, which the edit keeps (the lines' places on the
    render are then theirs on the edit), and, where the filter's folder is given (run_filter or
    run_keep: filter_kept.csv and filter_dropped.csv), whether FluXray's paired filter kept it."""
    if not a.edits:
        return None
    if "sample" not in source:
        raise SystemExit("--edits names a realism render's edits, so it takes --realism and --sample")
    sample = source["sample"]
    arms = {}
    for row in json_rows(os.path.join(a.edits, "edits.jsonl")):
        if row.get("sample_id") == sample and "arm" in row:
            arms[int(row["arm"])] = row
    verdict = {}
    for name, word in (("filter_kept.csv", "kept"), ("filter_dropped.csv", "dropped")) if a.filter else ():
        for r in read_table(os.path.join(a.filter, name), None, column="sample_id"):
            verdict[r["sample_id"]] = word
    out = []
    for arm in sorted(arms):
        name = "%s%s%d" % (sample, ARM_MARK, arm)
        path = os.path.join(a.edits, "edited", name + ".npy")
        held = tuple(np.load(path, mmap_mode="r").shape) == (view.height, view.width) if os.path.exists(path) else None
        out.append({"file": "edited/%s.npy" % name, "arm": arm, "seed": arms[arm].get("seed"),
                    "pixels_kept": "missing" if held is None else held,
                    "filter": verdict.get(name, "not scored") if a.filter else "not given"})
    return out


def flexray_check(source: dict) -> dict:
    """Which FleXray made the render, as its record names it, beside the release whose camera this
    is: a render of another is projected all the same, with a warning, since nothing here has held
    this camera to that release's renders."""
    made = source.get("flexray")
    if made and made != PJ.CHECKED["flexray"]:
        print("warning: the render was made by FleXray %s and this camera is FleXray %s's; run "
              "morphoview.tests.test_projection where FleXray %s is installed before trusting a pixel"
              % (made, PJ.CHECKED["flexray"], made), file=sys.stderr)
    return {"render": made or "not recorded", "camera": dict(PJ.CHECKED)}
''')
sub('''def ct_grid(a, mask) -> Optional[Tuple[np.ndarray, Tuple[int, int, int], str]]:
    """The grid of the CT the render was made from, its affine and shape, and where it was read:
    the header of --ct, which the mask must share, or else the mask's own, since SchwingNet puts a
    rendered subject's masks on its CT's grid; none where neither is given."""
    if a.ct:
        import nibabel as nib
        img = nib.load(a.ct)
        affine, shape = np.asarray(img.affine, float), tuple(int(n) for n in img.shape[:3])
        if mask is not None:''', '''def ct_header(path: str) -> Tuple[np.ndarray, Tuple[int, int, int]]:
    """A CT's affine and its shape, any trailing axes of one voxel dropped, as SchwingNet's renders
    read a CT (tools/realism.py, load_subject)."""
    import nibabel as nib
    img = nib.load(path)
    shape = tuple(int(n) for n in img.shape)
    while len(shape) > 3 and shape[-1] == 1:
        shape = shape[:-1]
    if len(shape) != 3:
        raise SystemExit("%s is not a three-dimensional CT" % path)
    return np.asarray(img.affine, float), shape


def ct_grid(a, mask) -> Optional[Tuple[np.ndarray, Tuple[int, int, int], str]]:
    """The grid of the CT the render was made from, its affine and shape, and where it was read:
    the header of --ct, which the mask must share, or else the mask's own, since SchwingNet puts a
    rendered subject's masks on its CT's grid; none where neither is given."""
    if a.ct:
        affine, shape = ct_header(a.ct)
        if mask is not None:''')
sub('''def read_table(path: str, study: Optional[str]) -> List[dict]:
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if not study or r["study"] == study]
''', '''def read_table(path: str, study: Optional[str], column: str = "study") -> List[dict]:
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if not study or r[column] == study]
''')
sub('''    projected it."""
    view, crop, source, n_samples = view_from(a)
    cam = PJ.Camera(view)
''', '''    projected it, the FleXray that made the render and, for a realism render, its fluoroscopic
    edits."""
    view, crop, source, n_samples = view_from(a)
    cam = PJ.Camera(view)
    made_by = flexray_check(source)
    edits = edits_of(a, source, view)
''')
sub('''    record = {"view": view.as_record(), "crop": crop.as_record() if crop else None, "from": source,
              "n_samples": n_samples, "canvas": a.canvas, "to_world": cam.to_world.tolist(),
              "intrinsics": cam.intrinsics.tolist(),
              "lines": {"file": os.path.basename(a.lines), "sha256": sha256_of(a.lines), "study": study,
                        "chosen_by": chosen},
              "labels": {"file": os.path.basename(a.labels), "sha256": sha256_of(a.labels), "scheme": a.scheme}
              if a.labels else None,''', '''    record = {"view": view.as_record(), "crop": crop.as_record() if crop else None, "from": source,
              "flexray": made_by, "n_samples": n_samples, "canvas": a.canvas, "to_world": cam.to_world.tolist(),
              "intrinsics": cam.intrinsics.tolist(),
              "lines": {"file": os.path.basename(a.lines), "sha256": sha256_of(a.lines), "study": study,
                        "chosen_by": chosen},
              "labels": labels_record(a, source) if a.labels else None, "edits": edits,''')
sub('''    print(summary(a.out, study, out, grid is not None, shade is not None))


def summary(out_dir: str, study: str, out: List[dict], placed: bool, shaded: bool) -> str:
    """One line of what was carried: a line is on the render where both its ends are in the beam
    and in what the render was made of, as far as the CT's grid tells."""''', '''    print(summary(a.out, study, out, grid is not None, shade is not None, edits))


def labels_record(a, source: dict) -> dict:
    """The labels the lines were measured on, by sha256, and for a realism render the truth folder
    whose file the render's row names by the same sha256, if any: the labels it rendered."""
    digest = sha256_of(a.labels)
    out = {"file": os.path.basename(a.labels), "sha256": digest, "scheme": a.scheme}
    if "truth_sha256" in source:
        out["rendered_as"] = next((f for f, d in sorted(source["truth_sha256"].items()) if d == digest), None)
    return out


def summary(out_dir: str, study: str, out: List[dict], placed: bool, shaded: bool,
            edits: Optional[List[dict]] = None) -> str:
    """One line of what was carried: a line is on the render where both its ends are in the beam
    and in what the render was made of, as far as the CT's grid tells; and how many of the render's
    fluoroscopic edits hold its pixels, and were kept by the filter."""''')
sub('''        said += ", %d with both ends on their level's shadow" % on
    return said
''', '''        said += ", %d with both ends on their level's shadow" % on
    if edits is not None:
        said += "; %d edits, %d holding the render's pixels, %d kept by the filter" % (
            len(edits), sum(e["pixels_kept"] is True for e in edits), sum(e["filter"] == "kept" for e in edits))
    return said
''')
sub('''    where.add_argument("--manifest", default="", help="SchwingNet's render manifest.json, with --file")
''', '''    where.add_argument("--manifest", default="", help="SchwingNet's render manifest.json, with --file")
    where.add_argument("--realism", default="", help="a render folder of SchwingNet's realism programme "
                       "(manifest.jsonl, recipe.json, raw/), with --sample and --ct")
''')
sub('''    q.add_argument("--file", default="", help="the render's file as the manifest names it, images/<stem>_v<NN>.png")
''', '''    q.add_argument("--file", default="", help="the render's file as the manifest names it, images/<stem>_v<NN>.png")
    q.add_argument("--sample", default="", help="the realism render's sample_id")
    q.add_argument("--edits", default="", help="the realism edit run's folder (edits.jsonl, edited/), whose edits "
                   "of the sample to list")
    q.add_argument("--filter", default="", help="the realism filter's folder (filter_kept.csv, filter_dropped.csv)")
''')
sub('''    q.add_argument("--canvas", type=int, default=PJ.CANVAS, help="the side of FleXray's inference canvas")
''', '''    q.add_argument("--canvas", type=int, default=PJ.CANVAS, help="the side of FleXray's inference canvas, square and "
                   "padded to a square, as the model's preprocessing.json names it (256 at FleXray's defaults)")
''')
sub('''    if a.cmd == "project" and a.manifest and not a.file:
        p.error("--manifest takes --file, the render's file as the manifest names it")
''', '''    if a.cmd == "project" and a.manifest and not a.file:
        p.error("--manifest takes --file, the render's file as the manifest names it")
    if a.cmd == "project" and a.realism and not a.sample:
        p.error("--realism takes --sample, the render's sample_id")
    if a.cmd == "project" and a.filter and not a.edits:
        p.error("--filter takes --edits, the edit run whose edits it filtered")
''')
open(path, "w", encoding="ascii", newline="\n").write(src)
open(ppath, "w", encoding="ascii", newline="\n").write(psrc)
print("ok")
