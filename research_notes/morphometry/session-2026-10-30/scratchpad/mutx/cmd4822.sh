S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad; python3 - <<'EOF'
p = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/mut/run_mutants.py"
s = open(p).read()
old = """    failed = [ln for ln in got.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
"""
new = """    failed = [ln for ln in got.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
    shutil.rmtree(dest, ignore_errors=True)
"""
assert s.count(old) == 1
open(p, "w").write(s.replace(old, new))
EOF
cd $S/mut && python3 - <<'EOF'
import sys
sys.argv = ["x"]
exec(open("run_mutants.py").read().replace('if __name__ == "__main__":\n    main()', ''))
import os
for name, path, old, new in MUTANTS:
    text = open(os.path.join(SRC, path)).read()
    if text.count(old) != 1:
        print("NOT APPLIED", name, text.count(old))
print(len(MUTANTS), "mutants checked")
EOF