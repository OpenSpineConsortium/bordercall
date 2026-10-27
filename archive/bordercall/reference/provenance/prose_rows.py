"""Every number the four papers state in their running text, set beside the cells it speaks of.

    python prose_rows.py         # writes prose.csv and reads/prose.csv

The entries below are the record: where the sentence is, the number as printed, the cells
of provenance.csv it speaks of and the rule that turns those cells into the number
(check_prose.py). A number that no cell can give, a bound ("less than 2 deg"), a
comparison with another study, or an approximation of an area by a formula, is kept with
no cells, so the list is complete but only what the tables carry is tested.

What each pass read is taken from the two prose-reading passes' files (README.md): an
entry is matched to a pass's record by the page, the digits and a key phrase of the
sentence, and the test holds both passes to the digits recorded here. The sign of an angle
printed as a word ("8 deg below the transverse plane") is carried in value, not in printed.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_prose  # noqa: E402
from check_prose import FIELDS  # noqa: E402
from render import OUT  # noqa: E402

READS_IN = os.path.join(OUT, "reads")
READS_KEPT = os.path.join(HERE, "reads", "prose.csv")
READ_FIELDS = ["paper", "pass", "page", "crop", "where", "quote", "measure", "levels", "value", "units",
               "statistic", "study", "note"]
C3_C7 = ["C3", "C4", "C5", "C6", "C7"]
C2_C7 = ["C2"] + C3_C7
T1_T12 = ["T%d" % i for i in range(1, 13)]
L1_L5 = ["L%d" % i for i in range(1, 6)]


def cell(table: str, measure: str, level: str, statistic: str = "mean", study: str | None = None) -> tuple:
    return (table, measure, level, statistic, study)


def lr(table: str, base: str, level: str, statistic: str = "mean") -> list[tuple]:
    return [cell(table, base + "r", level, statistic), cell(table, base + "l", level, statistic)]


def levels(table: str, measure: str, lvs: list[str], statistic: str = "mean") -> list[tuple]:
    return [cell(table, measure, lv, statistic) for lv in lvs]


def entry(paper, page, printed_page, where, key, measure, level, statistic, printed, units,
          cells=(), rule="equal", tolerance=0.05, value=None, note=""):
    return {"paper": paper, "pdf_page": page, "printed_page": printed_page, "where": where, "key": key,
            "measure": measure, "level": level, "statistic": statistic, "printed": printed,
            "value": printed if value is None else value, "units": units, "cells": list(cells),
            "rule": rule, "tolerance": tolerance, "note": note}


# All four papers measured the same twelve spines, C2 to L5, one row each in the thoracic paper's
# Table 1 (printed page 889). The cervical, lumbar and facets papers each print one summary of them
# in their Methods, 12 numbers in each, and name the thoracic paper as their specimens' record, so
# each number is held to Table 1: a count of its rows, or of the rows whose sex is M or F, and the
# mean, least and greatest of a column. The level "*" names every row of a column (resolve below).
TABLE_1 = "thoracic-t1"
ROWS = cell(TABLE_1, "Specimen No.", "*", "label")
SEX = cell(TABLE_1, "Sex", "*", "text")
# what Table 1's twelve rows give for each column the summaries describe
TABLE_1_GIVES = {"age": "the twelve ages of Table 1 average 46.33",
                 "weight": "the twelve weights of Table 1 average 67.83",
                 "height": "the twelve heights of Table 1 average 167.75"}
HEAVIEST = "Table 1's heaviest specimen, S15, weighs 84 kg, and no specimen weighs 85"


def column(name: str) -> tuple:
    return cell(TABLE_1, name, "*", "value")


def twelve(paper: str, page: int, printed_page: int) -> dict:
    return entry(paper, page, printed_page, "methods", "Twelve fresh autopsy", "specimens", "", "count", "12", "count",
                 [ROWS], "count", 0.0, note="printed as the word Twelve; the rows of Table 1, S3 to S24")


def summary(paper: str, page: int, printed_page: int, keys: tuple, ratio: str) -> list[dict]:
    """The age, weight, height and sex of the twelve spines as one later paper prints them, in its
    order: each column's mean and range, then the men and the women."""
    out = []
    for (measure, name, units, mean, low, high), key in zip(
            (("age", "Age", "years", "46.3", "19", "59"), ("weight", "Weight (kg)", "kg", "67.8", "54", "85"),
             ("height", "Height (cm)", "cm", "167.8", "157", "178")), keys):
        out += [entry(paper, page, printed_page, "methods", key, measure, "", "mean", mean, units, [column(name)], "mean",
                      0.05, note=TABLE_1_GIVES[measure]),
                entry(paper, page, printed_page, "methods", key, measure, "", "range_low", low, units, [column(name)], "low",
                      0.05),
                entry(paper, page, printed_page, "methods", key, measure, "", "range_high", high, units, [column(name)],
                      "high", 0.05, note=HEAVIEST if measure == "weight" else "")]
    for measure, printed, sex in (("males", "8", "M"), ("females", "4", "F")):
        out.append(entry(paper, page, printed_page, "methods", keys[3], measure, "", "count", printed, "count", [SEX],
                         "count:" + sex, 0.0, note="printed as the ratio %s" % ratio))
    return out


def vertebrae(paper: str, page: int, printed_page: int, key: str, printed: str, level: str, levels: str) -> dict:
    """A count of the vertebrae measured, which no table prints: the twelve spines times the levels."""
    return entry(paper, page, printed_page, "abstract", key, "vertebrae", level, "count", printed, "count",
                 note="twelve spines of %s; no table counts vertebrae" % levels)


ENTRIES = [
    # ---- cervical, Spine 1991;16(8):861-869 ------------------------------------------
    vertebrae("cervical", 1, 861, "72 human cervical vertebrae", "72", "C2-C7", "six levels, C2 to C7"),
    twelve("cervical", 1, 861),
    *summary("cervical", 1, 861, ("average age of 46.3", "weight of 67.8", "height of 167.8", "ratio of 8 to 4"),
             "of 8 to 4"),
    entry("cervical", 4, 864, "results", "elliptical approximation overestimated", "EPA by ellipse", "all levels",
          "percent_change", "10", "percent", note="an approximation of the area by a formula, not a cell"),
    entry("cervical", 4, 864, "results", "triangular approximation was", "EPA by triangle", "all levels",
          "percent_change", "40", "percent", note="an approximation of the area by a formula, not a cell"),
    entry("cervical", 4, 864, "results", "tilt of", "EPItu", "C3-C7", "range_low", "2", "deg",
          levels("cervical-t2", "EPItu", C3_C7), "low", 0.5, note="the tilt is printed to one decimal in Table 2 and as whole degrees here"),
    entry("cervical", 4, 864, "results", "tilt of", "EPItu", "C3-C7", "range_high", "5", "deg",
          levels("cervical-t2", "EPItu", C3_C7), "high", 0.5),
    entry("cervical", 4, 864, "results", "lower end-plates exhibited", "EPItl", "C3-C7", "range_low", "2", "deg",
          levels("cervical-t2", "EPItl", C3_C7), "low", 0.5),
    entry("cervical", 4, 864, "results", "lower end-plates exhibited", "EPItl", "C3-C7", "range_high", "4", "deg",
          levels("cervical-t2", "EPItl", C3_C7), "high", 0.5),
    entry("cervical", 4, 864, "results", "angular difference", "EPItu - EPItl", "all levels", "bound", "2", "deg",
          note="a bound, 'less than 2 deg'"),
    entry("cervical", 4, 864, "results", "midsagittal plane remained", "VBHp", "C3-C7", "range_low", "10.9", "mm",
          levels("cervical-t2", "VBHp", C3_C7), "low"),
    entry("cervical", 4, 864, "results", "midsagittal plane remained", "VBHp", "C3-C7", "range_high", "12.8", "mm",
          levels("cervical-t2", "VBHp", C3_C7), "high"),
    entry("cervical", 6, 866, "results", "left pedicle was", "PDAl over PDAr", "C2", "percent_change", "60", "percent",
          [cell("cervical-t4", "PDAl", "C2"), cell("cervical-t4", "PDAr", "C2")], "percent", 5.0),
    entry("cervical", 6, 866, "results", "transverse plane changed from about", "PDIt", "C3", "mean", "8", "deg",
          lr("cervical-t4", "PDIt", "C3"), "lr_mean", 1.0, value="-8",
          note="printed as 8 deg below the transverse plane; the sign is the word"),
    entry("cervical", 6, 866, "results", "transverse plane changed from about", "PDIt", "C7", "mean", "11", "deg",
          lr("cervical-t4", "PDIt", "C7"), "lr_mean", 1.0),
    entry("cervical", 6, 866, "results", "sagittal plane decreased from about", "PDIs", "C3", "mean", "40", "deg",
          lr("cervical-t4", "PDIs", "C3"), "lr_mean", 5.0, note="about 40, a round number: Table 4 prints 41.6 and 42.9, whose mean is 42.3"),
    entry("cervical", 6, 866, "results", "sagittal plane decreased from about", "PDIs", "C7", "mean", "29", "deg",
          lr("cervical-t4", "PDIs", "C7"), "lr_mean", 1.0),
    entry("cervical", 6, 866, "results", "upper articulating surface averaged", "UJAu", "C3-C7", "mean", "44", "mm2",
          levels("cervical-t6", "UJAru", C3_C7) + levels("cervical-t6", "UJAlu", C3_C7), "mean", 1.0,
          note="the mean of the right and left upper areas over C3 to C7; C2 has no upper joint and prints a dash"),
    entry("cervical", 7, 867, "discussion", "average cervical value of", "SCW/SCD", "C2-C6", "ratio", "1.4", "ratio",
          levels("cervical-t3", "SCW/SCD", ["C2", "C3", "C4", "C5", "C6"], "ratio"), "mean", 0.05,
          note="the average cervical value above C7"),
    entry("cervical", 7, 867, "discussion", "average cervical value of", "SCW/SCD", "C7", "ratio", "1.6", "ratio",
          [cell("cervical-t3", "SCW/SCD", "C7", "ratio")], "equal", 0.05),
    entry("cervical", 8, 868, "discussion", "within 2 mm", "EPD versus Nissan and Gilad, Francis", "C2-C7", "bound", "2", "mm",
          note="a bound on a comparison with other studies"),
    entry("cervical", 8, 868, "discussion", "less than those observed", "VBH below Nissan and Gilad, Francis", "", "range_low", "2", "mm",
          note="a comparison with other studies"),
    entry("cervical", 8, 868, "discussion", "less than those observed", "VBH below Nissan and Gilad, Francis", "", "range_high", "2.5", "mm",
          note="a comparison with other studies"),
    entry("cervical", 8, 868, "discussion", "overestimate of the measured area", "EPA by ellipse", "all levels", "percent_change", "10", "percent",
          note="restates page 864"),
    entry("cervical", 8, 868, "discussion", "underestimate by approximately", "EPA by triangle", "", "percent_change", "40", "percent",
          note="restates page 864"),
    # ---- lumbar, Spine 1992;17(3):299-306 --------------------------------------------
    vertebrae("lumbar", 1, 299, "study of 60 vertebrae", "60", "L1-L5", "five levels, L1 to L5"),
    twelve("lumbar", 1, 299),
    *summary("lumbar", 1, 299, ("average age of 46.3", "weight of 67.8", "height of 167.8", "ratio was 8/4"), "8/4"),
    entry("lumbar", 3, 301, "results", "end-plate widths of approximately", "EPWl L5 over L1", "L1-L5", "percent_change", "14", "percent",
          [cell("lumbar-t2", "EPWl", "L5"), cell("lumbar-t2", "EPWl", "L1")], "percent", 1.5,
          note="the sentence names no end-plate; the lower gives 14.1 percent and the upper 14.8"),
    entry("lumbar", 3, 301, "results", "upper end plate, the increase was", "EPWu/EPDu L5 over L1", "L1-L5", "percent_change", "12", "percent",
          [cell("lumbar-t2", "EPWu/EPDu", "L5", "ratio"), cell("lumbar-t2", "EPWu/EPDu", "L1", "ratio")], "percent", 1.5),
    entry("lumbar", 3, 301, "results", "lower end-plate ratio increased", "EPWl/EPDl L5 over L1", "L1-L5", "percent_change", "21", "percent",
          [cell("lumbar-t2", "EPWl/EPDl", "L5", "ratio"), cell("lumbar-t2", "EPWl/EPDl", "L1", "ratio")], "percent", 1.5),
    entry("lumbar", 3, 301, "results", "respectively 17% and 9%", "EPAu L5 over L1", "L1-L5", "percent_change", "17", "percent",
          [cell("lumbar-t2", "EPAu", "L5"), cell("lumbar-t2", "EPAu", "L1")], "percent", 1.5),
    entry("lumbar", 3, 301, "results", "respectively 17% and 9%", "EPAl L5 over L1", "L1-L5", "percent_change", "9", "percent",
          [cell("lumbar-t2", "EPAl", "L5"), cell("lumbar-t2", "EPAl", "L1")], "percent", 1.5),
    entry("lumbar", 3, 301, "results", "narrowest portion", "SCD", "L3", "mean", "17.5", "mm",
          [cell("lumbar-t3", "SCD", "L3")], "equal", 0.05, note="the sentence calls SCD the lateral dimension; Table 1 names it the depth"),
    entry("lumbar", 3, 301, "results", "height (PDH) averaged", "PDH", "L1", "mean", "15.9", "mm", lr("lumbar-t4", "PDH", "L1"), "lr_mean", 0.1),
    entry("lumbar", 3, 301, "results", "decreased to 14.4", "PDH", "L3", "mean", "14.4", "mm", lr("lumbar-t4", "PDH", "L3"), "lr_mean", 0.1),
    entry("lumbar", 3, 301, "results", "increased to 19.6", "PDH", "L5", "mean", "19.6", "mm", lr("lumbar-t4", "PDH", "L5"), "lr_mean", 0.1),
    entry("lumbar", 3, 301, "results", "width (PDW) was initially", "PDW", "L1", "mean", "8.6", "mm", lr("lumbar-t4", "PDW", "L1"), "lr_mean", 0.1),
    entry("lumbar", 3, 301, "results", "decreased to 8.2", "PDW", "L2", "mean", "8.2", "mm", lr("lumbar-t4", "PDW", "L2"), "lr_mean", 0.1),
    entry("lumbar", 3, 301, "results", "approximately 3.5 mm per vertebral level", "PDW per level L2-L5", "L2-L5", "difference", "3.5", "mm",
          note="a rate per level, not a cell"),
    entry("lumbar", 3, 301, "results", "At L5, the width was", "PDW", "L5", "mean", "18.9", "mm", lr("lumbar-t4", "PDW", "L5"), "lr_mean", 0.1,
          note="Table 4 prints 18.0 and 19.2, whose mean is 18.6: the paper's prose contradicts its table by 0.3 mm"),
    entry("lumbar", 4, 302, "results", "average ratio was", "PDH/PDW", "L1-L2", "ratio", "1.84", "ratio",
          [cell("lumbar-t4", "PDHr/PDWr", "L1", "ratio"), cell("lumbar-t4", "PDHl/PDWl", "L1", "ratio"),
           cell("lumbar-t4", "PDHr/PDWr", "L2", "ratio"), cell("lumbar-t4", "PDHl/PDWl", "L2", "ratio")], "mean", 0.05),
    entry("lumbar", 4, 302, "results", "decreased to approximately 1.0", "PDH/PDW", "L5", "ratio", "1.0", "ratio",
          [cell("lumbar-t4", "PDHr/PDWr", "L5", "ratio"), cell("lumbar-t4", "PDHl/PDWl", "L5", "ratio")], "mean", 0.1),
    entry("lumbar", 4, 302, "results", "(PDIs) increased generally", "PDIs", "L1", "mean", "14.5", "deg", lr("lumbar-t4", "PDIs", "L1"), "lr_mean", 0.5),
    entry("lumbar", 4, 302, "results", "(PDIs) increased generally", "PDIs", "L5", "mean", "24.5", "deg", lr("lumbar-t4", "PDIs", "L5"), "lr_mean", 0.5),
    entry("lumbar", 4, 302, "results", "(PDIt) increased slightly", "PDIt", "L1", "mean", "2.5", "deg", lr("lumbar-t4", "PDIt", "L1"), "lr_mean", 0.5),
    entry("lumbar", 4, 302, "results", "(PDIt) increased slightly", "PDIt", "L5", "mean", "5.5", "deg", lr("lumbar-t4", "PDIt", "L5"), "lr_mean", 0.5),
    entry("lumbar", 4, 302, "results", "cross-sectional area at L1 was about", "PIA", "L1", "mean", "62", "mm2", lr("lumbar-t5", "PIA", "L1"), "lr_mean", 1.0),
    entry("lumbar", 4, 302, "results", "cross-sectional area at L1 was about", "PIA", "L5", "mean", "81", "mm2", lr("lumbar-t5", "PIA", "L5"), "lr_mean", 1.0,
          note="Table 5 prints 92.9 (right) and 71.7 (left) at L5, whose mean is 82.3: the paper's prose contradicts its table by 1.3 mm2"),
    entry("lumbar", 4, 302, "results", "At L1, it was about", "SPL", "L1", "mean", "68", "mm", [cell("lumbar-t5", "SPL", "L1")], "equal", 0.5,
          note="the sentence cites Table 6; the value is in Table 5"),
    entry("lumbar", 4, 302, "results", "increased slightly to", "SPL", "L3", "mean", "72", "mm", [cell("lumbar-t5", "SPL", "L3")], "equal", 0.5),
    entry("lumbar", 4, 302, "results", "then decreased to 68", "SPL", "L5", "mean", "68", "mm", [cell("lumbar-t5", "SPL", "L5")], "equal", 0.5),
    entry("lumbar", 4, 302, "results", "increased generally from 71", "TPW", "L1", "mean", "71", "mm", [cell("lumbar-t5", "TPW", "L1")], "equal", 0.5),
    entry("lumbar", 4, 302, "results", "increased generally from 71", "TPW", "L5", "mean", "92", "mm", [cell("lumbar-t5", "TPW", "L5")], "equal", 0.5),
    entry("lumbar", 6, 304, "discussion", "increased by an average of", "PDIs L5 over L4", "L5", "difference", "8", "deg",
          lr("lumbar-t4", "PDIs", "L5") + lr("lumbar-t4", "PDIs", "L4"), "lr_diff", 1.0),
    entry("lumbar", 6, 304, "discussion", "pedicle widths were very small", "PDW", "L1-L2", "range_low", "8", "mm",
          lr("lumbar-t4", "PDW", "L1") + lr("lumbar-t4", "PDW", "L2"), "low", 0.5,
          note="the sentence names no level; the paragraph is the upper region, and L3 (10.2 mm) is outside 8 to 9"),
    entry("lumbar", 6, 304, "discussion", "pedicle widths were very small", "PDW", "L1-L2", "range_high", "9", "mm",
          lr("lumbar-t4", "PDW", "L1") + lr("lumbar-t4", "PDW", "L2"), "high", 0.5),
    entry("lumbar", 6, 304, "discussion", "in contrast to", "PDH", "lower lumbar levels", "range_low", "15", "mm",
          note="no level the sentence names fits: L4's mean is 15.5 and L5's 19.6"),
    entry("lumbar", 6, 304, "discussion", "in contrast to", "PDH", "lower lumbar levels", "range_high", "16", "mm",
          note="no level the sentence names fits: L4's mean is 15.5 and L5's 19.6"),
    entry("lumbar", 6, 304, "discussion", "consistently", "VBHp below Berry, Scoles, Gilad and Nissan", "", "range_low", "1", "mm",
          note="a comparison with other studies"),
    entry("lumbar", 6, 304, "discussion", "consistently", "VBHp below Berry, Scoles, Gilad and Nissan", "", "range_high", "2", "mm",
          note="a comparison with other studies"),
    entry("lumbar", 7, 305, "discussion", "elliptical approximation overestimated the measured area by less than", "EPA by ellipse", "", "bound", "10", "percent",
          note="a bound on an approximation by a formula"),
    entry("lumbar", 7, 305, "discussion", "consistent overestimate by", "SCA by ellipse", "", "range_low", "10", "percent",
          note="an approximation by a formula"),
    entry("lumbar", 7, 305, "discussion", "consistent overestimate by", "SCA by ellipse", "", "range_high", "30", "percent",
          note="an approximation by a formula"),
    entry("lumbar", 7, 305, "discussion", "triangular approximation underestimated the actual area by", "SCA by triangle", "", "range_low", "20", "percent",
          note="an approximation by a formula"),
    entry("lumbar", 7, 305, "discussion", "triangular approximation underestimated the actual area by", "SCA by triangle", "", "range_high", "30", "percent",
          note="an approximation by a formula"),
    # ---- thoracic, Spine 1991;16(8):888-901 ------------------------------------------
    # its Methods name the specimens' age, sex, weight, height and cause of death and give them
    # in Table 1, with no summary
    vertebrae("thoracic", 1, 888, "study of 144 vertebrae", "144", "T1-T12", "twelve levels, T1 to T12"),
    # The body table (Table 3, printed page 892) came from the owner's second scan on 27 October
    # 2026, read on its own (README.md), so the text's body values are held to its cells. Two of
    # the text's percentages and one height contradict it, and the contradictions are recorded
    # as such (CONTRADICTIONS.md).
    entry("thoracic", 3, 890, "results", "ranging from 55%", "EPWl T12 over T1", "T1-T12", "percent_change", "55", "percent",
          [cell("thoracic-t3", "EPWl", "T12"), cell("thoracic-t3", "EPWl", "T1")], "percent", 2.0,
          note="Table 3 gives 51.4% for the lower end-plate width (27.8 to 42.1) and 59.2% for the upper; "
               "the mean of the two widths' increases is 55.3%, the printed figure"),
    entry("thoracic", 3, 890, "results", "to 73% for the upper end-plate depth", "EPDu T12 over T1", "T1-T12", "percent_change", "73", "percent",
          [cell("thoracic-t3", "EPDu", "T12"), cell("thoracic-t3", "EPDu", "T1")], "percent", 2.0,
          note="Table 3 gives 77.3% for the upper end-plate depth (18.5 to 32.8) and 69.5% for the lower; "
               "the mean of the two depths' increases is 73.4%, the printed figure"),
    entry("thoracic", 3, 890, "results", "the width was 1.3 times", "EPWu/EPDu", "T1", "ratio", "1.3", "ratio",
          [cell("thoracic-t3", "EPWu/EPDu", "T1", "ratio")], "equal", 0.05,
          note="the upper end-plate's printed ratio; Table 3 prints 1.4 for the lower end-plate at T1"),
    entry("thoracic", 3, 890, "results", "at T12, the ratio was", "EPWu/EPDu", "T12", "ratio", "1.2", "ratio",
          [cell("thoracic-t3", "EPWu/EPDu", "T12", "ratio")], "equal", 0.05,
          note="the upper end-plate's printed ratio; Table 3 prints 1.3 for the lower end-plate at T12"),
    entry("thoracic", 3, 890, "results", "3.2 and 2.7 times larger", "EPAu T12 over T1", "T12", "ratio", "3.2", "ratio",
          [cell("thoracic-t3", "EPAu", "T12"), cell("thoracic-t3", "EPAu", "T1")], "ratio", 0.05),
    entry("thoracic", 3, 890, "results", "3.2 and 2.7 times larger", "EPAl T12 over T1", "T12", "ratio", "2.7", "ratio",
          [cell("thoracic-t3", "EPAl", "T12"), cell("thoracic-t3", "EPAl", "T1")], "ratio", 0.05),
    entry("thoracic", 3, 890, "results", "upper end-plate was 1.7", "EPItu", "all levels", "mean", "1.7", "deg",
          levels("thoracic-t3", "EPItu", T1_T12), "mean", 0.05),
    entry("thoracic", 3, 890, "results", "lower end-plate was 2.1", "EPItl", "all levels", "mean", "2.1", "deg",
          levels("thoracic-t3", "EPItl", T1_T12), "mean", 0.05, note="the twelve printed means average 2.075"),
    entry("thoracic", 3, 890, "results", "found to average 3.8", "EPIt", "all levels", "mean", "3.8", "deg",
          levels("thoracic-t3", "EPIt", T1_T12), "mean", 0.05, note="the twelve printed wedge angles average 3.775"),
    entry("thoracic", 3, 890, "results", "found to be 3.9", "wedge angle, radiographic", "all levels", "mean", "3.9", "deg",
          note="a supplementary radiographic study, in no table"),
    entry("thoracic", 3, 890, "results", "posterior vertebral height from a value of", "VBHp", "T1", "mean", "14.3", "mm",
          [cell("thoracic-t3", "VBHp", "T1")], "equal", 0.05,
          note="Table 3 prints 14.1 at T1, and Table 8's Present Study column restates 14.1; the text's 14.3 matches neither"),
    entry("thoracic", 3, 890, "results", "to 22.7 mm at T12", "VBHp", "T12", "mean", "22.7", "mm",
          [cell("thoracic-t3", "VBHp", "T12")], "equal", 0.05),
    entry("thoracic", 3, 890, "results", "an increase of 60%", "VBHp T12 over T1", "T1-T12", "percent_change", "60", "percent",
          [cell("thoracic-t3", "VBHp", "T12"), cell("thoracic-t3", "VBHp", "T1")], "percent", 2.0,
          note="61.0% from Table 3's 14.1 at T1; the text's own 14.3 would give 58.7%"),
    entry("thoracic", 3, 890, "results", "average increase of 0.8 mm per vertebral level", "VBHp per level", "T1-T12", "difference", "0.8", "mm",
          note="a rate per level, not a cell: (22.7 - 14.1) / 11 = 0.78 from Table 3"),
    entry("thoracic", 4, 891, "results", "with an average value of 17.4", "SCW", "T4-T9", "mean", "17.4", "mm",
          levels("thoracic-t4", "SCW", ["T4", "T5", "T6", "T7", "T8", "T9"]), "mean", 0.05),
    entry("thoracic", 4, 891, "results", "with an average value of 16.2", "SCD", "T1-T12", "mean", "16.2", "mm",
          levels("thoracic-t4", "SCD", T1_T12), "mean", 0.1, note="the sentence names no levels; the mean of all twelve"),
    entry("thoracic", 4, 891, "results", "significant increase to", "SCD", "T12", "mean", "18.1", "mm",
          [cell("thoracic-t4", "SCD", "T12")], "equal", 0.05),
    entry("thoracic", 4, 891, "results", "having a ratio of 1.0", "SCW/SCD", "T4-T6", "ratio", "1.0", "ratio",
          levels("thoracic-t4", "SCW/SCD", ["T4", "T5", "T6"], "ratio"), "mean", 0.06),
    entry("thoracic", 4, 891, "results", "averaging 198", "SCA", "T2-T10", "mean", "198", "mm2",
          levels("thoracic-t4", "SCA", ["T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]), "mean", 1.0),
    entry("thoracic", 4, 891, "results", "large increase to 280", "SCA", "T12", "mean", "280", "mm2",
          [cell("thoracic-t4", "SCA", "T12")], "equal", 0.05),
    entry("thoracic", 4, 891, "results", "cross-sectional area of 189", "SCA", "T3", "mean", "189", "mm2",
          [cell("thoracic-t4", "SCA", "T3")], "equal", 0.5,
          note="Table 4 prints 180.0 at T3, and 180.0 is the least of its row: the paper's prose contradicts its table"),
    entry("thoracic", 4, 891, "results", "height averaged 9.6", "PDH", "T1", "mean", "9.6", "mm", lr("thoracic-t5", "PDH", "T1"), "lr_mean", 0.1),
    entry("thoracic", 4, 891, "results", "increased rapidly to 11.9", "PDH", "T3", "mean", "11.9", "mm", lr("thoracic-t5", "PDH", "T3"), "lr_mean", 0.1),
    entry("thoracic", 4, 891, "results", "the height averaged 11.9", "PDH", "T3-T8", "mean", "11.9", "mm",
          [c for lv in ["T3", "T4", "T5", "T6", "T7", "T8"] for c in lr("thoracic-t5", "PDH", lv)], "mean", 0.1),
    entry("thoracic", 4, 891, "results", "approximately 1 mm per vertebral level", "PDH per level", "T8-T12", "difference", "1", "mm",
          note="a rate per level, not a cell"),
    entry("thoracic", 4, 891, "results", "width was initially 8.4", "PDW", "T1", "mean", "8.4", "mm", lr("thoracic-t5", "PDW", "T1"), "lr_mean", 0.1),
    entry("thoracic", 4, 891, "results", "average of 6.3", "PDW", "T3-T8", "mean", "6.3", "mm",
          [c for lv in ["T3", "T4", "T5", "T6", "T7", "T8"] for c in lr("thoracic-t5", "PDW", lv)], "mean", 0.1),
    entry("thoracic", 4, 891, "results", "linear increase of 0.7 mm", "PDW per level", "T8-T12", "difference", "0.7", "mm",
          note="a rate per level, not a cell"),
    entry("thoracic", 4, 891, "results", "the height was 16.6", "PDH", "T12", "mean", "16.6", "mm", lr("thoracic-t5", "PDH", "T12"), "lr_mean", 0.1),
    entry("thoracic", 4, 891, "results", "the width was 8.7", "PDW", "T12", "mean", "8.7", "mm", lr("thoracic-t5", "PDW", "T12"), "lr_mean", 0.1),
    entry("thoracic", 5, 893, "results", "average ratio was 1.1", "PDH/PDW", "T1", "ratio", "1.1", "ratio",
          [cell("thoracic-t5", "PDH/PDWr", "T1", "ratio"), cell("thoracic-t5", "PDH/PDWl", "T1", "ratio")], "mean", 0.1),
    entry("thoracic", 5, 893, "results", "increased to approximately 1.9", "PDH/PDW", "T5", "ratio", "1.9", "ratio",
          [cell("thoracic-t5", "PDH/PDWr", "T5", "ratio"), cell("thoracic-t5", "PDH/PDWl", "T5", "ratio")], "mean", 0.1),
    entry("thoracic", 5, 893, "results", "initial area was about", "PDA", "T1", "mean", "53", "mm2", lr("thoracic-t5", "PDA", "T1"), "lr_mean", 1.0),
    entry("thoracic", 5, 893, "results", "decreasing to 32", "PDA", "middle region", "mean", "32", "mm2",
          [c for lv in T1_T12 for c in lr("thoracic-t5", "PDA", lv)], "low", 1.0,
          note="the middle region is not named by level; the least of the twelve left and right means is taken"),
    entry("thoracic", 5, 893, "results", "reaching a value of 94", "PDA", "T12", "mean", "94", "mm2", lr("thoracic-t5", "PDA", "T12"), "lr_mean", 1.0),
    entry("thoracic", 5, 893, "results", "approximately threefold", "PDA T12 over T7", "T7-T12", "ratio", "3", "ratio",
          lr("thoracic-t5", "PDA", "T12") + lr("thoracic-t5", "PDA", "T7"), "lr_ratio", 0.5,
          note="printed as the word threefold, a round number: the T12 means over the T7 means of Table 5 give 2.6"),
    entry("thoracic", 5, 893, "results", "from approximately 27", "PDIs", "T1-T2", "mean", "27", "deg",
          lr("thoracic-t5", "PDIs", "T1") + lr("thoracic-t5", "PDIs", "T2"), "mean", 1.0),
    entry("thoracic", 5, 893, "results", "to 10", "PDIs", "T12", "mean", "10", "deg", lr("thoracic-t5", "PDIs", "T12"), "lr_mean", 1.0),
    entry("thoracic", 5, 893, "results", "at approximately 9", "PDIt", "T3-T11", "mean", "9", "deg",
          [c for lv in T1_T12[2:11] for c in lr("thoracic-t5", "PDIt", lv)], "mean", 1.0),
    entry("thoracic", 5, 893, "results", "jumped from 7.6", "PDIt", "T1", "mean", "7.6", "deg", lr("thoracic-t5", "PDIt", "T1"), "lr_mean", 0.1),
    entry("thoracic", 5, 893, "results", "to 17.9", "PDIt", "T2", "mean", "17.9", "deg", lr("thoracic-t5", "PDIt", "T2"), "lr_mean", 0.1),
    entry("thoracic", 5, 893, "results", "from 8.7", "PDIt", "T11", "mean", "8.7", "deg", lr("thoracic-t5", "PDIt", "T11"), "lr_mean", 0.1),
    entry("thoracic", 5, 893, "results", "to 5.0", "PDIt", "T12", "mean", "5.0", "deg", lr("thoracic-t5", "PDIt", "T12"), "lr_mean", 0.1),
    entry("thoracic", 5, 893, "results", "area at T3 was about", "PIA", "T3", "mean", "90", "mm2", lr("thoracic-t7", "PIA", "T3"), "lr_mean", 5.0,
          note="about 90, a round number: Table 7 prints 118 (right) and 73 (left) at T3, whose mean is 95.5, outside even a round statement"),
    entry("thoracic", 5, 893, "results", "at T11 it was 160", "PIA", "T11", "mean", "160", "mm2", lr("thoracic-t7", "PIA", "T11"), "lr_mean", 2.0),
    entry("thoracic", 5, 893, "results", "decreased suddenly to 98", "PIA", "T12", "mean", "98", "mm2", lr("thoracic-t7", "PIA", "T12"), "lr_mean", 2.0,
          note="Table 7 prints 86 (right) and 98 (left) at T12: the text's 98 is the left side alone; the mean is 92"),
    entry("thoracic", 5, 893, "results", "At T1, it was about 50", "SPL", "T1", "mean", "50", "mm", [cell("thoracic-t7", "SPL", "T1")], "equal", 1.0),
    entry("thoracic", 5, 893, "results", "continued to be about 50", "SPL", "T1-T10", "mean", "50", "mm",
          levels("thoracic-t7", "SPL", T1_T12[:10]), "mean", 2.0),
    entry("thoracic", 5, 893, "results", "decreased to 46", "SPL", "T11", "mean", "46", "mm", [cell("thoracic-t7", "SPL", "T11")], "equal", 0.5),
    entry("thoracic", 10, 898, "discussion", "wedge angle of 3.8", "EPIt", "all levels", "mean", "3.8", "deg",
          levels("thoracic-t3", "EPIt", T1_T12), "mean", 0.05, note="restates page 890"),
    entry("thoracic", 10, 898, "discussion", "total of approximately 45.6", "sum of the wedge angles", "T1-T12", "sum", "45.6", "deg",
          levels("thoracic-t3", "EPIt", T1_T12), "sum", 0.5,
          note="twelve times the rounded 3.8; the twelve wedge angles Table 3 prints sum to 45.3"),
    entry("thoracic", 10, 898, "discussion", "per thoracic vertebra to be 3.9", "wedge angle, radiographic", "all levels", "mean", "3.9", "deg",
          note="restates page 890"),
    entry("thoracic", 10, 898, "discussion", "consistently 4", "EPDl above Scoles, Cotterill", "", "range_low", "4", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "consistently 4", "EPDl above Scoles, Cotterill", "", "range_high", "5", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "consistently 1 to 2 mm less", "VBHp below Berry, Scoles", "", "range_low", "1", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "consistently 1 to 2 mm less", "VBHp below Berry, Scoles", "", "range_high", "2", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "by approximately 1 mm", "SCW above Scoles", "", "difference", "1", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "1 to 2 mm greater", "PDW above the earlier work", "", "range_low", "1", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "1 to 2 mm greater", "PDW above the earlier work", "", "range_high", "2", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "2 to 3 mm less", "PDW, Scoles below Zindrick", "T3, T6, T9", "range_low", "2", "mm", note="a comparison between other studies"),
    entry("thoracic", 10, 898, "discussion", "2 to 3 mm less", "PDW, Scoles below Zindrick", "T3, T6, T9", "range_high", "3", "mm", note="a comparison between other studies"),
    entry("thoracic", 10, 898, "discussion", "3 to 4 mm less", "PDW, Scoles below the present study and Krag", "T3, T6, T9", "range_low", "3", "mm", note="a comparison with other studies"),
    entry("thoracic", 10, 898, "discussion", "3 to 4 mm less", "PDW, Scoles below the present study and Krag", "T3, T6, T9", "range_high", "4", "mm", note="a comparison with other studies"),
    entry("thoracic", 12, 900, "discussion", "Berry: 137.0", "PDIt, Berry", "T2", "mean", "137.0", "deg",
          [cell("thoracic-t8b", "PDIt", "T2", "mean", "Berry (1987)")], "equal", 0.05),
    entry("thoracic", 12, 900, "discussion", "Zindrick: 17.5", "PDIt, Zindrick", "T2", "mean", "17.5", "deg",
          [cell("thoracic-t8b", "PDIt", "T2", "mean", "Zindrick (1987)")], "equal", 0.05),
    entry("thoracic", 12, 900, "discussion", "present study: 17.9", "PDIt", "T2", "mean", "17.9", "deg",
          [cell("thoracic-t8b", "PDIt", "T2", "mean", "Present Study")], "equal", 0.05),
    entry("thoracic", 12, 900, "discussion", "error of less than 10%", "EPA by ellipse", "all levels", "bound", "10", "percent",
          note="a bound on an approximation by a formula"),
    entry("thoracic", 12, 900, "discussion", "20% underestimate at T1", "EPA by triangle", "T1", "percent_change", "20", "percent",
          note="an approximation by a formula"),
    entry("thoracic", 12, 900, "discussion", "40% underestimate at T12", "EPA by triangle", "T12", "percent_change", "40", "percent",
          note="an approximation by a formula"),
    # ---- facets, Spine 1993;18(10):1298-1310 -----------------------------------------
    vertebrae("facets", 1, 1298, "study of 276 vertebrae", "276", "C2-L5", "23 levels, C2 to L5"),
    # The abstract's extremes run over every facet from C3 to L5, superior and inferior, right
    # and left: the lowest and highest of the level means of Tables 2 to 8.
    entry("facets", 1, 1298, "abstract", "width = 9.6", "FCW", "C3-L5", "range_low", "9.6", "mm",
          [c for m in ("FCWsr", "FCWsl") for c in levels("facets-t2", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("FCWir", "FCWil") for c in levels("facets-t3", m, C3_C7 + T1_T12 + L1_L5)], "low",
          note="the least facet width Tables 2 and 3 print from C3 to L5 is 9.5, the inferior right at T12 (Table 3), not 9.6"),
    entry("facets", 1, 1298, "abstract", "width = 9.6", "FCW", "C3-L5", "range_high", "16.3", "mm",
          [c for m in ("FCWsr", "FCWsl") for c in levels("facets-t2", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("FCWir", "FCWil") for c in levels("facets-t3", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "height = 10.2", "FCH", "C3-L5", "range_low", "10.2", "mm",
          [c for m in ("FCHsr", "FCHsl") for c in levels("facets-t2", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("FCHir", "FCHil") for c in levels("facets-t3", m, C3_C7 + T1_T12 + L1_L5)], "low"),
    entry("facets", 1, 1298, "abstract", "height = 10.2", "FCH", "C3-L5", "range_high", "18.4", "mm",
          [c for m in ("FCHsr", "FCHsl") for c in levels("facets-t2", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("FCHir", "FCHil") for c in levels("facets-t3", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "surface area = 72.3", "FCA", "C3-L5", "range_low", "72.3", "mm2",
          [c for m in ("FCAsr", "FCAsl", "FCAir", "FCAil") for c in levels("facets-t4", m, C3_C7 + T1_T12 + L1_L5)], "low",
          note="the least facet area Table 4 prints from C3 to L5 is 69.4, the inferior right at T6, not 72.3"),
    entry("facets", 1, 1298, "abstract", "surface area = 72.3", "FCA", "C3-L5", "range_high", "211.9", "mm2",
          [c for m in ("FCAsr", "FCAsl", "FCAir", "FCAil") for c in levels("facets-t4", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "interfacet width = 20.8", "IFW", "C3-L5", "range_low", "20.8", "mm",
          [c for m in ("IFWs", "IFWi") for c in levels("facets-t5", m, C3_C7 + T1_T12 + L1_L5)], "low"),
    entry("facets", 1, 1298, "abstract", "interfacet width = 20.8", "IFW", "C3-L5", "range_high", "40.6", "mm",
          [c for m in ("IFWs", "IFWi") for c in levels("facets-t5", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "interfacet height = 12.2", "IFH", "C3-L5", "range_low", "12.2", "mm",
          [c for m in ("IFHr", "IFHl") for c in levels("facets-t5", m, C3_C7 + T1_T12 + L1_L5)], "low"),
    entry("facets", 1, 1298, "abstract", "interfacet height = 12.2", "IFH", "C3-L5", "range_high", "33.0", "mm",
          [c for m in ("IFHr", "IFHl") for c in levels("facets-t5", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "transverse plane angle = 41.0", "T", "C3-L5", "range_low", "41.0", "deg",
          [c for m in ("Tsr", "Tsl") for c in levels("facets-t6", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("Tir", "Til") for c in levels("facets-t7", m, C3_C7 + T1_T12 + L1_L5)], "low"),
    entry("facets", 1, 1298, "abstract", "transverse plane angle = 41.0", "T", "C3-L5", "range_high", "86.0", "deg",
          [c for m in ("Tsr", "Tsl") for c in levels("facets-t6", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("Tir", "Til") for c in levels("facets-t7", m, C3_C7 + T1_T12 + L1_L5)], "high"),
    entry("facets", 1, 1298, "abstract", "sagittal plane angle = 67.4", "S", "C3-L5", "range_low", "67.4", "deg",
          [c for m in ("Ssr", "Ssl") for c in levels("facets-t6", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("Sir", "Sil") for c in levels("facets-t7", m, C3_C7 + T1_T12 + L1_L5)], "abs_low",
          note="the abstract prints the range without sign; the least magnitude is 67.4, the superior left at T12"),
    entry("facets", 1, 1298, "abstract", "sagittal plane angle = 67.4", "S", "C3-L5", "range_high", "154.8", "deg",
          [c for m in ("Ssr", "Ssl") for c in levels("facets-t6", m, C3_C7 + T1_T12 + L1_L5)]
          + [c for m in ("Sir", "Sil") for c in levels("facets-t7", m, C3_C7 + T1_T12 + L1_L5)], "abs_high",
          note="the abstract prints the range without sign"),
    entry("facets", 1, 1298, "abstract", "X-card angle = 41.0", "CAX", "C3-L5", "range_low", "41.0", "deg",
          [c for m in ("CAXsr", "CAXsl", "CAXir", "CAXil") for c in levels("facets-t8", m, C3_C7 + T1_T12 + L1_L5)], "abs_low",
          note="the abstract prints the range without sign, and the same range as the transverse plane angle"),
    entry("facets", 1, 1298, "abstract", "X-card angle = 41.0", "CAX", "C3-L5", "range_high", "86.0", "deg",
          [c for m in ("CAXsr", "CAXsl", "CAXir", "CAXil") for c in levels("facets-t8", m, C3_C7 + T1_T12 + L1_L5)], "abs_high",
          note="the abstract prints the range without sign, and the same range as the transverse plane angle"),
    entry("facets", 1, 1298, "abstract", "Y-card angle = 5.8", "CAY", "C3-L5", "range_low", "5.8", "deg",
          [c for m in ("CAYsr", "CAYsl", "CAYir", "CAYil") for c in levels("facets-t8", m, C3_C7 + T1_T12 + L1_L5)], "abs_low",
          note="the abstract prints the range without sign; the least magnitude Table 8 prints from C3 to L5 is 4.1, "
               "the superior right at T1, which the results on page 1306 themselves call the dip at T1, not 5.8"),
    entry("facets", 1, 1298, "abstract", "Y-card angle = 5.8", "CAY", "C3-L5", "range_high", "66.1", "deg",
          [c for m in ("CAYsr", "CAYsl", "CAYir", "CAYil") for c in levels("facets-t8", m, C3_C7 + T1_T12 + L1_L5)], "abs_high",
          note="the abstract prints the range without sign"),
    # the Methods' sentence on the specimens begins on printed page 1298 and goes on to 1299
    twelve("facets", 1, 1298),
    *summary("facets", 2, 1299, ("average age of the subjects was 46.3", "weight was 67.8", "height was 167.8",
                                 "ratio was 8:4"), "8:4"),
    entry("facets", 2, 1299, "methods", "disarticulating the 12 spines", "specimens", "", "count", "12", "count",
          [ROWS], "count", 0.0, note="the 12 spines taken apart into 276 vertebrae"),
    entry("facets", 2, 1299, "methods", "into 276 vertebrae", "vertebrae", "C2-L5", "count", "276", "count",
          note="twelve spines of 23 levels, C2 to L5; no table counts vertebrae"),
    entry("facets", 2, 1299, "methods", "pooled from the 12 vertebrae", "vertebrae per level", "", "count", "12", "count",
          [ROWS], "count", 0.0, note="one vertebra of each spine at each level"),
    entry("facets", 7, 1304, "results", "increased above 1.0", "IFWs/IFWi", "middle to lower cervical", "bound", "1.0", "ratio",
          note="a threshold"),
    entry("facets", 7, 1304, "results", "between 1.5 and 3", "IFW/IFH", "C2-C7", "range_low", "1.5", "ratio",
          levels("facets-t5", "IFW/IFH", C2_C7, "ratio"), "low", 0.3),
    entry("facets", 7, 1304, "results", "between 1.5 and 3", "IFW/IFH", "C2-C7", "range_high", "3", "ratio",
          levels("facets-t5", "IFW/IFH", C2_C7, "ratio"), "high", 0.3),
    entry("facets", 7, 1304, "results", "approximately 1 in the thoracic and lumbar", "IFW/IFH", "T1-L5", "mean", "1", "ratio",
          levels("facets-t5", "IFW/IFH", T1_T12 + L1_L5, "ratio"), "mean", 0.15),
    entry("facets", 7, 1304, "results", "decreased significantly from 116", "Ss", "C2", "mean", "116", "deg",
          [cell("facets-t6", "Ssr", "C2"), cell("facets-t6", "Ssl", "C2")], "abs_mean", 1.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "decreased significantly from 116", "Ss", "C3", "mean", "75", "deg",
          [cell("facets-t6", "Ssr", "C3"), cell("facets-t6", "Ssl", "C3")], "abs_mean", 5.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "increased from 75", "Ss", "C7", "mean", "80", "deg",
          [cell("facets-t6", "Ssr", "C7"), cell("facets-t6", "Ssl", "C7")], "abs_mean", 5.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "remained constant at approximately 70", "Ss", "T2-T11", "range_low", "70", "deg",
          [c for m in ("Ssr", "Ssl") for c in levels("facets-t6", m, T1_T12[1:11])], "abs_low", 5.0,
          note="approximately 70-75, round numbers, as magnitudes"),
    entry("facets", 7, 1304, "results", "remained constant at approximately 70", "Ss", "T2-T11", "range_high", "75", "deg",
          [c for m in ("Ssr", "Ssl") for c in levels("facets-t6", m, T1_T12[1:11])], "abs_high", 5.0,
          note="approximately 70-75, round numbers, as magnitudes"),
    entry("facets", 7, 1304, "results", "changed from approximately 70", "Ss", "T12", "mean", "70", "deg",
          [cell("facets-t6", "Ssr", "T12"), cell("facets-t6", "Ssl", "T12")], "abs_mean", 5.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "changed from approximately 70", "Ss", "L1", "mean", "137", "deg",
          [cell("facets-t6", "Ssr", "L1"), cell("facets-t6", "Ssl", "L1")], "abs_mean", 1.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "decreased from approximately 137", "Ss", "L5", "mean", "118", "deg",
          [cell("facets-t6", "Ssr", "L5"), cell("facets-t6", "Ssl", "L5")], "abs_mean", 1.0,
          note="the mean of the right and left magnitudes; Table 6 gives the right side a minus by its sign convention"),
    entry("facets", 7, 1304, "results", "From C2 to T4 the angle increased", "Ts", "C2", "mean", "35", "deg",
          [cell("facets-t6", "Tsr", "C2"), cell("facets-t6", "Tsl", "C2")], "mean", 5.0,
          note="approximately 35, a round number: Table 6 prints 40.7 and 33.5 at C2, whose mean is 37.1"),
    entry("facets", 7, 1304, "results", "From C2 to T4 the angle increased", "Ts", "T4", "mean", "75", "deg",
          [cell("facets-t6", "Tsr", "T4"), cell("facets-t6", "Tsl", "T4")], "mean", 5.0, note="approximately 75, a round number"),
    entry("facets", 7, 1304, "results", "slightly larger, approximately 80", "Ts", "L1-L5", "mean", "80", "deg",
          [c for m in ("Tsr", "Tsl") for c in levels("facets-t6", m, L1_L5)], "mean", 5.0,
          note="approximately 80, a round number: the ten lumbar cells of Table 6 average 83.3"),
    entry("facets", 8, 1305, "results", "from about -41", "CAXs", "C2", "mean", "-41", "deg",
          [cell("facets-t8", "CAXsr", "C2"), cell("facets-t8", "CAXsl", "C2")], "mean", 1.0,
          note="Table 8 prints -40.7 (right) and -33.5 (left) at C2: the text's -41 is the right side alone; the mean is -37.1"),
    entry("facets", 8, 1305, "results", "from about -41", "CAXs", "L5", "mean", "-86", "deg",
          [cell("facets-t8", "CAXsr", "L5"), cell("facets-t8", "CAXsl", "L5")], "mean", 1.0),
    entry("facets", 9, 1306, "results", "Starting from +38.9", "CAYsr", "C2", "mean", "+38.9", "deg", [cell("facets-t8", "CAYsr", "C2")], "equal", 0.05, value="38.9"),
    entry("facets", 9, 1306, "results", "Starting from +38.9", "CAYsr", "C3", "mean", "-17.6", "deg", [cell("facets-t8", "CAYsr", "C3")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "Starting from +38.9", "CAYsr", "C5", "mean", "+9.2", "deg", [cell("facets-t8", "CAYsr", "C5")], "equal", 0.05, value="9.2",
          note="Figure 8's label for C5 reads +9.8 (page 1307)"),
    entry("facets", 9, 1306, "results", "dip at T1", "CAYsr", "T1", "mean", "+4.1", "deg", [cell("facets-t8", "CAYsr", "T1")], "equal", 0.05, value="4.1"),
    entry("facets", 9, 1306, "results", "respective CAY values are", "CAYsr", "T12", "mean", "+18.0", "deg", [cell("facets-t8", "CAYsr", "T12")], "equal", 0.05, value="18.0"),
    entry("facets", 9, 1306, "results", "respective CAY values are", "CAYsr", "L1", "mean", "-50.5", "deg", [cell("facets-t8", "CAYsr", "L1")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "continuous decrease to", "CAYsr", "L5", "mean", "-27.7", "deg", [cell("facets-t8", "CAYsr", "L5")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "right inferior facet of C6", "CAXir", "C6", "mean", "-55.0", "deg", [cell("facets-t8", "CAXir", "C6")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "right inferior facet of C6", "CAYir", "C6", "mean", "10.3", "deg", [cell("facets-t8", "CAYir", "C6")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "superior facet of C7", "CAXsr", "C7", "mean", "-59.4", "deg", [cell("facets-t8", "CAXsr", "C7")], "equal", 0.05),
    entry("facets", 9, 1306, "results", "superior facet of C7", "CAYsr", "C7", "mean", "11.4", "deg", [cell("facets-t8", "CAYsr", "C7")], "equal", 0.05),
    entry("facets", 10, 1307, "caption", "C5 +9.8", "CAYsr", "C5", "mean", "+9.8", "deg", [cell("facets-t8", "CAYsr", "C5")], "equal", 0.05, value="9.8",
          note="a label drawn in Figure 8; the results on page 1306 say +9.2"),
    entry("facets", 10, 1307, "caption", "C5 +9.8", "CAXsr", "C5", "mean", "-45.8", "deg", [cell("facets-t8", "CAXsr", "C5")], "equal", 0.05,
          note="a label drawn in Figure 8"),
    entry("facets", 10, 1307, "caption", "T6 +18.2", "CAYsr", "T6", "mean", "+18.2", "deg", [cell("facets-t8", "CAYsr", "T6")], "equal", 0.05, value="18.2",
          note="a label drawn in Figure 8"),
    entry("facets", 10, 1307, "caption", "T6 +18.2", "CAXsr", "T6", "mean", "-73.5", "deg", [cell("facets-t8", "CAXsr", "T6")], "equal", 0.05,
          note="a label drawn in Figure 8"),
    entry("facets", 10, 1307, "caption", "L3 -42.0", "CAYsr", "L3", "mean", "-42.0", "deg", [cell("facets-t8", "CAYsr", "L3")], "equal", 0.05,
          note="a label drawn in Figure 8"),
    entry("facets", 10, 1307, "caption", "L3 -42.0", "CAXsr", "L3", "mean", "-81.9", "deg", [cell("facets-t8", "CAXsr", "L3")], "equal", 0.05,
          note="a label drawn in Figure 8"),
    entry("facets", 10, 1307, "discussion", "above 1.5", "IFW/IFH", "cervical", "bound", "1.5", "ratio", note="a threshold"),
    entry("facets", 10, 1307, "discussion", "transverse plane (i.e., 30", "Ts", "C2-C7", "range_low", "30", "deg",
          [c for m in ("Tsr", "Tsl") for c in levels("facets-t6", m, C2_C7)], "low", 5.0, note="a round statement"),
    entry("facets", 10, 1307, "discussion", "transverse plane (i.e., 30", "Ts", "C2-C7", "range_high", "50", "deg",
          [c for m in ("Tsr", "Tsl") for c in levels("facets-t6", m, C2_C7)], "high", 5.0,
          note="a round statement, 30-50: Table 6 prints 59.4 for the superior right facet at C7, past its upper end even as a round number"),
    entry("facets", 10, 1307, "discussion", "uniform increase from 35", "Ts", "C2", "mean", "35", "deg",
          [cell("facets-t6", "Tsr", "C2"), cell("facets-t6", "Tsl", "C2")], "mean", 5.0,
          note="a round number: Table 6 prints 40.7 and 33.5 at C2, whose mean is 37.1"),
    entry("facets", 10, 1307, "discussion", "uniform increase from 35", "Ts", "L5", "mean", "80", "deg",
          [cell("facets-t6", "Tsr", "L5"), cell("facets-t6", "Tsl", "L5")], "mean", 5.0,
          note="a round number, but Table 6 prints 86.0 and 85.1 at L5, whose mean is 85.6; the results on page 1304 say "
               "approximately 80 for the lumbar spine as a whole, which holds"),
    entry("facets", 10, 1307, "discussion", "approximately 16", "CAYsr", "T1-T12", "mean", "16", "deg",
          levels("facets-t8", "CAYsr", T1_T12), "abs_mean", 3.0, note="a magnitude; the right superior facet, which the results describe"),
    entry("facets", 10, 1307, "discussion", "decreased from 1.15", "IFWs/IFWi", "T1", "ratio", "1.15", "ratio",
          [cell("facets-t5", "IFWs/IFWi", "T1", "ratio")], "equal", 0.05),
    entry("facets", 10, 1307, "discussion", "decreased from 1.15", "IFWs/IFWi", "T9", "ratio", "0.95", "ratio",
          [cell("facets-t5", "IFWs/IFWi", "T9", "ratio")], "equal", 0.05),
    entry("facets", 10, 1307, "discussion", "oriented between 120", "S", "lumbar", "range_low", "120", "deg", note="a round statement"),
    entry("facets", 10, 1307, "discussion", "oriented between 120", "S", "lumbar", "range_high", "150", "deg", note="a round statement"),
    entry("facets", 10, 1307, "discussion", "angled from 60", "S", "cervical and thoracic", "range_low", "60", "deg", note="a round statement"),
    entry("facets", 10, 1307, "discussion", "angled from 60", "S", "cervical and thoracic", "range_high", "90", "deg", note="a round statement"),
    entry("facets", 11, 1308, "discussion", "highest, about 90", "CAX", "lumbar", "mean", "90", "deg", note="a round statement of a magnitude"),
    entry("facets", 11, 1308, "discussion", "from about 50", "CAYsr magnitude", "L1", "mean", "50", "deg",
          [cell("facets-t8", "CAYsr", "L1")], "abs_mean", 1.0),
    entry("facets", 11, 1308, "discussion", "from about 50", "CAYsr magnitude", "L5", "mean", "28", "deg",
          [cell("facets-t8", "CAYsr", "L5")], "abs_mean", 1.0),
    entry("facets", 11, 1308, "discussion", "ratios were 0.9", "IFW/IFH", "L3", "ratio", "0.9", "ratio", [cell("facets-t5", "IFW/IFH", "L3", "ratio")], "equal", 0.05),
    entry("facets", 11, 1308, "discussion", "ratios were 0.9", "IFW/IFH", "L4", "ratio", "1.16", "ratio", [cell("facets-t5", "IFW/IFH", "L4", "ratio")], "equal", 0.05),
    entry("facets", 11, 1308, "discussion", "ratios were 0.9", "IFW/IFH", "L5", "ratio", "1.44", "ratio", [cell("facets-t5", "IFW/IFH", "L5", "ratio")], "equal", 0.05),
    entry("facets", 12, 1309, "discussion", "Skipor", "forward tilt, Skipor", "lumbar", "mean", "18", "deg", note="another study's value"),
    entry("facets", 12, 1309, "discussion", "Skipor", "forward tilt, Skipor", "lumbar", "range_low", "-28", "deg", note="another study's value"),
    entry("facets", 12, 1309, "discussion", "Skipor", "forward tilt, Skipor", "lumbar", "range_high", "53", "deg", note="another study's value"),
    entry("facets", 12, 1309, "discussion", "We observed a range from 19.5", "forward tilt", "lumbar", "range_high", "19.5", "deg",
          note="printed from the larger to the smaller; no table carries the tilt"),
    entry("facets", 12, 1309, "discussion", "We observed a range from 19.5", "forward tilt", "lumbar", "range_low", "8.7", "deg",
          note="printed from the larger to the smaller; no table carries the tilt"),
    entry("facets", 12, 1309, "discussion", "must be approximately 90", "T", "lumbar", "bound", "90", "deg", note="a condition, not a value"),
    entry("facets", 12, 1309, "discussion", "sagittal plane angles are approximately 90", "S", "cervical and thoracic", "bound", "90", "deg",
          note="a condition, not a value"),
]


def ascii_quote(s: str) -> str:
    return (s.replace("\u2013", "-").replace("\u2014", "-").replace("\u00b0", " deg").replace("\u00b2", "2")
            .replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"'))


def kept(r: dict) -> dict:
    """A pass's record as reads/prose.csv keeps it, its words in ASCII."""
    return {"page": str(r["page"]), "crop": r["crop"], "where": r["where"], "quote": ascii_quote(r["quote"]),
            "measure": ascii_quote(r["measure"]), "levels": ascii_quote(r["levels"]), "value": r["value"],
            "units": r["units"], "statistic": r["statistic"], "study": r["study"], "note": ascii_quote(r["note"])}


def load_reads(new: bool = True) -> dict[tuple[str, str], list[dict]]:
    """Every record of every prose pass, by (paper, pass): those reads/prose.csv keeps, then, with
    `new`, those of a later pass's files under out/provenance/reads/ (prose-*.json) that it does not
    keep yet. The first passes' own files were never committed, so the kept record is where their
    reads live, and prose.csv can be made again from the repository alone."""
    out: dict[tuple[str, str], list[dict]] = {}
    seen = set()

    def add(paper: str, which: str, record: dict) -> None:
        r = kept(record)
        key = (paper, which) + tuple(r[f] for f in READ_FIELDS[2:])
        if key not in seen:
            seen.add(key)
            out.setdefault((paper, which), []).append(r)

    if os.path.exists(READS_KEPT):
        with open(READS_KEPT, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                add(r["paper"], r["pass"], r)
    for path in sorted(glob.glob(os.path.join(READS_IN, "prose-*.json"))) if new else []:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for r in data["values"]:
            add(data["paper"], data["pass"], r)
    return out


def match(records: list[dict], e: dict) -> str:
    """What a pass read for an entry: its value where a record on the page quotes the key phrase."""
    for r in records:
        if int(r["page"]) != e["pdf_page"]:
            continue
        if e["key"].lower() in ascii_quote(r["quote"]).lower() and r["value"] == e["printed"]:
            return r["value"]
    for r in records:                       # the key phrase in another crop's version of the sentence
        if int(r["page"]) == e["pdf_page"] and r["value"] == e["printed"] and e["measure"].split(" ")[0] in r["measure"]:
            return r["value"]
    return ""


def quote_of(records: list[dict], e: dict) -> str:
    for r in records:
        if int(r["page"]) == e["pdf_page"] and e["key"].lower() in ascii_quote(r["quote"]).lower():
            return ascii_quote(r["quote"])
    return ""


def resolve(cells: list[dict], spec: tuple) -> list[str]:
    """The cell ids a spec names: one cell, or, with the level "*", every row of the column in
    the table's order. A table whose rows are specimens, not levels (the thoracic paper's Table 1),
    names a row by its label."""
    table, measure, level, statistic, study = spec
    out = []
    for c in cells:
        if c["table"] != table or c["measure"] != measure:
            continue
        if level != "*" and (c["level"] or c["row_label"]) != level:
            continue
        if study is not None and c["col_label"] != study:
            continue
        if c["statistic"] == statistic or (c["statistic"] == "mean+sem" and statistic in ("mean", "sem")):
            out.append("%s/r%02d_c%02d/%s" % (table, int(c["row"]), int(c["col"]), statistic))
            if level != "*":
                break
    if not out:
        raise SystemExit("no cell for %r" % (spec,))
    return out


def build(entries: list[dict], reads: dict[tuple[str, str], list[dict]]) -> list[dict]:
    """The rows of prose.csv: each entry with the cells it names, whether they give its number,
    and what each pass read."""
    with open(os.path.join(HERE, "cells.csv"), newline="", encoding="utf-8") as fh:
        cells = list(csv.DictReader(fh))
    prov = {r["id"]: r for r in check_prose.read_csv(os.path.join(HERE, "provenance.csv"))}
    rows = []
    for e in entries:
        a, b = reads.get((e["paper"], "A"), []), reads.get((e["paper"], "B"), [])
        ids = [i for s in e["cells"] for i in resolve(cells, s)]
        agrees = ""
        if ids:
            got = check_prose.evaluate(e["rule"], check_prose.cell_values(prov, ";".join(ids), e["rule"]))
            agrees = "yes" if abs(got - float(e["value"])) <= e["tolerance"] + 1e-9 else "no"
        rows.append({"paper": e["paper"], "pdf_page": str(e["pdf_page"]), "printed_page": str(e["printed_page"]),
                     "where": e["where"], "quote": quote_of(a, e) or quote_of(b, e), "measure": e["measure"],
                     "level": e["level"], "statistic": e["statistic"], "printed": e["printed"], "value": str(e["value"]),
                     "units": e["units"], "cells": ";".join(ids), "rule": e["rule"] if ids else "",
                     "tolerance": str(e["tolerance"]) if ids else "", "agrees": agrees, "note": e["note"],
                     "passA": match(a, e), "passB": match(b, e)})
    return rows


def write(entries: list[dict]) -> None:
    reads = load_reads()
    rows = build(entries, reads)
    for r in rows:
        if r["agrees"] == "no":
            print("contradiction: %s p.%s %s %s printed %s" % (r["paper"], r["printed_page"], r["measure"], r["level"],
                                                               r["printed"]))
        if not r["passA"] or not r["passB"]:
            print("unmatched: %s p.%s %s %s -> A %r B %r" % (r["paper"], r["printed_page"], r["measure"], r["printed"],
                                                             r["passA"], r["passB"]))
    with open(os.path.join(HERE, "prose.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.makedirs(os.path.dirname(READS_KEPT), exist_ok=True)
    with open(READS_KEPT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(READ_FIELDS)
        for (paper, which), records in sorted(reads.items()):
            for r in records:
                w.writerow([paper, which] + [r[f] for f in READ_FIELDS[2:]])
    print("prose.csv: %d entries, %d held to cells" % (len(rows), sum(1 for r in rows if r["cells"])))


if __name__ == "__main__":
    write(ENTRIES)
