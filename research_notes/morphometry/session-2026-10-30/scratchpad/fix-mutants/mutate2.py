"""The second round's mutants: each one replacement in the fixed code; the named tests must fail on it."""
import os, shutil, subprocess, sys

ROOT, WORK, PY = sys.argv[1], sys.argv[2], sys.argv[3]
FR = "morphometry.tests.test_lines_export"
MV = "morphoview.tests.test_lines.Phantom.test_a_median_is_drawn_in_the_reading_nearest_it"
MAIN, LINES = "morphometry/__main__.py", "morphoview/lines.py"
MUTANTS = [
    ("canal depth on the wrong section", LINES, "_, (_, _, wa, wp, xm, z) = nearest(1, canal[\"canal_ap\"])",
     "_, (_, _, wa, wp, xm, z) = rows[0]", [MV]),
    ("canal width on the wrong section", LINES, "s, _ = nearest(0, canal[\"canal_w\"])", "s, _ = rows[0]", [MV]),
    ("h_post in the furthest cell", LINES, "cell, lo, hi = min(runs, key=lambda r:", "cell, lo, hi = max(runs, key=lambda r:", [MV]),
    ("widths' ends named the wrong way", LINES, "**{k: (\"left\", \"right\") for k in (\"body_w_mid\"",
     "**{k: (\"right\", \"left\") for k in (\"body_w_mid\"", [FR + ".Frames.test_each_end_lies_where_its_name_says"]),
    ("a and b swapped in the file", MAIN, "out = [row(\"\", ln.a, ln.b, whole(ln.value)",
     "out = [row(\"\", ln.b, ln.a, whole(ln.value)", [FR + ".Frames.test_each_end_lies_where_its_name_says"]),
    ("every frame called the bisector", MAIN, "return \"one plate\" if \"axis_one_plate\" in v.flags else \"bisector\"",
     "return \"bisector\"", [FR + ".Frames.test_each_frame_says_which_axis_its_z_lies_along"]),
    ("the column's line written as z", MAIN, "column = v.column_ez if v.column_ez is not None else f.ez", "column = f.ez",
     [FR + ".Frames.test_each_frame_says_which_axis_its_z_lies_along"]),
    ("geometry to four places", MAIN, "return repr(x) if math.isfinite(x) else \"\"",
     "return (\"%.4f\" % x) if math.isfinite(x) else \"\"", [FR + ".RunWithLines.test_each_measured_vertebra_has_a_right_handed_frame",
                                                            FR + ".RunWithLines.test_a_length_is_the_distance_between_its_ends"]),
    ("measured written as the value", MAIN, "whole(ln.value), float(ln.measured), ends.get",
     "whole(ln.measured), float(ln.measured), ends.get", [FR + ".Failing.test_a_line_off_its_row_is_withheld_and_keeps_both_values"]),
    ("the value written as measured", MAIN, "whole(ln.value), float(ln.measured), ends.get",
     "whole(ln.value), float(ln.value), ends.get", [FR + ".Failing.test_a_line_off_its_row_is_withheld_and_keeps_both_values"]),
    ("stamp blind to the drawing's code", MAIN, "h.update(LINES_SOURCE.encode() + b\"\\0\" + read_bytes(os.path.join(here, LINES_SOURCE)))",
     "h.update(LINES_SOURCE.encode() + b\"\\0\")", [FR + ".Stamp"]),
    ("parts written with their line's ends", MAIN, "out += [row(name, a, b, \"\", \"\"", "out += [row(name, ln.a, ln.b, \"\", \"\"",
     [FR + ".RunWithLines.test_the_further_segments_ride_with_their_line"]),
    ("side files written in place", MAIN, "        write_atomic(lines, lines_path, LINE_FIELDS)\n        write_atomic(frames, frames_path, FRAME_FIELDS)\n",
     "        write_rows(lines, lines_path, LINE_FIELDS)\n        write_rows(frames, frames_path, FRAME_FIELDS)\n",
     [FR + ".Failing.test_a_study_cut_short_at_any_of_its_writes_is_measured_again"]),
    ("every level in the first vertebra's frame", MAIN, "frames.append(frame_row(study, lv, v))",
     "frames.append(frame_row(study, lv, next(iter(verts.values()))))", [FR + ".Frames.test_the_origin_is_the_labels_centroid"]),
    ("no interpedicular lines", LINES, "out += [(\"pedicles\", lambda: pedicles(v, ped, vals)), (\"interpedicular\", lambda: interpedicular(v, ped))]",
     "out += [(\"pedicles\", lambda: pedicles(v, ped, vals))]", [FR + ".RunWithLines.test_the_keys_drawn_are_the_ones_the_lines_name"]),
]
only = sys.argv[4:]
for name, rel, old, new, tests in MUTANTS:
    if only and not any(o in name for o in only):
        continue
    d = os.path.join(WORK, name.replace(" ", "_").replace("'", ""))
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for pkg in ("morphometry", "morphoview", "scanimport", "maskedge", "schwingcheck"):
        if os.path.isdir(os.path.join(ROOT, pkg)):
            shutil.copytree(os.path.join(ROOT, pkg), os.path.join(d, pkg), ignore=shutil.ignore_patterns("__pycache__"))
    p = os.path.join(d, rel)
    with open(p) as f:
        src = f.read()
    if src.count(old) != 1:
        print("MUTANT %-44s NOT APPLIED (%d matches)" % (name, src.count(old)), flush=True)
        continue
    with open(p, "w") as f:
        f.write(src.replace(old, new))
    r = subprocess.run([PY, "-W", "ignore", "-m", "unittest", *tests], cwd=d, env=dict(os.environ, PYTHONPATH=d),
                       capture_output=True, text=True, timeout=2400)
    tail = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    print("MUTANT %-44s %s %s" % (name, "KILLED" if r.returncode else "SURVIVED", " ".join(tail)), flush=True)
    if not r.returncode:
        pass
    else:
        first = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))][:2]
        print("       ", " | ".join(first), flush=True)
