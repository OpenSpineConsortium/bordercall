"""Each level's distance map made once, not once a line end."""
import sys

path = sys.argv[1]
text = open(path, encoding="ascii").read()
EDITS = [
    ('''def distance_to(shadow: Optional[np.ndarray], uv: np.ndarray) -> str:
    """How far, in pixels, the pixel of a place on the render lies from the shadow: the distance
    between pixel centres, none on the shadow, empty off the detector or where no shadow is."""
    if shadow is None or not np.isfinite(uv).all():
        return ""
    r, c = int(math.floor(uv[1])), int(math.floor(uv[0]))
    if not (0 <= r < shadow.shape[0] and 0 <= c < shadow.shape[1]):
        return ""
    if not shadow.any():
        return ""
    from scipy import ndimage
    return whole(ndimage.distance_transform_edt(~shadow)[r, c])


def landing(row: dict, cam: PJ.Camera, shade: Dict[str, np.ndarray]) -> dict:
    """The line's ends and midpoint against its level's shadow, a disc's against its two
    vertebrae's together."""
    parts = [shade.get(lv) for lv in row["level"].split("-")]
    shadow = None
    if all(s is not None for s in parts):
        shadow = np.logical_or.reduce(parts)
    a, b = end_of(row, "a"), end_of(row, "b")
    out = {}
    for name, p in (("a_off_px", a), ("b_off_px", b), ("mid_off_px", None if a is None or b is None else 0.5 * (a + b))):
        out[name] = "" if p is None else distance_to(shadow, cam.project(p[None]).uv[0])
    return out
''',
     '''def distance_maps(shade: Dict[str, np.ndarray]):
    """For a line's level, how far each pixel of the render lies from the level's shadow, a disc's
    from its two vertebrae's together, in pixels between centres; None where a level has no shadow
    or an empty one. Each map is made once, since a level has many lines and a render of 1024
    pixels a map of a million."""
    from scipy import ndimage
    made: Dict[str, Optional[np.ndarray]] = {}

    def of(level: str) -> Optional[np.ndarray]:
        if level not in made:
            parts = [shade.get(lv) for lv in level.split("-")]
            shadow = np.logical_or.reduce(parts) if all(s is not None for s in parts) else None
            made[level] = ndimage.distance_transform_edt(~shadow) if shadow is not None and shadow.any() else None
        return made[level]
    return of


def distance_to(far: Optional[np.ndarray], uv: np.ndarray) -> str:
    """How far, in pixels, the pixel of a place on the render lies from the shadow whose distance
    map is `far`: the distance between pixel centres, none on the shadow, empty off the detector or
    where no shadow is."""
    if far is None or not np.isfinite(uv).all():
        return ""
    r, c = int(math.floor(uv[1])), int(math.floor(uv[0]))
    if not (0 <= r < far.shape[0] and 0 <= c < far.shape[1]):
        return ""
    return whole(far[r, c])


def landing(row: dict, cam: PJ.Camera, far) -> dict:
    """The line's ends and midpoint against its level's shadow, a disc's against its two
    vertebrae's together, far giving each level's distance map."""
    shadow = far(row["level"])
    a, b = end_of(row, "a"), end_of(row, "b")
    out = {}
    for name, p in (("a_off_px", a), ("b_off_px", b), ("mid_off_px", None if a is None or b is None else 0.5 * (a + b))):
        out[name] = "" if p is None else distance_to(shadow, cam.project(p[None]).uv[0])
    return out
'''),
    ("""    shade = shadows(mask, crop, cam, (lv for r in rows for lv in r["level"].split("-")), n_samples) if mask else None
    os.makedirs(a.out, exist_ok=True)
    out = []
    for r in rows:
        line = projected_line(r, cam, a.canvas, inside)
        if shade is not None:
            line.update(landing(r, cam, shade))""",
     """    shade = shadows(mask, crop, cam, (lv for r in rows for lv in r["level"].split("-")), n_samples) if mask else None
    far = distance_maps(shade) if shade is not None else None
    os.makedirs(a.out, exist_ok=True)
    out = []
    for r in rows:
        line = projected_line(r, cam, a.canvas, inside)
        if far is not None:
            line.update(landing(r, cam, far))"""),
]
for old, new in EDITS:
    if text.count(old) != 1:
        sys.exit("not found once: %r" % old[:80])
    text = text.replace(old, new)
open(path, "w", encoding="ascii", newline="\n").write(text)
print("__main__.py: %d edits" % len(EDITS))
