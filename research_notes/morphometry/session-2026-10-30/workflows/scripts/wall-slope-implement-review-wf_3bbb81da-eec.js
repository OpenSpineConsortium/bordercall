export const meta = {
  name: 'wall-slope-implement-review',
  description: 'Put the chosen posterior-wall reader into body.py, test it, review it adversarially and fix what holds',
  phases: [
    { title: 'Implement', detail: 'one agent edits the checkout and runs the suite' },
    { title: 'Review', detail: 'four lenses read the diff' },
    { title: 'Verify', detail: 'skeptics try to refute each finding' },
    { title: 'Fix', detail: 'one agent fixes what survived and runs the suite again' },
  ],
}

const S = '/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad'
const BASE = 'a9f21fd'
const RULES = `
Context: bordercall's morphometry engine (private research code; nothing goes public). Checkout /home/user/bordercall, branch claude/project-thread-e89pjg (PR 44), last commit ${BASE}. Python: ${S}/venv/bin/python with PYTHONPATH=/home/user/bordercall; set OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 on probes, since four CPUs are shared.
Hard rules: never commit, push, switch branches or touch GitHub; never run anything under bordercall's archive/ (read it at most); phantoms only, no real mask or CT, no grid job; no new dependencies (numpy, scipy, nibabel only); write scratch files only under the folder your task names, scripts as files run by path. The repository's writing rules: plain prose that says why, short functions, names that read as English, no emoji, ASCII and LF only, nothing that refers to a file that does not exist. Report only numbers you measured.

The work so far. body.posterior_wall_slope(v, B, xc) reads dy/dz of the vertebral body's posterior wall in the vertebra's frame (x right, y anterior, z cranial) as the least y of z bins near the midline; four readings are taken against the plane square to it: pedicle.one_side's pedicle_angle_sagittal (through pedicle.wall_slope), body.inclinations' endplate_incl and endplate_lower_incl, and posterior.spinous_angle. A diagnosis on 98 cached phantom vertebrae (${S}/wall/cache, scored by ${S}/wall/score.py; build_cache.py builds them) found it errs by up to 4.14 degrees on 1 mm slices and 5.66 on 2.5 mm slices where the grid lies within a few degrees of the frame: the wall's binary staircase on the lattice, and the body cut (anatomy.body_in_front along the canal line from anatomy.wall_slope, which has the same staircase) shaving the wall's first row at one end. A judge chose a reader that walks the scan's own lattice from the vertebra's label: ${S}/wall/judge/proposed.py, function posterior_wall(v, B, xc) -> (slope, info). On the clean cache it errs at most 0.35 thin and 0.79 thick (median 0.08 and 0.19); over 12 label alterations (notches, holes, ragged edges, cut volume) at most 1.64 thin and 3.03 thick; a lip 1.5 mm proud inside the window on thick slices is its known failure (11.69). The judge's full notes: ${S}/wall/judge/ (prop_table.txt, downstream_table.txt, held_out_proposed.txt, freedom_calib.txt, tests_proposed_nan.txt).
`

const IMPL = {
  type: 'object',
  properties: {
    files_changed: { type: 'array', items: { type: 'string' } },
    what_changed: { type: 'array', items: { type: 'string' } },
    suite: { type: 'string', description: 'the last lines of the morphometry suite run, verbatim, with its time' },
    morphoview: { type: 'string' },
    bench: { type: 'string', description: 'what bench --slice 2.5 printed for endplate_incl before and after, or why not run' },
    score: { type: 'string', description: 'score.py summary for the reader as committed in body.py' },
    new_tests: { type: 'array', items: { type: 'string' } },
    deviations: { type: 'array', items: { type: 'string' }, description: 'where you departed from the judge notes, and why' },
    open_items: { type: 'array', items: { type: 'string' } },
  },
  required: ['files_changed', 'what_changed', 'suite', 'score', 'new_tests', 'open_items'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          file: { type: 'string' }, line: { type: 'integer' },
          detail: { type: 'string', description: 'the defect and a concrete case that shows it, with numbers where measured' },
          fix: { type: 'string' },
        },
        required: ['title', 'severity', 'file', 'detail', 'fix'],
      },
    },
  },
  required: ['findings'],
}
const VERDICT = {
  type: 'object',
  properties: { refuted: { type: 'boolean' }, reason: { type: 'string' }, measured: { type: 'string' } },
  required: ['refuted', 'reason'],
}
const FIXED = {
  type: 'object',
  properties: {
    fixed: { type: 'array', items: { type: 'string' } },
    not_fixed: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, why: { type: 'string' } }, required: ['title', 'why'] } },
    suite: { type: 'string' }, morphoview: { type: 'string' }, score: { type: 'string' },
  },
  required: ['fixed', 'not_fixed', 'suite', 'score'],
}

phase('Implement')
const impl = await agent(RULES + `
Your task: put the judge's reader into the checkout, the one agent allowed to edit it. Read ${S}/wall/judge/proposed.py and the judge's implementation notes in ${S}/wall/judge/ (and, for context, the workflow result ${'/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/tasks/w35xz0djd.output'}, key result.verdict). Then:
1. morphometry/body.py: add posterior_wall(v, B, xc) -> (slope, info) from proposed.py, its constants each with a comment saying why, its functions short and named in English, and a docstring in the file's style that says what it reads and why (the staircase, the cut, the clamp, the freedom and its bound). posterior_wall_slope returns its slope, NAN on refusal in place of today's silent 0.0. Cache the reading on the vertebra so the four callers read it once per vertebra (check that every caller passes v.body_pts and the midpoint of its x range; key the cache so a different B or xc reads again). Check every number the notes quote against the code (the notes say G.MIN_CHORD_POINTS is 12; scanimport/geometry.py may say otherwise: use what the code holds and name it rightly). Avoid an import cycle (pedicle imports body).
2. The consumers on a NAN wall: endplate_incl and endplate_lower_incl NAN with a flag naming the reason; pedicle_angle_sagittal NAN with a note; spinous_angle NAN with a flag; a flag where the freedom passes FREE_FLAG_DEG. Follow how each module already writes its flags and notes.
3. Tests in morphometry/tests/test_morphometry.py, phantoms only: ThickSlices asserts endplate_incl (the notes: 4.55 off today, about 0.2 with the new reader); a grid within 2 degrees of the frame on 1 mm slices with the wall leaned 5 degrees asserts the wall's slope within 0.5 degree (add a lean parameter to the phantom's Vert in morphometry/tests/phantom.py, default 0 so nothing else moves, drawn by shearing the body's inside test as build_cache.py does, and say in its comment what the truths do not account for); and a basivertebral notch on the posterior wall (another phantom parameter, default off) asserts the wall slope and the inclinations. Keep the new tests few: each phantom build costs about half a minute.
4. Restate the words: pedicle.py's module docstring paragraph on the wall's error and wall_slope's docstring; research_notes/morphometry/README.md where it speaks of the wall's error and of the canal walls leaning half as far; column.wall_corner's docstring; anything else that quotes the old behaviour. The canal line (anatomy.wall_slope) is not changed here: say in the docstrings and the note that it shares the staircase and is the next to fix.
5. Run: the full suite \`cd /home/user/bordercall && PYTHONPATH=. ${S}/venv/bin/python -m unittest -v morphometry.tests.test_morphometry\` (about six minutes; run it in the background and poll its log, since a single tool call may time out), \`python -m unittest morphoview.tests.test_lines\`, score.py on body.posterior_wall_slope as it now stands, and \`python -m morphometry bench --slice 2.5\` before (git stash is not allowed; run bench before you edit, or from a copy of the base commit made with git worktree add under ${S}/wall/base and removed after) and after, if each takes under ten minutes. Everything must pass before you return; if something cannot be made to pass, say exactly what and why.
Scratch folder ${S}/wall/impl/. Do not commit.`, { label: 'implement', phase: 'Implement', schema: IMPL })
if (!impl) return { error: 'the implementer returned nothing' }
log('implemented: ' + impl.files_changed.join(', '))

phase('Review')
const DIFF_HOW = `Read the change with \`git -C /home/user/bordercall diff ${BASE}\` (uncommitted, in the working tree) and the files it touches whole where you need them. The implementer's report: ${JSON.stringify(impl)}`
const lenses = [
  { key: 'geometry', prompt: 'Lens: geometry and correctness of the new reader. The lattice walk (which axis, which direction is posterior, the run rule, the gate against the canal line), the midpoints, the fit and its trimming, the linear programs and the clamp (the signs of the constraints, what parts), the freedom and its unit, the conversion to degrees, the sign conventions of the four consumers against the plane square to the wall, the cache key. Build small cases on the cached phantoms or new ones to show any defect.' },
  { key: 'robustness', prompt: 'Lens: robustness on real masks and runs. Cervical bodies (small, the band not capped by the body width), thoracic bodies against the rib heads, L5 and the sacrum, a body cut by the volume, holes and notches, thick slices whose thick axis is not z, a vertebra with no full canal ring, a label with stray pieces, NaN propagation into every consumer and into the CSV rows and morphoview, the run time over 1,600 studies of 24 levels each, determinism, exceptions linprog can raise.' },
  { key: 'words', prompt: 'Lens: the words against the code. Every docstring, comment, constant comment, the README and column.wall_corner: does each say what the code does, are the quoted numbers the measured ones (check them against the judge files and your own runs), does anything refer to a file or function that does not exist, is it ASCII and LF, plain prose that says why.' },
  { key: 'tests', prompt: 'Lens: the tests. Do the new tests exercise the new paths (the clamp, the refusal, the flag, NaN propagation), would each fail on the old reader (check by running it against the base commit, for example from a git worktree of ' + BASE + ' under ' + S + '/wall/review_tests/base, removed after), are the tolerances justified by the measurements, does the phantom change move any old truth, is the suite still green and how long it takes.' },
]
const reviews = await parallel(lenses.map(l => () =>
  agent(RULES + '\n' + DIFF_HOW + '\n\nYour task: review adversarially, read-only on the checkout. ' + l.prompt + ` Report real defects only, each with a concrete case; no style nits beyond the repository's rules. Scratch folder ${S}/wall/review_${l.key}/.`,
    { label: 'review:' + l.key, phase: 'Review', schema: FINDINGS }).then(r => r ? r.findings.map(f => ({ ...f, lens: l.key })) : [])))
const all = reviews.flat()
const rank = { high: 0, medium: 1, low: 2 }
all.sort((a, b) => rank[a.severity] - rank[b.severity])
const CAP = 12
const checked = all.slice(0, CAP)
if (all.length > CAP) log(`verify: ${all.length - CAP} low-ranked findings not put to a skeptic; they go to the fixer marked unverified`)
log(`review: ${all.length} findings`)

phase('Verify')
const judged = await parallel(checked.map((f, i) => () => {
  const n = f.severity === 'high' ? 2 : 1
  return parallel(Array.from({ length: n }, (_, k) => () =>
    agent(RULES + '\n' + DIFF_HOW + `\n\nA reviewer (lens ${f.lens}) claims this defect in the uncommitted change:\n${JSON.stringify(f)}\n\nYour task: try to refute it. Read the code, and where it can be measured, measure it on phantoms (scratch folder ${S}/wall/verify_${i}_${k}/). Default to refuted=true only where the claim is wrong or does not arise from code that can run; where it holds, say so and say what you measured.`,
      { label: `verify:${f.lens}:${i}`, phase: 'Verify', schema: VERDICT })))
    .then(vs => ({ ...f, votes: vs.filter(Boolean) }))
}))
const survived = judged.filter(f => f.votes.length === 0 || f.votes.filter(v => !v.refuted).length * 2 >= f.votes.length)
const refuted = judged.filter(f => !survived.includes(f))
const unverified = all.slice(CAP)
log(`verify: ${survived.length} held, ${refuted.length} refuted, ${unverified.length} unverified`)

phase('Fix')
let fix = null
if (survived.length || unverified.length) {
  fix = await agent(RULES + '\n' + DIFF_HOW + `\n\nThe adversarial review of this change left these findings standing (with the skeptics' votes):\n${JSON.stringify(survived)}\n\nAnd these, not put to a skeptic, to judge yourself:\n${JSON.stringify(unverified)}\n\nYour task: you are now the one agent allowed to edit the checkout. Fix each standing finding that is real, in the smallest change that fixes it, and say why for any you leave. Then run the full morphometry suite (in the background, polling its log), morphoview's tests and score.py on the reader as it now stands, and report. Do not commit. Scratch folder ${S}/wall/fix/.`,
    { label: 'fix', phase: 'Fix', schema: FIXED })
}
return { impl, findings: judged, survived, refuted, unverified, fix }
