"""Is parting's margin LP ever unbounded on a band built as lattice_under builds it?

A lattice of px by px by fz is pitched by theta about the frame's x axis. The pedicle's top is
the plane z = Z0 + slope*y in frame coordinates; a centre is bone where it lies below it. Frame
columns stand at rows half a pixel apart over span_y and a pixel apart over span_x; each
column's surface is read as height_run reads it (max bone z in a 1.5 px box, plus half a layer)
and the centres within SURFACE_LAYERS of it are kept as lattice_under keeps them."""
import sys, math, numpy as np
from scipy.optimize import linprog
from morphometry.pedicle import parting, SURFACE_LAYERS, SAGITTAL_SPAN_MM, MIN_PARTED

def band(px, fz, theta_deg, span_y=6.0, span_x=3.0, slope=0.0, roll_deg=0.0, Z0=0.37, phase=(0.13, 0.29, 0.41)):
    th, ro = math.radians(theta_deg), math.radians(roll_deg)
    # lattice centres in lattice coordinates, generous extent
    I = np.arange(-40, 41); J = np.arange(-40, 41); K = np.arange(-20, 21)
    ijk = np.stack(np.meshgrid(I, J, K, indexing="ij"), -1).reshape(-1, 3).astype(float)
    L = ijk * np.array([px, px, fz]) + np.array(phase) * np.array([px, px, fz])
    Rx = np.array([[1, 0, 0], [0, math.cos(th), -math.sin(th)], [0, math.sin(th), math.cos(th)]])
    Ry = np.array([[math.cos(ro), 0, math.sin(ro)], [0, 1, 0], [-math.sin(ro), 0, math.cos(ro)]])
    q = L @ (Ry @ Rx).T                      # frame coordinates
    bone = q[:, 2] < Z0 + slope * q[:, 1]
    ys = np.arange(0.0, span_y + 1e-9, 0.5 * px)
    xs = np.arange(0.0, span_x + 1e-9, px)
    cols = []
    for y in ys:
        for x in xs:
            inbox = (np.abs(q[:, 0] - x) <= 0.75 * px) & (np.abs(q[:, 1] - y) <= 0.75 * px) & bone
            if inbox.sum() < 2:
                continue
            cols.append((x, y, q[inbox, 2].max() + 0.5 * fz))
    cols = np.array(cols)
    apart = np.maximum(np.abs(q[:, :1] - cols[None, :, 0]) / (0.5 * px),
                       np.abs(q[:, 1:2] - cols[None, :, 1]) / (0.25 * px + 1e-6))
    j = np.argmin(apart, 1)
    keep = (apart[np.arange(len(q)), j] <= 1.0) & (np.abs(q[:, 2] - cols[j, 2]) <= SURFACE_LAYERS * fz)
    q, bone = q[keep], bone[keep]
    return q[:, 1], q[:, 0] - 0.5 * span_x, q[:, 2], bone, float(np.ptp(cols[:, 1])) + 0.5 * px

def raw_status(y, across, z, bone):
    F = np.column_stack([np.ones_like(y), y, across, across ** 2])
    sign = np.where(bone, -1.0, 1.0)
    res = linprog(c=[0, 0, 0, 0, -1.0], A_ub=np.column_stack([sign[:, None] * F, np.ones(len(y))]),
                  b_ub=sign * z, bounds=[(None, None)] * 5, method="highs")
    return res.status, res.success

print("1. HiGHS on a separable toy band (bone at y<0, air at y>0, no column holding both):")
y = np.array([-2., -1.5, -1., -0.5, 0.5, 1., 1.5, 2.]); z = np.zeros(8); bone = y < 0
st, ok = raw_status(y, np.zeros(8), z, bone)
print("   status", st, "success", ok, "-> parting returns", parting(y, np.zeros(8), z, bone, True))

print("\n2. Bands built as lattice_under builds them, px 0.6, fz 2.5 (thick slices), 6 x 3 mm region:")
for theta in (0, 5, 10, 20, 30, 45, 50, 60):
    for slope_deg in (0, 15):
        yb, xb, zb, bb, span = band(0.6, 2.5, theta, slope=math.tan(math.radians(slope_deg)))
        st, ok = raw_status(yb, xb, zb, bb)
        got = parting(yb, xb, zb, bb, True)
        print("   pitch %2d slope %2d: bone %3d air %3d span %.1f  LP status %d  -> b=%s margin=%s"
              % (theta, slope_deg, bb.sum(), (~bb).sum(), span, st,
                 None if got is None else "%.3f" % got["coefficients"][1],
                 None if got is None else "%.2f" % got["margin"]))

print("\n3. Same with a roll about y too (pitch 20, roll 20), px 0.6 fz 2.5, and px 0.5 fz 1.24:")
for px, fz in ((0.6, 2.5), (0.5, 1.24)):
    yb, xb, zb, bb, span = band(px, fz, 20, roll_deg=20)
    st, ok = raw_status(yb, xb, zb, bb)
    print("   px %.1f fz %.2f: bone %d air %d  LP status %d" % (px, fz, bb.sum(), (~bb).sum(), st))

print("\n4. The proposed fix on the separable toy band: cap t and read b (the climb):")
F = np.column_stack([np.ones_like(y), y, np.zeros(8), np.zeros(8)])
sign = np.where(bone, -1.0, 1.0)
for cap in (1.0, 3.75):
    res = linprog(c=[0, 0, 0, 0, -1.0], A_ub=np.column_stack([sign[:, None] * F, np.ones(8)]),
                  b_ub=sign * z, bounds=[(None, None)] * 4 + [(None, cap)], method="highs")
    print("   cap %.2f: status %d margin %.2f b=%.3f (climb %.1f deg) -- any b beyond %.2f is equally optimal"
          % (cap, res.status, res.x[4], res.x[1], math.degrees(math.atan(res.x[1])), cap / 0.5))
