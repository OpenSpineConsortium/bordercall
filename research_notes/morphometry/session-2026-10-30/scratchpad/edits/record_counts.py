"""The recorder's counts: FleXray's channels on a volume of one attenuation, as whole numbers of
nanoDRR's steps, beside each recorded view."""
import sys

path = sys.argv[1]
text = open(path, encoding="ascii").read()
EDITS = [
    ("""- the phantom's own render, its vertebrae at 1000 HU in air: where each vertebra's channel is above
  zero, its support, and above FleXray's 0.5, its label mask (fxr/drr/rendering.py, _project_labels).
""",
     """- the phantom's own render, its vertebrae at 1000 HU in air: where each vertebra's channel is above
  zero, its support, and above FleXray's 0.5, its label mask (fxr/drr/rendering.py, _project_labels);
- the phantom's labels rendered over a volume of one attenuation, 1000 HU everywhere: each
  vertebra's channel at every pixel as a count of nanoDRR's steps, the channel over the attenuation
  and the ray's step. nanoDRR reads the attenuation between voxels (grid_sample's bilinear mode)
  and the label at the nearest voxel (nanodrr/drr/renderer.py, render), so only where the
  attenuation is the same everywhere is a channel a whole number of steps, its count of the
  samples whose nearest voxel holds the label; the recorder refuses a channel that is not.
"""),
    ("""def unpack(text: str, shape) -> np.ndarray:
    bits = np.frombuffer(zlib.decompress(base64.b64decode(text)), np.uint8)
    return np.unpackbits(bits)[:int(np.prod(shape))].reshape(shape).astype(bool)
""",
     """def unpack(text: str, shape) -> np.ndarray:
    bits = np.frombuffer(zlib.decompress(base64.b64decode(text)), np.uint8)
    return np.unpackbits(bits)[:int(np.prod(shape))].reshape(shape).astype(bool)


def pack_counts(counts: np.ndarray) -> str:
    return base64.b64encode(zlib.compress(np.asarray(counts, np.uint8).tobytes(), 9)).decode("ascii")


def unpack_counts(text: str, shape) -> np.ndarray:
    return np.frombuffer(zlib.decompress(base64.b64decode(text)), np.uint8).reshape(shape).astype(np.int64)
"""),
    ("""def camera(view, uv: np.ndarray) -> dict:""",
     """def bone_mu() -> float:
    \"\"\"nanoDRR's attenuation at the phantom's bone, per mm (nanodrr/data/preprocess.py, hu_to_mu).\"\"\"
    import torch
    from nanodrr.data.preprocess import hu_to_mu
    return float(hu_to_mu(torch.full((1, 1, 1, 1, 1), BONE_HU, dtype=torch.float64)).reshape(-1)[0])


def steps(view) -> np.ndarray:
    \"\"\"The step nanoDRR takes along each pixel's ray, the ray's length over n - 1, from its own
    rays (nanodrr/drr/renderer.py, render's step_size).\"\"\"
    import torch
    from fxr.drr.rendering import _resolve_intrinsics
    from nanodrr.drr.renderer import _make_src, _make_tgt
    f64 = torch.float64
    intr = _resolve_intrinsics({"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0],
                                "y0": [view.y0], "height": view.height, "width": view.width},
                               num_views=1, reference=torch.zeros(1, dtype=f64), orthographic_override=view.orthographic)
    tgt = _make_tgt(intr.k_inv, intr.sdd, view.height, view.width, torch.device("cpu"), f64)
    src = _make_src(view.orthographic, tgt, intr.sdd)
    length = (tgt - src).norm(dim=-1)[0].numpy()
    return (length / float(N_SAMPLES - 1)).reshape(view.height, view.width)


def counts_of(lab: np.ndarray, aff: np.ndarray, view, ids: Dict[str, int]) -> Dict[str, str]:
    \"\"\"Each vertebra's channel over a volume of one attenuation, in steps, packed; refused where a
    channel is not a whole number of steps or more than a byte holds.\"\"\"
    rendered = render(np.full(lab.shape, BONE_HU), lab, aff, view)
    out = {}
    for lv, i in ids.items():
        counts = rendered[i] / (bone_mu() * steps(view))
        whole = np.rint(counts)
        if not (np.abs(counts - whole).max() < 1e-3 and whole.max() < 256):
            raise ValueError("%s's channel is not a whole number of steps below 256" % lv)
        out[lv] = pack_counts(whole)
    return out


def camera(view, uv: np.ndarray) -> dict:"""),
    ("""            "masks": {lv: pack(rendered[i] > 0.5) for lv, i in ids.items()},
        })""",
     """            "masks": {lv: pack(rendered[i] > 0.5) for lv, i in ids.items()},
            "counts": counts_of(lab, aff, view, ids),
        })"""),
    ("""        "isocentre_mm": iso.tolist(), "n_samples": N_SAMPLES, "seg_threshold": 0.5,""",
     """        "isocentre_mm": iso.tolist(), "n_samples": N_SAMPLES, "seg_threshold": 0.5,
        "uniform": {"hu": BONE_HU, "mu_per_mm": bone_mu()},"""),
    ("""def add_crop(out: str = FIXTURE) -> dict:
    \"\"\"The crop's view added to a fixture recorded before it, the rest left as it was recorded.\"\"\"
    with open(out, encoding="ascii") as fh:
        doc = json.load(fh)
    lab, aff = phantom()
    if digest(lab, aff) != doc["phantom"]["sha256"]:
        raise SystemExit("the phantom is not the one %s was recorded from; record it whole" % out)
    doc["crop"] = crop_record(lab, aff, np.array(doc["isocentre_mm"]), level_ids())
    write(doc, out)
    return doc
""",
     """def add(parts: List[str], out: str = FIXTURE) -> dict:
    \"\"\"Parts added to a fixture recorded before them, the rest left as it was recorded: the crop's
    view, or each view's counts over a volume of one attenuation.\"\"\"
    with open(out, encoding="ascii") as fh:
        doc = json.load(fh)
    lab, aff = phantom()
    if digest(lab, aff) != doc["phantom"]["sha256"]:
        raise SystemExit("the phantom is not the one %s was recorded from; record it whole" % out)
    if "crop" in parts:
        doc["crop"] = crop_record(lab, aff, np.array(doc["isocentre_mm"]), level_ids())
    if "counts" in parts:
        from morphoview.projection import View
        for v in doc["views"]:
            v["counts"] = counts_of(lab, aff, View(**v["view"]), level_ids())
        doc["uniform"] = {"hu": BONE_HU, "mu_per_mm": bone_mu()}
    write(doc, out)
    return doc
"""),
    ("""    p.add_argument("--crop-only", action="store_true", help="add the crop's view to the fixture as it stands")
    a = p.parse_args(argv)
    doc = add_crop(a.out) if a.crop_only else record(a.out)""",
     """    p.add_argument("--add", action="append", choices=("crop", "counts"),
                   help="add this part alone to the fixture as it stands, the rest as it was recorded")
    a = p.parse_args(argv)
    doc = add(a.add, a.out) if a.add else record(a.out)"""),
]
for old, new in EDITS:
    if text.count(old) != 1:
        sys.exit("not found once: %r" % old[:80])
    text = text.replace(old, new)
open(path, "w", encoding="ascii", newline="\n").write(text)
print("flexray_record.py: %d edits" % len(EDITS))
