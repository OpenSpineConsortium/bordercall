# The clinical reread: synthesis

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29: the synthesis of the 43 checked notes in ../notes/; each part was drafted by one writer, read by an accuracy critic and four completeness critics, fixed against them and checked again by a second reader.

Confidential, like the rest of this repository.

This page is the way into the reread: what the 43 papers mean for the model that names every vertebra on a CT mask,
a radiograph or a fluoroscopy frame, the papers themselves, and the parts that hold the detail. The notes are the
authority; where a part or this page differs from a note, the note wins (atlas.md, opening).

How to read it:

- "(anomalies.md 3.2)" names a part of this folder and its section. "(eisenstein1977 p. 177)" names a note, linked
  in the table of papers below, and the paper's printed page as the note records it.
- A count is numerator/denominator with its unit and its material: living patients (CT, MRI or film), cadaver, or
  dry bone. A percentage or interval the paper does not print is Inference, computed in the part cited from the
  count beside it; intervals are Wilson 95%.
- "Inference:" marks arithmetic or a reading no paper states, with its inputs.

## What this means for the naming model

1. **Count from both ends and name from the sequence, never from one value.** Every norm in the set assumes 7
   cervical, 12 thoracic and 5 lumbar vertebrae (atlas.md 2A Step 5; panjabi1993f p. 1299); no paper gives a rule
   for numbering a spine with a transitional segment, and none reports a measure separately for a transitional
   spine (atlas.md, Part 2 opening; anomalies.md 1.6, 3.5). Neighbours from C3 to C5 and from T4 to T9 differ by
   under 1 SD in most of Panjabi's measures and under 1.6 SD in all (Inference in atlas.md, Part 2 opening, from
   panjabi1991c pp. 863-865 and panjabi1991t p. 892). What to do: anchor C2 by its lower-only uncovertebral
   surface, the column's largest superior facets (about 208 mm2, S above 90 deg) and its deepest canal (21.0 mm)
   in Panjabi's twelve spines (panjabi1993f pp. 1301-1303; panjabi1991c pp. 864-865), and by the dens, which is
   anatomy from outside the set (atlas.md 2A Step 4); anchor S1 by its collapsed lower surface and the ala. C2 and
   S1 lie outside the rule's pool of C3 to L5 (atlas.md, "How to read this part"), so both anchors are form calls,
   not likelihoods. Decode from both, and report a disagreement between the two counts as a candidate numerical
   variant, never as an average; carry C3 to C5 and T4 to T9 by count from a named neighbour and pass its
   uncertainty on; with one anchor in view, say which and carry that end's known failure (anomalies.md 4.5, rules
   1 and 4; atlas.md 2A Steps 5 and 11). A count down from C2 is untouched by any lumbosacral variant (atlas.md 2A
   Step 5). Changes: the chain of levels (bordercall pull request 20; bordercall's TODO.md, item P step e), which
   is to decode from both anchors and report where they disagree.

2. **Measure in the vertebra's own frame, from the right label and from the right start.** The archive measurer takes
   every extent along scanner axes, which mixes lordosis and rotation into the value (measures.md 2.1); Inference in
   measures.md 3.1: a 45 by 35 mm end plate turned 10 deg reads 45 cos 10 + 35 sin 10 = 50.4 mm, 5.4 mm high. Label
   61 is the canal's contents along the column, not one vertebra's bony canal, and SPINEPS has no pedicle and no rib
   label (measures.md 2.3). It is the only point that corrects measured values the runs on real masks use today: all
   seven measures the archive measurer gives are taken along scanner axes, and canal_w and canal_ap from label 61
   (measures.md 2.1, 2.3). mnemonics.py starts spinous_length at the canal's back wall, and the comment above
   SPINEPS_MAP in schwingcheck/measures.py and schwingcheck/README.md, "The pool", say Panjabi starts there, while
   the lumbar and thoracic papers start it at the upper end-plate centre, so a mask value taken by that text would
   read about half the table (measures.md 9.1, 11.8; panjabi1992 p. 302; panjabi1991t p. 893). What to do: build
   frame F from the posterior wall before any measure, take the canal from bone, cut the pedicle isthmus out of label
   41, start SPL at the cranial end-plate centroid (measures.md 2.2, 2.4, 6, 9.1), and make the other corrections of
   measures.md 11.8: h_post's AP regime, the demifacet and per-rib wording, the pedicle's isthmus claim, and
   Panjabi's specimens called embalmed when they were fresh autopsy spines cleaned to dry bone (panjabi1992 p. 299;
   panjabi1991t p. 888). Correct the three spinous texts, and the reason the README gives for leaving the archive's
   spinous extent unregistered: that extent starts at the body centroid, which matches the cervical text and lies
   about half a body height from the papers' start below C7 (measures.md 9.1, 11.8). Changes: the measurer,
   archive/bordercall/spineps_map.py (measure_vertebra and axes_from; label 61 for canal_w and canal_ap), which
   measures.MEASURERS names; the reread leaves the archive unchanged until the owner's word
   ([HANDOFF.md](../HANDOFF.md), step 4), so the fix lands there or in a new measurer the registry names.

3. **Set the decoder's transitions from the checked priors, say whose they are, and run their ranges.** The set's
   only count of lumbosacral variants in a general population is one series of 443 South African dry skeletons:
   six lumbar-type segments (2 true L6 and 9 lumbarised S1) in 11/443; a sacralised L5 in 8/443, only a ceiling
   for a lost segment, since the paper still counts five lumbar vertebrae per skeleton (Inference in
   anomaly-priors.md: 2,166 = 443 x 5 - 49); and a count-changing
   state of any kind in 11/443 to 19/443 (eisenstein1977 p. 177, p. 173; anomaly-priors.md: 2.48%, 1.81%, 2.48% to
   4.29%). The ribs come from 517 Turkish adults on CT: a lumbar rib in 12/517 and a twelfth rib absent on at
   least one side in 22/517. The decoder's states count neither as a change in the vertebral count, a modelling
   choice of anomalies.md 3.1, not a finding: the paper gives no criterion that tells a lumbar rib on L1 from a
   T13 (anomaly-priors.md; measures.md 10.3). T13 has no value and no bound anywhere in the set (duman2026 p. 10;
   anomalies.md 3.2). What to do: take six_lumbar at 11/443 (Wilson 95% 1.39 to 4.39%), which assumes every
   lumbarised S1 was a free segment, as the paper never states (anomalies.md 3.2); Inference: if none was, only
   the 2 true L6 change the count, so run 2/443 as the lower sensitivity end, and 27/443 as the upper only if the
   segmenter splits S1 off at a persistent S1-S2 joint (16/443); four_lumbar from 0 to 8/443 as a ceiling; t13 as
   a modelling choice, not a datum; no_rib_t12 from 0 to 22/517 as a ceiling for bilateral absence, the only case
   that slips a rib count, since laterality was never reported; lumbar_rib at 12/517 as a rib term at L1 with no
   count change; where sex is known, condition both on it: a twelfth rib absent on at least one side in 18/240
   women against 4/277 men, a lumbar rib in 10/277 men against 2/240 women, all Turkish adults on CT (duman2026
   p. 10, Table 5; anomalies.md 3.2, 3.3; anomaly-priors.md, "How to use them"); Marfan's 5/32 transitional
   vertebrae on films as one state of unknown type (ahn2001 p. 68). Keep the sacro-transverse joint (10/443) and
   the true transitional vertebra (1/443) as changes of shape or emission at L5, keep the missing-body transition
   apart, and run the ranges as a sensitivity study that reports how often the top path changes (anomalies.md
   3.1, 3.2; anomaly-priors.md, "How to use them"). Treat the generator's anomaly profiles as modelling choices
   too (schwingcheck/columns.py, _profile and profiles; SYNTH blend 0.5): six_lumbar keeps a typical L5 and
   appends an L6 at L5 + 0.5 (L5 - L4), and t13, lumbar_rib and no_rib_t12 draw a body half-way between T12 and
   L1, while no paper reports a measure of a body under any variant beyond smaller facets beside a
   sacro-transverse joint (anomalies.md 3.5). Run the blend at 0 and 1 beside 0.5, and an L6 arm in which the true
   L5 reads half-way between L4 and L5 and the L6 takes L5's profile, as atlas.md infers (the L6 section), in the
   same sensitivity study, and say so in schwingcheck/README.md, "The generator and the fields". Changes: the
   chain of levels (bordercall pull request 20; bordercall's TODO.md, item P step e), whose plan names
   transitions only for a missed body, an L6 and a T13: add four_lumbar and a rib term at L1; and the profiles in
   schwingcheck/columns.py.

4. **Name T12 and T1 by their form, and give the rib one term.** A twelfth rib short or absent on at least one side
   was found in up to 77/517 Turkish adults on CT (Inference: 55 hypoplastic + 22 absent = 77, an upper bound
   only if a patient can be counted in both rows, which the paper does not say; its Fig. 4A-B shows one patient
   with both), and where that rib is rudimentary the counts from the top and from the bottom often disagree on
   planning images and on fluoroscopy (duman2026 p. 10, p. 9, pp. 12-13; anomalies.md 1.2; atlas.md 2A Step 5).
   Today a rib seen or missed enters the rule nowhere: the generator's lumbar_rib and no_rib_t12 phenotypes draw a
   body half-way between the T12 and L1 profiles and carry no rib feature (measures.md 10). What to do: name T12
   by a costovertebral facet on the body, no costotransverse facet, and thoracic-type superior with lumbar-type
   inferior facets (anomalies.md 4.3, 4.5 rule 2; panjabi1991t p. 895); name C7 against T1 by transverse process
   width, the round T1 pedicle, the rib-1 facet and the drop in IPD (anomalies.md 4.2, 4.5 rule 3), and by IFWs
   (38.6 against 33.2 mm) and IFW/IFH (2.09 against 1.68) in Panjabi's twelve spines, but never by the paper's
   rule that IFW/IFH above 1.5 is cervical, which passes T1 (panjabi1993f p. 1302, Table 5; p. 1307; atlas.md 2A
   Step 4); look for a cervical rib (7/517 Turkish adults on CT, duman2026 p. 10) or a long C7 transverse process
   before naming C7 by its TPW (atlas.md 2A Step 4); store rib presence, the lower and costotransverse facets and
   the lowest rib's length per side as states, not as zeros (measures.md 10.4); read the ribs from the CT by a
   segmentation or trace of their own, since SPINEPS segments none (measures.md 10; atlas.md 2A Step 6).
   Inference, since duman2026 gives no rule: call a costal element on the first lumbar-type instance a lumbar rib
   on L1 only when twelve thoracic instances lie above it by count from C2 or T1, and treat that instance as a T13
   candidate when it has thoracic-type facets and a costovertebral body facet (atlas.md, the T13 section, and 2A
   Step 6 rule 4; measures.md 10.3). A T13 would carry a costovertebral facet too, so the T12 form rule alone
   cannot part T12 from T13 (anomalies.md 4.5 rule 2, which says the same of a rib-bearing L1, where anomalies.md
   2.4 and atlas.md's T13 section expect no body facet). The facet switch is a soft cue: it falls at T12-L1 only
   on average, its SEMs widen to 8.2-9.5 deg there against 0.9-2.8 deg at T1 to T10, and how often it falls
   elsewhere is not counted (panjabi1993f pp. 1303-1304; anomalies.md 3.5). Changes: a rib segmentation beside
   SPINEPS, rib states beside the measures registry (schwingcheck/measures.py), and the lumbar_rib and no_rib_t12
   phenotypes in schwingcheck/columns.py.

5. **Expect the 0.99 promise to fail on other people, and put the offsets in the means.** Careful studies of one
   measure differ by 2 to 8 mm between series, more than any observer error in the set; the authors and notes put
   most of it down to definition, but no comparison in the set separates definition from population (error.md 1.7,
   4). tan2004's factors against Panjabi run from 0.60 to 1.16, so no single population scale fits (error.md 2.4,
   3.6). On fields drawn from 25 papers' own printed means and SDs (one series per paper, 200 fields per place), the
   rule built on Panjabi's table named three bodies exactly in 23.7% of fields against 47.2% on fields drawn from his
   own table, and was right on 88.8% of the 660 fields it named at 0.99 against 100.0% of 2,851; widened by the
   papers' spread it was right on 92.0% of 591; at one body it was right on 87.7% of 310 as built and 89.5% of 257
   widened ([paper-tables results](../../paper-tables/results/README.md), "Naming the papers' fields with Panjabi's
   rule"). Inference: widening gains 3.2 points at three bodies (92.0 - 88.8) and 1.8 at one (89.5 - 87.7), so it
   does not restore the promise; until masks of real spines calibrate the rule, a posterior of 0.99 means about 0.9
   right, at one body or three, on another series' tables. Over 11 papers, canal depth sits a median 1.48 of
   Panjabi's SDs from his means (same page, "How far the papers sit from Panjabi"). These are draws from printed
   tables, not real spines. What to do: estimate population terms per measure family only from same-method contrasts,
   and definition offsets apart from them, by running one mask pipeline over each population's images; name the rest
   as a known gap, never folding it into sigma (error.md 3.1, 3.6). Inference, from the widened arm of the
   paper-tables results: widen the rule by the between-paper spread until masks of real spines can calibrate it,
   knowing that it buys 2 to 3 points of the promise at one and three bodies (8.5 at five, 94.4 - 85.9).

6. **Set each error term from its bracket, never below it, and give the canal heavy tails.** Of the 43 papers, 16
   measured their own error, 5 checked only an instrument and 22 nothing; none measured an automated mask
   (error.md 1.1). An error set too small breaks the calibration: the archive's record, which took 3 mm of error
   as 1 mm, was right at 0.99 only 82.6% of the time at three bodies, while doubling the errors in the build-up
   study cost share named (73.1% to 63.0% with seven measures) and left the answers at 0.99 right, because rule and
   generator moved together (error.md 0). In one CT series of 200 Bosnian patients with lumbar pain, canal maxima
   reach 4.6 SD above the level mean (Inference in error.md 3.1: (30.8 - 17.79) / 2.84 at the male L5, cizmic2023
   p. 202); the note suspects that some are transitional or misnumbered segments, so a heavy tail tolerates
   biology and may also hide a naming error. What to do: keep 1 mm for in-plane body and canal lengths on thin CT
   (bracket 0.8 to 1.3 mm; error.md 3.2 recommends 1.0); posterior height sqrt(0.65^2 + (0.41 dz)^2) and at least
   1 mm, dz the slice spacing; pedicle height 1.0 to 1.4 mm by slice spacing; areas sqrt(pi A / 2), traced; angles
   3 deg; run the spinous and transverse lengths at both c = 0.013 and c = 0.05 in sqrt(1 + (c L)^2), since the
   set does not settle that term; and give the canal a Student t or log-scale likelihood widest at L5 (error.md
   3.2, 3.8). Inference: flag any canal value past 3 SD at its named level for the red-flag check of point 14; a
   log-scale normal can keep the rule's closed form if both the spread and the error are taken in log units
   (schwingcheck/README.md, "The rule"), while a Student t needs a new likelihood in rule.py and the same in the
   generator, changed together so the two never part (error.md 0). Changes: LENGTH_ERROR_MM and ANGLE_ERROR_DEG in
   schwingcheck/measures.py, and the canal's likelihood.

7. **Build the transverse_width measurer first, and hold cross-paper steps as upper bounds.** At T12/L1 none of the
   four strongest measures has a measurer today. The two largest steps there, transverse_width (+4.01 SD) and
   spinous_length (+3.99 SD), both cross from Panjabi's thoracic table to his lumbar one; tan2004 and busscher2010,
   each measured within one series, show the TPW step, tan2004 at about half its size (+12.6 and about +24.6 mm
   against Panjabi's +24.3), but not the SPL step (+3.0 and +4.3 against +20.3) (Inference in measures.md 9.1, 9.2
   and atlas.md 2A Step 9a). TPW's absolute values sit far from Panjabi's: tan2004 reads 15.6% below on average and
   24.7% at L1 (measures.md 9.2), a median 1.76 of his SDs and 1.63 levels over 22 cells ([paper-tables
   results](../../paper-tables/results/README.md), "How far the papers sit from Panjabi"). The seven measurers that
   exist carry no strong step at C5/C6, T1/T2 or T12/L1, or anywhere from L1 to L5 (Inference in atlas.md 2A Step
   9a). What to do: add transverse_width, which serves seven junctions, then the interfacet widths and facet S, five
   each, then pedicle size, four (atlas.md 2A Step 9a). Enter TPW as the within-patient step or as TPW / EPWu
   (measures.md 9.2(c)); measure it by measures.md 9.2(b), the 3D distance between the tips in frame F, store the x
   extent of atlas.md 2A Step 9b beside it, and register it in measures.MEASURERS (schwingcheck/measures.py). On
   lumbar fields build pedicle size beside transverse_width: pedicle_w carries the two strongest lumbar steps (L3/L4
   +2.45, L4/L5 +1.95; atlas.md 2A Step 9a), and its means sit a median 0.71 of his SDs from his means across 14
   papers (paper-tables results, same section); fix its section first, since an isthmus minimum reads nearer Hou
   than Panjabi, 12.9 against 18.6 mm at L5 (atlas.md 2A Step 9b). Since neither series reproduces the SPL step at
   T12/L1, widen spinous_length's spread at L1 in the table the rule reads, or check it on CT before trusting it, and
   run the build-up study both ways (measures.md 9.1). Hold every C7/T1 and T12/L1 step as an upper bound until a
   single series spanning the junction confirms it (atlas.md, "How to read this part"; measures.md 12).

8. **The two end-plate inclinations repeat the cervical row; the owner keeps them as printed.** The owner chose on
   2026-10-29 09:01 UTC to keep all 32 measures as printed, so nothing is rerun on 30 and every study states the
   reprint (bordercall TODO.md step b, pull request 31); the paper-tables comparison scores them as printed too. The
   case below for dropping them is what was weighed. Panjabi's lumbar Table 2 prints at L1 to L5 the same 20 numbers
   for endplate_incl and endplate_lower_incl, means and SEMs, as his cervical Table 2 at C3 to C7. That one set was
   printed twice is near certain; that the cervical is the original is probable, not proven; three second readers
   told to refute the note did not refute its main conclusion ([the end-plate
   note](../../panjabi-endplate-inclination.md), status and section 1; panjabi1991c p. 863; panjabi1992 p. 301).
   Kept, the row makes a lower plate tilted like tan2004's L5 mean of 10.5 deg 2.0 nats more like L1 than L5; marked
   missing at L1 to L5, it favours every body placed there by at least 2 nats per measure, at the thoracolumbar
   border (Inference in that note, section 3). What was recommended: one exclusion list that measures.pool,
   measures.left_out and measures.select all read, with the tests and the README moved from 32 measures to 30 and the
   build-up study rerun in the same pull request. The drop costs roughly a quarter to a half point named exactly at
   one body and under a point at 0.99 at three, but about 1.5 points named exactly and 4 at 0.99 in the lateral view,
   whose 10 measures become 8 (Inference in that note, section 3, on 300 of the study's columns); after it the code
   reproduces none of records/curve-2026-10-28's numbers outside the seven, and bordercall pull request 20, the chain
   of levels, is built on the pool of 32 (that note, section 3). Later, a whole C3 to L5 series from tan2004, with
   Tan 2002 read first, or a table from CTs read by the same measurer (that note, section 3; measures.md 3.5, 11.8).

9. **Add the anterior body height: its ratio to the posterior is the strongest L5 body marker in the series means.**
   In every series only L5 is 10% or more taller in front, about 1.10 to 1.18, against 0.99 to 1.05 at L4 and 0.85 to
   1.01 at every other level measured; the ratio is free of magnification and of size, and the generator holds no
   anterior height (Inference in measures.md 3.3 and atlas.md 2A Step 9a, ratios of the means of tan2004 pp. 140-141,
   busscher2010 p. 1107, frontphys2026 p. 5 and moncadahabib2025 p. 4). These are ratios of series means: no paper
   prints the per-person spread of VBHa/VBHp, and L4 can come near L5's low end (atlas.md 2A Step 9a), so how well
   the ratio parts L4 from L5 in one person is not known. What to do: measure anterior, middle and posterior heights
   (measures.md 3.3, 11.9). None of Panjabi's four papers tabulates an anterior height (measures.md 3.3), and
   measures.select refuses a measure with no table row at a level asked for (schwingcheck/README.md, "The measures"),
   so a measurer alone changes no naming: give the rule a row from a series that covers C3 to L5, such as tan2004
   (pp. 140-141), or from CTs read by the same measurer, and enter it as the ratio, whose SD is then a stated
   assumption to run as a sensitivity. At L5/S1 name a level only on two distinct cues among pedicle shape, wedge,
   IPD step, facet orientation and the disc below, since each fails alone in a known condition, the wedge in a
   compression fracture (anomalies.md 2.15, 4.5 rule 5; atlas.md 2A Step 8).

10. **Load size on stature less, and shift sex per family.** The twelve stature elasticities in the set, eight
    from griffith2016's correlations (1,080 living Hong Kong Chinese on CT: canal depth, canal width, canal area
    and body area, each by sex; slopes attenuated by error in stature) and four from yu2015 (503 dry skeletons,
    pedicle height and width), all lie below isometric, mean 0.53; none is for the end plates, body heights,
    processes or facets (error.md 2.3). The canal's run 0.34 to 0.75, and several series find canal depth equal
    between the sexes, or deeper in women, while the body differs (error.md 2.3, 3.4). One sex shift cannot fit
    body, canal width and canal depth together (error.md 2.1, 3.5). What to do: beta_height ~ N(0.55, 0.25^2) in
    place of N(1, 0.5^2); a smaller size loading for the canal; and male-minus-female shifts in log mean of +0.06
    for body lengths, +0.04 for canal width, about 0 for canal depth, +0.09 to +0.19 for pedicle width, +0.04 to
    +0.06 for pedicle height and 0 for angles, each centred on Panjabi's 8:4 mix, a man at +delta / 3 and a woman
    at -2 delta / 3 (error.md 3.4, 3.5). Unconditioned, a woman's L4 pedicle is as wide as a man's L3 to L4, so her
    vertebra tends to be named a level too cranial (olsewski1990 p. 544, p. 545; the naming bias is the note's
    Inference, atlas.md 2A Step 10). Changes: beta_height, beta_height_sd and sex_size in schwingcheck/covariates.py;
    a size power of 0.3 to 0.75 in place of 1 for canal_w and canal_ap, which needs a per-measure override, since
    schwingcheck/measures.py takes each measure's size_power from its kind (SIZE_POWER); and a per-family sex
    shift in the rule's mean and the generator together.

11. **On films, divide by the magnification or let it act as size, and prefer ratios.** Only eisenstein1977
    measured a film factor: 1.14 on the AP and 1.23 on the lateral at 110 cm, from 55 vertebrae of 11 dry
    skeletons; hinck1966, amonookuofi1982, ahn2001 and chaudhary2015 print uncorrected film values
    (eisenstein1977 pp. 174-175; error.md 1.4). Known film offsets are large: AP films of disarticulated cadaver
    spines read the L5 pedicle 3.5 mm narrow, and thoracic contact films read the posterior disc about 37% short
    (olsewski1990 p. 544; kunkel2011 p. 380, Table 1 p. 378). What to do: where M is known only to lie in 1.07 to
    1.23, shift the prior mean of log size by about +0.14 and widen its SD to 0.081 (Inference in error.md 3.3: log
    1.07 = 0.068 to log 1.23 = 0.207; 0.139 / sqrt(12) = 0.040; sqrt(0.07^2 + 0.040^2) = 0.081), for a film at
    100 to 110 cm only; give the AP and the lateral of one patient separate factors, 1.14 and 1.23 at 110 cm
    (eisenstein1977 p. 175; error.md 3.3); give a film reading 1.0 mm of random error and a superimposed structure
    at least 1.5 mm; put the offsets in the mean; prefer ratios, TPW / EPWu, pedicle width / height, VBHa / VBHp
    and canal / body; and never take an IPD, a pedicle width, a transverse angle or a pedicle depth from a lateral
    view (atlas.md 2B Steps 1 to 4; error.md 3.3). Changes: the size prior of a film field, in
    schwingcheck/covariates.py.

12. **On fluoroscopy, carry the name from CT: the set measured nothing there.** No paper measures on fluoroscopy
    or gives a C-arm's geometry, magnification or distortion (atlas.md 2B Step 5; error.md 4). duman2026 advises
    tracing the whole rib cage on a preoperative CT, because counts disagree on intraoperative fluoroscopy when the
    twelfth rib is rudimentary (duman2026 pp. 12-13). What to do: treat a frame as a film of unknown
    magnification, whose factor the set does not bound, since every film factor holds only for its own geometry
    (anomalies.md 4.5 rule 6), so set the C-arm's log-size prior as a stated modelling choice, or work in ratios
    alone; never name a thoracolumbar or lumbosacral level from an AP frame alone; carry the name from a
    preoperative CT by a landmark both show (atlas.md 2B Steps 5 and 7); on an en-face pedicle view read the
    ellipse's tilt, within about 8 deg of vertical at L1 to L3, about 30 deg at L4 and 50 to 55 deg at L5, on
    coaxial films of 10 dry-bone specimens of unstated origin, sex and age (robertson2000 p. 711, Table 1). Do not
    lean on L4's tilt alone, whose SD is 17 to 21 deg (atlas.md 2B Step 5); Inference: a single L4 can then look
    upright like L3 or oblique like L5. Changes: the size prior of a frame field, in schwingcheck/covariates.py.

13. **Check the chain of instances, and give missing, split and merged instances transitions of their own, apart
    from anatomy.** Before decoding, check that facing end plates and facets match across each disc and joint
    (panjabi1991t p. 890, Table 3; panjabi1993f p. 1306); join a detached arch to its body, since spondylolysis was
    found in 10/443 dry skeletons, nine bilateral at L5 (eisenstein1977 p. 177); read an instance about twice the
    usual height with an end-plate remnant as a block candidate (Inference in atlas.md 2A Step 3); and never call
    the top instance of a low-back CT L1, which routine low-back CT usually left out (olsewski1990 p. 546; atlas.md
    2A Steps 1 and 3). The end-plate match confirms that two instances face one disc; it cannot find a skipped
    level (atlas.md 2A Step 3). On lateral cervical films of healthy working men aged 20 to 38, C1 was hidden on all
    141, C2 unclear on 11/141 and C7 hidden on 15/141, lower bounds since the films were chosen for defined
    vertebrae (gilad1985 p. 117; Inference in anomalies.md 3.4: 141 - 130 and 141 - 126 from the n of Table 1, p.
    118); on AP films the IPD of C1 and C2 could not be measured (hinck1966 p. 142). No paper gives a rate of
    SPINEPS instances split or merged, of bodies lost from a CT field of view, or of visibility on fluoroscopy
    (anomalies.md 3.5). What to do: keep the missing-body transition apart from the count-changing variants, set it
    from these rates on films, and treat it as a modelling choice on CT masks until those rates are measured
    (anomalies.md 3.1, 3.4); give the chain of levels split and merged transitions beside the missed body. Changes:
    the chain of levels (bordercall pull request 20; bordercall's TODO.md, item P step e), whose plan names a missed
    body, an L6 and a T13 and no split or merged instance.

14. **Look for the red flags before scoring, and drop the cues they distort.** In 32 US adults with Marfan syndrome
    on uncorrected AP films, against Hinck's adults as historical controls, the IPD is wider by 4.5 mm at L1 to 9.9
    mm at L5, so a Marfan L1 of 29.5 mm reads like a normal L5 of 29.7 (Inference: differences of printed means,
    ahn2001 p. 68; atlas.md 2A Step 10); achondroplasia, osteopetrosis and trisomy 21 stop or reverse the caudal
    widening, the last reported and not measured (hinck1966 pp. 152-153; amonookuofi1982 p. 232); a degenerative slip
    at L4-L5 lifts L4's superior interfacet width to near a control L5 (masharawi2021 p. 6); L5-S1 was grade 2 or 3
    in 22 of 34 cadaver spines over 60 (Inference: 11 grade 2 + 11 grade 3, the note's sum from Table 4; twomey1985
    p. 498); and the L5 pedicle pointed caudad in 12 of 83 elderly cadaver pedicles against 2 of 94 pedicles of young
    living adults on films (olsewski1990 pp. 544-546). What to do: work through atlas.md 2A Step 10: drop absolute
    IPD in a widened canal and raise the transitional prior to 5/32, use the inferior interfacet width in a slip,
    never call a thin last disc transitional without a body or rib sign, and give the L5 pedicle angle a two-part
    mixture with a caudad weight of about 0.15 in elderly cadavers measured directly and 0.02 in young living adults
    on lateral films (Inference: 12/83 = 0.145, 2/94 = 0.021; age and method are confounded; anomalies.md 2.12 to
    2.15, 3.3; atlas.md 2A Steps 8 and 10). Changes: the L5 row of pedicle_incl_trans, Panjabi's name for the
    clinical sagittal angle (measures.md 7.4), as a two-part mixture in rule.py and the generator together.

15. **Answer with a distribution, and abstain when neither anchor nor chain holds.** Every rule for naming a
    transitional spine is Inference, and no paper measured a segmentation mask (atlas.md, Part 2 opening; measures.md
    12). What to do: report every competing name with its probability, and say that the probabilities are
    calibrated only on fields drawn from Panjabi's table (point 5); answer with a distribution whenever the two
    counts disagree, only one anchor is in view, the lumbosacral segment has fewer than two agreeing cues, the
    twelfth rib is short or absent with an unclear facet switch, or a red flag removes the measures that carry the
    nearest junction; give no absolute name, and say why, when the chain of instances is broken beyond repair or no
    anchor is in view, only the order of the run; and report the population behind each prior: South African dry
    bone for the lumbosacral rates, Turkish CT for the ribs, Panjabi's twelve spines for most size norms (atlas.md
    2A Steps 6 and 11, 2B Steps 6 and 7). Changes: what the chain of levels (bordercall pull request 20;
    bordercall's TODO.md, item P step e) reports for each field.

## The 43 papers

One row per note, ordered by the year the note's title gives, then by author; where a note's id differs from its
first author and year, the id is shown. The cells paraphrase each note's record (notes/<id>.json) and were checked
against the note. Every Panjabi row is one series: 12 fresh autopsy spines, C2 to L5 with no sacrum, cleaned to dry
bone (panjabi1991t p. 888, p. 890). Inference: the last column names the parts that cite the paper most often per 10
KB of their text, every part with at least half the top rate and at most three; it counts citations, it does not
weigh them.

| Paper | What it measured | Material and population, n | Modality | Levels | Parts that lean on it most |
|---|---|---|---|---|---|
| [Hinck 1966](../notes/hinck1966.md) | interpediculate distance (IPD) with SDs and 90% ranges; AP spine against PA chest | living white hospital patients, Portland, Oregon: 474 AP films, 121 adults and 353 children aged 3-18; counts by sex not given | AP radiograph at 101.6 cm, uncorrected | C3-L5 | atlas, error, anomalies |
| [Eisenstein 1977](../notes/eisenstein1977.md) | canal sagittal and interpedicular diameters, body diameters; survey of lumbosacral variants, trefoil canal, spondylolysis; film magnification | dry bone: 443 adult skeletons (113 Caucasoid, 162 Zulu, 168 Sotho), Raymond Dart Collection, 2,166 lumbar vertebrae; films of 55 vertebrae of 11 skeletons | vernier caliper; AP and lateral films at 110 cm | L1-L5; lumbosacral junction surveyed | anomaly-priors, anomalies |
| [Amonoo-Kuofi 1982](../notes/amonookuofi1982.md) | IPD and body transverse diameter; canal-to-body ratio | living Nigerian adults: 290 AP films (150 men, 140 women) aged 20-45, casualty patients with no bony injury | AP radiograph at 100 cm, uncorrected | L1-L5 | error, atlas, measures |
| [Amonoo-Kuofi 1985](../notes/amonookuofi1985.md) | canal mid-sagittal diameter, body depth; canal-to-body and notch-to-body ratios | dry bone: lumbar sets of 122 Nigerian adults (79 men, 43 women) aged 23-60, Ibadan | vernier caliper | L1-L5 | error, measures |
| [Gilad 1985](../notes/gilad1985.md) | body heights and depths, spinous reach (e, f), process angle, overall length on lateral films | living healthy working men aged 20-38: 141 cervical and 157 lumbar lateral films (Inference in the note: Israel) | lateral radiograph corrected to the midsagittal plane | C2-C7, L1-L5 | anomaly-priors, anomalies, atlas |
| [Twomey 1985](../notes/twomey1985.md) | disc diameters, anterior, middle and posterior disc heights, convexity, gross grade, by age | cadaver: 204 post-mortem lumbar blocks, infants to over 60 (89 male, 78 female, 37 pooled); grades on 140 | calipers on dissected and sectioned blocks | discs L1-2 to L5-S1 | error |
| [Zindrick 1987](../notes/zindrick1987.md) | pedicle isthmus widths, transverse and sagittal angles, depth to the anterior cortex | cadaver specimens and clinical CTs, number of people not stated; 2,905 measurements (2,005 specimen films, 900 CT) | axial and lateral films of disarticulated vertebrae; axial CT | T1-L5 | measures, atlas, error |
| [Krag 1988](../notes/krag1988.md) | pedicle diameter and axis angle, chord lengths, body depth for screws | living: 41 patients (27 men, 14 women) aged 18-75, 91 vertebrae, 182 pedicles; 8 cadaver vertebrae as a check | axial CT, 4 mm, measured by hand on prints | T9-L5 | measures, error |
| [Olsewski 1990](../notes/olsewski1990.md) | pedicle width, height, transverse and sagittal angles, depth; film and CT against direct | cadaver: 49 embalmed spines (24 men, 25 women, aged 60-98), 21 of them filmed; living: 51 patients with low-back problems (23 men, 28 women, aged 20-50) | caliper under a microscope; films of disarticulated spines; films and CT in the living | L1-L5 | error, anomalies, atlas |
| [Panjabi 1991, cervical](../notes/panjabi1991c.md) | end plates, posterior body height, canal, pedicles, processes, uncovertebral joints (the generator's cervical rows) | cadaver dry bone: 12 fresh autopsy spines (8 men, 4 women, mean 46.3 y), 72 vertebrae | 3D digitiser | C2-C7 | atlas, measures |
| [Panjabi 1991, thoracic](../notes/panjabi1991t.md) | the same families plus costovertebral and costotransverse facets and pars (the thoracic rows) | cadaver dry bone: the same 12 spines, 144 vertebrae | 3D digitiser | T1-T12 | measures, atlas |
| [Panjabi 1992, lumbar](../notes/panjabi1992.md) | the same families (the lumbar rows) | cadaver dry bone: the same 12 spines, 60 vertebrae (the same donors by the note's Inference) | 3D digitiser | L1-L5 | measures, atlas |
| [Hou 1993](../notes/hou1993.md) | pedicle width, height, length and inclination; pedicle centre against transverse process and facet | dry bone: 40 Chinese T9-L5 columns (25 male, 15 female), Xian; inclination in 10 more | vernier caliper | T9-L5 | atlas, error, measures |
| [Panjabi 1993, facets](../notes/panjabi1993f.md) | facet width, height and area, interfacet widths and height, facet angles | cadaver dry bone: the same 12 spines, 276 vertebrae | 3D digitiser | C2-L5 | atlas, measures |
| [Robertson 2000](../notes/robertson2000.md) | coaxial pedicle height, width, ellipse tilt and isthmus; film against wired cortex; S1 pedicle form | dry bone: 10 lumbosacral specimens, 100 lumbar and 20 S1 pedicles; origin, sex and age not stated | radiographs of dry bone with wire on the cortex | L1-L5; S1 described | error, measures, atlas |
| [Ahn 2001](../notes/ahn2001.md) | IPD and cut-offs in Marfan syndrome; transitional vertebrae counted | living: 32 US adults with Marfan syndrome (18 women, 14 men); Hinck's adults as historical controls | AP and lateral radiographs at about 101 cm, uncorrected | L1-L5 | anomalies, atlas |
| [Mitra 2002](../notes/mitra2002.md) | pedicle diameters, angles, chord, cortical thickness, entry point; three methods compared | cadaver: 20 Indian cadavers (18 men, 2 women), Nagpur | caliper and goniometer; lateral films at 100 cm; axial CT | L1-L5 | error, measures |
| [Tan 2004](../notes/tan2004.md) | Panjabi's measures on a second series: end plates, body heights, canal, pedicles, processes, angles | cadaver dry bone: 10 Chinese Singaporean cadavers, mean 65.7 y, sex not reported, 220 vertebrae | 3D digitiser | C3-L5 | measures |
| [Lien 2007](../notes/lien2007.md) | pedicle width, height, safe zone, transverse and sagittal angles; root and dura distances | dry bone: 15 T1-L5 sets from an anatomy department in Taipei (8 male, 7 female; ethnicity not stated); cadaver: 6 Taiwanese (3 men, 3 women) | caliper and goniometer; dissection | T1-L5 dry; T11-L5 cadaver | measures, atlas |
| [van der Houwen 2009](../notes/vanderhouwen2009.md) | end-plate concavity depth, rim diameters, disc wedge angle and height | living: 77 Dutch patients (46 men, 31 women, aged 21-86) with spinal CT, about 25 end plates per position; pig vertebrae for verification | CT, 0.75 mm | T12 inferior to S1 superior | error, measures |
| [Busscher 2010](../notes/busscher2010.md) | 16 dimensions per vertebra (body, end plates, canal, pedicles, processes, discs), human against pig | cadaver: 6 fresh-frozen male spines from Groningen, the Netherlands (mean 72 y, 182 cm; ethnicity not stated), 132 vertebrae; 6 pigs | CT of specimens, 1 mm, three observers | C3-L5 | measures, error |
| [Chen 2011](../notes/chen2011.md) | end-plate concave angles, concavity location, end-plate diameters | living: 83 patients aged 21-65 with thoracic or abdominal CT (Inference in the note: 43 men, 40 women); cadaver: 10 T10-L3 spines | CT, 0.625 mm reformats | T10 inferior to L3 superior | error |
| [Kunkel 2011](../notes/kunkel2011.md) | anterior, middle and posterior disc and body heights; ratio indices; prediction equations | cadaver: 72 thoracic motion segments of 30 donors (15 women, 15 men, mean 57.4 y), country not stated (Inference: authors' institution, Ulm) | lateral contact films and sagittal sections of the same segments | bodies C7-T12; discs C7-T1 to T11-T12 | error, atlas |
| [Makino 2012](../notes/makino2012.md) | transverse and sagittal pedicle widths, minimum diameter, cephalocaudal inclination | living: 50 patients (Inference in the note: Japanese, from the authors' department in Osaka; 23 men, 27 women, aged 52-85) with stenosis or degenerative spondylolisthesis | multiplanar CT, 1.25 mm | L1-L5 | measures, anomalies, atlas |
| [Chaudhary 2015](../notes/chaudhary2015.md) | IPD | living: 300 North Indian adults (150 men, 150 women, aged 25-40), films reported normal | AP radiograph, distance not stated, uncorrected | L1-L5 | error, atlas |
| [Yu 2015](../notes/yu2015.md) | pedicle height and width; narrow pedicles; regression on sex, stature, weight, age and race | dry bone: 503 Hamann-Todd skeletons (404 male, 99 female; 281 Caucasian, 222 African American; aged 17-93) | digital caliper | L1-L5 | error |
| [Griffith 2016](../notes/griffith2016.md) | canal area, depth and width; body area; their ratio; percentiles by sex | living: 1,080 Hong Kong Chinese adults (540 men, 540 women, aged 21-80) with abdominopelvic CT | CT, 0.6 mm, semi-automated, planes set to each vertebra | L1-L5 at mid-pedicle | error |
| [Tang 2016](../notes/tang2016.md) | disc and end-plate cross-sectional areas and diameters; a compilation of earlier series | living: 109 Utah adults (55 women, 54 men, aged 20-40) with lumbar MRI; 318 discs and 590 end plates kept | MRI, 1.5 T | discs L3/L4 to L5/S1 and their end plates | error |
| [Pierro 2017](../notes/italianmri.md) (id italianmri) | canal, body and dural sac sagittal diameters; dural sac ratios | living: 604 Caucasian adults of central and southern Italy (302 men, 302 women, aged 20-45); transitional spines excluded | sagittal MRI, 1.5 T | L1-S1 | anomalies, error |
| [Ahmed 2019](../notes/ahmed2019.md) | canal mid-sagittal diameter and IPD | living: 80 Indian patients (36 men, 44 women, aged 20-70) with low back pain | MRI, 1.5 T | L1-L5 | error, measures, atlas |
| [Bach 2019](../notes/bach2019.md) | anterior, middle and posterior disc heights and foraminal height, by sex and decade | living: 240 US patients (131 women, 109 men, aged 10-80) with abdominal CT | CT made into 3D models | discs T12/L1 to L5/S1 | error |
| [Yadav 2020](../notes/yadav2020.md) | canal depth and width, lateral recess, foramen, interfacet distance, body widths and depths, disc height | living: 302 North Indian adults (174 men, 128 women, aged 20-40) with CT for non-spinal complaints | CT, 1 mm | T12-S1 | measures, error |
| [Abbas 2021](../notes/abbas2021.md) | body length, width and heights; canal depth, width and area; laminar angles; stenosis against controls | living Israeli patients aged 40 or over: 165 with degenerative stenosis and 180 controls | CT, 0.9-3 mm | L1-L5 | error, measures |
| [Abu-Leil 2021](../notes/masharawi2021.md) (id masharawi2021) | canal, foramen, pedicle and facet dimensions, facet angles, arthrosis grade; spondylolisthesis against controls | living: 100 Israeli patients aged 50-80, 50 with L4-L5 degenerative spondylolisthesis and 50 controls (25 men and 25 women in each) | CT | L1-L5; foramina to L5-S1 | measures, error |
| [Alonge 2021](../notes/alonge2021.md) | canal depth and width, body depth, Torg ratio, canal shape | living: 120 Nigerian adults (66 women, 54 men, aged 18-65) with abdominal CT | CT | L1-L5 | anomalies, measures, error |
| [Irie 2021](../notes/otsuki2021.md) (id otsuki2021) | pedicle isthmus diameters, wall thickness, bone area fraction | cadaver: 6 fresh-frozen US lumbar spines (3 men, 3 women, aged 50-67), 60 pedicles | micro-CT, 34.4 micrometre voxels | L1-L5 | error, measures |
| [Cizmic 2023](../notes/cizmic2023.md) | canal mid-sagittal diameter and IPD | living: 200 Bosnian patients with lumbar pain (100 men, 100 women) | CT, 2 mm | L1-L5 | error, atlas, measures |
| [Bonczar 2024](../notes/bonczar2024.md) | 27 measures per level pooled: end plates, heights, canal, pedicles, processes | meta-analysis: 1,481 individuals of 18 studies (CT 966, film 273, MRI 50, caliper 170, digitiser 22), living, cadaver and dry bone pooled | pooled from all five methods | L1-L5 | error, measures, atlas |
| [Arockiaraj 2025](../notes/arockiaraj2025.md) | pedicle width, height, length, chord and axis angle | living: 300 Saudi adults (150 men, 150 women, aged 18-60), 1,500 vertebrae | CT, 2.5 mm | L1-L5 | measures, error |
| [Moncada-Habib 2025](../notes/moncadahabib2025.md) | pedicle width, height, length, transverse angle; body length, width and heights | living: 37 Mexican patients aged 26-88 (Inference in the note: 20 men, 17 women), 185 vertebrae | CT, 1 mm | L1-L5 | error, measures, atlas |
| [Shin 2025](../notes/shin2024.md) (id shin2024) | disc space heights; foraminal widths, height and area | living: 700 US adults (350 men, 350 women, aged 18-35), one institution (Inference in the note: Loma Linda) | CT, 64-slice | L1-L2 to L5-S1 | error, measures |
| [Duman 2026](../notes/duman2026.md) | body heights; pedicle width, height, length and angle; 12th-rib, lumbar-rib and cervical-rib anomalies | living: 517 Turkish adults (277 men, 240 women) with chest or abdominal CT | CT, 0.625 mm | T11-L2; ribs over the scan | anomaly-priors, anomalies, error |
| [Li 2026](../notes/frontphys2026.md) (id frontphys2026) | body heights, end-plate widths, cortical thickness, attenuation (HU) by region | living: 100 Chinese adults aged 20-70 (text 50 men and 50 women; table 46 and 54) with health-check CT | CT, 1 mm | L1-L5 bodies | error, measures, atlas |

## The parts

[anomalies.md](anomalies.md), 96 KB in 1,388 lines: anomalies, numbering and the junctions. Section 1 tables every
prevalence the set reports, with how each paper numbered its levels (1.6); section 2 says how to recognise each
variant on a mask and on AP and lateral films and what it does to the measures and to the count (2.1 to 2.15);
section 3 turns prevalence into the decoder's transitions, modifiers and observation priors (3.1 to 3.4); section 4
gives every criterion the set offers at C2/C3, C7/T1, T12/L1 and L5/S1 and the decoder's rules at the junctions (4.1
to 4.5). Read it to build or check the sequence decoder.

[anomaly-priors.md](anomaly-priors.md), 10 KB in 58 lines: the priors as a second reader checked them against the
rendered pages, each count with its material, population, paper, page and Wilson interval, then how to use them and
what the set does not give (anomaly-priors.md, source line). It is the table to set the decoder's transitions from;
anomalies.md 1.1, 1.2 and 3 agree with it (anomalies.md, opening).

[measures.md](measures.md), 239 KB in 1,971 lines: every measure as a recipe for a CT instance mask and for a
radiograph. Sections 1 and 2 give the sources, Panjabi's frame, recipe F, what the SPINEPS labels give, the
operations and the projection effects; sections 3 to 10 take the body, the end-plate concavity, the discs, the canal,
the pedicles, the facets, the processes and the ribs, each with its definitions compared across papers, the biases a
mask value carries, a mask recipe, a film recipe and its course across levels; section 11 gives a feature-extraction
line per generator key, the corrections the generator's own text needs (11.8) and the features the set supports that
the generator lacks (11.9); section 12 the gaps. Read it to write or check a measurer.

[error.md](error.md), 91 KB in 760 lines: measurement error, modality agreement and covariates. Section 0 states what
schwingcheck assumes now and what that assumption is worth; section 1 gathers every reliability figure in the set,
modality against direct measurement, magnification, resolution, partial volume and definition offsets; section 2 the
covariates, sex, age, stature, population and stenosis; section 3 the recommended error, size, sex, population and
age terms, ending in the changes to schwingcheck in order (3.8); section 4 what the set cannot tell. Read it to set
the error and size terms of the generator and the rule.

[atlas.md](atlas.md), 147 KB in 1,758 lines: Part 1 is an atlas level by level from C2 to S1, with step/SD tables
from Panjabi's means and the sections on L6, sacralisation and T13; Part 2 is the playbook for the autonomous
anatomist, eleven steps for naming every instance on a 3D CT (2A), from checking the volume to deciding when to
answer with uncertainty, and seven for AP and lateral films and fluoroscopy frames (2B). Read it to see the order of
work the agent follows, and why.

The parts stay separate. Together they are about 583 KB in the unit of the sizes above, 1,024 bytes to the KB
(Inference: 98,405 + 10,267 + 244,880 + 93,033 + 150,767 = 597,352 bytes; 597,352 / 1,024 = 583), too long to read in
one sitting or to render as one page, and each serves a different reader: the decoder (anomalies.md and
anomaly-priors.md), the measurer (measures.md), the error model (error.md) and the agent's playbook (atlas.md). Each
part cites the notes directly and points to another part by section where they meet (measures.md 10.3; atlas.md 2A
Step 8). This file is the way in.

Two records outside this folder carry the reread on: [the end-plate note](../../panjabi-endplate-inclination.md),
the verdict on Panjabi's lumbar end-plate inclinations behind point 8, and [the paper-tables
results](../../paper-tables/results/README.md), the evaluation of Panjabi's rule on every paper's tables behind
points 5 and 7.

## What the set does not give

The gaps that matter for naming; anomalies.md 3.5, measures.md 12, error.md 4 and anomaly-priors.md list them in
full with their sources.

- No count of T13, of 11 or 13 thoracic vertebrae or of 11 or 13 rib pairs, and no bound for T13; duman2026
  promised the laterality of its rib anomalies and never reported it, so bilateral absence of the twelfth rib has
  only a ceiling (duman2026 p. 5, p. 10; anomalies.md 3.5).
- No prevalence of a lumbosacral variant in any living general population, no definition of any lumbosacral
  category, no Castellvi or other grade, no side of a transitional joint, and no word on whether a sacralised L5
  lost its free segment (eisenstein1977 p. 177; anomalies.md 3.5).
- No rule, in any paper, for numbering a spine with a transitional segment, no measure reported separately for
  one, and no measured effect of any variant on any measure beyond smaller facets beside a sacro-transverse joint
  and the syndromic IPD changes (eisenstein1977 p. 177; ahn2001 p. 68; hinck1966 pp. 152-153; atlas.md, Part 2
  opening; anomalies.md 3.5).
- No joint rate of rib and lumbosacral variants in one person, so the decoder cannot learn from the set whether a
  lumbar rib and an L6 travel together (anomalies.md 3.5).
- No count of how often the thoracolumbar facet switch falls away from T12-L1; panjabi1993f gives only SEMs that
  widen to 8.2-9.5 deg there (p. 1303; anomalies.md 3.5).
- No count from total length: busscher2010 found human C3-L5 569.4 mm against 569.5 mm in a pig with four more
  vertebrae (p. 1107, p. 1113; anomalies.md 3.5).
- No rib facet measured on CT and no distribution of rib lengths, which the rib states of point 4 need
  (measures.md 12).
- No prevalence of block vertebrae or hemivertebrae, beyond one syndromic child, and none of occipitalisation
  (hinck1966 pp. 152-153; anomalies.md 3.5).
- No reliability of any anomaly call: Eisenstein's were by one inspector with no definitions, Duman's by one
  radiologist whose agreement figures cover the measures and not the calls (eisenstein1977 p. 177; duman2026 p. 6).
- No error of any automated segmentation mask against manual reading or bone, no rate of SPINEPS instances split or
  merged at the sacrum, and no rate of bodies lost from a CT field of view (error.md 1.1, 4; anomalies.md 3.5).
- No fluoroscopic measurement and no C-arm geometry, magnification or distortion (error.md 4; atlas.md 2B Step 5).
- No per-spine values in Panjabi's tables, so no covariance between measures and no coefficient of size, sex, age
  or stature from the generator's own source; no S1 or sacrum in his series (measures.md 12; panjabi1991t p. 888).
- No within-person correlation across levels or measures beyond griffith2016's four correlations of subject means,
  so the generator's rho of 0.5 (schwingcheck/columns.py, SYNTH) is a modelling choice to run as a sensitivity;
  hinck1966 says only that people differ mainly in the overall level of their profile (p. 146; error.md 2.3, 4).
- No statement in Panjabi's papers of where the canal and pedicle sections were taken, so every recipe assumes it
  (measures.md 12).
- No confirmation that Panjabi's cervical, thoracic and lumbar papers define each measure alike, which every step
  at C7/T1 and T12/L1 assumes (atlas.md, "What the set does not give"; measures.md 12), and most probably no lumbar
  end-plate inclination of his at all (the end-plate note, section 1).
- No CT error in millimetres for most of the 32 pooled measures: the spinous and transverse lengths, the facet sizes
  and angles, the interfacet distances and the end-plate areas have only pooled ICCs or a phantom bound (error.md 4).
- No separation of population from definition, age and instrument in any comparison between series (error.md 3.6,
  4).
- Thin coverage outside the lumbar spine: 26 of the 43 papers measure nothing above L1, and 7 reach a cervical
  level, two of them in living people, on films (Inference: counted from the Levels column above; hinck1966,
  gilad1985); nothing measures the dens or the atlanto-axial joint (atlas.md, "What the set does not give").
- No living-patient thoracic film norm except hinck1966's AP IPD (atlas.md, "What the set does not give").
