"""Shapes beside the straight lines: curves, arcs and splines, planes and flat polygons, and
volumes, each in the world's millimetres of a mask's affine, as morphoview.lines' ends are, and
each carried onto a FleXray render by morphoview.projection's camera.

A curve is a polyline, open or closed. An arc, a circle and a spline are curves sampled finely
enough that no point of the true shape lies further than a tolerance from the polyline (0.05 mm
unless asked otherwise), so every curve projects the same way: a straight segment of the world is
a straight segment of the render, its ends projected, so a polyline projects exactly, and a
smooth curve within its tolerance times the magnification. A segment that runs behind the source
is cut where it reaches the source's plane, since no ray of the render passes behind the source.

A plane is a point and a unit normal, fitted to points by least squares where it is not given
(the smallest singular vector of the centred points, with its root mean square residual); its
patch is a flat polygon, a rectangle about the point unless corners are given, and a flat polygon
projects as a closed curve.

A volume is a label's voxels on its grid, the largest connected piece unless asked otherwise.
Its projection is an image on the render's detector: the length in mm each ray runs through the
volume (path_length), and the silhouette, where that length is above zero. Two samplings are
offered. The fine one walks each ray through the volume's box at most half the smallest voxel
spacing apart, which is the geometric chord to about a voxel. The FleXray one samples the ray as
nanoDRR does (nanodrr/drr/renderer.py, render: n points from the source to the detector, each
the label of its nearest voxel as grid_sample's nearest mode reads it, every point weighing the
step), so where the render's image carries a label, the volume's path_length is above zero
too, and FleXray's per-label channel is the attenuation summed over the same points.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np
from scipy import ndimage

from .projection import Camera, Projected

TOLERANCE_MM = 0.05             # how far a sampled curve may lie from the true one
NEAR = 1e-6                     # a segment is cut this far in front of the source, in mm


def unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    if not n > 0:
        raise ValueError("a direction of zero length")
    return v / n


def across(normal) -> Tuple[np.ndarray, np.ndarray]:
    """Two unit directions across a normal, right-handed with it."""
    n = unit(normal)
    seed = np.eye(3)[int(np.argmin(np.abs(n)))]
    e1 = unit(np.cross(n, seed))
    return e1, np.cross(n, e1)


# ---- curves ---------------------------------------------------------------------------------

@dataclass(frozen=True)
class Curve2D:
    """A curve on a render: its points' places (Projected.uv), depths and whether the render
    sampled each, in order; closed when its last point joins its first."""
    uv: np.ndarray
    depth: np.ndarray
    in_beam: np.ndarray
    closed: bool = False

    def length_px(self) -> float:
        pts = np.vstack([self.uv, self.uv[:1]]) if self.closed else self.uv
        return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())

    def area_px(self) -> float:
        """The area a closed curve encloses on the render, by the shoelace rule."""
        u, v = self.uv[:, 0], self.uv[:, 1]
        return 0.5 * abs(float(np.dot(u, np.roll(v, -1)) - np.dot(v, np.roll(u, -1))))


@dataclass(frozen=True)
class Curve:
    """A polyline in the world, open or closed."""
    points: np.ndarray
    closed: bool = False

    def __post_init__(self):
        pts = np.atleast_2d(np.asarray(self.points, float))
        if pts.ndim != 2 or pts.shape[1] != 3 or len(pts) < 2:
            raise ValueError("a curve is two or more points in three dimensions")
        object.__setattr__(self, "points", pts)

    def segments(self) -> np.ndarray:
        pts = np.vstack([self.points, self.points[:1]]) if self.closed else self.points
        return np.stack([pts[:-1], pts[1:]], axis=1)

    def length(self) -> float:
        seg = self.segments()
        return float(np.linalg.norm(seg[:, 1] - seg[:, 0], axis=1).sum())

    def resampled(self, step: float) -> "Curve":
        """The curve with points every `step` mm of its length, its corners kept, so the polyline
        is the same."""
        out = []
        for a, b in self.segments():
            n = max(1, int(math.ceil(float(np.linalg.norm(b - a)) / step)))
            out.append(a + np.linspace(0.0, 1.0, n, endpoint=False)[:, None] * (b - a))
        if not self.closed:
            out.append(self.points[-1:])
        return Curve(np.vstack(out), self.closed)

    def project(self, camera: Camera) -> Curve2D:
        """The curve on the render: each segment cut where it runs behind the source, then its
        points projected; a closed curve cut so stays closed only where nothing was cut."""
        pts, cut = in_front(self.segments(), camera, closed=self.closed)
        got = camera.project(pts)
        return Curve2D(got.uv, got.depth, got.in_beam, self.closed and not cut)


def in_front(segments: np.ndarray, camera: Camera, closed: bool) -> Tuple[np.ndarray, bool]:
    """A polyline's points with each segment cut to the part in front of the source's plane, in
    order, and whether anything was cut. Parallel rays reach behind nothing they render, so under
    them the points stand as they are."""
    if camera.view.orthographic:
        pts = segments[:, 0] if closed else np.vstack([segments[:, 0], segments[-1:, 1]])
        return pts, False
    out, cut = [], False
    for a, b in segments:
        za, zb = camera.camera_points(np.stack([a, b]))[:, 2]
        if za <= NEAR and zb <= NEAR:
            cut = True
            continue
        if za <= NEAR or zb <= NEAR:
            cut = True
            t = (NEAR - za) / (zb - za)
            p = a + t * (b - a)
            a, b = (p, b) if za <= NEAR else (a, p)
        if not out or not np.array_equal(out[-1], a):
            out.append(a)
        out.append(b)
    if closed and not cut and len(out) > 1:
        out = out[:-1]
    if not out:
        raise ValueError("the curve lies wholly behind the source")
    return np.stack(out), cut


def segments_needed(radius: float, angle: float, tolerance: float) -> int:
    """How many chords an arc of `radius` and `angle` radians needs so that none lies further
    than `tolerance` from it: a chord's sagitta is r (1 - cos(t / 2))."""
    if tolerance >= radius:
        return max(1, int(math.ceil(abs(angle) / math.pi)))
    step = 2.0 * math.acos(1.0 - tolerance / radius)
    return max(1, int(math.ceil(abs(angle) / step)))


def arc(centre, normal, start, angle_deg: float, tolerance: float = TOLERANCE_MM) -> Curve:
    """The arc about `centre` in the plane of `normal`, from `start`'s place in that plane,
    turning `angle_deg` the right-handed way about the normal; open."""
    centre, n = np.asarray(centre, float), unit(normal)
    r0 = np.asarray(start, float) - centre
    r0 = r0 - (r0 @ n) * n
    radius = float(np.linalg.norm(r0))
    if not radius > 0:
        raise ValueError("an arc's start lies on its axis")
    e1 = r0 / radius
    e2 = np.cross(n, e1)
    angle = math.radians(angle_deg)
    t = np.linspace(0.0, angle, segments_needed(radius, angle, tolerance) + 1)
    return Curve(centre + radius * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2))


def circle(centre, normal, radius: float, tolerance: float = TOLERANCE_MM) -> Curve:
    """The circle of `radius` about `centre` in the plane of `normal`, closed."""
    centre, n = np.asarray(centre, float), unit(normal)
    e1, e2 = across(n)
    k = max(3, segments_needed(radius, 2.0 * math.pi, tolerance))
    t = np.linspace(0.0, 2.0 * math.pi, k, endpoint=False)
    return Curve(centre + radius * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2), closed=True)


def spline(points, closed: bool = False, tolerance: float = TOLERANCE_MM) -> Curve:
    """The centripetal Catmull-Rom spline through the points, which passes through every one and
    neither loops nor overshoots between them, each span sampled until halving its step moves no
    sample point by more than the tolerance."""
    pts = np.atleast_2d(np.asarray(points, float))
    if len(pts) < 2:
        raise ValueError("a spline needs two or more points")
    if closed:
        ext = np.vstack([pts[-1:], pts, pts[:2]])
        spans = len(pts)
    else:
        ext = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
        spans = len(pts) - 1
    out = []
    for i in range(spans):
        p = ext[i:i + 4]
        out.append(span_samples(p, tolerance))
    if not closed:
        out.append(pts[-1:])
    return Curve(np.vstack(out), closed)


def span_samples(p: np.ndarray, tolerance: float) -> np.ndarray:
    """One span of the spline from p[1] to p[2], its last point left to the next span."""
    n = 4
    while True:
        fine = catmull_rom(p, np.linspace(0.0, 1.0, 2 * n + 1))
        coarse = fine[::2]
        mid = 0.5 * (coarse[:-1] + coarse[1:])
        if float(np.linalg.norm(fine[1::2] - mid, axis=1).max()) <= tolerance or n >= 4096:
            return coarse[:-1]
        n *= 2


def catmull_rom(p: np.ndarray, s: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Points of the centripetal (alpha 1/2) Catmull-Rom span between p[1] and p[2] at s in 0 to 1,
    by the Barry and Goldman pyramid."""
    d = np.linalg.norm(np.diff(p, axis=0), axis=1)
    d = np.where(d > 0, d, 1e-12) ** alpha
    t = np.concatenate([[0.0], np.cumsum(d)])
    tt = (t[1] + s * (t[2] - t[1]))[:, None]

    def lerp(a, b, ta, tb):
        return ((tb - tt) * a + (tt - ta) * b) / (tb - ta)

    a1, a2, a3 = lerp(p[0], p[1], t[0], t[1]), lerp(p[1], p[2], t[1], t[2]), lerp(p[2], p[3], t[2], t[3])
    b1, b2 = lerp(a1, a2, t[0], t[2]), lerp(a2, a3, t[1], t[3])
    return lerp(b1, b2, t[1], t[2])


# ---- planes ---------------------------------------------------------------------------------

@dataclass(frozen=True)
class Plane:
    """A plane through `point` with the unit `normal`."""
    point: np.ndarray
    normal: np.ndarray

    def __post_init__(self):
        object.__setattr__(self, "point", np.asarray(self.point, float))
        object.__setattr__(self, "normal", unit(self.normal))

    @classmethod
    def fit(cls, points) -> Tuple["Plane", float]:
        """The least-squares plane through three or more points and its root mean square residual
        in mm."""
        pts = np.atleast_2d(np.asarray(points, float))
        if len(pts) < 3:
            raise ValueError("a plane needs three or more points")
        centre = pts.mean(axis=0)
        _, sv, vt = np.linalg.svd(pts - centre, full_matrices=False)
        if len(sv) < 3 or not sv[1] > 0:
            raise ValueError("the points lie on one line")
        return cls(centre, vt[2]), float(sv[2] / math.sqrt(len(pts))) if len(sv) > 2 else 0.0

    def distance(self, points) -> np.ndarray:
        """Each point's signed distance from the plane, positive on the normal's side."""
        return (np.atleast_2d(np.asarray(points, float)) - self.point) @ self.normal

    def angle_deg(self, other: "Plane") -> float:
        """The angle between the two planes, 0 to 90 degrees."""
        c = min(1.0, abs(float(self.normal @ other.normal)))
        return math.degrees(math.acos(c))

    def meet(self, a, b) -> Optional[np.ndarray]:
        """Where the line through a and b meets the plane, or None where it runs parallel."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        den = float((b - a) @ self.normal)
        if abs(den) < 1e-12:
            return None
        return a + float((self.point - a) @ self.normal) / den * (b - a)

    def patch(self, half_a: float, half_b: float, toward=None) -> "Polygon":
        """The rectangle of half sides half_a and half_b about the point, its first side along the
        part of `toward` that lies in the plane where `toward` is given."""
        if toward is not None:
            t = np.asarray(toward, float)
            e1 = unit(t - (t @ self.normal) * self.normal)
            e2 = np.cross(self.normal, e1)
        else:
            e1, e2 = across(self.normal)
        corners = [self.point + sa * half_a * e1 + sb * half_b * e2 for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        return Polygon(np.stack(corners))


@dataclass(frozen=True)
class Polygon:
    """A flat polygon in the world, its corners in order."""
    corners: np.ndarray

    def __post_init__(self):
        pts = np.atleast_2d(np.asarray(self.corners, float))
        if pts.shape[1] != 3 or len(pts) < 3:
            raise ValueError("a polygon is three or more corners in three dimensions")
        object.__setattr__(self, "corners", pts)

    def plane(self) -> Plane:
        return Plane.fit(self.corners)[0]

    def area(self) -> float:
        """The area in mm2, half the length of the sum of the corners' cross products."""
        c = self.corners - self.corners.mean(axis=0)
        return 0.5 * float(np.linalg.norm(np.cross(c, np.roll(c, -1, axis=0)).sum(axis=0)))

    def outline(self) -> Curve:
        return Curve(self.corners, closed=True)

    def project(self, camera: Camera) -> Curve2D:
        return self.outline().project(camera)


# ---- volumes --------------------------------------------------------------------------------

@dataclass(frozen=True)
class Volume:
    """A set of voxels on a grid: mask[i, j, k] on the voxel whose centre the affine puts in the
    world."""
    mask: np.ndarray
    affine: np.ndarray

    def __post_init__(self):
        object.__setattr__(self, "mask", np.asarray(self.mask, bool))
        object.__setattr__(self, "affine", np.asarray(self.affine, float))
        if not self.mask.any():
            raise ValueError("a volume of no voxels")

    @classmethod
    def from_labels(cls, labels: np.ndarray, affine: np.ndarray, value: int, largest: bool = True) -> "Volume":
        """The voxels of one label value, its largest face-connected piece alone where `largest`."""
        mask = np.asarray(labels) == value
        if largest and mask.any():
            parts, n = ndimage.label(mask)
            if n > 1:
                sizes = np.bincount(parts.ravel())
                sizes[0] = 0
                mask = parts == int(np.argmax(sizes))
        return cls(mask, affine)

    @property
    def spacing(self) -> np.ndarray:
        return np.linalg.norm(self.affine[:3, :3], axis=0)

    def points(self) -> np.ndarray:
        idx = np.argwhere(self.mask).astype(float)
        return idx @ self.affine[:3, :3].T + self.affine[:3, 3]

    def centroid(self) -> np.ndarray:
        return self.points().mean(axis=0)

    def volume_mm3(self) -> float:
        return float(self.mask.sum()) * abs(float(np.linalg.det(self.affine[:3, :3])))

    def box(self) -> Tuple[np.ndarray, np.ndarray]:
        """The voxel box the volume fills, from the low faces of its lowest voxels to the high faces
        of its highest, in voxel coordinates."""
        idx = np.argwhere(self.mask)
        return idx.min(axis=0) - 0.5, idx.max(axis=0) + 0.5

    def corners(self) -> np.ndarray:
        """The box's eight corners in the world."""
        lo, hi = self.box()
        c = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        return c @ self.affine[:3, :3].T + self.affine[:3, 3]

    def footprint(self, camera: Camera) -> np.ndarray:
        """The pixels (row, column) whose rays can meet the volume: the bounding rectangle of the box's
        projected corners, on the detector."""
        uv = camera.project(self.corners()).uv
        if not np.isfinite(uv).all():
            raise ValueError("the volume reaches behind the source")
        c0, r0 = np.floor(uv.min(axis=0)).astype(int)
        c1, r1 = np.ceil(uv.max(axis=0)).astype(int)
        rows = np.arange(max(r0, 0), min(r1, camera.view.height))
        cols = np.arange(max(c0, 0), min(c1, camera.view.width))
        r, c = np.meshgrid(rows, cols, indexing="ij")
        return np.stack([r.ravel(), c.ravel()], axis=1)

    def path_length(self, camera: Camera, step: Optional[float] = None, n_samples: Optional[int] = None,
                    chunk: int = 4096) -> np.ndarray:
        """The length in mm each of the render's rays runs through the volume, an image of the
        detector's size: by the fine sampling, at most `step` mm apart (half the smallest voxel
        spacing unless given) through the volume's box, or, with n_samples, by FleXray's sampling of
        the whole ray from the source to the detector."""
        out = np.zeros((camera.view.height, camera.view.width))
        pix = self.footprint(camera)
        to_voxel = np.linalg.inv(self.affine)
        lo, hi = self.box()
        for i in range(0, len(pix), chunk):
            part = pix[i:i + chunk]
            src, tgt = camera.rays(part[:, ::-1] + 0.5)
            a = src @ to_voxel[:3, :3].T + to_voxel[:3, 3]
            b = tgt @ to_voxel[:3, :3].T + to_voxel[:3, 3]
            length = np.linalg.norm(tgt - src, axis=1)
            if n_samples is not None:
                got = self.flexray_samples(a, b, length, n_samples)
            else:
                got = self.fine_samples(a, b, length, lo, hi, step or 0.5 * float(self.spacing.min()))
            out[part[:, 0], part[:, 1]] = got
        return out

    def silhouette(self, camera: Camera, **kwargs) -> np.ndarray:
        """Where the render's rays meet the volume."""
        return self.path_length(camera, **kwargs) > 0

    def inside(self, ijk: np.ndarray) -> np.ndarray:
        """Whether each voxel coordinate's nearest voxel is the volume's, rounding half to even as
        grid_sample's nearest mode does; a place off the grid is not."""
        idx = np.rint(ijk).astype(np.int64)
        shape = np.array(self.mask.shape)
        ok = np.all((idx >= 0) & (idx < shape), axis=-1)
        hit = np.zeros(idx.shape[:-1], bool)
        hit[ok] = self.mask[idx[ok][:, 0], idx[ok][:, 1], idx[ok][:, 2]]
        return hit

    def flexray_samples(self, a: np.ndarray, b: np.ndarray, length: np.ndarray, n: int) -> np.ndarray:
        """nanoDRR's sampling: n points from the source to the detector, the step the ray's length
        over n - 1, each point weighing one step where its nearest voxel is the volume's."""
        t = np.linspace(0.0, 1.0, n)
        hits = np.zeros(len(a))
        for k in range(0, n, 256):
            tk = t[k:k + 256]
            pts = a[:, None, :] + tk[None, :, None] * (b - a)[:, None, :]
            hits += self.inside(pts).sum(axis=1)
        return hits * length / (n - 1)

    def fine_samples(self, a: np.ndarray, b: np.ndarray, length: np.ndarray, lo: np.ndarray, hi: np.ndarray,
                     step: float) -> np.ndarray:
        """The chord through the volume's box, sampled at the midpoints of steps at most `step` mm
        long, each step counted where its midpoint's nearest voxel is the volume's."""
        t0, t1 = slab(a, b, lo, hi)
        span = np.clip(t1 - t0, 0.0, None) * length
        n = int(math.ceil(float(span.max(initial=0.0)) / step)) if span.size else 0
        if n == 0:
            return np.zeros(len(a))
        hits = np.zeros(len(a))
        for k in range(0, n, 256):
            s = (np.arange(k, min(n, k + 256)) + 0.5) / n
            tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
            pts = a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :]
            hits += self.inside(pts).sum(axis=1)
        return hits * span / n


def slab(a: np.ndarray, b: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Where each segment from a to b enters and leaves the box from lo to hi, as fractions of the
    segment, by the slab method; an entry after the exit means it misses."""
    d = b - a
    with np.errstate(divide="ignore", invalid="ignore"):
        ta, tb = (lo - a) / d, (hi - a) / d
    near = np.where(np.isnan(ta), -np.inf, np.minimum(ta, tb))
    far = np.where(np.isnan(tb), np.inf, np.maximum(ta, tb))
    parallel = d == 0
    outside = parallel & ((a < lo) | (a > hi))
    near = np.where(parallel, -np.inf, near)
    far = np.where(parallel, np.inf, far)
    t0 = np.clip(near.max(axis=1), 0.0, 1.0)
    t1 = np.clip(far.min(axis=1), 0.0, 1.0)
    t1 = np.where(outside.any(axis=1), t0, t1)
    return t0, t1


def project_points(points, camera: Camera) -> Projected:
    """Points of any shape onto the render, as projection.Camera.project."""
    return camera.project(np.atleast_2d(np.asarray(points, float)))
