"""Where every numeric table of the four Panjabi papers sits on its rendered page.

Each table is described by the page it is printed on, the pixel region it occupies on the
300-dpi render (render.py), the line that carries the column labels, the body below it, the
right edge of the row-label column, and the rows and columns in print order. layout.py reads
the pixels inside the region to find each line of print and each run of ink in it, and this
file says what those lines and runs mean. Nothing here is a value: the values are read from
the images, twice, by eye (README.md).

Two tables are nomenclature (cervical Table 1, lumbar Table 1, facets Table 1) and the
thoracic Table 2 is nomenclature too; they print no number and are left out. The thoracic
body table (Table 3, printed page 892) is on a page the thoracic scan does not carry (the
PDF goes from page 891 to 893): it is read from a one-page file of its own, named by its
`source`, render.py's key for that file (the owner's second scan, 27 October 2026).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Row:
    label: str
    statistic: str | None = None     # mean, sem, ratio, value, text, or None when the column decides
    fmt: str | None = None           # num, pm, paren, ratio, text, section, continuation
    level: str | None = None
    span: int = 1                    # lines of print this row occupies


@dataclass
class Col:
    label: str
    fmt: str | None = None
    level: str | None = None
    statistic: str | None = None


@dataclass
class Table:
    key: str
    paper: str
    page: int                        # page of the PDF
    printed: int                     # page number printed on it
    title: str
    x: tuple[int, int]
    header: tuple[int, int]          # the line of column labels
    body: tuple[int, int]
    label_x: int                     # ink ending left of this is a row label, not a value
    rows: list[Row]
    cols: list[Col]
    min_gap: int = 28                # ink gaps narrower than this stay inside one cell
    col_edges: list[int] | None = None   # explicit column boundaries where the print is skewed
    axis: str = "cols"               # which axis carries the vertebral level: cols or rows
    note: str = ""
    source: str = ""                 # render.py's key of the file the page is in, when not the paper's own
    ink: int = 0                     # grey below this is ink on this page, where layout.py's INK is too strict


CERVICAL = ["C%d" % i for i in range(2, 8)]
THORACIC = ["T%d" % i for i in range(1, 13)]
LUMBAR = ["L%d" % i for i in range(1, 6)]
C2_TO_L5 = CERVICAL + THORACIC + LUMBAR


def lines(mn: str) -> list[Row]:
    """A 1991-paper parameter: the mean on one line of print, its standard error on the next."""
    return [Row(mn, "mean", "num"), Row(mn, "sem", "num")]


def single(mn: str, statistic: str = "ratio") -> list[Row]:
    return [Row(mn, statistic, "num" if statistic != "ratio" else "ratio")]


def pm(mn: str) -> list[Row]:
    """A lumbar-paper parameter: 'mean +/- SEM' in one cell."""
    return [Row(mn, None, "pm")]


def section(text: str) -> list[Row]:
    return [Row(text, None, "section")]


def cont(text: str) -> list[Row]:
    return [Row(text, None, "continuation")]


def compare(mn: str, levels: list[str]) -> list[Row]:
    return [Row(mn, "mean", None, level=lv) for lv in levels]


def levels(fmt: str | None = None) -> list[Row]:
    return [Row(lv, None, fmt, level=lv) for lv in C2_TO_L5]


def level_cols(names: list[str]) -> list[Col]:
    return [Col(n, level=n) for n in names]


def measure_cols(names: list[str], ratio: tuple[str, ...] = ()) -> list[Col]:
    return [Col(n, "ratio" if n in ratio else "paren") for n in names]


def compare_cols(studies: list[str]) -> list[Col]:
    return [Col("Level", "label", statistic="label")] + [Col(s, "num", statistic="mean") for s in studies]


TABLES: list[Table] = [
    # ---- cervical, Spine 1991;16(8):861-869 ------------------------------------------
    Table("cervical-t2", "cervical", 3, 863, "Table 2. Vertebral Body Dimensions",
          x=(215, 2266), header=(2101, 2168), body=(2172, 3068), label_x=600,
          rows=section("Linear dimensions (mm)") + lines("EPDu") + lines("EPWu") + lines("EPDl")
          + lines("EPWl") + lines("VBHp") + single("EPWu/EPDu") + single("EPWl/EPDl")
          + section("Surface area (mm2)") + lines("EPAu") + lines("EPAl")
          + section("Angular dimensions (deg)") + lines("EPItu") + lines("EPItl"),
          cols=level_cols(CERVICAL)),
    Table("cervical-t3", "cervical", 4, 864, "Table 3. Spinal Canal Dimensions",
          x=(270, 2330), header=(424, 490), body=(495, 861), label_x=600,
          rows=section("Linear dimensions (mm)") + lines("SCW") + lines("SCD") + single("SCW/SCD")
          + section("Cross-sectional areas (mm2)") + lines("SCA"),
          cols=level_cols(CERVICAL)),
    Table("cervical-t4", "cervical", 4, 864, "Table 4. Pedicle Dimensions",
          x=(270, 2330), header=(1254, 1319), body=(1326, 2297), label_x=620,
          rows=section("Linear Dimensions (mm)") + lines("PDWr") + lines("PDHr") + lines("PDWl")
          + lines("PDHl") + single("PDHr/PDWr") + single("PDHl/PDWl")
          + section("Cross-sectional areas (mm2)") + lines("PDAr") + lines("PDAl")
          + section("Angular Dimensions (deg)") + lines("PDIsr") + lines("PDItr") + lines("PDIsl")
          + lines("PDItl"),
          cols=level_cols(CERVICAL)),
    Table("cervical-t5", "cervical", 4, 864, "Table 5. Spinous Process and Transverse Process",
          x=(270, 1270), header=(2687, 2755), body=(2758, 2976), label_x=400,
          rows=section("Linear Dimensions (mm)") + lines("SPL") + lines("TPW"),
          cols=level_cols(CERVICAL)),
    Table("cervical-t6", "cervical", 5, 865, "Table 6. Uncovertebral Joints",
          x=(220, 2300), header=(440, 493), body=(500, 1203), label_x=600,
          rows=section("Surface Areas (mm2)") + lines("UJAru") + lines("UJAlu") + lines("UJArl")
          + lines("UJAll") + section("Angular Dimensions (deg)") + lines("UJIfu") + lines("UJIsu")
          + lines("UJIfl") + lines("UJIsl"),
          cols=level_cols(CERVICAL)),
    Table("cervical-t7", "cervical", 8, 868, "Table 7. Comparison with Previous Studies",
          x=(1330, 2340), header=(340, 430), body=(435, 1790), label_x=1500,
          rows=compare("EPDl", CERVICAL) + compare("EPWl", CERVICAL) + compare("EPAl", CERVICAL)
          + compare("SCD", CERVICAL) + compare("SCW", CERVICAL) + compare("VBH", CERVICAL[1:]),
          cols=compare_cols(["Present Study", "Liu (1986)", "Nissan (1984)", "Francis (1952)"]),
          axis="rows"),
    # ---- thoracic, Spine 1991;16(8):888-901 ------------------------------------------
    Table("thoracic-t1", "thoracic", 2, 889, "Table 1. Spine Specimen Data",
          x=(220, 2275), header=(380, 434), body=(440, 918), label_x=0, min_gap=60,
          rows=[Row("S%d" % n, None, None) for n in (3, 4, 7, 9, 10, 13, 14, 15, 20, 22, 23, 24)],
          cols=[Col("Specimen No.", "label", statistic="label"), Col("Age", "num", statistic="value"),
                Col("Sex", "text", statistic="text"), Col("Weight (kg)", "num", statistic="value"),
                Col("Height (cm)", "num", statistic="value"), Col("Cause of death", "text", statistic="text")],
          axis="rows"),
    Table("thoracic-t3", "thoracic", 1, 892, "Table 3. Vertebral Body Dimensions (See Figure 3 and Table 2 for Nomenclature)",
          x=(70, 2500), header=(493, 519), body=(540, 1512), label_x=260,
          rows=section("Linear dimensions (mm)") + lines("EPWu") + lines("EPDu") + lines("EPWl")
          + lines("EPDl") + lines("VBHp") + single("EPWu/EPDu") + single("EPWl/EPDl")
          + section("Cross-sectional area (mm2)") + lines("EPAu") + lines("EPAl")
          + section("Angular dimension (deg)") + lines("EPItu") + lines("EPItl") + single("EPIt", "mean"),
          cols=level_cols(THORACIC), source="thoracic-p892", ink=170,
          note="Printed page 892 is not in the thoracic scan the other tables were read from (its page 4 is 891 and "
               "its page 5 is 893); this table is read from the one-page file the owner supplied on 27 October 2026, "
               "a landscape scan whose table reads upright with no turn and prints its lightest digits paler than "
               "the other scans (two ratio cells, T7 and T12 of EPWu/EPDu, reach grey 140 in four pixels or fewer), "
               "so ink on this page is grey below 170. Its last row, EPIt, prints one line, a mean with no standard error."),
    Table("thoracic-t4", "thoracic", 5, 893, "Table 4. Spinal Canal Dimensions",
          x=(200, 2300), header=(456, 490), body=(498, 832), label_x=400,
          rows=section("Liner dimensions (mm)") + lines("SCW") + lines("SCD") + single("SCW/SCD")
          + section("Cross-sectional area (mm2)") + lines("SCA"),
          cols=level_cols(THORACIC)),
    Table("thoracic-t5", "thoracic", 6, 894, "Table 5. Pedicle Dimensions",
          x=(130, 2990), header=(800, 850), body=(860, 2060), label_x=340,
          rows=section("Linear dimensions (mm)") + lines("PDWr") + lines("PDWl") + lines("PDHr")
          + lines("PDHl") + single("PDH/PDWr") + single("PDH/PDWl")
          + section("Cross-sectional area (mm2)") + lines("PDAr") + lines("PDAl")
          + section("Angular dimensions (deg)") + lines("PDIsr") + lines("PDIsl") + lines("PDItr")
          + lines("PDItl"),
          cols=level_cols(THORACIC)),
    Table("thoracic-t6", "thoracic", 7, 895, "Table 6. Rib and Processes Dimensions",
          x=(150, 3000), header=(345, 395), body=(398, 1030), label_x=400,
          rows=section("Costovertebral articulation area") + lines("CVAur") + lines("CVAul")
          + lines("CVAlr") + lines("CVAll") + single("CVA", "mean") + cont("total per rib")
          + lines("CTAr") + lines("CTAl") + single("CVA + CTA", "mean") + cont("total per rib"),
          cols=level_cols(THORACIC),
          note="The T11 column is set left of its heading and the T12 entries of CTAr and CTAl stand on the lower line; "
               "the label of the last row, CVA + CTA, runs past x=300, so the labels' edge is 400 here."),
    Table("thoracic-t7", "thoracic", 7, 895, "Table 7. Pars Intra-Articularis, Spinous, and Transverse Processes",
          x=(150, 3000), header=(1705, 1755), body=(1758, 2165), label_x=300,
          rows=section("Cross-sectional area (mm2)") + [Row("PIAr", "mean", "num", span=2), Row("PIAr", "sem", "num")]
          + lines("PIAl") + section("Linear dimensions (mm)") + lines("SPL") + lines("TPW"),
          cols=level_cols(THORACIC),
          note="The PIAr means take two lines of print: the dashes of T1 and T2 on the first, the values of T3 to T12 on the second."),
    Table("thoracic-t8a", "thoracic", 11, 899, "Table 8. Comparison of Our Results with Those of Previous Studies",
          x=(230, 2320), header=(390, 479), body=(488, 3190), label_x=560,
          rows=section("Linear dimensions (mm)") + compare("EPDl", THORACIC) + compare("EPWl", THORACIC)
          + compare("VBHp", THORACIC) + compare("SCD", THORACIC) + compare("SCW", THORACIC)
          + compare("PDH", THORACIC[:10]),
          cols=compare_cols(["Present Study", "Berry (1987)", "Zindrick (1987)", "Scoles (1988)",
                             "Krag (1986, 1988)", "Cotterill (1986)"]),
          axis="rows"),
    Table("thoracic-t8b", "thoracic", 12, 900, "Table 8 (Continued)",
          x=(250, 2320), header=(380, 468), body=(476, 1976), label_x=600,
          rows=compare("PDH", THORACIC[10:]) + compare("PDW", THORACIC)
          + section("Angular dimension (deg)") + compare("PDIs", THORACIC) + compare("PDIt", THORACIC),
          cols=compare_cols(["Present Study", "Berry (1987)", "Zindrick (1987)", "Scoles (1988)",
                             "Krag (1986, 1988)", "Cotterill (1986)"]),
          axis="rows"),
    # ---- lumbar, Spine 1992;17(3):299-306 --------------------------------------------
    Table("lumbar-t2", "lumbar", 3, 301, "Table 2. Vertebral Body Dimensions",
          x=(204, 2283), header=(2456, 2522), body=(2528, 3083), label_x=500,
          rows=section("Linear dimensions (mm)") + pm("EPDu") + pm("EPWu") + pm("EPDl") + pm("EPWl")
          + pm("VBHp") + single("EPWu/EPDu") + single("EPWl/EPDl")
          + section("Surface Areas (mm2)") + pm("EPAu") + pm("EPAl")
          + section("Angular dimensions (deg)") + pm("EPItu") + pm("EPItl"),
          cols=level_cols(LUMBAR)),
    Table("lumbar-t3", "lumbar", 4, 302, "Table 3. Spinal Canal Dimensions",
          x=(256, 2340), header=(402, 467), body=(474, 726), label_x=500,
          rows=section("Linear dimensions (mm)") + pm("SCW") + pm("SCD") + single("SCW/SCD")
          + section("Cross-sectional areas (mm2)") + pm("SCA"),
          cols=level_cols(LUMBAR)),
    Table("lumbar-t4", "lumbar", 4, 302, "Table 4. Pedicle Dimensions",
          x=(256, 2340), header=(1131, 1197), body=(1202, 1797), label_x=600,
          rows=section("Linear dimensions (mm)") + pm("PDWr") + pm("PDHr") + pm("PDWl") + pm("PDHl")
          + single("PDHr/PDWr") + single("PDHl/PDWl")
          + section("Cross-sectional areas (mm2)") + pm("PDAr") + pm("PDAl")
          + section("Angular dimensions (deg)") + pm("PDIsr") + pm("PDItr") + pm("PDIsl") + pm("PDItl"),
          cols=level_cols(LUMBAR)),
    Table("lumbar-t5", "lumbar", 6, 304, "Table 5. Pars Interarticularis, Spinous Process, and Transverse Process",
          x=(260, 2345), header=(2684, 2747), body=(2754, 3006), label_x=560,
          rows=section("Cross-sectional area (mm2)") + pm("PIAr") + pm("PIAl")
          + section("Linear dimensions (mm)") + pm("SPL") + pm("TPW"),
          cols=level_cols(LUMBAR)),
    Table("lumbar-t6", "lumbar", 7, 305, "Table 6. Comparison of Results of Present Study to Those of Previous Studies",
          x=(200, 2290), header=(330, 421), body=(428, 2229), label_x=440,
          rows=section("Linear dimensions (mm)") + compare("EPDl", LUMBAR) + compare("EPWl", LUMBAR)
          + compare("VBHp", LUMBAR) + compare("SCD", LUMBAR) + compare("SCW", LUMBAR)
          + compare("PDH", LUMBAR) + compare("PDW", LUMBAR)
          + section("Angular dimension (deg)") + compare("PDIs", LUMBAR) + compare("PDIt", LUMBAR),
          cols=compare_cols(["Present Study", "Berry (1987)", "Zindrick (1987)", "Scoles (1988)",
                             "Krag (1986, 1988)", "Cotterill (1986)", "Gilad (1986)"]),
          axis="rows"),
    # ---- facets, Spine 1993;18(10):1298-1310 -----------------------------------------
    Table("facets-t2", "facets", 4, 1301, "Table 2. Means (and Standard Errors of the Mean) of the Superior Articular Facet Linear Dimensions",
          x=(260, 2330), header=(430, 490), body=(500, 1410), label_x=420,
          rows=levels(), cols=measure_cols(["FCWsr", "FCWsl", "FCHsr", "FCHsl", "FCW/FCHsr", "FCW/FCHsl"],
                                           ratio=("FCW/FCHsr", "FCW/FCHsl")), axis="rows"),
    Table("facets-t3", "facets", 4, 1301, "Table 3. Means (and Standard Errors of the Mean) of the Inferior Articular Facet Linear Dimensions",
          x=(260, 2330), header=(1630, 1695), body=(1702, 2618), label_x=420,
          rows=levels(), cols=measure_cols(["FCWir", "FCWil", "FCHir", "FCHil", "FCW/FCHir", "FCW/FCHil"],
                                           ratio=("FCW/FCHir", "FCW/FCHil")), axis="rows"),
    Table("facets-t4", "facets", 5, 1302, "Table 4. Means (and Standard Errors of the Mean) of the Superior and Inferior Articular Facet Surface Areas",
          x=(270, 2340), header=(405, 472), body=(478, 1392), label_x=420,
          rows=levels(), cols=measure_cols(["FCAsr", "FCAsl", "FCAir", "FCAil"]), axis="rows"),
    Table("facets-t5", "facets", 5, 1302, "Table 5. Means (and Standard Errors of the Mean) of the Interfacet Distances",
          x=(270, 2340), header=(1610, 1680), body=(1686, 2640), label_x=420,
          rows=levels(), cols=measure_cols(["IFWs", "IFWi", "IFHr", "IFHl", "IFWs/IFWi", "IFW/IFH"],
                                           ratio=("IFWs/IFWi", "IFW/IFH")), axis="rows"),
    Table("facets-t6", "facets", 6, 1303, "Table 6. Means (and Standard Errors of the Mean) of the Superior Articular Facet Orientations with Respect to the Anatomic Planes: Transverse and Sagittal",
          x=(240, 2305), header=(440, 514), body=(520, 1416), label_x=400,
          rows=levels(), cols=measure_cols(["Tsr", "Ssr", "Tsl", "Ssl"]), axis="rows"),
    Table("facets-t7", "facets", 6, 1303, "Table 7. Means (and Standard Errors of the Mean) of the Inferior Articular Facet Orientations with Respect to the Anatomic Planes: Transverse and Sagittal",
          x=(240, 2305), header=(1700, 1770), body=(1776, 2682), label_x=400,
          rows=levels(), cols=measure_cols(["Tir", "Sir", "Til", "Sil"]), axis="rows"),
    Table("facets-t8", "facets", 7, 1304, "Table 8. Average Card Angles for the Superior and Inferior Articular Facets",
          x=(270, 2340), header=(410, 482), body=(488, 1388), label_x=440,
          rows=levels("num"), cols=[Col(n, "num", statistic="mean") for n in
                                    ["CAXsr", "CAYsr", "CAXsl", "CAYsl", "CAXir", "CAYir", "CAXil", "CAYil"]],
          axis="rows"),
    Table("facets-t9", "facets", 11, 1308, "Table 9. Comparison with Previous Studies: Linear Dimensions, Facet and Interfacet Widths and Heights",
          x=(240, 2320), header=(390, 460), body=(466, 1200), label_x=600,
          rows=compare("FCHs", CERVICAL) + compare("FCWs", CERVICAL) + compare("IFWs", ["T6", "T12", "L3"])
          + compare("IFH", ["T6", "T12", "L3"]),
          cols=compare_cols(["Present Study", "Francis (1955)", "Cotterill (1986)"]), axis="rows"),
    Table("facets-t10", "facets", 11, 1308, "Table 10. Comparison with Previous Studies: Angular Dimensions and Sagittal Plane Angle of Superior Vertebrae",
          x=(240, 2320), header=(2725, 2797), body=(2803, 3146), label_x=400,
          rows=compare("Ss", ["T11", "T12", "L1", "L2", "L3", "L4", "L5", "S1"]),
          cols=compare_cols(["Present Study", "Malmivaara (1987)", "Ahmed (1990)", "Van Schaik (1985)",
                             "Horwitz & Smith (1940)"]), axis="rows"),
]

def by_key() -> dict[str, Table]:
    return {t.key: t for t in TABLES}
