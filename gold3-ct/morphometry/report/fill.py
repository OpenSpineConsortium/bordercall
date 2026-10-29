"""Fill the report template from the fragments below; the phantom block reads phantom.json when it exists."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "pending"

LEDE = ("All 228 thin-slice studies are measured, and every measure can be drawn on the slices where it is taken. "
        "The measures are tested against five kinds of truth. The masks sit on the bone's edge to within a few "
        "tenths of a millimetre, and the thin and thick scans agree. Three measures are wrong because of how "
        "they are built, so they are held back until the code changes. The VerSe test waits on its helper thread.")


def phantom():
    path = os.path.join(HERE, "phantom.json")
    if os.path.exists(path):
        return json.load(open(path))
    return {"chip": ("run", "running"),
            "ledger": "20 tests pass, holding lengths to 0.75 mm, angles to 1.5 degrees and areas to 4 per cent. "
                      "The sweep over slices from 1 to 5 mm is still running.",
            "text": "<p>The phantom draws lumbar vertebrae whose every measure is fixed by their parameters. Its "
                    "20 tests pass, holding lengths to 0.75 mm, angles to 1.5 degrees and areas to 4 per cent. On "
                    "2.5 mm slices, over 22 tilts and turns, heights read 0.6 to 0.7 mm tall on average and discs "
                    "0.6 to 0.8 mm short, with errors up to about one slice. The sweep over four slice thicknesses "
                    "(1, 1.25, 2.5 and 5 mm), three tilts and two grid turns is still running; its figure follows.</p>",
            "figure": None}


def chip(kind, text):
    return '<span class="chip %s">%s</span>' % (kind, text)


def ledger():
    p = phantom()
    rows = [
        ("Measure every thin-slice study", ("ok", "done"),
         "228 of 229 measured; one (0980) stopped on an error. That gives 452,546 rows: 79 measures for each "
         "vertebra, 12 for each disc, 13 for the pelvis and 6 for the column. The rows stay in the project's "
         "files."),
        ("Draw each measure on its slices", ("ok", "done"),
         "Study 0004 at C5, T1, T8, L3, L4 and L5. Every line was rebuilt from the measuring code, and all 150 "
         "matched the run's rows."),
        ("Phantom with known shapes", p["chip"], p["ledger"]),
        ("Mask surface against the CT's bone", ("ok", "done"),
         "Three CTs, 69 vertebrae. The body's walls and the arch sit 0.07 to 0.34 mm from the bone's edge, and the "
         "end-plates 0.34 and 0.72 mm. A height reads 0.37 mm short and a width 0.14 mm wide."),
        ("Discs in the CT", ("ok", "done"),
         "The masks take in 0.47 mm of each cervical disc and 0.11 mm of each thoracic one. They leave each lumbar "
         "disc 0.31 mm wider than the CT shows."),
        ("Thick slices", ("ok", "done"),
         "Three studies thinned to 2.5 and 5 mm slices. The median of every measure moves by less than 0.9 mm."),
        ("Published adult means", ("ok", "done"),
         "39 papers, 4,476 rows. Against CT papers our heights read 4.2 mm taller in front and 1.7 mm behind, and "
         "the end-plate's width 9.4 mm wider. The papers differ among themselves by as much."),
        ("Canal shape", ("ok", "done"),
         "At L4, L5 and in the neck, the front half of the canal is 3.4 to 9.8 mm wider than its middle. "
         "The interpedicular distance is read across the middle."),
        ("Measures held back", ("bad", "held back"),
         "Three are held back: the interpedicular distance at L4, L5 and in the neck; the pedicle's width and "
         "height in the neck, at C7 and at T1; and the mid-disc height in the neck and the upper thorax."),
        ("VerSe heights against readers' grades", ("wait", "waiting"),
         "This is the helper thread you approved. It tests 3,548 vertebrae of 331 patients graded by two readers, "
         "and is never pooled with ENHANCE.PET."),
        ("Repaired masks 1347, 1283, 1134", ("wait", "not started"),
         "Each published mask measured against its repaired copy, at 3 mm."),
        ("Suites, review and merge", ("wait", "not started"),
         "All suites, then an adversarial review written into PR 30, then the merge."),
    ]
    out = []
    for piece, (kind, text), result in rows:
        out.append('          <tr><td>%s</td><td>%s</td><td class="result">%s</td></tr>' % (piece, chip(kind, text), result))
    return "\n".join(out)


RENDERS = [
    ("C5", "<b>C5.</b> The masks of C4, C5 and C6 nearly touch, so the three disc heights read between -0.7 and "
           "1.6 mm (A); the CT itself shows these discs about 3 mm tall (the disc test, below). The right pedicle's "
           "chord leaves bone after 6.25 mm, and the left pedicle is too short front to back to give an axis (D). "
           "Cervical discs and chords are held back."),
    ("T1", "<b>T1.</b> At the isthmus each pedicle's cut is an island 13 to 14 mm square (C), about twice the "
           "papers' 7.7 mm. The cut takes in more than the pedicle, so T1's pedicle width and height are held back. "
           "This body reads 33.1 mm across its end-plate, whole and alone in its coronal cut (B), so it does not "
           "explain the run's median of 40.2 mm at T1."),
    ("T8", "<b>T8.</b> The pedicles read 7.6 and 5.9 mm wide and 14.7 and 14.1 mm tall (C), and the discs 1.8 to "
           "3.0 mm (A). The lower end-plate's width, 36.6 mm, runs past the body's outline in this cut (B). It is "
           "read across a slab, and that slab holds bone at the rim that this cut does not. It reads 8.8 mm wider "
           "than the waist."),
    ("L3", "<b>L3.</b> The lower end-plate's width, 47.6 mm, runs from one lip of the rim to the other, 9 mm wider "
           "than the waist a few millimetres above it (B). The whole run shows the same excess at every level from "
           "T2 to L5. The left pedicle's chord is 14 mm longer than the right because its axis climbs 10.5 degrees "
           "and runs into the posterior elements higher up (D)."),
    ("L4", "<b>L4.</b> The lower end-plate's depth, 34.5 mm, runs about 5 mm behind the posterior wall, while the "
           "upper end-plate's, 26.5 mm, stops at the wall (A). It is not yet known whether this is a lip at the "
           "back of the rim or other bone the slab takes in. This is one body; drawing more studies will show "
           "whether it is common."),
    ("L5", "<b>L5.</b> The interpedicular distance, 23.4 mm, is drawn across the middle of the canal, behind the "
           "pedicles, where the trefoil canal narrows; between the pedicles the canal is 27.6 mm wide (D). The "
           "pedicles' islands take in the root of the transverse process (C). Both measures are held back at L5."),
]


def renders():
    out = []
    for level, cap in RENDERS:
        out.append('      <figure>\n        <div class="plate"><img src="fig/render-0004-%s.png" alt="Study 0004, %s: '
                   'the measures drawn on sagittal, coronal and axial cuts of the vertebra\'s mask" loading="lazy"></div>\n'
                   '        <figcaption>%s</figcaption>\n      </figure>' % (level, level, cap))
    return "\n".join(out)


def block(title, kind, text, truth, body, fig=None, alt=""):
    img = ""
    if fig:
        img = ('\n      <figure><div class="plate"><img src="fig/%s" alt="%s" loading="lazy"></div></figure>' % (fig, alt))
    return ('    <div class="bench">\n      <div class="head"><h3>%s</h3>%s<span class="truth">truth: %s</span></div>\n'
            '      <div class="prose">%s</div>%s\n    </div>' % (title, chip(kind, text), truth, body, img))


DISC_TABLE = """<table class="ledger"><thead><tr><th>Region</th><th>Discs</th><th>Masks' gap</th><th>CT's disc</th><th>Gap less disc</th></tr></thead><tbody>
<tr><td>cervical</td><td class="result">14</td><td class="result">2.60 mm</td><td class="result">3.15 mm</td><td class="result">-0.47 (-0.66 to -0.34)</td></tr>
<tr><td>thoracic</td><td class="result">16</td><td class="result">3.00 mm</td><td class="result">3.48 mm</td><td class="result">-0.11 (-0.62 to +0.19)</td></tr>
<tr><td>lumbar</td><td class="result">10</td><td class="result">7.90 mm</td><td class="result">7.46 mm</td><td class="result">+0.31 (+0.04 to +0.44)</td></tr>
</tbody></table>"""

PAPERS_TABLE = """<table class="ledger"><thead><tr><th>Measure</th><th>Ours less the CT papers' means</th><th>Rows, papers</th></tr></thead><tbody>
<tr><td>end-plate width</td><td class="result">+9.4 mm</td><td class="result">54, 5</td></tr>
<tr><td>end-plate depth</td><td class="result">+6.1 mm</td><td class="result">40, 4</td></tr>
<tr><td>anterior height</td><td class="result">+4.2 mm</td><td class="result">58, 5</td></tr>
<tr><td>posterior height</td><td class="result">+1.7 mm</td><td class="result">58, 5</td></tr>
<tr><td>waist width</td><td class="result">+2.2 mm</td><td class="result">5, 1</td></tr>
<tr><td>mid-disc height</td><td class="result">-0.4 mm</td><td class="result">75, 2</td></tr>
<tr><td>canal depth at the pedicles</td><td class="result">+1.7 mm</td><td class="result">48, 6</td></tr>
<tr><td>pedicle width</td><td class="result">+2.6 mm</td><td class="result">112, 8</td></tr>
<tr><td>interpedicular distance (against films)</td><td class="result">-4.2 mm</td><td class="result">32, 3</td></tr>
</tbody></table>"""


def bench():
    p = phantom()
    kind, text = p["chip"]
    parts = [block("Phantom with known shapes", kind, text, "the phantom's own parameters", p["text"], p["figure"],
                   "Each phantom measure less its truth, by slice thickness")]
    parts.append(block(
        "Mask surface against the CT's bone", "ok", "done", "the bone's half-maximum edge in the CT",
        "<p>Along the outward normal of each mask's surface, the CT's bone edge is found and compared with the "
        "mask, at up to 400 points per region. On the phantom the exact mask reads +0.14 to +0.20 mm. A mask grown "
        "or shrunk by one voxel moves the reading by about a voxel, as it should. On three ENHANCE.PET CTs, over 69 "
        "vertebrae, the lateral wall reads -0.07 mm, the anterior +0.13, the posterior -0.21 and the arch -0.34; "
        "a positive offset means bone beyond the mask. A height measured on the masks reads 0.37 mm short and a "
        "width 0.14 mm wide. Each mask also sits 0.44 to 0.77 mm off its CT along the column, which way depending "
        "on the study. No measure here is taken across mask and CT together, so none is moved by it.</p>",
        "maskedge.png", "Offsets of the bone's edge from the mask by region, phantom and three CTs"))
    parts.append(block(
        "Discs in the CT", "ok", "done", "the disc the CT shows",
        "<p>Each disc is read along 25 lines through the middle of the body below it. On the phantom's 10 mm discs, "
        "the CT's reading stays put when the mask is grown or shrunk, while the masks' gap moves by about a voxel. "
        "On the three CTs:</p><div class=\"wrap\">" + DISC_TABLE + "</div>"
        "<p>The run's own mid-disc height also reads 1.35 mm short of the masks' gap in the neck, because of its "
        "rule for finding each plate's surface. That is why it is held back there.</p>",
        "disc.png", "Disc height in the CT against the masks' gap, phantom and three CTs"))
    parts.append(block(
        "Thick slices", "ok", "done", "the same patient's thin scan",
        "<p>Three thin studies were read again keeping one slice in every three or four (about 2.8 to 3.0 mm), and "
        "in every five or seven (about 5 mm), as a clinical scan would hold them. The median of every measure "
        "moves by less than 0.9 mm. At 5 mm the heights rise by 0.6 to 0.8 mm and the mid-disc height drops 0.8 mm, "
        "and the middle half of the vertebrae's own changes reaches about 2 mm either way. That is why the comparison with the "
        "papers uses only the thin studies.</p>",
        "thicken.png", "Change of each measure from the thin scan at 2.5 and 5 mm"))
    parts.append(block(
        "Published adult means", "ok", "done", "39 papers, 4,476 rows of adults measured by people",
        "<p>Only adult humans are compared, and each paper's technique is kept apart. These are the medians of the "
        "rows' differences against CT papers:</p><div class=\"wrap\">" + PAPERS_TABLE + "</div>"
        "<p>The papers disagree with each other by as much. At T8, three series give anterior heights of 20.1, "
        "17.0 and 16.1 mm against our 21.1. The smallest series, ten cadavers, weighs in nearly every body "
        "comparison. The end-plate's width is read on the rim's flare and its lips, which the renders show.</p>",
        "papers.png", "Ours by level beside the papers' adult means for ten measures"))
    parts.append(block(
        "VerSe heights against readers' grades", "wait", "waiting", "two readers' Genant grades, on masks we did not make",
        "<p>VerSe 19 and 20 provide 3,548 thoracic and lumbar vertebrae of 331 patients. A neuroradiologist and a "
        "resident graded each vertebra independently. This is the one test of our heights against human reads on "
        "masks we did not make. The helper thread you approved is reading VerSe's 473 masks (1,428,261,472 bytes) "
        "and the 11,823-byte grade table. Its results will be kept apart from ENHANCE.PET, never pooled. No open "
        "CT set gives per-case canal, pedicle or facet dimensions measured by people, so those can only be tested "
        "against the phantom and the papers.</p>"))
    return "\n".join(parts)


NEXT = [
    "Read the interpedicular distance between the pedicles, at their own place front to back, instead of across "
    "the canal's middle. Changing the code means every study is measured again, about an hour and a half here.",
    "Define the cervical pedicle so its cut keeps out the lateral mass and the bar behind the transverse foramen, "
    "and do the same at C7 and T1.",
    "Separate L5's pedicle from the root of its transverse process.",
    "Change the disc rule so it reads a plate's typical surface rather than its outermost point.",
    "Fix the neck's body cut where no transverse foramen is found closed (C3 to C7 in 89 to 186 of the 228 studies).",
    "Draw the studies at the top of T1's end-plate spread, and L4's lower end-plate depth in more studies.",
    "Test the heights against VerSe's readers' grades when the helper thread brings its rows.",
    "Measure the published masks of 1347, 1283 and 1134 against their repaired copies.",
    "Run every suite, then an adversarial review, then merge PR 30 on your standing permission.",
]


def footer():
    return ("    <p>bordercall draft pull request 30, branch claude/project-thread-6o9umj at %s. The records are in "
            "records/morphometry-2026-10-29/ and hold aggregates only. The rows of the 228 studies are in the "
            "project's files under gold3-ct/morphometry/run229/, never in git.</p>\n"
            "    <p>On your word of 12:12 UTC, three ENHANCE.PET CTs (0004, 0006, 0010; 954,848,980 bytes) were read "
            "from the public bucket, measured and deleted. Nothing went to the grid. Confidential, like everything "
            "in bordercall.</p>" % COMMIT)


def main():
    html = open(os.path.join(HERE, "template.html")).read()
    html = html.replace("On study 0004, all 77 lines at L3, T8 and C5 matched their rows.",
                        "On study 0004, all 150 lines at C5, T1, T8, L3, L4 and L5 matched their rows.")
    fills = {"REPLACE_LEDE": LEDE, "REPLACE_LEDGER": ledger(), "REPLACE_RENDERS": renders(),
             "REPLACE_BENCH": bench(), "REPLACE_NEXT": "\n".join("      <li>%s</li>" % n for n in NEXT),
             "REPLACE_FOOTER": footer()}
    for key, val in fills.items():
        assert key in html, key
        html = html.replace(key, val)
    open(os.path.join(HERE, "index.html"), "w").write(html)
    print("written", len(html))


main()
