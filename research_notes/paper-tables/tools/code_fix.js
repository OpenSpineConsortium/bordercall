export const meta = {
  name: 'paper-tables-code-fix',
  description: 'Apply the confirmed review findings to series.py and its readings, cross_naming.py and results.py, then verify each file independently',
  phases: [
    { title: 'Fix', detail: 'one fixer per file group applies the confirmed findings it reproduces' },
    { title: 'Verify', detail: 'one independent verifier per file group checks every fix and looks for regressions' },
  ],
}
const R = `${args.repo}/research_notes/paper-tables`
const RV = `${args.sp}/review`
const COMMON = `Repository ${args.repo} (bordercall, private research code). Folder ${R}: tools/series.py turns mapped table
readings (data/readings/<id>.csv, data/cohorts/<id>.cohorts.json) into data/series.csv; tools/cross_naming.py sets every
paper's series beside Panjabi's cadaver table and writes data/cross_naming.json; tools/results.py writes results/README.md
with figures and CSVs from that record. README.md there and each tool's docstring say what the tools mean to do. Python:
~/venv-sc/bin/python from the repository root. Scratch: ${args.sp}/work/<your label>/ only. Never run git.
Do NOT regenerate data/series.csv, data/cross_naming.json or results/ in the repository; the lead does that after all
fixes land. Test in scratch: e.g. python3 -I tools/series.py data/readings data/cohorts <scratch>/series.csv and diff
against data/series.csv; cross_naming.py with --fields 2 into scratch; results.py into a scratch folder.
Style: the code's own idiom, short functions, names that read as English, comments that say why, ASCII and LF, no new
dependency. Each rule that leaves something out (a misprint, a reprint, a right-only side) carries its reason in the code,
with the paper's page, as MISPRINTS does. Keep every docstring true to what the code now does.`
const GROUPS = [
  { key: 'series', files: 'tools/series.py and, only where a finding says the reading itself is wrong, data/readings/<id>.csv (fix a reading only against the page image of the PDF in ' + args.sp + '/papers/<id>.pdf, rendered with pdftoppm -r 200 into scratch, and say what the page prints)' },
  { key: 'cross_naming', files: 'tools/cross_naming.py' },
  { key: 'results', files: 'tools/results.py' },
]
const OUT = { type: 'object', properties: {
  outcomes: { type: 'array', items: { type: 'object', properties: { id: { type: 'integer' },
    outcome: { type: 'string', enum: ['applied', 'partly', 'skipped'] }, why: { type: 'string' } },
    required: ['id', 'outcome', 'why'] } },
  expected_changes: { type: 'string', description: 'what regenerating series.csv, cross_naming.json and results/ should change, from your scratch runs' },
  summary: { type: 'string' } }, required: ['outcomes', 'expected_changes', 'summary'] }
const FIND = { type: 'object', properties: { checked: { type: 'integer' },
  findings: { type: 'array', items: { type: 'object', properties: { id: { type: 'integer', description: 'the finding id it concerns, or -1 for a new problem' },
    kind: { type: 'string', enum: ['not_fixed', 'fixed_wrong', 'regression', 'docstring', 'style'] },
    where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } }, required: ['id', 'kind', 'where', 'what', 'fix'] } },
  summary: { type: 'string' } }, required: ['checked', 'findings', 'summary'] }

const out = await pipeline(GROUPS,
  g => agent(`${COMMON}\n\nYou fix ${g.files}. The confirmed findings of an adversarial review for it are the JSON list in
${RV}/${g.key}.json (each with id, scenario, impact, and a verifier's evidence and suggested fix). The fixes are suggestions:
reproduce each finding first, then make the smallest correct change, which may differ from the suggestion where you find a
better one (say why). Findings in one file interact; apply them so they hold together (e.g. series.py's side and sex
choices, counts and misprints). ${RV}/refuted.json lists findings a refuter rejected; do not act on them.
Return one outcome per finding id, what regenerating the outputs should change according to your scratch runs, and a summary.`,
    { label: `fix:${g.key}`, phase: 'Fix', schema: OUT }),
  (fixed, g) => fixed ? agent(`${COMMON}\n\nYou are the independent verifier of the fixes just made to ${g.files}. Assume
they are wrong until a run shows otherwise. The findings are ${RV}/${g.key}.json; the fixer's report is:
${JSON.stringify(fixed)}
For every finding: rerun its scenario in scratch on the code as it now stands and say whether it is fixed and fixed
right. Then look for regressions: rebuild the output in scratch and diff it against the committed one, explaining every
changed row group (each must follow from a finding); check the docstrings and comments match the code; check the code
still runs end to end (series.py on all readings; cross_naming.py --fields 2; results.py on the committed record).
Never edit a file in the repository; report only, each problem with a fix a writer can apply.`,
    { label: `verify:${g.key}`, phase: 'Verify', schema: FIND }).then(v => ({ group: g.key, fixed, verify: v })) : { group: g.key, fixed: null })
return { results: out }