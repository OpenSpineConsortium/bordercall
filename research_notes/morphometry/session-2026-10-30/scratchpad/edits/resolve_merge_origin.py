"""Resolve the trial merge of origin/main into the branch with the working tree's fixes."""
import re
from pathlib import Path


def sides(text):
    """The one conflict of a file: (before, ours, theirs, after)."""
    m = re.search(r"^<<<<<<< HEAD\n(.*?)^=======\n(.*?)^>>>>>>> origin/main\n", text, re.S | re.M)
    assert m and text.count("<<<<<<< ") == 1
    return text[:m.start()], m.group(1), m.group(2), text[m.end():]


# gate.sh: our two RERUNS with their comments, and main's TOTALSEG_RERUNS with its comment; main's
# COVARIATES_RERUNS="" and its "no check across reports yet" sentence are what our check replaced.
p = Path("grid/gate.sh")
before, ours, theirs, after = sides(p.read_text(encoding="utf-8"))
keep = theirs[theirs.index("# The owner's word for one more totalseg complete job"):]
assert keep.rstrip("\n").endswith('TOTALSEG_RERUNS="complete:40882547"')
p.write_text(before + ours + keep + after, encoding="utf-8")

# the fake hpcworker: one env line holding both sides' names
p = Path("tests/fakes/hpcworker")
before, ours, theirs, after = sides(p.read_text(encoding="utf-8"))
extra = theirs.split("CENSUS_COMMIT=${CENSUS_COMMIT:-}", 1)[1].rstrip("\n")
assert ours.rstrip("\n").endswith('CENSUS_COMMIT=${CENSUS_COMMIT:-}"') and extra.endswith('"')
p.write_text(before + ours.rstrip("\n")[:-1] + extra + "\n" + after, encoding="utf-8")

# grid/README.md: main's totalseg row, our two morphometry rows
p = Path("grid/README.md")
before, ours, theirs, after = sides(p.read_text(encoding="utf-8"))
o, t = ours.splitlines(keepends=True), theirs.splitlines(keepends=True)
assert len(o) == len(t) == 3 and t[0].startswith("| `totalseg complete` |") and o[1].startswith("| `morphometry <set>` |")
p.write_text(before + t[0] + o[1] + o[2] + after, encoding="utf-8")
print("resolved")
