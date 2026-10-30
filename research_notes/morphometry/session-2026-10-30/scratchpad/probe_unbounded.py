import numpy as np
from scipy.optimize import linprog
from morphometry.pedicle import parting
import scipy; print("scipy", scipy.__version__)
# the finding's input: bone and air separable by y alone
y = np.array([-12.0]*6 + [-5.0]*6); across = np.zeros(12); z = np.zeros(12)
bone = np.array([True]*6 + [False]*6)
print("separable-by-y ->", parting(y, across, z, bone, True))
F = np.column_stack([np.ones_like(y), y, across, across**2]); sign = np.where(bone, -1.0, 1.0); n = len(y)
res = linprog(c=[0,0,0,0,-1.0], A_ub=np.column_stack([sign[:,None]*F, np.ones(n)]), b_ub=sign*z, bounds=[(None,None)]*5, method="highs")
print("status", res.status, res.success, res.message)
# the realistic shape: bone and air stacked in each column, bone below -> bounded
y2 = np.repeat(np.linspace(-12,-5,6), 2); across2 = np.zeros(12); z2 = np.tile([-0.5, 0.5], 6) + 0.1*y2
bone2 = np.tile([True, False], 6)
print("bracketed ->", parting(y2, across2, z2, bone2, True))
# all bone
print("all bone ->", parting(y2, across2, z2, np.ones(12, bool), True))
# one centre per column, middle columns bone and outer columns air (parabola in x')
y3 = np.array([-10.0]*7); across3 = np.linspace(-3,3,7); z3 = np.zeros(7); bone3 = np.abs(across3) < 1.5
print("parabola-separable ->", parting(y3, across3, z3, bone3, True))
