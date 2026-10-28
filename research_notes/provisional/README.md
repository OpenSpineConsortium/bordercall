# The provisional: WSU's draft and the Bayesian work

Thread "Decide how to handle the provisional patent", 2026-10-28, for greg's ask of 20:28 UTC: whether it is in
his interest to add the new Bayesian approach to the application WSU will file, and whether the approach is
different enough to file on its own. Kept here at his request of 21:32 UTC ("i also want the patent thread in
git"); the same analysis, private to greg, is the Claude Doc "Provisional: WSU's draft and the Bayesian work"
(https://claude.ai/artifact/SVcDbZVd3xStuABMJKs9aS). Confidential: nothing here goes to a public place.

This is not legal advice. It maps the technical facts so that greg's own patent attorney can advise quickly.
Ownership, a separate filing and whether to sign WSU's MOU and royalty agreement are questions for an attorney
who represents greg, not WSU's counsel, who represents WSU.

Who can read this: GitHub lists two people on bordercall on 2026-10-28, Gregory-Schwing-MD-PhD (admin) and
aschehr (write). greg chose to keep the note here knowing that (decision card, 21:34 UTC). Git keeps it in the
history even if it is deleted later.

What is not here: the email from WSU's technology transfer office and the draft application itself are
summarised below, not copied.

## Where things stand (handoff)

- On 28 Oct WSU's technology transfer office wrote that WSU claims ownership because WSU computing was used, and
  that it will file the provisional on Friday 30 Oct (WSU case 26-1902) unless it hears otherwise. greg plans a
  public disclosure on Saturday 1 Nov; the CNS talk is on 2 Nov.
- Answer given (thread, 20:59 UTC): do not add the Bayesian work to Friday's filing; let WSU file the chain; do
  not sign the MOU until an attorney of greg's own has read it; disclose none of the Bayesian work on 1 Nov;
  delete the Google AI Mode share link of 28 Oct.
- Held until greg's attorney has advised: the approved and unsent bordercall grid pilot, any use of the roughly
  2,000 labelled CTs or other WSU data on the Bayesian work, and the AIDaS repayment of Claude subscriptions.
- Owed by greg: an attorney this week (WSU's own procedure starts an application only after the MOU is signed,
  so the MOU question comes due before Friday); the requests to the office below; deleting the share link.
- Nothing was sent to WSU or anyone else from this thread.

## The short answer

Should the Bayesian approach go into WSU's application? No. Adding it puts it into a WSU application, which in
practice concedes the ownership question greg wants kept open. Two days is too little to describe it well, and
a provisional protects only what it describes (MPEP 211.05). Most of it is still synthetic results and plans.
Nothing forces a date, provided none of it is disclosed on 1 Nov.

Is it different enough to file on its own? Technically yes; legally that is not the test.

- It is a different invention. The draft names levels along a chain counted from a declared landmark and says
  that a single field with no landmark cannot be named. The Bayesian model names a run of vertebrae with no
  landmark, from measurements, under a model built from published cadaver tables; it integrates out the
  patient's size and answers only at a posterior of 0.99. The draft describes none of that.
- Whether it is greg's turns on what WSU resources went into it, not on how different it is, and on the fact
  that on 25 Sep he disclosed the same goal to WSU (Part A, naming levels on CT without counting from a fixed
  end; Part B, naming from local morphology) and listed WSU's grid and library as support.
- The broad idea is already public, partly through his own arXiv of 19 Sep, so only the specific mechanism can
  be claimed.

## What Friday's draft covers

The draft (case 26-1902) is about the chain: naming vertebral levels on a C-arm by linking overlapping
limited-field images into one patient-specific sequence from a declared landmark, and commanding the next
exposure from it. Its six independent claims:

- Claims 1, 10 and 11 (method, system, medium): link overlapping exposures by image content, form one element
  per body, name the run consecutively within an admissible ordering with a declared landmark at a terminus,
  compute a confidence from the lowest probability and a margin against a one-body shift, and command the next
  displacement in millimetres from the observed spacing.
- Claim 13: fewer exposures to name a vertebra far from the landmark.
- Claim 15, the alphabets: score per-body distributions against several admissible orderings (with L6, T13,
  four lumbar), consecutive and with a declared landmark at a terminus; output the winning ordering and its
  margin. Dependents add a log prior per ordering (69) and dynamic programming or Viterbi (70).
- Claim 55: margin-based control of the device.

On naming without a landmark the draft says the opposite of the Bayesian work. Its Field of Invention says the
information that tells a vertebra from its neighbour "is therefore not contained in the appearance of the
vertebra itself" and "cannot be remedied by improving the analysis of a single image"; later it says "On a
single limited field containing no landmark the alphabets cannot be distinguished". One sentence lists
"template matching, shape descriptors, and classical classifiers operating on engineered features" as
alternatives to a trained network, and the alphabet decoding may run on a CT volume, but every embodiment needs a
landmark. Every distribution in the draft is a categorical distribution over level names from the naming module;
no distribution of a measurement per level appears anywhere, and no learned producer of measurements, no
degradation of segmentations and no measurement model carried from CT to fluoroscopy (CT renders are used only
to train and test the detector).

## Overlap map

Each element of the Bayesian work (schwingcheck, the PyMC model, draft PR 20 and greg's direction of 28 Oct)
against Friday's draft, the 25 Sep disclosure, what is public and the prior art found.

| # | Element | In Friday's draft? | In the 25 Sep disclosure? | Public or prior art | Reading |
|---|---|---|---|---|---|
| E1 | Naming a window of consecutive bodies with no landmark, from measurements alone (the place summed out) | No; the draft requires a landmark and says it cannot be done | Yes as a goal (Part A, Part B) | greg's arXiv 2609.22760 (T12 against L1 from shape, AUC 0.990); Schinz et al. 2025; Klinder et al. 2009 (naming a run in CT with no reference structure, from shape models); Mohammed et al. 2020 (one vertebra's level from its mask's shape) | The idea is old and already in WSU's hands; only the mechanism can be new |
| E2 | Likelihood built from published cadaver tables (Panjabi), with no training images | No | No | Closest: forensic osteometry assigns an isolated vertebra to C3 to L5 from caliper measurements by discriminant analysis (Minetz 2011 and 2024; Zvyagin 2010), from its own samples, one bone at a time, with no run, size model or calibration | Novelty candidate |
| E3 | Patient size as a latent integrated out exactly, with a power per kind of measure | No (an anatomical spacing constant sets scale only) | No | Glocker et al. 2012 scale a per-level model by a patient size, as a point estimate; the arXiv divides each measure by the patient's median | Novelty candidate |
| E4 | A shared per-person deviation (correlation 0.5) across levels | No | No | Not found | Part of E2 and E3 |
| E5 | Summing out the place and the pattern of missed bodies | Related: offsets enumerated, the best kept, always anchored at a landmark | No | Enumerating placements and HMM or dynamic-programming decoding are old (Klinder 2009, Glocker 2012, Lessmann 2019, Chen 2020, Wang 2021) | Old machinery; new only with E2 and E3 |
| E6 | Answer only at posterior 0.99, else abstain; region and border claims by summing the posterior | Related: conformal prediction sets with a region-hierarchy fallback, and a margin-based confidence | Part A has an abstention | Selective classification is general; no automatic labeller found reports a calibrated probability | Same purpose as the draft, different mechanism; part of the candidate |
| E7 | L6, T13 and missed bodies as states of a Markov chain (draft PR 20) | Yes in landmark form: claims 15, 69, 70 | Part B couples alphabets with the count | Meng et al. 2021 to 2023 (graph edges for T13, L6, a missing T12); VERIDAH 2026 (11 to 13 thoracic, 4 to 6 lumbar by dynamic programming); Hanaoka et al. 2017 (whole-spine hypotheses by posterior); VerSe labels L6 and T13 | Old, and in WSU's draft |
| E8 | The auto-anatomist: a network that makes the named measurements on a 3D segmentation, visualisable | No | Part A computes per-vertebra features | Automated morphometry networks exist | Idea only, no code |
| E9 | A degradation ladder of segmentations down to HU thresholding | No | No | The Google AI Mode share link, if anyone can open it | Idea only (a mask-free HU mode exists in scanimport) |
| E10 | Carrying it to fluoroscopy through enhanced DRRs and FLUX realism | Partly: the detector is trained on CT rendered to synthetic radiographs | No | DRR-to-real transfer is well known; same share link | Weak novelty on its own |

The reading. Technically E1 to E6 fall outside the draft's claims: the draft needs a landmark and teaches that
landmark-free naming cannot work, while the Bayesian model names a window without one. So it is a different
invention from the chain, not a variant of it. Three questions remain:

1. Is it patentable? The broad idea (naming levels from shape without counting) is old (Klinder 2009, Mohammed
   2020, forensic osteometry since 2010), and partly in greg's arXiv and in the repository material that became
   public in August and September. Decoding with L6 and T13 is old too (Meng, VERIDAH, Hanaoka). Not found in a
   limited search, and so what could be claimed: a likelihood from published population tables; patient size
   integrated out exactly; joint naming of a 1 to 3 body window with calibrated posteriors and a 0.99 rule; and,
   once built, transitional places weighted by clinical frequency from measurements alone.
2. Who owns it? That turns on what WSU resources went into it (next section), and WSU will see it as the same
   family as Parts A and B.
3. Can it be used freely? Claim 15 covers decoding any per-body distributions against the alphabets with a
   landmark. The landmark-free core sits outside it, but a Bayesian posterior decoded with a landmark (a
   panorama reaching C2 or the sacrum, or fusion into the chain) would fall under claim 15, so combining the two
   may need a licence from WSU even if the Bayesian method is greg's.

## Where the Bayesian work was made

From bordercall's git history (108 commits on all branches), the grid's job logs (312 commits of the branch
grid in symphony-template) and the project records.

The core was made off WSU's machines. The repository was made on greg's own computer on the evening of 25 Oct
(182b3da). The first generative piece (e777cae, 26 Oct 00:34 UTC), the exact Bayes rule (00f969f, 26 Oct
17:45), the PyMC rewrite (b864ad4, 27 Oct 14:07), the build-up study (962985c, 28 Oct 17:07) and the chain of
levels (754c42e, 28 Oct 18:51) were written and run in claude.ai cloud sessions or on greg's computer. The
model's knowledge is Panjabi's published tables, and every result is synthetic. No grid job ever ran any of it:
no grid log mentions it, and the bordercall pilot approved on 25 Oct was never sent.

WSU appears at the edges:

| Touch | When | What | Weight (a reading, not a ruling) |
|---|---|---|---|
| WSU library | before 26 Oct; 28 Oct | A copy of Panjabi's thoracic paper came by document delivery to Wayne State; where a second scan the table uses came from is not recorded; another paper came "via the library" | Matters: the table rests on these papers |
| The Claude account | throughout | The claude.ai account is registered to greg's WSU address; who pays is not recorded; an AIDaS grant line would repay $1,500 of Claude subscriptions once an adjunct appointment starts | Matters if WSU money pays |
| WSU grid, one job | 28 Oct 01:04 | Job 40819848 fetched 17 open-access papers for the reading list behind the generator; WSU's Elsevier token was tried and refused | Small |
| WSU storage | 28 Oct 18:31 | Gold-tier CT masks (ENHANCE.PET, public) landed on WSU's Ceph for the next step; the rule has not used them | Small now |
| The precursor | Sep to 25 Oct | The shape classifier bordercall was ported from (CTSpinoPelvic1K, T12 against L1) is public, F30-funded in its first months, under WSU IRB HPR 2026-269; its per-level table was probably computed on the grid | Matters for the broad idea, less for the mechanism |
| WSU identity | 25 to 26 Oct | 14 commits carry greg's WSU address; a figure went to a OneDrive that is probably WSU's | Weak on its own |
| The white paper | 26 to 27 Oct | It cites the grid-computed chain numbers as preliminary data | Weak |

The next steps would make it plainly WSU-supported: training the auto-anatomist on the roughly 2,000 labelled CTs
on WSU's Ceph, the bordercall pilot on the grid, and the gold-tier work. Not known: who pays for each Claude
plan; whether greg's computer is personal (the path suggests so); how the ten closed papers uploaded on 28 Oct
were obtained; whether anyone else opened the share link, or another AI service given the idea (an upload titled
"Vertebral Labeling Graph Prior Art" suggests one).

## WSU's rules, as read on 2026-10-28

- The governing text is Board of Governors statute 2.41.04, "Patent and Copyright Policy" (adopted 1969,
  amended 13 July 1984), carried out by Executive Order 86-5 (1986). The PDF on the office's site, dated 2004, is
  an adaptation of the statute. The MOU calls it the statute "adopted July 11, 1984".
- 2.41.04.110: an invention is the inventor's if made "without University support (including salary, funds,
  facilities, equipment or services not available to the general public)"; the inventor reports it, and WSU
  acknowledges ownership in writing within 20 working days if it finds no support was used; it may ask for a
  sworn statement; a disagreement goes to the Patent Committee.
- 2.41.04.120: WSU has a right of first refusal to title in inventions made with University support, and in
  those "made by non-salaried personnel or other individuals affiliated with the University" with "University
  funds, facilities, or equipment"; it decides to acquire or waive within four calendar months of the report.
- 2.41.04.540: non-salaried personnel include "adjunct ... faculty, as well as undergraduate, graduate and
  postdoctoral students".
- Executive Order 86-5: section 5.2 counts "secretarial and computer" services as University involvement;
  section 6.0 says patent application procedures "may be initiated only after the inventor(s) has signed a
  Memorandum of Understanding", and that where WSU waives, it keeps a royalty-free licence; the Patent Committee
  recommends and the President decides.
- The MOU in the disclosure form says "the Inventors hereby assign to the University all their right, title, and
  interest in and to the subject invention(s)"; "subject invention(s)" is not defined in its body, and its recital
  says the invention was "developed with use of the University's facilities and/or other University support". The
  royalty schedule is 75, 50, 40 and 35 percent to the inventors by income band; ownership passes to the inventors
  if WSU makes no reasonable licensing effort within 24 months of a patent issuing.
- A provisional is filed by the inventor, or by someone the inventor has assigned to or must assign to (35 U.S.C.
  111(b); 37 CFR 1.46). It protects only what it describes, and lapses after 12 months. The US forgives an
  inventor's own disclosure within a year (35 U.S.C. 102(b)(1)(A)); Europe does not (EPC Articles 54 and 55).

## Options before Friday

| Option | Gain | Cost | View |
|---|---|---|---|
| 1. Let WSU file the chain (with the fixes below); keep the Bayesian work out and confidential; sign nothing until greg's attorney has read the MOU | The chain gets a date before 1 Nov; the Bayesian question stays open | Nothing, as long as none of it is disclosed | Recommended |
| 2. Add the Bayesian work to Friday's filing | A 30 Oct date for it | Concedes ownership in practice; too little time to describe it; most of its value is plans; the draft's opening argues against it | Only if an attorney finds WSU owns it anyway and it must be disclosed soon |
| 3. File greg's own provisional on it before 1 Nov | His own date, cheaply | A dispute if WSU's right of first refusal applies; nothing forces the date | Only on an attorney's advice, and reported to WSU |
| 4. Ask WSU to hold Friday's filing | Time | The chain loses its date before the 1 Nov disclosure | Not in his interest |

Whatever the choice: no grid job, WSU data or WSU money goes into the Bayesian work until the attorney has
advised; keep it on published tables, synthetic data and compute WSU does not provide, and ask the attorney
whether the Claude account registered to the WSU address should be replaced; report it to WSU only after advice.

## Questions for greg's own patent attorney

1. The MOU's reach: if signed, what does an undefined "subject invention(s)" reach? Can a schedule limit it to
   case 26-1902 as disclosed on 25 Sep and filed on 30 Oct, with an express carve-out for later work made without
   WSU support?
2. Filing without the signature: since Executive Order 86-5 starts an application only after the MOU is signed,
   what is the safest thing to sign by Friday, a narrowed MOU or a narrower authorisation to file? Does letting
   WSU file concede anything beyond what is filed?
3. Ownership of the Bayesian work under 2.41.04.110 or .120, on the facts above: employed by the DMC, F30 ended
   31 May, WSU degree, adjunct appointment pending; the non-salaried clause names adjuncts and graduate students.
   The dispute path (Patent Committee, then the President), and the royalty-free licence WSU keeps on a waiver.
4. Parts A and B: does the 25 Sep disclosure, which listed WSU's grid and library as support, give WSU a claim on
   the Bayesian method as an improvement or embodiment of Part A?
5. Reporting it under 2.41.04.110 now or later, and what the report should and should not contain.
6. greg's own provisional on the Bayesian method: whether, when, and the risk while ownership is unsettled.
7. His own earlier disclosures: the arXiv of 19 Sep, and repository material public in August and September (a
   Part A design note by 27 Aug, scripts and a Zenodo record on 7 Sep, Part B concepts pushed on 4 Sep and still
   fetchable by commit). What the US grace period covers, and the effect on foreign rights for both inventions.
8. The Google AI Mode share link of 28 Oct: a public disclosure? Is deleting it enough?
9. AI-assisted work: much of the code and writing came from Claude sessions under greg's direction. Conception,
   inventorship and the dated records to keep.
10. Grant money for tools: would the AIDaS repayment of Claude subscriptions make the work University-supported?
11. Next steps that touch WSU (the 2,000 CTs on WSU's Ceph under WSU's IRB): can they be structured so the
    method's ownership does not change?
12. The chain: federal funding rules through the F30; whether the royalty schedule and the 24-month reversion are
    negotiable; and whether using the Bayesian posteriors with a landmark needs a licence under claim 15.

## Requests for the office (everything said there reaches WSU)

1. The application exactly as it will be filed, with the cover sheet naming applicant and inventor, before Friday.
2. Written confirmation that the filing and any MOU concern case 26-1902 as disclosed on 25 Sep, and nothing later.
3. Which WSU resources WSU relies on for its ownership claim.
4. Confirmation that statute 2.41.04 and Executive Order 86-5 govern, and any University Patent Agreement greg
   signed as a student or resident (2.41.04.080 refers to one).
5. What exactly WSU needs from greg to file on Friday; greg wants his own counsel to read the MOU and royalty
   agreement first and will not hold up the filing.
6. The filing receipt (application number and date) as soon as it is filed; nothing is disclosed before it.
7. The plan for the 12-month deadline (non-provisional, PCT, foreign filings) and the NIH reporting for the F30.
8. The fixes below, before filing.
9. Whether the office will read the public CNS deck before 2 Nov.

Do not describe the Bayesian work to the office before the attorney has advised.

## What not to show or say on 1 November

1. Wait for the filing receipt; if the filing slips, the disclosure slips.
2. Nothing of the Bayesian work, results included, since no filing covers it: no method (the generative model,
   the likelihood from Panjabi's tables, the handling of size, naming without a landmark, the 0.99 rule, region
   and border claims, the Markov chain with L6 and T13), no numbers (47.3, 73.1 or 96.1 percent named from 1, 3 or
   9 bodies; 98.3 percent at 3 bodies with 32 measures), nothing of the auto-anatomist, the ladder or the eDRR and
   FLUX route.
3. None of the confidential decks or notes: archive/slides (exact_slides_cns.pdf, exact_slides_neurips.pdf,
   junction_slides.pdf) and archive/docs/SCHWINGCHECK_LEVELCHECK.md. bordercall stays private.
4. Nothing of Part A beyond what is already out; the 20 Oct answers planned it for a later provisional.
5. For the talk only the cleared deck, CNS2026_Schwing_NotAllSpines_public_v12.pptx, after the disclosure audit,
   and only chain content Friday's application as filed describes. Not the v13 deck: its slide 15, "Shape alone
   names the border, without a count", is the count-free naming that archive/HANDOFF.md says to clear with the
   office first.
6. In questions, do not explain how a level is named without a landmark.
7. Delete the Google AI Mode share link now.

## Fixes worth asking for in Friday's draft

1. Remove the drafting notes inside the claims ("Pattern: Example 48 claim 2 ... sidesteps Recentive"; "The
   strongest novelty. No surveyed method addresses transitional spines at all.") and "(ALTERNATIVE TITLES FOR
   COUNSEL ...)" from the title.
2. That second note is also wrong: Meng et al. 2021 model transitional vertebrae, VERIDAH 2026 decodes 4 to 6
   lumbar and 11 to 13 thoracic, and VerSe labels L6 and T13.
3. Three numbers the 20 Oct answers said to re-run or drop are still in: 85.8 against 95.5 percent decoded (18
   September corpus); the 4,792 query images, 95.7 against 95.3 percent; 2.2 percent missed and 17.9 percent
   entered twice on real radiographs (no result file named). The other corrections, such as the 120 held-out
   renders, are in.
4. Ask the attorney before asking WSU whether to soften the Field of Invention's statement that appearance cannot
   tell a vertebra from its neighbour. The chain does not need it; it may help or hurt a later Bayesian filing.
5. Smaller: the "Family F: additional claims drawn from the inventor responses of 20 October 2026" heading and
   the other family headings inside the claims; advocacy sentences in the description; the number of alphabets
   (four, five and six in different places); garbled wording in claims 7, 13, 17, 36 and 37; and the closing
   definition of the naming module, which requires a trained model and is narrower than the main text.

## Prior art read

A limited search (about 22 searches and 25 fetches), not a patent search: Meng, Boyer and Pujades, arXiv
2110.12177 (2021; MLMI 2022; CMIG 2023); Moeller et al., VERIDAH, arXiv 2601.14066 (2026); Hanaoka et al., IJCARS
2017; Glocker et al., MICCAI 2012; Klinder et al., Med Image Anal 2009; Lessmann et al., Med Image Anal 2019; Chen
et al., IEEE TMI 2020; Wang et al., CVPR 2021; Mohammed, Meng and Pujades, ShapeMI 2020; Minetz et al., AAFS 2011
and Forensic Anthropology 2024; Zvyagin and Karapetyan 2010; Schinz et al., Eur Spine J 2025; VerSe (Sekuboyina et
al. 2021). Not done: claim-level patent searching, Google Scholar, and full texts behind paywalls.

## Sources

- The draft application greg attached on 28 Oct, and the email from the office (summarised above, not copied).
- spine-program provisional_patent/: the 25 Sep disclosure package with its MOU and royalty agreement, the policy
  PDF, the 20 Oct answers and cover memo, and arXiv 2609.22760.
- bordercall: all branches and PR 20; archive/HANDOFF.md, the white paper and the slides.
- WSU: bog.wayne.edu/code/2-41-04; policies.wayne.edu Executive Order 86-5; the office's 2026 disclosure form.
- US and Europe: 35 U.S.C. 102, 111(b), 119(e); 37 CFR 1.46, 1.53(c); MPEP 211.05; EPC Articles 54, 55, 87 to 89.
