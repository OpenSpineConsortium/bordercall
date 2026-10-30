"""Write each mutant of the frame_row call at morphometry/__main__.py:165 into a copy of base."""
import os
import shutil
import sys

S = sys.argv[1]
ORIG = "        frames.append(frame_row(study, lv, v.frame))\n"
MUTANTS = {
    # the frame on the column's line, before the own_axis turn
    "m1": "        frames.append(frame_row(study, lv, G.frame_from(v.frame.origin, v.column_ez if v.column_ez is not None else v.frame.ez, v.grid.anterior())))\n",
    # y and z turned 5 degrees about x
    "m2": ("        _c, _s = np.cos(np.radians(5.0)), np.sin(np.radians(5.0))\n"
           "        frames.append(frame_row(study, lv, G.Frame(v.frame.origin, v.frame.ex, _c * v.frame.ey + _s * v.frame.ez, -_s * v.frame.ey + _c * v.frame.ez)))\n"),
    # the origin at the world's zero
    "m7": "        frames.append(frame_row(study, lv, G.Frame(np.zeros(3), v.frame.ex, v.frame.ey, v.frame.ez)))\n",
    # x to the left and y to the back
    "m8": "        frames.append(frame_row(study, lv, G.Frame(v.frame.origin, -v.frame.ex, -v.frame.ey, v.frame.ez)))\n",
    # x to the left and z down
    "m12": "        frames.append(frame_row(study, lv, G.Frame(v.frame.origin, -v.frame.ex, v.frame.ey, -v.frame.ez)))\n",
    # the origin 15 mm in front, at about the body's centre rather than the label's centroid
    "m9": "        frames.append(frame_row(study, lv, G.Frame(v.frame.origin + 15.0 * v.frame.ey, v.frame.ex, v.frame.ey, v.frame.ez)))\n",
}
for name, line in MUTANTS.items():
    dst = os.path.join(S, name)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(S, "base"), dst, ignore=shutil.ignore_patterns("__pycache__"))
    path = os.path.join(dst, "morphometry", "__main__.py")
    text = open(path).read()
    assert text.count(ORIG) == 1, name
    open(path, "w").write(text.replace(ORIG, line))
    print(name, "written")
