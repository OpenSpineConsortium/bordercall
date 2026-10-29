export const meta = {
  name: 'clinical-reread-synthesis',
  description: 'Synthesise the 43 checked reread notes for the naming model and the autonomous anatomist, then critique and fix the synthesis',
  phases: [
    { title: 'Synthesise', detail: 'four topic syntheses: anomalies, measures, error and covariates, level atlas and playbook' },
    { title: 'Integrate', detail: 'one SYNTHESIS.md from the four parts' },
    { title: 'Critique', detail: 'an accuracy critic and a completeness critic' },
    { title: 'Fix', detail: 'apply every confirmed finding' },
  ],
}

const D = args.dirs
const COMMON = `
CONTEXT. greg, the owner (a spine surgeon-scientist), had all 43 papers he gave reread for clinical and anatomical detail,
to direct an "autonomous anatomist": an agent that names every vertebra. His pipeline (2026-10-28): a Bayesian generator
(bordercall's schwingcheck, on Panjabi's four papers; its measures are listed in ${D.repo}/schwingcheck/measures.py and
${D.repo}/schwingcheck/README.md, section "The measures") draws per-level morphometric dimensions with a patient size
factor; code computes the same dimensions from each vertebra instance of a real 3D CT mask (SPINEPS instance masks);
a classifier or the Bayes rule gives each instance a probability over levels; a sequence decoder (HMM or Viterbi chain over
the ordered instances, with transitions for a missing body, an L6 or a T13; bordercall's draft pull request 20 builds such
a chain) turns them into names. The same names are wanted on lateral and AP radiographs and fluoroscopy.

INPUTS. One checked note per paper: ${D.notes}/<id>.md, and its structured record ${D.notes}/<id>.json. Topic extracts of
all the records are in ${D.syn}/in/ (papers.json, anomalies.json, measures.json, errors.json, atlas.json). Read the notes
themselves wherever the extract is thin or you cite a detail; the notes are the authority, and the PDFs in ${D.papers}/
(<id>.pdf, read with the Read tool and its pages parameter) settle any doubt about a note.

RULES. Cite every statement by note id and page, as "(eisenstein1977 p. 177)". Where papers disagree, give each side with its
population and method; never average silently. Say what every count is made of (numerator, denominator, population, living
or cadaver or dry bone). Anything derived by you (a pooled prevalence, a recommended prior or error) is labelled
"Inference:" with its arithmetic and sources. Never invent a value; where the set holds nothing on a question, say so in one
line. Paraphrase; quote at most 12 words of any paper. ASCII only, LF line ends: no Unicode symbols, dashes, curly quotes,
Greek letters or emoji ("+/-", "deg", "mm", "sigma", "<="). Plain prose that says why; tables in markdown. Write instructions
as imperatives an agent or a programmer can act on. Before finishing, run LC_ALL=C grep -nP '[^\\x00-\\x7F]' on your file
and fix every hit.
`

const PARTS = [
  { key: 'anomalies', file: 'anomalies.md', title: 'Anomalies, numbering and the junctions', brief: `
Write ${D.syn}/anomalies.md. (1) A table of every anomaly prevalence the set reports: variant, population (country,
ethnicity, living or cadaver or dry bone, age), count and denominator, prevalence, how recognised (inspection, AP, lateral,
CT, MRI), paper and page. Include lumbarisation, sacralisation, transitional vertebrae (with any Castellvi-like grading),
L6, T13, 11 or 13 rib pairs, cervical ribs, persistent S1-S2 joints, sacro-transverse joints, spondylolysis, spina bifida,
trefoil canals, facet orientation variants, block vertebrae, and syndromes that change dimensions (Marfan dural ectasia,
achondroplasia, stenosis), and how each paper numbered levels and handled transitional segments (excluded, renumbered,
silent). (2) For each variant: how to recognise it on a CT instance mask, on an AP radiograph and on a lateral radiograph,
and what it does to the measures and to counting. (3) Priors for the sequence decoder: per variant, per population where
the set gives data, as Inference with arithmetic and ranges, and plainly what the set does not give (for example T13 or
cervical-rib prevalence if absent). (4) The junctions C2/C3, C7/T1, T12/L1 and L5/S1: every criterion the set gives for
telling the levels apart (ribs, costal facets, transverse processes, facet orientation switch, body shape, canal shape).` },
  { key: 'measures', file: 'measures.md', title: 'Every measure, as a recipe for a CT mask and a radiograph', brief: `
Write ${D.syn}/measures.md. Group by family: vertebral body (end-plate widths and depths, superior and inferior; anterior,
middle and posterior heights; wedge), end-plate concavity, disc heights, canal (sagittal diameter, interpedicular distance,
area, shape, lateral recess), pedicles (width, height, angles, chord length, isthmus, cortical wall), facets (width, height,
area, orientation angles, interfacet distance, tropism), laminae and processes, ribs and costal facets. For each measure:
(a) every definition the set uses, by paper, and which equals Panjabi's (bordercall's generator) and which differ, with the
bias a difference would put into a value extracted from a mask; (b) one consolidated recipe for computing it from a 3D CT
instance mask (which voxels or surface, which axis or plane, how to find the landmarks), labelled Inference where no paper
says; (c) how to take it from a lateral or AP radiograph alone, with magnification; (d) its course from C2 to S1 stitched
across papers, where it peaks or bottoms out and which adjacent levels it separates or fails to; (e) its covariates. End
with a feature-extraction specification: one line per generator measure in measures.py (by its key), the recommended mask
algorithm, the papers that define it the same way, and the known biases.` },
  { key: 'error', file: 'error.md', title: 'Measurement error, modality agreement and covariates', brief: `
Write ${D.syn}/error.md. (1) Every reliability figure in the set: intra- and inter-observer (ICC, kappa, mean differences),
repeatability, CT against direct or specimen measurement, radiograph magnification factors and tube distances, MRI against CT,
instrument resolution, partial-volume and cortical-thickness effects; a table by measure family. (2) Covariates: sex, age
(disc height changes, osteophytes, degeneration), stature and weight, and population (every population in the set against
Panjabi's 12 specimens), with magnitudes and pages. (3) Inference, labelled: a recommended measurement error (sigma_err) per
measure family for CT masks and for radiographs, and how the size factor should take height, sex and population, each with
the sources and the arithmetic. (4) What the set cannot tell.` },
  { key: 'atlas', file: 'atlas.md', title: 'Level by level, and a playbook for the autonomous anatomist', brief: `
Write ${D.syn}/atlas.md. (1) A level-by-level atlas from C2 to S1 (and L6 or T13 where present): every distinguishing
feature the set gives for each level, with the measures in which it is extreme or turns, and the pearls and pitfalls at that
level. (2) A playbook: an ordered procedure the autonomous anatomist follows to name every vertebra instance on a 3D CT, and
separately on an AP and a lateral radiograph or fluoroscopy frame of a limited field of view: which anchors to find first,
how to count, how to check ribs, costal facets, transverse processes and facet orientation, how to recognise and resolve a
transitional or anomalous segment, which measures to extract for the Bayes rule and how, which red flags (Marfan widening,
trefoil canal, spondylolysis, degeneration, osteophytes, wedge fracture) distort which measures, and when to answer with
uncertainty instead of a name. Every step cites its papers.` },
]

const FINDINGS = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      kind: { type: 'string', enum: ['wrong', 'unsupported', 'missing', 'rule', 'unclear'] },
      where: { type: 'string', description: 'section or line of SYNTHESIS.md, or the note id for a missing item' },
      what: { type: 'string' }, fix: { type: 'string' }, source: { type: 'string', description: 'note id and page that proves it' } },
      required: ['kind', 'where', 'what', 'fix'] } },
    summary: { type: 'string' },
  },
  required: ['findings', 'summary'],
}

phase('Synthesise')
await parallel(PARTS.map(p => () => agent(`You write one part of a synthesis of 43 research notes: "${p.title}".
${COMMON}
${p.brief}
Return one paragraph saying what the part covers and its largest gaps.`, { label: `synth:${p.key}`, phase: 'Synthesise' })))

phase('Integrate')
await agent(`Integrate four synthesis parts into one document, ${D.syn}/SYNTHESIS.md.
${COMMON}
The parts: ${PARTS.map(p => `${D.syn}/${p.file} (${p.title})`).join('; ')}.
Write SYNTHESIS.md: a title; the source line "Source: thread \\"Reread every paper for clinical detail\\", project symphony_4,
2026-10-28; the 43 notes beside this file."; a section "What this means for the naming model" of at most 15 numbered points,
each cited, that a reader can act on first (the anomaly priors for the decoder, the measures whose definitions differ from
Panjabi's, the error to use, the junction rules, the red flags); then the four parts as sections, kept whole, made consistent
in terms and cites, duplicates merged, nothing of substance dropped; then "The papers" as a table of all 43 notes (id, first
author and year, population and n with what it is made of, modality, what it is best used for). Keep SYNTHESIS.md ASCII.
Return one paragraph on what you merged or dropped and why.`, { label: 'integrate', phase: 'Integrate' })

phase('Critique')
const critiques = await parallel([
  () => agent(`You are the accuracy critic of ${D.syn}/SYNTHESIS.md. Assume it is wrong until the notes prove otherwise.
${COMMON}
Check at least 80 of its statements, every number and prevalence among them and every point of "What this means for the
naming model", against the note and page it cites (and the PDF where the note is unclear). Report every wrong, unsupported or
unclear statement, every count that does not say what it is made of, every Inference not labelled, and every rule broken.`,
    { label: 'critic:accuracy', phase: 'Critique', schema: FINDINGS }),
  () => agent(`You are the completeness critic of ${D.syn}/SYNTHESIS.md.
${COMMON}
Read every one of the 43 notes in ${D.notes}/ (all of them, not a sample) and report every clinically or anatomically useful
detail that matters for naming vertebrae or for extracting the generator's measures from a CT mask or a radiograph and that
SYNTHESIS.md leaves out or states more weakly than the note: anomalies and prevalences, measure definitions and projections,
level-specific features, junction criteria, error figures, covariates, pearls and pitfalls, playbook steps. Give the note id
and page for each.`,
    { label: 'critic:completeness', phase: 'Critique', schema: FINDINGS }),
])
const all = critiques.filter(Boolean).flatMap(c => c.findings)
log(`${all.length} critic findings`)

phase('Fix')
const fixed = await agent(`Apply the critics' findings to ${D.syn}/SYNTHESIS.md.
${COMMON}
FINDINGS (JSON): ${JSON.stringify(all)}
For each finding, check it against the cited note (and the PDF if needed). Apply it if it holds; skip it if it does not,
saying why. Add missing details in the section where they belong; correct wrong ones in place. Keep the document ASCII and
coherent. Return a list: for each finding, applied or skipped and why.`,
  { label: 'fix', phase: 'Fix', schema: { type: 'object', properties: { outcomes: { type: 'array', items: { type: 'object', properties: {
    what: { type: 'string' }, outcome: { type: 'string', enum: ['applied', 'skipped'] }, why: { type: 'string' } }, required: ['what', 'outcome'] } } }, required: ['outcomes'] } })
return { findings: all.length, kinds: all.map(f => f.kind), outcomes: fixed ? fixed.outcomes : null, summaries: critiques.filter(Boolean).map(c => c.summary) }
