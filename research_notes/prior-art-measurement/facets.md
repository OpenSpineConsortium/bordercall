# Prior art for the facet family: facet dimensions, orientation, tropism and joint space

Source: the thread "Plan clinical reread next steps", 2026-10-29, web reading (WebSearch and WebFetch from the
cloud container). Family: the 21 facet keys of bordercall's vocabulary.csv (rows 34 to 50 and 93 to 96):
facet_w_sup, facet_w_inf, facet_h_sup, facet_h_inf, facet_area_sup, facet_area_inf, interfacet_w_sup,
interfacet_w_inf, interfacet_h, facet_trans_sup, facet_trans_inf, facet_sag_sup, facet_sag_inf, facet_card_x_sup,
facet_card_x_inf, facet_card_y_sup, facet_card_y_inf, facet_angle_axial, facet_angle_sagittal, facet_tropism,
facet_gap. The first 17 are Panjabi's (the facets paper, Spine 1993;18(10):1298-1310); the last four are the
clinical names that the literature uses for the same quantities (axial and sagittal facet orientation, the
left-right difference, and the joint space width).

Reading status of every claim: [full] the whole page or PMC article was read; [abstract] only the abstract or an
indexing record; [page] a repository, dataset or project page; [code] a code repository. Publisher pages at
Wiley, Ovid/LWW, Springer, ScienceDirect and MDPI answered 403, so each such paper was read on PMC, arXiv, a
university record or a GitHub page, named in each row. No PDF, image or dataset was downloaded.

Reviewed on 2026-10-30 (thread "Finish the clinical reread", project symphony_5): a second reader checked 170
claims at their sources and found 11 wrong, unsupported or imprecise, none of them a number in the Table; a refuter
held all 11, which are corrected here. The record is [review/](review/README.md).

## What the existing notes already say

- morphometry-beyond-the-42-papers.md, "What the rule takes from the papers": the facets paper is the one
  paper outside the 42 that the build-up study's 32-measure pool draws on; it measured the same twelve boiled
  cadaver spines (8 men, 4 women, 19 to 59) as the cervical, thoracic and lumbar papers, and it was not checked
  against its page images for that note. Its table "Panjabi's printed tables are what was measured" records one
  facet misprint: at T1 the left superior facet's X-card angle is printed -47.7 degrees where the transverse-plane
  angle, which the rule scores in its place, makes it -57.7. So the rule already uses facet_trans_* rather than
  the card angles where the two disagree.
- The same note's "Published summaries" table lists Masharawi 2008 (240 people, T1 to L5, body shape) as read in
  abstract only; this note adds the same group's facet papers (2004, 2005), from the same Hamann-Todd columns.
- benchmarks-to-beat.md, public-spine-and-pelvis-models-to-benchmark.md and the four notes under "Vertebra
  measures without masks" contain no facet, tropism or zygapophyseal term (grep, 2026-10-29). The facet family
  is therefore new ground for the lab's notes; nothing below repeats them.

## What was found

### Classical measurement of the family (cadaver bone, digitiser or CT, by hand)

- Panjabi 1993 [abstract, read on qxmd and an indexing record; the full text is in bordercall's archive]:
  276 vertebrae C2 to L5 of 12 spines; linear, angular and area dimensions of superior and inferior facets as
  means and SEM; facet area from C3 to L5 72.3 to 211.9 mm2; X-card angles 41.0 to 86.0 and Y-card angles 5.8 to
  66.1 degrees; card angles introduced as "a new concept". This is the whole source of the first 17 keys.
- Masharawi 2004, Spine 29(16):1755-1763 [abstract, University of Haifa record]: 240 Hamann-Todd columns,
  4,080 vertebrae T1 to L5, Microscribe 3-D digitiser, transverse and longitudinal facet angles. T1 to T11 sit
  about 25 to 30 degrees from the frontal plane; T12 to L2 means 25.89 to 33.87 degrees, "closer to the
  midsagittal plane"; L3 to L5 means 40.40 to 56.30 degrees; longitudinal angle from about 150 degrees at T1 to
  about 170 at L5; orientation independent of sex, age and ethnic group; at the thoracolumbar junction about 80
  percent of specimens show about 101 degrees and about 20 percent about 35 degrees (the abstract's numbers; the
  two conventions it mixes are not explained there). This is the largest per-level facet orientation table in
  the literature, in people, and it is exactly the level dependence a naming rule would use.
- Masharawi 2005, Spine 30(11):E281-E292 [abstract, PubMed 15928537]: facet width, length, width/length ratio and
  interfacet distances of 240 Hamann-Todd spines, 4,080 vertebrae T1 to L5, aged 20 to 80, Microscribe 3-D
  digitiser; tropism is a normal characteristic that varies along the column, the left facet longer in the thorax
  and the right in the lumbar spine; facet length similar at all thoracic levels and rising sharply through the
  lumbar; the interarticular area inverted trapezoidal at T1-T2, rectangular at T3-L3, trapezoidal at L4-L5; facet
  size larger in men, with an ethnic component, independent of age, correlated with height and weight; the abstract
  gives no value in mm.
- Masharawi 2008 (growth), Spine 33(8):898-902, facet asymmetry in normal vertebral growth [abstract, PubMed
  18404110]: 32 children's skeletons aged 4 to 17 (Hamann-Todd), T1 to L5, 3-D digitiser; facet length, width,
  concavity, convexity, lateral interfacet height, transverse and sagittal angles; asymmetry only in the thoracic
  superior facets (right shorter at every level T1 to T12, by up to 2.91 mm at T1; right wider at T1 to T9, T8
  excluded, P < 0.003; right transverse and sagittal angles larger at T1 to T11, P < 0.003), none in the lumbar
  facets, independent of age.
- Kunkel, Schmidt, Wilke 2011, J Anat [full, PMC3042753]: no new bone; third-order polynomials predicting 20 facet
  parameters of T1 to L4 from the posterior body height, fitted to Panjabi's 1991 to 1993 tables; sagittal angle
  errors that the discussion puts at up to -15 percent at the thoracolumbar junction (T12 to L1), where the
  thoracic facets are "frontally oriented" and the lumbar "sagittally oriented", while the results give the
  inferior sagittal angles a mean error of about 27 percent at T11 and 5 to 20 percent in the lumbar spine, and the
  superior ones under 4 percent thoracic and -0.6 to -9.3 percent lumbar. It is the one published attempt to get
  the facet family from a measure a radiograph gives, and it rests on the same twelve spines.
- Van Schaik 1997, Spine 22(5):531-536 [abstract]: the "facet orientation circle", a transverse-plane CT
  parameter; 212 lower lumbar levels of 123 patients; mean circle diameters 43.7 mm at L3-L4, 63.8 at L4-L5,
  82.3 at L5-S1; intra-observer variability 2.3 percent; no inter-observer figure; no data.
- Simon 2012, Spine 37(12):1058-1064 [full, PMC3685171]: facet joint space width (facet_gap) in 3-D from
  1.0 mm lumbar CT, 96 volunteers (62 asymptomatic, 34 symptomatic, 22 to 59), 1,920 facet surface models L1/L2
  to L5/S1; surfaces traced by hand on axial slices with a tablet digitiser, the least distance to the opposing
  surface computed by a custom program; central zone 1.93 +/- 0.51 mm, superior 1.75 +/- 0.48, inferior
  1.63 +/- 0.49, lateral 1.65 +/- 0.48, medial 1.48 +/- 0.44; men wider than women, symptomatic narrower; no
  reproducibility, no code, no data.
- Cahill, Radcliffe, Reitman 2017, Int J Spine Surg 11(5):36 [full, PMC5779274]: 30 trauma CTs with no documented
  cervical injury, 22 measurements per subaxial cervical level, all made by the primary author in Microview,
  cortical edge to cortical edge; among them sagittal facet joint height at the anterior, middle and posterior
  positions, means 0.87, 1.15 and 0.68 mm, upper limits of normal (mean + 2 SD) 1.54, 2.0 and 1.27 mm; inter- and
  intra-rater reliability never tested; no data availability statement.

### Automatic measurement of the family (the only direct hits)

- Semiautomatic facet tropism from lumbar MRI, Northern Finland Birth Cohort 1966, Spine 2024
  [full, PMC10997184; the article is CC BY 4.0]: T2 axial MRI at L3/4, L4/5 and L5/S1 of 1,288 participants;
  UNet++ with an EfficientNet-B6 encoder segments vertebral body, facet joints and posterior arch on a 512 x 512
  slice; 370 training and 60 test participants, one resident's annotations as truth, two further raters on the
  60; facet angle per side between the line joining the anterior and posterior ends of the facet mask and the
  line from the body's centre of mass to the posterior end of the arch mask; tropism = left minus right. Test
  Dice 0.933 overall, but inter-rater Dice on the facet joints alone 75.5 (vertebral body 96.4, arch 85.8) and
  intra-rater 82.5. No angle error in degrees or ICC is given; 76.8 percent of the two radiologists' differences
  fall under 10 degrees, 68.3 and 66.6 percent against the third rater; r2 0.84 for asymmetry between the
  radiologists. Thresholds 7 and 10 degrees; mean asymmetry 7.1 degrees in men, 6.3 in women; L4/5 most affected
  (44.6 percent of men over 7 degrees). The slice per level is chosen by hand, so it is semiautomatic. No code
  or data availability statement in the article; the images are the NFBC1966 cohort's (12,231 participants born in
  1966; 1,540 had lumbar MRI at Oulu University Hospital, 2011 to 2015), and the article gives no access terms
  for them [full, PMC10997184]. This is the only published automatic measurement of
  facet_angle_axial and facet_tropism found, on any modality.
- Wang 2025, JOR Spine 8(3):e70115, facet joint osteoarthritis on lumbar CT [full, PMC12424607]: 1,360 patients
  with low back pain from two hospitals (1,132 internal, 228 external), 13,223 axial facet patches L1/2 to L5/S1
  (7,430 train, 2,000 validation, 1,890 internal test, 1,903 external test); stage 1 nnU-Net segments the two
  facet joint regions on the chosen axial slice, Dice 0.81 (0.77 to 0.84); stage 2 ResNet-18 with five heads
  grades Weishaupt's features. Joint space narrowing is a binary call at 2 mm (internal accuracy 89.8 percent,
  kappa 0.82; external 76.6 percent, kappa 0.57); osteophytes 79.6/80.2 percent; hypertrophy 65.5/56.0 percent;
  erosions 88.0/89.6; cysts 82.8/89.8. Inter-reader Gwet kappa 0.81 internal and 0.71 external. No width in mm,
  no orientation; slices chosen by hand. Data on request; code at github.com/DRhattaneee/FacetJoint [code]: one
  file FacetJoint_Model.py, no README, no licence, no weights.
- Nikpasand 2024, JOR Spine 7(3), automated Pfirrmann and Fujiwara grading on lumbar MRI [full, PMC11249006]:
  the public Lumbar Spine MRI Dataset (Sudirman, Mendeley k57fr854j2; 515 symptomatic patients, axial 4 mm
  slices, 0.6875 mm pixels [page]); 2,377 facet images (2,135 train, 242 test), both sides, L1-L2 to L5-S1, T1
  axial; a small CNN on 32 x 32 patches; truth one musculoskeletal radiologist, five graders in all whose Fleiss
  kappa for Fujiwara averaged 0.13 (0.04 to 0.19), 40 percent agreement; model 49 percent agreement with the
  lead grader, r 0.3, kappa 0.18. Code and outputs on DRUM, hdl.handle.net/11299/264061, CC BY-NC-ND 4.0
  [page]. Grades only; no angle, no width.
- Wu 2024, Diagnostics 14(7):755, facet joints in ultrasound [full, PMC11011346]: 300 patients, 420 images
  (356 train, 35 test), Mask R-CNN with ResNet-101 FPN, AP50 90.4 percent detection and 85.0 percent
  segmentation in the abstract (98.57 and 90.75 in its tables, inconsistent); two anaesthetists annotated;
  no level given; data and code on reasonable request; no measurement.

### Segmentation of the articular processes (the step a 3-D measurement would start from)

- SPINEPS, Moller and others, arXiv 2402.16368 [full on ar5iv; code page]: sagittal T2 MRI (and since the
  2025 releases CT, with separate models) into 14 structures, among them Superior_Articular_Left (45), Right
  (46), Inferior_Articular_Left (47), Right (48), Arcus (41), Spinosus (42), Costal (43, 44). The substructure
  labels were made by translating T2 images into artificial CTs and segmenting those with the Bonescreen SpineR
  tool; the manually corrected test set is 11 NAKO subjects. Dice on the articular processes: superior 0.683
  cervical, 0.813 thoracic, 0.787 lumbar, 0.762 overall; inferior 0.714, 0.827, 0.823, 0.790 overall; the paper
  says the cervical substructures are very hard to tell apart on sagittal T2. Code and weights Apache-2.0 at
  github.com/Hendrik-code/spineps; outputs are masks and centroids, no angle or width. This matters because the
  lab's census masks are SPINEPS masks, so every facet key could be read from the masks already held, and the
  Dice above bounds how well.
- Da Mutten and others 2026, J Imaging Inform Med, doi 10.1007/s10278-026-02169-7 [abstract, PubMed 42573685]:
  118 thoracolumbar CTs segmented by hand into seven subregions (body, lamina, pedicle, superior and inferior
  articular process, transverse and spinous process); nnU-Net, ResEnc nnU-Net, SwinUNETR and Blomenkamp's
  geometric method compared; external-validation Dice of standard nnU-Net 0.985 +/- 0.034 superior and
  0.980 +/- 0.046 inferior articular process (the geometric method 0.382 to 0.889). Source of the CTs,
  annotators, external set and data or code availability not in the abstract.
- SpineToolkit, VisSim-UniKO [code page] and SLD, Blomenkamp and others, arXiv 2601.16782 [full]: a 3D
  Slicer extension whose ShapeSegmentation module splits a vertebra mesh by rules (clustering, extreme points,
  skeleton curves) into body, laminae, transverse processes, articular processes and spinous process; the
  ligament landmarks built on it (SLD, arXiv 2601.16782 [full]) reach MAE 0.7 mm and RMSE 1.1 mm on VerSe, the
  artificial Sawbone set and Al-Dhamari 2019's cervical set, 57 vertebral surface models with ligament sites
  annotated by hand, the capsular-ligament points on the facet surfaces at MAE 1.0 mm and RMSE 1.6; licence not
  stated on the page; no facet measurement. The same group's 3D vertebrae measurements paper, Kramer 2024, arXiv
  2402.01462 [full, arxiv.org/html/2402.01462], measures the vertebral body alone (superior and inferior end-plate
  widths and depths; anterior, central, posterior, left and right heights) on 6 VerSe patients (L2, L3, T4 and T5,
  three raters in 3D Slicer) and 50 artificial Sawbone lumbar spines: MAE 1.09 mm on the patient meshes in the
  abstract, an average deviation of 1.32 mm lumbar in the results text (1.32 is also the table's lumbar anterior
  height cell), and 0.7 mm on the artificial spines; no facet measure; code and the artificial spine set at
  github.com/VisSim-UniKO/Spine-Morphology-Analyzer, its licence not read here.
- LSMA-PQR, Mendeley p3r4xd2488 [page], CC BY 4.0: the same 515 Sudirman patients, 3,090 axial and 1,030
  sagittal images at 384 x 384, axial labels for disc, "posterior elements" and canal at L3-L4 to L5-S1,
  Pfirrmann grades and disc heights; the posterior-elements class is not split into facets.

### Public datasets checked for facet truth

- VerSe 2019/2020, TotalSegmentator, CTSpine1K, SPIDER, MRSpineSeg, BUU-LSPINE, NHANES II films, AASCE and
  SpineWeb [page or abstract for each as the earlier notes read them, plus searches here]: whole-vertebra
  masks, centroids or landmarks only; none carries a facet label, a facet angle or a joint space width. The
  SPIDER paper notes that its vertebra masks include the arch "in its entirety", with facet arthrosis as one
  reason, but gives no facet class.
- IMBE-SPINES-DATASET, University of Leeds, doi 10.5518/1835 [page, readme-collection and spine4 readme],
  CC BY 4.0, published 2026: high-resolution CT (XtremeCT, 50 or 82 micron isotropic voxels, 3 to 12 GB per
  zip) and MR of 5 cadaver spines, 11 lumbar specimens (for instance donor 4, male 92, L1-L2, L3-L4, L5-S1) with
  Weishaupt facet grades per side (grade 2 at L3-L4, 3 at L5-S1 for that donor); no masks, no angle, no width.
  It is the one public CT set with any facet truth, and the truth is a grade.
- A Hugging Face mirror of the Sudirman data (Nikpasand's source) and its radiologist notes (Mendeley s6bgczr8s2,
  version 2, CC BY 4.0) [page]: the notes' page lists facet joint and ligamentum flavum hypertrophy among the
  conditions recorded, with no facet label, angle or width described; the mirror itself was not re-read for this
  check.

## Table

| Method | Dataset (public? size, modality, truth) | Code (public? licence) | Accuracy (vs what truth) | Lacks for naming levels |
|---|---|---|---|---|
| Panjabi 1993 [abstract] | No. 12 cadaver spines, 276 vertebrae C2 to L5, electromechanical morphometer; means and SEM | No | Means only; no error | 12 people, no per-person data, 1990 bone, no CT or film |
| Masharawi 2004 [abstract] | No digital set; 240 Hamann-Todd columns, 4,080 vertebrae T1 to L5, 3-D digitiser | No | Means per level; junction bimodal (80/20) | Dry bone, no images, no cervical, no transitional vertebrae stated |
| Masharawi 2005 [abstract] | No digital set; same 240 Hamann-Todd columns, 4,080 vertebrae T1 to L5; facet width, length, ratio and interfacet distances | No | Tropism side by region and interfacet shape by level; no mm in the abstract | Dry bone, no images, thoracolumbar only |
| Kunkel 2011 [full] | None new; regressions on Panjabi's tables, T1 to L4 | No (equations printed) | Sagittal angle error up to -15 percent at T12-L1 (discussion); inferior sagittal about 27 percent at T11 and 5 to 20 percent lumbar (results) | Rests on 12 spines; L5 excluded; predicts from a body height, so no new information for a rule that already has the heights |
| Van Schaik 1997 [abstract] | No. 123 patients, 212 lower lumbar levels, CT | No | Intra-observer 2.3 percent | L3-L4 to L5-S1 only, one plane, a diameter rather than an angle |
| Simon 2012 [full] | No. 96 volunteers, 1,920 facet models L1/L2 to L5/S1, 1.0 mm CT, hand-traced surfaces | No (custom program) | Zone means 1.48 to 1.93 mm; no reproducibility | Lumbar only, manual tracing, no level labels, osteophytes excluded by hand |
| Cahill 2017 [full] | No. 30 trauma CTs, subaxial cervical, 22 measures per level | No | Upper limits 1.27 to 2.0 mm (mean + 2 SD) | Cervical only, 30 people, normative limits not measurements per vertebra |
| NFBC1966 facet tropism, Spine 2024 [full] | No (no availability statement). 1,288 participants, T2 axial MRI L3/4 to L5/S1; 430 annotated, 60 test by 3 raters | No | Dice 0.933 overall; facet inter-rater Dice 75.5; 76.8 percent of radiologist pairs within 10 degrees; no degree error | Three lumbar levels, axial MRI, slice chosen by hand, no level labels, no transitional vertebrae, one centre, one rater's truth |
| Wang 2025 CT facet OA [full] | On request. 1,360 patients, 13,223 axial CT patches L1/2 to L5/S1, two hospitals; two readers plus adjudicator, Gwet kappa 0.81/0.71 | Yes, github DRhattaneee/FacetJoint, one file, no licence, no weights | Segmentation Dice 0.81; narrowing accuracy 89.8/76.6 percent, kappa 0.82/0.57 | Grades, not mm or degrees; 2-D slices chosen by hand; lumbar only; no level naming |
| Nikpasand 2024 MRI grading [full] | Yes, Sudirman Lumbar Spine MRI Dataset (515 patients); 2,377 facet images, 242 test; 5 graders, Fleiss kappa 0.13 | Yes, DRUM 11299/264061, CC BY-NC-ND 4.0 | 49 percent agreement, kappa 0.18 with lead grader | Grades only; truth itself at slight agreement; lumbar, axial MRI; no measure |
| Wu 2024 ultrasound [full] | On request. 300 patients, 420 images, 35 test | On request | AP50 90.4 detection, 85.0 segmentation | Ultrasound, no level, no measure |
| SPINEPS [full, code] | SPIDER public (218); substructure test 11 NAKO subjects, corrected by two experts | Yes, Apache-2.0, weights | Articular process Dice 0.683 to 0.827 by region | Masks only, sagittal T2 (CT model newer and unmeasured here); cervical facets weakest; no angle or width computed |
| Da Mutten 2026 subregions [abstract] | Not stated. 118 thoracolumbar CTs, hand segmented, external set unnamed | Not stated | Dice 0.985 superior, 0.980 inferior articular process (nnU-Net, external) | Thoracolumbar only, no measure, availability unknown |
| SpineToolkit / SLD / Kramer 2024 [code page; full, arXiv 2601.16782 and 2402.01462] | SLD: VerSe, the artificial Sawbone set and Al-Dhamari 2019's cervical set, 57 vertebral surface models with ligament sites annotated by hand; Kramer 2024: 6 VerSe patients (L2, L3, T4, T5) and 50 artificial lumbar spines; meshes | Yes on GitHub (SpineToolkit; Spine-Morphology-Analyzer), licence not stated on the SpineToolkit page, Spine-Morphology-Analyzer's not read | Ligament landmark MAE 0.7 mm, RMSE 1.1 mm (capsular ligament points on the facet surfaces MAE 1.0 mm, RMSE 1.6); body dimensions MAE 1.09 mm (1.32 mm lumbar in the results text) | Rule-based on meshes (needs a segmentation first), no facet angle or area reported |
| LSMA-PQR [page] | Yes, CC BY 4.0; 515 patients, 3,090 axial MRI slices L3-L4 to L5-S1; posterior elements as one class | Labels, no model | None for facets | Facets not separated; three lumbar levels |
| IMBE-SPINES (Leeds) [page] | Yes, CC BY 4.0; 5 spines, 11 lumbar specimens, 50 to 82 micron CT and MR; Weishaupt grades per side | No | None | Grades only, lumbar, cadaver, 5 people |

## What the family's prior art settles and does not

Settled:

- The per-level behaviour of facet orientation is known and large: Masharawi 2004's 4,080 vertebrae give the
  transverse angle at every level T1 to L5, with the thoracic facets near the frontal plane (25 to 30 degrees),
  T12 to L2 nearest the midsagittal plane and L3 to L5 opening to 40 to 56 degrees, and it is independent of
  sex, age and ancestry. That is the strongest level signal in this family, stronger than any body dimension,
  and it holds in people rather than in Panjabi's twelve. But it is dry-bone data, abstract-only here, and it
  carries no digital record, so it can be a prior, not a benchmark.
- The thoracolumbar junction is bimodal in facet orientation (about 80 percent of columns at one orientation,
  20 at the other, Masharawi 2004; abrupt at T12-L1 or gradual over T11-L1 in near-equal shares in the
  510-vertebra study the search surfaced [abstract only, source page not readable]). A naming rule that reads
  T12 versus L1 from the facet angle will meet that split, and Kunkel 2011's sagittal angle errors there (up to
  -15 percent at T12-L1 in its discussion, about 27 percent at T11 in its results) show it in the only published
  predictor.
- Automatic facet orientation and tropism has been done once, on axial MRI at three lumbar levels, with
  masks whose inter-rater Dice is 75.5 and no angle error in degrees reported (NFBC 2024). Nothing automatic
  exists on CT or on radiographs for any key of the family, and nothing exists for the facet dimensions or
  areas (facet_w_*, facet_h_*, facet_area_*, interfacet_*) or the card angles.
- Facet joint space width has been measured in 3-D from CT once (Simon 2012, 96 people, by hand-traced
  surfaces) with zone means around 1.5 to 1.9 mm, and automatic CT work reads only a binary narrowing at 2 mm
  (Wang 2025). Nobody has validated an automatic facet_gap in mm.
- The articular processes can be segmented: SPINEPS gives them as four labels with Dice 0.68 to 0.83 on
  sagittal T2 and is the lab's own mask source; one 2026 CT study reports Dice 0.98 for them on thoracolumbar
  CT. So the family is computable from masks the lab already holds, with the cervical facets the weakest part.

Not settled:

- No public dataset carries any facet measure as truth: no angle, no area, no width, no interfacet distance.
  The only public truths touching facets are Fujiwara grades at slight agreement (kappa 0.13, Nikpasand) and
  Weishaupt grades on five cadaver spines (Leeds). Any benchmark of the family would have to be built, most
  likely by two readers on held CT.
- No method names a level from a facet measure, and no automatic pipeline covers the cervical facets, the
  whole column or a transitional vertebra. The one automatic tropism paper is lumbar L3/4 to L5/S1.
- Inter-reader agreement on facet angles in degrees is not reported anywhere found; NFBC gives it as a share
  within 10 degrees (76.8 percent between two radiologists), which is coarse beside the 7 and 10 degree tropism
  thresholds themselves.
- Whether the facet angle read from a SPINEPS or nnU-Net mask agrees with a digitiser or a reader is unmeasured.

## Gaps

- Panjabi 1993 was read only as an abstract on the web; the full text is in bordercall's archive and the earlier
  note already records its one known misprint.
- Masharawi 2004 was read as an abstract on a university record, and the 2005 and 2008 (growth) papers as their
  PubMed abstracts in the review of 2026-10-30; Spine (LWW/Ovid) refused. The 2005 paper's abstract gives no value
  in mm.
- Wang 2025 and Nikpasand 2024 were read on PMC, not Wiley; Wu 2024 on PMC, not MDPI; Da Mutten 2026 only on
  PubMed, so its data and code availability are unknown. Kramer 2024 and SLD were read in full on arXiv's HTML in
  the review: Kramer 2024 names its sets (6 VerSe patients, 50 artificial Sawbone lumbar spines) and links its
  code; SLD names VerSe, the artificial Sawbone set and Al-Dhamari 2019's cervical set, 57 vertebral surface
  models in all.
- The 510-vertebra thoracolumbar facet study (360 thoracic, 150 lumbar) was seen only in a search summary and
  its page could not be identified for a fetch; its numbers are not used above beyond the abrupt-or-gradual
  finding.
- Chinese-language literature was searched once (one query) and gave nothing on automatic facet angles; CNKI
  itself was not searched.
- No Grand Challenge or MICCAI task on facets was found; the SPIDER challenge has no facet class.

## Sources (what was read, by link)

- Panjabi 1993 abstract: https://read.qxmd.com/read/8211362/articular-facets-of-the-human-spine-quantitative-three-dimensional-anatomy
- Masharawi 2004: https://cris.haifa.ac.il/en/publications/facet-orientation-in-the-thoracolumbar-spine-three-dimensional-an/
- Masharawi 2005: https://pubmed.ncbi.nlm.nih.gov/15928537/ (record also at https://neomed.omeka.net/items/show/9965)
- Masharawi 2008, facet asymmetry in growth: https://pubmed.ncbi.nlm.nih.gov/18404110/ and https://cris.haifa.ac.il/en/publications/facet-asymmetry-in-normal-vertebral-growth-characterization-and-e/
- Kunkel 2011: https://pmc.ncbi.nlm.nih.gov/articles/PMC3042753
- Van Schaik 1997 record: https://scilit.com/publications/8868c2e0280e4316c53ff62e704c3f58
- Simon 2012: https://pmc.ncbi.nlm.nih.gov/articles/PMC3685171
- Cahill 2017: https://pubmed.ncbi.nlm.nih.gov/29372140/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC5779274/
- NFBC1966 facet tropism, Spine 2024: https://pmc.ncbi.nlm.nih.gov/articles/PMC10997184/
- Wang 2025 CT facet OA: https://pmc.ncbi.nlm.nih.gov/articles/PMC12424607/ and https://github.com/DRhattaneee/FacetJoint
- Nikpasand 2024: https://pmc.ncbi.nlm.nih.gov/articles/PMC11249006 and https://conservancy.umn.edu/items/7c8f5a83-9a02-4dc2-921d-886c0475dcd1
- Sudirman Lumbar Spine MRI Dataset: https://data.mendeley.com/datasets/k57fr854j2 ; LSMA-PQR: https://data.mendeley.com/datasets/p3r4xd2488
- Wu 2024 ultrasound: https://pmc.ncbi.nlm.nih.gov/articles/PMC11011346/
- SPINEPS: https://arxiv.org/abs/2402.16368 (tables on https://ar5iv.labs.arxiv.org/html/2402.16368) and https://github.com/Hendrik-code/spineps
- Da Mutten 2026: https://pubmed.ncbi.nlm.nih.gov/42573685/
- SpineToolkit: https://github.com/VisSim-UniKO/SpineToolkit ; SLD: https://arxiv.org/abs/2601.16782 ; Kramer 2024: https://arxiv.org/abs/2402.01462
- SPIDER: https://arxiv.org/abs/2306.12217 and https://zenodo.org/records/10159224
- IMBE-SPINES-DATASET: https://archive.researchdata.leeds.ac.uk/1619/1/readme-collection.txt and https://archive.researchdata.leeds.ac.uk/1622/4/spine4_readme.txt (doi 10.5518/1835)
