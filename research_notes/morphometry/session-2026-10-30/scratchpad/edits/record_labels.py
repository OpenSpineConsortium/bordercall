import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def sub(old, new, count=1):
    global src
    if src.count(old) != count:
        raise SystemExit("expected %d of %r, found %d" % (count, old[:70], src.count(old)))
    src = src.replace(old, new)

sub("""- the phantom's own render, its vertebrae at 1000 HU in air: where each vertebra's channel is above
  zero, its support, and above FleXray's 0.5, its label mask (fxr/drr/rendering.py, _project_labels);
""", """- the phantom's own render, its vertebrae at 1000 HU in air: FleXray's labels of each vertebra
  (DRRRenderResult.labels, fxr/drr/rendering.py, _project_labels) at the two thresholds a request
  names, 0.0, at which FleXray's training profile renders them (fxr/models/camera/config.py, the
  threshold of seg_cfg), where the vertebra's channel is above zero, its support, and 0.5, a bare
  request's default, at which SchwingNet's realism programme renders its truth masks
  (tools/realism.py, render_one), its label mask;
""")
sub("""OTHER_ORIENTATIONS = ("PA", None)
""", """OTHER_ORIENTATIONS = ("PA", None)
# FleXray's labels of the phantom at its training profile's threshold and at a bare request's
LABEL_THRESHOLDS = {"supports": 0.0, "masks": 0.5}
""")
sub('''def render(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, n_samples: int = N_SAMPLES) -> np.ndarray:
    """FleXray's raw per-label channels of one view, (labels + 1, height, width), as render_drr
    gives them in DRRRenderResult.rendered."""
    import torch
    from fxr.drr import DRRRenderRequest, render_drr
    intr = {"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0], "y0": [view.y0],
            "height": int(view.height), "width": int(view.width)}
    request = DRRRenderRequest(rot=torch.tensor([view.rot_deg], dtype=torch.float32),
                               xyz=torch.tensor([view.xyz_mm], dtype=torch.float32), intrinsics=intr,
                               isocenter=torch.tensor([view.isocentre_mm], dtype=torch.float32),
                               orientation=view.orientation, n_samples=int(n_samples), orthographic=view.orthographic)
    with torch.inference_mode():
        result = render_drr(volume=torch.from_numpy(hu.astype(np.float32))[None],
                            label=torch.from_numpy(label.astype(np.int64))[None],
                            affine=torch.from_numpy(np.asarray(aff, np.float32)), request=request)
    return result.rendered[0].double().numpy()


def render_crop(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, crop: dict,
                n_samples: int = N_SAMPLES) -> np.ndarray:
    """FleXray's channels of a view of a crop of the volume: the volume, its labels and its affine
    cut and moved by FleXray's own functions, as SchwingNet's render cuts them for each view
    (fxr/datasets/ct_crops.py, CropSpec, crop_z and offset_affine; tools/flexray_render.py, cut)."""
    from fxr.datasets.ct_crops import CropSpec, crop_z, offset_affine
    spec = CropSpec(0, crop["z_start"], crop["z_stop"], crop["pad_before"], crop["pad_after"])
    return render(crop_z(hu, spec, fill_value=AIR_HU), crop_z(label, spec, fill_value=0), offset_affine(aff, spec),
                  view, n_samples)


def crop_record(lab: np.ndarray, aff: np.ndarray, iso, ids: Dict[str, int]) -> dict:
    """The crop's view: its camera, the crop, and where each vertebra's channel is above zero. A
    vertebra wholly outside the crop has no channel at all, since render_drr gives one channel for
    each label up to the cropped volume's largest, so its support is empty."""
    view = view_of(CROP_VIEW, iso)
    rendered = render_crop(np.where(lab > 0, BONE_HU, AIR_HU), lab, aff, view, CROP)
    support = lambda i: rendered[i] > 0 if i < len(rendered) else np.zeros(rendered.shape[1:], bool)  # noqa: E731
    return {"name": CROP_VIEW["name"], "view": view.as_record(), "crop": dict(CROP),
            "supports": {lv: pack(support(i)) for lv, i in ids.items()}}
''', '''def result(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, n_samples: int = N_SAMPLES,
           seg_threshold: float = LABEL_THRESHOLDS["masks"]):
    """FleXray's render of one view, its DRRRenderResult, through render_drr as SchwingNet calls it,
    its labels cut at seg_threshold."""
    import torch
    from fxr.drr import DRRRenderRequest, render_drr
    intr = {"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0], "y0": [view.y0],
            "height": int(view.height), "width": int(view.width)}
    request = DRRRenderRequest(rot=torch.tensor([view.rot_deg], dtype=torch.float32),
                               xyz=torch.tensor([view.xyz_mm], dtype=torch.float32), intrinsics=intr,
                               isocenter=torch.tensor([view.isocentre_mm], dtype=torch.float32),
                               orientation=view.orientation, n_samples=int(n_samples), orthographic=view.orthographic,
                               seg_threshold=float(seg_threshold))
    with torch.inference_mode():
        return render_drr(volume=torch.from_numpy(hu.astype(np.float32))[None],
                          label=torch.from_numpy(label.astype(np.int64))[None],
                          affine=torch.from_numpy(np.asarray(aff, np.float32)), request=request)


def render(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, n_samples: int = N_SAMPLES) -> np.ndarray:
    """FleXray's raw per-label channels of one view, (labels + 1, height, width), as render_drr
    gives them in DRRRenderResult.rendered."""
    return result(hu, label, aff, view, n_samples).rendered[0].double().numpy()


def labels(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, seg_threshold: float) -> np.ndarray:
    """FleXray's labels of one view at a threshold, (labels + 1, height, width), the background
    first, as render_drr gives them in DRRRenderResult.labels."""
    return result(hu, label, aff, view, seg_threshold=seg_threshold).labels[0].numpy() > 0.5


def cropped(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, crop: dict):
    """The volume, its labels and its affine cut and moved by FleXray's own functions, as
    SchwingNet's render cuts them for each view (fxr/datasets/ct_crops.py, CropSpec, crop_z and
    offset_affine; tools/flexray_render.py, cut)."""
    from fxr.datasets.ct_crops import CropSpec, crop_z, offset_affine
    spec = CropSpec(0, crop["z_start"], crop["z_stop"], crop["pad_before"], crop["pad_after"])
    return crop_z(hu, spec, fill_value=AIR_HU), crop_z(label, spec, fill_value=0), offset_affine(aff, spec)


def crop_record(lab: np.ndarray, aff: np.ndarray, iso, ids: Dict[str, int]) -> dict:
    """The crop's view: its camera, the crop, and each vertebra's support, FleXray's label of it at
    its training profile's threshold. A vertebra wholly outside the crop has no label at all, since
    render_drr gives one channel for each label up to the cropped volume's largest, so its support
    is empty."""
    view = view_of(CROP_VIEW, iso)
    hu, label, affine = cropped(np.where(lab > 0, BONE_HU, AIR_HU), lab, aff, CROP)
    got = labels(hu, label, affine, view, LABEL_THRESHOLDS["supports"])
    support = lambda i: got[i] if i < len(got) else np.zeros(got.shape[1:], bool)  # noqa: E731
    return {"name": CROP_VIEW["name"], "view": view.as_record(), "crop": dict(CROP),
            "supports": {lv: pack(support(i)) for lv, i in ids.items()}}
''')
sub('''        rendered = render(bone, lab, aff, view)
        ballrender = render(balls, bead_lab, aff, view, BEAD_SAMPLES)
''', '''        cut = {key: labels(bone, lab, aff, view, t) for key, t in LABEL_THRESHOLDS.items()}
        ballrender = render(balls, bead_lab, aff, view, BEAD_SAMPLES)
''')
sub('''            "supports": {lv: pack(rendered[i] > 0) for lv, i in ids.items()},
            "masks": {lv: pack(rendered[i] > 0.5) for lv, i in ids.items()},
''', '''            "supports": {lv: pack(cut["supports"][i]) for lv, i in ids.items()},
            "masks": {lv: pack(cut["masks"][i]) for lv, i in ids.items()},
''')
sub('''"n_samples": N_SAMPLES, "seg_threshold": 0.5,''', '''"n_samples": N_SAMPLES, "label_thresholds": dict(LABEL_THRESHOLDS),''')
open(path, "w", encoding="ascii", newline="\n").write(src)
print("ok")
