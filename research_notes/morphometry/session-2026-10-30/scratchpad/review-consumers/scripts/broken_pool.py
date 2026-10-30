"""The new engine's run over a folder whose rows/ an older engine wrote, with one worker killed
outright, as a node's memory killer would: what rows.csv holds afterwards and how the run exits."""
import os, sys
sys.path.insert(0, sys.argv[1])
import multiprocessing
multiprocessing.set_start_method("fork", force=True)
from morphometry import measure as M
from morphometry import __main__ as MM
real = M.measure_file
def dying(path, scheme, study):
    if study == "e001":
        os._exit(9)
    return real(path, scheme, study)
M.measure_file = dying
MM.main(["run", "--masks", sys.argv[2], "--scheme", "enhance", "--out", sys.argv[3], "--workers", "1"])
print("run returned normally")
