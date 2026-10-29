export const meta = {
  name: 'paper-tables-code-fix-2',
  description: 'Apply the second readers findings to series.py and to the docstrings and page prose of cross_naming.py and results.py, then verify',
  phases: [
    { title: 'Fix', detail: 'series.py fixer and docs fixer, separate files' },
    { title: 'Verify', detail: 'one independent verifier per fixer' },
  ],
}
const R = `${args.repo}/research_notes/paper-tables`
const RV = `${args.sp}/review`
const COMMON = `Repository ${args.repo} (bordercall, private research code). Folder ${R}: tools/series.py turns mapped table
readings (data/readings/<id>.csv, data/cohorts/<id>.cohorts.json) into data/series.csv; tools/cross_naming.py writes
data/cross_naming.json; tools/results.py writes results/README.md from it. These files were just fixed for 24 review
findings (${RV}/series.json, cross_naming.json, results.json hold them) and a second reader of each file reported what
remains. Python: ~/venv-sc/bin/python from the repository root. Scratch: ${args.sp}/work/<your label>/ only. Never run
git. Do NOT regenerate data/series.csv, data/cross_naming.json or results/ in the repository; the lead does that. Style:
the code's idiom, short functions, names that read as English, comments that say why with the paper's page, ASCII and
LF, no new dependency; docstrings true to the code.`
const GROUPS = [
  { key: 'series', file: `${RV}/round1b-series.json`, own: 'tools/series.py only',
    extra: 'Apply all three, including the optional Tang [31] duplicate (other threads read series.csv, so one series per set of subjects matters). Where a cell is printed in several tables, take its mean from the table that prints its SD, and its meta (table, units, definition) from that same row. Check the page images for any reason text you write (PDFs in ' + args.sp + '/papers/, render with pdftoppm -r 200 into scratch).' },
  { key: 'docs', file: `${RV}/round1b-docs.json`, own: 'tools/cross_naming.py and tools/results.py (docstrings, comments and the page prose results.py writes; no change to any number)',
    extra: 'These are wording findings; apply each one that holds, so every docstring and every sentence of the page says what the code does.' },
]
const OUT = { type: 'object', properties: {
  outcomes: { type: 'array', items: { type: 'object', properties: { index: { type: 'integer' }, outcome: { type: 'string', enum: ['applied', 'partly', 'skipped'] }, why: { type: 'string' } }, required: ['index', 'outcome', 'why'] } },
  expected_changes: { type: 'string' }, summary: { type: 'string' } }, required: ['outcomes', 'expected_changes', 'summary'] }
const FIND = { type: 'object', properties: { checked: { type: 'integer' },
  findings: { type: 'array', items: { type: 'object', properties: { kind: { type: 'string', enum: ['not_fixed', 'fixed_wrong', 'regression', 'docstring', 'style'] },
    where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } }, required: ['kind', 'where', 'what', 'fix'] } },
  summary: { type: 'string' } }, required: ['checked', 'findings', 'summary'] }
const out = await pipeline(GROUPS,
  g => agent(`${COMMON}\n\nYou fix ${g.own}. The findings are the JSON list in ${g.file} (numbered from 0). Reproduce each
before changing anything; make the smallest correct change. ${g.extra}
Return one outcome per finding, what regenerating the outputs should change by your scratch runs, and a summary.`,
    { label: `fix:${g.key}`, phase: 'Fix', schema: OUT }),
  (fixed, g) => fixed ? agent(`${COMMON}\n\nYou independently verify the change just made to ${g.own} for the findings in ${g.file}.
The fixer's report: ${JSON.stringify(fixed)}
Rerun each finding's scenario on the code as it stands; rebuild the outputs in scratch (series.py over all readings;
cross_naming.py --fields 2; results.py on the committed record) and explain every difference from the committed outputs
by a finding; check docstrings against code. Report only, never edit.`,
    { label: `verify:${g.key}`, phase: 'Verify', schema: FIND }).then(v => ({ group: g.key, fixed, verify: v })) : { group: g.key, fixed: null })
return { results: out }