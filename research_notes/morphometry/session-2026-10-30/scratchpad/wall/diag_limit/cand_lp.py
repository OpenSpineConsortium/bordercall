"""Candidate readers from the information limit: the widest-margin surface y = a + b z + c x + d x^2
parting the vertebra's own label (bone) from what it does not hold (the canal) on the scan's
lattice, over posterior_wall_slope's region (cand_x3_h60) or a wider one (cand_x6_h80), with the
range of slopes the mask leaves free in info. Diagnostic only: not a proposed change of code."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import limit as L  # noqa: E402


def reader(v, B, xc, across, cut):
    lo, hi, s, i = L.region(v, B, xc, across, cut)
    q, ijk = L.lattice(v, xc, lo, hi, s, i, across)
    got = L.part(q, v.is_bone(ijk), xc, 4)
    if not got.get("ok"):
        return float("nan"), {"why": got.get("why", "")}
    return got["b_mm"], {"width_deg": L.deg(got["b_hi"]) - L.deg(got["b_lo"]), "margin": got["margin"],
                         "parts": float(got["parts"])}


def cand_x3_h60(v, B, xc):
    return reader(v, B, xc, 3.0, 0.2)


def cand_x6_h80(v, B, xc):
    return reader(v, B, xc, 6.0, 0.1)
