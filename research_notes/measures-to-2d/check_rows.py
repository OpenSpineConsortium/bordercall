"""Hold the rows of README.md beside this file to their three sources.

Every row of the note rests on vocabulary.csv, on measures.md and on the engine's and project.py's
names, and a row that names a key, a section or a function that is not there is a row nobody can
check, so this script fails on any of those before a person reads the row for its sense. It checks
that the drafted rows and the keys listed as not drafted are exactly the vocabulary's keys, with none
twice and none missing; that each row's kind, units, mnemonic and definition are the vocabulary's to
the character; that each measures.md section a row's Sources line cites exists; and that every dotted
name and every upper-case constant a row names is defined in the engine's packages (morphometry,
morphoview, scanimport, from the tree --engine points at, bordercall PR 30's branch until it merges)
or in autoanatomist/project.py of this tree, a module's name, a function's, a class's, a method's,
a constant's or an attribute an instance carries (v.panjabi). It reads the sense of no row: that is a reader's work,
and the note's verification paragraph says how it was done.

    python3 research_notes/measures-to-2d/check_rows.py --engine <checkout of PR 30>
"""
from __future__ import annotations

import argparse
import ast
import collections
import csv
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
NOT_NAMES = {"e.g", "i.e", "n.r"}          # prose that looks dotted: a dot product, an abbreviation
ENGINE_PACKAGES = ("morphometry", "morphoview", "scanimport")


def defined_names(root: pathlib.Path, packages) -> set:
    """Every function, class, method and module-level constant of the packages, as module.name,
    package.module.name, Class.method and the bare constant, which is how the rows spell them."""
    names = set()
    for pkg in packages:
        for f in (root / pkg).glob("*.py"):
            names.update({f"{pkg}.{f.stem}", f.stem})
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                # an attribute an instance carries, which a row spells as v.panjabi
                if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                    names.add(f"_.{node.attr}")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    names.update({f"{pkg}.{f.stem}.{node.name}", f"{f.stem}.{node.name}"})
                    if isinstance(node, ast.ClassDef):
                        for b in node.body:
                            if isinstance(b, ast.FunctionDef):
                                names.update({f"{f.stem}.{node.name}.{b.name}", f"{node.name}.{b.name}"})
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            names.update({f"{f.stem}.{t.id}", t.id})
    return names


def sections_of(measures_md: str) -> set:
    return set(re.findall(r"^#{2,3} (\d+(?:\.\d+)?)[. ]", measures_md, re.M))


def rows_of(note: str):
    drafted = note.split("## Not drafted")[0]
    for r in re.split(r"\n### ", drafted)[1:]:
        head = r.splitlines()[0]
        m = re.match(r"(\w+) \((\w+), ([^,)]+)(?:, ([^)]+))?\)", head)
        yield m.group(1), m.group(2), m.group(3), m.group(4) or "", r


def check(engine: pathlib.Path) -> list:
    problems = []
    note = (HERE / "README.md").read_text()
    vocab = {r["key"]: r for r in csv.DictReader(open(ROOT / "research_notes/paper-tables/tools/vocabulary.csv"))}
    sections = sections_of((ROOT / "research_notes/clinical-reread/synthesis/measures.md").read_text())
    names = defined_names(engine, ENGINE_PACKAGES) | defined_names(ROOT, ("autoanatomist",))
    drafted = []
    for key, kind, units, mnemonic, row in rows_of(note):
        drafted.append(key)
        v = vocab.get(key)
        if v is None:
            problems.append(f"{key}: not in vocabulary.csv")
            continue
        if (v["kind"], v["units"], v["mnemonic"]) != (kind, units, mnemonic):
            problems.append(f"{key}: heading says {kind}, {units}, {mnemonic!r}; the vocabulary says {v['kind']}, {v['units']}, {v['mnemonic']!r}")
        definition = re.search(r"Definition \(vocabulary.csv\): (.*)", row)
        if definition is None or definition.group(1).strip() != v["definition"]:
            problems.append(f"{key}: the definition is not the vocabulary's")
        sources = re.search(r"\nSources: (.*)", row)
        if sources is None:
            problems.append(f"{key}: no Sources line")
            continue
        cited = sources.group(1).split(";")[0]
        for s in re.findall(r"(\d+\.\d+|\b\d+\b)(?= \(| ?,|;|$)", cited):
            if s not in sections:
                problems.append(f"{key}: cites measures.md section {s}, which is not there")
        for dotted in sorted(set(re.findall(r"\b([a-z_]+(?:\.[A-Za-z_]+)+)\b", row))):
            if dotted in NOT_NAMES or dotted.split(".")[-1] in ("md", "csv", "py", "json"):
                continue
            head, tail = dotted.split(".", 1)
            if dotted not in names and tail not in names and not (len(head) == 1 and f"_.{tail}" in names):
                problems.append(f"{key}: names {dotted}, which no package defines")
        for constant in sorted(set(re.findall(r"\b([A-Z][A-Z_]{3,})\b", sources.group(1)))):
            if constant not in names:
                problems.append(f"{key}: names the constant {constant}, which no package defines")
    listed = re.findall(r"^- (\w+) \(", note.split("## Not drafted")[1], re.M)
    for key, n in collections.Counter(drafted + listed).items():
        if n > 1:
            problems.append(f"{key}: appears {n} times")
    for key in sorted(set(vocab) - set(drafted) - set(listed)):
        problems.append(f"{key}: in the vocabulary, neither drafted nor listed")
    for key in sorted(set(drafted + listed) - set(vocab)):
        problems.append(f"{key}: not a vocabulary key")
    print(f"{len(drafted)} rows drafted, {len(listed)} keys listed as not drafted, {len(vocab)} keys in the vocabulary")
    return problems


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--engine", type=pathlib.Path, default=ROOT, help="a checkout holding morphometry/, morphoview/ and scanimport/ (PR 30's branch until it merges)")
    a = p.parse_args(argv)
    problems = check(a.engine.resolve())
    for line in problems:
        print(line)
    print("ok" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
