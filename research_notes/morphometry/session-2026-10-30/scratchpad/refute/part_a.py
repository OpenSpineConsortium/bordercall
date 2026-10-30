import numpy as np
from scipy.optimize import linprog
from morphometry import pedicle as PED

# separable in (y, x'): bone under the front rows, air under the back ones
y = np.array([0.0, 0.5, 1.0, 1.5, 4.0, 4.5, 5.0, 5.5])
across = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0])
z = np.array([9.5, 9.5, 9.5, 9.5, 10.5, 10.5, 10.5, 10.5])
bone = np.array([True] * 4 + [False] * 4)
F = np.column_stack([np.ones_like(y), y, across, across ** 2])
sign = np.where(bone, -1.0, 1.0)
res = linprog(c=[0, 0, 0, 0, -1.0], A_ub=np.column_stack([sign[:, None] * F, np.ones(len(y))]),
              b_ub=sign * z, bounds=[(None, None)] * 5, method="highs")
print("separable: status", res.status, "success", res.success, "message", res.message)
print("parting ->", PED.parting(y, across, z, bone, True))

# the same points with one bone and one air sharing (y, x'): bounded
y2 = y.copy(); y2[4] = 0.0; across2 = across.copy(); across2[4] = 0.0
print("one shared (y,x') -> ", PED.parting(y2, across2, z, bone, True))
