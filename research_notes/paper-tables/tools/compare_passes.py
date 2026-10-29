"""Compare two blind readings of one paper's tables, cell by cell, and say where they part.

Usage: python3 -I compare_passes.py <pass a.csv> <pass b.csv> [<earlier reading.csv>]

Two readers never word a row's or a column's label alike, so the comparison does not match
rows by their labels. Within each table it compares the multisets of (level, statistic,
value): a cell both readers read the same way matches whatever either called its row, and
what is left on either side is a cell one reader read and the other did not, or read
otherwise. Tables are matched by name with Roman numerals read as numbers. The report lists,
table by table, the counts and every cell left over, with the labels its reader gave it, so
the reconciler looks only at those on the page. An earlier reading, where one exists, is
compared with each pass the same way and counted, as a third witness.
"""

import collections
import csv
import re
import sys

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50}


def roman(token):
    total, last = 0, 0
    for ch in reversed(token):
        value = ROMAN[ch]
        total += -value if value < last else value
        last = max(last, value)
    return total


def table_key(name):
    text = name.strip().lower()
    match = re.match(r"^(table|tab\.?)\s*([ivxl]+|s?\d+)([a-z]?)\b", text)
    if match:
        number = match.group(2)
        if re.fullmatch(r"[ivxl]+", number):
            number = str(roman(number))
        return "table " + number + match.group(3)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def number_key(value):
    try:
        return "%.6g" % float(value)
    except ValueError:
        return value.strip()


def cells(path):
    by_table = collections.defaultdict(list)
    for row in csv.DictReader(open(path, newline="")):
        if not row["value"].strip():
            continue
        key = (row["level"].strip(), row["statistic"].strip(), number_key(row["value"]))
        by_table[table_key(row["table"])].append((key, row))
    return by_table


def leftover(mine, theirs):
    remaining = collections.Counter(key for key, _ in theirs)
    out = []
    for key, row in mine:
        if remaining[key]:
            remaining[key] -= 1
        else:
            out.append(row)
    return out


def label(row):
    return "p%s %s | %s | %s | %s %s %s | %s=%s (%s)" % (
        row["pdf_page"], row["row_label"], row["column_label"], row["measure_label"], row["sex"],
        row["group"], row["side"], row["statistic"], row["value"], row["level"])


def compare(a_path, b_path, earlier_path=None):
    a, b = cells(a_path), cells(b_path)
    lines, total_a, total_b, total_match = [], 0, 0, 0
    for table in sorted(set(a) | set(b)):
        only_a, only_b = leftover(a[table], b[table]), leftover(b[table], a[table])
        matched = len(a[table]) - len(only_a)
        total_a += len(a[table])
        total_b += len(b[table])
        total_match += matched
        lines.append("## %s: pass a %d cells, pass b %d, matched %d" % (table, len(a[table]), len(b[table]), matched))
        for name, rows in (("only in pass a", only_a), ("only in pass b", only_b)):
            if rows:
                lines.append("%s (%d):" % (name, len(rows)))
                lines += ["  " + label(row) for row in rows]
    head = ["# %d cells in pass a, %d in pass b, %d matched" % (total_a, total_b, total_match)]
    if earlier_path:
        earlier = cells(earlier_path)
        for name, other in (("pass a", a), ("pass b", b)):
            shared = sum(len(earlier[t]) - len(leftover(earlier[t], other.get(t, []))) for t in earlier)
            count = sum(len(rows) for rows in earlier.values())
            head.append("# earlier reading: %d cells, %d of them also in %s" % (count, shared, name))
    return "\n".join(head + lines)


def main():
    print(compare(*sys.argv[1:4]))


if __name__ == "__main__":
    main()
