"""Find every cell of every table on the rendered pages and cut its image out.

    python3 layout.py            # cells.csv, cells/<table>/*.png, and the reading strips under archive/out/

For each table in tables.py the body region is read for lines of print: a line is a run of
pixel rows that carry ink, horizontal rules masked out first. The lines must match the rows
the table lists, in order and in number, or the run stops and says which table disagrees.
Within each line, a cell is a run of ink columns; gaps narrower than the table's min_gap stay
inside one cell, so "18.5 (C3)" and "46.6 (L1) +/- 1.20" are each one cell. A run that ends
left of label_x is the row's label and not a value. A value run belongs to the column whose
span, midway between neighbouring column labels on the header line, holds its centre.

The outputs. cells.csv is committed: one line per cell with its box on the page. The crops
under cells/ are committed, since the Markdown pages show them. The reading strips are not:
archive/out/provenance/strips/pass1/ holds each table in chunks of a few rows with its header,
for the first reading pass, and strips/pass2/ holds sheets of the cell crops at twice their
size, each numbered, for the second pass; overlays/ holds the pages with every box drawn, for
a person to check the boxes against the print.
"""
from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import OUT, page_path  # noqa: E402
from tables import TABLES, Table  # noqa: E402

CELLS_DIR = os.path.join(HERE, "cells")
STRIPS = os.path.join(OUT, "strips")
OVERLAYS = os.path.join(OUT, "overlays")
MARGIN = 5
INK = 140           # grey below this is ink
LINE_INK = 4        # a pixel row with less ink than this is blank: the tail of a descender, or dust
MIN_LINE_PEAK = 30  # a line whose darkest row has less ink than this is dust, not print
MAX_LINE = 46       # rows: a run of inked rows taller than this holds more than one line of print
RULE_BLUR = 8       # rows on each side of a rule that the scan blurs
CHUNK_ROWS = 8      # lines of print per first-pass strip
SHEET_CELLS = 20    # crops per second-pass sheet


@dataclass
class Cell:
    table: str
    row: int
    col: int
    row_label: str
    col_label: str
    measure: str
    level: str
    statistic: str
    fmt: str
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def name(self) -> str:
        return "r%02d_c%02d" % (self.row, self.col)

    @property
    def image(self) -> str:
        return "cells/%s/%s.png" % (self.table, self.name)


def load_page(paper: str, page: int) -> np.ndarray:
    with Image.open(page_path(paper, page)) as im:
        return np.asarray(im.convert("L"))


def runs(mask: np.ndarray, gap: int, min_ink: int = 1) -> list[tuple[int, int]]:
    """Runs of True in a 1-d mask, joined across gaps of at most `gap` Falses."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    out = []
    start = prev = int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i - prev > gap + 1:
            out.append((start, prev + 1))
            start = i
        prev = i
    out.append((start, prev + 1))
    return [(a, b) for a, b in out if b - a >= min_ink]


def mask_rules(dark: np.ndarray, width: int) -> np.ndarray:
    """Drop the pixel rows of the table's rules, and the blurred edges beside them.

    A rule's row is a quarter ink or more and, even broken into fragments by the scan, has a
    run of ink an eighth of the width long; a line of print across a narrow table can be as
    dark, but its longest run is one number. The scan blurs a rule over several rows on each
    side, so those rows go with it; print never sits that close to a rule.
    """
    heavy = np.zeros(dark.shape[0], dtype=bool)
    for y in np.flatnonzero(dark.sum(axis=1) >= width * 0.25):
        longest = max((b - a for a, b in runs(dark[y], 4)), default=0)
        heavy[y] = longest >= width * 0.12
    keep = np.ones(dark.shape[0], dtype=bool)
    for y in np.flatnonzero(heavy):
        keep[max(0, y - RULE_BLUR):y + RULE_BLUR + 1] = False
    out = dark.copy()
    out[~keep] = False
    return out


def split_tall(ink: np.ndarray, a: int, b: int) -> list[tuple[int, int]]:
    """Cut a run of inked rows too tall for one line at its faintest interior row.

    On a blurred page two lines can share a few faint rows, so a run of inked rows may hold
    two or three lines; the cut goes where the ink is least, and only where that row is well
    under half the run's darkest row, since a line's own descenders never fall that low.
    """
    if b - a <= MAX_LINE:
        return [(a, b)]
    inner = ink[a + 8:b - 8]
    y = a + 8 + int(inner.argmin())
    if ink[y] >= 0.5 * ink[a:b].max():
        return [(a, b)]
    return split_tall(ink, a, y) + split_tall(ink, y + 1, b)


def print_lines(strip: np.ndarray, y0: int, y1: int) -> list[tuple[int, int]]:
    """The lines of print between y0 and y1 of a strip of the page, as (top, bottom) rows.

    The rules are masked over the whole strip first, so a rule just outside the range still
    takes its blurred edge with it.
    """
    ink = mask_rules(strip, strip.shape[1])[y0:y1].sum(axis=1)
    lines = []
    for a, b in runs(ink >= LINE_INK, 2):
        for c, d in split_tall(ink, a, b):
            if ink[c:d].max() >= MIN_LINE_PEAK:
                lines.append((y0 + c, y0 + d))
    return lines


def ink_runs(dark: np.ndarray, y0: int, y1: int, x0: int, x1: int, gap: int) -> list[tuple[int, int]]:
    cols = mask_rules(dark[y0:y1, x0:x1], x1 - x0).sum(axis=0)
    return [(x0 + a, x0 + b) for a, b in runs(cols > 0, gap) if cols[a:b].sum() >= 12 and b - a >= 5]


def header_line(dark: np.ndarray, t: Table) -> tuple[int, int]:
    """The line of print inside the header range that carries the most ink: the column labels."""
    lines = print_lines(dark[:, t.x[0]:t.x[1]], t.header[0], t.header[1])
    if not lines:
        raise SystemExit("%s: no line of print in the header range %s" % (t.key, t.header))
    return max(lines, key=lambda ab: dark[ab[0]:ab[1], t.x[0]:t.x[1]].sum())


def header_centres(dark: np.ndarray, t: Table) -> list[int]:
    y0, y1 = header_line(dark, t)
    blobs = ink_runs(dark, y0, y1, t.x[0], t.x[1], t.min_gap)
    blobs = [(a, b) for a, b in blobs if b > t.label_x]
    return [(a + b) // 2 for a, b in blobs]


def skew_of(dark: np.ndarray, t: Table) -> float:
    """The page's tilt under the table, in rows per pixel of width, from the column labels.

    Some pages were scanned a little askew, and a tilt of twenty rows across a wide table
    smears neighbouring lines of print into one when the rows are summed straight across.
    Each label on the header line gives a point (its centre); a line through them gives the
    slope, and the body is sheared by it before its lines are sought.
    """
    y0, y1 = header_line(dark, t)
    xs, ys = [], []
    for a, b in ink_runs(dark, y0, y1, t.x[0], t.x[1], t.min_gap):
        rows = np.flatnonzero(dark[y0:y1, a:b].sum(axis=1))
        xs.append((a + b) / 2)
        ys.append(y0 + rows.mean())
    if len(xs) < 2:
        return 0.0
    x, y = np.array(xs), np.array(ys)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())


def shear(dark: np.ndarray, x0: int, slope: float) -> np.ndarray:
    """The page with each pixel column moved up by the tilt at that column, so lines run level."""
    out = dark.copy()
    for x in range(dark.shape[1]):
        shift = int(round(slope * (x - x0)))
        if shift:
            out[:, x] = np.roll(dark[:, x], -shift)
    return out


def column_edges(dark: np.ndarray, t: Table) -> list[int]:
    if t.col_edges:
        edges = list(t.col_edges)
    else:
        centres = header_centres(dark, t)
        if len(centres) != len(t.cols):
            raise SystemExit("%s: %d column labels on the header line, %d columns listed: %s"
                             % (t.key, len(centres), len(t.cols), centres))
        edges = [t.x[0]] + [(a + b) // 2 for a, b in zip(centres, centres[1:])] + [t.x[1]]
    if len(edges) != len(t.cols) + 1:
        raise SystemExit("%s: %d column edges for %d columns" % (t.key, len(edges), len(t.cols)))
    return edges


def group_lines(t: Table, lines: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Join lines of print into the rows the table lists; a row may span several lines."""
    need = sum(r.span for r in t.rows)
    if len(lines) != need:
        raise SystemExit("%s: %d lines of print in the body, %d expected from the rows listed; lines at %s"
                         % (t.key, len(lines), need, [a for a, _ in lines]))
    rows, i = [], 0
    for r in t.rows:
        rows.append((lines[i][0], lines[i + r.span - 1][1]))
        i += r.span
    return rows


def which_column(edges: list[int], centre: int) -> int | None:
    for c in range(len(edges) - 1):
        if edges[c] <= centre < edges[c + 1]:
            return c
    return None


def level(dark: np.ndarray, t: Table) -> tuple[np.ndarray, float]:
    """The page sheared level under this table, and the slope that did it."""
    slope = skew_of(dark, t)
    return (shear(dark, t.x[0], slope) if abs(slope) > 1e-4 else dark), slope


def cells_of(t: Table, dark: np.ndarray) -> list[Cell]:
    flat, slope = level(dark, t)
    edges = column_edges(flat, t)
    rows = group_lines(t, print_lines(flat[:, t.x[0]:t.x[1]], t.body[0], t.body[1]))
    cells: list[Cell] = []
    for i, (r, (y0, y1)) in enumerate(zip(t.rows, rows)):
        if r.fmt in ("section", "continuation"):
            continue
        boxes: dict[int, list[int]] = {}
        for a, b in ink_runs(flat, y0, y1, t.x[0], t.x[1], t.min_gap):
            if b <= t.label_x:
                continue
            if a < t.label_x:
                a = t.label_x + 2      # a label set close to its first value: keep the value
            c = which_column(edges, (a + b) // 2)
            if c is None:
                continue
            box = boxes.setdefault(c, [a, b])
            box[0], box[1] = min(box[0], a), max(box[1], b)
        for c, (a, b) in sorted(boxes.items()):
            col = t.cols[c]
            fmt = r.fmt or col.fmt or "num"
            statistic = r.statistic or col.statistic or ("value" if fmt == "num" else fmt)
            if fmt in ("pm", "paren"):
                statistic = "mean+sem"
            lv = r.level or col.level or ""
            # A row that names a mnemonic beside its level (a comparison table) carries the
            # measure; a row that is only a level (the facet tables) or only a specimen (the
            # specimen table) takes it from the column.
            if t.axis == "rows" and not (r.level and r.label != r.level):
                measure = col.label
            else:
                measure = r.label
            tilt = int(round(slope * ((a + b) / 2 - t.x[0])))
            cells.append(Cell(t.key, i, c, r.label, col.label, measure, lv, statistic, fmt,
                              a - MARGIN, y0 - MARGIN + tilt, b + MARGIN, y1 + MARGIN + tilt))
    return cells


def write_cells(all_cells: list[Cell]) -> None:
    with open(os.path.join(HERE, "cells.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["table", "row", "col", "row_label", "col_label", "measure", "level", "statistic",
                    "fmt", "x0", "y0", "x1", "y1", "image"])
        for c in all_cells:
            w.writerow([c.table, c.row, c.col, c.row_label, c.col_label, c.measure, c.level, c.statistic,
                        c.fmt, c.x0, c.y0, c.x1, c.y1, c.image])


def crop(page: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return page.crop(box)


def write_crops(t: Table, page: Image.Image, cells: list[Cell]) -> None:
    d = os.path.join(CELLS_DIR, t.key)
    os.makedirs(d, exist_ok=True)
    for c in cells:
        im = crop(page, (c.x0, c.y0, c.x1, c.y1)).quantize(16)
        im.save(os.path.join(d, c.name + ".png"), optimize=True)


def write_overlay(t: Table, page: Image.Image, cells: list[Cell]) -> None:
    os.makedirs(OVERLAYS, exist_ok=True)
    im = page.crop((t.x[0] - 10, t.header[0] - 10, t.x[1] + 10, t.body[1] + 10)).convert("RGB")
    draw = ImageDraw.Draw(im)
    ox, oy = t.x[0] - 10, t.header[0] - 10
    for c in cells:
        draw.rectangle((c.x0 - ox, c.y0 - oy, c.x1 - ox, c.y1 - oy), outline=(220, 0, 0), width=2)
    draw.rectangle((0, t.header[0] - oy, im.size[0] - 1, t.header[1] - oy), outline=(0, 120, 220), width=2)
    draw.line((t.label_x - ox, 0, t.label_x - ox, im.size[1]), fill=(0, 160, 0), width=2)
    im.save(os.path.join(OVERLAYS, t.key + ".png"))


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def write_pass1(t: Table, page: Image.Image, dark: np.ndarray) -> list[dict]:
    """The table in chunks of CHUNK_ROWS rows of print, the header line above each chunk.

    The chunks are cut from the page sheared level, so a tilted scan reads as straight rows.
    """
    d = os.path.join(STRIPS, "pass1")
    os.makedirs(d, exist_ok=True)
    flat, slope = level(dark, t)
    if abs(slope) > 1e-4:
        grey = np.asarray(page)
        page = Image.fromarray(shear(grey, t.x[0], slope))
    dark = flat
    edges = column_edges(dark, t)
    rows = group_lines(t, print_lines(dark[:, t.x[0]:t.x[1]], t.body[0], t.body[1]))
    header = page.crop((t.x[0], t.header[0] - MARGIN, t.x[1], t.header[1] + MARGIN))
    wide = (t.x[1] - t.x[0]) > 1700 and len(t.cols) >= 8
    halves = []
    if wide:
        mid = edges[len(t.cols) // 2]
        halves = [(t.x[0], mid), (mid - 0, t.x[1])]
    out = []
    indices = [i for i, r in enumerate(t.rows)]
    for start in range(0, len(indices), CHUNK_ROWS):
        chunk = indices[start:start + CHUNK_ROWS]
        y0 = rows[chunk[0]][0] - MARGIN
        y1 = rows[chunk[-1]][1] + MARGIN
        body = page.crop((t.x[0], y0, t.x[1], y1))
        pieces = [((0, t.x[1] - t.x[0]), "")] if not wide else [((a - t.x[0], b - t.x[0]), "ab"[k]) for k, (a, b) in enumerate(halves)]
        for (a, b), tag in pieces:
            label_w = t.label_x - t.x[0]
            if tag == "b":
                parts = [header.crop((0, 0, label_w, header.size[1])), header.crop((a, 0, b, header.size[1]))]
                bparts = [body.crop((0, 0, label_w, body.size[1])), body.crop((a, 0, b, body.size[1]))]
            else:
                parts = [header.crop((a, 0, b, header.size[1]))]
                bparts = [body.crop((a, 0, b, body.size[1]))]
            w = sum(p.size[0] for p in parts) + 20 * (len(parts) - 1)
            h = header.size[1] + body.size[1] + 12
            strip = Image.new("L", (w, h), 255)
            x = 0
            for p, bp in zip(parts, bparts):
                strip.paste(p, (x, 0))
                strip.paste(bp, (x, header.size[1] + 12))
                x += p.size[0] + 20
            name = "%s_rows%02d-%02d%s.png" % (t.key, chunk[0], chunk[-1], tag)
            strip.save(os.path.join(d, name))
            out.append({"table": t.key, "file": name, "rows": chunk, "half": tag,
                        "cols": [c.label for c in t.cols] if not tag else
                        [c.label for k, c in enumerate(t.cols) if (k < len(t.cols) // 2) == (tag == "a")]})
    return out


def write_pass2(t: Table, page: Image.Image, cells: list[Cell]) -> list[dict]:
    """Sheets of the cell crops at twice their size, numbered down the page."""
    d = os.path.join(STRIPS, "pass2")
    os.makedirs(d, exist_ok=True)
    f = font(36)
    out = []
    for s in range(0, len(cells), SHEET_CELLS):
        batch = cells[s:s + SHEET_CELLS]
        crops = [crop(page, (c.x0, c.y0, c.x1, c.y1)) for c in batch]
        crops = [im.resize((im.size[0] * 2, im.size[1] * 2), Image.LANCZOS) for im in crops]
        w = 120 + max(im.size[0] for im in crops)
        h = sum(im.size[1] + 16 for im in crops) + 16
        sheet = Image.new("L", (w, h), 255)
        draw = ImageDraw.Draw(sheet)
        y = 8
        for k, im in enumerate(crops):
            draw.text((8, y + max(0, im.size[1] // 2 - 20)), "%2d" % (k + 1), fill=0, font=f)
            sheet.paste(im, (110, y))
            y += im.size[1] + 16
        name = "%s_sheet%02d.png" % (t.key, s // SHEET_CELLS)
        sheet.save(os.path.join(d, name))
        out.append({"table": t.key, "file": name, "cells": [c.name for c in batch]})
    return out


def run(keys: list[str] | None = None) -> None:
    import json
    all_cells: list[Cell] = []
    pass1, pass2 = [], []
    for t in TABLES:
        if keys and t.key not in keys:
            continue
        dark = load_page(t.paper, t.page) < INK
        with Image.open(page_path(t.paper, t.page)) as im:
            page = im.convert("L")
        cells = cells_of(t, dark)
        print("%-14s %3d cells" % (t.key, len(cells)), file=sys.stderr)
        write_crops(t, page, cells)
        write_overlay(t, page, cells)
        pass1 += write_pass1(t, page, dark)
        pass2 += write_pass2(t, page, cells)
        all_cells += cells
    if not keys:
        write_cells(all_cells)
        with open(os.path.join(STRIPS, "pass1.json"), "w") as f:
            json.dump(pass1, f, indent=1)
        with open(os.path.join(STRIPS, "pass2.json"), "w") as f:
            json.dump(pass2, f, indent=1)


if __name__ == "__main__":
    run(sys.argv[1:] or None)
