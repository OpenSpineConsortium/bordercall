"""What the papers say of measurement error and of how often a column is not the typical one.

Both are set beside what the generator assumes. The errors come from the reread's synthesis part
on its branch (claude/project-thread-adplcz at 448006f, research_notes/clinical-reread/
synthesis/error.md), each with the line it stands on there and the paper it comes from. At 45130ac,
this note's first snapshot, that part was a draft no second reader had checked; since then it has
been read by an accuracy critic and four completeness critics and fixed (f067734, ad83cfc), so
it is cited at 448006f, the papers' notes staying the authority where the two differ; the
snapshot's commit, 401aaee, leaves it as it was at 448006f. The prevalences are the checked
priors (research_notes/clinical-reread/synthesis/anomaly-priors.md, the same at 45130ac, 448006f
and 401aaee), counts recomputed by a second reader against the rendered
pages, with Wilson intervals; each is of the population the paper names, not of an unselected one.
"""
from __future__ import annotations

import math
from typing import List, Sequence

from schwingcheck import LEVELS
from schwingcheck import measures as MS

# (what, modality, low, high, unit, source): an error SD of one reading (SEmeas), or the nearest figure printed
ERRORS = (
    ("body heights", "CT", 0.3, 0.65, "mm", "duman2026, 50 scans read again after 4 weeks; error.md L55"),
    ("pedicle width and height", "CT", 0.2, 0.55, "mm", "duman2026; error.md L65"),
    ("pedicle angle", "CT", 0.7, 1.8, "deg", "duman2026; error.md L73"),
    ("canal width and depth", "CT", 0.4, 1.2, "mm", "griffith2016, by level L1-L5; error.md L62"),
    ("canal area", "CT", 10.0, 30.0, "mm2", "griffith2016; error.md L62"),
    ("disc and end-plate diameters", "MRI", 0.5, 0.9, "mm", "tang2016, between observers; error.md L60"),
    ("disc and end-plate area", "MRI", 40.0, 40.0, "mm2", "tang2016, between observers; error.md L60"),
    ("pedicle width and height", "bone, caliper", 0.35, 0.95, "mm", "yu2015; error.md L67"),
    ("interpedicular distance", "film", 0.27, 0.27, "mm", "hinck1966, 89 duplicate readings; error.md L63"),
    ("one pig vertebra, CT repeated", "CT", 0.22, 0.22, "mm",
     "vanderhouwen2009, the mean of nine dimensions' SDs over three repeats; error.md L59"),
    ("CT against caliper", "CT and bone", 0.66, 0.66, "mm",
     "vanderhouwen2009 Fig. 4, 12 dimensions of 2 pig vertebrae, the caliper's own error in it; error.md L91"),
)

# (state, the generator's share, the chain's weight, the papers' point, low, high, source); NaN where
# the papers give no value and no bound
EQUAL_SHARE = 1.0 / 6.0      # model.py's generator draws its six phenotypes in equal shares
NONE = float("nan")
PREVALENCE = (
    ("six lumbar-type segments (L6 or lumbarised S1)", EQUAL_SHARE, 0.05, 0.0248, 0.0139, 0.0439,
     "eisenstein1977 p. 177, 11 / 443 dry skeletons (2 true L6, 9 lumbarised S1); anomaly-priors.md L11"),
    ("of which a true L6", None, None, 0.0045, 0.0012, 0.0163, "eisenstein1977 p. 177, 2 / 443; anomaly-priors.md L12"),
    ("four lumbar segments (sacralised L5), a ceiling", EQUAL_SHARE, None, 0.0181, 0.0092, 0.0352,
     "eisenstein1977 p. 177, 8 / 443; sacralisation undefined, so a ceiling; anomaly-priors.md L14"),
    ("a thirteenth rib-bearing body (T13)", EQUAL_SHARE, 0.05, NONE, NONE, NONE,
     "no count and no bound in the 43 papers; any value is a modelling choice; anomaly-priors.md L22"),
    ("a rib on the first lumbar-type body", EQUAL_SHARE, None, 0.0232, 0.0133, 0.0401,
     "duman2026 Table 5 p. 10, 12 / 517 adults' CTs at a chest hospital for other reasons; a T13 not told apart;"
     " anomaly-priors.md L21"),
    ("no twelfth rib, one side or both", EQUAL_SHARE, None, 0.0426, 0.0283, 0.0636,
     "duman2026 Table 5 p. 10, 22 / 517; a ceiling for bilateral absence, laterality never reported; anomaly-priors.md L23"),
)


def generator_errors(measures: Sequence[MS.Measure]) -> List[dict]:
    """The error the generator adds to each measure (measures.error_of): 1 mm for a length,
    sqrt(pi A / 2) for an area of mean A over the levels, 3 degrees for an angle; beside the
    measure's SD at L3 in Panjabi's table, the share of a person's spread the error is."""
    mu, sd = MS.arrays(list(measures), LEVELS)
    i = LEVELS.index("L3")
    return [{"measure": m.key.split(":")[0], "kind": m.kind, "error": float(m.error), "mean_l3": float(mu[j, i]),
             "sd_l3": float(sd[j, i]), "error_over_sd_l3": float(m.error / sd[j, i])} for j, m in enumerate(measures)]


def wilson(k: int, n: int, z: float = 1.959964) -> tuple:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
