#!/usr/bin/env python3
"""The note's table of part C from cadaver_power.py's part_b JSONs: per table, the share named
exactly at 1, 3 and 9 bodies, its difference from the 2,000-person table, the SD of that share from
one drawn table to the next, and the precision of the 0.99 answers (the mean over the table's
draws, its SD from one draw to the next, and the worst draw). A table SD is what the note's 4-table
means are uncertain by beyond the columns: their SE from the tables alone is that SD over the
square root of the tables.

    python3 part_c_table.py seven/part_b_seven.json [more part_b JSONs] > verify/part_c_table.log
"""
import json
import sys

READINGS = {
    "observed": "the published series, ten measures, as seen",
    "kind": "the published series, ten measures, sampling error taken out twice (kept, not quoted)",
}
SEVEN = {
    "seen": "the published series, read harshly",
    "kind": "the published series, sampling error out of the shift, level by level 0",
}


def label(arm: str, settings: dict) -> str:
    if arm == "true":
        return "the generator's own table"
    kind, value = arm.split("-", 1)
    if kind == "people":
        return "%s people of the population named" % value
    if kind == "profile":
        return "another population, %s SD level by level" % value
    if kind == "shift":
        return "another population, one shift of %s SD per measure" % value
    shift = "shift %.2f, level by level %.2f, " % (settings["shift"], settings["level_by_level"])
    tl = settings.get("thoracic_lumbar")
    shift += "regions drawn apart" if tl is None else "thoracic and lumbar shifts correlated %.1f" % tl
    if kind == "seven":
        what = "the published series as they disagree, %s" % value.replace("r", "r = ", 1) if value[0] == "r" else SEVEN[value]
        return "%s (%s)" % (what, shift)
    return "%s (%s)" % (READINGS[kind], shift)


def table(path: str) -> None:
    b = json.load(open(path))
    print("%s\n" % path)
    head = "| table | tables | " + " | ".join(
        "%d bodies: exact (vs 2,000), table SD | 0.99 right, mean (table SD, worst)" % n for n in b["widths"]) + " |"
    print(head)
    print("|" + "---|" * (2 + 2 * len(b["widths"])))
    for name, by in b["arms"].items():
        arm, rule = name.split("/")
        first = by[str(b["widths"][0])]
        cells = []
        for n in b["widths"]:
            s = by[str(n)]
            cells.append("%.1f%% (%+.1f), %.1f" % (100 * s["exact"], 100 * s["minus_2000"], 100 * s["exact_table_sd"]))
            cells.append("%.2f%% (%.2f, %.2f%%)" % (
                100 * s["precision"], 100 * s["precision_table_sd"], 100 * s["precision_worst"]))
        print("| %s, %s | %d | %s |" % (label(arm, first["settings"]), rule, first["tables"], " | ".join(cells)))
    print()


def main(paths: list) -> int:
    for path in paths:
        table(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
