import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def sub(old, new, count=1):
    global src
    if src.count(old) != count:
        raise SystemExit("expected %d of %r, found %d" % (count, old[:70], src.count(old)))
    src = src.replace(old, new)

sub('''def read_table(path: str, study: Optional[str], column: str = "study") -> List[dict]:
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if not study or r[column] == study]
''', '''def read_table(path: str, study: Optional[str]) -> List[dict]:
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if not study or r["study"] == study]
''')
sub('''    verdict = {}
    for name, word in (("filter_kept.csv", "kept"), ("filter_dropped.csv", "dropped")) if a.filter else ():
        for r in read_table(os.path.join(a.filter, name), None, column="sample_id"):
            verdict[r["sample_id"]] = word
''', '''    verdict = {}
    for name, word in (("filter_kept.csv", "kept"), ("filter_dropped.csv", "dropped")) if a.filter else ():
        for r in read_table(held(a.filter, name), None):
            verdict[r["sample_id"]] = word
''')
sub('''    for row in json_rows(os.path.join(a.edits, "edits.jsonl")):
        if row.get("sample_id") == sample and "arm" in row:''', '''    for row in json_rows(held(a.edits, "edits.jsonl")):
        if row.get("sample_id") == sample and "arm" in row:''')
sub('''        held = tuple(np.load(path, mmap_mode="r").shape) == (view.height, view.width) if os.path.exists(path) else None
        out.append({"file": "edited/%s.npy" % name, "arm": arm, "seed": arms[arm].get("seed"),
                    "pixels_kept": "missing" if held is None else held,''', '''        same = tuple(np.load(path, mmap_mode="r").shape) == (view.height, view.width) if os.path.exists(path) else None
        out.append({"file": "edited/%s.npy" % name, "arm": arm, "seed": arms[arm].get("seed"),
                    "pixels_kept": "missing" if same is None else same,''')
sub('''    recipe = read_json(os.path.join(a.realism, "recipe.json"))
    log = os.path.join(a.realism, "manifest.jsonl")
''', '''    recipe = read_json(held(a.realism, "recipe.json"))
    log = held(a.realism, "manifest.jsonl")
''')
sub('''def json_rows(path: str) -> List[dict]:''', '''def held(folder: str, name: str) -> str:
    """The path of a record a run's folder must hold, refused where it holds none."""
    path = os.path.join(folder, name)
    if not os.path.isfile(path):
        raise SystemExit("%s holds no %s" % (folder, name))
    return path


def json_rows(path: str) -> List[dict]:''')
sub('''    if edits is not None:
        said += "; %d edits, %d holding the render's pixels, %d kept by the filter" % (
            len(edits), sum(e["pixels_kept"] is True for e in edits), sum(e["filter"] == "kept" for e in edits))
    return said
''', '''    if edits is not None:
        said += "; %d edits of the render, %d holding its pixels" % (len(edits),
                                                                     sum(e["pixels_kept"] is True for e in edits))
        if any(e["filter"] != "not given" for e in edits):
            said += ", %d kept by the filter" % sum(e["filter"] == "kept" for e in edits)
    return said
''')
open(path, "w", encoding="ascii", newline="\n").write(src)
print("ok")
