import torch, torch.nn.functional as F, numpy as np
# a 1-D line of 6 voxels along x (W), labels 0..5; sample at exact half-integers
W = 6
lab = torch.arange(W, dtype=torch.float32).reshape(1, 1, 1, 1, W)
ix = torch.tensor([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 5.49, -0.51], dtype=torch.float32)
x = (2 * ix + 1) / W - 1  # inverse of ((x + 1) W - 1) / 2
grid = torch.stack([x, torch.zeros_like(x), torch.zeros_like(x)], -1).reshape(1, 1, 1, -1, 3)
for dt in (torch.float32, torch.float64):
    out = F.grid_sample(lab.to(dt) + 1, grid.to(dt), mode="nearest", align_corners=False)
    print(dt, "ix", ix.tolist())
    print("   torch nearest label+1 (0 = off grid):", out.flatten().tolist())
print("   numpy rint:", np.rint(ix.numpy().astype(np.float64)).tolist())
