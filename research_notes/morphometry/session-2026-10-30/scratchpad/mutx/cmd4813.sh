S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad; mkdir -p $S/mut && cat > $S/mut/run_mutants.py <<'EOF'
"""Each mutant applied alone to a copy of bordercall's code, the shapes and projection tests run on
it; a mutant the tests pass is one they do not guard against."""
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys

SRC = "/home/user/bordercall"
HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(os.path.dirname(HERE), "venv", "bin", "python")
SKIP = {".git", "archive", "records", "research_notes", "reports", "holdings"}
TESTS = ["morphoview.tests.test_shapes", "morphoview.tests.test_projection"]
P, SHP, CLI = "morphoview/projection.py", "morphoview/shapes.py", "morphoview/__main__.py"

MUTANTS = [
    ("P1 zxy order", P, "return rz @ rx @ ry", "return rz @ ry @ rx"),
    ("P2 translation unturned", P, "pose[:3, 3] = rot @ np.asarray(view.xyz_mm, float) + np.asarray(view.isocentre_mm, float)",
     "pose[:3, 3] = np.asarray(view.xyz_mm, float) + np.asarray(view.isocentre_mm, float)"),
    ("P3 AP turn", P, '"AP": ((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0)),', '"AP": ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0)),'),
    ("P4 PA turn", P, '"PA": ((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)),', '"PA": ((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),'),
    ("P5 no turn", P, "None: ((-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),", "None: ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),"),
    ("P6 cx at a corner", P, "self.cx = view.x0 / view.delx + view.width / 2.0", "self.cx = view.x0 / view.delx + view.width / 2.0 - 0.5"),
    ("P7 fy from delx", P, "self.fx, self.fy = view.sdd / view.delx, view.sdd / view.pixel_y", "self.fx, self.fy = view.sdd / view.delx, view.sdd / view.delx"),
    ("P8 cy from delx", P, "self.cy = view.y0 / view.pixel_y + view.height / 2.0", "self.cy = view.y0 / view.delx + view.height / 2.0"),
    ("P9 parallel as cone", P, "scale = np.full(len(cam), 1.0 / self.view.sdd)", "scale = 1.0 / depth"),
    ("P10 beam beyond the detector", P, "in_beam=(depth > 0) & (depth < self.view.sdd) & on", "in_beam=(depth > 0) & on"),
    ("P11 pixels by column", P, "np.arange(self.view.width) + 0.5, indexing=\"ij\")", "np.arange(self.view.width) + 0.5, indexing=\"xy\")"),
    ("P12 parallel source at origin", P, "source = detector - [0.0, 0.0, sdd] if self.view.orthographic else np.zeros_like(detector)", "source = np.zeros_like(detector)"),
    ("P13 ray at the corner", P, "detector = np.stack([(uv[:, 0] - self.cx) * sdd / self.fx,", "detector = np.stack([(uv[:, 0] - 0.5 - self.cx) * sdd / self.fx,"),
    ("P14 magnification inverted", P, "            return self.view.sdd / depth", "            return depth / self.view.sdd"),
    ("P15 pads swapped", P, "return canvas / side, float((side - int(width)) // 2), float((side - int(height)) // 2)",
     "return canvas / side, float((side - int(height)) // 2), float((side - int(width)) // 2)"),
    ("P16 pads halved", P, "return canvas / side, float((side - int(width)) // 2), float((side - int(height)) // 2)",
     "return canvas / side, (side - int(width)) / 2.0, (side - int(height)) / 2.0"),
    ("P17 pads taken off", P, "return (np.atleast_2d(np.asarray(uv, float)) + [left, top]) * scale", "return (np.atleast_2d(np.asarray(uv, float)) - [left, top]) * scale"),
    ("P18 manifest cone only", P, "orthographic=bool(pose[\"orthographic\"]), orientation=orientation)", "orthographic=False, orientation=orientation)"),
    ("P19 manifest isocentre", P, "isocentre_mm=row[\"isocentre\"][\"point_mm\"],", "isocentre_mm=(0.0, 0.0, 0.0),"),
    ("S1 nearest by floor", SHP, "idx = np.rint(ijk).astype(np.int64)", "idx = np.floor(ijk).astype(np.int64)"),
    ("S2 window too narrow", SHP, "k0 = np.clip(np.floor(t0 * (n - 1)).astype(np.int64) - 1, 0, n - 1)", "k0 = np.clip(np.floor(t0 * (n - 1)).astype(np.int64) + 2, 0, n - 1)"),
    ("S3 step over n", SHP, "return hits * length / (n - 1)", "return hits * length / n"),
    ("S4 arcs too coarse", SHP, "step = 2.0 * math.acos(1.0 - tolerance / radius)", "step = 4.0 * math.acos(1.0 - tolerance / radius)"),
    ("S5 no refining", SHP, "if float(np.linalg.norm(fine[1::2] - mid, axis=1).max()) <= tolerance or k >= MOST_SAMPLES:", "if True:"),
    ("S6 cut ring not joined", SHP, "if closed and joined and len(starts) > 1:", "if False:"),
    ("S7 cut at the middle", SHP, "p = a + (NEAR - za) / (zb - za) * (b - a)", "p = 0.5 * (a + b)"),
    ("S8 plane normal", SHP, "return cls(centre, vt[2]), float(sv[2] / math.sqrt(len(pts)))", "return cls(centre, vt[1]), float(sv[2] / math.sqrt(len(pts)))"),
    ("S9 seen at by acos", SHP, "return math.degrees(math.asin(min(1.0, abs(float(d @ self.normal)))))", "return math.degrees(math.acos(min(1.0, abs(float(d @ self.normal)))))"),
    ("S10 area doubled", SHP, "return 0.5 * float(np.linalg.norm(np.cross(c, np.roll(c, -1, axis=0)).sum(axis=0)))", "return float(np.linalg.norm(np.cross(c, np.roll(c, -1, axis=0)).sum(axis=0)))"),
    ("S11 first piece", SHP, "mask = parts == int(np.argmax(sizes))", "mask = parts == 1"),
    ("S12 footprint shrunk", SHP, "c0, r0 = np.floor(got.uv.min(axis=0)).astype(int)", "c0, r0 = np.ceil(got.uv.min(axis=0)).astype(int)"),
    ("S13 image transposed", SHP, "out[part[:, 0], part[:, 1]] = got", "out[part[:, 1] % camera.view.height, part[:, 0] % camera.view.width] = got"),
    ("S14 circle open", SHP, "return Curve(centre + radius * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2), closed=True)",
     "return Curve(centre + radius * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2), closed=False)"),
    ("S15 arc turned left-handed", SHP, "    e2 = np.cross(n, e1)\n    angle = math.radians(angle_deg)", "    e2 = np.cross(e1, n)\n    angle = math.radians(angle_deg)"),
    ("C1 disc on one vertebra", CLI, "parts = [shade.get(lv) for lv in row[\"level\"].split(\"-\")]", "parts = [shade.get(row[\"level\"].split(\"-\")[0])]"),
    ("C2 pixel row and column swapped", CLI, "r, c = int(math.floor(uv[1])), int(math.floor(uv[0]))", "r, c = int(math.floor(uv[0])), int(math.floor(uv[1]))"),
    ("C3 b end from a", CLI, "out.update(place(cam, b, \"b\", canvas))", "out.update(place(cam, a, \"b\", canvas))"),
    ("C4 samples not the view's", CLI, "int(doc.get(\"n_samples\", a.samples))", "int(a.samples)"),
    ("C5 manifest detector", CLI, "view = PJ.View.from_manifest(row, int(blocks[\"detector\"]))", "view = PJ.View.from_manifest(row, 512)"),
    ("C6 frame axes u and v swapped", CLI, "row[e + \"u\"], row[e + \"v\"] = whole(got.uv[i, 0]), whole(got.uv[i, 1])", "row[e + \"u\"], row[e + \"v\"] = whole(got.uv[i, 1]), whole(got.uv[i, 0])"),
    ("C7 column reversed", CLI, "key=lambda r: LEVELS.index(r[\"level\"]))", "key=lambda r: -LEVELS.index(r[\"level\"]))"),
    ("C8 canvas of the turned image", CLI, "on = PJ.to_canvas(uv, v.height, v.width, canvas)[0]", "on = PJ.to_canvas(uv, v.width, v.height, canvas)[0]"),
    ("C9 shadow of the main piece", CLI, "SH.Volume.from_labels(vol, grid.affine, values, largest=False)", "SH.Volume.from_labels(vol, grid.affine, values, largest=True)"),
    ("C10 midpoint at a", CLI, "(\"mid_off_px\", None if a is None or b is None else 0.5 * (a + b))", "(\"mid_off_px\", a)"),
    ("C11 record of another file", CLI, "\"sha256\": sha256_of(a.lines), \"study\"", "\"sha256\": sha256_of(a.frames or a.lines), \"study\""),
    ("C12 magnification inverted", CLI, "prefix + \"_magnification\": whole(cam.magnification(depth))", "prefix + \"_magnification\": whole(1.0 / cam.magnification(depth))"),
]


def copy_tree(dest: str) -> None:
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for name in os.listdir(SRC):
        if name in SKIP:
            continue
        src = os.path.join(SRC, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, name), ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, os.path.join(dest, name))


def run(job):
    k, (name, path, old, new) = job
    dest = os.path.join(HERE, "w%d" % k)
    copy_tree(dest)
    target = os.path.join(dest, path)
    text = open(target).read()
    if name != "baseline":
        if text.count(old) != 1:
            return name, "NOT APPLIED (%d matches)" % text.count(old), ""
        open(target, "w").write(text.replace(old, new))
    got = subprocess.run([PY, "-m", "unittest"] + TESTS, cwd=dest, capture_output=True, text=True, timeout=900)
    tail = got.stderr.strip().splitlines()[-1] if got.stderr.strip() else ""
    failed = [ln for ln in got.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
    return name, ("passed" if got.returncode == 0 else "caught"), tail + " | " + "; ".join(f.split(" (")[0] for f in failed[:4])


def main():
    only = sys.argv[1:]
    jobs = [("baseline", P, "", "")] + [m for m in MUTANTS if not only or m[0].split()[0] in only]
    with cf.ProcessPoolExecutor(3) as pool:
        results = list(pool.map(run, list(enumerate(jobs))))
    for name, verdict, why in results:
        print("%-36s %-8s %s" % (name, verdict, why))
    json.dump(results, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
EOF
grep -c "" $S/mut/run_mutants.py