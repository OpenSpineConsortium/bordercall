# Anomaly priors for the chain of levels, as checked

Source: the thread "Finish the clinical reread", 2026-10-29. A second reader checked every count of the draft's anomaly part (synthesis/anomalies.md, sections 1 and 3) against the rendered pages of the papers and recomputed every share and interval. This file is that reader's table: each prior with what it is made of, the population, the paper and page. Shares are percentages with Wilson 95% intervals. Where a count comes from arithmetic on a paper's figures rather than from print, the note says Inference.

These are the only rates the 43 papers give. None is from a living general population, and no count of T13 exists in the set (end of this file).

## The priors

| State | Count | Share % (95%) | Made of | Population | Source | Note |
| --- | ---: | --- | --- | --- | --- | --- |
| six_lumbar: L5 -> L6 (true L6 or lumbarised S1) | 11/443 | 2.48 (1.39-4.39) | skeletons; dry macerated bone; direct inspection, categories undefined; 2 true L6 + 9 lumbarised S1, assumed disjoint | South African adult skeletons, Raymond Dart Collection (113 Caucasoid, 162 Zulu, 168 Sotho), age 16-96 | eisenstein1977 p. 177 (PDF 5) | Sensitivity upper: adding the 16 persistent S1-S2 joints gives 27/443 = 6.09% (4.22-8.72), but only if a segmenter splits S1 off. |
| true L6 only | 2/443 | 0.45 (0.12-1.63) | skeletons, dry bone, inspection | same; both cases Sotho | eisenstein1977 p. 177 (PDF 5) | Sotho 2/168 = 1.19% (0.33-4.24); others 0/275 (upper 1.38). Fisher p = 0.14 (Inference), so no population effect is shown. |
| lumbarised S1 | 9/443 | 2.03 (1.07-3.82) | skeletons, dry bone, inspection, undefined | same, both races and sexes | eisenstein1977 p. 177 (PDF 5) |  |
| four_lumbar: L4 -> sacrum (sacralised L5) | 8/443 | 1.81 (0.92-3.52) | skeletons, dry bone, inspection; 'sacralisation' undefined, so whether a free L5 instance is lost is not stated (2,166 = 443x5-49 counts five lumbar per skeleton, p. 173) | same; 0/35 Caucasoid females | eisenstein1977 p. 177 (PDF 5); p. 173 (PDF 1) | Use as a ceiling (0 to 1.81%) for a count-changing four_lumbar state. 0/35 Caucasoid F: Wilson upper 9.89%, P(0 given 1.8%) = 0.53, so no evidence of a sex effect. |
| true transitional lumbosacral vertebra (count effect unknown) | 1/443 | 0.23 (0.04-1.27) | skeleton, dry bone, inspection, undefined | same; one Zulu | eisenstein1977 p. 177 (PDF 5) | Zulu 1/162 = 0.62% (0.11-3.41). |
| sacro-transverse joint at L5 (patent or ankylosed; count assumed unchanged) | 10/443 | 2.26 (1.23-4.10) | skeletons, dry bone, inspection; side and type not given; overlap with sacralisation unknown; smaller lumbosacral facets on that side in most | same | eisenstein1977 p. 177 (PDF 5) | An emission or shape modifier at L5, not a count transition. Not part of Eisenstein's 36. |
| persistent S1-S2 zygapophysial joints | 16/443 | 3.61 (2.24-5.79) | skeletons, dry bone, inspection | same | eisenstein1977 p. 177 (PDF 5) | The author calls it possibly the least form of lumbarisation. Matters to the decoder only if the segmenter splits S1. |
| any of Eisenstein's five transitional categories | 36/443 | 8.13 (5.93-11.05) | skeletons; plain sum 9+16+2+1+8 (overlap not removed or none present) | same | eisenstein1977 p. 180 (PDF 8) | Printed '8 per cent'. Excludes the sacro-transverse joints. |
| any count-changing lumbosacral state (L6 + lumbarised S1 + sacralised L5) | 19/443 | 4.29 (2.76-6.60) | skeletons; 9+2+8, assuming the categories are disjoint and all change the count (neither stated) | same | eisenstein1977 p. 177 | Defensible range 11/443 (2.48%) to 19/443. |
| Marfan: any lumbosacral transitional vertebra, type unknown | 5/32 | 15.63 (6.86-31.75) | patients; AP and lateral lumbosacral radiographs L1-S5; LSTV undefined; count-changing share unknown | 32 US living adult Marfan volunteers (DePaepe), 18 F 14 M; excludes prior back surgery, stenosis, scoliosis >20 deg | ahn2001 p. 68 (PDF 2), p. 70 (PDF 4) | Do not split by Eisenstein's mix. The excess over Eisenstein is 1.9x to 3.5x depending on the comparator (Fisher p 0.18 to 0.02). |
| lumbar_rib: rib-bearing vertebra below the twelfth rib-bearer (L1 with lumbar rib; T13 not separable) | 12/517 | 2.32 (1.33-4.01) | patients; CT axial/MPR/3D, one radiologist; bearing vertebra not named; no criterion against an unfused transverse process | 517 Turkish adults at one chest hospital, Izmir, CT 2021-2025, non-spinal indications | duman2026 Table 5 p. 10 (PDF 10); definitions p. 5 | Men 10/277 = 3.61% (1.97-6.52); women 2/240 = 0.83% (0.23-2.99); Fisher p = 0.042. Not an upper bound for T13. |
| t13: true thirteenth thoracic vertebra | none | no value | no count in the set | none | none (duman2026 pp. 3-5 give no counting rule; panjabi1991t, busscher2010 report none in 12 and 6 screened spines) | No value and no bound. The union of supernumerary ribs, 19/517 = 3.68% (2.37-5.67), is not a bound either. Any range used is a modelling choice. |
| no_rib_t12: 12th rib absent on at least one side | 22/517 | 4.26 (2.83-6.36) | patients; CT; laterality never reported; how T12 was named is not stated | Duman series | duman2026 Table 5 p. 10 | Upper bound for bilateral absence (11 rib pairs), the only case that shifts a rib-based count. Men 4/277 = 1.44% (0.56-3.65); women 18/240 = 7.50% (4.80-11.54). |
| hypoplastic 12th rib (<4 cm on CT) | 55/517 | 10.64 (8.27-13.59) | patients; CT; length method not stated | Duman series | duman2026 Table 5 p. 10; p. 5 | Men 25/277 = 9.03% (6.19-12.98); women 30/240 = 12.50% (8.90-17.28). Matters for 2D rib reading (foreshortening); does not change the count. |
| short or absent 12th rib, at least one side | 77/517 | 14.89 (12.08-18.22) | patients; 55+22, exact only if Table 5 files each patient once (contradicted by Fig. 4A-B, p. 9) | Duman series | duman2026 Table 5 p. 10; p. 8 | An upper bound if the rows overlap. |
| cervical rib (C7 may be read as T1 by ribs) | 7/517 | 1.35 (0.66-2.77) | patients; CT; the denominator may include scans not reaching C7; side not reported | Duman series | duman2026 Table 5 p. 10 | Men 1/277 = 0.36% (0.06-2.02); women 6/240 = 2.50% (1.15-5.35); Fisher p = 0.053, so the sex split is weak. |
| any rib anomaly | 96/517 | 18.57 (15.45-22.15) | individuals (text p. 8); the rows sum exactly | Duman series | duman2026 p. 8, Table 5 p. 10 | Men 40/277 = 14.44% (10.79-19.07); women 56/240 = 23.33% (18.43-29.08). |
| observation: C2 not clearly defined on a lateral cervical film | 11/141 | 7.80 (4.41-13.43) | films; derived from Table 1 n (130 of 141); the paper prints 'about 10%' | healthy working men aged 20-38, films pre-selected for defined vertebrae | gilad1985 p. 117 (PDF 3), Table 1 p. 118 | A lower bound for unselected films. |
| observation: C7 obscured by clavicle, humerus and ribs on a lateral cervical film | 15/141 | 10.64 (6.55-16.81) | films; derived from Table 1 n (126 of 141); the paper prints 'about 10%' | same | gilad1985 p. 117, Table 1 p. 118 |  |
| observation: C1 not identifiable on a lateral cervical film | 141/141 | 100.00 | films; 'covered superiorly by the skull in all' | same | gilad1985 p. 117 | C1 is outside schwingcheck's pool anyway. |
| measure availability (not a missing body): L5/S1 end-plates lacking oblique MRI slices | 23/109 | 21.10 (14.49-29.68) | subjects; acquisition protocol gap | 109 US adults aged 20-40, Utah archive | tang2016 p. 4117 | Not a missing-body rate. |

## How to use them

- six_lumbar: 11/443 (2.48%) is the point prior; 27/443 (6.09%) is a sensitivity upper only if the segmenter splits S1 off at a persistent S1-S2 joint.
- four_lumbar: 0 to 8/443 (0 to 1.81%) as a ceiling, since Eisenstein never defines sacralisation and his vertebra count (2,166 = 443 x 5 - 49, p. 173) still counts five lumbar in each sacralised skeleton.
- Any count-changing lumbosacral state: 11/443 to 19/443 (2.48% to 4.29%), the upper end assuming disjoint categories that all change the count.
- no_rib_t12: 22/517 (4.26%) is a ceiling for bilateral absence, the only case that shifts a rib count; laterality was never reported. Use a lower point prior or a sensitivity range of 0 to 4.26%.
- t13: no value and no bound in the set; any range is a modelling choice for the sensitivity study.
- Marfan: one state, LSTV of unknown type, 5/32 (15.6%); do not split it by Eisenstein's mix. Its excess over Eisenstein is 1.9 to 3.5 times depending on the comparator.
- The sacro-transverse joint (10/443) and the true transitional vertebra (1/443) change shape or emission at L5, not the count.

## What the set does not give

- Any count of T13, of 11 or 13 thoracic vertebrae, or of 11 or 13 rib pairs; and no bound for T13 (Duman gives no counting rule and files supernumerary ribs only as cervical or lumbar, p. 5).
- The laterality of any rib anomaly (Duman promised it, p. 5, and never reported it), so there is no rate of bilateral 12th-rib absence.
- A definition of any lumbosacral category (lumbarisation, sacralisation, true transitional, true L6) or of how they were told apart (eisenstein1977 p. 177); no Castellvi type; no side.
- Whether Eisenstein's sacralised L5 lost a free segment, and whether his categories and the sacro-transverse joints overlap.
- The type of Ahn's 5 Marfan LSTVs, and whether any changed the count.
- An LSTV prevalence in any living general population (italianmri and masharawi2021 excluded transitional vertebrae without counts).
- Any joint distribution of rib and lumbosacral variants within one person.
- A prevalence of block vertebrae, hemivertebrae (one syndromic child, hinck1966 pp. 152-153) or occipitalisation of C1.
- How often the thoracolumbar facet switch falls away from T12-L1 (only widened SEMs, panjabi1993f p. 1303).
- Reliability of any anomaly call: single inspector (Eisenstein), single radiologist with ICC on linear measures only (Duman p. 6).
- Rates of vertebrae lost from a CT field of view or by SPINEPS splitting or merging; observation rates on fluoroscopy.
- Any rib or lumbosacral rate outside South Africa and Turkey, except Ahn's US Marfan series; nothing by age.
- Re-checks against PubMed, Europe PMC, EBI or Crossref were not possible from this session's machine; every finding above rests on the notes and the local PDFs.

