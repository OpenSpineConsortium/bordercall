export const meta = {
  name: 'clinical-reread-group',
  description: 'Reread a group of spine papers for clinical detail: one note per paper, then an adversarial check of each note against its PDF',
  phases: [
    { title: 'Read', detail: 'one reader per paper writes its note and structured record' },
    { title: 'Check', detail: 'one skeptic per note rereads the PDF, fixes errors and omissions' },
  ],
}

const D = args.dirs
const CONTEXT = `
WHY THIS READING EXISTS. greg (the owner, a spine surgeon-scientist) asked for every paper he gave to be reread for its
clinical and anatomical detail, not only its printed values: transitional anomalies (lumbosacral transitional vertebrae,
sacralisation, lumbarisation, L6, T13, 11 or 13 rib pairs, cervical ribs, block vertebrae) with their prevalence by
population; indications; how each measure is taken and on which projection (for example the posterior canal from a
lateral radiograph alone); details level by level and at the junctions (C2/C3, C7/T1, T12/L1, L5/S1); measurement error
and reliability; and the author's pearls and pitfalls. His words: Eisenstein's "entire discussion is about lstv, different
indications and prevalences, radiographic projection of morphological metrics including how to measure certain things like
the posterior canal using just a lateral xray and the intricacies all the way down to specfic levels and pearls and pitfalls".
He wants these details to direct an "autonomous anatomist": an agent that names every vertebra.

THE PIPELINE THE NOTES SERVE (greg's direction of 2026-10-28). A Bayesian generator (bordercall's schwingcheck, built on
Panjabi's four papers) draws per-level morphometric dimensions (end-plate widths and depths, body heights, canal width and
depth, pedicle width and height, facet dimensions and angles, and so on) for levels C3 to L5, with a patient size factor.
Real data arrive as a 3D CT with an instance segmentation of the vertebrae (SPINEPS masks: one mask per vertebra, unnamed,
with subregions such as body and posterior elements where the segmenter gives them). Code must compute, from each instance
mask, the SAME dimensions the generator draws, defined the same way; a classifier or the Bayes rule then gives each
instance a probability over levels, and a sequence decoder (an HMM or Viterbi chain over the ordered instances, with
transitions for a missing body, an L6 or a T13) turns them into names: a semantic segmentation. The same names are wanted
on lateral and AP radiographs and fluoroscopy. So for every measure the note must say exactly how it is defined, which
landmarks, which plane or projection, how one would take it from a 3D instance mask (which part of the mask, which axis),
whether a lateral or an AP radiograph alone can give it and how, how it changes from level to level (which adjacent levels
it separates, where it peaks or bottoms out), how it depends on sex, age, body size and population, and how large its
measurement error is. For the decoder, every anomaly prevalence with its population and denominator matters.

RULES (hard):
- Read the WHOLE paper, every page: abstract, methods, results, every table and figure with its caption, discussion,
  conclusions. Use the Read tool on the PDF with the pages parameter (at most 20 pages per call) so you see the page
  images; take every number from the page image. pdftotext (Bash) may help you search a text layer, but some papers are
  scans with no text layer or a poor OCR layer, and OCR numbers are not trusted.
- Paraphrase. Never copy a passage of the paper's text into the note; a quoted phrase of at most 12 words is allowed only
  where the author's exact wording matters (a definition, a named sign), in double quotes, with its page. No page image,
  no figure, no table reproduced whole: give the values that matter with their table and page.
- Never copy any download stamp, IP address, institution name or date line printed by a publisher's download service
  (the Hinck 1966 PDF has one on every page); never mention it.
- Cite every detail by printed journal page and PDF page, as "p. 176 (PDF 2)", plus the table or figure where there is one.
- Say what every count is made of ("2,166 lumbar vertebrae of 433 skeletons", "36 men and 44 women"), and the population
  (country, ethnicity, living patients or cadavers or dry bone, age range).
- Mark anything that is your own inference, not the paper's statement, with "Inference:". Never invent a value.
- ASCII only and LF line ends: no Unicode symbols, no em or en dashes, no curly quotes, no emoji, no Greek letters (write
  "+/-", "deg", "mm", "x", "mu", "sigma", "<=", ">="). Plain prose that says why; short bullets are fine.
- The note is confidential research for a private repository; that is fine, nothing here is published.
`

const NOTE_TEMPLATE = `
THE NOTE (markdown), in this order, with these headings:
# <first author> <year>: <short title>
Source line: "Source: thread \\"Reread every paper for clinical detail\\", project symphony_4, 2026-10-28." then the full
citation as printed on the paper's first page (every author, title, journal, year, volume, issue, pages), and the copy read
(its origin and the first 16 hex of its sha256, both given to you).
## What the paper is
Design, population and denominators, modality and instrument, levels covered, how levels were identified and counted (and
whether transitional segments were excluded or how they were handled), inclusion and exclusion criteria.
## Anomalies, numbering and transitional segments
Every mention, with prevalence, denominator, population, how it was recognised and on which projection; how the author
numbered levels; what the anomaly does to the measures. If the paper says nothing, say so in one line.
## Measures, each as a recipe
One subsection per measure the paper defines or reports: its name and abbreviation; the exact landmarks; the plane or
projection; the instrument; the levels; then "From a 3D CT instance mask:" (how to compute it, which part of the mask,
which axis; say Inference: where the paper does not say), "From a radiograph alone:" (lateral or AP, or not possible, and
magnification), "Across levels:" (its shape C2 to S1 as far as the paper covers: where it peaks, where it is smallest,
which adjacent levels it separates or fails to), "Sex, age, size, population:", "Error:" (intra- and inter-observer,
repeatability, instrument resolution, magnification).
## Level by level and at the junctions
Everything the paper says about particular levels and the junctions.
## Measurement error and reliability
## Clinical pearls, indications and pitfalls
What the author says matters clinically (stenosis thresholds, syndromes such as Marfan or achondroplasia, screw sizing,
safe zones), and every pitfall of measuring or of anatomy.
## Instructions for the autonomous anatomist
A numbered list of imperative instructions an agent can act on, each tied to a page: what to look for, on which
projection, at which level, how to measure, what to compare it with, what goes wrong and how to guard against it.
## For bordercall's generator and classifier
(a) anomaly priors for the sequence decoder; (b) measures the generator holds or could add, and any difference between this
paper's definition and Panjabi's or a CT mask's that would bias a value extracted from a mask; (c) measurement error to use;
(d) size, sex and population covariates. Say plainly where the paper gives nothing.
## Gaps and conflicts
What the paper leaves unsaid, internal inconsistencies (text against table), and anything that disagrees with other papers
you know of in this set (label it Inference if from memory).
`

const RECORD_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    citation: { type: 'string' },
    population: { type: 'string', description: 'country/ethnicity, living/cadaver/dry bone, n with what it is made of, ages, sexes' },
    modality: { type: 'string' },
    levels_covered: { type: 'string' },
    anomalies: { type: 'array', items: { type: 'object', properties: {
      variant: { type: 'string' }, finding: { type: 'string', description: 'prevalence with numerator/denominator and what it is made of, or the qualitative statement' },
      population: { type: 'string' }, how_identified: { type: 'string' }, page: { type: 'string' } }, required: ['variant', 'finding', 'page'] } },
    measures: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, definition: { type: 'string', description: 'landmarks, plane, instrument' },
      projection: { type: 'string', description: 'dry bone caliper, CT axial/sagittal/3D, MRI, AP radiograph, lateral radiograph' },
      levels: { type: 'string' }, ct_mask_recipe: { type: 'string' }, radiograph_recipe: { type: 'string' },
      level_pattern: { type: 'string' }, covariates: { type: 'string' }, error: { type: 'string' }, page: { type: 'string' } },
      required: ['name', 'definition', 'projection', 'page'] } },
    level_details: { type: 'array', items: { type: 'object', properties: {
      level: { type: 'string' }, detail: { type: 'string' }, page: { type: 'string' } }, required: ['level', 'detail', 'page'] } },
    errors: { type: 'array', items: { type: 'object', properties: {
      what: { type: 'string' }, value: { type: 'string' }, page: { type: 'string' } }, required: ['what', 'value', 'page'] } },
    pearls_pitfalls: { type: 'array', items: { type: 'object', properties: {
      text: { type: 'string' }, page: { type: 'string' } }, required: ['text', 'page'] } },
    instructions: { type: 'array', items: { type: 'object', properties: {
      text: { type: 'string' }, page: { type: 'string' } }, required: ['text', 'page'] } },
    bordercall: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['id', 'citation', 'population', 'modality', 'levels_covered', 'anomalies', 'measures', 'level_details', 'errors', 'pearls_pitfalls', 'instructions', 'bordercall', 'gaps'],
}

const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    pages_read: { type: 'string', description: 'which PDF pages you viewed as images' },
    corrections: { type: 'array', items: { type: 'object', properties: {
      kind: { type: 'string', enum: ['wrong', 'missing', 'unsupported', 'rule'] },
      what: { type: 'string' }, fix: { type: 'string' }, page: { type: 'string' } }, required: ['kind', 'what', 'fix'] } },
    verdict: { type: 'string', description: 'one paragraph: how complete and correct the note now is' },
    record: RECORD_SCHEMA,
  },
  required: ['id', 'pages_read', 'corrections', 'verdict', 'record'],
}

function paperBlock(p) {
  let s = `PAPER: ${p.id}\nPDF: ${D.papers}/${p.file} (${p.pages} pages${p.scan ? ', a scan with NO text layer: read every page as an image' : ''})\n`
  if (p.extra) s += `ALSO READ: ${D.papers}/${p.extra}\n`
  s += `Copy read (for the source line): ${p.origin}; sha256 begins ${p.sha}\n`
  if (p.focus) s += `SPECIAL ATTENTION: ${p.focus}\n`
  return s
}

function readPrompt(p) {
  return `You are rereading one published spine paper for its clinical and anatomical detail.
${CONTEXT}
${paperBlock(p)}
Write the note to ${D.notes}/${p.id}.md with the Write tool, following the template below, then return the structured
record (the same content, compact). Be complete: every clinically or anatomically useful detail the paper holds belongs in
the note; nothing padded, nothing invented. Before you finish, run
  LC_ALL=C grep -nP '[^\\x00-\\x7F]' ${D.notes}/${p.id}.md
and fix every non-ASCII character it finds.
${NOTE_TEMPLATE}`
}

function checkPrompt(p) {
  return `You are the skeptic for one research note about a published spine paper. Another reader wrote the note; assume it
is wrong and incomplete until the paper proves otherwise. Your job is to make it correct and complete.
${CONTEXT}
${paperBlock(p)}
NOTE: ${D.notes}/${p.id}.md

Do this:
1. Read the whole PDF yourself, every page as an image (Read with pages, at most 20 per call), independently of the note.
2. Check every statement and every number in the note against the page it cites: value, units, level, sex, table, page
   (printed and PDF). Fix each wrong one in the note (Edit tool).
3. Hunt omissions: anything clinically or anatomically useful the paper says that the note leaves out, especially
   anomalies and their prevalence, how each measure is defined and on which projection, level-specific statements,
   junctions, error and reliability, the discussion's pearls and pitfalls, and limitations the author admits. Add them.
4. Check the instructions for the autonomous anatomist: each must be actionable and supported by the cited page; remove or
   relabel as Inference anything the paper does not support.
5. Enforce the rules: no copied passages (quotes at most 12 words), no download stamp or IP or institution line, every
   count says what it is made of, ASCII only (run LC_ALL=C grep -nP '[^\\x00-\\x7F]' on the note and fix every hit),
   the source line and full citation present, the template's headings present.
Then write the final structured record (as the reader's, corrected and completed) to ${D.notes}/${p.id}.json with the Write
tool as pretty JSON, and return it with your list of corrections.
${NOTE_TEMPLATE}`
}

const results = await pipeline(
  args.group,
  p => agent(readPrompt(p), { label: `read:${p.id}`, phase: 'Read', schema: RECORD_SCHEMA }),
  (rec, p) => agent(checkPrompt(p), { label: `check:${p.id}`, phase: 'Check', schema: CHECK_SCHEMA })
    .then(c => c ? { id: p.id, corrections: c.corrections.length, kinds: c.corrections.map(x => x.kind), verdict: c.verdict, pages_read: c.pages_read } : { id: p.id, failed: true }),
)
const failed = results.filter(r => !r || r.failed)
log(`${results.length - failed.length} of ${args.group.length} papers read and checked; failed: ${failed.map(r => r ? r.id : '?').join(', ') || 'none'}`)
return results
