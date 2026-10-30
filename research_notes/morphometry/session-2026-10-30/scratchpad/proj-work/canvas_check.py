"""FleXray's own canvas against morphoview.projection.to_canvas: content_box, and a blob's centroid
through prepare's array and tensor paths, loading fxr/inference/preprocessing.py without the
package's __init__ (which needs torchvision)."""
import importlib.util, os, sys, types
import numpy as np
import fxr
base = os.path.join(os.path.dirname(fxr.__file__), "inference")
pkg = types.ModuleType("fxr.inference"); pkg.__path__ = [base]; sys.modules["fxr.inference"] = pkg
for name in ("dicom", "preprocessing"):
    spec = importlib.util.spec_from_file_location("fxr.inference." + name, os.path.join(base, name + ".py"))
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
pp = sys.modules["fxr.inference.preprocessing"]
sys.path.insert(0, "/home/user/bordercall")
from morphoview import projection as PJ
import torch
P = pp.ImagePreprocessing()
print(pp.DEFAULT_IMAGE_SIZE)
for h, w in ((168, 136), (176, 144), (144, 160), (256, 256), (300, 97), (97, 300), (1024, 1024), (513, 512)):
    a = PJ.to_canvas(np.array([[0.0, 0.0], [w, h]]), h, w)
    mine = (min(round(a[0, 1]), 255), min(round(a[0, 0]), 255))
    mine = (mine[0], mine[1], max(mine[0] + 1, round(a[1, 1])), max(mine[1] + 1, round(a[1, 0])))
    print(h, w, P.content_box(h, w), mine, P.content_box(h, w) == mine)
for h, w, u0, v0 in ((168, 136, 40.3, 101.7), (144, 160, 120.2, 20.9), (1024, 1024, 300.4, 700.1), (300, 97, 50.5, 150.25)):
    r, c = np.indices((h, w))
    sig = 3.0 * max(h, w) / 168
    img = np.exp(-(((c + 0.5) - u0) ** 2 + ((r + 0.5) - v0) ** 2) / (2 * sig ** 2)).astype(np.float32)
    want = PJ.to_canvas([u0, v0], h, w)[0]
    for name, x in (("array", img), ("tensor", torch.from_numpy(img)[None, None])):
        out = P.prepare(x)[0, 0].numpy().astype(float)
        R, C = np.indices(out.shape)
        got = np.array([(out * (C + 0.5)).sum() / out.sum(), (out * (R + 0.5)).sum() / out.sum()])
        print(h, w, name, np.round(got, 3), np.round(want, 3), "err %.3f px" % np.linalg.norm(got - want))
