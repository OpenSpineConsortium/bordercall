import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''def edits_of(a, source: dict, view: PJ.View) -> Optional[List[dict]]:
    """The fluoroscopic edits of a realism render, where the edit run's folder is given
    (tools/realism.py, run_edit: edits.jsonl and edited/<sample>__a<arm>.npy): each arm's file, its
    seed, whether it holds the render's pixels, which the edit keeps (the lines' places on the
    render are then theirs on the edit), and, where the filter's folder is given (run_filter or
    run_keep: filter_kept.csv and filter_dropped.csv), whether FluXray's paired filter kept it."""''', '''def edits_of(a, source: dict, view: PJ.View) -> Optional[List[dict]]:
    """The fluoroscopic edits of a realism render, where the edit run's folder is given
    (tools/realism.py, run_edit: edits.jsonl and edited/<sample>__a<arm>.npy): each arm's file, its
    seed, whether it holds the render's pixels, which the edit keeps, and how far it moved the
    render's picture (edit_shift), so the lines' places on the render are theirs on the edit as
    far as that shift says; and, where the filter's folder is given (run_filter or run_keep:
    filter_kept.csv and filter_dropped.csv), whether FluXray's paired filter kept it."""''')

swap('''    out = []
    for arm in sorted(arms):
        name = "%s%s%d" % (sample, ARM_MARK, arm)
        path = os.path.join(a.edits, "edited", name + ".npy")
        same = tuple(np.load(path, mmap_mode="r").shape) == (view.height, view.width) if os.path.exists(path) else None
        out.append({"file": "edited/%s.npy" % name, "arm": arm, "seed": arms[arm].get("seed"),
                    "pixels_kept": "missing" if same is None else same,
                    "filter": verdict.get(name, "not scored") if a.filter else "not given"})
    return out''', '''    raw_path = os.path.join(a.realism, source["file"])
    raw = np.load(raw_path) if os.path.exists(raw_path) else None
    out = []
    for arm in sorted(arms):
        name = "%s%s%d" % (sample, ARM_MARK, arm)
        path = os.path.join(a.edits, "edited", name + ".npy")
        same = tuple(np.load(path, mmap_mode="r").shape) == (view.height, view.width) if os.path.exists(path) else None
        shift = edit_shift(raw, np.load(path)) if same and raw is not None else None
        out.append({"file": "edited/%s.npy" % name, "arm": arm, "seed": arms[arm].get("seed"),
                    "pixels_kept": "missing" if same is None else same, "shift_px": shift,
                    "shift_canvas_px": None if shift is None else
                    math.hypot(*shift) * PJ.canvas_geometry(view.height, view.width, a.canvas)[0],
                    "filter": verdict.get(name, "not scored") if a.filter else "not given"})
    return out


def edit_shift(raw: np.ndarray, edited: np.ndarray) -> Optional[List[float]]:
    """How far an edit moved the render's picture, along a row and down the image in pixels, the
    edit's place less the render's: the peak of the two images' phase correlation, as the realism
    programme reads a pair's shift (tools/realism.py, paired_metrics), refined between pixels by a
    parabola through the peak and its two neighbours each way. The peak is the correlation's
    largest magnitude, since an edit may turn the picture's contrast over; a picture of one grey
    has no shift to read."""
    x, y = (np.asarray(im, np.float64) for im in (raw, edited))
    x, y = x - x.mean(), y - y.mean()
    if not (np.abs(x).max() > 0 and np.abs(y).max() > 0):
        return None
    spectrum = np.fft.fft2(y) * np.conj(np.fft.fft2(x))
    peak = np.abs(np.fft.ifft2(spectrum / (np.abs(spectrum) + 1e-12)).real)
    at = np.unravel_index(int(np.argmax(peak)), peak.shape)
    shift = []
    for axis, size in enumerate(peak.shape):
        k = list(at)
        sides = []
        for step in (-1, 1):
            k[axis] = (at[axis] + step) % size
            sides.append(float(peak[tuple(k)]))
        bend = sides[0] - 2.0 * float(peak[at]) + sides[1]
        p = at[axis] + (0.5 * (sides[0] - sides[1]) / bend if bend < 0 else 0.0)
        shift.append(p - size if p > size / 2.0 else p)
    return [shift[1], shift[0]]''')

swap('''    """One line of what was carried: a line is on the render where both its ends are in the beam
    and in what the render was made of, as far as the CT's grid tells; and how many of the render's
    fluoroscopic edits hold its pixels, and were kept by the filter."""''', '''    """One line of what was carried: a line is on the render where both its ends are in the beam
    and in what the render was made of, as far as the CT's grid tells; and how many of the render's
    fluoroscopic edits hold its pixels, the most one moved it on FleXray's canvas, and how many the
    filter kept."""''')
swap('''        said += "; %d edits of the render, %d holding its pixels" % (len(edits),
                                                                     sum(e["pixels_kept"] is True for e in edits))
        if any(e["filter"] != "not given" for e in edits):''', '''        said += "; %d edits of the render, %d holding its pixels" % (len(edits),
                                                                     sum(e["pixels_kept"] is True for e in edits))
        moved = [e["shift_canvas_px"] for e in edits if e["shift_canvas_px"] is not None]
        if moved:
            said += ", moved %.2f px at most on FleXray's canvas" % max(moved)
        if any(e["filter"] != "not given" for e in edits):''')
open(path, "w", encoding="ascii").write(src)
print("ok")
