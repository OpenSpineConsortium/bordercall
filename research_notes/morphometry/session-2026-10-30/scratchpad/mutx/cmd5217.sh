S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad; cd $S/mut && python3 - <<'EOF'
p = "run_mutants.py"
t = open(p).read()
anchor = "]\n\n\ndef copy_tree"
add = ('    ("S16 spline uniform", SHP, "def catmull_rom(p: np.ndarray, s: np.ndarray, alpha: float = 0.5)", "def catmull_rom(p: np.ndarray, s: np.ndarray, alpha: float = 0.0)"),\n'
       '    ("S17 spline chordal", SHP, "catmull_rom(p, s), 0.0, 1.0, 4, tolerance", "catmull_rom(p, s, 1.0), 0.0, 1.0, 4, tolerance"),\n')
assert t.count(anchor) == 1
t = t.replace(anchor, add + anchor)
open(p, "w").write(t)
EOF
grep -c '^    ("' run_mutants.py; cd $S/mut && python3 run_mutants.py S16 S17 2>&1 | tail -4