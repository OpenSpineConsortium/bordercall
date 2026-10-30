export const meta = {
  name: 'paper-tables-review',
  description: 'Adversarial review of the paper-tables code and its results page: three lenses find, a refuter verifies each finding',
  phases: [
    { title: 'Find', detail: 'statistics, data rules, and page-against-record lenses' },
    { title: 'Verify', detail: 'one refuter per finding, reproducing it by running code' },
  ],
}
const R = `${args.repo}/research_notes/paper-tables`
const COMMON = `Repository ${args.repo} (bordercall, private research code; branch claude/project-thread-adplcz). Folder ${R}:
tools/series.py turns mapped table readings (data/readings/*.csv, data/cohorts/*.cohorts.json) into data/series.csv;
tools/cross_naming.py sets every paper's series beside Panjabi's cadaver table (schwingcheck in ${args.repo}/schwingcheck)
and writes data/cross_naming.json; tools/results.py writes results/README.md with figures and CSVs from that record.
README.md in ${R} and each tool's docstring say what they are meant to do. Python with numpy and schwingcheck's
requirements: ~/venv-sc/bin/python, run from the repository root. Scratch space: ${args.sp}/work/<your label>/ (write
nothing else). Never edit a file in the repository and never run git. A full cross_naming run takes about 40 minutes on
4 CPUs; use --fields 2 or small subsets to test behaviour, never a full run.`
const FIND = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, file: { type: 'string' }, line: { type: 'integer' },
  scenario: { type: 'string', description: 'concrete input or state and the wrong output it gives' },
  impact: { type: 'string', description: 'which number on the results page or in the record it changes, and by how much if known' },
  severity: { type: 'string', enum: ['high', 'medium', 'low'] } }, required: ['title', 'file', 'scenario', 'impact', 'severity'] } },
  summary: { type: 'string' } }, required: ['findings', 'summary'] }
const VERDICT = { type: 'object', properties: { real: { type: 'boolean' }, evidence: { type: 'string' },
  fix: { type: 'string' } }, required: ['real', 'evidence', 'fix'] }
const LENSES = [
  { key: 'statistics', prompt: `Lens: statistics. Read tools/cross_naming.py and tools/series.py whole. Check every formula against
its docstring and the standard method: the DerSimonian-Laird random-effects pool and its tau, the leave-one-paper-out
widened rule, disagreement in Panjabi SDs and in levels, the SD from SE and variance, side averaging, sex pooling with the
between-means term, the transport draw and its seeds (is the record reproducible for any --processes?), the claim
threshold and how "named exactly", "within one level" and "named at 0.99" are counted. Run small cases to prove each finding.` },
  { key: 'data-rules', prompt: `Lens: data rules. Check that data/series.csv follows series.py's own rules on the real readings: pick
at least 30 series across at least 12 papers (include tan2004, bonczar2024, griffith2016, busscher2010, hinck1966,
eisenstein1977) and trace each back to its reading rows, checking statistic, sides, sexes, n and n_from, sd_from, units and
vs_panjabi; look for series built from rows that should not combine (different statistics, a quoted study's values
mixed with the paper's own, levels that are ranges, pig cohorts reaching the comparison, SEMs of 0, misprints like a
value a sixth of its neighbours). Report each rule broken with the rows.` },
  { key: 'page', prompt: `Lens: the results page against its record. Check results/README.md, its CSVs and captions against
data/cross_naming.json and data/series.csv: recompute at least 25 printed numbers (table cells, counts of papers,
fields, shares, the per-paper transport rows, the disagreement table) from the record with python; check every
sentence of the page's prose says what the numbers show and no more; check the figures' captions match the CSVs; check
that results.py would write the same page again from the same record (run it into ${args.sp}/work/page/ and diff).` },
]
const out = await pipeline(LENSES,
  l => agent(`${COMMON}\n\n${l.prompt}\nReport only real defects with a concrete scenario; style is out of scope.`,
    { label: `find:${l.key}`, phase: 'Find', schema: FIND }),
  (r, l) => r ? parallel(r.findings.map((f, i) => () =>
    agent(`${COMMON}\n\nTry to REFUTE this finding from a review of ${l.key}. Reproduce it by reading the code and running a
small case. Answer real=false if it does not reproduce, if the code is right for a reason the finder missed, or if its
impact on any result is nil; default to real=false when unsure. If real, give the smallest correct fix.\nFinding: ${JSON.stringify(f)}`,
      { label: `verify:${l.key}:${i + 1}`, phase: 'Verify', schema: VERDICT }).then(v => ({ lens: l.key, ...f, verdict: v })))) : [])
const all = out.flat().filter(Boolean)
return { confirmed: all.filter(f => f.verdict && f.verdict.real), refuted: all.filter(f => f.verdict && !f.verdict.real).map(f => ({ title: f.title, why: f.verdict.evidence })) }