import sys
path = sys.argv[1]
src = open(path).read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:70], src.count(old))
    src = src.replace(old, new)

swap('''    """The lines of every measure the study's rows hold, on the vertebrae measure_volume built
    and checked against the values it wrote (morphoview.lines.checked), the vertebrae's frames,
    and a flag row for a level whose lines could not be built, so that a failure of the drawing
    loses no row of the measuring."""
    from morphoview import lines as LN
    lines, frames, flags = [], [], []
    verts = kept.get("verts", {})

    def build(level: str, make) -> None:
        try:
            for ln in make():
                lines.extend(line_rows(study, ln))
        except Exception as e:                  # the drawing of one level must not lose the others
            flags.append({"study": study, "level": level, "key": "flag:lines", "value": "",
                          "note": "%s: %s" % (type(e).__name__, e)})

    for lv, v in verts.items():
        frames.append(frame_row(study, lv, v.frame))
        vals = kept["values"][lv]
        build(lv, lambda: LN.checked(LN.vertebra_lines(v, kept["peds"][lv], vals), vals))
    for (a, b), vals in kept.get("discs", {}).items():
        build("%s-%s" % (a, b), lambda: LN.checked(LN.discs(verts[a], verts[b]), vals))
    return lines, frames, flags
''', '''    """The lines of the measures morphoview.lines draws, every one of scanimport's seven chords
    among them, on the vertebrae measure_volume built and checked against the values it wrote
    (morphoview.lines.checked), the vertebrae's frames, and a flag row naming the builder for
    each builder whose lines could not be drawn, so that a failure of the drawing loses no row of
    the measuring and no line of the other builders."""
    from morphoview import lines as LN
    lines, frames, flags = [], [], []
    verts = kept.get("verts", {})

    def build(level: str, name: str, make) -> None:
        try:
            for ln in make():
                lines.extend(line_rows(study, ln))
        except Exception as e:                  # one builder's failure must not lose the others' lines
            flags.append({"study": study, "level": level, "key": "flag:lines", "value": "",
                          "note": "%s: %s: %s" % (name, type(e).__name__, e)})

    for lv, v in verts.items():
        frames.append(frame_row(study, lv, v.frame))
        vals = kept["values"][lv]
        for name, draw in LN.vertebra_builders(v, kept["peds"][lv], vals):
            build(lv, name, lambda: LN.checked(draw(), vals))
    for (a, b), vals in kept.get("discs", {}).items():
        build("%s-%s" % (a, b), "discs", lambda: LN.checked(LN.discs(verts[a], verts[b]), vals))
    return lines, frames, flags
''')

swap('''def current(out: str, stamp: str, with_lines: bool = False) -> bool:''', '''def stamped(out: str, stamp: str) -> bool:
    """Whether a study's CSV is there and was written by the code of this stamp, error or not."""
    if not os.path.exists(out):
        return False
    with open(out, newline="") as fh:
        return any(r["key"] == "code" and r["note"] == stamp for r in csv.DictReader(fh))


def current(out: str, stamp: str, with_lines: bool = False) -> bool:''')

swap('''    of this run's list at the end, and only those. With --lines each study's lines and frames go
    under --out/lines/ and --out/frames/ and are joined as lines.csv and frames.csv."""''', '''    of this run's list at the end, and only those. With --lines each study's lines and frames go
    under --out/lines/ and --out/frames/ and are joined as lines.csv and frames.csv, of the
    studies this run's code wrote alone: a lines file carries no stamp of its own, and a run a
    dead worker cut short leaves some studies' files from older code, which rows.csv tells apart
    by each study's code row and the lines could not."""''')

swap('''    join_rows([c for c in chosen if os.path.exists(c)], os.path.join(a.out, "rows.csv"))
    if a.lines:
        lines, frames = zip(*[side_paths(c) for c in chosen]) if chosen else ((), ())
        join_rows([p for p in lines if os.path.exists(p)], os.path.join(a.out, "lines.csv"), LINE_FIELDS)
        join_rows([p for p in frames if os.path.exists(p)], os.path.join(a.out, "frames.csv"), FRAME_FIELDS)


def join_rows(paths: List[str], path: str, fields: List[str] = FIELDS) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\\n")
        w.writerow(fields)
        for name in sorted(paths):
            with open(name, newline="") as g:
                for row in list(csv.reader(g))[1:]:
                    w.writerow(row)
''', '''    join_rows([c for c in chosen if os.path.exists(c)], os.path.join(a.out, "rows.csv"))
    if a.lines:
        written = [side_paths(c) for c in chosen if stamped(c, stamp)]
        join_rows([p for p, _ in written if os.path.exists(p)], os.path.join(a.out, "lines.csv"), LINE_FIELDS)
        join_rows([p for _, p in written if os.path.exists(p)], os.path.join(a.out, "frames.csv"), FRAME_FIELDS)


def join_rows(paths: List[str], path: str, fields: List[str] = FIELDS) -> None:
    """The files' rows under one header, written whole or not at all, so a job killed while it
    joins leaves the last whole join and never a cut one."""
    tmp = path + ".part"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\\n")
        w.writerow(fields)
        for name in sorted(paths):
            with open(name, newline="") as g:
                for row in list(csv.reader(g))[1:]:
                    w.writerow(row)
    os.replace(tmp, path)
''')

swap('''                   help="also write each measure's line and each vertebra's frame (morphoview.lines)")''',
     '''                   help="also write the lines of the measures morphoview.lines draws and each vertebra's frame")''')
open(path, "w").write(src)
print("ok")
