"""Render every page of the four Panjabi papers at 300 dpi, the images every cell box refers to.

    python3 render.py            # writes archive/out/provenance/pages/<paper>-<NN>.png and pages.json
    python3 render.py thoracic-p892   # one key only, merged into the pages.json already there

The boxes in cells.csv and provenance.csv are pixel coordinates on these images, so the
command that makes them is fixed here: poppler's pdftoppm at 300 dots per inch, one page per
call, and the two landscape pages of the thoracic paper turned clockwise by a quarter turn so
their tables read upright. pages.json records the poppler version, each image's size and its
sha256, so a later render can be checked against the one the boxes were drawn on. The renders
are not committed (archive/out/ is ignored); the cell crops under cells/ are.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS_DIR = os.path.join(HERE, "..", "papers")
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "out", "provenance"))
PAGES_DIR = os.path.join(OUT, "pages")
DPI = 300

# key -> (file name, number of pages, pages turned clockwise so they read upright)
PAPERS = {
    "cervical": ("Panjabi_1991_Cervical_Spine_16-8_861-869.pdf", 9, ()),
    "thoracic": ("Panjabi_1991_Thoracic_Spine_16-8_888-901.pdf", 13, (6, 7)),
    "lumbar": ("Panjabi_1992_Lumbar_Spine_17-3_299-306.pdf", 8, ()),
    "facets": ("Panjabi_1993_Facets_Spine_18-10_1298-1310.pdf", 13, ()),
    # printed page 892 of the thoracic paper, which the scan above lacks: one landscape page from
    # the owner's second scan of 27 October 2026, whose table already reads upright
    "thoracic-p892": ("Panjabi_1991_Thoracic_Spine_16-8_888-901_p892.pdf", 1, ()),
}


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_path(paper: str, page: int) -> str:
    return os.path.join(PAGES_DIR, "%s-%02d.png" % (paper, page))


def poppler_version() -> str:
    out = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True)
    return (out.stderr or out.stdout).strip().splitlines()[0]


def render_page(pdf: str, page: int, dest: str, turn: bool) -> None:
    prefix = dest[:-4]
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-f", str(page), "-l", str(page),
                    "-singlefile", pdf, prefix], check=True)
    if turn:
        from PIL import Image
        with Image.open(dest) as im:
            im.rotate(-90, expand=True).save(dest)


def render_all(papers=PAPERS, keys=None) -> dict:
    """Render every paper, or only the keys given, which are merged into the record already
    there, so one added page (thoracic-p892) is rendered without rendering the rest again."""
    os.makedirs(PAGES_DIR, exist_ok=True)
    record = {"dpi": DPI, "pdftoppm": poppler_version(), "papers": {}}
    if keys:
        with open(os.path.join(OUT, "pages.json"), encoding="utf-8") as f:
            record = json.load(f)
        papers = {k: v for k, v in papers.items() if k in keys}
    from PIL import Image
    for key, (name, pages, turned) in papers.items():
        pdf = os.path.join(PAPERS_DIR, name)
        record["papers"][key] = {"file": name, "sha256": sha256_of(pdf), "pages": {}}
        for page in range(1, pages + 1):
            dest = page_path(key, page)
            render_page(pdf, page, dest, page in turned)
            with Image.open(dest) as im:
                size = im.size
            record["papers"][key]["pages"][str(page)] = {
                "size": list(size), "turned": page in turned, "sha256": sha256_of(dest)}
            print(dest, size, file=sys.stderr)
    with open(os.path.join(OUT, "pages.json"), "w") as f:
        json.dump(record, f, indent=1)
    return record


if __name__ == "__main__":
    render_all(keys=sys.argv[1:] or None)
