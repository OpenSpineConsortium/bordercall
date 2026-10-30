import os, pickle, sys
import numpy as np
cache = sys.argv[1]
worst = 0.0
for f in sorted(os.listdir(cache))[::7]:
    v = pickle.load(open(os.path.join(cache, f), "rb"))["vert"]
    q = v.frame.local(v.grid.world(v.idx.astype(float)))
    worst = max(worst, float(np.abs(q - v.loc).max()))
print("max |loc - frame.local(world(idx))| =", worst)
