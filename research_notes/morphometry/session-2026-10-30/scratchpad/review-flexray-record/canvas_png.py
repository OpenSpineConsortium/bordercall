"""FleXray's canvas fed a 16-bit PNG file, as SchwingNet's renders are written (save_png), against
morphoview.projection.to_canvas: a Gaussian spot's centre, at sizes the record does not hold."""
import os
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ  # noqa: E402
from morphoview.tests import flexray_record as FR  # noqa: E402

pre = FR.image_preprocessing()
tmp = tempfile.mkdtemp()
worst = 0.0
for h, w, u, v in ((200, 120, 33.3, 150.6), (90, 211, 170.2, 40.7), (512, 512, 100.25, 400.75), (257, 256, 128.0, 128.0)):
    img = FR.spot(h, w, u, v)
    data = np.round(np.clip(img, 0, 1) * 65535.0).astype(np.uint16)
    path = os.path.join(tmp, "s.png")
    Image.fromarray(data).save(path, format="PNG")
    got = FR.centroid(pre.prepare(path)[0, 0].double().numpy())
    want = PJ.to_canvas([u, v], h, w)[0]
    err = float(np.linalg.norm(np.array(got) - want))
    worst = max(worst, err)
    print((h, w), "want", np.round(want, 4), "got", np.round(got, 4), "err %.4f" % err)
print("worst", worst)
