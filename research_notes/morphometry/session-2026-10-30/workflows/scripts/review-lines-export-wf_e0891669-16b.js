export const meta = {
  name: 'review-lines-export',
  description: 'Adversarial review of the morphometry run --lines export in bordercall, then skeptics on each finding',
  phases: [
    { title: 'Review', detail: 'four lenses on commit 4086684' },
    { title: 'Verify', detail: 'two skeptics per finding' },
  ],
}

const S = '/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad'
const CONTEXT = `
Context:
- Repository: /home/user/bordercall, branch claude/project-thread-gv744i. The change under review is commit 4086684 ("Write each measure's line and each vertebra's frame beside the rows") on top of origin/main ee495d5. See it with: git -C /home/user/bordercall show 4086684 (and git diff ee495d5 4086684). Files: morphometry/__main__.py (run --lines, line_rows, frame_row, study_lines, side_paths, one_study, current, code_stamp, join_rows), morphometry/measure.py (measure_volume's keep), morphoview/lines.py (side_reading, pedicles, vertebra_lines with vals), morphometry/tests/test_lines_export.py (13 tests), research_notes/morphometry/README.md and handoff.md (words).
- Do not edit files under /home/user/bordercall. Work in a scratch folder of your own under ${S}/review-lines-<your lens>/ (copy the repository there with git worktree add or cp -r if you want to try a fix or a mutant).
- Python with numpy, scipy, nibabel: ${S}/venv/bin/python, run from the repository root (or with PYTHONPATH at your copy). Phantoms only: morphometry/tests/phantom.py draws columns (P.straight, P.draw, P.Vert, P.cervical, P.lumbar, chain, Joint; look at morphometry/tests/test_morphometry.py for how each test class draws its phantom, including DensAtC2, ThickSlices, LateralMass, WrongMasks). Never read a real mask or CT; none is in the container.
- The export's purpose: bordercall PR 45 (branch origin/claude/project-thread-2akdys, research_notes/latent-shape-prior-evaluation/README.md, section 10 row "1 export" near line 387, and section 8 near line 233; pipeline.html near line 524) reads, per vertebra, each measure's value, its two line ends and the vertebra's frame, to build a point-distribution model of landmarks from the real masks' line ends and to project the named 3-D line ends onto 2-D views. The export runs on the grid inside SchwingNet's morphometry job (grid/morphometry.sbatch in /home/user/SchwingNet runs "python -m morphometry run --masks ... --scheme enhance|verse|totalseg --out ... --workers 32"), over 1,597 ENHANCE.PET masks, 374 VerSe and 159 TotalSegmentator, with resumption by code stamp.
- The owner's rules: no new dependencies; ASCII and LF; plain prose comments that say why; no real data in the container; nothing public.
- A finding is a defect: a wrong result, a crash or lost data on some input, a resumption or atomicity hole, a line or frame that does not mean what the words say, something PR 45 needs and does not get, a test that does not bite, or words that do not match the code. Give file:line evidence and, where you can, a reproduction on a phantom with its output. Do not report style preferences.
`

const FINDINGS = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'high', 'medium', 'low'] },
          detail: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['title', 'severity', 'detail', 'evidence', 'fix'],
      },
    },
  },
  required: ['summary', 'findings'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    evidence: { type: 'string' },
  },
  required: ['refuted', 'reason', 'evidence'],
}

const LENSES = [
  { key: 'correctness', prompt: `Lens: correctness of what is written. Check that every line row's ends, value, measured and status mean what LINE_FIELDS' comment and the README say, that the lines are drawn on the same vertebra objects and checked against the same values the rows were written from (so nothing measure_volume does after vertebra_values, such as COL.disc, PELVIS.measures or COL.regional, changes a vertebra before its lines are drawn; check by reading and by a phantom with a pelvis, scheme enhance, if phantom.py offers one), that the disc lines are checked against the disc's own values, that the frames are the vertebra's final frame (v.frame after any turn in anatomy.build) and in the same world as the line ends, that side_reading's reuse of the measure's own pedicle reading gives what reading again gives on more phantoms than the one SameLines uses (cervical, LateralMass, PitchedDown, Overhang, thick slices, a cut vertebra), and that number() writes what write_rows wrote before for every kind of value (float, nan, int, numpy scalar, bool, str).` },
  { key: 'robustness', prompt: `Lens: robustness on the grid. Look for inputs that crash, hang or lose data: a study with no usable vertebra, a study whose measuring raises, a vertebra the volume's edge cuts, C2 with its dens, a cervical level whose pedicle is refused, a level present in kept["verts"] but missing from peds or values, disc pairs, the scheme totalseg (a folder per study; check that side_paths and the per-study file naming still work when --masks holds folders, as SchwingNet's verse job measures TotalSegmentator's stacked int16 files; read cmd_run's file filter), memory and time with 32 workers (the lines are built inside the worker; kept holds every vertebra until the study ends), the .part files and os.replace on a crash between the three writes, a run killed and resumed, a run with --limit or --studies, ProcessPoolExecutor pickling of the job tuple, and the lazy import of morphoview inside the worker. Measure the drawing's cost on two or three phantom columns of your own (e.g. 5 lumbar levels at 0.8x0.8x1 and a cervical-to-lumbar chain if phantom.chain allows), with and without --lines, one worker.` },
  { key: 'fitness', prompt: `Lens: fitness for PR 45's stage 1. Read PR 45's plan (see Context) and say whether lines.csv and frames.csv give what stage 1 and the stages after it need: each measure's value, its two named line ends, the vertebra's frame; whether the frame written is "the new frame" the plan names (read the plan's words on the frame, and morphometry/anatomy.py's build and the own-axis turn), whether line ends are in a coordinate system the plan can use (world millimetres of the mask's affine) and whether the plan also needs them in the vertebra's frame or voxel indices, whether a line can be joined to its row (study, level, key) without ambiguity (duplicate keys per level, extras rows), whether the study id carries what the plan's loader needs (the plan mentions a person field like enhance_pet:0001; say whether the export must carry it or SchwingNet's job maps it), whether status values let the plan drop withheld or not-measured lines, and what the line count per level will look like. Also check that SchwingNet's vendored copy can carry morphoview/lines.py: read /home/user/SchwingNet/tools/bordercall_vendor.py (ENGINE, what it copies) and say exactly what must change there for the export to reach the grid (morphoview's other modules import maskedge and matplotlib; does lines.py import anything beyond morphometry and scanimport?).` },
  { key: 'tests-and-words', prompt: `Lens: the tests and the words. For each of the 13 tests in morphometry/tests/test_lines_export.py, say what defect it catches and make at least four mutants of the code in a scratch copy (for example: write rows before lines in one_study; drop the lines check from current(); make code_stamp ignore the lines flag; write frames from a different vertebra; swap a and b; write measured as value; make side_reading return the values but another side's info; skip extras) and run the test module against each, reporting which mutants survive. Then compare every sentence the commit adds to research_notes/morphometry/README.md, handoff.md, the docstrings and the comments with the code, and report each that does not hold (for example the "about 5 per cent" figure: measure it; "13 tests": count them; "the same to the bit": check).` },
]

phase('Review')
const reviews = await pipeline(
  LENSES,
  l => agent(`${CONTEXT}\n${l.prompt}`, { label: `review:${l.key}`, phase: 'Review', schema: FINDINGS }),
  (r, l) => parallel((r ? r.findings : []).map((f, i) => () =>
    parallel([0, 1].map(k => () => agent(`${CONTEXT}
You are a skeptic. A reviewer (lens ${l.key}) reports this finding on commit 4086684. Try to refute it: read the code, and where the claim can be tested, test it on a phantom in a scratch folder of your own under ${S}/skeptic-${l.key}-${i}-${k}/. Refuted means the defect does not exist as stated or does not matter for the export's use (say why). Default to refuted=false only if you confirmed the defect yourself.

Finding: ${f.title} (${f.severity})
Detail: ${f.detail}
Evidence: ${f.evidence}
Proposed fix: ${f.fix}`, { label: `skeptic:${l.key}:${i}:${k}`, phase: 'Verify', schema: VERDICT })))
      .then(vs => ({ lens: l.key, ...f, verdicts: vs.filter(Boolean) })))),
)
const all = reviews.filter(Boolean).flat().filter(Boolean)
const held = all.filter(f => f.verdicts.filter(v => !v.refuted).length >= 1)
const refuted = all.filter(f => f.verdicts.length && f.verdicts.every(v => v.refuted))
return {
  summaries: LENSES.map((l, i) => ({ lens: l.key, summary: reviews[i] ? 'see findings' : 'no result' })),
  held: held.map(f => ({ lens: f.lens, title: f.title, severity: f.severity, detail: f.detail, evidence: f.evidence, fix: f.fix,
    verdicts: f.verdicts.map(v => ({ refuted: v.refuted, reason: v.reason })) })),
  refuted: refuted.map(f => ({ lens: f.lens, title: f.title, reasons: f.verdicts.map(v => v.reason) })),
}
