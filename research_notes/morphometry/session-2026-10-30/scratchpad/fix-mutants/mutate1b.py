"""The first round's mutants again, on the final tree: frame_row now takes the vertebra, so the
four frame mutants change its frame; each other mutant is the first round's replacement."""
import os, shutil, subprocess, sys

ROOT = sys.argv[1]
WORK = sys.argv[2]
PY = sys.argv[3]
FR = "morphometry.tests.test_lines_export"
FRAME = "    f = v.frame\n    r: Dict[str, object] = {\"study\": study, \"level\": level}\n"


def frame(expr):
    return FRAME.replace("f = v.frame", "f = " + expr)


MUTANTS = [
    ("frame on the column's line", "morphometry/__main__.py", FRAME,
     frame("G.frame_from(v.frame.origin, v.column_ez, v.grid.anterior()) if v.column_ez is not None else v.frame"),
     [FR + ".Frames"]),
    ("frame turned 5 degrees about x", "morphometry/__main__.py", FRAME,
     frame("G.Frame(v.frame.origin, v.frame.ex, np.cos(0.0873) * v.frame.ey + np.sin(0.0873) * v.frame.ez, "
           "np.cos(0.0873) * v.frame.ez - np.sin(0.0873) * v.frame.ey)"),
     [FR + ".Frames"]),
    ("origin at zero", "morphometry/__main__.py", FRAME,
     frame("G.Frame(0 * v.frame.origin, v.frame.ex, v.frame.ey, v.frame.ez)"), [FR + ".Frames"]),
    ("x and y reversed", "morphometry/__main__.py", FRAME,
     frame("G.Frame(v.frame.origin, -v.frame.ex, -v.frame.ey, v.frame.ez)"), [FR + ".Frames"]),
    ("rows written first", "morphometry/__main__.py",
     "        write_atomic(lines, lines_path, LINE_FIELDS)\n        write_atomic(frames, frames_path, FRAME_FIELDS)\n    rows += study_rows(study, path, stamp)\n    rows.append({\"study\": study, \"level\": \"study\", \"key\": \"seconds\", \"value\": time.time() - t0, \"note\": \"\"})\n    write_atomic(rows, out)\n",
     "    rows += study_rows(study, path, stamp)\n    rows.append({\"study\": study, \"level\": \"study\", \"key\": \"seconds\", \"value\": time.time() - t0, \"note\": \"\"})\n    write_atomic(rows, out)\n    if with_lines:\n        write_atomic(lines, lines_path, LINE_FIELDS)\n        write_atomic(frames, frames_path, FRAME_FIELDS)\n",
     [FR + ".Failing.test_a_study_cut_short_at_any_of_its_writes_is_measured_again"]),
    ("kept not reset", "morphometry/__main__.py",
     "rows, note, kept = [], \"%s: %s\" % (type(e).__name__, e), {}",
     "rows, note = [], \"%s: %s\" % (type(e).__name__, e)",
     [FR + ".Failing.test_a_study_that_fails_after_its_vertebrae_are_kept_writes_empty_lines"]),
    ("one guard for the whole level", "morphometry/__main__.py",
     "        for name, draw in LN.vertebra_builders(v, kept[\"peds\"][lv], vals):\n            build(lv, name, lambda: LN.checked(draw(), vals))\n",
     "        build(lv, \"spinous\", lambda: LN.checked(LN.vertebra_lines(v, kept[\"peds\"][lv], vals), vals))\n",
     [FR + ".Failing.test_a_builder_that_fails_is_flagged_and_loses_only_its_own_lines"]),
    ("join takes every study's files", "morphometry/__main__.py",
     "written = [side_paths(c) for c in chosen if stamped(c, stamp)]",
     "written = [side_paths(c) for c in chosen]", [FR + ".CutShort"]),
    ("join written in place", "morphometry/__main__.py",
     "    os.replace(tmp, path)\n\n\n# ---- the comparison",
     "    os.replace(tmp, path)\n    open(path + \".part\", \"w\").close()\n\n\n# ---- the comparison", [FR + ".CutShort"]),
    ("no reading again on a cut vertebra", "morphoview/lines.py",
     "if ped is None or vals is None or v.touching.any():",
     "if ped is None or vals is None:", [FR + ".SameLines"]),
    ("no h_post line", "morphoview/lines.py",
     "(\"panjabi_height\", panjabi_height), ", "", [FR + ".RunWithLines.test_every_one_of_panjabis_seven_chords_is_drawn"]),
    ("no canal lines", "morphoview/lines.py",
     "(\"panjabi_canal\", panjabi_canal),\n             ", "", [FR + ".RunWithLines.test_every_one_of_panjabis_seven_chords_is_drawn"]),
    ("h_post across the plate, not up it", "morphoview/lines.py",
     "a, b = v.points_world(np.array([from_wall(v, x, y, lo), from_wall(v, x, y, hi)]))",
     "a, b = v.points_world(np.array([from_wall(v, x - 3, y, lo), from_wall(v, x + 3, y, hi)]))", [FR + ".Frames"]),
]
only = sys.argv[4:]
for name, rel, old, new, tests in MUTANTS:
    if only and not any(o == name for o in only):
        continue
    d = os.path.join(WORK, name.replace(" ", "_").replace("'", ""))
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for pkg in ("morphometry", "morphoview", "scanimport", "maskedge", "schwingcheck"):
        if os.path.isdir(os.path.join(ROOT, pkg)):
            shutil.copytree(os.path.join(ROOT, pkg), os.path.join(d, pkg), ignore=shutil.ignore_patterns("__pycache__"))
    p = os.path.join(d, rel)
    src = open(p).read()
    if src.count(old) != 1:
        print("MUTANT %-40s NOT APPLIED (%d matches)" % (name, src.count(old)), flush=True)
        continue
    open(p, "w").write(src.replace(old, new))
    r = subprocess.run([PY, "-m", "unittest", *tests], cwd=d, env=dict(os.environ, PYTHONPATH=d),
                       capture_output=True, text=True, timeout=1800)
    tail = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    errs = [l for l in r.stderr.splitlines() if l.startswith(("ERROR:", "FAIL:"))]
    print("MUTANT %-40s %s %s" % (name, "KILLED" if r.returncode else "SURVIVED", " ".join(tail)), flush=True)
    for l in errs:
        print("        " + l, flush=True)
    shutil.rmtree(d, ignore_errors=True)
