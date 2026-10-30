import pathlib, sys
root = pathlib.Path(sys.argv[1])
tests = pathlib.Path(sys.argv[2])
path = root / "tests" / "test_gate.py"
text = path.read_text(encoding="utf-8")
anchor = "    def covariates_inputs(self, ended=(0, 0)):\n"
assert text.count(anchor) == 1
text = text.replace(anchor, tests.read_text(encoding="utf-8") + anchor)
path.write_text(text, encoding="utf-8")
print("inserted")
