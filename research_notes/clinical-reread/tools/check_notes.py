"""Check the reread notes against the rules before they go into git.

Usage: python3 -I check_notes.py <notes dir> [<pdf dir>]

Every note must be ASCII with LF line ends, carry the source line and the template's headings,
and print no publisher download stamp or IP address. Where the PDF folder is given and a paper
has a text layer, no run of 13 or more consecutive words of the note may appear in the paper's
own text below the citation, so no passage of the paper is copied (the quotes the rules allow are
12 words at most).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HEADINGS = [
    "## What the paper is",
    "## Anomalies, numbering and transitional segments",
    "## Measures, each as a recipe",
    "## Level by level and at the junctions",
    "## Measurement error and reliability",
    "## Clinical pearls, indications and pitfalls",
    "## Instructions for the autonomous anatomist",
    "## For bordercall's generator and classifier",
    "## Gaps and conflicts",
]
STAMP = re.compile(r"downloaded from|ip address|ajronline", re.I)
RUN = 13


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def shingles(seq, n):
    return {tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)}


def pdf_text(pdf):
    out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
    return out.stdout


def copied_runs(note_text, paper_text):
    note_words = words(note_text)
    paper = shingles(words(paper_text), RUN)
    hits = []
    i = 0
    while i <= len(note_words) - RUN:
        if tuple(note_words[i:i + RUN]) in paper:
            j = i + RUN
            while j < len(note_words) and tuple(note_words[j - RUN + 1:j + 1]) in paper:
                j += 1
            hits.append(" ".join(note_words[i:j]))
            i = j
        else:
            i += 1
    return hits


def is_numbers(run):
    tokens = run.split()
    return sum(token.isdigit() for token in tokens) * 2 > len(tokens)


def check_note(md, pdf_dir):
    problems = []
    raw = md.read_bytes()
    if any(b > 127 for b in raw):
        problems.append("non-ASCII bytes")
    if b"\r" in raw:
        problems.append("CR line ends")
    text = raw.decode("utf-8", "replace")
    if "Source: thread" not in text:
        problems.append("no source line")
    for heading in HEADINGS:
        if heading not in text:
            problems.append("missing heading: " + heading)
    for match in STAMP.finditer(text):
        problems.append("stamp or address: " + match.group(0))
    record = md.with_suffix(".json")
    if not record.exists():
        problems.append("no structured record")
    else:
        try:
            json.loads(record.read_text())
        except ValueError as error:
            problems.append("record is not JSON: %s" % error)
    if pdf_dir:
        pdf = Path(pdf_dir) / (md.stem + ".pdf")
        if pdf.exists():
            body = text[text.find("## "):]  # the citation above it names the paper's own title
            for run in copied_runs(body, pdf_text(pdf)):
                if is_numbers(run):
                    continue  # a row of a table's values is data, not the paper's prose
                problems.append("copied run of %d words: %s" % (len(run.split()), run[:120]))
    return problems


def main():
    notes = Path(sys.argv[1])
    pdf_dir = sys.argv[2] if len(sys.argv) > 2 else None
    failed = 0
    for md in sorted(notes.glob("*.md")):
        problems = check_note(md, pdf_dir)
        if problems:
            failed += 1
            print(md.name)
            for problem in problems:
                print("  " + problem)
    print("%d notes, %d with problems" % (len(list(notes.glob("*.md"))), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
