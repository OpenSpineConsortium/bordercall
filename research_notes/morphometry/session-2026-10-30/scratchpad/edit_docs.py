"""The words of PR 47 after its review: the research note's run paragraph and the handoff's top section."""
import sys
root = sys.argv[1]


def edit(rel, pairs):
    path = root + "/" + rel
    src = open(path).read()
    for old, new in pairs:
        assert src.count(old) == 1, (rel, old[:70], src.count(old))
        src = src.replace(old, new)
    open(path, "w").write(src)


edit("research_notes/morphometry/README.md", [
("Every measure can be drawn on its own cuts of its own vertebra, and on study 0004 all 150 lines at C5, T1, T8, L3, "
 "L4 and L5 match the run's rows (morphoview, below).",
 "The measures with a construction to show, 25 keys of a vertebra and a disc's three heights, can each be drawn on "
 "its own cuts of its own vertebra, and on study 0004 all 150 lines then drawn at C5, T1, T8, L3, L4 and L5 matched "
 "the run's rows (morphoview, below)."),
("With `--lines`, `run` also writes each measure's line and each measured vertebra's frame beside its rows "
 "(lines/ID.csv and frames/ID.csv, joined as lines.csv and frames.csv): the line's two ends in the world's "
 "millimetres of the mask's affine, its rule, its panel, the value its construction gives beside the row's and "
 "whether it is drawn, withheld or not measured, built by [morphoview/lines.py](../../morphoview/lines.py) on the "
 "vertebrae the rows were read from; the frame is the vertebra's origin and its three axes in the same world. It is "
 "the export the latent shape prior's evaluation reads (PR 45, stage 1); such a run has a stamp of its own, over "
 "morphoview/lines.py too, and a level whose drawing fails is flagged (flag:lines) without losing a row. On the "
 "phantoms the drawing adds about 5 per cent to a study's time.",
 "With `--lines`, `run` also writes, beside each study's rows, the lines "
 "[morphoview/lines.py](../../morphoview/lines.py) draws and each measured vertebra's frame (lines/ID.csv and "
 "frames/ID.csv, joined as lines.csv and frames.csv), built on the vertebrae the rows were read from and checked "
 "against the values written. A vertebra's lines are those of the 25 keys morphoview.lines.VERTEBRA_KEYS names, "
 "Panjabi's seven chords (scanimport.SEVEN) among them, and a disc's those of its three heights (DISC_KEYS); the "
 "other keys, @UNLINED@ of the @LUMBAR_KEYS@ a lumbar vertebra's rows hold, have no line and leave no line row. A line "
 "row gives the line's rule and panel, the value its construction gives beside the row's, its drawn length, whether "
 "it is drawn, withheld or not measured, and its two ends in the world's millimetres of the mask's affine, each "
 "named (a_end and b_end, from morphoview.lines.ENDS: left or right, posterior or anterior, inferior or superior, "
 "medial or lateral, the canal or the tip) as it lies in the frame of the vertebra the line is drawn in, a disc's "
 "line in that of the vertebra below the disc. A frame row gives the vertebra's origin, the centroid of its label's "
 "main piece, and its three axes, x to the patient's right, y from the canal to the body and z up; which axis its z "
 "lies along (axis: the end-plates' bisector, one end-plate's normal, or the column's line kept); and the column's "
 "line z was turned from (cx, cy, cz). Ends, values and frames are written whole, so a reader can hold a length to "
 "its ends and a frame to its orthonormality to the bit; measured is the row's value, to the rows' four places. This "
 "is the export the latent shape prior's evaluation reads (PR 45, stage 1), less two frames its stage 1 compares, "
 "the oracle's and the one found without the mask, which need the CT and a step of their own. A run with the lines "
 "has a stamp of its own, over morphoview/lines.py too: a study whose rows carry another stamp, or whose lines or "
 "frames file is missing, is measured again, and the joins take only the studies whose rows carry the run's stamp, "
 "each join written whole or not at all. A drawing that fails is flagged (flag:lines, naming its builder) and loses "
 "only its own lines. On three phantom columns on one worker the drawing adds 9 per cent to the measuring of L1 to "
 "L5, 13 to that of C2 to C7 and 13 to that of a column from C2 to L5."),
])

OLD_TOP_END = "# Morphometry: the handoff of 2026-10-30, 14:00 UTC\n"
NEW_TOP = """# Morphometry: the handoff of 2026-10-30, @WHEN@ UTC: the lines export, reviewed

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's word of 14:28 UTC ("yes do all these": merge PR 44, re-pin the engine in SchwingNet,
give a count) read with the other thread's note of 14:34 UTC, which asked that PR 45's stage 1
export ride in the morphometry jobs. This pass read no real mask or CT and queued no grid job; at
14:45 UTC the owner held the jobs until a resynthesis.

## What the export is

- `python -m morphometry run --lines` writes, per study, lines/ID.csv and frames/ID.csv beside
  rows/ID.csv and joins them as lines.csv and frames.csv; the research note says what each row
  holds. The lines are morphoview.lines' builders run on the vertebrae measure_volume built (its
  new `keep`) and checked against the values it wrote: 25 keys a vertebra (VERTEBRA_KEYS), 3 a
  disc (DISC_KEYS), each end named (ENDS). The lines and frames are written before the rows, which
  stay the commit marker, and a run with the lines has a stamp of its own, over
  morphoview/lines.py too.
- morphoview.lines.pedicles takes the measure's own reading of each side (side_reading), since
  reading pedicle.one_side again took 8 of a study's 11 s of drawing on the phantom; on a vertebra
  the volume's edge cuts, whose values the measure blanks, it reads the side again.

## The review, and what was done

Four reviewers read commit 4086684 by correctness, robustness on the grid, fitness for PR 45's
stage 1, and the tests and the words; two skeptics tried the first finding and could not refute
it. Fixed:

- Three of Panjabi's seven chords, the posterior height at the wall and the canal's width and
  depth at the pedicles (h_post, canal_w, canal_ap), had no line, though PR 45's minimal shape
  model is fitted on all seven. morphoview.lines draws them (panjabi_height, panjabi_canal); each
  is a median, drawn in the cell or section nearest it, with the median as its value.
- The words promised a line for every measure; they name the keys that have one.
- Ends, values and frames were written to four places, so a frame read back was orthonormal only
  to 1e-4 and failed the oracle interface's check at 1e-6; they are written whole.
- The ends were unnamed and their order was set builder by builder; each is named (a_end, b_end).
- A frame did not say which axis its z lies along; frames.csv adds axis and the column's line.
- The frame tests passed with the origin at zero, x and y reversed, the frame turned 5 degrees or
  left on the column's line. Frames now takes every line's ends into its frame on a chain whose
  joints open, tilt, turn and slip, and holds the origin to the main piece's centroid and each end
  to the side its name says.
- One failing builder dropped every line of its level; each has its own guard, and the flag names
  it.
- After a run a dead worker cut short, the joins mixed files an older code wrote with the run's;
  they take only the studies whose rows carry the run's stamp, and are written to a part file and
  moved into place.
- No test held the write order or the reset after a failed measuring; Failing kills a study at
  each of its three writes, and fails one after its vertebrae are kept.

@MUTANTS@

Left, with the reason:

- A run whose pool breaks exits 0 and prints "a worker died ... run again", as every run has, with
  the lines or without; SchwingNet's report is to read that line from the run's log.
- A key with no line leaves no line row; VERTEBRA_KEYS and DISC_KEYS give the denominator.
- The oracle's frame and the one found without the mask, which PR 45's stage 1 compares with the
  engine's, need the CT and autoanatomist, which the job has not; they are a step of their own.

## What SchwingNet needs before the counted jobs

None of this is done in bordercall:

- vendor the merged commit with morphoview/__init__.py and morphoview/lines.py
  (tools/bordercall_vendor.py's ENGINE), since `run --lines` imports morphoview before it
  measures;
- pass --lines in grid/morphometry.sbatch's measure() and print code_stamp(True) in the report;
- digest lines.csv and frames.csv, and count flag:lines and the lines per level by status, as
  aggregates only;
- read "a worker died" from the run's log into the report;
- refuse the word where grid/bordercall/morphoview/lines.py is missing;
- then the owner's count of three, enhance, verse and the covariates join, one at a time.

## Tests and timing

- morphometry/tests/test_lines_export.py, @N_EXPORT@ tests on phantoms written as label files: L2
  to L4 straight, the same cut through L4's body by the volume's edge, a thick-sliced pair and the
  chain whose joints open, tilt, turn and slip. The engine's suite, @N_SUITE@ tests, passes
  (@SECS@ s on four shared CPUs).
- On three phantom columns on one worker the drawing adds 9 per cent to the measuring of L1 to L5,
  13 to that of C2 to C7 and 13 to that of a column from C2 to L5, and nothing to the peak memory.

"""


def top(rel):
    path = root + "/" + rel
    src = open(path).read()
    assert src.startswith("# Morphometry: the handoff of 2026-10-30, 15:00 UTC: the lines export\n")
    assert src.count(OLD_TOP_END) == 1
    src = NEW_TOP + src[src.index(OLD_TOP_END):]
    open(path, "w").write(src)


top("research_notes/morphometry/handoff.md")
print("ok")
