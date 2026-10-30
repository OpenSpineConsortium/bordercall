"""Mutants of commit 4086684's export, each applied to a fresh copy of the packages and the test
module run against it. Usage: mutants.py BASE OUTDIR NAME [NAME ...] (or 'list')."""
import os
import re
import shutil
import subprocess
import sys

MAIN = "morphometry/__main__.py"
LINES = "morphoview/lines.py"

ONE_STUDY_WRITES = '''    if with_lines:
        lines, frames, flags = study_lines(study, kept)
        rows += flags
        lines_path, frames_path = side_paths(out)
        write_atomic(lines, lines_path, LINE_FIELDS)
        write_atomic(frames, frames_path, FRAME_FIELDS)
    rows += study_rows(study, path, stamp)
    rows.append({"study": study, "level": "study", "key": "seconds", "value": time.time() - t0, "note": ""})
    write_atomic(rows, out)
'''

ROWS_FIRST = '''    if with_lines:
        lines, frames, flags = study_lines(study, kept)
        rows += flags
    rows += study_rows(study, path, stamp)
    rows.append({"study": study, "level": "study", "key": "seconds", "value": time.time() - t0, "note": ""})
    write_atomic(rows, out)
    if with_lines:
        lines_path, frames_path = side_paths(out)
        write_atomic(lines, lines_path, LINE_FIELDS)
        write_atomic(frames, frames_path, FRAME_FIELDS)
'''

MUTANTS = {
    "M01_rows_before_lines": [(MAIN, ONE_STUDY_WRITES, ROWS_FIRST)],
    "M02_current_ignores_side_files": [
        (MAIN, "if not os.path.exists(out) or (with_lines and not all(os.path.exists(p) for p in side_paths(out))):",
         "if not os.path.exists(out):")],
    "M03_stamp_ignores_flag": [(MAIN, "    if lines:\n        h.update(LINES_SOURCE", "    if False:\n        h.update(LINES_SOURCE")],
    "M04_stamp_constant_not_lines_py": [
        (MAIN, 'h.update(LINES_SOURCE.encode() + b"\\0" + open(os.path.join(here, LINES_SOURCE), "rb").read())',
         'h.update(b"lines")')],
    "M05_frames_of_first_vertebra": [
        (MAIN, "frames.append(frame_row(study, lv, v.frame))",
         "frames.append(frame_row(study, lv, next(iter(verts.values())).frame))")],
    "M06_swap_a_b": [(MAIN, 'out = [row("", ln.a, ln.b, float(ln.value), float(ln.measured))]',
                      'out = [row("", ln.b, ln.a, float(ln.value), float(ln.measured))]')],
    "M07_measured_written_as_value": [(MAIN, 'out = [row("", ln.a, ln.b, float(ln.value), float(ln.measured))]',
                                       'out = [row("", ln.a, ln.b, float(ln.measured), float(ln.measured))]')],
    "M08_side_reading_other_sides_info": [
        (LINES, 'for k in keys}, ped.get(name)', 'for k in keys}, ped.get("left" if name == "right" else "right")')],
    "M09_side_reading_other_sides_values": [
        (LINES, 'return {k: vals.get("%s_%s" % (k, name), NAN) for k in keys}, ped.get(name)',
         'return {k: vals.get("%s_%s" % (k, "left" if name == "right" else "right"), NAN) for k in keys}, ped.get(name)')],
    "M10_skip_extras": [(MAIN, '    out += [row(name, a, b, "", "") for name, (a, b) in ln.extra.items()]\n', '')],
    "M11_kept_not_reset_on_error": [(MAIN, 'rows, note, kept = [], "%s: %s" % (type(e).__name__, e), {}',
                                     'rows, note = [], "%s: %s" % (type(e).__name__, e)')],
    "M12_ends_in_local_frame": [(LINES, "    return list(v.points_world(np.array(local, float)))",
                                 "    return list(np.array(local, float))")],
    "M13_frames_identity": [(MAIN, 'for name, vec in (("o", f.origin), ("ex", f.ex), ("ey", f.ey), ("ez", f.ez)):',
                             'for name, vec in (("o", np.zeros(3)), ("ex", np.eye(3)[0]), ("ey", np.eye(3)[1]), ("ez", np.eye(3)[2])):')],
    "M14_frame_origin_zero": [(MAIN, '(("o", f.origin), ("ex", f.ex)', '(("o", 0 * f.origin), ("ex", f.ex)')],
    "M15_discs_checked_on_vertebra_values": [
        (MAIN, 'lambda: LN.checked(LN.discs(verts[a], verts[b]), vals))',
         'lambda: LN.checked(LN.discs(verts[a], verts[b]), kept["values"][a]))')],
    "M16_checked_on_first_levels_values": [(MAIN, '        vals = kept["values"][lv]\n',
                                            '        vals = kept["values"][sorted(kept["values"])[0]]\n')],
    "M17_drop_flags": [(MAIN, "        rows += flags\n", "")],
    "M18_join_lines_with_row_fields": [
        (MAIN, 'os.path.join(a.out, "lines.csv"), LINE_FIELDS)', 'os.path.join(a.out, "lines.csv"), FIELDS)')],
    "M19_limit_path_ignores_lines": [
        (MAIN, "chosen = [c for c in chosen if current(c, stamp, a.lines)] + [j[3] for j in jobs]",
         "chosen = [c for c in chosen if current(c, stamp)] + [j[3] for j in jobs]")],
    "M20_pedicles_read_again": [(LINES, "    out += pedicles(v, ped, vals)\n", "    out += pedicles(v)\n")],
    "M21_current_checks_lines_only": [
        (MAIN, "all(os.path.exists(p) for p in side_paths(out))", "all(os.path.exists(p) for p in side_paths(out)[:1])")],
    "M22_side_files_not_atomic": [
        (MAIN, "        write_atomic(lines, lines_path, LINE_FIELDS)\n        write_atomic(frames, frames_path, FRAME_FIELDS)\n",
         "        write_rows(lines, lines_path, LINE_FIELDS)\n        write_rows(frames, frames_path, FRAME_FIELDS)\n")],
    "M23_frames_ex_ey_swapped": [(MAIN, '("ex", f.ex), ("ey", f.ey)', '("ex", f.ey), ("ey", f.ex)')],
    "M24_vertebra_values_after_rows_skip_cut_levels": [
        (MAIN, "    for lv, v in verts.items():\n        frames.append",
         "    for lv, v in verts.items():\n        if v.touching.any():\n            continue\n        frames.append")],
}


R0 = "np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])"
MUTANTS.update({
    "M25_extras_written_with_main_ends": [
        (MAIN, 'out += [row(name, a, b, "", "") for name, (a, b) in ln.extra.items()]',
         'out += [row(name, ln.a, ln.b, "", "") for name, (a, b) in ln.extra.items()]')],
    "M26_world_rotated_consistently": [
        (MAIN, '    def row(part: str, a: np.ndarray, b: np.ndarray, value: object, measured: object) -> Dict[str, object]:\n',
         '    def row(part: str, a: np.ndarray, b: np.ndarray, value: object, measured: object) -> Dict[str, object]:\n'
         '        a, b = %s @ a, %s @ b\n' % (R0, R0)),
        (MAIN, '            r[name + axis] = float(x)\n', '            r[name + axis] = float(x)\n'
         '    for name in ("o", "ex", "ey", "ez"):\n'
         '        v = %s @ np.array([r[name + axis] for axis in "xyz"])\n'
         '        for axis, x in zip("xyz", v):\n'
         '            r[name + axis] = float(x)\n' % R0)],
    "M30_value_written_as_measured": [(MAIN, 'out = [row("", ln.a, ln.b, float(ln.value), float(ln.measured))]',
                                       'out = [row("", ln.a, ln.b, float(ln.value), float(ln.value))]')],
})


MUTANTS.update({
    "M31_no_interpedicular_lines": [(LINES, "    out += interpedicular(v, ped)\n    return out\n", "    return out\n")],
    "M32_no_pedicle_chord_lines": [
        (LINES, '            out.append(Line("pedicle_chord_" + name, v.level, ends[1] - ends[0], a, b, "length", "axial_pedicle"))\n',
         '            pass\n')],
})


def apply(base, dest, edits):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(base, dest)
    for rel, old, new in edits:
        p = os.path.join(dest, rel)
        text = open(p).read()
        n = text.count(old)
        if n != 1:
            raise SystemExit("%s: the text to replace occurs %d times in %s" % (os.path.basename(dest), n, rel))
        open(p, "w").write(text.replace(old, new))


def run(dest, py):
    env = dict(os.environ, PYTHONPATH=dest)
    r = subprocess.run([py, "-W", "ignore", "-m", "unittest", "-v", "morphometry.tests.test_lines_export"],
                       cwd=dest, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    bad = re.findall(r"^(test_\w+) \(.*?\)(?:\n.*?)?\.\.\. (FAIL|ERROR)", out, re.M)
    bad += [(m, k) for k, m in re.findall(r"^(FAIL|ERROR): (\w+)", out, re.M)]
    names = sorted({(m, k) for m, k in bad})
    summary = re.findall(r"^(Ran \d+ tests.*|OK.*|FAILED.*)$", out, re.M)
    return names, summary, out


def main():
    base, outdir, py = sys.argv[1], sys.argv[2], sys.argv[3]
    names = sys.argv[4:]
    if names == ["list"]:
        print("\n".join(MUTANTS))
        return
    os.makedirs(outdir, exist_ok=True)
    for name in names:
        dest = os.path.join(outdir, name)
        apply(base, dest, MUTANTS[name])
        bad, summary, out = run(dest, py)
        open(os.path.join(outdir, name + ".log"), "w").write(out)
        print("%s: %s | caught by: %s" % (name, " ".join(summary),
                                         ", ".join("%s(%s)" % (m, k) for m, k in bad) or "nothing (survives)"), flush=True)


if __name__ == "__main__":
    main()
