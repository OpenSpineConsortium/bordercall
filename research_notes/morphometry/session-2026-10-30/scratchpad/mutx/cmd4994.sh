S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad; cd $S/mut && python3 - <<'EOF'
p = "run_mutants.py"
t = open(p).read()
old_tests = 'TESTS = ["morphoview.tests.test_shapes", "morphoview.tests.test_projection"]\n'
new_tests = old_tests + ('QUICK = ["morphoview.tests.test_shapes"] + ["morphoview.tests.test_projection." + c\n'
                         '                                           for c in ("FlexraysCamera", "Geometry", "Canvas", "Pieces")]\n')
assert t.count(old_tests) == 1
t = t.replace(old_tests, new_tests)
old_run = '    got = subprocess.run([PY, "-m", "unittest"] + TESTS, cwd=dest, capture_output=True, text=True, timeout=900)\n'
new_run = ('    # the classes that build no phantom first, the whole of both modules only where they pass\n'
           '    try:\n'
           '        got = subprocess.run([PY, "-m", "unittest"] + QUICK, cwd=dest, capture_output=True, text=True, timeout=900)\n'
           '        if got.returncode == 0:\n'
           '            got = subprocess.run([PY, "-m", "unittest"] + TESTS, cwd=dest, capture_output=True, text=True, timeout=900)\n'
           '    except subprocess.TimeoutExpired:\n'
           '        shutil.rmtree(dest, ignore_errors=True)\n'
           '        return name, "caught", "timed out"\n')
assert t.count(old_run) == 1
t = t.replace(old_run, new_run)
open(p, "w").write(t)
EOF
grep -n "QUICK\|TimeoutExpired" run_mutants.py; python3 -c "import ast,sys; ast.parse(open('$S/mut/run_mutants.py').read()); print('parses')"