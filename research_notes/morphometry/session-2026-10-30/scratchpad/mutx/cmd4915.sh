pkill -f run_mutants.py; sleep 1; pkill -f "morphoview.tests.test_projection" ; S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad; python3 - <<'EOF'
p = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/mut/run_mutants.py"
s = open(p).read()
old = """    got = subprocess.run([PY, "-m", "unittest"] + TESTS, cwd=dest, capture_output=True, text=True, timeout=900)
"""
new = """    # the classes that build no phantom first, the whole of both modules where they pass
    got = subprocess.run([PY, "-m", "unittest"] + QUICK, cwd=dest, capture_output=True, text=True, timeout=900)
    if got.returncode == 0:
        got = subprocess.run([PY, "-m", "unittest"] + TESTS, cwd=dest, capture_output=True, text=True, timeout=900)
"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """TESTS = ["morphoview.tests.test_shapes", "morphoview.tests.test_projection"]
"""
new = """TESTS = ["morphoview.tests.test_shapes", "morphoview.tests.test_projection"]
QUICK = ["morphoview.tests.test_shapes"] + ["morphoview.tests.test_projection." + c
                                           for c in ("FlexraysCamera", "Geometry", "Canvas", "Pieces")]
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
rm -rf $S/mut/w*/ ; ls $S/mut