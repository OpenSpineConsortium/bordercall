"""Turn the mapped readings of the papers' tables into series: one mean, SD and count per measure
and level for each set of subjects, technique, sex and subgroup a paper prints.

Usage: python3 -I series.py <mapped folder> <cohorts folder> <out.csv>

A paper prints a measure as a mean with an SD, an SE or a variance, for each sex or both, each side
or their mean, in one table or several. The comparison between papers, and the naming of one
paper's fields by another paper's table, need one mean and one population SD per measure and
level of each set of subjects, so this file decides, in code that can be read, how each is made:

- the SD is the printed SD; else an SE times the root of its count; else the root of a printed
  variance; a series with no way to an SD keeps its mean and an empty SD. A meta-analysis's SE
  (technique meta_pool) is the uncertainty of a random-effects pooled mean, not the spread of the
  people behind it, so neither it nor its printed variance (its square) gives an SD: Bonczar
  2024's SEs times the root of its 1,481 subjects made SDs of 30 to 180 mm and deg, and the root
  of its variance would make SDs of about 1;
- the count is the n printed for that cell; else the n the text states for that measure, level
  and sex where no table prints one (STATED_COUNTS); else the n a table prints for every measure of that
  level (Gilad 1985's and Zindrick 1987's rows of n), from the table the mean comes from; else the
  n printed for that measure and subgroup elsewhere in the paper, at that level or at none, never
  an n printed at another level or over a range of levels; else the n printed for the
  subgroup as a whole, an n before a count where both are printed, since a count may count
  something else (Busscher 2010's vertebrae per spine); else, for a series of both sexes, the
  cohort's number of people from its cohorts file, while a series of one sex with no printed count
  has none, since the cohort's people are not its (Duman 2026's sex and age bands); and the series
  says which (n_from). A paper's printed n that counts pedicles,
  both sides of each person, is kept as printed while the sexes and sides are pooled, since its
  SDs are over pedicles too, and the series written carries half of it, rounded up
  (PEDICLES_COUNTED);
- the sides: a value printed for both sides or their mean is taken as it is; a right and a left
  only are averaged, mean with mean and SD with SD (sides "averaged"). Where a paper prints the
  two sides of one angle with opposite signs, its left is negated first (MIRRORED_LEFT), as its
  mapping note says, since a plain mean would cancel the angle: Tan 2004's pedicle angles, left
  -42.9 and right 39.6 at C3, averaged to -1.65 against Panjabi's 42.25. Where a mapping note
  says a side is not to be used, the other stands alone (RIGHT_ONLY, each with its reason);
- the sexes: a value printed for both sexes is taken as it is; a male and a female only, each
  with its count, are pooled into one series with the pooled SD, which takes in the difference
  between the sexes' means (sex "pooled"); without both counts they stay two series;
- a value printed for both sides or both sexes that has no SD gives way to the two printed apart
  where they give one (a right and a left with SDs, a male and a female that can be pooled): it
  is most often the text restating a table, sometimes as a magnitude with its sign lost (Tan
  2004's Results, p. 143, give the sagittal angle at T8 as 8.6 where Table 1 prints right -7.6
  and left 9.6, mirrored -8.6), and the two printed apart carry the spread;
- subgroups (age bands, patients and controls, modalities) stay series of their own, since
  whether pooling them is right depends on what they are. A group label the mapping overruled,
  having put the row in the other cohort, or a label the text gives where a table names the same
  people otherwise, is read as the table's group (REGROUPED, with its reason). A group that is no
  population, a model's estimates for the paper's people or a group chosen by the measure itself,
  makes no series (NOT_POPULATIONS);
- a signed mean of a measure Panjabi prints unsigned, where the mapping says to compare
  magnitudes, is taken as its magnitude (MAGNITUDES).

Values a table quotes from another study are series of that study's subjects, not of the paper's,
and keep the study's name in source_of_values. A series' mean is the first mean printed for its
cell, else the first single value, but a cell printed in several tables takes its mean from the
table that prints its SD, where that table prints a mean too, so that the mean and the SD are one
table's pair (mean_row); its units, definition and comparison with Panjabi are those of the row
its mean is taken from. A printed value that cannot be the measure, a misprint, stays in readings/
as printed and is left out here (MISPRINTS, each with its reason), and so are a paper's own values
printed again, under a label of their own in a table beside other studies' values or in text
restating a table (REPRINTS), and the values a table quotes from another work on the paper's own
subjects (REPRINTED_SOURCES), which would otherwise count the same subjects twice.
"""

import collections
import csv
import json
import math
import os
import re
import sys

POOLED_MEANS = {"meta_pool"}
# Cells printed as the paper prints them in readings/ but kept out of every series, each with why:
# a value the page prints that cannot be the measure (a misprint), never corrected by guess. A key
# of four names one side of a cell, the other side then standing for the cell; a key of five names
# one side and one sex, the other sexes then standing for the cell.
MISPRINTS = {
    ("hou1993", "pedicle_h", "T9", "", "all"):
        "Table 2 (p. 1852, PDF 3) prints the T9 cumulative height 12.9 +/- 1.2 mm beside the men's 12.5 and the "
        "women's 12.2: no mean of the two sexes can lie outside them (25 men and 15 women give 12.39), as every "
        "other level's does not; the sexes, pooled, stand for T9",
    ("tan2004", "endplate_lower_area", "L3"):
        "Table 1 prints 172.0 +/- 20.6 mm2 (p. 141, PDF 5; both readers and the text layer agree) between "
        "1,090.9 at L2 and 1,199.3 at L4: a sixth of its neighbours, probably 1172.0 with a digit lost",
    ("robertson2000", "pedicle_h", "L3", "left"):
        "Table 1 prints the left L3 height 18.6 mm with an SD of 13.0 (p. 711, PDF 3) on 10 pedicles, against "
        "2.5 to 3.9 for every other height and 2.5 on the right at L3: a spread no 18.6 mm pedicle can have, "
        "probably 3.0; the right side, 18.7 +/- 2.5, stands for L3",
}
# (paper, table, group) of the paper's own values printed again, under a label of their own, in a
# table or text that sets them beside other studies' or restates another table: the same subjects
# as the series they repeat, so they make no series of their own.
REPRINTS = {
    ("arockiaraj2025", "Table 3", "Current study"):
        "Table 3 (p. 317, PDF 6) prints Table 2's means and SDs again as 'Current study, Arockiaraj et al. "
        "(n=300)' beside other regions' studies",
    ("ahmed2019", "Table 3", "MRI study of symptomatic adults; Indian"):
        "Table 3 (p. 25, PDF 5) prints Table 1's male and female canal depths again as 'Present study' "
        "beside other studies, the same 80 subjects",
    ("ahmed2019", "Table No.4", "MRI study of symptomatic adults; Indian"):
        "Table No.4 (p. 25, PDF 5) prints Table 2's male and female canal widths again as 'Present study' "
        "beside other studies, the same 80 subjects",
    ("masharawi2021", "Table 6", "Israeli"):
        "Table 6 (p. 12, PDF 12) gives the same 50 controls again, one mean over sides and sexes, as 'Current "
        "study, Israeli, 50' beside other studies; its widths and its L3 to L5 heights are Table 5's control "
        "means over sides and sexes, rounded (p. 11, PDF 11, the controls as REGROUPED reads them), while its "
        "L1 and L2 heights, 12.4 and 12.06, differ from those means, 12.74 and 11.91",
    ("yu2015", "Table 5", "American"):
        "Table 5 (p. 1645, PDF 7) gives the whole 503 again as 'CS, American (N = 503)' beside other studies; "
        "its means are Table 4's 404 men and 99 women pooled, to 0.01 mm (p. 1643, PDF 5)",
    ("ahn2001", "Text: Results", "Marfan"):
        "the Results (p. 68, PDF 2) give the Table's Marfan interpedicular means again, citing the Table, "
        "the same 32 patients",
    ("chaudhary2015", "Table II", "sonepat District"):
        "Table II (p. 35, PDF 3) prints Table I's interpedicular means again as 'Present study (sonepat "
        "District)' beside other studies, the same 300 films, to the 0.01 mm",
    ("mitra2002", "Text: Abstract", ""):
        "the Abstract (p. 453, PDF 1) gives Table 1's direct means for the 18 men again with no sex named "
        "(16.19 mm at L5, which the Results call the men's), so read as the cohort's they would displace the sexes",
    ("mitra2002", "Text: Results", "Direct"):
        "the Results (pp. 454 to 455, PDF 2 to 3) restate Tables 1 and 2's direct means, some under the wrong sex (5.95 mm at "
        "L1, called male, is the women's) and one with a digit lost (4.79 for 14.79)",
    ("mitra2002", "Text: Results", "CT"):
        "the Results (p. 456, PDF 4) restate Table 1's CT widths, printed in cm for mm",
    ("mitra2002", "Text: Discussion", "Direct"):
        "the Discussion (pp. 456 to 457, PDF 4 to 5) gives Table 1's men's direct L5 width and angle again as 'the current "
        "study', with no sex named",
}
# Bach 2019's Figures 2 to 7 (pp. e108 to e109, PDF 3 to 4) plot each decade's disc height of the same 240 patients
# as Tables 2 and 3 print by decade (pp. e110 to e111; the points of decades 20 to 70 equal the tables' three-point
# averages or lie within 0.15 mm, the 10 point is the same age band, read off a chart): the same
# subjects twice. The 80 point has no table row and stays.
REPRINTS.update({
    ("bach2019", "Figure %d" % figure, "decade %d" % decade):
        "Figure %d's decade %d point repeats Tables 2 and 3's decade of the same patients, read off a chart"
        % (figure, decade)
    for figure in range(2, 8) for decade in range(10, 80, 10)})
# (paper, group) of values a paper prints that are no group of people measured: estimates of a model
# fitted to the paper's people, whose SE is the model's and not a sampling SE, and groups chosen by
# the measure itself, which a comparison of populations cannot take as one.
NOT_POPULATIONS = {
    ("griffith2016", "adjusted for height and weight"):
        "Tables S1 to S4 and S6 (suppl.) print 'Estimated mean (SE)' after adjusting for height and weight: "
        "a model's estimates for the same 1,080 patients as Tables 2 to 6, whose SE times the root of 540 "
        "is no spread of people",
    ("griffith2016", "25% largest"):
        "Table 7's quartiles are the patients whose canal was largest, chosen by the measure itself",
    ("griffith2016", "25% smallest"):
        "Table 7's quartiles are the patients whose canal was smallest, chosen by the measure itself",
}
# Olsewski 1990 prints its transverse pedicle angle apart for the pedicles that point cephalad and
# the pedicles that point caudad (Tables I to III, pp. 544 to 545, PDF 4 to 5; the Results, p. 545):
# groups chosen by the measure's own sign, neither a mean over all pedicles, so no population.
NOT_POPULATIONS.update({
    ("olsewski1990", "%s, %s" % (part, direction)):
        "the pedicles of one sign of the angle, a group chosen by the measure itself (pp. 544 to 545)"
    for part in ("Part 1 cadavers, direct", "Part 2 cadavers, direct", "Part 2 cadavers, lateral radiographs",
                 "Part 3 living patients, lateral radiographs")
    for direction in ("cephalad", "caudad")})
# (paper, source_of_values) of a work a paper's tables quote whose subjects are the paper's own: its
# values repeat the paper's own series, so they make no series of their own.
REPRINTED_SOURCES = {
    ("tang2016", "Tang [31]"):
        "Tables 5 to 7 (pp. 4124 to 4128, PDF 9 to 13) quote the first author's 2013 dissertation (ref. 31, "
        "p. 4130, PDF 15) with this paper's 55 women and 52 men and Table 4's means and SDs (p. 4120, PDF 5), "
        "all but the men's L5/S1 disc AP diameter, printed 4.00 cm against Table 4's 4.01",
}
# (paper, key) whose left side is printed with the opposite sign to the right and to Panjabi's
# convention; the mapping note of each reading says to reverse the left (readings/tan2004.csv).
MIRRORED_LEFT = {("tan2004", "pedicle_incl_sag")}
# (paper, key) whose mapping note says to compare the right side only: every other side is left out,
# each with why.
RIGHT_ONLY = {
    ("bonczar2024", "pedicle_incl_sag"):
        "Tables 2 to 6 (pp. 5 to 9) give pooled left sagittal angles falling from 2.62 to -8.54 deg, none "
        "differing from zero (p 0.22 to 0.92), against 10.31 to 21.24 deg on the right: the pooled sources "
        "likely mixed sign conventions on the left, and averaging the sides gave 5.2 to 7.9 deg",
}
# (paper, table, cohort, printed group): the group of the cohort the mapping put the row in, where
# the page's label is wrong and the reading keeps it as printed. Masharawi 2021's Table 5 (p. 11,
# PDF 11) prints its Control and DS labels in no fixed order (Left Width / Males reads DS then
# Control, Left Length / Males Control twice); each sex's first row is the control, as Table 6's
# control widths show (p. 12: 7.3 at L1 is the mean of the male left 7.63 printed DS, the male right
# 7.35 and the female 7.36 and 6.95, where the row printed Control would give 7.4), so the mapping
# put each row in its cohort (map_note) and its group follows the cohort.
REGROUPED = {
    ("masharawi2021", "Table 5", "control", "DS"): "Control",
    ("masharawi2021", "Table 5", "ds", "Control"): "DS",
    # Shin 2024's Results count its people as Caucasian and African-American (p. 3) where Table 5
    # prints the same groups as White and Black (p. 4), so its counts reach the table's groups.
    ("shin2024", "Text: Results", "shin700", "Caucasian"): "White",
    ("shin2024", "Text: Results", "shin700", "African-American"): "Black",
    # Twomey 1985 bounds its young adults three ways: Table 1 counts them as 18-35 (women) and 20-36
    # (men), 24 each (PDF 1), Table 2 prints them as 20-35 for both sexes (PDF 2) and Table 3 as 18-35
    # for the women; one group, so the counts reach the means.
    ("twomey1985", "Table 1", "cadavers-204", "18-35"): "20-35",
    ("twomey1985", "Table 1", "cadavers-204", "20-36"): "20-35",
    ("twomey1985", "Table 3", "cadavers-204", "18-35"): "20-35",
}
# Bach 2019's Table 1 counts each decade and sex as "decade 10" to "decade 70" (p. e108, PDF 3)
# where Tables 2 to 5 name the same people First to Seventh Decade (pp. e110 to e113, PDF 5 to 8);
# one spelling, the tables', so the paper's printed counts reach its 252 decade cells.
REGROUPED.update({
    ("bach2019", "Table 1", "usf_ct240", "decade %d" % (10 * i)): "%s Decade" % name
    for i, name in enumerate(("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh"), 1)})
# (paper, table) whose every value is a model's estimate and no group of people measured, where
# the rows carry no group to list under NOT_POPULATIONS. Shin 2024's Tables 4 and 5 (p. 4, PDF 4)
# print estimated marginal means of a two-way ANCOVA "accounting for weight, height, BMI" and
# ethnicity or sex (Methods 2.2, p. 3): the Griffith 2016 class. Its sex pairs average to Table 2
# because the groups are equal, which tells adjusted from raw not at all.
NOT_POPULATION_TABLES = {("shin2024", "Table 4"), ("shin2024", "Table 5")}
# (paper, cohort) whose text states, or whose counts over a range of levels give, how many were
# measured at each level where no table prints an n for it:
# the count for a measure, level and sex, and why. Kunkel 2011 tested 72 motion segments of 30 spines,
# six a disc level from C7-T1 to T11-T12 (p. 377, PDF 3), so six a disc is stated; that each segment
# gave both its bodies, twelve a body from T1 to T11 and six at C7 and T12, is an inference from
# Fig. 1a, which marks the corners of both vertebrae of a segment, since Table 2 prints no n.
STATED_COUNTS = {
    ("kunkel2011", "ulm_thoracic_segments"):
        (lambda key, level, sex: 6 if "-" in level or level in ("C7", "T12") else 12,
         "six motion segments a disc level (p. 377, PDF 3): six a disc; twelve a body and six at C7 and T12 "
         "by inference, both bodies of each segment measured (Fig. 1a)"),
    # Chen 2011 prints its counts for the ten end-plates from T10 inferior to L3 superior together:
    # 830 for its 83 patients (Table 1), 430 and 400 by sex (Tables 2 and 3), so 43 men and 40 women.
    ("chen2011", "chongqing_ct83"):
        (lambda key, level, sex: {"male": 43, "female": 40}.get(sex),
         "Table 1 (p. 1817, PDF 4) counts 830 end-plates of 83 patients and Tables 2 and 3 (pp. 1817 to 1818, "
         "PDF 4 to 5) 430 and 400 by sex, ten a person: 43 men and 40 women"),
}
# Papers whose cell n, printed for both sides together, counts pedicles and not people: the people
# are taken as half the pedicles, rounded up, as one person gives two. Olsewski 1990's footnotes to
# Tables I and II (p. 544, PDF 4) and III (p. 545, PDF 5) call the n "the numbers of examples", 47 at
# the men's L5 width for 24 men.
PEDICLES_COUNTED = {"olsewski1990"}
# (paper, key) whose mean is signed where Panjabi prints a magnitude; the mapping note says to compare
# magnitudes, so the series takes the mean's magnitude. Tan 2004 prints its end-plate angles signed,
# the thoracic lower angles negative (Table 1, pp. 140 to 141, PDF 4 to 5), Panjabi unsigned.
MAGNITUDES = {("tan2004", "endplate_incl"), ("tan2004", "endplate_lower_incl")}
NOT_MEASURES = {"subject_age", "subject_height", "subject_weight", "subject_bmi", "subject_count", "prevalence",
                "reliability", "other"}
PLAIN_SIDES = ("", "both", "mean of sides")
PLAIN_SEXES = ("all", "not stated", "")
# The statistics a series' mean is taken from, the first present winning.
MEAN_STATISTICS = ("mean", "single")
COLUMNS = ["paper", "cohort", "technique", "source_of_values", "key", "level", "sex", "group", "side", "mean", "sd",
           "n", "sd_from", "n_from", "units", "vs_panjabi", "definition", "tables", "pages"]
VERTEBRA = re.compile(r"^(C[1-7]|T(1[0-3]|[1-9])|L[1-6]|S[1-5])(-(C[1-7]|T(1[0-3]|[1-9])|L[1-6]|S[1-5]))?$")


def number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def read_mapped(folder):
    rows = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".csv"):
            rows += list(csv.DictReader(open(os.path.join(folder, name), newline="")))
    return rows


def cohort_people(folder):
    people = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith(".cohorts.json"):
            data = json.load(open(os.path.join(folder, name)))
            for c in data.get("cohorts", []):
                people[(data["paper"], c.get("cohort"))] = c.get("n_people")
    return people


def group_of(row):
    return REGROUPED.get((row["paper"], row["table"], row["cohort"], row["group"]), row["group"])


def cell_key(row):
    return (row["paper"], row["cohort"], row["technique"], row["source_of_values"], row["key"], row["level"],
            row["sex"], group_of(row), row["side"])


def left_out(row):
    """Whether a row is kept out of every series: a misprint, a group that is no population, a
    reprint, a quoted work on the paper's own subjects or a side not to be used."""
    cell = (row["paper"], row["key"], row["level"])
    if cell in MISPRINTS or cell + (row["side"],) in MISPRINTS or cell + (row["side"], row["sex"]) in MISPRINTS:
        return True
    if (row["paper"], row["group"]) in NOT_POPULATIONS or (row["paper"], row["table"]) in NOT_POPULATION_TABLES:
        return True
    if row["source_of_values"] == "this paper" and (row["paper"], row["table"], row["group"]) in REPRINTS:
        return True
    if (row["paper"], row["source_of_values"]) in REPRINTED_SOURCES:
        return True
    return (row["paper"], row["key"]) in RIGHT_ONLY and row["side"] != "right"


def gather(rows):
    """{cell: {statistic: [values], ...}} for the measure rows that name one vertebra or one disc,
    and each cell's description (described)."""
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    cell_rows = collections.defaultdict(list)
    for row in rows:
        if row["key"] in NOT_MEASURES or not VERTEBRA.match(row["level"]) or left_out(row):
            continue
        value = number(row["canonical_value"])
        if value is None:
            continue
        k = cell_key(row)
        cells[k][row["statistic"]].append(value)
        cell_rows[k].append(row)
    return cells, {k: described(found) for k, found in cell_rows.items()}


def mean_row(rows):
    """The row a cell's mean is taken from: the first mean, else the first single, but where the
    table of the cell's first SD, the SD one_series takes, prints a mean too, that table's first
    mean, so that the mean and the SD are one table's pair; another table's mean may be rounded,
    read off a chart or another number. Cizmic 2023 prints the women's L4 canal depth as 17.38 in
    Table 3 and as 17.1420 +/- 2.15820 in Table 5 (p. 202, PDF 3); Bach 2019's Figure 8 labels its
    points 5.656725 and so on (p. e113, PDF 8), where the Abstract gives 5.6 +/- 1.1 mm for men at
    T12/L1 (p. e106, PDF 1)."""
    sd_table = next((row["table"] for row in rows if row["statistic"] == "sd"), None)
    for statistic in MEAN_STATISTICS:
        means = [row for row in rows if row["statistic"] == statistic]
        if means:
            return next((row for row in means if row["table"] == sd_table), means[0])
    return None


def described(rows):
    """A cell's description: every table and page that prints it, and the mean, table, units,
    definition and comparison with Panjabi of the row its mean is taken from (mean_row), not of
    whichever row comes first, which may be its n, r or p."""
    description = {"tables": {row["table"] for row in rows}, "pages": {row["pdf_page"] for row in rows}}
    row = mean_row(rows)
    if row is not None:
        description.update(mean=number(row["canonical_value"]), table=row["table"], units=row["canonical_units"],
                           vs_panjabi=row["vs_panjabi"], definition=row["definition"])
    return description


def printed_counts(rows):
    """The n a paper prints outside a cell, to stand in for a cell that prints none: "level",
    {(paper, cohort, table, level, sex, group): n} for an n a table prints for every measure of one
    level; "measure", {(paper, cohort, key, level, sex, group): n} where one n is printed for a
    measure and subgroup, at that level or at none, since an n printed at one level says nothing of
    another (Olsewski 1990's caudad angles count 8 and 4 pedicles at L5 alone); "level_any",
    {(paper, cohort, level, sex, group): n} for a level's n that every table of the cohort prints
    alike, for a mean the text gives (Krag 1988's Results means at T9, T12 and L5, whose Tables 1
    and 2 both count each level); "group", {(paper, cohort, sex, group): n} for a count printed for
    the subgroup as a whole, where one n, else one n or count, is printed; a count printed at one
    level feeds that level alone, never the subgroup (Robertson 2000's 20 sides of S1). A count
    printed for a range of levels is none of these, since it counts each level's people again (Shin
    2024's 3,500 interspaces of 700 patients, Chen 2011's 430 end-plates of 43 men)."""
    by_level, by_level_any, by_measure, by_group, group_n = (collections.defaultdict(set) for _ in range(5))
    for row in rows:
        value = number(row["canonical_value"]) if row["canonical_value"] else number(row["value"])
        if value is None or row["statistic"] not in ("n", "count"):
            continue
        if row["level"] and not VERTEBRA.match(row["level"]):
            continue
        group = group_of(row)
        if row["key"] == "subject_count":
            if VERTEBRA.match(row["level"]):
                if row["statistic"] == "n":
                    by_level[(row["paper"], row["cohort"], row["table"], row["level"], row["sex"], group)].add(value)
                    by_level_any[(row["paper"], row["cohort"], row["level"], row["sex"], group)].add(value)
                continue
            by_group[(row["paper"], row["cohort"], row["sex"], group)].add(value)
            if row["statistic"] == "n":
                group_n[(row["paper"], row["cohort"], row["sex"], group)].add(value)
        elif row["key"] not in NOT_MEASURES and row["statistic"] == "n":
            # An n alone: a count printed for a measure may count something else (Krag 1988's Table 2
            # counts the pedicles of each 1-mm bin of width).
            by_measure[(row["paper"], row["cohort"], row["key"], row["level"], row["sex"], group)].add(value)
    single = lambda d: {k: next(iter(v)) for k, v in d.items() if len(v) == 1}
    return {"level": single(by_level), "level_any": single(by_level_any), "measure": single(by_measure),
            "group": {**single(by_group), **single(group_n)}}


def first(values):
    return values[0] if values else None


def count_of(k, stats, table, people, counts):
    """The cell's n and where it came from (n_from), in the order the docstring gives."""
    paper, cohort, _, _, key, level, sex, group, _ = k
    stated = STATED_COUNTS.get((paper, cohort))
    candidates = ((first(stats.get("n", [])), "cell"),
                  (stated[0](key, level, sex) if stated else None, "stated"),
                  (counts["level"].get((paper, cohort, table, level, sex, group)), "level"),
                  (counts["level_any"].get((paper, cohort, level, sex, group)), "level"),
                  (counts["measure"].get((paper, cohort, key, level, sex, group)), "measure"),
                  (counts["measure"].get((paper, cohort, key, "", sex, group)), "measure"),
                  (counts["group"].get((paper, cohort, sex, group)), "subgroup"),
                  (people.get((paper, cohort)) if sex in ("all", "not stated") else None, "cohort"))
    return next(((n, n_from) for n, n_from in candidates if n is not None), (None, ""))


def one_series(k, stats, description, people, counts):
    """The cell's mean (from its description), SD and count, in the order the docstring gives."""
    technique = k[2]
    mean = description.get("mean")
    if mean is None:
        return None
    n, n_from = count_of(k, stats, description["table"], people, counts)
    # A printed count of pedicles stays as printed while the sexes and sides are pooled, since the
    # paper's SDs are over pedicles too, and is halved once the series is written (halve_pedicles).
    pedicles = k[0] in PEDICLES_COUNTED and n_from in ("cell", "level", "measure")
    sd, sd_from = first(stats.get("sd", [])), "sd"
    if sd is None and stats.get("sem") and n and technique not in POOLED_MEANS:
        sd, sd_from = stats["sem"][0] * math.sqrt(n), "sem x root n"
    if sd is None and stats.get("variance") and technique not in POOLED_MEANS:
        sd, sd_from = math.sqrt(stats["variance"][0]), "root of variance"
    if sd is None:
        sd_from = ""
    return {"mean": mean, "sd": sd, "n": n, "sd_from": sd_from, "n_from": n_from, "pedicles": pedicles}


def plain_stands(plain, pair_has_sd):
    """Whether a value printed for both sides or both sexes is taken over the two printed apart:
    unless it has no SD and they can give one (the module docstring says why)."""
    return plain["sd"] is not None or not pair_has_sd


def joined(a, b, **values):
    """a with values set, its tables and pages joined with b's, for a series made of two."""
    return dict(a, tables=a["tables"] | b["tables"], pages=a["pages"] | b["pages"], **values)


def average_sides(r, l, mirrored):
    if mirrored:
        l = dict(l, mean=-l["mean"])
    sd = (r["sd"] + l["sd"]) / 2 if r["sd"] is not None and l["sd"] is not None else None
    n = min(x for x in (r["n"], l["n"]) if x) if (r["n"] or l["n"]) else None
    return joined(r, l, mean=(r["mean"] + l["mean"]) / 2, sd=sd, n=n, sd_from=r["sd_from"] if sd is not None else "")


def merge_sides(found, mirrored=False):
    """found: {side: series}. One series for the measure: a plain side as it is, unless it has no
    SD and a right and a left with SDs are printed; else the mean of a right and a left, the left's
    sign reversed first where the paper prints the sides mirrored."""
    plain = next((side for side in PLAIN_SIDES if side in found), None)
    pair = "right" in found and "left" in found
    pair_has_sd = pair and found["right"]["sd"] is not None and found["left"]["sd"] is not None
    if plain is not None and plain_stands(found[plain], pair_has_sd):
        return plain, found[plain]
    if pair:
        return "averaged", average_sides(found["right"], found["left"], mirrored)
    side = sorted(found)[0]
    return side, found[side]


def halve_pedicles(s, side):
    """A series whose count is the paper's count of pedicles, both sides of each person, written
    with the people: half the pedicles, rounded up. A cell of one side counts people and is left."""
    if s.get("pedicles") and s["n"] and side == "both":
        return dict(s, n=math.ceil(s["n"] / 2), n_from=s["n_from"] + ", pedicles halved")
    return s


def pool_sexes(m, f):
    """A male and a female series with counts and SDs pooled into one, the SD taking in the
    difference between the means."""
    n = m["n"] + f["n"]
    mean = (m["n"] * m["mean"] + f["n"] * f["mean"]) / n
    within = (m["n"] - 1) * m["sd"] ** 2 + (f["n"] - 1) * f["sd"] ** 2
    between = m["n"] * f["n"] / n * (m["mean"] - f["mean"]) ** 2
    return joined(m, f, mean=mean, sd=math.sqrt((within + between) / (n - 1)), n=n,
                  sd_from="pooled from the sexes", n_from="sum of the sexes")


def poolable(s):
    return s is not None and s["n"] and s["n"] > 1 and s["sd"] is not None


def pick_sexes(found):
    """found: {sex: (side, series)}. The series written for one measure, level and subgroup."""
    plain = next((sex for sex in PLAIN_SEXES if sex in found), None)
    both = "male" in found and "female" in found and poolable(found["male"][1]) and poolable(found["female"][1])
    if plain is not None and plain_stands(found[plain][1], both):
        return [(plain, found[plain])]
    if both:
        side = found["male"][0] if found["male"][0] == found["female"][0] else "mixed"
        return [("pooled", (side, pool_sexes(found["male"][1], found["female"][1])))]
    return sorted(found.items())


def build(rows, people):
    cells, meta = gather(rows)
    counts = printed_counts(rows)
    sides = collections.defaultdict(dict)
    for k, stats in cells.items():
        s = one_series(k, stats, meta[k], people, counts)
        if s is not None:
            s.update(meta[k])
            if (k[0], k[4]) in MAGNITUDES:
                s["mean"] = abs(s["mean"])
            sides[k[:8]][k[8]] = s
    sexes = collections.defaultdict(dict)
    for k, found in sides.items():
        side, s = merge_sides(found, (k[0], k[4]) in MIRRORED_LEFT)
        sexes[k[:6] + k[7:8]][k[6]] = (side, s)
    out = []
    for k, found in sexes.items():
        paper, cohort, technique, source, key, level, group = k
        for sex, (side, s) in pick_sexes(found):
            s = halve_pedicles(s, side)
            out.append({"paper": paper, "cohort": cohort, "technique": technique, "source_of_values": source,
                        "key": key, "level": level, "sex": sex, "group": group, "side": side,
                        "mean": s["mean"], "sd": s["sd"], "n": s["n"], "sd_from": s["sd_from"], "n_from": s["n_from"],
                        "units": s["units"], "vs_panjabi": s["vs_panjabi"], "definition": s["definition"],
                        "tables": "; ".join(sorted(s["tables"])), "pages": "; ".join(sorted(s["pages"], key=int))})
    return sorted(out, key=lambda r: tuple(str(r[c]) for c in COLUMNS[:9]))


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return "%.6g" % value
    return str(value)


def main():
    mapped, cohorts, out_path = sys.argv[1:4]
    series = build(read_mapped(mapped), cohort_people(cohorts))
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS)
        for s in series:
            w.writerow([fmt(s[c]) for c in COLUMNS])
    print("%d series from %s" % (len(series), mapped))


if __name__ == "__main__":
    main()
