"""The shapes mutants of the handoff, applied alone to a copy of the current tree, since shapes.py
and test_shapes.py changed after the main mutant run; the quick suites run on each."""
import concurrent.futures as cf
import importlib.util
import os
import shutil
import subprocess
import sys

SP = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad"
spec = importlib.util.spec_from_file_location("rm", os.path.join(SP, "mut", "run_mutants.py"))
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)
SRC = os.path.join(SP, "review-words", "bc")
HERE = os.path.join(SP, "review-words", "mutants")
PY = os.path.join(SP, "venv", "bin", "python")
QUICK = rm.QUICK

def run(job):
    k, (name, path, old, new) = job
    dest = os.path.join(HERE, "w%d" % k)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "research_notes"))
    target = os.path.join(dest, path)
    text = open(target).read()
    if text.count(old) != 1:
        shutil.rmtree(dest, ignore_errors=True)
        return name, "NOT APPLIED (%d matches)" % text.count(old)
    open(target, "w").write(text.replace(old, new))
    got = subprocess.run([PY, "-m", "unittest"] + QUICK, cwd=dest, capture_output=True, text=True, timeout=900)
    failed = [ln.split(" (")[0] for ln in got.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
    shutil.rmtree(dest, ignore_errors=True)
    return name, ("passed" if got.returncode == 0 else "caught") + " " + "; ".join(failed[:3])

jobs = [m for m in rm.MUTANTS if m[0].startswith(tuple(sys.argv[1:]) or ("S",))]
os.makedirs(HERE, exist_ok=True)
with cf.ProcessPoolExecutor(2) as pool:
    for name, verdict in pool.map(run, list(enumerate(jobs))):
        print("%-32s %s" % (name, verdict), flush=True)
