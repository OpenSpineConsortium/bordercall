"""Report every run of 13 or more words a file shares with any paper's text layer (not table rows of numbers)."""
import re, sys
from pathlib import Path
RUN = 13
def words(t): return re.findall(r"[a-z0-9]+", t.lower())
def is_numbers(run):
    toks = run.split(); return sum(t.isdigit() for t in toks) * 2 > len(toks)
text_dir = Path(sys.argv[1]); files = sys.argv[2:]
index = {}
for txt in sorted(text_dir.glob("*.txt")):
    w = words(txt.read_text(errors="replace"))
    for i in range(len(w) - RUN + 1):
        index.setdefault(tuple(w[i:i + RUN]), txt.stem)
bad = 0
for f in files:
    w = words(Path(f).read_text(errors="replace")); i = 0
    while i <= len(w) - RUN:
        k = tuple(w[i:i + RUN])
        if k in index:
            j = i + RUN
            while j < len(w) and tuple(w[j - RUN + 1:j + 1]) in index: j += 1
            run = " ".join(w[i:j])
            if not is_numbers(run):
                bad += 1; print("%s: %s, %d words: %s" % (f, index[k], j - i, run[:160]))
            i = j
        else: i += 1
print("runs found:", bad)
