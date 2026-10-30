"""Write one copy of the export's code per mutant of the frame_row call in study_lines, so each
can run the RunWithLines tests on its own; the base copy is the commit under review as it is."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base")
LINE = "        frames.append(frame_row(study, lv, v.frame))\n"

MUTANTS = {
    # the column line's frame, before own_axis turned z onto the end-plates' bisector
    "m1": ("        f0 = G.frame_from(v.frame.origin, v.column_ez if v.column_ez is not None else v.frame.ez,"
           " v.grid.anterior())\n"
           "        frames.append(frame_row(study, lv, f0))\n"),
    # y and z turned 5 degrees about x
    "m2": ("        import math as _m\n"
           "        c, s = _m.cos(_m.radians(5.0)), _m.sin(_m.radians(5.0))\n"
           "        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin, f.ex, c * f.ey + s * f.ez, -s * f.ey + c * f.ez)))\n"),
    # z down and x to the left, still right-handed
    "m3": ("        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin, -f.ex, f.ey, -f.ez)))\n"),
    # the origin 15 mm toward the body
    "m4": ("        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin + 15.0 * f.ey, f.ex, f.ey, f.ez)))\n"),
    # y and z turned 7.5 degrees about x
    "m5": ("        import math as _m\n"
           "        c, s = _m.cos(_m.radians(7.5)), _m.sin(_m.radians(7.5))\n"
           "        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin, f.ex, c * f.ey + s * f.ez, -s * f.ey + c * f.ez)))\n"),
    # y and z turned 9 degrees about x: past the 0.99 cosine, so this one should be caught
    "m6": ("        import math as _m\n"
           "        c, s = _m.cos(_m.radians(9.0)), _m.sin(_m.radians(9.0))\n"
           "        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin, f.ex, c * f.ey + s * f.ez, -s * f.ey + c * f.ez)))\n"),
    # the origin at the world's zero
    "m7": ("        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(0.0 * f.origin, f.ex, f.ey, f.ez)))\n"),
    # x to the left and y to the back
    "m8": ("        f = v.frame\n"
           "        frames.append(frame_row(study, lv, G.Frame(f.origin, -f.ex, -f.ey, f.ez)))\n"),
}


def copy_code(dest: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for pkg in ("morphometry", "morphoview", "scanimport"):
        shutil.copytree(os.path.join(BASE, pkg), os.path.join(dest, pkg),
                        ignore=shutil.ignore_patterns("__pycache__"))


def main() -> None:
    names = sys.argv[1:] or sorted(MUTANTS)
    for name in names:
        dest = os.path.join(HERE, name)
        copy_code(dest)
        path = os.path.join(dest, "morphometry", "__main__.py")
        text = open(path).read()
        assert text.count(LINE) == 1, "the frame_row call is not where it was"
        open(path, "w").write(text.replace(LINE, MUTANTS[name]))
        print("wrote", name)


if __name__ == "__main__":
    main()
