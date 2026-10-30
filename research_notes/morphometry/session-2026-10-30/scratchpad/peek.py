import sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0, "/home/user/SchwingNet/tests")
import test_gold3_covariates as T
d = Path(tempfile.mkdtemp())
f = T.Fake(d)
rc = T.J.run(f.args(), off_grid=T.off_grid_fake)
lines = (f.out / "report.lines").read_text().splitlines()
print(rc, len(lines))
for l in lines:
    if not T.cell_lines([l]):
        print(l)
print(len(T.cell_lines(lines)))
shutil.rmtree(d)
