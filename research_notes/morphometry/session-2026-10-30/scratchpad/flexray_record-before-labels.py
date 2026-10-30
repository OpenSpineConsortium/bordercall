"""What FleXray 1.0.2 itself makes of the morphometry phantom, recorded for test_projection.py in
fixtures/flexray.json, so the projection is held to FleXray's own camera and renders where FleXray
is not installed, as in bordercall's own environments:

    python -m morphoview.tests.flexray_record

in an environment with FleXray 1.0.2 (the distribution flexray, imported as fxr), nanoDRR 0.1.5 and
torch beside bordercall's own requirements. Nothing of the package imports FleXray: this file
imports it inside the functions that render, so the tests read its views and its packing without it.

Three views of the straight L2 to L4 phantom at 0.8 by 0.8 by 1 mm, each differing from the others
in what FleXray's camera reads: a lateral cone beam on a detector taller than wide, an oblique cone
beam with its principal point off the centre and pixels taller than wide, and a parallel beam from
behind on a detector wider than tall. Each records:

- FleXray's camera: the inverse extrinsics and the inverse intrinsics render_drr hands nanoDRR,
  made by FleXray's own functions in float64 (fxr/drr/rendering.py, _make_rt_inv_per_view and
  _resolve_intrinsics), and the rays nanoDRR casts through 41 pixels, the four corners and the
  centre among them (nanodrr/drr/renderer.py, _make_tgt and _make_src);
- beads: balls of 2.5 mm radius, each a label of its own, centred on the ends of the lines
  morphoview draws on the phantom no nearer than 7 mm to one another, rendered as a CT of air with
  the balls at 1000 HU at 2000 samples a ray, a step of about 0.6 mm, so that a ball's few pixels
  are summed smoothly; the centroid of each ball's channel on the render;
- the phantom's own render, its vertebrae at 1000 HU in air: where each vertebra's channel is above
  zero, its support, and above FleXray's 0.5, its label mask (fxr/drr/rendering.py, _project_labels);
- the phantom's labels rendered over a volume of one attenuation, 1000 HU everywhere: each
  vertebra's channel at every pixel as a count of nanoDRR's steps, the channel over the attenuation
  and the ray's step. nanoDRR reads the attenuation between voxels (grid_sample's bilinear mode)
  and the label at the nearest voxel (nanodrr/drr/renderer.py, render), so only where the
  attenuation is the same everywhere is a channel a whole number of steps, its count of the
  samples whose nearest voxel holds the label; the recorder refuses a channel that is not.

Beside the views it records a fourth, the first view's pose on a square detector of a crop of the
phantom, cut, padded with air and its affine moved by FleXray's own functions as SchwingNet's
render cuts the CT for each view (fxr/datasets/ct_crops.py, crop_z and offset_affine), so that L4
lies wholly outside it, L3 across its edge and L2 within it: each vertebra's support on that render.
It records the camera of the first view's pose under nanoDRR's two other orientations, PA and
none, and FleXray's canvas: where content_box puts images of eight sizes, and
where FleXray's resize carries the centre of a smooth spot on four of them, through prepare's array
and tensor paths (fxr/inference/preprocessing.py).

The renders take FleXray's production path, a float32 volume through render_drr, the phantom's at
FleXray's 500 samples a ray, as SchwingNet's render passes it (tools/flexray_render.py).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import zlib
from typing import Dict, List, Tuple

import numpy as np

LEVELS = ["L2", "L3", "L4"]
SPACING = (0.8, 0.8, 1.0)
BONE_HU, AIR_HU = 1000.0, -1000.0
BEAD_MM, APART_MM = 2.5, 7.0
N_SAMPLES = 500                 # FleXray's DRRRenderRequest.n_samples
BEAD_SAMPLES = 2000             # the beads' renders, whose balls are a few pixels across
OTHER_ORIENTATIONS = ("PA", None)
# images on FleXray's canvas: the views' sizes, a square, sizes far from square, larger than the
# canvas and one pixel off square
CANVAS_SIZES = ((168, 136), (176, 144), (144, 160), (256, 256), (300, 97), (97, 300), (1024, 1024), (513, 512))
# a spot's image (height, width) and centre (u, v)
SPOTS = ((168, 136, 40.3, 101.7), (144, 160, 120.2, 20.9), (1024, 1024, 300.4, 700.1), (300, 97, 50.5, 150.25))
FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "flexray.json")

# the source's place from the isocentre and the turn, the detector and its pixels; the isocentre is
# the phantom's centroid
VIEWS = [
    {"name": "lateral cone", "rot_deg": (90.0, 3.0, -2.0), "xyz_mm": (-9.0, 700.0, -15.0), "sdd": 1200.0,
     "delx": 1.8, "height": 168, "width": 136, "orthographic": False},
    {"name": "oblique cone, principal point off the centre", "rot_deg": (20.0, -10.0, 5.0),
     "xyz_mm": (-30.0, 650.0, 20.0), "sdd": 1180.0, "delx": 1.6, "dely": 1.7, "x0": 40.0, "y0": -40.0,
     "height": 176, "width": 144, "orthographic": False},
    {"name": "parallel beam from behind", "rot_deg": (-140.0, 12.0, -6.0), "xyz_mm": (15.0, 820.0, 10.0),
     "sdd": 1240.0, "delx": 1.6, "height": 144, "width": 160, "orthographic": True},
]


# a crop of the phantom's slices with air pads before and after, as a crop of a volume shorter
# than FleXray's 256 slices has, on a square detector as SchwingNet's renders are
CROP = {"z_start": 140, "z_stop": 230, "pad_before": 5, "pad_after": 7}
CROP_VIEW = {"name": "lateral cone of a crop", "rot_deg": (90.0, 3.0, -2.0), "xyz_mm": (-9.0, 700.0, -15.0),
             "sdd": 1200.0, "delx": 1.8, "height": 160, "width": 160, "orthographic": False}


def view_of(spec: dict, isocentre) -> "object":
    from morphoview.projection import View
    fields = {k: v for k, v in spec.items() if k != "name"}
    return View(isocentre_mm=tuple(float(x) for x in isocentre), **fields)


def phantom() -> Tuple[np.ndarray, np.ndarray]:
    """The straight L2 to L4 phantom the lines export's tests measure."""
    from morphometry.tests import phantom as P
    return P.draw(P.straight(LEVELS, P.Vert()), spacing=SPACING)


def digest(lab: np.ndarray, aff: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(repr((lab.shape, str(lab.dtype))).encode())
    h.update(np.ascontiguousarray(lab).tobytes())
    h.update(np.asarray(aff, np.float64).tobytes())
    return h.hexdigest()


def level_ids() -> Dict[str, int]:
    from morphometry.tests import phantom as P
    return {lv: P.LEVEL_IDS[lv] for lv in LEVELS}


def centroid_mm(lab: np.ndarray, aff: np.ndarray) -> np.ndarray:
    idx = np.argwhere(lab > 0).astype(float)
    return idx.mean(axis=0) @ aff[:3, :3].T + aff[:3, 3]


def pack(mask: np.ndarray) -> str:
    return base64.b64encode(zlib.compress(np.packbits(np.asarray(mask, bool).ravel()).tobytes(), 9)).decode("ascii")


def unpack(text: str, shape) -> np.ndarray:
    bits = np.frombuffer(zlib.decompress(base64.b64decode(text)), np.uint8)
    return np.unpackbits(bits)[:int(np.prod(shape))].reshape(shape).astype(bool)


def pack_counts(counts: np.ndarray) -> str:
    return base64.b64encode(zlib.compress(np.asarray(counts, np.uint8).tobytes(), 9)).decode("ascii")


def unpack_counts(text: str, shape) -> np.ndarray:
    return np.frombuffer(zlib.decompress(base64.b64decode(text)), np.uint8).reshape(shape).astype(np.int64)


def line_ends(lab: np.ndarray, aff: np.ndarray) -> np.ndarray:
    """The ends of every line morphoview draws on the phantom, its vertebrae and its discs."""
    from maskedge import edge as E
    from morphometry import column as COL
    from morphometry import measure as M
    from morphoview import lines as LN
    from scanimport import geometry as G
    names = {i: lv for lv, i in level_ids().items()}
    vs = E.vertebrae(lab, G.VoxelGrid(aff, lab.shape), names)
    got = []
    for level in LEVELS:
        vals, _, ped = M.vertebra_values(vs[level])
        got += LN.checked(LN.vertebra_lines(vs[level], ped), vals)
    for up, low in zip(LEVELS, LEVELS[1:]):
        got += LN.checked(LN.discs(vs[up], vs[low]), COL.disc_heights(vs[up], vs[low]))
    return np.array([end for ln in got if ln.status == "drawn" for end in (ln.a, ln.b)], float)


def pick_beads(ends: np.ndarray, apart: float = APART_MM) -> np.ndarray:
    chosen: List[np.ndarray] = []
    for p in ends:
        if all(float(np.linalg.norm(p - q)) >= apart for q in chosen):
            chosen.append(p)
    return np.array(chosen)


def bead_labels(shape, aff: np.ndarray, centres: np.ndarray, radius: float = BEAD_MM) -> Tuple[np.ndarray, np.ndarray]:
    """A label volume on the phantom's grid with ball k + 1 of `radius` about each centre, and each
    ball's centroid in the world, the mean of its voxels' centres."""
    lab = np.zeros(shape, np.int64)
    inv = np.linalg.inv(aff)
    out = []
    for k, c in enumerate(centres):
        ijk = inv[:3, :3] @ c + inv[:3, 3]
        lo = np.maximum(np.floor(ijk - 5).astype(int), 0)
        hi = np.minimum(np.ceil(ijk + 5).astype(int) + 1, np.array(shape))
        g = np.stack(np.meshgrid(*(np.arange(a, b) for a, b in zip(lo, hi)), indexing="ij"), -1).reshape(-1, 3)
        world = g @ aff[:3, :3].T + aff[:3, 3]
        inside = np.linalg.norm(world - c, axis=1) <= radius
        if (lab[tuple(g[inside].T)] != 0).any():
            raise ValueError("two beads share a voxel")
        lab[tuple(g[inside].T)] = k + 1
        out.append(world[inside].mean(axis=0))
    return lab, np.array(out)


def render(hu: np.ndarray, label: np.ndarray, aff: np.ndarray, view, n_samples: int = N_SAMPLES) -> np.ndarray:
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


def bone_mu() -> float:
    """nanoDRR's attenuation at the phantom's bone, per mm (nanodrr/data/preprocess.py, hu_to_mu)."""
    import torch
    from nanodrr.data.preprocess import hu_to_mu
    return float(hu_to_mu(torch.full((1, 1, 1, 1, 1), BONE_HU, dtype=torch.float64)).reshape(-1)[0])


def steps(view) -> np.ndarray:
    """The step nanoDRR takes along each pixel's ray, the ray's length over n - 1, from its own
    rays (nanodrr/drr/renderer.py, render's step_size)."""
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
    """Each vertebra's channel over a volume of one attenuation, in steps, packed; refused where a
    channel is not a whole number of steps or more than a byte holds."""
    rendered = render(np.full(lab.shape, BONE_HU), lab, aff, view)
    out = {}
    for lv, i in ids.items():
        counts = rendered[i] / (bone_mu() * steps(view))
        whole = np.rint(counts)
        if not (np.abs(counts - whole).max() < 1e-3 and whole.max() < 256):
            raise ValueError("%s's channel is not a whole number of steps below 256" % lv)
        out[lv] = pack_counts(whole)
    return out


def camera(view, uv: np.ndarray) -> dict:
    """FleXray's inverse extrinsics and intrinsics for the view and nanoDRR's rays through uv, in
    float64."""
    import torch
    from fxr.drr.rendering import _make_rt_inv_per_view, _resolve_intrinsics
    f64 = torch.float64
    rt = _make_rt_inv_per_view(torch.tensor([view.rot_deg], dtype=f64), torch.tensor([view.xyz_mm], dtype=f64),
                               orientation=view.orientation, isocenter=torch.tensor(view.isocentre_mm, dtype=f64))
    intr = _resolve_intrinsics({"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0],
                                "y0": [view.y0], "height": view.height, "width": view.width},
                               num_views=1, reference=torch.zeros(1, dtype=f64), orthographic_override=view.orthographic)
    tgt, src = rays_at(intr.k_inv, intr.sdd, view, uv)
    rt0 = rt[0].numpy()
    to_world = lambda p: p @ rt0[:3, :3].T + rt0[:3, 3]  # noqa: E731
    return {"rt_inv": rt0.tolist(), "k_inv": intr.k_inv[0].numpy().tolist(), "uv": uv.tolist(),
            "source": to_world(src).tolist(), "detector": to_world(tgt).tolist()}


def rays_at(k_inv, sdd, view, uv: np.ndarray):
    """nanoDRR's ray ends in the camera through every pixel of the view, read at the pixels whose
    centres are uv, so the rays are found in nanoDRR's own order of pixels (row r, column c being
    ray r W + c)."""
    import torch
    from nanodrr.drr.renderer import _make_src, _make_tgt
    tgt = _make_tgt(k_inv, sdd, view.height, view.width, torch.device("cpu"), torch.float64)
    src = _make_src(view.orthographic, tgt, sdd)
    n = (np.floor(uv[:, 1]) * view.width + np.floor(uv[:, 0])).astype(int)
    tgt0 = tgt[0].numpy()[n]
    src0 = src[0].numpy()[n] if view.orthographic else np.repeat(src[0].numpy(), len(n), axis=0)
    return tgt0, src0


def sample_pixels(view, count: int = 36, seed: int = 11) -> np.ndarray:
    """The four corners, the centre and `count` pixels drawn at random, as their centres (u, v)."""
    h, w = view.height, view.width
    fixed = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1), (h // 2, w // 2)]
    rng = np.random.default_rng(seed)
    drawn = [(int(rng.integers(h)), int(rng.integers(w))) for _ in range(count)]
    rc = np.array(fixed + drawn, float)
    return rc[:, ::-1] + 0.5


def channel_centroid(img: np.ndarray):
    """A channel's centroid on the render, (u, v) at the pixels' centres, or None where it is empty
    or touches the image's edge, where its centroid would be cut."""
    total = float(img.sum())
    if not total > 0 or img[0].any() or img[-1].any() or img[:, 0].any() or img[:, -1].any():
        return None
    r, c = np.indices(img.shape)
    return [float((img * (c + 0.5)).sum() / total), float((img * (r + 0.5)).sum() / total)]


def orientations(iso) -> List[dict]:
    """The first view's pose under nanoDRR's other two orientations, the camera alone."""
    out = []
    for orientation in OTHER_ORIENTATIONS:
        view = view_of(dict(VIEWS[0], orientation=orientation), iso)
        out.append({"view": view.as_record(), "camera": camera(view, sample_pixels(view))})
    return out


def image_preprocessing():
    """FleXray's ImagePreprocessing at its defaults. fxr.inference's __init__ imports the
    segmentation runner, which needs torchvision and huggingface_hub; where they are missing the
    module is read from its own file with the one module of the package it imports."""
    try:
        from fxr.inference.preprocessing import ImagePreprocessing
    except ImportError:
        import importlib.util
        import sys
        import types
        import fxr
        base = os.path.join(os.path.dirname(fxr.__file__), "inference")
        package = types.ModuleType("fxr.inference")
        package.__path__ = [base]
        sys.modules["fxr.inference"] = package
        for name in ("dicom", "preprocessing"):
            spec = importlib.util.spec_from_file_location("fxr.inference." + name, os.path.join(base, name + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
        ImagePreprocessing = sys.modules["fxr.inference.preprocessing"].ImagePreprocessing
    return ImagePreprocessing()


def spot(height: int, width: int, u: float, v: float) -> np.ndarray:
    """A Gaussian spot centred at (u, v), a 56th of the image's longer side wide, so that resized to
    the canvas it spans some pixels."""
    r, c = np.indices((height, width))
    sigma = max(height, width) / 56.0
    return np.exp(-(((c + 0.5) - u) ** 2 + ((r + 0.5) - v) ** 2) / (2.0 * sigma ** 2)).astype(np.float32)


def centroid(img: np.ndarray) -> List[float]:
    r, c = np.indices(img.shape)
    total = float(img.sum())
    return [float((img * (c + 0.5)).sum() / total), float((img * (r + 0.5)).sum() / total)]


def canvas() -> dict:
    """FleXray's canvas: content_box of each size, and each spot's centre after prepare."""
    import torch
    pre = image_preprocessing()
    boxes = [{"height": h, "width": w, "content_box": [int(x) for x in pre.content_box(h, w)]} for h, w in CANVAS_SIZES]
    spots = []
    for h, w, u, v in SPOTS:
        img = spot(h, w, u, v)
        got = {path: centroid(pre.prepare(x)[0, 0].double().numpy())
               for path, x in (("array", img), ("tensor", torch.from_numpy(img)[None, None]))}
        spots.append({"height": h, "width": w, "uv": [u, v], "canvas_uv": got})
    return {"image_size": [int(x) for x in pre.image_size], "pad_to_square": bool(pre.pad_to_square),
            "boxes": boxes, "spots": spots}


def record(out: str = FIXTURE) -> dict:
    import importlib.metadata as md
    lab, aff = phantom()
    iso = centroid_mm(lab, aff)
    ids = level_ids()
    beads = pick_beads(line_ends(lab, aff))
    bead_lab, bead_mm = bead_labels(lab.shape, aff, beads)
    bone = np.where(lab > 0, BONE_HU, AIR_HU)
    balls = np.where(bead_lab > 0, BONE_HU, AIR_HU)
    views = []
    for spec in VIEWS:
        view = view_of(spec, iso)
        rendered = render(bone, lab, aff, view)
        ballrender = render(balls, bead_lab, aff, view, BEAD_SAMPLES)
        views.append({
            "name": spec["name"], "view": view.as_record(),
            "camera": camera(view, sample_pixels(view)),
            "bead_centroids_uv": [channel_centroid(ballrender[k + 1]) for k in range(len(bead_mm))],
            "supports": {lv: pack(rendered[i] > 0) for lv, i in ids.items()},
            "masks": {lv: pack(rendered[i] > 0.5) for lv, i in ids.items()},
            "counts": counts_of(lab, aff, view, ids),
        })
    doc = {
        "about": "What FleXray made of the morphometry phantom; written by python -m morphoview.tests.flexray_record.",
        "versions": {name: md.version(name) for name in ("flexray", "nanodrr", "torch")},
        "phantom": {"levels": LEVELS, "spacing_mm": list(SPACING), "shape": list(lab.shape),
                    "sha256": digest(lab, aff), "ids": ids},
        "isocentre_mm": iso.tolist(), "n_samples": N_SAMPLES, "seg_threshold": 0.5,
        "uniform": {"hu": BONE_HU, "mu_per_mm": bone_mu()},
        "beads": {"radius_mm": BEAD_MM, "apart_mm": APART_MM, "n_samples": BEAD_SAMPLES,
                  "centroids_mm": bead_mm.tolist()},
        "views": views,
        "orientations": orientations(iso),
        "canvas": canvas(),
        "crop": crop_record(lab, aff, iso, ids),
    }
    write(doc, out)
    return doc


def add(parts: List[str], out: str = FIXTURE) -> dict:
    """Parts added to a fixture recorded before them, the rest left as it was recorded: the crop's
    view, or each view's counts over a volume of one attenuation."""
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


def write(doc: dict, out: str) -> None:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".part", "w", encoding="ascii", newline="\n") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    os.replace(out + ".part", out)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m morphoview.tests.flexray_record")
    p.add_argument("--out", default=FIXTURE)
    p.add_argument("--add", action="append", choices=("crop", "counts"),
                   help="add this part alone to the fixture as it stands, the rest as it was recorded")
    a = p.parse_args(argv)
    doc = add(a.add, a.out) if a.add else record(a.out)
    seen = sum(c is not None for v in doc["views"] for c in v["bead_centroids_uv"])
    print("%s: %d views, %d beads, %d bead centroids seen" % (a.out, len(doc["views"]),
                                                             len(doc["beads"]["centroids_mm"]), seen))


if __name__ == "__main__":
    main()
