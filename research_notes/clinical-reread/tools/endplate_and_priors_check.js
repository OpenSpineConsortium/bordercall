export const meta = {
  name: 'endplate-verdict-and-priors-check',
  description: 'Three refuters attack the Panjabi end-plate verdict, a verifier checks the anomaly priors, then a reviser applies what holds',
  phases: [
    { title: 'Refute', detail: 'three refuters on the end-plate verdict, one verifier on the anomaly priors' },
    { title: 'Revise', detail: 'apply the confirmed findings to the end-plate note' },
  ],
}

const SP = args.sp
const REPO = args.repo
const NOTE = `${REPO}/research_notes/panjabi-endplate-inclination.md`
const COMMON = `
SETTING. bordercall (${REPO}, a private, confidential repository) builds a Bayesian rule that names vertebrae from
morphometric measures; its table comes from Panjabi's four cadaver papers (1991 cervical, 1991 thoracic, 1992 lumbar,
1993 facets; all twelve C2-L5 spines). The code is ${REPO}/schwingcheck/ (measures.py, table.py, rule.py, README.md,
mnemonics.py, data/panjabi_long.csv) and the older package ${REPO}/archive/bordercall/. Per-paper reading notes,
each checked by two readers, are ${REPO}/research_notes/clinical-reread/notes/<id>.md (and <id>.json).
The PDFs are ${SP}/papers/<id>.pdf (ids: panjabi1991c, panjabi1991t, panjabi1991t_p892 (printed p. 892 of the thoracic
paper, scanned alone), panjabi1992, panjabi1993f, tan2004, gilad1985, bonczar2024, frontphys2026, moncadahabib2025,
abbas2021, busscher2010, kunkel2011, vanderhouwen2009, eisenstein1977, duman2026, ahn2001, hinck1966, olsewski1990,
tang2016, italianmri and the rest of the 43). Read a PDF with the Read tool and its pages parameter; where a printed
digit matters, render the page yourself (pdftoppm -r 200 -f N -l N -png <pdf> <prefix>) into your own folder
${SP}/work/<your label>/ and read the image. A Python with numpy and scipy is ~/venv-sc/bin/python.

RULES. Never run a git command that changes anything; never commit; never write any file inside ${REPO} unless your
task says to. Never copy more than 12 consecutive words of a paper. ASCII only in anything you write. The network
refuses PubMed, Europe PMC, EBI and Crossref from this machine, so a claim that rests only on those searches cannot be
rechecked: say so, never guess. Cite every finding by file and printed page (and PDF page), or by file and line for code.
Arithmetic you do is labelled Inference with the numbers.
`
const FINDINGS = {
  type: 'object',
  properties: {
    checked: { type: 'integer', description: 'how many distinct claims you checked' },
    main_conclusion_refuted: { type: 'boolean' },
    main_conclusion_assessment: { type: 'string', description: 'one paragraph: does the part you checked hold, and how strongly' },
    findings: { type: 'array', items: { type: 'object', properties: {
      section: { type: 'string' }, claim: { type: 'string' },
      verdict: { type: 'string', enum: ['wrong', 'unsupported', 'overstated', 'needs_caveat', 'missing', 'holds'] },
      evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['section', 'claim', 'verdict', 'evidence', 'fix'] } },
  },
  required: ['checked', 'main_conclusion_refuted', 'main_conclusion_assessment', 'findings'],
}

const REFUTERS = [
  { key: 'panjabi-own', brief: `Your part: section 1 (the answer) and section 2.1 (Panjabi's own papers) of the note. Assume the
note is wrong. Check every value and page it quotes from panjabi1991c, panjabi1991t, panjabi1991t_p892, panjabi1992 and
panjabi1993f against the page images you render: the disputed 20 numbers, the C2 column's dashes and numbers, the decimal
quirk (count the one-decimal SEMs yourself in lumbar Tables 2 to 5 and in the cervical tables), the junction table, the
Methods comparison, the acceptance dates, the thoracic EPIt = EPItu + EPItl check. Rerun the repeat search:
~/venv-sc/bin/python ${REPO}/research_notes/panjabi-endplate-inclination-scripts/runs.py ${REPO}/schwingcheck/data/panjabi_long.csv
and check its counts against the note. Then argue the strongest case for the opposite direction (the lumbar row is the
original and the cervical a copy, or both are a third table) and say whether the evidence excludes it. Report every
error, every overstatement and anything the note leaves out that bears on the direction.` },
  { key: 'others', brief: `Your part: section 2.2 (the other papers on Panjabi's footing) and the parts of 2.3 that the PDFs in
hand can check (tan2004 Table 2, the Kunkel 2011 note; Breglia, Ceran, Bellina, Lavecchia and Kunkel 2010 are not in
hand, so mark those unverifiable here). Assume the note is wrong. Check every Tan 2004 value in the table against
tan2004's page images (Table 1, printed pp. 140 to 141), Tan's sign and SEM definitions, the inferred sign convention
(EPItl - EPItu against Tan's wedge at L1, L2, L5), every L5 source value (gilad1985, bonczar2024, frontphys2026,
moncadahabib2025, abbas2021, busscher2010) and every wedge the note infers from printed heights and depths (redo the
arithmetic). Rerun ~/venv-sc/bin/python ${REPO}/research_notes/panjabi-endplate-inclination-scripts/calibrate.py and check its
typed inputs against the pages. Check the z-scores and the triangle-inequality cap argument (is a body wedge really
bounded by EPItu + EPItl when the two angles are unsigned and taken from a transverse plane set by the posterior wall?).
Report every error and overstatement, and anything that would change the cervical-versus-lumbar verdict.` },
  { key: 'rule', brief: `Your part: section 3 (what it means for the rule) and section 4. Assume the note is wrong. Check every
statement about bordercall's code against the code: that both measures are in the pool of 32 and not among the seven;
that no measurer reads them; measures.select and measures.pool behaviour; the table SD = SEM x sqrt(12) (schwingcheck/table.py
near line 275); the 3 deg angle error (README); the log densities in option 1 (-5.53 as L5, -3.56 as L1, -3.79 as L3 for a
lower plate of 10.5 deg) and in option 2 (peak -2.02, -2.08 at T12) - recompute them from the table and the rule's
terms in ${REPO}/schwingcheck (state the formula you used); the curve-table rows 23-24 and 30-31 against schwingcheck/README.md;
the list of results kept whole versus kept only for the generator's world. Then judge the recommendation itself: is
option 4 (drop both measures from the pool now) the right call, or would another option be better for the naming rule,
and are option 2's and option 3's dismissals sound? Also check that the end-plate measures are already left out where the
comparison research_notes/paper-tables/tools/cross_naming.py says they are. Report every error and every overstatement.` },
]

phase('Refute')
const refuteJobs = REFUTERS.map(r => () => agent(`You are a second reader told to REFUTE a draft verdict, ${NOTE}: that Panjabi's
lumbar end-plate inclinations (1992 Table 2, L1 to L5) reprint his cervical C3 to C7 row (1991 Table 2), and that the rule
should drop both measures for now. Read the whole note first, then work only on your part.
${COMMON}
${r.brief}
Default to doubt: a claim you could not check is "unsupported", not "holds". List "holds" findings only for the
load-bearing claims you verified.`, { label: `refute:${r.key}`, phase: 'Refute', schema: FINDINGS }))

const priorsJob = () => agent(`You verify the anomaly priors a sequence decoder will use. The file is
${REPO}/research_notes/clinical-reread/synthesis/anomalies.md, a draft written from the notes by one writer and never checked.
Check sections 1.1, 1.2, 3 (all of 3.1 to 3.5) and 4.5 against the notes (eisenstein1977, duman2026, ahn2001, gilad1985,
hinck1966, olsewski1990, tang2016, italianmri, kunkel2011, busscher2010, panjabi1991t, panjabi1993f and any other
note a row cites) and against the PDFs where the number matters: every numerator, denominator, population, material
(living, cadaver, dry bone, CT), page, and the category definitions (for example, are Duman's rib categories mutually
exclusive as the draft says; does Eisenstein's 36 include or exclude the sacro-transverse joints; were the two L6 both
Sotho). Recompute every percentage and every Wilson 95% interval with Python and report any that differ by 0.1 point or
more. Judge every Inference: is the arithmetic right, is the reasoning sound (for example the claim that Duman would
log any rib below T12 as a lumbar rib, so T13 cannot exceed 2.3%; the Marfan split borrowing Eisenstein's type mix).
Do not edit the file.
${COMMON}
Return your findings, and a verified priors table for the decoder: one row per state or transition, with what the
count is made of.`, { label: 'verify:priors', phase: 'Refute', schema: {
  type: 'object',
  properties: {
    findings: FINDINGS.properties.findings,
    priors: { type: 'array', items: { type: 'object', properties: {
      state: { type: 'string' }, population: { type: 'string' }, numerator: { type: 'number' }, denominator: { type: 'number' },
      made_of: { type: 'string', description: 'what the count is made of: units, material, how recognised' },
      point_percent: { type: 'number' }, wilson_low: { type: 'number' }, wilson_high: { type: 'number' },
      source: { type: 'string' }, note: { type: 'string' } },
      required: ['state', 'population', 'made_of', 'point_percent', 'source'] } },
    not_in_the_set: { type: 'array', items: { type: 'string' } },
  },
  required: ['findings', 'priors', 'not_in_the_set'],
} })

const results = await parallel([...refuteJobs, priorsJob])
const refutes = results.slice(0, 3)
const priors = results[3]
const live = refutes.filter(Boolean)
log(`${live.length} of 3 refuters returned; priors verifier ${priors ? 'returned' : 'failed'}`)

phase('Revise')
const revised = await agent(`You revise ${NOTE}, a draft verdict on Panjabi's end-plate inclinations, after three second readers
tried to refute it. Their reports (JSON): ${JSON.stringify(refutes.map((r, i) => r ? { part: REFUTERS[i].key, ...r } : { part: REFUTERS[i].key, failed: true }))}
${COMMON}
For each finding that is not "holds": check it yourself against the page image, the note or the code it cites. Apply it if
it holds; skip it if it does not, and say why. A refuter that failed leaves its part unchecked: say so in the status
paragraph. Rewrite the status paragraph at the top of the note to say what was checked on 2026-10-29 in the thread "Finish
the clinical reread" (three refuters, one per part, then this revision; how many findings were applied and skipped),
what still rests on one reader (section 2.3's database searches, which this machine cannot reach), and the verdict's
strength after the check. Keep the note's structure, its citations and its plain style; ASCII only; edit the note in
place (you may write this one file in the repository). If the refuters showed the recommendation is wrong, change it and
say why. Also fix the two scripts' docstrings or paths if a refuter found them broken (runs.py takes the long table's
path as its argument). Return what you changed and a short text, for the thread that holds the chain of levels, saying
what it should do with endplate_incl and endplate_lower_incl.`, { label: 'revise', phase: 'Revise', schema: {
  type: 'object',
  properties: {
    outcomes: { type: 'array', items: { type: 'object', properties: { what: { type: 'string' }, outcome: { type: 'string', enum: ['applied', 'skipped'] }, why: { type: 'string' } }, required: ['what', 'outcome'] } },
    verdict_now: { type: 'string' },
    recommendation_now: { type: 'string' },
    for_chain_thread: { type: 'string' },
  },
  required: ['outcomes', 'verdict_now', 'recommendation_now', 'for_chain_thread'],
} })

return { refutes, priors, revised }