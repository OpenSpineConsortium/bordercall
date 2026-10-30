export const meta = {
  name: 'projection-review-extra-lenses',
  description: 'Three more review lenses on the FleXray projection change (the words, the FleXray record, the owner\'s ask), each finding then tried by two skeptics',
  phases: [
    { title: 'Find', detail: 'one reviewer per lens' },
    { title: 'Verify', detail: 'two skeptics per finding, each trying to refute it' },
  ],
}

const S = '/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad'
const RULES = `
Rules for this task:
- The change is the uncommitted working tree of /home/user/bordercall (branch claude/project-thread-gv744i); see \`git -C /home/user/bordercall status --short\` and \`git -C /home/user/bordercall diff\`. New files: morphoview/projection.py, morphoview/shapes.py, morphoview/tests/test_projection.py, morphoview/tests/test_shapes.py, morphoview/tests/flexray_record.py, morphoview/tests/fixtures/flexray.json; changed: morphoview/__main__.py (the \`project\` subcommand), morphoview/__init__.py (docstring), research_notes/morphometry/README.md (section "Carrying the lines onto FleXray's X-rays").
- Do not modify, create or delete anything under /home/user/bordercall or /home/user/SchwingNet. To run code, copy what you need into ${S}/review-<your lens>/ and work there.
- Python: ${S}/venv/bin/python has bordercall's dependencies without torch (run a test with \`python -m unittest morphoview.tests.test_shapes\` from a copy's root); ${S}/fxr-venv/bin/python has torch, fxr 1.0.2 and nanodrr 0.1.5 (installed under ${S}/fxr-venv/lib/python3.13/site-packages; install nothing, it has no pip). FleXray on CPU is slow: keep volumes and detectors small. Four CPUs are shared with other reviewers.
- Never use pkill -f or killall. There is no network, grid or real patient data here and none is needed. The project allows no new dependencies.
- The project's owner asked, at 16:49 UTC: "make sure these lines can be projected from 3D to 2D natively, surviving a conversion by flexray to a fluroscopic xray, further, there should be basic functioanlity for non-linear arcs/curves/planes/volumes/ect". The lines are the morphometry export (python -m morphometry run --lines: each measure's two ends and each vertebra's frame in world millimetres of the mask's nibabel affine).`

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          file: { type: 'string' },
          line: { type: 'integer' },
          defect: { type: 'string', description: 'one sentence: what is wrong' },
          scenario: { type: 'string', description: 'concrete inputs and the wrong output, or the untrue words and what is true' },
          evidence: { type: 'string', description: 'what you ran and what it printed, or the lines you read' },
          status: { type: 'string', enum: ['CONFIRMED', 'PLAUSIBLE'] },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['title', 'file', 'defect', 'scenario', 'evidence', 'status', 'severity'],
      },
    },
    checked: { type: 'string', description: 'briefly, what you checked and found correct' },
  },
  required: ['findings', 'checked'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    severity: { type: 'string', enum: ['high', 'medium', 'low', 'none'] },
    reasoning: { type: 'string', description: 'what you ran or read, and why it does or does not hold' },
    fix: { type: 'string', description: 'if it holds, the smallest change that fixes it' },
  },
  required: ['refuted', 'severity', 'reasoning'],
}

const LENSES = [
  {
    key: 'words',
    prompt: `You are an adversarial reviewer with one lens: are the words true. ${RULES}

Read every claim made about this change and test each against the code and against what the tests and probes actually print:
- research_notes/morphometry/README.md, section "Carrying the lines onto FleXray's X-rays" (every number: 5e-13 mm, 41 pixels, 95 beads, 0.21 px, medians 0.05 to 0.08, half a pixel misses by 0.5, 0.16 px and median 0.05, nine views and levels pixel for pixel, within one pixel, 3 to 7 px, 3 to 4 px, about 9 mm at 1000 HU, up to 20 px, eight image sizes, 0.002 px, 0.05 mm, 1e-4, 0.005, 2 to 4 s a view, 0.3 to 0.6 s a level, 46 tests about a minute);
- the docstrings of morphoview/projection.py, morphoview/shapes.py, morphoview/__init__.py, the project parts of morphoview/__main__.py, and of the tests;
- the draft handoff entry at ${S}/handoff_entry.md, which will be put at the top of research_notes/morphometry/handoff.md.
Re-derive the numbers yourself where you can (run the tests, read the fixture ${S}/../ is not needed: the fixture is morphoview/tests/fixtures/flexray.json, write small probes). A finding is a claim the code or the evidence does not bear out, or a number that is wrong; name the file and line, quote the words, and say what is true.`,
  },
  {
    key: 'record',
    prompt: `You are an adversarial reviewer with one lens: is the FleXray record a faithful instrument. ${RULES}

morphoview/tests/flexray_record.py rendered FleXray on a phantom and wrote morphoview/tests/fixtures/flexray.json; the tests in morphoview/tests/test_projection.py hold morphoview/projection.py to that record. If the recorder shares a convention error with projection.py (a half-pixel convention, an axis order, an orientation, a centroid biased by a threshold, a canvas mapping computed by our code rather than read from FleXray), the tests would pass while FleXray disagrees. Read the recorder line by line against FleXray's and nanoDRR's own code under ${S}/fxr-venv/lib/python3.13/site-packages, and decide for each recorded quantity whether it is FleXray's own output or something our code computed. Where you can, check independently with ${S}/fxr-venv/bin/python: render a small volume (for example 48^3, a few beads, a 64 to 128 pixel detector) with FleXray's own API and compare where FleXray puts a bead with where morphoview.projection.Camera projects it, under AP, PA and no orientation, cone and parallel. Also check that the tests read the record in a way that would fail if projection.py were wrong. A finding is a way the record or the tests' use of it could be wrong while the tests pass.`,
  },
  {
    key: 'ask',
    prompt: `You are an adversarial reviewer with one lens: does the change do what the owner asked. ${RULES}

The X-rays are rendered by SchwingNet: read /home/user/SchwingNet/tools/flexray_render.py (the DRR renders and their manifest), /home/user/SchwingNet/tools/realism.py and /home/user/SchwingNet/src/schwingnet/realism.py (the fluoroscopic realism edit that turns a render into a fluoroscopic-looking X-ray), and anything they call that moves, crops, flips, resizes, pads or warps an image between FleXray's render and the X-ray that is stored or used. For each such step, decide whether a line carried by \`python -m morphoview project\` (morphoview/__main__.py, morphoview/projection.py) still lands where the stored X-ray shows the bone, and whether the command can even read that step's records. Then hold morphoview/shapes.py to the second half of the ask: are arcs, curves, planes and volumes each creatable, projectable onto a render, and tested, and is there an obvious basic shape the ask names or implies that cannot be made or projected. A finding is a concrete case where the ask is not met (name the file and line and the inputs), not a wish for more features.`,
  },
]

const skeptic = (f, lens, i) => agent(`You are a skeptic. Try to refute this review finding about an uncommitted change. ${RULES}

The finding (from the "${lens}" lens):
${JSON.stringify(f, null, 1)}

${i === 0
  ? 'Your method: reproduce it. Build the scenario it describes in a scratch copy and run it. It stands only if you see the wrong output yourself.'
  : 'Your method: read the ground truth. Decide from FleXray\'s and nanoDRR\'s code, SchwingNet\'s render and realism code, the docstrings and the owner\'s ask what the right behaviour or words are, and whether the finding\'s expectation is the right one.'}
Default to refuted=true if, after honest effort, you cannot make it stand. Give severity "none" when refuted. If it stands, say the smallest fix.`, { label: `verify:${lens}:${(f.title || '').slice(0, 24)}:${i}`, phase: 'Verify', schema: VERDICT })

const results = await pipeline(
  LENSES,
  l => agent(l.prompt, { label: `find:${l.key}`, phase: 'Find', schema: FINDINGS }),
  (found, l) => parallel((found && found.findings ? found.findings : []).map(f => () =>
    parallel([0, 1].map(i => () => skeptic(f, l.key, i))).then(vs => ({ lens: l.key, ...f, votes: vs.filter(Boolean) }))
  )).then(vs => ({ lens: l.key, checked: found ? found.checked : 'reviewer failed', findings: vs.filter(Boolean) })),
)
return results.filter(Boolean)
