export const meta = {
  name: 'morphometry-rerun-gate',
  description: 'Review the re-pinned morphometry engine against SchwingNet, add a gate rule to measure each set again on the owner\'s count, and verify it adversarially',
  phases: [
    { title: 'Review', detail: 'consumers of the rows, grid runtime and timing, rerun design' },
    { title: 'Implement', detail: 'gate rule, tests, docs in the SchwingNet working tree' },
    { title: 'Verify', detail: 'three skeptics on count safety, data keeping, tests and words' },
    { title: 'Fix', detail: 'fix what the skeptics confirmed' },
  ],
}

const S = '/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad'
const CONTEXT = `
Context (shared by every step):
- SchwingNet working tree: /home/user/SchwingNet, branch claude/project-thread-gv744i, HEAD e95e5fa ("Pin bordercall at ee495d5, the merged morphometry engine") on top of origin/main 2fe153f. That commit re-pins grid/bordercall/ (tools/bordercall_vendor.py copy) from bordercall 16f7b40 to bordercall main ee495d5; only grid/bordercall/morphometry/{anatomy,body,canal,column,pedicle,posterior}.py and grid/bordercall/VENDORED change. The OLD engine is "git -C /home/user/SchwingNet show origin/main:grid/bordercall/..." (extract with: git -C /home/user/SchwingNet archive origin/main grid/bordercall | tar -x -C <dir>). The NEW engine is /home/user/SchwingNet/grid/bordercall (same files as bordercall main, checked out at ${S}/bc-main, which also has the tests/ folders, morphometry/tests/phantom.py among them).
- Python with numpy 2.5.4, scipy 1.18.1, nibabel 5.4.2: ${S}/venv/bin/python. System python3 is 3.11/3.12 stdlib only, for SchwingNet's own tests.
- The grid jobs: grid/gate.sh word_morphometry (sets enhance and verse, one batch job a set, report grid/logs/MORPHOMETRY-<set>.md printed on every later send, "a report that stands queues nothing"), grid/morphometry.sbatch (writes under \${MORPHOMETRY_ROOT:-$RS/morphometry}/<set>, rows/<id>.csv, rows.csv, run.log, facts.jsonl, verdicts.csv, and for verse a totalseg/ subfolder with masks/, stacked/, int16/, manifests/ and its own rows), word_morphometry_covariates with COVARIATES_RERUNS and covariates_rerun_allowed, grid/morphometry-covariates.sbatch, tools/gold3_covariates.py. Tests: tests/test_gate.py (morphometry tests near line 2637 onward), tests/test_gold3_covariates.py, tests/test_bordercall_vendor.py. docs/memory/morphometry-on-the-grid.md describes it all.
- What ran: enhance Slurm 40872077 (exit 0, 05:58 UTC 30 Oct, 1597 ENHANCE.PET masks, 40:48 elapsed), verse Slurm 40877151 (exit 0, 12:21 UTC, 3:55:05 elapsed; VerSe 374 masks measured in 821 s, TotalSegmentator 159 stacked serially then measured in 84 s), covariates Slurm 40878978 (exit 0, 5:50 elapsed). All on the old engine. The grid's logs are on symphony-template's branch grid: git -C /home/user/symphony-template show origin/grid:logs/job-schwingnet-morphometry-verse.json (and -enhance, -covariates, -status). The measuring interpreter on the grid is /wsu/home/go/go24/go2432/mambaforge/envs/spineps/bin/python (3.11.16); its package versions are not recorded unless something in SchwingNet records them (look).
- The owner's count, 2026-10-30 14:33 UTC, on a decision card: "Three: enhance, verse, covariates": three CPU jobs on the merged engine, enhance and verse measured again and then the covariates join redone on the new rows, the old rows kept under their job numbers. No job is sent by you: nobody in this workflow runs grid-accounts.yml, ssh, sbatch, or any GitHub write. Nothing is committed or pushed; the main session does that.
- Owner's standing rules: every grid job needs the owner's word and number of jobs (the count above); never run archived code (grid/bordercall/bordercall, the clone's archive/); no real mask or CT is read in this container (phantoms only); no new dependencies (Python stdlib for SchwingNet tools/tests, plain bash; grid bash must run on bash 4.2); ASCII and LF; plain prose comments that say why, matching gate.sh's own style.
- Do not run scripts/check.sh in /home/user/SchwingNet (it pollutes the clone); a separate run is going in another checkout. Run single test modules or -k filters instead.
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
          severity: { type: 'string', enum: ['blocker', 'high', 'medium', 'low', 'info'] },
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

phase('Review')
const [consumers, runtime, design] = await parallel([
  () => agent(`${CONTEXT}
Your task: check that the NEW engine's output still fits everything in SchwingNet that reads it, before the owner's three jobs run on it.
1. Diff the row keys, flags and CLI between the old engine and the new: run both engines' code paths far enough to list every key each writes (read morphometry/__main__.py, measure.py and the reworked modules; grep the dict keys; or measure a phantom column with each, drawn with bordercall's morphometry/tests/phantom.py from ${S}/bc-main and written to NIfTI in a scratch folder under ${S}/review-consumers/, running "python -m morphometry run --masks <dir> --scheme <scheme> --out <dir> --workers 2" with PYTHONPATH set to each engine's folder). Note keys added, removed, renamed, and values that changed meaning (e.g. NaN where 0.0 stood).
2. Find every consumer in SchwingNet: grid/morphometry.sbatch (its level_table reads h_ant, h_post_inset, body_index_ant_post; it greps 'flag:error'), tools/gold3_covariates.py and its tests, the screening package if it reads morphometry rows, any doc or research note under docs/ that names keys or the pinned commit 16f7b40 or says which engine is pinned (git grep), docs/memory/morphometry-on-the-grid.md. Say for each whether the new engine breaks it, changes its numbers' meaning, or leaves it as is.
Report findings with file:line evidence; a finding is something that must change before or with the rerun.`, { label: 'review:consumers', phase: 'Review', schema: FINDINGS }),
  () => agent(`${CONTEXT}
Your task: will the new engine run on the grid, and how long will the three jobs take?
1. API and versions: list every numpy/scipy/nibabel call the new engine makes that the old did not (scipy.optimize.linprog with method highs, its status codes, any numpy 2-only API). Find what versions the grid's spineps environment holds if anything in SchwingNet records it (git grep for spineps, mambaforge, scipy==, environment files, logs on symphony-template's branch grid such as setup or status logs); if not recorded, say so and say what the oldest scipy is that the new code needs (linprog highs since 1.6; check every option and attribute used, e.g. res.status values, options keys, integrality, bounds forms). Say whether the engine would fail outright or only differ.
2. Timing: on phantoms only, time the old engine against the new per vertebra and per study. Draw a lumbar column (L1 to L5 or more) and if possible a cervical-to-sacrum column with bordercall's morphometry/tests/phantom.py (${S}/bc-main) at 0.8x0.8x1 mm and 0.86x0.86x2.5 mm, write label NIfTIs under ${S}/review-runtime/, and time "python -m morphometry run" (or the per-study call) with PYTHONPATH at each engine, one worker, several repeats. Then estimate the enhance job (1597 studies, old run 40:48 elapsed on 32 CPUs) and the verse job (374 VerSe + 159 TotalSegmentator; old measuring 821 s and 84 s) on the new engine, against the job's 24 h limit and --no-requeue, and say whether the TotalSegmentator stacking will be redone or skipped on a rerun (read grid/morphometry.sbatch: stacked/ verdict files). Also check the parallel stacking change of SchwingNet #498 is on origin/main.
Report findings with evidence (numbers, file:line).`, { label: 'review:runtime', phase: 'Review', schema: FINDINGS }),
  () => agent(`${CONTEXT}
Your task: design the gate rule that lets the owner's count of three measure each set once more and redo the join once more, and nothing beyond that.
Read grid/gate.sh fully where it concerns morphometry (word_morphometry, word_morphometry_covariates, covariates_rerun_allowed, COVARIATES_RERUNS, covariates_lost_word, live_of, bench_failed_on_older_code, bench_job_of, began_on_older_code, submit, depend_on, checkout_holders, the STATE file, the .sent markers), grid/morphometry.sbatch (where it writes, how it resumes: rows of another code stamp are measured again; the stacking's stacked/ verdicts; the HOLD file; REPORT.part and its trap), grid/morphometry-covariates.sbatch, tools/gold3_covariates.py's inputs, and tests/test_gate.py's morphometry tests and their harness.
Design, precisely enough to implement:
- MORPHOMETRY_RERUNS beside COVARIATES_RERUNS, one word "<set>:<job>" a job, naming the job whose standing report a rerun replaces; set now to "enhance:40872077 verse:40877151", and COVARIATES_RERUNS to "covariates:40878978", each with a comment citing the owner's choice of 2026-10-30 14:33 UTC. A word whose entry names the standing report's job keeps the old report as MORPHOMETRY-<set>-<job>.md and the old rows, facts, verdicts and run logs where nothing later overwrites them (say where: e.g. <set>/kept/<job>/, and for verse its totalseg/ files too, keeping masks/, stacked/, int16/ and manifests/ so the TotalSegmentator subjects are not stacked again unless the sbatch would need to), then queues one job. Whether the moving happens in the gate (login node: only mv, never a computation) or at the job's start on the compute node, choose and say why.
- The count must hold in every case: once the new report stands its job is not the entry's, so later sends print only; a send while any morphometry job is live refuses (exit 75); a submission whose answer was lost must not let the next send queue another (see how word_morphometry_covariates does it with its .sent marker and covariates_lost_word; say whether word_morphometry needs the same and how); a rerun job killed past its trap, leaving REPORT.part and no report, must not let the next send queue another without a new word; and the covariates rerun must refuse while either set's standing report is still one a MORPHOMETRY_RERUNS entry names (a rerun pending), so the join never reads one new set and one old.
- The tests to add to tests/test_gate.py, by name and what each asserts, in the harness's own style.
- The doc changes: docs/memory/morphometry-on-the-grid.md and its index line in docs/memory/MEMORY.md (the index line must stay one line), the pinned commit named where docs say which engine is pinned.
Return the design as precise prose and pseudo-code in the summary, with findings for any existing defect you find on the way.`, { label: 'review:design', phase: 'Review', schema: FINDINGS }),
])

const reviews = { consumers, runtime, design }
log(`reviews: consumers ${consumers ? consumers.findings.length : 'none'}, runtime ${runtime ? runtime.findings.length : 'none'}, design ${design ? design.findings.length : 'none'} findings`)

phase('Implement')
const impl = await agent(`${CONTEXT}
Your task: implement, in the SchwingNet working tree /home/user/SchwingNet (do not commit, do not push), the gate rule designed below, the tests it names, the doc changes, and any change the two other reviews below say must come with the rerun (only what is needed for the three jobs to run correctly on the new engine and report truthfully; list anything you leave out and why).
The design review:
${JSON.stringify(design, null, 1)}
The consumers review:
${JSON.stringify(consumers, null, 1)}
The runtime review:
${JSON.stringify(runtime, null, 1)}
Rules: match gate.sh's style (comments in plain prose saying why, functions with a one-line comment after the brace, bash 4.2), no new dependencies, ASCII and LF, docs/memory one fact per file with its one-line index entry. Run the morphometry tests of tests/test_gate.py (find how the file is run: unittest or pytest, and use -k or a pattern for morphometry and covariates) and tests/test_bordercall_vendor.py and tests/test_gold3_covariates.py, plus python3 tools/bordercall_vendor.py check and any doc check the repository has for docs/memory (tools/ scripts that check MEMORY.md; find them in scripts/check.sh and run only those steps). Make sure every new test fails with its fix taken out (try it, then restore).
Return: the files changed, what each change does, the commands run and their results, and anything left out.`, { label: 'implement', phase: 'Implement' })

phase('Verify')
const LENSES = [
  ['count', `Can any sequence of sends queue more jobs than the owner's count of three (enhance once more, verse once more, covariates once more), or fewer than intended? Walk every path of word_morphometry and word_morphometry_covariates as changed: the entry naming the standing job, a live job, a lost answer, a job killed past its trap, a failed rerun on the same commit, a failed report on older code (bench_failed_on_older_code's requeue), covariates sent between the two set reruns, the same word sent twice in a row, the gate pulled to a newer main between sends. Check with the tests' harness where you can (write throwaway tests under ${S}/verify-count/ that drive gate.sh as tests/test_gate.py does).`],
  ['data', `Is anything lost or mixed? The old rows, facts, verdicts and logs are kept where nothing overwrites them; the TotalSegmentator stacking is reused or redone correctly; the new run reads only new rows; the covariates join reads the new rows of both sets and not the kept ones; disk use; what happens to MORPHOMETRY-<set>.md naming, bench_job_of on the kept report, and the report's own lines. Also re-check the consumers review's points against the change: does the job's report and the join still read the keys they read, with the meaning they assume, on the new engine.`],
  ['tests-words', `Do the tests bite (each fails with its fix taken out; try it), do they cover the cases the count lens names, and are they in the harness's style? Are the words true: comments in gate.sh, the memory file and its index line, any doc the change touched; bash 4.2 compatibility of every new line (no \${var@Q}, no declare -n where 4.2 lacks it, no mapfile -d, etc.); ASCII and LF; nothing refers to a file that does not exist.`],
]
const verdicts = await parallel(LENSES.map(([key, lens]) => () => agent(`${CONTEXT}
You are a skeptic reviewing a change another agent just made in /home/user/SchwingNet (read it with git -C /home/user/SchwingNet diff, against HEAD e95e5fa). The implementer's own account:
${impl}
Your lens: ${lens}
Report only findings you have confirmed by reading the code or running something; for each give the evidence and the fix. Do not edit /home/user/SchwingNet.`, { label: `verify:${key}`, phase: 'Verify', schema: FINDINGS })))

const confirmed = verdicts.filter(Boolean).flatMap(v => v.findings).filter(f => f.severity !== 'info')
log(`skeptics confirmed ${confirmed.length} findings`)

let fix = null
if (confirmed.length) {
  phase('Fix')
  fix = await agent(`${CONTEXT}
Your task: fix, in /home/user/SchwingNet (do not commit, do not push), each finding below that is real; for one you judge not real, say why with evidence. Then rerun the tests the implementer ran (the morphometry and covariates tests of tests/test_gate.py, tests/test_bordercall_vendor.py, tests/test_gold3_covariates.py, the memory index check) and confirm each new or changed test fails with its fix taken out.
The implementer's account:
${impl}
The findings:
${JSON.stringify(confirmed, null, 1)}
Return: each finding with fixed / not real and why, the files changed, and the test results.`, { label: 'fix', phase: 'Fix' })
}

return { reviews, impl, verdicts, fix }
