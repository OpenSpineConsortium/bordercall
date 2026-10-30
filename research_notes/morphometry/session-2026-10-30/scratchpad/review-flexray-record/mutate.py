"""Mutations of morphoview/projection.py in the scratch copy, each run against
test_projection (Live skipped without torch), to see which mutations the record's tests catch."""
import os
import subprocess
import sys

COPY = sys.argv[1]
PY = sys.argv[2]
ONLY = sys.argv[3:]
TARGET = os.path.join(COPY, "morphoview", "projection.py")
ORIGINAL = open(TARGET).read()

MUTATIONS = {
    "half_pixel_cx_cy": [("view.x0 / view.delx + view.width / 2.0", "view.x0 / view.delx + (view.width - 1) / 2.0"),
                         ("view.y0 / view.pixel_y + view.height / 2.0", "view.y0 / view.pixel_y + (view.height - 1) / 2.0")],
    "half_pixel_cx_only": [("view.x0 / view.delx + view.width / 2.0", "view.x0 / view.delx + (view.width - 1) / 2.0")],
    "PA_as_AP": [('"PA": ((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))',
                  '"PA": ((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0))')],
    "None_as_AP": [('None: ((-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0))',
                    'None: ((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0))')],
    "euler_zyx": [("return rz @ rx @ ry", "return rz @ ry @ rx")],
    "ortho_as_cone": [("scale = np.full(len(cam), 1.0 / self.view.sdd)", "scale = 1.0 / depth")],
    "no_far_bound": [("in_beam=(depth > 0) & (depth < self.view.sdd) & on", "in_beam=(depth > 0) & on")],
    "canvas_left_top_swapped": [("return canvas / side, float((side - int(width)) // 2), float((side - int(height)) // 2)",
                                 "return canvas / side, float((side - int(height)) // 2), float((side - int(width)) // 2)")],
    "canvas_float_pad": [("return canvas / side, float((side - int(width)) // 2), float((side - int(height)) // 2)",
                          "return canvas / side, (side - int(width)) / 2.0, (side - int(height)) / 2.0")],
    "canvas_half_pixel": [("return (np.atleast_2d(np.asarray(uv, float)) + [left, top]) * scale",
                           "return (np.atleast_2d(np.asarray(uv, float)) + [left, top] - 0.5) * scale + 0.5")],
    "v_uses_fx": [("self.fy * cam[:, 1] * scale + self.cy", "self.fx * cam[:, 1] * scale + self.cy")],
    "x0_sign": [("self.cx = view.x0 / view.delx + view.width / 2.0", "self.cx = -view.x0 / view.delx + view.width / 2.0")],
    "isocentre_ignored": [("pose[:3, 3] = rot @ np.asarray(view.xyz_mm, float) + np.asarray(view.isocentre_mm, float)",
                           "pose[:3, 3] = rot @ np.asarray(view.xyz_mm, float)")],
    "project_quarter_px": [("uv = np.stack([self.fx * cam[:, 0] * scale + self.cx, self.fy * cam[:, 1] * scale + self.cy], axis=1)",
                            "uv = np.stack([self.fx * cam[:, 0] * scale + self.cx + 0.25, self.fy * cam[:, 1] * scale + self.cy], axis=1)")],
    "project_and_rays_half_px": [
        ("self.cx = view.x0 / view.delx + view.width / 2.0", "self.cx = view.x0 / view.delx + view.width / 2.0 - 0.5"),
        ("v, u = np.meshgrid(np.arange(self.view.height) + 0.5, np.arange(self.view.width) + 0.5, indexing=\"ij\")",
         "v, u = np.meshgrid(np.arange(self.view.height) + 0.5, np.arange(self.view.width), indexing=\"ij\")")],
}


def run(name, edits):
    text = ORIGINAL
    for old, new in edits:
        assert text.count(old) == 1, (name, old)
        text = text.replace(old, new)
    with open(TARGET, "w") as fh:
        fh.write(text)
    try:
        out = subprocess.run([PY, "-m", "unittest", "morphoview.tests.test_projection"], cwd=COPY,
                             capture_output=True, text=True, timeout=900)
    finally:
        with open(TARGET, "w") as fh:
            fh.write(ORIGINAL)
    tail = out.stderr.strip().splitlines()
    failed = [line for line in tail if line.startswith(("FAIL:", "ERROR:"))]
    summary = tail[-1] if tail else ""
    return summary, failed


if __name__ == "__main__":
    for name, edits in MUTATIONS.items():
        if ONLY and name not in ONLY:
            continue
        summary, failed = run(name, edits)
        print("%-26s %s" % (name, summary))
        for line in failed:
            print("      ", line)
        sys.stdout.flush()
