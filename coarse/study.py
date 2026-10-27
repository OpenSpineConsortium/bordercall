"""Coarse claims a field of bodies supports when its exact level cannot be named: below T12,
below T5, and the others with a cited clinical use, measured world by world.

    python -m coarse --outdir coarse/records/coarse-2026-10-27

The owner's queue of 27 October 2026, 09:44 UTC, item 6, third line: "extend to other coarse
predictions such as below T12, below T5, and any others with citable clinically beneficial
utility". The exact rule's posterior over places is a posterior over the level of every body in
the field, so a coarse claim about one body is a sum of it: "the middle body is at or below L1"
is the posterior mass on L1 to L5. Made only when that sum reaches 0.99, a claim is right at
least 99 per cent of the times it is made while the generator is the truth, whatever the claim
(archive/bordercall/exact.py, guarantee 3); what varies from claim to claim is how often the
field lets one make it. The archive scores every border this way (exact.claims_summary); this
file names the borders and intervals that matter clinically, with the reason and a source for
each, and measures each one, by the plane the measures come from and in the worlds where the
scale is not what the rule assumes (combinations/study.py's worlds), where the guarantee is
tested rather than given.

The claims are about the middle body of the field (the upper of the two middle ones for an even
n, exact.target_offset), the body a marker or a needle would be set against. Each border claim
is two-sided: a field may say the body is below the border, or at or above it, or neither.

Every number is about synthetic columns drawn from Panjabi's tables; nothing here is a patient.
"""
from __future__ import annotations

import json
import math
import os
import time
from typing import Dict, List, Sequence

import numpy as np

from combinations import study as S
from combinations.study import EX, L, NB, P, SEVEN

LEVEL = 0.99
WIDTHS = (1, 3, 5, 9)
REGIMES = {"all seven": SEVEN,
           "AP film (EPWu, EPWl, SCW)": ["endplate", "endplate_lower", "canal_w"],
           "lateral film (EPDu, EPDl, VBHp, SCD)": ["endplate_depth", "endplate_lower_depth", "h_post", "canal_ap"]}

# Each claim: the border it is decided at (the first level below it) or the interval it names, and why it matters.
CLAIMS: List[dict] = [
    {"name": "below C7", "below": "T1",
     "use": "the cervicothoracic junction, where a body called cervical or thoracic decides the approach and "
            "the hardware; kept as a reference border, with no source checked here for its clinical use"},
    {"name": "below T5", "below": "T6",
     "use": "the upper end of the T5 to T12 sagittal curve, on which the Lenke classification of adolescent "
            "idiopathic scoliosis grades its sagittal thoracic modifier (under +10, +10 to +40, over +40 "
            "degrees) and so the extent of the fusion (Lenke LG et al. J Bone Joint Surg Am "
            "2001;83(8):1169-1181)"},
    {"name": "at or above T6", "above": "T6",
     "use": "autonomic dysreflexia follows spinal cord injury at or above T6, so the injured level's side of "
            "the T6/T7 border sets the monitoring (Krassioukov A, Warburton DE, Teasell R, Eng JJ. Arch Phys "
            "Med Rehabil 2009;90(4):682-695; the level is in the review's background, not its abstract)"},
    {"name": "below T12", "below": "L1",
     "use": "thoracic or lumbar: half of the spine surgeons surveyed reported operating at a wrong level at "
            "least once in their careers (Mody MG et al. Spine 2008;33(2):194-198), and the count from the "
            "lowest rib or the sacrum is the one a transitional column misleads"},
    {"name": "below L2", "below": "L3",
     "use": "the interspace for a spinal needle: anaesthetists identified a marked lumbar interspace "
            "correctly in only 29 per cent of patients and placed it one space higher than they assumed in 51 "
            "per cent (Broadbent CR et al. Anaesthesia 2000;55:1122-1126), and the conus was damaged where "
            "spinal anaesthesia was given above the intended space (Reynolds F. Anaesthesia "
            "2001;56:238-247)"},
    {"name": "within the thoracolumbar junction, T11 to L2", "interval": ["T11", "T12", "L1", "L2"],
     "use": "the junction of the rib-stiffened thoracic spine and the mobile lumbar spine; injuries of the "
            "thoracolumbar spine are classified and their treatment chosen by the Thoracolumbar Injury "
            "Classification and Severity Score (Vaccaro AR et al. Spine 2005;30(20):2325-2333)"},
]


def claim_mass(tp: np.ndarray, claim: dict) -> np.ndarray:
    """The posterior mass on the claim being true, per field, from the target's posterior."""
    lv = EX.LEVELS
    if "below" in claim:
        return tp[:, lv.index(claim["below"]):].sum(1)
    if "above" in claim:
        return tp[:, :lv.index(claim["above"]) + 1].sum(1)
    return tp[:, [lv.index(x) for x in claim["interval"]]].sum(1)


def claim_truth(level: np.ndarray, claim: dict) -> np.ndarray:
    lv = EX.LEVELS
    if "below" in claim:
        return level >= lv.index(claim["below"])
    if "above" in claim:
        return level <= lv.index(claim["above"])
    return np.isin(level, [lv.index(x) for x in claim["interval"]])


def border_of(claim: dict) -> float:
    """Where the claim's border sits on the level index, for 'within two levels of it'."""
    lv = EX.LEVELS
    if "below" in claim:
        return lv.index(claim["below"]) - 0.5
    if "above" in claim:
        return lv.index(claim["above"]) + 0.5
    return float("nan")


def score_claims(post: np.ndarray, truth: np.ndarray, group: np.ndarray, n: int) -> dict:
    """Every claim on every field of one width: how often it is decided at LEVEL either way, its
    precision overall and within two levels of its border, and, beside them, how often the
    middle body's exact level is named at LEVEL."""
    tp = EX.target_posterior(post, n)
    level = truth + EX.target_offset(n)
    named = tp.max(1) >= LEVEL
    out = {"named_exactly": round(float(named.mean()), 4), "n_named": int(named.sum()),
           "named_wrong": int((named & (tp.argmax(1) != level)).sum()), "claims": {}}
    gid = np.unique(group, return_inverse=True)[1]
    for c in CLAIMS:
        t = claim_truth(level, c)
        if t.all() or not t.any():
            out["claims"][c["name"]] = {"settled_by_field_size": True}
            continue
        m = claim_mass(tp, c)
        say_yes, say_no = m >= LEVEL, m <= 1.0 - LEVEL
        dec = say_yes | say_no
        wrong = (say_yes & ~t) | (say_no & t)
        row = {"decided": round(float(dec.mean()), 4), "n_decided": int(dec.sum()), "errors": int(wrong.sum()),
               "precision": round(float(1.0 - wrong.sum() / dec.sum()), 5) if dec.any() else None,
               "precision_se": EX.ratio_se(np.bincount(gid, weights=wrong), np.bincount(gid, weights=dec)),
               "said_true": round(float(say_yes.mean()), 4), "said_false": round(float(say_no.mean()), 4)}
        b = border_of(c)
        if not math.isnan(b):
            near = np.abs(level - b) <= 2.0
            nd = int((dec & near).sum())
            row.update({"decided_within_two": round(float(dec[near].mean()), 4) if near.any() else None,
                        "errors_within_two": int((wrong & near).sum()), "n_decided_within_two": nd})
        out["claims"][c["name"]] = row
    return out


def run(n_columns: int = S.N_COLUMNS, widths: Sequence[int] = WIDTHS, log=print) -> dict:
    ref = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
    mu7, sd7 = EX.table_arrays(ref, SEVEN)
    synth = dict(NB.SYNTH)
    V0 = EX.column_values(NB.draw_columns(ref, ["typical"], NB.SCORE_SEED, n_columns, SEVEN), SEVEN)
    record = {"columns": n_columns, "seed": NB.SCORE_SEED, "world_seed": S.WORLD_SEED, "level": LEVEL,
              "claims": CLAIMS, "widths": list(widths), "results": {}}
    jobs = [(w, r) for w in ("nominal", "film", "film, magnification wrong") for r in REGIMES
            if w == "nominal" or r == "all seven"]
    W = S.worlds(V0)
    for wname, regime in jobs:
        idx = [SEVEN.index(m) for m in REGIMES[regime]]
        mu, sd = mu7[idx], sd7[idx]
        w = W[wname]
        key = "%s | %s" % (wname, regime)
        record["results"][key] = {}
        for n in widths:
            t0 = time.time()
            X, truth, group = EX.fields(w["V"][:, idx, :], n)
            res = {"exact rule": score_claims(EX.posterior(S.exact_logev(X, mu, sd, synth, w["log_mean"], w["extra_sd"])),
                                              truth, group, n),
                   "scale-free exact rule": score_claims(S.invariant_posterior(X, mu, sd, synth), truth, group, n)}
            record["results"][key][str(n)] = res
            log("%-50s n=%d %.1fs" % (key, n, time.time() - t0))
    return record


def cell(r: dict) -> str:
    if r.get("settled_by_field_size"):
        return "settled"
    near = "" if r.get("decided_within_two") is None else ", %.3f near" % r["decided_within_two"]
    return "%.3f%s (%d of %d wrong)" % (r["decided"], near, r["errors"], r["n_decided"])


def table(record: dict, rule: str = "exact rule") -> str:
    """Per world and plane: for each claim and width, the share of fields decided at 0.99, the
    share decided among middle bodies within two levels of the border ("near"), and the errors
    among all decided; the first row is the middle body's exact level named at 0.99."""
    lines = []
    for key, by_n in record["results"].items():
        widths = list(by_n)
        lines += ["", "**%s, %s**" % (key, rule), "",
                  "| Claim about the middle body | " + " | ".join("n = %s" % n for n in widths) + " |",
                  "| --- |" + " --- |" * len(widths),
                  "| its exact level | " + " | ".join("%.3f (%d of %d wrong)" % (by_n[n][rule]["named_exactly"],
                                                                         by_n[n][rule]["named_wrong"], by_n[n][rule]["n_named"])
                                                       for n in widths) + " |"]
        for c in CLAIMS:
            lines.append("| %s | %s |" % (c["name"], " | ".join(cell(by_n[n][rule]["claims"][c["name"]]) for n in widths)))
    return "\n".join(lines)


def write(outdir: str, record: dict) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "coarse.json"), "w", newline="\n") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(outdir, "TABLE.md"), "w", newline="\n") as fh:
        fh.write("Share of fields where the claim is decided at posterior 0.99 (either way), the share among middle bodies\n"
                 "within two levels of the claim's border (near), and the errors among all decided.\n")
        fh.write(table(record, "exact rule") + "\n")
        fh.write(table(record, "scale-free exact rule") + "\n")
