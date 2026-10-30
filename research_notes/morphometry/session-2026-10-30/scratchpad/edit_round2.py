"""Round two of the fixes: full precision for the geometry, named ends, the frame's axis."""
import sys
root = sys.argv[1]

def edit(rel, pairs):
    path = root + "/" + rel
    src = open(path).read()
    for old, new in pairs:
        assert src.count(old) == 1, (rel, old[:70], src.count(old))
        src = src.replace(old, new)
    open(path, "w").write(src)

edit("morphoview/lines.py", [
('''NAN = float("nan")
AGREE = 1e-6                    # a line's value may differ from the measured one by this share of it
ROWS_PLACES = 4                 # morphometry's rows.csv writes each value to this many decimals
''', '''NAN = float("nan")
AGREE = 1e-6                    # a line's value may differ from the measured one by this share of it
ROWS_PLACES = 4                 # morphometry's rows.csv writes each value to this many decimals

# what each line's two ends are, a first and b second, in the frame of the vertebra it is drawn in
# (a disc's, the vertebra below); x runs to the patient's right, y from the canal to the body, z up
ENDS: Dict[str, Tuple[str, str]] = {
    **{k: ("inferior", "superior") for k in ("h_ant", "h_post_inset", "h_mid", "h_post", "disc_h_ant",
                                             "disc_h_mid", "disc_h_post")},
    **{k: ("posterior", "anterior") for k in ("wedge", "body_d_mid", "endplate_depth", "endplate_lower_depth",
                                              "canal_ap_min", "canal_ap", "canal_ap_lateral_film")},
    **{k: ("left", "right") for k in ("body_w_mid", "endplate", "endplate_lower", "canal_w", "tp_span",
                                      "interpedicular", "interpedicular_max")},
    "spinous_length": ("canal", "tip"),
    **{"pedicle_w_" + s: ("medial", "lateral") for s in ("right", "left")},
    **{"pedicle_h_" + s: ("inferior", "superior") for s in ("right", "left")},
    **{"pedicle_chord_" + s: ("anterior", "posterior") for s in ("right", "left")},
}
# the further segments a line carries, by the part's name
PART_ENDS: Dict[str, Tuple[str, str]] = {"lower plate": ("posterior", "anterior"), "apex to apex": ("superior", "inferior")}
# the measures a vertebra's and a disc's lines are drawn for; every other key the rows hold has none
VERTEBRA_KEYS = tuple(k for k in ENDS if not k.startswith("disc_"))
DISC_KEYS = ("disc_h_ant", "disc_h_mid", "disc_h_post")
'''),
])

edit("morphometry/__main__.py", [
('''# the lines file: one row per measure's line (morphoview.lines), its two ends in the world's
# millimetres of the mask's affine, and one row more for each further segment a line carries
# (the wedge's lower plate, Eisenstein's apex-to-apex line), named in part, with no value of its own
LINE_FIELDS = ["study", "level", "key", "part", "rule", "panel", "value", "measured", "drawn", "status",
               "ax", "ay", "az", "bx", "by", "bz"]
# the frames file: each measured vertebra's frame, its origin and its three axes in the same world
FRAME_FIELDS = ["study", "level", "ox", "oy", "oz", "exx", "exy", "exz", "eyx", "eyy", "eyz", "ezx", "ezy", "ezz"]
''', '''# the lines file: one row per line morphoview.lines draws, its two ends in the world's millimetres
# of the mask's affine and what each end is (morphoview.lines.ENDS), and one row more for each
# further segment a line carries (the wedge's lower plate, Eisenstein's apex-to-apex line), named
# in part, with no value of its own. The ends, the construction's value and its drawn length are
# written whole, so a reader can hold a length to its ends; measured is the row's value as the
# rows write it, to four places
LINE_FIELDS = ["study", "level", "key", "part", "rule", "panel", "value", "measured", "drawn", "status",
               "a_end", "ax", "ay", "az", "b_end", "bx", "by", "bz"]
# the frames file: each measured vertebra's frame, its origin and its three axes in the same world,
# written whole; which axis its z lies along (axis_of); and the column's line its z was turned from
FRAME_FIELDS = ["study", "level", "ox", "oy", "oz", "exx", "exy", "exz", "eyx", "eyy", "eyz", "ezx", "ezy", "ezz",
                "axis", "cx", "cy", "cz"]
'''),
('''def write_rows(rows: Iterable[Dict[str, object]], path: str, fields: List[str] = FIELDS) -> None:''',
 '''def whole(v: object) -> str:
    """A float as Python writes it back to the bit; not a number as empty."""
    x = float(v)
    return repr(x) if math.isfinite(x) else ""


def write_rows(rows: Iterable[Dict[str, object]], path: str, fields: List[str] = FIELDS) -> None:'''),
('''def line_rows(study: str, ln) -> List[Dict[str, object]]:
    """A line as its row, and a row for each further segment it carries."""
    def row(part: str, a: np.ndarray, b: np.ndarray, value: object, measured: object) -> Dict[str, object]:
        return {"study": study, "level": ln.level, "key": ln.key, "part": part, "rule": ln.rule, "panel": ln.panel,
                "value": value, "measured": measured, "drawn": float(np.linalg.norm(b - a)), "status": ln.status,
                "ax": float(a[0]), "ay": float(a[1]), "az": float(a[2]),
                "bx": float(b[0]), "by": float(b[1]), "bz": float(b[2])}
    out = [row("", ln.a, ln.b, float(ln.value), float(ln.measured))]
    out += [row(name, a, b, "", "") for name, (a, b) in ln.extra.items()]
    return out


def frame_row(study: str, level: str, f: G.Frame) -> Dict[str, object]:
    r: Dict[str, object] = {"study": study, "level": level}
    for name, vec in (("o", f.origin), ("ex", f.ex), ("ey", f.ey), ("ez", f.ez)):
        for axis, x in zip("xyz", vec):
            r[name + axis] = float(x)
    return r
''', '''def line_rows(study: str, ln, ends: Dict[str, Tuple[str, str]], part_ends: Dict[str, Tuple[str, str]]
              ) -> List[Dict[str, object]]:
    """A line as its row, and a row for each further segment it carries; `ends` and `part_ends`
    say what each end is, by the line's key and by the part's name."""
    def row(part: str, a: np.ndarray, b: np.ndarray, value: object, measured: object,
            names: Tuple[str, str]) -> Dict[str, object]:
        return {"study": study, "level": ln.level, "key": ln.key, "part": part, "rule": ln.rule, "panel": ln.panel,
                "value": value, "measured": measured, "drawn": whole(np.linalg.norm(b - a)), "status": ln.status,
                "a_end": names[0], "ax": whole(a[0]), "ay": whole(a[1]), "az": whole(a[2]),
                "b_end": names[1], "bx": whole(b[0]), "by": whole(b[1]), "bz": whole(b[2])}
    out = [row("", ln.a, ln.b, whole(ln.value), float(ln.measured), ends.get(ln.key, ("", "")))]
    out += [row(name, a, b, "", "", part_ends.get(name, ("", ""))) for name, (a, b) in ln.extra.items()]
    return out


def axis_of(v) -> str:
    """Which axis the vertebra's frame has its z along (anatomy.own_axis): the end-plates'
    bisector, which the column's line within SETTLED_DEG of it stands for; one end-plate's normal,
    where one alone faces a neighbour; or the column's line through the neighbours, kept where no
    end-plate faces one, where the axis read lies more than AXIS_TURN_MAX_DEG off the line or where
    turning loses the canal, and on a vertebra the measure could not read at all."""
    if "all" in v.flags or "axis" in v.flags:
        return "column line"
    return "one plate" if "axis_one_plate" in v.flags else "bisector"


def frame_row(study: str, level: str, v) -> Dict[str, object]:
    f = v.frame
    r: Dict[str, object] = {"study": study, "level": level}
    for name, vec in (("o", f.origin), ("ex", f.ex), ("ey", f.ey), ("ez", f.ez)):
        for axis, x in zip("xyz", vec):
            r[name + axis] = whole(x)
    r["axis"] = axis_of(v)
    column = v.column_ez if v.column_ez is not None else f.ez
    for axis, x in zip("xyz", column):
        r["c" + axis] = whole(x)
    return r
'''),
('''            for ln in make():
                lines.extend(line_rows(study, ln))''', '''            for ln in make():
                lines.extend(line_rows(study, ln, LN.ENDS, LN.PART_ENDS))'''),
('''        frames.append(frame_row(study, lv, v.frame))''', '''        frames.append(frame_row(study, lv, v))'''),
])
print("ok")
