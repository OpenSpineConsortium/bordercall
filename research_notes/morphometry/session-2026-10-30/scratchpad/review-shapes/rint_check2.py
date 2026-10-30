import torch, torch.nn.functional as F, numpy as np
# W a power of two, so the normalised coordinate and its unnormalising are exact in binary
W = 8
lab = torch.arange(W, dtype=torch.float64).reshape(1, 1, 1, 1, W)
ix = torch.tensor([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5], dtype=torch.float64)
x = (2 * ix + 1) / W - 1
back = ((x + 1) * W - 1) / 2
print("unnormalised exactly:", torch.equal(back, ix))
grid = torch.stack([x, torch.zeros_like(x), torch.zeros_like(x)], -1).reshape(1, 1, 1, -1, 3)
for dt in (torch.float32, torch.float64):
    out = F.grid_sample(lab.to(dt) + 1, grid.to(dt), mode="nearest", align_corners=False).flatten() - 1
    print(dt, "torch index (-1 = off grid):", out.tolist())
print("numpy rint index           :", np.rint(ix.numpy()).tolist())
