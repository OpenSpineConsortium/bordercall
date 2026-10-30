export const meta = {
  name: 'wall-slope-diagnose-design',
  description: 'Diagnose the posterior wall slope error on aligned grids and score three candidate fixes on phantoms',
  phases: [
    { title: 'Diagnose', detail: 'three lenses on why body.posterior_wall_slope errs on grids aligned with the frame' },
    { title: 'Design', detail: 'three candidate wall-slope readers, each scored on the same 98 cached phantoms' },
    { title: 'Judge', detail: 'pick the reader to put into body.py' },
  ],
}

const S = '/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad'
const CTX = `
You are working on bordercall's morphometry engine (a private research repository; confidential, nothing goes public).
Checkout: /home/user/bordercall, branch claude/project-thread-e89pjg (bordercall PR 44). Python: ${S}/venv/bin/python (numpy, scipy, nibabel, matplotlib), always with PYTHONPATH=/home/user/bordercall and OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 (four CPUs are shared by several agents).

Hard rules:
- Do NOT edit any file under /home/user/bordercall, and do not commit, push, switch branches or touch GitHub. Write only under the scratch folder named in your task.
- Never run anything under bordercall's archive/ folder (read it at most).
- Phantoms only: no real mask or CT is read in this container. Never send or start a grid job.
- No new dependencies (numpy, scipy, nibabel are allowed). Write scripts as files and run them by path.
- Report numbers you measured, from runs you made; say plainly what you did not measure.

The problem. morphometry/body.py posterior_wall_slope(v, B, xc) returns dy/dz of the vertebral body's posterior wall in the vertebra's own frame (x right, y anterior toward the body, z cranial): it keeps the body points B within ACROSS_HALF_MM (3 mm) of the midline xc, bins them in z over the middle 60 percent of the height with step max(v.fz, 0.5) mm, takes the least y (the most posterior point) of each bin and fits a line. Three readings are taken against the plane square to that wall, so they inherit its error: pedicle.one_side's pedicle_angle_sagittal (raw climb minus atan(wall)), body.inclinations' endplate_incl and endplate_lower_incl (-(rim slope + atan(wall))), and posterior.spinous_angle (+atan(wall)). anatomy.py has a separate wall_slope(z, y) for the canal's wall line, used for the body's cut and canal_ap_lateral_film; it is not the subject here, but say if it shares the mechanism.

Measured so far (score.py on the cache, frame-relative truth): on 1 mm slices the current reader errs by up to 1.72 degrees (grid tilted 2 degrees about x), 0.96 at 5 degrees, 0.57 on a grid exactly aligned, about 0.1 at the test suite's 18-degree tilt; on 2.5 mm slices up to 4.93 (tilt 2), 2.14 (tilt 10), 1.49 (aligned). An earlier probe found 1.8 to 4.2 degrees on three phantoms at tilt 2, 1 mm slices. The frame itself is right to 0.07 degrees on thin slices, but on 2.5 mm slices at small tilts it errs by 1.6 to 2.6 degrees; score.py compares the wall against the truth taken into the measured frame, so frame error is not counted against the wall.

The phantoms. morphometry/tests/phantom.py draws each vertebra in its own frame with the body's posterior wall at y = 0 (vertical) and labels a voxel when its centre falls inside a part. ${S}/wall/build_cache.py builds 98 configs: phantoms straight (wall leans 0, +5, -5 degrees, drawn by shearing the body's inside test), pitched, shapes (lean 0 and +4), pitched_down; grids aligned (tilt 0), x2, x5, x10 (tilts about x), suite18 ((1,0.3,0) 18 degrees, turn 7), t25, y12; spacings thin (0.8, 0.8, 1.0) and thick (0.86, 0.86, 2.5). Each pickle in ${S}/wall/cache/ holds {cfg, vert (the anatomy Vertebra of L3), truth, raw, frame_err_deg, wall_truth_deg, xc}. ${S}/wall/score.py scores any candidate: \`cd ${S}/wall && PYTHONPATH=/home/user/bordercall ${S}/venv/bin/python score.py cache <candidate.py> <function> --json <out.json>\` (use "current x" in place of a file to score the reader as it stands). A candidate has the signature fn(v, B, xc) -> dy/dz, or (dy/dz, info dict), or NAN to refuse. Read score.py and build_cache.py first. The cache should hold 98 pickles; if fewer, the build is still running (four processes): work on what is there and score again at the end.

Useful code to read: morphometry/body.py (posterior_wall_slope, inclinations, plate_rims), morphometry/pedicle.py (lattice_under, parting and slope_range: a linear-program parting of bone from air centres on the scan's own lattice, with the range of slopes that still part it; one_side; wall_slope), morphometry/anatomy.py (the Vertebra: frame, grid, is_bone, points_world, fx fy fz, pixel, body_pts, loc, wall_slope), scanimport/geometry.py.
`

const DIAG = {
  type: 'object',
  properties: {
    mechanism: { type: 'string', description: 'what makes the reading err, in plain sentences' },
    confirmed: { type: 'boolean' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'each a measured fact with its numbers' },
    implications_for_fix: { type: 'string' },
    files_written: { type: 'array', items: { type: 'string' } },
  },
  required: ['mechanism', 'confirmed', 'evidence', 'implications_for_fix'],
}

const CAND = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    file: { type: 'string', description: 'absolute path of the candidate module' },
    function: { type: 'string' },
    summary: { type: 'string', description: 'how it reads the wall, in plain sentences' },
    score_json: { type: 'string' },
    score_summary: { type: 'string', description: 'the == thin and == thick blocks score.py printed, verbatim' },
    thin_max_err: { type: 'number' }, thin_median_err: { type: 'number' },
    thick_max_err: { type: 'number' }, thick_median_err: { type: 'number' },
    refused: { type: 'integer', description: 'configs where it returned NAN' },
    seconds_per_config: { type: 'number' },
    risks: { type: 'array', items: { type: 'string' }, description: 'how it could fail on real masks' },
  },
  required: ['name', 'file', 'function', 'summary', 'score_summary', 'thin_max_err', 'thick_max_err', 'refused', 'risks'],
}

const JUDGE = {
  type: 'object',
  properties: {
    winner: { type: 'string' },
    combine: { type: 'string', description: 'what to graft from the others, or none' },
    reasons: { type: 'array', items: { type: 'string' } },
    gate: { type: 'string', description: 'when the slope should be refused or flagged, with the bound and its calibration' },
    expected: { type: 'string', description: 'the errors to expect, thin and thick, by grid' },
    implementation_notes: { type: 'string', description: 'exactly what body.posterior_wall_slope should become, and what else must change' },
  },
  required: ['winner', 'reasons', 'expected', 'implementation_notes'],
}

phase('Diagnose')
const lenses = [
  { key: 'binning', prompt: `Lens: the binning. Test the hypothesis that posterior_wall_slope's z bins (step max(fz, 0.5), centred on a grid of the frame's z, with the least y per bin) alias against the scan's lattice when the grid lies within a few degrees of the frame: bins that catch no lattice layer at the wall, or two, so the least y jumps, and the jumps drift one way over the height and bias the fit. Print, for the cached straight phantom at x2 and x5 (thin and thick) and at suite18, each bin's z, count, least y and which lattice layers (the scan's own k index, from v.grid) its points come from. Then say whether the error is this aliasing, the binary staircase of the wall itself, or something else, with numbers. Scratch folder: ${S}/wall/diag_binning/.` },
  { key: 'limit', prompt: `Lens: the information limit. A binary mask on a lattice pins a near-vertical wall's slope only so far. For every cached config, compute the interval of slopes b of a line y = a + b z (and of a plane y = a + b z + c x) that parts the body's bone centres within 3 mm of the midline over the middle 60 percent of the height from the non-body centres just behind the wall (use the vertebra's own lattice: v.grid, v.is_bone or the body's label, as pedicle.lattice_under does; decide carefully what counts as not-body behind the wall, since the canal lies there), by linear programs (scipy.optimize.linprog, method highs). Report per grid and spacing the interval's width in degrees, whether the frame-relative truth lies inside it, and where the widest-margin line falls in it. This bounds what any reader can do. Scratch folder: ${S}/wall/diag_limit/.` },
  { key: 'consumers', prompt: `Lens: the consumers and the second wall. (1) List every reader of body.posterior_wall_slope and of pedicle.wall_slope, and every place in morphometry/ and morphoview/ that reads anatomy's v.wall_slope, with what each does with it, and which tests in morphometry/tests/test_morphometry.py and morphoview/tests/ cover each and at which grid tilt and turn (P.draw's default grid_turn, P.straight's default tilt). (2) Measure on the cache whether anatomy's v.wall_slope (the canal wall's line) errs by the same mechanism on aligned grids (compare it with the frame-relative truth of the posterior wall, which on these phantoms is also the canal's anterior wall at the midline). (3) research_notes/morphometry/README.md says "the slabs' canal walls lean half as far as the posterior wall does, a cause in scanimport not found"; say whether these numbers bear on that. (4) Name any test that would change if the wall reader changed. Read-only on the repository; scratch folder ${S}/wall/diag_consumers/.` },
]
const diag = await parallel(lenses.map(l => () =>
  agent(CTX + '\n\nYour task.\n' + l.prompt, { label: 'diagnose:' + l.key, phase: 'Diagnose', schema: DIAG })
    .then(r => r ? { key: l.key, ...r } : null)))
const diagOk = diag.filter(Boolean)
log(`diagnose: ${diagOk.length} of ${lenses.length} lenses returned`)
const DIAG_TEXT = JSON.stringify(diagOk, null, 1)

phase('Design')
const designs = [
  { key: 'lattice', prompt: `Candidate A, lattice-native. Read the wall on the scan's own lattice, not on bins of the frame's z: for each lattice layer (and row) that crosses the wall band near the midline, take the posterior-most body centre (or the midpoint between it and the first non-body centre behind it), in frame coordinates, and fit the line through all of them, so that no layer is missed or caught twice. Consider using the whole middle 60 percent and a band in x wider than 3 mm if the wall allows.` },
  { key: 'parting', prompt: `Candidate B, parted by a linear program. As pedicle.parting does for the pedicle's surfaces: part the body's bone centres near the wall from the not-body centres just behind it by the line or plane of widest margin (scipy.optimize.linprog, highs), the slope its b, with the range of slopes that still part them (as pedicle.slope_range) returned in info, a least-crossing program where no line parts them, and a refusal where the range is too wide or the crossing too far. Decide what counts as not-body behind the wall (the canal is there; the posterior elements are further back).` },
  { key: 'boundary', prompt: `Candidate C, boundary midpoints by least squares. Take every pair of lattice-neighbouring centres across the posterior wall (body inside, not-body outside, along the lattice direction nearest the frame's y) within the band and the middle 60 percent, put the wall point at the pair's midpoint, and fit y = a + b z (+ c x if it helps) by least squares, perhaps robustly (a few iterations of trimming), so that every phase of the staircase is averaged.` },
]
const cands = await parallel(designs.map(d => () =>
  agent(CTX + `\n\nWhat the diagnosis found (three lenses, JSON):\n${DIAG_TEXT}\n\nYour task. Write one candidate wall reader as a module ${S}/wall/cand_${d.key}/cand.py with a function slope(v, B, xc) returning (dy/dz, info) or (NAN, info) to refuse, score it with score.py on the full cache (all 98 pickles; if the build is not finished when you start, develop on what is there and score again at the end), and report. ${d.prompt} Keep it short and readable, plain names, no new dependencies, and time it. Do not tune to the cache's truths beyond setting a bound you can justify from the geometry, and say which bound you set and why. If the information-limit lens shows a config cannot be pinned, say whether your reader refuses it or reads it.`,
    { label: 'design:' + d.key, phase: 'Design', schema: CAND }).then(r => r ? { key: d.key, ...r } : null)))
const candOk = cands.filter(Boolean)
log(`design: ${candOk.length} of ${designs.length} candidates returned`)

phase('Judge')
const verdict = await agent(CTX + `\n\nWhat the diagnosis found:\n${DIAG_TEXT}\n\nThe candidates (JSON, each with its score file):\n${JSON.stringify(candOk, null, 1)}\n\nYour task. Judge which reader should replace body.posterior_wall_slope. Re-run score.py yourself on each candidate's file to check its numbers (do not trust the summaries), read each candidate's code for what would break on real masks (a body whose posterior wall is concave or carries an osteophyte, a basivertebral foramen, a body cut by the volume's edge, a mask with holes), and weigh accuracy on thin and thick slices, refusals, simplicity and cost. Say what to graft from the runners-up, whether and when to refuse or flag, and exactly what body.posterior_wall_slope should become. Scratch folder ${S}/wall/judge/.`,
  { label: 'judge', phase: 'Judge', schema: JUDGE })

return { diagnose: diagOk, candidates: candOk, verdict }
