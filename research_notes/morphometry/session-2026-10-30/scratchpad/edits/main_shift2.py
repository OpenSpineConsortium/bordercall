import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''def edit_shift(raw: np.ndarray, edited: np.ndarray) -> Optional[List[float]]:
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
    return [shift[1], shift[0]]''', '''def edit_shift(raw: np.ndarray, edited: np.ndarray) -> Optional[List[float]]:
    """How far an edit moved the render's picture, along a row and down the image in pixels, the
    edit's place less the render's: the peak of the two images' phase correlation, as the realism
    programme reads a pair's shift (tools/realism.py, paired_metrics), refined between pixels as
    Foroosh, Zerubia and Berthod refine it (IEEE Transactions on Image Processing 11:188, 2002), by
    the share of the peak and its larger neighbour each way that the neighbour holds, which is
    the fraction itself for the sinc a moved picture's correlation is. The peak is the
    correlation's largest magnitude, turned positive, since an edit may turn the picture's
    contrast over; a picture of one grey has no shift to read."""
    x, y = (np.asarray(im, np.float64) for im in (raw, edited))
    x, y = x - x.mean(), y - y.mean()
    if not (np.abs(x).max() > 0 and np.abs(y).max() > 0):
        return None
    spectrum = np.fft.fft2(y) * np.conj(np.fft.fft2(x))
    corr = np.fft.ifft2(spectrum / (np.abs(spectrum) + 1e-12)).real
    at = np.unravel_index(int(np.argmax(np.abs(corr))), corr.shape)
    corr = corr * np.sign(corr[at])
    shift = []
    for axis, size in enumerate(corr.shape):
        k = list(at)
        k[axis] = (at[axis] - 1) % size
        before = float(corr[tuple(k)])
        k[axis] = (at[axis] + 1) % size
        after = float(corr[tuple(k)])
        top = float(corr[at])
        if after >= before and after > 0:
            frac = after / (after + top)
        elif before > 0:
            frac = -before / (before + top)
        else:
            frac = 0.0
        p = at[axis] + frac
        shift.append(p - size if p > size / 2.0 else p)
    return [shift[1], shift[0]]''')
open(path, "w", encoding="ascii").write(src)

t = sys.argv[2]
src = open(t, encoding="ascii").read()
swap('''        for edit, want, within in zip(rec["edits"], ([3.0, -2.0], [1.5, 0.25]), (0.05, 0.2)):''', '''        for edit, want, within in zip(rec["edits"], ([3.0, -2.0], [1.5, 0.25]), (0.02, 0.02)):''')
swap('''    def test_an_edits_shift_is_read_on_any_side_and_none_on_one_grey(self):
        rng = np.random.default_rng(9)
        picture = ndimage.gaussian_filter(rng.normal(size=(96, 160)), 3.0)
        for rows, cols in ((0, 0), (5, -7), (-40, 70)):
            np.testing.assert_allclose(MV.edit_shift(picture, np.roll(picture, (rows, cols), axis=(0, 1))), [cols, rows],
                                       atol=1e-6)''', '''    def test_an_edits_shift_is_read_on_any_side_and_none_on_one_grey(self):
        rng = np.random.default_rng(9)
        picture = ndimage.gaussian_filter(rng.normal(size=(96, 160)), 3.0)
        for rows, cols in ((0, 0), (5, -7), (-40, 70), (0.3, -0.8), (-12.7, 4.45)):
            moved = np.fft.ifft2(ndimage.fourier_shift(np.fft.fft2(picture), (rows, cols))).real
            for edit in (moved, 2.0 - 3.0 * moved):
                np.testing.assert_allclose(MV.edit_shift(picture, edit), [cols, rows], atol=1e-3)''')
open(t, "w", encoding="ascii").write(src)
print("ok")
