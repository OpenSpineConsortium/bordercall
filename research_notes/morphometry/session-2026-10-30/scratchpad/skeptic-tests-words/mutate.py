"""Apply one mutant at a time to the scratch copy, run the named tests, restore the file byte for byte.

    python3 mutate.py MUTANTS.json [NAME ...]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "sn"
TESTS = {
    "gate": ["python3", "-m", "unittest", "tests.test_gate", "-k", "morphometry", "-k", "covariates"],
    "join": ["python3", "-m", "unittest", "tests.test_gold3_covariates"],
}


def run(mutant):
    path = ROOT / mutant["file"]
    original = path.read_bytes()
    text = original.decode("utf-8")
    count = text.count(mutant["old"])
    if count != 1:
        return f"SKIP ({count} matches)"
    path.write_bytes(text.replace(mutant["old"], mutant["new"]).encode("utf-8"))
    try:
        results = []
        for suite in mutant["tests"]:
            done = subprocess.run(TESTS[suite], cwd=ROOT, capture_output=True, text=True, timeout=1200,
                                  env=dict(os.environ))
            tail = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else ""
            results.append(f"{suite}: rc={done.returncode} {tail}")
        killed = any("rc=0" not in r for r in results)
        return ("KILLED" if killed else "SURVIVED") + " | " + " ; ".join(results)
    finally:
        path.write_bytes(original)
        assert path.read_bytes() == original


def main():
    mutants = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    wanted = set(sys.argv[2:])
    for mutant in mutants:
        if wanted and mutant["name"] not in wanted:
            continue
        print(mutant["name"], "->", run(mutant), flush=True)


if __name__ == "__main__":
    main()
