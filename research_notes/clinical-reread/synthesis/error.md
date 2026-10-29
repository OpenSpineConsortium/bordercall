# Measurement error, modality agreement and covariates

Source: one part of the synthesis of the clinical re-read, written 2026-10-28 by a workflow subagent from the 43 notes in /home/user/bordercall/research_notes/clinical-reread/notes/ (each cited by its id) and from bordercall's schwingcheck/measures.py, schwingcheck/covariates.py and schwingcheck/README.md. Pages are the paper's printed pages as each note gives them. Two PDFs were opened to confirm the figures the size recommendation rests on: griffith2016 Table 1 (p. 674) and yu2015 Table 2 (p. 1641); both match their notes. Where any other note and its PDF (scratchpad/papers/<id>.pdf) could disagree, the PDF settles it.

How to read it:

- "(id p. N)" cites a note and the paper's page. "(id note)" marks a figure the note itself derived from the paper.
- "Inference:" marks arithmetic of mine, with its inputs and their sources.
- SEmeas is the standard error of measurement, SD x sqrt(1 - ICC), with SD the between-subject SD of the same paper. "SE" is the standard error of a mean. Panjabi prints mean +/- SEM of the 12 spines (panjabi1992 p. 300), so his between-person SD is sqrt(12) x SE = 3.46 x SE (panjabi1992 note), the conversion schwingcheck's loader makes (measures.py, sem x sqrt(n)).
- Every count says what it is made of: people, vertebrae, pedicles or readings, and whether the material is living patients, cadavers or dry bone.

## 0. The yardstick: what schwingcheck assumes now

The generator and the rule share one error per kind of measure (README "Each kind its own term"; measures.py):

- A length: 1 mm (LENGTH_ERROR_MM, the archive's noise_mm), described as a stated assumption.
- An area of mean A mm2: sqrt(pi A / 2) mm2, the error of a circle's area when the diameter is read 1 mm off on each axis. That is 19.6 mm2 for the canal's area and 31.1 mm2 for the upper end plate's.
- An angle: 3 deg (ANGLE_ERROR_DEG). That is the error in the direction of a line about 27 mm long whose two ends are each read 1 mm off. The README calls it a round figure, not a measured one.
- Size: log s = beta_height x log(height / 167.75) + eps, with eps ~ N(0, 0.07^2) and beta_height ~ N(1, 0.5^2). The prior is isometric, a starting belief and not a measurement. Its residual SD 0.07 is kept even once height is known, which "overstates it" (covariates.py).
- Hooks: sex_size, the weight effects and the age effects are all at 0 (covariates.py).
- The power of the size is 1 for a length, 2 for an area and 0 for an angle.
- The generator floors a size-scaled value at 0.5 (README).

What the error assumption is worth (README build-up study, three-body fields of 2,000 typical columns):

| Errors | Seven measures named exactly | All 32 named exactly |
|---|---|---|
| As assumed | 73.1% | 98.3% |
| Halved | 76.8% | 99.2% |
| Doubled | 63.0% | 95.3% |

Inference: doubling the errors costs 10.1 points with the seven (73.1 - 63.0) but 3.0 with all 32 (98.3 - 95.3). The error figures below matter most for the short measure lists that a radiograph or a partial CT will give.

In those arms the rule and the generator change their errors together, so the answers at 0.99 stay right by construction (README "Errors move the share named and not the promise"). A rule whose error is set too small is another matter: the archive's record, taking 3 mm of measurement error as 1 mm, was right at 0.99 only 82.6% of the time at three bodies (README, same paragraph). Inference: an error set too large costs a few points of share named; one set too small breaks the calibration. Where the set brackets an error, take the upper end.

## 1. Every reliability figure in the set

### 1.1 Which papers measured their own error

- Some observer, repeat or method-error figure: 16 of the 43 notes: abbas2021, arockiaraj2025, busscher2010, duman2026, frontphys2026, gilad1985, griffith2016, hinck1966, kunkel2011, masharawi2021, moncadahabib2025, shin2024, tang2016, twomey1985, vanderhouwen2009 and yu2015.
- An instrument or phantom check only: 5. These are panjabi1991c, panjabi1991t, panjabi1992 and panjabi1993f (a Plexiglas phantom) and tan2004 (a digitiser calibration).
- Nothing: 22. These are ahmed2019, ahn2001, alonge2021, amonookuofi1982, amonookuofi1985, bach2019, bonczar2024, chaudhary2015, chen2011, cizmic2023, eisenstein1977, hou1993, italianmri, krag1988, lien2007, makino2012, mitra2002, olsewski1990, otsuki2021, robertson2000, yadav2020 and zindrick1987.
- chen2011, krag1988, mitra2002 and olsewski1990 do compare modalities (1.3).
- bonczar2024 is a meta-analysis with double extraction and no error figure (bonczar2024 pp. 3-4).

No study in the set measured the error of an automated segmentation mask against a manual reading. The nearest is griffith2016's semi-automated tool, read against a second, manual reader (griffith2016 p. 676).

### 1.2 Observer and repeat studies, by measure family

| Family | Study, material, n | Design | Figure | Inference or note: absolute error |
|---|---|---|---|---|
| Body heights | busscher2010, CT of 6 male cadavers (Dutch, 55-84 y), three observers | intra and inter | VBHa/VBHc/VBHp intra 0.98/0.99/0.99 (VBHa 95% CI 0.56-1.00); inter 0.98/0.99/0.98 (busscher2010 Table 1 p. 1106) | none in mm; text calls the coefficients "Kappa", which they are not (busscher2010 p. 1107). No repeat reading by one observer is described, so what the Intra-CC column measures is not explained (busscher2010 note) |
| Body heights | duman2026, CT of living Turkish adults; one radiologist re-read 50 scans after 4 weeks | intra only | linear measures ICC 0.912-0.965 (duman2026 p. 6) | SEmeas 0.3-0.65 mm for heights (duman2026 note) |
| Body heights | kunkel2011, thoracic segments of body donors (15 women, 15 men, 37-80 y); 10 radiographs of 10 specimens, minutes apart | intra on film; inter on sections and film | VBH intra 1.7-5.1%; inter "CV" VBHA/VBHP 0.95-0.98 (kunkel2011 pp. 377, 380) | the "CV" behaves like a reliability coefficient, not a percentage (kunkel2011 note) |
| Body heights and widths | frontphys2026, CT of living Henan Chinese; 20 vertebrae, 2 weeks apart | intra only; each value the mean of 3 | ICC > 0.90 (frontphys2026 p. 3); no inter-observer study (frontphys2026 p. 8) | its SDs of 0.6-1.7 mm sit far below Panjabi's 2.6-4.9 mm (frontphys2026 Table 2 p. 5; note) |
| End-plate depth | busscher2010, as above | intra and inter | UEPD intra 0.97, inter 0.95; LEPD 0.99 and 0.98 (busscher2010 Table 1 p. 1106) | none in mm |
| End-plate width and depth (pig) | vanderhouwen2009, CT and caliper; 1 pig vertebra, 9 dimensions x 3 repeats | repeatability | SD 0.22 mm on CT against 0.18 mm by caliper (vanderhouwen2009 pp. 36, 38) | method floor, one observer |
| Disc and end-plate diameters | tang2016, MRI of 40 scans of living US adults 20-40 y; 2 observers x 2 rounds | intra and inter, ICC(3,1) | CSA intra 0.996/0.990, inter 0.971; FD 0.984/0.984, 0.953; APD 0.993/0.984, 0.970; MSD 0.914/0.906, 0.938 (tang2016 Table 3 p. 4119) | SEmeas between observers: APD 0.5 mm, FD 0.9 mm, MSD 0.8 mm, CSA 40 mm2 (tang2016 note) |
| Canal depth and width | busscher2010, as above | intra and inter | SCD intra 0.83, inter 0.86; SCW intra 0.90 (busscher2010 Table 1 p. 1106) | the canal depth is the least reliable of busscher's measures |
| Canal depth, width, CSA | griffith2016, CT of living Hong Kong Chinese; 20 subjects, 100 levels, 1 week apart | intra; computerised against a manual second reader | intra ICC by level 0.85, 0.87, 0.91, 0.85, 0.96 (L1-L5); computerised against manual 0.80, 0.89, 0.88, 0.83, 0.95 (griffith2016 p. 676) | SEmeas 0.4-1.2 mm for depth and width, 10-30 mm2 for canal CSA (griffith2016 note) |
| Canal width, interpedicular distance (IPD) on AP film | hinck1966, films of living white patients; 89 duplicate readings in 9 cases by one author | repeat reading | absolute difference: median 0.26 mm, mean 0.40, range 0-3.6; 10% zero, 50% < 0.26, 75% < 0.50, 90% < 1.0 mm (hinck1966 p. 142) | one reading SD about 0.27 mm with a heavy tail (hinck1966 note). Inference: for a normal difference of two readings, median abs = 0.954 x sigma, so sigma = 0.26 / 0.954 = 0.27 mm |
| Pedicle height and angle | busscher2010, as above | intra and inter | PedH 0.89 (CI 0.54-0.96), PedA 0.89; SPA inter 0.83 (busscher2010 Table 1 p. 1106) | lowest coefficients in that paper, with SCD |
| Pedicle diameters | duman2026, as above | intra | as above (duman2026 p. 6) | SEmeas 0.2-0.55 mm (duman2026 note) |
| Pedicle side difference | duman2026, 517 living patients | right minus left | mean TPD difference 0.04-0.09 mm (duman2026 Table 3 p. 8) | the within-patient SD of the side difference is about 1.3-1.9 mm, biology and error together (duman2026 note) |
| Pedicle width and height | yu2015, dry bone (Hamann-Todd, n = 503 per level); 21 random samples | caliper, intra and inter | intra CV 4.0% (1.7-6.2); inter CV 5.2% (1.5-16.8) (yu2015 p. 1640) | 0.6-0.8 mm for PH and 0.35-0.95 mm for PW (yu2015 note). The error CV is a third to four fifths of the biological CV of PH (yu2015 note) |
| Pedicle measures | arockiaraj2025, CT of 300 living Saudi adults; two radiologists, each value read three times | inter | "no interobserver bias" P > 0.05 only (arockiaraj2025 p. 314) | a Table 1 column headed Correlation holds -0.018 to 0.143, unexplained (arockiaraj2025 p. 315) |
| Pedicle and body | moncadahabib2025, CT of 37 living Mexican adults; two readers | tolerance rule | differences over 2 mm or 2 deg went to consensus; no ICC (moncadahabib2025 pp. 3, 7) | per-reading SD about 1 mm or 1 deg, half the tolerance (moncadahabib2025 note) |
| Disc heights | shin2024, CT of living US adults 18-35 (700 patients per level); four medical students | one overall ICC; intra or inter, model, raters and sample not stated | ICC .842 (shin2024 p. 5) | error SD 0.76/0.64/0.52 mm for anterior, middle and posterior DSH, SD x sqrt(1 - .842), larger if the ICC was pooled over measures and levels (shin2024 note) |
| Disc heights | kunkel2011, as above | inter and intra | inter "CV" 0.79-0.93 on sections, 0.49-0.82 on films (PDH 0.49); intra ADH 1.7-6.1%, PDH 17-26.1%; repeat radiographs about 15% less reproducible (kunkel2011 p. 380) | the posterior disc on film is the least reliable measure in the set |
| Disc heights | twomey1985, cadaver sections, 204 cadavers | caliper inter-trial | r = 0.97; calipers 0.05 mm (twomey1985 p. 496) | none in mm |
| Pedicle angle | duman2026, as above | intra | TPA ICC 0.898 (0.872-0.924) (duman2026 p. 6) | SEmeas 0.7-1.8 deg (duman2026 note) |
| End-plate angles on film | panjabi1991t, 10 lateral films | film against bone | mean 3.9 deg on film against 3.8 deg on bone; no agreement statistic (panjabi1991t pp. 889-890) | agreement of means only |
| Pooled, all measures | abbas2021, CT of 20 living Israeli individuals | intra: one tester twice, 3-5 days apart; inter: two testers within an hour | intra ICC 0.782-0.985; inter 0.721-0.980 (abbas2021 p. 2) | no SEmeas; the lowest-ICC measures are not named |
| Pooled, all measures | masharawi2021, CT of living Israeli adults 50-80; 10 CTs, 1 week apart | intra and inter | intra ICC(3,1) 0.85-1; inter 0.85-0.92 (masharawi2021 pp. 3-4) | facet arthrosis graded by agreement, no kappa |
| Pooled, film | gilad1985, lateral films of living men 20-38 y | method error | calipers under +/-0.5 mm, parallax at most +/-1.0 mm more; together up to 10% cervical, under 5% lumbar (gilad1985 p. 119) | an SD of about 10% overall is total spread, not error |
| Instrument | panjabi1991c, 1991t, 1992, 1993f, the same 12 spines | phantom with drawn shapes | linear, angular and area values within 5% (panjabi1991t p. 889; panjabi1991c p. 863; panjabi1992 p. 300; panjabi1993f p. 1300); point location +/-0.5 mm (panjabi1991t p. 889) | no observer study in any of the four. Inference (panjabi1992 note): 5% of SPL or TPW is 3.4-4.6 mm |
| Instrument | tan2004, 10 Chinese Singaporean cadavers | digitiser calibration | 0.01 mm stated; 1.28% at 20 mm, 0.44% at 10 mm; angle 0.68%; area 1.71% (tan2004 p. 138); each point the mean of 10 hits, each parameter the mean of 3 readings (tan2004 p. 139) | no observer study. Its SE is defined as SD/n, so SD = 3.16 x SE on the usual reading, or 10 x SE read literally (tan2004 p. 139) |

### 1.3 Modality against direct measurement

Each line gives the paired comparison, its material and its sign convention.

CT against bone or caliper:

- chen2011, 100 end plates of 10 cadavers. SCA 162.4 +/- 5.7 deg on CT against 162.1 +/- 6.1 on the cadaver, alpha 0.8191. Sagittal diameter 28.8 +/- 3.7 mm against 29.1 +/- 3.8 mm, alpha 0.8806 (chen2011 Table 4 p. 1818). The CT used 0.625 mm reformats (chen2011 p. 1815).
  - The printed "mean difference" of 0.3 is only the difference of the two means; no paired SD is given (chen2011 note).
  - Inference (chen2011 note): a near-flat concavity angle moves 6-8 deg per mm of depth error.
- krag1988, 8 cadaver vertebrae: sectioned = 1.01 x CT + 0.7 mm (krag1988 Fig. 7 p. 31). CT reads widths small, from convex cortices and partial volume in 4 mm cuts (krag1988 pp. 27, 31).
- vanderhouwen2009, 12 measurements on 2 pig vertebrae of about 29-55 mm: CT minus caliper -0.18 mm, SD 0.66 mm, limits of agreement -1.47 to 1.12 mm (vanderhouwen2009 Fig. 4 p. 39). The paper gives no error for concavity depth or wedge angle (vanderhouwen2009 note).
- mitra2002, 20 cadavers (18 men, 2 women), CT minus direct in men (mitra2002 Tables 1-2 p. 455, p. 456):
  - TD (transverse pedicle width): +0.45 to -1.79 mm, significant at L4-L5.
  - TA (transverse angle): +2.0 to -5.03 deg.
  - CL (chord length): +0.79 to +3.52 mm.
  - The CT used 5 mm slices (mitra2002 p. 456).
- zindrick1987: CT against film is reported only as no significant difference, with no numbers, on different vertebrae (zindrick1987 p. 160).

Film against bone or caliper:

- olsewski1990 Part 2, 21 disarticulated spines (12 men, 9 women). The technique was calibrated for no measurable magnification at 47 in (119.4 cm) (olsewski1990 p. 543), so these are projection and definition offsets, not magnification (olsewski1990 p. 548). Radiograph minus bone, L1 to L5 (olsewski1990 Table II p. 544):

  | Measure | L1 | L2 | L3 | L4 | L5 |
  |---|---|---|---|---|---|
  | Pedicle width (mm) | 0 | -0.1 | -0.2 | -0.6 | -3.5 |
  | Pedicle height (mm) | +1.8 | +1.8 | +1.5 | +0.2 | -2.4 |
  | Transverse angle (deg) | 0 | +2 | +6 | +5 | +7 |

  Beyond the table: sagittal angle within about 1 deg; distance +2.5 to +8.0 mm.
- mitra2002, lateral film minus direct (mitra2002 p. 455):
  - pedicle height -0.87 to +0.62 mm;
  - sagittal angle -3.4 to -6.1 deg;
  - craniocaudal interpedicular distance +3.0 to +5.7 mm.

  The film was at 100 cm with a "magnifying factor" printed as 0, which is not a possible factor (mitra2002 p. 453; note).
- kunkel2011, thoracic segments on contact films at 60 cm with a scale on the rig (kunkel2011 p. 377). Radiographic disc heights read short (kunkel2011 Table 1 p. 378):
  - ADH by about 9% (1.67-19.22% by level; 0.10-1.29 mm; R^2 0.921);
  - PDH by about 37% (28.91-50.12%; 1.11-2.51 mm; R^2 0.690).
- robertson2000, 10 specimens with wire on the cortex. The densest pedicle image lies 1-3 mm inside the true cortex in the lumbar spine (robertson2000 p. 711, Fig. 6 p. 712). At the medial S1 border it lies 3-4 mm inside (robertson2000 pp. 712-713). The films were corrected to a known standard (robertson2000 p. 710).
- panjabi1991c: its posterior body heights run 2-2.5 mm below the radiographic and caliper studies, because of where height was taken; Table 7 gives 1.8-3.0 (panjabi1991c p. 868).
- eisenstein1977: the radiographic markers were reproduced consistently in 11 skeletons, with no number given (eisenstein1977 p. 174).

MRI against CT or bone. The set holds no paired comparison; all of it is between studies:

- ahmed2019, 1.5 T, 4 mm slices: midsagittal canal depth (MS) is lower than other series (ahmed2019 Table 3 p. 25):

  | Comparison series | Modality | MS lower by (mm) |
  |---|---|---|
  | Amonoo-Kuofi | dry bone | 1.2-2.7 |
  | Al-Anazi | CT | 3.8-4.4 |
  | Alam | CT | 0.4-3.4 |
  | Varol | CT | 0.8-2.6 |
  | Shukri | MRI | 1.9-2.8 |

  Because another MRI series also differs, modality alone does not explain the gap (ahmed2019 note).
- italianmri: SCD agrees with Panjabi at L1-L3 within 0.6 mm, but rises only 0.4 mm to L5 against Panjabi's 2.2 mm (italianmri note, Tables 2-5 pp. 4-5).
- bach2019: the authors say MRI may give other heights, with no numbers (bach2019 p. e116).
- tang2016: no CT comparison. Its ellipse estimates of area err by 2% (APD) and 9% (MSD) (tang2016 pp. 4119, 4122).

### 1.4 Radiographic magnification and tube distances

| Study | Projection, distance | Factor or handling | Page |
|---|---|---|---|
| eisenstein1977 | dry skeletons, 110 cm tube to plate | lateral 1.23, AP 1.14, from 55 vertebrae of 11 skeletons, no spread given | eisenstein1977 pp. 174-175 |
| hinck1966 | AP, 40 in (101.6 cm) | not corrected; note Inference 1.07-1.17. AP spine against PA chest at 72 in: 0.57 mm larger on AP, 1.10 mm at T1-T3 and 0.38 at T4-T12 | hinck1966 pp. 141, 148 |
| amonookuofi1982 | AP, 100 cm | not corrected; every value is a film value | amonookuofi1982 p. 226 |
| ahn2001 | AP, printed "101 mm" (Inference: 101 cm) | not corrected | ahn2001 p. 68 |
| chaudhary2015 | AP, distance not stated | not corrected | chaudhary2015 p. 34 |
| gilad1985 | lateral; cervical 150 cm standing, lumbar 100 cm on the side | parallax corrected | gilad1985 pp. 115-117 |
| mitra2002 | lateral, 100 cm | factor printed as "0" | mitra2002 p. 453 |
| olsewski1990 | Part 2 at 119.4 cm; Part 3 clinical | Part 2 calibrated to none; Part 3 AP x1.08, corrected by 0.93; CT read at 0.55 of true size, corrected by 1.82 | olsewski1990 pp. 543-544 |
| kunkel2011 | contact films at 60 cm | scale on the rig | kunkel2011 p. 377 |
| robertson2000 | plain film | corrected to a known standard | robertson2000 p. 710 |
| zindrick1987 | constant technique | "no detectable magnification" | zindrick1987 p. 160 |

Inferences:

- If the factor is purely geometric, M = FFD / (FFD - OFD). Eisenstein's figures then put the canal about 20.6 cm from the film on the lateral and 13.5 cm on the AP (eisenstein1977 note). Any other geometry, a C-arm among them, needs its own factor.
- Inference: dM/dOFD = FFD / (FFD - OFD)^2.
  - Lateral: 110 / 89.4^2 = 0.0138 per cm, or 1.1% of 1.23 per cm of depth.
  - AP: 110 / 96.5^2 = 0.0118 per cm, or 1.0% of 1.14.
  - So structures a few centimetres apart in depth on one film differ in scale by a few percent.
- The film-to-cadaver width ratio has no single value (hinck1966 note, against hinck1966 Table II p. 145):
  - about 1.05-1.10 against Panjabi in the lumbar spine;
  - about 1.00 at T6-T8;
  - about 1.13-1.18 against Eisenstein's Caucasoid men.

  No single magnification factor reconciles the series, so magnification is confounded with definition.

### 1.5 Instrument and image resolution

| Study | Modality | Resolution as printed | Page |
|---|---|---|---|
| busscher2010 | CT | 1.00 mm slices, 0.39 x 0.39 mm pixels | busscher2010 p. 1105 |
| duman2026 | CT | 0.625 mm slices, bone window W1500/L300 | duman2026 pp. 3-4 |
| chen2011 | CT | 0.625 mm reformats | chen2011 p. 1815 |
| otsuki2021 | CT for comparison; micro-CT for study | clinical CT 0.625 mm slices, 0.53 mm pixels (note); micro-CT 34.4 um | otsuki2021 p. 10, Table 2 p. 6 |
| griffith2016 | CT | 0.6 mm reconstruction | griffith2016 p. 672 |
| vanderhouwen2009 | CT | 0.75 mm slices read on 3.13 mm average projections | vanderhouwen2009 p. 34 |
| abbas2021 | CT | 0.9-3 mm slices; pixel not given | abbas2021 p. 2 |
| moncadahabib2025 | CT | 1.0 mm slices, FOV 250 mm (note Inference: 0.49 mm pixels) | moncadahabib2025 p. 3 |
| frontphys2026 | CT | 3.0 mm acquisition slices, reconstructed at 1 mm slices and interval, B60s kernel | frontphys2026 p. 3 |
| makino2012 | CT | 1.25 mm slices, window W2000/L300, software 0.01 mm | makino2012 p. 1517 |
| yadav2020 | CT | 3 mm sections reconstructed to 1 mm; pixel not given | yadav2020 p. 176 |
| arockiaraj2025 | CT | 2.5 mm contiguous slices; pixel not given | arockiaraj2025 p. 314 |
| krag1988 | CT | 4 mm cuts; reading resolution about 0.4 mm life size, angles 0.5 deg | krag1988 pp. 27, 31 |
| olsewski1990 | CT, caliper | 4 mm cuts; caliper +/-0.1 mm, protractor +/-1 deg, mean of 3 trials | olsewski1990 pp. 541-543 |
| mitra2002 | CT, caliper | 5 mm slices; 0.1 mm, 1 deg | mitra2002 p. 456 |
| bach2019 | CT surface model | 226-3071 HU threshold; slice and voxel not given | bach2019 p. e107 |
| alonge2021 | CT | 0.1 mm readout at 4x display; slice not given | alonge2021 p. 71 |
| masharawi2021, shin2024 | CT | slice and pixel not given | masharawi2021 p. 3; shin2024 note |
| ahmed2019 | MRI 1.5 T | 4 mm slices (4.3 on a figure overlay); readout 0.1 mm | ahmed2019 pp. 22-23 |
| italianmri | MRI 1.5 T | 4 mm slices, 0.4 mm spacing, matrix 384 x 224 over 320 mm (note Inference: 0.83 x 1.43 mm pixels) | italianmri p. 2 |
| tang2016 | MRI 1.5 T | 3-4.5 mm slices; pixel not given | tang2016 p. 4117 |
| yu2015 | dry bone | caliper 0.01 mm | yu2015 p. 1640 |
| twomey1985 | sections | calipers 0.05 mm | twomey1985 p. 496 |
| kunkel2011 | sections, film | digital caliper +/-0.05 mm | kunkel2011 p. 377 |
| hou1993, amonookuofi1985, lien2007 | dry bone | vernier 0.1 mm (lien: goniometer 1 deg) | hou1993 p. 1851; amonookuofi1985 p. 72; lien2007 p. 1216 |
| amonookuofi1982, chaudhary2015 | film | vernier 0.1 mm; ruler 0.5 mm | amonookuofi1982 p. 226; chaudhary2015 p. 34 |
| robertson2000 | film with wire | wire 0.4 and 0.8 mm | robertson2000 p. 710 |
| eisenstein1977 | dry bone | vernier; Table I printed to whole mm, so +/-0.5 mm of rounding (note) | eisenstein1977 p. 173 |

Spurious precision is common:

- yadav2020 prints values to 0.001 mm (yadav2020 note).
- italianmri prints figure values to 0.01 mm on pixels about 1 mm wide (italianmri note).
- makino2012 states a software precision of 0.01 mm (makino2012 p. 1517).

### 1.6 Partial volume and cortical thickness

- otsuki2021, micro-CT of 6 donors at 34.4 um (otsuki2021 Table 2 p. 6):
  - pedicle walls 0.6-1.7 mm thick;
  - the L1 lateral wall 0.6 mm; the L5 lateral wall 1.7 mm and the medial 1.3 mm;
  - the cranial and caudal walls about 3 mm and porous;
  - lateral bone area fraction 58.8% against 97.4% medial.
  - Inference (otsuki2021 note): about +/-0.5 mm per wall for a mask boundary at 0.5-0.6 mm voxels.
- Cortex measured on CT by mitra2002, as quoted by otsuki2021 (otsuki2021 pp. 7-8; mitra2002 Table 2 p. 455):
  - lateral 0.82, 0.55, 0.87, 0.60, 1.25 mm at L1-L5;
  - medial 1.07, 1.15, 1.15, 1.37, 1.32 mm.
- Other cortex figures quoted by otsuki2021 (otsuki2021 pp. 7-8):
  - Li, CT: medial 1.4-2.3 mm, lateral 0.8-1.8 mm.
  - Inceoglu, direct: lateral 609 um, medial 793 um.
- Donor build: the BMI 34.2 donor has a lateral bone area fraction of 46.4%, against 74.3% for the BMI 17.0 donor (otsuki2021 Table 3 p. 6).
- frontphys2026: end-plate thickness 0.8 mm anterior and 0.9-1.0 mm posterior, at the resolution limit of 1 mm CT (frontphys2026 pp. 6-7).
- bach2019: the 226 HU threshold sets where the end-plate surface lies. Another threshold or a learned mask boundary moves every disc height by up to about one voxel in total (bach2019 p. e107; note).
- Inference (hou1993 note): partial volume at 1 mm voxels changes a 5-7 mm pedicle width by 10-20%.
- Inference (arockiaraj2025 note): pedicle height measured across 2.5 mm slices carries up to +/-1.25 mm.
- Inference (abbas2021 note): with slices up to 3 mm, a plane named as "mid-height" can fall up to half a slice from where it is meant to be.

### 1.7 Definition offsets between careful studies

Offsets of definition are larger than any observer error in 1.2. Each one is a difference between series, with the method that explains it.

- Pedicle width, panjabi1991t against earlier series (panjabi1991t Table 8 pp. 899-900, p. 898):
  - Panjabi's widths are 1-2 mm wider than earlier work.
  - Scoles' widths are 2-3 mm below Zindrick's and 3-4 mm below Panjabi's and Krag's.
  - At T6: Scoles 3.5, Zindrick 5.2, Cotterill 4.1, Panjabi 6.0 mm.
  - The note concludes that the definition of the section dominates the error.
- Pedicle sagittal angle at T12 (panjabi1991t Table 8 pp. 899-900): Panjabi 9.8, Zindrick -4.2, Berry -3.0, Krag 0.0 and Scoles 9.5 deg.
- End-plate depth (panjabi1991t p. 898): Panjabi's lower end-plate depth runs 4-5 mm above Scoles and Cotterill, whose depths were probably taken at mid-body height.
- Rim chords: Panjabi's EPD runs 6-8 mm and his EPW about 5 mm above vanderhouwen2009's rim chords (vanderhouwen2009 note). chen2011's male sagittal diameter sits 4-6 mm below Panjabi's EPD (chen2011 note).
- Mid-body against end plate: italianmri's mid-body VBD is 26.5-29.6 mm against Panjabi's EPDu 34.1-35.5 mm (italianmri note).
- Pedicle height by definition: Panjabi's L5 PDH is 19.6 mm against yu2015's narrowest-point PH of 13.67 mm (yu2015 note).
- Area estimates: Panjabi's end-plate ellipse estimate is about 10% over the digitised area. His canal ellipse is 10-30% over and his canal triangle 20-30% under (panjabi1992 p. 305; panjabi1991t p. 900).
- Canal width in the thoracic spine: Scoles' canal widths are about 1 mm below Panjabi's (panjabi1991t p. 898).

### 1.8 Between-subject spread as an upper bound

Every SD a paper prints for a level mixes biology with measurement error. That SD is an upper bound on sigma_err, and a lower bound on what the generator must spread.

- Panjabi lumbar end-plate width: SEM 0.74-1.41 mm, so SD about 2.6-4.9 mm (3.46 x SE; panjabi1992 p. 301 Table 2 and note).
- Thoracic pedicle width: SD 1.2-3.7 mm (panjabi1991t note).
- zindrick1987, SDs that also mix modalities (zindrick1987 note):
  - pedicle width SD 0.9-4.1 mm, a CV of 16-32%;
  - angles SD 2.2-9.5 deg;
  - depths SD 3.1-11.0 mm.
- tan2004 median CVs (tan2004 note):

  | Measure | Median CV |
  |---|---|
  | EPW | 3% |
  | EPD | 4-5% |
  | VBH | 4.5-6% |
  | SCW | 7% |
  | SCD | 6% |
  | PDH | 7-9% |
  | PDW | 12-13% |

- yadav2020 between-subject CVs in men (yadav2020 note):
  - body widths and depths 7-12%;
  - canal depth 8-14%, and 21-30% at L5 and S1;
  - disc height 17-25%.
- Disc height SDs 0.8-2.9 mm (bach2019 Table 6 p. e113).
- Panjabi's and tan2004's printed dispersions are standard errors of the mean (panjabi1992 p. 300; tan2004 p. 139). Compilations can set them beside other series' SDs unconverted: tang2016 lists end-plate FD as Panjabi 4.80-4.95 (0.12-0.14) cm and Tan 4.35-4.53 (0.03-0.05) cm beside Zhou's 5.17-5.31 (0.47-0.60) cm (tang2016 Table 6 p. 4126). Convert every printed SE before using it as a spread.
- frontphys2026's end-plate width SDs of 0.6-1.0 mm in a mixed-sex sample aged 20-70 are implausibly small next to Panjabi's 2.6-4.2 mm (frontphys2026 note, Table 2 p. 5).

## 2. Covariates

### 2.1 Sex

The male-female gap is not one number. Bodies differ by about 9-13%, pedicle width by up to 20%, the canal by about 0-6% or with women deeper, and angles not at all.

| Family | Study, material, n | Male against female | Page |
|---|---|---|---|
| Body diameters | abbas2021, CT, living Israeli | bodies 2.4-4.7 mm larger in men; canal equal | abbas2021 Table 1 p. 4 |
| Body heights | duman2026, CT, 277 men, 240 women, living | heights 9.1-11.9% larger in men, d about 1.1-1.4 (note) | duman2026 p. 7 |
| End-plate diameters | chen2011, CT, living Chongqing patients | women about 0.88 of men for sagittal and transverse diameters | chen2011 pp. 1816-1817 |
| End-plate diameters | vanderhouwen2009, CT, living Dutch 21-86 y, 25 end plates per level | female/male medians 0.91 sagittal, 0.88 transverse; none on concavity | vanderhouwen2009 Table 2 p. 39 |
| Body depth | italianmri, MRI, 604 living Italians 20-45 | VBD 3.5-4.1 mm larger in men at every level | italianmri Tables 2-5 pp. 4-5 |
| Disc and end-plate diameters, areas | tang2016, MRI, 109 living US adults 20-40 | diameters 6-16% and areas 16-26% larger in men, while stature differs by only 178 against 166 cm | tang2016 pp. 4119, 4122, Table 2 p. 4119 |
| End-plate diameters | yadav2020, CT, living North Indian 20-40 | 0.75-3.2 mm (2-9%) larger in men; canal depth and foramen equal | yadav2020 pp. 177-178 |
| Body diameters | eisenstein1977, dry bone, South African | 1-6 mm larger in males | eisenstein1977 Table I p. 174 |
| Body depth | amonookuofi1985, dry bone, Nigerian | female body AP about 3 mm smaller at L1-L4 | amonookuofi1985 Table 4 p. 74 |
| Body width, length | moncadahabib2025, CT, 37 living Mexicans | CW +4.3 mm, CL +3.1 mm (male/female about 1.10 and 1.11) | moncadahabib2025 Table 3 p. 6 |
| Mid-body area | griffith2016, CT, 540 levels per sex, living Hong Kong Chinese | VB CSA larger in men at every level, also after adjustment for height and weight | griffith2016 Table 5 p. 675 |
| Anterior body height | bonczar2024, meta-analysis | no sex effect | bonczar2024 Table 7 p. 10 |
| Body heights | hou1993, dry bone, Chinese | heights 0.2-1.8 mm larger in males | hou1993 Tables 1-3 p. 1852 |
| Canal | eisenstein1977 | AP equal (females equal or larger); interpedicular 0-2 mm larger in males | eisenstein1977 Table I p. 174, p. 179 |
| Canal | italianmri | SCD equal at L1-L4; men larger at L5 (0.4 mm) and S1 (1.3 mm) | italianmri Tables 2-5 pp. 4-5 |
| Canal | cizmic2023, CT, living Bosnian | women deeper by 0.5-1.1 mm while men are wider | cizmic2023 Table 5 p. 202 |
| Canal | griffith2016 | depth unadjusted 15.82 men against 15.55 women; adjusted, women deeper at L1-L3; width larger in men at every level, also adjusted | griffith2016 Table 3, Table 4 p. 675; p. 673 |
| Canal | alonge2021, CT, living Nigerian | TD men +1.2 to +2.1 mm per level; APD equal | alonge2021 Tables 1-4 p. 73 |
| Canal | hinck1966, film, living white | IPD about 1 mm larger in men (computed adult mean 1.25 mm) | hinck1966 p. 143 |
| Canal | chaudhary2015, film, living North Indian | IPD female/male 0.90-0.95 | chaudhary2015 Table I p. 34 |
| Canal | bonczar2024 | IPD men about 1 mm (3.5-5%) larger | bonczar2024 Table 7 p. 10 |
| Canal | amonookuofi1985 | female canal 0.7-1.5 mm smaller | amonookuofi1985 Table 1 p. 71 |
| Canal | ahmed2019, MRI | TD only, 1.3-1.6 mm at L1-L4, 0.4 mm at L5 | ahmed2019 Tables 1-2 pp. 22, 24 |
| Pedicles | yu2015, dry bone, n = 503 per level | female/male PW 0.80 (L1) to 0.88 (L5); PH 0.91-0.93 | yu2015 Table 4 p. 1643 |
| Pedicles | olsewski1990, cadavers and living | linear dimensions 5-23% larger in men in elderly cadavers; width up to 44% in young living patients; angles equal | olsewski1990 pp. 544-547 |
| Pedicles | arockiaraj2025, CT, 150 men, 150 women | TPD sex effect about 16% at L1 falling to 5% at L5 (note) | arockiaraj2025 Table 2 p. 316 |
| Pedicles | hou1993 | width 0.4-1.3 mm larger in males, female 0.2 mm wider at L5; female/male 0.85-0.96 (note) | hou1993 Tables 1-3 p. 1852 |
| Pedicles | duman2026 | width and height 1-7% larger in men, none at T12 | duman2026 p. 7 |
| Pedicles | moncadahabib2025 | PW +1.1 mm (ratio about 1.14); PH +0.45 mm, not significant | moncadahabib2025 Table 3 p. 6 |
| Discs | bach2019, CT, 131 women, 109 men, living | anterior height ratio men/women 1.31 at T12/L1 falling to about 1.05 at L5/S1, none at L5/S1 | bach2019 Table 6 p. e113 |
| Discs | shin2024, CT, living | men larger, the gap shrinking caudally and gone for middle and posterior DSH at L5-S1 | shin2024 Table 4 p. 4 |
| Discs | twomey1985, cadaver | males thicker at every level (young adults 1.8-3.1 mm) | twomey1985 Table 2 p. 497 |
| Discs | yadav2020 | larger in men as stated, but the printed values do not support it | yadav2020 pp. 177-178 |
| Angles | olsewski1990, duman2026, chen2011, moncadahabib2025 | no sex difference in pedicle, end-plate or concavity angles | olsewski1990 pp. 544-547; duman2026 p. 7; chen2011 pp. 1816-1817; moncadahabib2025 Table 3 p. 6 |
| Lamina angles | abbas2021 | LI larger in women by 2.6-3.9 deg (note, from Table 4); ILA smaller in women by 2-5 deg | abbas2021 Table 4 p. 6 |

Inference, the female/male ratios taken from the table above:

| Measure (source) | Female/male ratio | log(M/F) |
|---|---|---|
| Body diameters (chen2011, vanderhouwen2009) | 0.88-0.91 | 0.094-0.128 |
| Body heights (duman2026) | 1/1.091 to 1/1.119 | 0.087-0.112 |
| Pedicle width (yu2015) | 0.80-0.88 | 0.128-0.223 |
| Pedicle height (yu2015) | 0.91-0.93 | 0.073-0.094 |

The canal ratios, computed from griffith2016's L1-L5 means:

| Canal measure | Unadjusted ratio | log(M/F) | Adjusted ratio | log(M/F) |
|---|---|---|---|---|
| Width | 22.26 / 23.66 = 0.941 | 0.061 | 22.54 / 23.38 = 0.964 | 0.037 |
| Depth | 15.55 / 15.82 = 0.983 | 0.017 | 15.87 / 15.50 = 1.024 | -0.024 |

The ratios come from griffith2016 Tables 3-4 p. 675, Tables S2-S3. The adjustment is for height and weight. The canal therefore carries a third or less of the body's sex gap, and one sex shift on every measure cannot fit both. cizmic2023 shows the opposite signs within one study (cizmic2023 Table 5 p. 202).

### 2.2 Age

- End-plate concavity: the cranial concavity rises about 0.01 mm per year, in living Dutch patients 21-86 y (vanderhouwen2009 pp. 36, 38).
- griffith2016 (Table 1 p. 674; p. 676; Table S5):
  - Canal width rises about +0.04 mm per year, r 0.28 in men and 0.27 in women (note Inference). The canal CSA is flat with age. The depth is flat in men and falls slightly in women.
  - VB CSA rises about +1.8 mm2 per year in men and +2.7 in women (note Inference). In the means by age group, men go from 1,378.8 to 1,448.0 mm2 and women from 1,129.8 to 1,213.0 mm2, from 21-40 y to 61-80 y.
  - Older patients were also shorter (griffith2016 p. 673).
- Pedicles, adjusted for height, weight, sex and race, in dry bone (yu2015 Table 2 p. 1641):
  - PH rises +0.011 to +0.018 mm per year;
  - PW rises +0.008 to +0.026 mm per year.
- Pedicle height: Spearman rho -0.27 (right) and -0.30 (left) in 37 living Mexicans (moncadahabib2025 Table 4 p. 6). Each patient's levels are pooled, so the p values are optimistic (moncadahabib2025 note).
- Disc height: the two sides disagree.

  | Study | Material, n | Finding | Page |
  |---|---|---|---|
  | bach2019 | supine CT of 240 living patients in Tampa | Women: anterior height falls at L3/4 to L5/S1 (R -0.265 to -0.388); posterior falls at L1/2 to L4/5; foraminal height falls at every level. Men: middle height rises at T12/L1 to L2/3 (R 0.403, 0.341, 0.258) | bach2019 Tables 7-8 p. e114 |
  | twomey1985 | sections of 204 cadavers; mean height from the disc's area | Height rises from young adult to 60+, males +0.6 to +1.1 mm and females +0.3 to +1.8 mm. AP diameter rises about 9-11% in females and 3-4% in males. Adjusting for stature strengthened the rise | twomey1985 p. 497 |

  The methods differ (living supine CT against a cadaver area mean), and neither series is matched to the other's population.
- Degeneration and osteophytes:
  - Discs graded 2-3 by Rolander, out of the discs graded (twomey1985 Table 4 p. 498):

    | Age | Discs graded 2-3 |
    |---|---|
    | 13-20 | 2 of 65 |
    | 20-35 | 11 of 158 |
    | 36-59 | 30 of 170 |
    | 60+ | 98 of 170 |

    Only grade 3 (47 of 170 at 60+, 28%) includes thinning and desiccation; the authors call degeneration a minority of elderly discs, which holds only for grade 3 (twomey1985 pp. 497-499; note). The Rolander grades come from 140 specimens, sexes pooled, while the abstract says 204 (twomey1985 pp. 496, 498).
  - Osteophytosis of the lumbar spine in dry skeletons, by group (eisenstein1977 Table IV p. 176): Caucasoid men 50%, Zulu men 25.2%, Sotho men 43.4%, Caucasoid women 51.4%, Zulu women 55.6%, Sotho women 43.5%; mean age of those affected 70, 58, 53, 70, 58 and 52 years. It worsens from L1 to L5 (eisenstein1977 p. 175). The text says 169 skeletons, while the table's percentages of the group sizes give about 187 (eisenstein1977 p. 176; note). The grading is admitted to be subjective (eisenstein1977 p. 179). Body measures were taken at mid-height to keep border osteophytes out (eisenstein1977 note).
  - Thoracic donors (kunkel2011 p. 379): the sample was only mild to moderately degenerated; grade iii bodies already carry marginal corner osteophytes under 2 mm, and a grade iv disc or an anterior osteophyte over 2 mm lies outside the norms. The authors say post-mortem change and degeneration may add error to disc heights (kunkel2011 p. 383; note).
  - Facet arthrosis, Pathria grade 3, in 50 living Israeli controls aged 50-80 (masharawi2021 Table 3 p. 8): men 16.7-66.7% and women 23.1-57.7% of joints by level and side, highest at L5-S1 in every group. The per-cell denominators are not printed. Single-level degenerative spondylolisthesis at L4-L5 lowers foramen height by 1.85-3.94 mm and makes lower lumbar pedicles taller and longer by 1-2.14 mm (masharawi2021 note, Tables 2-5).
  - Most normative series excluded osteophytes: chen2011 (marked osteophytes, p. 1815), alonge2021 (degenerative change at the landmarks and age over 65, p. 70), frontphys2026 (severe osteophytosis, p. 3), amonookuofi1985 (specimens with osteophytes, p. 71). Their tables describe spines without them. Trim osteophyte voxels from a mask before taking a width, depth or corner height, or the value will read large against these tables and against Panjabi (chen2011 note; frontphys2026 note; busscher2010 note).
  - Caudad L5 pedicles: 12 of 83 L5 pedicles in elderly cadavers pointed caudad (olsewski1990 Table I p. 544). In that paper age is confounded with method: elderly cadavers by caliper, young adults by radiograph and CT (olsewski1990 note).
- Growth: lumbar IPD grows 4.5-5.2 mm from 3-5 y to adult; mid-thoracic growth is least (hinck1966 pp. 143-144; note).
- No age effect:
  - chen2011, 21-65 y, tested only as over 40 against 40 or under (chen2011 p. 1815);
  - duman2026 on TPD (duman2026 Table 4 p. 8);
  - masharawi2021, 50-80 y, 0.53 < p < 0.994 (masharawi2021 p. 4).
- Confounding with population: eisenstein1977's Caucasoid groups average 65-66 y against 40-49 y for its African groups (eisenstein1977 Table IV p. 176).

### 2.3 Stature and weight

| Study | Material | Finding | Page |
|---|---|---|---|
| yu2015 | dry bone, n = 503 per level, adjusted for age, sex, race and weight | PH +4.97 to +5.68 mm per m; PW +2.07 (L1), +2.71, +3.34, +4.20, +7.59 (L5) mm per m. Elasticity at 1.70 m: PH 0.56-0.71, PW 0.41-0.70 (note). Weight: PW +0.015 to +0.022 mm per kg, PH -0.011 to +0.005 | yu2015 Table 2 p. 1641 |
| griffith2016 | CT, living, men 168.1 +/- 6.8 cm, women 157.0 +/- 5.9 cm | r with height (men / women): canal CSA 0.186 / 0.298, depth 0.163 / 0.255, width 0.126 / 0.143, VB CSA 0.331 / 0.264. Weight r for VB CSA 0.255 / 0.269 | griffith2016 p. 673, Table 1 p. 674 |
| shin2024 | CT, living 18-35 | DSH against height r .000-.050 within sex; weight r .05-.35; BMI r .04-.25 | shin2024 Table 7 p. 5 |
| italianmri | MRI, 604 living | no measure correlates with height or weight (R^2 < 0.1) | italianmri p. 3 |
| masharawi2021 | CT, living 50-80 | no effect of height, weight or BMI | masharawi2021 p. 4 |
| twomey1985 | cadaver | disc thickness rises linearly with stature at every level (p < 0.05); slope and stature not printed | twomey1985 p. 497 |
| tang2016 | MRI | men 178 against women 166 cm (ratio 1.076, squared 1.158, note); the sex gap exceeds stature | tang2016 Table 2 p. 4119 |
| bach2019 | CT | stature incomplete, no relation reported; women's stature fell with age (R -0.332) | bach2019 pp. e114, e117 |
| amonookuofi1982 | film | IPD proportional to body width | amonookuofi1982 p. 231 |
| hinck1966 | film | individuals differ mainly in the overall level of their profile, not in single vertebrae | hinck1966 p. 146 |
| busscher2010 | CT of 6 Dutch male cadavers, 175-192 cm (mean 182) | "striking resemblance" to Panjabi in pedicle width and height, canal width and depth and transverse process length, with no numbers in the note | busscher2010 pp. 1105-1106, 1112 |

Inference, elasticity with stature from griffith2016's correlations: slope = r x SD_y / SD_height, then elasticity = slope x mean height / mean value. The inputs are the L1-L5 subject means and SDs (griffith2016 Tables 2-5 p. 675; p. 673).

| Measure | Men | Women | Isometric |
|---|---|---|---|
| Canal depth | 0.163 x 1.96 / 6.8 = 0.047 mm/cm; x 168.1 / 15.82 = 0.50 | 0.255 x 1.72 / 5.9 = 0.074; x 157.0 / 15.55 = 0.75 | 1 |
| Canal width | 0.126 x 2.59 / 6.8 = 0.048; x 168.1 / 23.66 = 0.34 | 0.143 x 2.25 / 5.9 = 0.055; x 157.0 / 22.26 = 0.39 | 1 |
| VB CSA | 0.331 x 185.5 / 6.8 = 9.03 mm2/cm; x 168.1 / 1,419.3 = 1.07 | 0.264 x 153.7 / 5.9 = 6.88; x 157.0 / 1,162.9 = 0.93 | 2 |
| Canal CSA | 0.186 x 50.3 / 6.8 = 1.38; x 168.1 / 278.5 = 0.83 | 0.298 x 42.5 / 5.9 = 2.15; x 157.0 / 262.8 = 1.28 | 2 |

Halved, the area elasticities give a linear equivalent of 0.53 and 0.46 for VB CSA and 0.42 and 0.64 for canal CSA. With yu2015's ends (PH 0.56 and 0.71, PW 0.41 and 0.70), the twelve estimates are 0.34, 0.39, 0.41, 0.42, 0.46, 0.50, 0.53, 0.56, 0.64, 0.70, 0.71 and 0.75. Their mean is 6.41 / 12 = 0.53, their median 0.515, and their SD 0.14 (sum of squared deviations 0.211, / 11, square root). Every one is below isometric 1.

Two caveats:

- A slope from a correlation is attenuated by error in the measured stature, so the true elasticities are somewhat larger by an unknown amount.
- No paper in the set regresses end-plate width, end-plate depth, posterior body height, the spinous or transverse processes or the facets on stature.

The owner's expectations, that weight compresses the discs and age changes the facets (covariates.py), are not tested in the set:

- The only weight figure on discs is shin2024's weak positive r of .05-.35, which is no compression (shin2024 Table 7 p. 5).
- bach2019 reports no relation (bach2019 p. e114).
- masharawi2021 finds no age effect on facets within 50-80 y (masharawi2021 p. 4).

### 2.4 Populations against Panjabi's twelve

Panjabi's sample:

- Twelve fresh autopsy spines, C2 to L5, 8 men and 4 women (panjabi1991t note; panjabi1992 p. 299).
- 19-59 y (mean 46.3), 54-85 kg (mean 67.8) and 157-178 cm (mean 167.8) (panjabi1992 p. 299).
- The men averaged 50.3 y, 70.4 kg and 170.3 cm, against the women's 38.5 y, 62.8 kg and 162.8 cm (panjabi1991t Table 1 p. 889).
- Six of the twelve died of malignancy (panjabi1991t Table 1 p. 889; note).
- Country and ethnicity are not stated. The note infers a US autopsy service from the Yale address (panjabi1991t note). bonczar2024 calls the series Caucasian (bonczar2024 p. 9).
- Inference: the reference height of 167.75 cm matches the 8:4 mix, since (8 x 170.3 + 4 x 162.8) / 12 = 167.8.

Each comparison below is between studies, so it carries population, method, definition and age together:

| Population, material, n | Against Panjabi | Page |
|---|---|---|
| Chinese Singaporean, 10 cadavers, 65.7 y, 1.66 m, 61.6 kg, sex not reported | factors below | tan2004 p. 137, Table 2 |
| North Indian, living CT | canal depth 3-5 mm below; end-plate depth 2-6 mm smaller; widths similar | yadav2020 note, Tables 4-8 pp. 179-181 |
| Telangana Indian, MRI | MS 4.7-6.1 mm below Panjabi SCD; IPD within 1.3 mm of SCW | ahmed2019 note, Table 3 p. 25 |
| Hong Kong Chinese, living CT | Panjabi canal depth 3.3-3.6 mm larger than Griffith's men at L1-L4, equal at L5; width +2.8 mm at L1, -2.5 mm at L5 | griffith2016 note |
| Bosnian, living CT | MSG matches at L1 and is 0.8-1.9 mm smaller at L3-L5; IPD 1-2 mm larger at L1-L4 and 4.8 mm at L5 | cizmic2023 note, Tables 6-11 pp. 203-204 |
| Israeli 50-80 y, living CT | VCW 1-3.3 mm below; VCL 2.6-5.3 mm smaller; L5 PW 14.1 against 18.6 mm | masharawi2021 note |
| Mexican, living CT | PW 2-6 mm narrower; PH 3-9 mm lower | moncadahabib2025 note |
| Henan Chinese, living CT | EPWu +0.6 to +1.1 mm at L1-L4 and +3.4 at L5; VBHp +1.7 to +3.8 mm | frontphys2026 note |
| Nigerian, living CT | Panjabi SCD 2.4-3.4 mm deeper; TD 22.5-32.4 against SCW 23.7-27.1 mm | alonge2021 note |
| Nigerian, dry bone | Panjabi SCD 2.4-3.7 mm above the male means and 3.1-5.1 mm above the female | amonookuofi1985 note |
| Chinese, dry bone | Panjabi pedicle widths larger (T9 7.7 against 5.7, L5 18.6 against 12.9 mm); lumbar heights agree (L5 19.6 against 19.8) | hou1993 note |
| US Hamann-Todd, dry bone | PW agrees (L1 8.6 against 8.52, L5 18.6 against 18.33); PH at L5 19.6 against 13.67 by definition | yu2015 note |
| US tissue bank, micro-CT, 6 donors | L5 transverse 11.8 against 18.6 mm | otsuki2021 note |
| Indian, 20 cadavers | L5 PDH flat against Panjabi's rise to 19.6; TA at L5 29.3 against 24.5 deg | mitra2002 note |
| US, cadavers | L5 PDH 17.4 men / 16.2 women against 19.6; PDW at L5 21.1 / 18.4 against 18.6 | olsewski1990 note |
| Turkish, living CT | PDW and PDH shapes opposite to Panjabi's at the thoracolumbar junction | duman2026 note |
| Dutch, living CT | Panjabi EPD 6-8 mm and EPW about 5 mm above the rim chords (definition) | vanderhouwen2009 note |
| Chongqing, living CT | Panjabi EPD 4-6 mm above the male sagittal diameter | chen2011 note |
| body donors (authors at Ulm; country not named), thoracic sections | VBHP 0.2-2.0 mm above Panjabi's thoracic VBHp | kunkel2011 note |
| Italian, MRI | mid-body VBD 26.5-29.6 against end-plate EPDu 34.1-35.5 mm (definition) | italianmri note |
| Dutch male cadavers, 182 cm | "striking resemblance" | busscher2010 p. 1112 |
| US white patients, film | film/cadaver width ratio 1.05-1.10 lumbar, 1.00 at T6-T8 | hinck1966 note |
| South African dry bone, 443 skeletons (Caucasoid, Zulu, Sotho) | Panjabi SCD 1.0-2.6 mm above Caucasoid men's minimum chord at every level; Panjabi SCW 0.2 mm below to 1.4 mm above their greatest interpedicular distance | eisenstein1977 note, Table I p. 174 |
| Israeli, living CT, 345 people aged 40+ | canal ML at mid body 0.8-1.8 mm above Panjabi SCW at L1 and about 8 mm above at L5 (34.9 against 27.1); canal AP within about 1 mm of SCD; the ML is a longest line, a definition offset | abbas2021 note, Table 2 p. 5 |
| Israeli working men 20-38, lateral films, 157 lumbar and 141 cervical spines | no numerical comparison in the note; corner-to-corner silhouette distances include the rim and any lipping | gilad1985 note |
| Saudi, living CT, 300 adults 18-60 | pedicle height 8.3-9.75 mm against Panjabi's PDH of 14.4-19.6 mm; the note reads it as a definition or resolution difference, the authors as population | arockiaraj2025 Table 3 p. 317, p. 318; panjabi1992 p. 301 |
| Japanese, living CT, 50 patients 52-85 (mean 70.1) | endosteal pedicle widths, below Panjabi's outer-cortex values by about two cortical thicknesses; no number in the note | makino2012 note |
| Taiwanese, 15 dry sets and 6 cadavers | L5 width 17.6 mm against Panjabi 18.6 mm; no sex or age data | lien2007 Table 1 p. 1218; panjabi1992 p. 302 |
| New Zealand authors, 10 dry-bone specimens of unstated origin | coaxial L5 width 21.6 mm against Panjabi's 18.6 mm; a coaxial bounding width, not an axial one | robertson2000 Table 1 p. 711; panjabi1992 p. 302 |
| zindrick1987: US authors, mixed specimens and clinical CT, numbers and population not stated (zindrick1987 p. 160) | T6 pedicle width 5.2 against Panjabi 6.0 mm | panjabi1991t Table 8 pp. 899-900 |
| US Vermont, living CT, 41 patients 18-75 | no numerical comparison with Panjabi; CT read slightly low against sections (sectioned = 1.01 x CT + 0.7 mm) | krag1988 Fig. 7 p. 31 |
| US Utah, MRI, 109 adults 20-40 | Panjabi's end-plate areas 7-22% below Tang's traced areas; the note calls the cause a guess to test (ellipse definition, age, cadaver) | tang2016 note, Tables 6-7 pp. 4125-4128 |
| US Loma Linda, living CT, 700 adults 18-35, multi-ethnic | discs only; no Panjabi counterpart | shin2024 note |
| US Tampa, living CT, 240 people 10-80 | discs only; no Panjabi counterpart | bach2019 note |
| Western Australian cadavers (by inference), 204 | discs only; no Panjabi counterpart | twomey1985 note |
| US Marfan adults, 32, AP film, against Hinck's controls | Marfan IPD 1.18-1.33 x normal from L1 to L5, on the film scale | ahn2001 note, Table p. 68 |
| Nigerian, 290 living AP films, 20-45 | uncorrected film IPD; narrower than Hinck's white Americans, wider than Eisenstein's Zulus; no Panjabi comparison | amonookuofi1982 Fig. 5 p. 230 |
| North Indian, 300 living AP films, 25-40 | uncorrected film IPD; no numerical Panjabi comparison | chaudhary2015 note |
| Pooled, 1,481 people in 18 studies, 1,076 Asian | includes Panjabi's 12 as one source; its Table 1 labels Panjabi Asia, India, radiograph while its text calls the series Caucasian | bonczar2024 p. 3, p. 9 |

tan2004's factors, Chinese Singaporean over Panjabi's values. Each is computed as 1 + regional mean difference / 100 from Table 2 (tan2004 note):

| Measure | C3-C7 | T1-T12 | L1-L5 |
|---|---|---|---|
| EPW | 0.86 | 0.91 | 0.90 |
| EPD | 0.90 | 0.83 | 0.85 |
| VBHp | 0.98 | 0.97 | 0.92 |
| SCW | 0.81 | 0.79 | 0.82 |
| SCD | 0.62 | 0.73 | 0.62 |
| PDH | 0.87 | 0.82 | 0.86 |
| PDW | 0.85 | 0.72 | 0.68 |
| SPL | 1.05 | 0.98 | 0.77 |
| TPW | 0.91 | 0.83 | 0.81 |
| SCA | 0.64 | 0.73 | 0.60 |

The canal and pedicle factors lie far below the body factors, so one size factor cannot reproduce them.

The two Singapore series point opposite ways. tan2004's 10 Chinese Singaporean cadavers (C3-L5, digitiser) read below Panjabi on almost every measure (tan2004 p. 144). bonczar2024 cites another Tan series, 60 lumbar vertebrae of 12 Singaporean cadavers, as larger than Panjabi's on numerous measures despite a smaller physique (bonczar2024 p. 9); that paper is not in the set, so its method cannot be compared. Keep both and do not take a Singapore or Chinese factor from either alone.

Within-study contrasts by one method, the clean ones:

- Canal, Africans against Caucasoids: African canals are 0-3 mm (mostly 1-2 mm) smaller than Caucasoid in both diameters (eisenstein1977 Table I p. 174, p. 179). This is confounded with age (eisenstein1977 Table IV p. 176).
- Pedicles, Caucasian against African American (yu2015 Table 4 p. 1643):
  - PH differs by 0.01-0.17 mm, not significantly;
  - PW is wider in African Americans at L1-L2 and in Caucasians at L5 (18.69 against 17.86 mm).
- Discs: Asians have the largest anterior and posterior DSH; White, Hispanic and Black are alike (shin2024 Table 5 p. 4).
- Between studies only: Nigerian IPD is narrower than Hinck's white Americans and wider than Eisenstein's Zulus at every level (amonookuofi1982 Fig. 5 p. 230).
- bonczar2024's pool is Asian-weighted and has no analysis by age, weight or height (bonczar2024 p. 10).

## 3. Inference: recommended error and size terms

Everything in this section is Inference: arithmetic of mine on the figures above, with its inputs named.

### 3.1 The pieces of a mask's error

For a CT mask, sigma_err has three random parts, added in quadrature:

1. The equivalent of an observer: placing the plane and the landmark. The set's manual CT figures are:
   - duman2026 SEmeas 0.3-0.65 mm for heights and 0.2-0.55 mm for pedicles;
   - griffith2016 0.4-1.2 mm;
   - shin2024 0.5-0.8 mm;
   - the vanderhouwen2009 CT-caliper SD of 0.66 mm;
   - about 1 mm in moncadahabib2025.
2. Voxel quantisation. A boundary placed uniformly within a voxel of width v has an SD of v / sqrt(12) = 0.29 v, so a length between two boundaries has sqrt(2) x 0.29 v = 0.41 v. That is 0.41 mm at v = 1 mm, 1.02 mm at a 2.5 mm slice spacing and 2.04 mm at 5 mm.
3. Partial volume on thin cortex. The set gives about +/-0.5 mm per wall at 0.5-0.6 mm voxels (otsuki2021 note), and 10-20% of a 5-7 mm pedicle width at 1 mm voxels (hou1993 note).

Definition offsets against Panjabi's tables (1.7) are systematic, run to 2-8 mm, and are not part of sigma_err. They belong in the measure's mean, estimated where the set gives them. Otherwise they must be named as a known gap, never folded silently into sigma. Panjabi's own measurement error already sits inside his printed spread (1.8).

### 3.2 Recommended sigma_err for CT masks, per family

| Family (schwingcheck measures) | Arithmetic | Recommended sigma_err |
|---|---|---|
| End-plate width and depth (endplate, endplate_lower, endplate_depth, endplate_lower_depth) at v <= 1 mm | sqrt(0.66^2 + 0.41^2) = sqrt(0.436 + 0.168) = 0.78 mm, from vanderhouwen2009's SD and quantisation; with griffith2016's upper 1.2 mm, sqrt(1.44 + 0.168) = 1.27 mm | 1.0 mm; keep LENGTH_ERROR_MM, bracket 0.8-1.3 |
| Posterior body height (h_post), along the scanner's z axis | sqrt(0.65^2 + (0.41 dz)^2), with 0.65 the top of duman2026's SEmeas. dz = 1 mm: 0.77; dz = 2.5: sqrt(0.423 + 1.051) = 1.21; dz = 5: sqrt(0.423 + 4.20) = 2.15 | sqrt(0.65^2 + (0.41 dz)^2), and at least 1 mm; dz is the slice spacing |
| Canal width and depth (canal_w, canal_ap) | the same parts as the end plate, about 0.8-1.3 mm. busscher2010's canal depth is its least reliable measure (intra 0.83). At 1 mm the error is 4-7% of a 14-19 mm canal depth against 2-3% of a 35-50 mm end plate | 1.0 mm; expect the canal to separate levels less well than the end plate relative to its size |
| Pedicle width (pedicle_w:mean) | sqrt(0.55^2 + 0.41^2 + 0.71^2) = sqrt(0.303 + 0.168 + 0.504) = 0.99 mm. The parts are duman2026's top SEmeas, quantisation at 1 mm and two walls at 0.5 mm each (sqrt(2) x 0.5). They may overlap, so this is an upper middle. hou1993's 10-20% of 5-7 mm is 0.5-1.4 mm | 1.0 mm in absolute terms, which is 14-20% of a 5-7 mm thoracic pedicle. Do not halve it for the mean of the two sides: the threshold errors of the two sides are likely correlated, and the set does not measure that correlation |
| Pedicle height (pedicle_h:mean), mostly along z | sqrt(0.55^2 + (0.41 dz)^2 + 0.71^2). dz = 1: 0.99; dz = 2.5: sqrt(0.303 + 1.051 + 0.504) = 1.36 mm. arockiaraj2025's bound is +/-1.25 mm at 2.5 mm | 1.0-1.4 mm, by slice spacing |
| Spinous length and transverse width (spinous_length, transverse_width), 68-92 mm in the lumbar spine (panjabi1992 p. 302) | No CT figure in the set. Two bounds bracket a proportional term c x L: tan2004's calibration (1.28% at 20 mm) and Panjabi's 5%. c = 0.013: sqrt(1 + (0.013 x 68..92)^2) = sqrt(1 + 0.88^2..1.20^2) = 1.33-1.56 mm. c = 0.05: sqrt(1 + 3.4^2..4.6^2) = 3.5-4.7 mm | sqrt(1^2 + (c L)^2) with c not known. Run the build-up study at c = 0.013 and c = 0.05 rather than choosing |
| Facet and interfacet lengths (facet_w/h, interfacet_w/h) | panjabi1993f's 5% of 10-17 mm is 0.5-0.9 mm (panjabi1993f note). masharawi2021's pooled ICC 0.85-1 gives no mm figure | 1.0 mm. The C4 interfacet height spread (SE 3.6/3.3) is probably one outlier, not error (panjabi1993f note) |
| Areas (endplate_area, endplate_lower_area, canal_area, pedicle_area, facet areas) | sqrt(pi A / 2). For canal CSA of 263-279 mm2 (griffith2016 Table 2 p. 675) it gives 20.3-20.9 mm2, inside griffith2016's SEmeas of 10-30 mm2. For tang2016's disc and end-plate CSA of 1,171-1,808 mm2 (tang2016 Table 4 p. 4120) it gives 42.9-53.3 mm2, against the 40 mm2 SEmeas between observers | keep sqrt(pi A / 2). Compute areas by tracing, not as an ellipse of width and depth, which runs up to 10% over Panjabi's digitised end-plate areas, 10-30% over his canal areas and 85-93% over his L4-L5 pedicle areas (panjabi1992 p. 305; note). Inference: 10% of an area A against sqrt(pi A / 2) is 1.9 sigma at A = 600 mm2 and 2.9 sigma at 1,290 mm2, Panjabi's lower lumbar end-plate area as tang2016 lists it (tang2016 Table 6 p. 4125). tang2016 files Panjabi's areas under ellipse estimates (tang2016 Fig. 8 p. 4128), while Panjabi digitised points around each surface and set the ellipse against that area (panjabi1992 p. 299, p. 305) |
| Angles (endplate_incl, pedicle_incl_*, facet_*) | duman2026 SEmeas 0.7-1.8 deg (long pedicle axis); panjabi1993f bound 1.5-3 deg; moncadahabib2025 about 1 deg. A mask point quantised at 1 mm gives sqrt(2) x 0.29 / 27 rad = 0.87 deg on a 27 mm line. A near-flat concavity angle moves 6-8 deg per mm (chen2011 note) | 3 deg is conservative for angles from planes fitted to many voxels and fair for landmark-defined angles. Between-study offsets in pedicle angles reach 14 deg at T12 (panjabi1991t Table 8 pp. 899-900). Treat the lumbar facet sagittal angles (SE 2.9-9.2 deg, spreads of 10-32 deg) as weak (panjabi1993f note) |
| Disc heights, outside the 32 | sqrt(0.76^2 + (0.41 dz)^2), from shin2024's top error SD and quantisation along z. dz = 1: 0.86; dz = 2.5: 1.27 mm | about one slice spacing on routine series (bach2019 note) |

What follows for schwingcheck: its flat 1 mm is right in order for in-plane body and canal lengths on thin CT. It understates three groups:

- heights along z on thick series;
- the long posterior lengths, if the 5% bound holds;
- small pedicles, in relative terms, which is also where the generator's floor binds (README).

Where a row gives a bracket, set the rule's error at its upper end (section 0: an error set too small breaks the answers at 0.99, one set too large costs only share named).

### 3.3 Recommended sigma_err for radiographs, per family

A film value carries four terms: reading, parallax, magnification and the radiographic definition.

| Term | Source | Value |
|---|---|---|
| Reading | hinck1966 p. 142; gilad1985 p. 119 | SD about 0.27 mm (hinck1966, heavy tail); calipers under +/-0.5 mm (gilad1985) |
| Parallax and projection | gilad1985 p. 119; hinck1966 p. 148; ahn2001 p. 67 | at most +/-1.0 mm (gilad1985). AP against PA gives a mean shift of 0.57 mm (hinck1966). Rotation over 20 deg of scoliosis changes the IPD (ahn2001) |
| Magnification | section 1.4 | uncorrected 1.07-1.23 at 100-110 cm; a C-arm is not covered |
| Definition | section 1.3 | measure- and level-specific offsets |

- Random part for well-edged lengths (IPD, body width on AP, body depth on lateral), in film millimetres:
  - Take the reading as SD 0.27 mm and the parallax as uniform within +/-1 mm (SD 0.58): sqrt(0.27^2 + 0.58^2) = sqrt(0.073 + 0.336) = 0.64 mm.
  - Take the reading as SD 0.5 and the parallax as SD 1.0: sqrt(0.25 + 1.0) = 1.12 mm.
  - Recommend 1.0 mm before magnification.
- Superimposed or low-contrast structures carry larger error than the above:
  - pedicle height on the lateral;
  - the posterior disc (PDH intra 17-26% and films 15% less reproducible; kunkel2011 p. 380);
  - the canal depth on the lateral.

  Their random part is not measured in the set. Recommend at least 1.5 mm until it is, and do not use PDH from film for level naming.
- Systematic offsets to put into the mean, radiograph minus true. Each holds only for its own set-up:
  - pedicle width: 0 to -0.6 mm at L1-L4 and -3.5 mm at L5;
  - pedicle height: +1.5 to +1.8 mm at L1-L3, +0.2 mm at L4 and -2.4 mm at L5;
  - transverse angle: 0 to +7 deg (olsewski1990 Table II p. 544);
  - lateral sagittal pedicle angle: -3.4 to -6.1 deg;
  - lateral craniocaudal interpedicular distance: +3.0 to +5.7 mm (mitra2002 p. 455);
  - ADH about -9% and PDH about -37% on thoracic films (kunkel2011 Table 1 p. 378);
  - the dense pedicle ring 1-3 mm inside the true cortex per border (robertson2000 pp. 711-712);
  - posterior body height on a cervical lateral 2-2.5 mm above the midsagittal value (panjabi1991c p. 868).

  The two pedicle-width sources disagree:

  | Source | Material and method | Pedicle width on film |
  |---|---|---|
  | olsewski1990 | 21 disarticulated spines, caliper against film | within 0.6 mm at L1-L4 |
  | robertson2000 | 10 specimens, wire on the cortex | the ring 1-3 mm inside per border, so short by up to about 2-6 mm (robertson2000 note) |

  Take the offset from the set-up that matches the clinic's.
- Angles: sagittal end-plate angles agree on film to 0.1 deg in the mean (panjabi1991t p. 890), and olsewski1990's sagittal pedicle angles agree within about 1 deg (olsewski1990 Table II p. 544). Keep 3 deg for sagittal angles. The set gives no basis for transverse angles read from AP films, whose offset reaches +7 deg.
- Areas: the set holds no radiographic area study. tang2016's ellipse from lateral depth and AP width comes within about 2-3% of a traced MRI area when the depth is the APD, but it carries the square of the magnification (tang2016 note).

Magnification acts as size. On one film every length at one depth carries the same M, every area M^2 and no angle. An unknown M is therefore indistinguishable from the patient's size factor:

- log s_film = log s + log M.
- Uncorrected AP at 100-110 cm gives log M = 0.068 to 0.157 (M 1.07-1.17 from the hinck1966 note; 1.14 from eisenstein1977). The lateral at 110 cm gives log 1.23 = 0.207.
- If M is unknown within 1.07-1.23, uniform in log, the width is 0.207 - 0.068 = 0.139 and the SD is 0.139 / sqrt(12) = 0.040.
- Recommend shifting the prior mean of log s by the set-up's log M, here about +0.14 when only "100-110 cm" is known. Widen its SD to sqrt(0.07^2 + 0.040^2) = sqrt(0.0049 + 0.0016) = 0.081.
- Lateral and AP films of one patient take separate factors: 1.23 against 1.14 in one set-up (eisenstein1977 p. 175).
- Within one lateral film, depth changes M by about 1.1% per cm (1.4), so anterior and posterior structures are not on one scale.

### 3.4 How the size factor should take height

- Recommend centring beta_height on about 0.55, not 1, with prior SD 0.25: beta_height ~ N(0.55, 0.25^2).
  - Every stature slope in the set is below isometric: the twelve elasticities of 2.3 have mean 0.53, median 0.515 and SD 0.14.
  - The centre is rounded up from 0.53 for the attenuation of correlation slopes.
  - The SD is about twice the spread of the estimates, because no estimate exists for end-plate, body-height or posterior-element lengths.
  - The current N(1, 0.5^2) puts 0.53 just inside one SD, so it does not contradict the set. It centres the size where no data in the set lie.
- The canal should be loaded on the size less than the body. The canal's own elasticities are 0.34-0.75. Within a person, the canal's correlation with the mid-body area is r 0.29 (men) and 0.25 (women) for canal area, 0.44 and 0.37 for canal width and 0.29 and 0.20 for canal depth, against r 0.61 and 0.55 between canal depth and width (griffith2016 Table 1 p. 674, subject L1-L5 means, read on the PDF). abbas2021, italianmri, eisenstein1977 and cizmic2023 each find the canal equal between the sexes, or with women deeper, while the body differs (2.1). A per-family loading lambda_m on log s would carry this: lambda about 1 for body lengths and lower for the canal. The set fixes the canal's lambda only to a range of about 0.3-0.75.
- Disc heights should not be tied to stature within sex: r .000-.050 (shin2024 Table 7 p. 5).
- What knowing height buys:
  - Within-sex height CV is 6.8 / 168.1 = 0.040 and 5.9 / 157.0 = 0.038 (griffith2016 p. 673).
  - With beta 0.53 the height explains 0.53 x 0.04 = 0.021 of log s. The residual is sqrt(0.07^2 - 0.021^2) = sqrt(0.0049 - 0.00044) = 0.067.
  - With beta 1 the residual is sqrt(0.0049 - 0.0016) = 0.057.
  - The README's 0.07 therefore overstates the residual once height is known by only 0.003 to 0.013 in log s. Stature within one sex sharpens the size little. Do not expect height to raise the share named.
- 0.07 itself is plausible as a shared part:
  - Within-sex CVs of body diameters run 6-10% (Panjabi lumbar EPW SD 2.6-4.9 mm; italianmri VBD SD 2.4-2.8 mm on about 27-30 mm).
  - tan2004's body CVs run 3-6%.
  - griffith2016's VB CSA CV is 185.5 / 1,419.3 = 0.13 in area, about 0.065 in length.
  - The set gives no within-person correlation matrix with which to split the shared from the measure-specific part, beyond griffith2016's four pairs of correlations.

### 3.5 How the size factor should take sex

Recommend a sex shift per family on log mean, applied after height. A single sex_size on s cannot fit families whose gaps run from -0.02 (canal depth) to about +0.2 (pedicle width).

How much of the body gap stature explains (griffith2016):

- The heights differ by log(168.1 / 157.0) = 0.068.
- At elasticity 0.53, stature explains 0.53 x 0.068 = 0.036.
- Adjustment for height and weight in fact took the linear-equivalent VB CSA gap from 0.100 to 0.061, a fall of 0.039.
  - Unadjusted: log(1,419.3 / 1,162.9) / 2 = 0.1993 / 2 = 0.100.
  - Adjusted: log(1,370.0 / 1,212.2) / 2 = 0.1224 / 2 = 0.061.
  - The adjusted means are from griffith2016 Table S4.
- So the low elasticity and the observed adjustment agree.

Recommended male-minus-female shifts in log mean, after stature:

| Family | Shift | Arithmetic and source |
|---|---|---|
| Body lengths | +0.06 | griffith2016's adjusted VB CSA in linear units |
| Canal width | +0.04 | log(23.38 / 22.54) = 0.037 |
| Canal depth | about 0 | log(15.50 / 15.87) = -0.024 |
| Pedicle width | +0.09 to +0.19 | yu2015's unadjusted 0.128-0.223 less the 0.036 stature share. yu2015 does not print its sex coefficient (yu2015 note) |
| Pedicle height | +0.04 to +0.06 | 0.073-0.094 less 0.036 |
| Angles | 0 | olsewski1990, duman2026, chen2011, moncadahabib2025 |
| Lamina angles | none recommended | abbas2021 is the only exception, at 2-5 deg |
| Disc heights | level-specific, near 0 at L5/S1 | from log 1.31 = 0.27 for the anterior height at T12/L1 (bach2019 Table 6 p. e113) |

Panjabi's tables are an 8:4 mix of men and women, so centre each shift on the mix:

- For a family's gap delta, a man sits at +delta / 3 and a woman at -2 delta / 3 from Panjabi's mean. The mixture mean is (8 x (+delta / 3) + 4 x (-2 delta / 3)) / 12 = 0.
- For the body's delta of 0.06, that is +0.02 and -0.04.
- Panjabi's men were also older (50.3 against 38.5 y; panjabi1991t Table 1 p. 889).

### 3.6 How the size factor should take population

Recommend no single population scale on s:

- tan2004's factors run from 0.60 (SCA) to 1.05 (cervical SPL), log -0.51 to +0.05.
- Stature explains almost none of them: log(166 / 167.75) x 0.53 = -0.0105 x 0.53 = -0.006 (tan2004 p. 137).
- Its body factors of 0.83-0.91 lie 9-17% below what stature predicts. They are confounded with age (65.7 against 46.3 y), with unreported sex and with another instrument (tan2004 note).
- An SCD factor of 0.62 cannot be size; definition and method must carry most of it.

The busscher2010 check:

- At 182 cm, isometric scaling predicts log(182 / 167.75) = 0.082, or +8.5%. Elasticity 0.53 predicts +4.4%.
- An all-male sample adds delta / 3 above Panjabi's mix, about +0.02 for the body.
- The paper reports a "striking resemblance" for pedicles, canal and transverse processes (busscher2010 p. 1112). That fits a low elasticity for those families, but is no test: the note carries no numbers, n is 6, and the method is CT.

Recommend:

1. Adjust each series for stature, sex and age first, through 3.4, 3.5 and 3.7.
2. Estimate a population term per measure family only from same-method contrasts, which the set has for three families:
   - the canal, 1-2 mm smaller in Africans than in Caucasoids, confounded with age (eisenstein1977);
   - the pedicles, under 1 mm between Caucasians and African Americans (yu2015);
   - the discs, larger in Asians (shin2024).
3. Estimate definition offsets separately, by running one mask pipeline over each population's images. The set cannot separate population from definition anywhere else.

### 3.7 Age and weight hooks

Recommend that the age hooks start small and per family:

| Family | Change per year | Over Panjabi's 46.3 y to tan2004's 65.7 y (19.4 y) |
|---|---|---|
| Mid-body size | 0.06-0.12%. From griffith2016's VB CSA: +1.8 / 1,419.3 = 0.13% (men) and +2.7 / 1,162.9 = 0.23% (women) of area, halved for length | +1.2 to +2.3% |
| Canal width | 0.17% (+0.04 / 23.66) | +3.3% |
| Pedicle width | 0.09-0.14% (+0.008 / 8.52 at L1, +0.026 / 18.33 at L5; yu2015 Table 2 p. 1641 and the L1 and L5 means of the yu2015 note) | +1.8 to +2.7% |
| End-plate concavity | +0.01 mm absolute (vanderhouwen2009) | +0.2 mm |

These changes are an order smaller than the population and definition offsets of 2.4.

Disc height with age: give the bach2019 and twomey1985 directions as two hypotheses. Do not average them, since they come from different populations and methods (2.2).

Weight: PW +0.015 to +0.022 mm per kg, adjusted (yu2015 Table 2 p. 1641). That is 0.15-0.22 mm, or about 0.8-2.5% of the L1-L5 widths, per 10 kg (Inference: 0.15 / 18.33 and 0.22 / 8.66, the L5 and L2 means of yu2015 Table 5 p. 1645). Leave the other weight hooks at 0: the set has no weight effect on discs or facets beyond shin2024's weak positive r.

### 3.8 What to change in schwingcheck, in order

1. Make the error of a height-like length depend on slice spacing, sqrt(0.65^2 + (0.41 dz)^2). Keep 1 mm for in-plane body and canal lengths, and keep sqrt(pi A / 2) for areas. Where the set gives only a bracket, use its upper end.
2. Run the build-up study with the long posterior lengths at c = 0.013 and c = 0.05. The set does not settle that term.
3. Lower the centre of beta_height to about 0.55 (SD 0.25), and give the canal a smaller loading on the size than the body.
4. Replace the single sex_size with shifts per family (3.5), centred on Panjabi's 8:4 mix.
5. For radiographs, add a reading sigma of about 1 mm, the measure- and level-specific offsets of 3.3, and the magnification as a shift and widening of log s (+0.14, SD 0.081). Read transverse angles and the posterior disc from film as weak or not at all.
6. Keep population terms per family and estimate them only after adjustment; never apply tan2004's factors as one scale.

## 4. What the set cannot tell

- No per-measure error in millimetres for human CT on most of schwingcheck's 32 measures. The spinous and transverse lengths, the facet sizes and angles, the interfacet distances and the end-plate areas have only pooled ICCs (abbas2021, masharawi2021) or a phantom bound (Panjabi).
- No reliability of any automated segmentation mask, SPINEPS or other, against manual reading or against bone.
- No paired MRI against CT measurement of the same vertebrae.
- No fluoroscopy: no C-arm magnification, image-intensifier distortion or obliquity figure.
- No measurement of one of Panjabi's spines, so neither his observer error nor any regression on his specimens' height, sex or age can be estimated.
- No regression on stature for end-plate width or depth, body heights, the spinous and transverse processes or the facets.
- No sex coefficient after stature for the pedicles (yu2015 does not print it).
- No within-person correlation matrix across measures and levels, beyond griffith2016's four correlations of subject means.
- No correlation between the error on the left and on the right side.
- No separation of population from definition, age and instrument in any between-study comparison.
- No test of the owner's expectations that weight compresses the discs or that age changes facet articulation.
- No partial-volume study of mask thresholds beyond otsuki2021's micro-CT cortex and bach2019's single HU threshold.
- No measurement error for transitional or anomalous vertebrae.
- No reliability for the degeneration grades that would serve as covariates: osteophytosis is graded subjectively (eisenstein1977 p. 179), facet arthrosis by agreement with no kappa (masharawi2021 p. 3), and the Rolander grade with no error at all (twomey1985 note).
- No paired study of one population measured by two definitions or two methods, so every population row of 2.4 carries method and definition with it.
- Thin coverage outside the lumbar spine:
  - thoracic: kunkel2011, panjabi1991t, zindrick1987, busscher2010, lien2007, duman2026 at the thoracolumbar junction;
  - cervical: gilad1985, panjabi1991c, tan2004, busscher2010.
