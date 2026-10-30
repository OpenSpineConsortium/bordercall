import pickle, sys, numpy as np
r = pickle.load(open(sys.argv[1], "rb"))
v = r["vert"]
rings = v.full_rings()
print(r["cfg"], "fx fy fz", v.fx, v.fy, v.fz, "pixel", v.pixel)
print("rings", len(rings), "ap", [round(s.ap, 2) for s in rings])
print("wall", v.wall, "wall_post", v.wall_post, "wall_slope", v.wall_slope, "z0", v.wall_z0, "y0", v.wall_y0, "midline", v.midline, "xc", r["xc"])
B = v.body_pts
print("B", B.shape, "z", B[:, 2].min(), B[:, 2].max(), "y", B[:, 1].min(), B[:, 1].max())
print("loc", v.loc.shape, "idx", v.idx.shape)
