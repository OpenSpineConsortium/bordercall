# Prior art: counts and anomalies (keys rib, sacrum, prevalence)

Source: the thread "Plan clinical reread next steps", 2026-10-29, web reading (arXiv and ar5iv full texts, Europe PMC
full-text XML, GitHub READMEs, Hugging Face and Zenodo pages, the ACR use-case page); the four notes under
bordercall "Vertebra measures without masks" and three SchwingNet notes (docs/research/morphometry-beyond-the-42-papers.md,
benchmarks-to-beat.md, public-spine-and-pelvis-models-to-benchmark.md) read first and cited, with SchwingNet's
full-spine-corpora-with-reader-counted-variants.md, lumbosacral-to-cervical-extrapolation.md, spineps-anomaly-route.md
and ct-priors-for-2d-detection.md, which the first three point at. The vocabulary keys covered are rib ("any rib or
costal measure"), sacrum ("any sacral or pelvic measure") and prevalence ("a count or share of an anomaly, variant or
finding"), read here as: vertebral counting and level labelling, lumbosacral and thoracolumbar transitional vertebrae,
cervical and lumbar ribs, numerical variants, how the public segmentation sets label them, and automatic level
identification on radiographs, CT and MRI. Reading-status tags: [full] the whole text read, [abstract] the abstract
or a metadata page, [page] a web page that is not the paper (dataset card, forum, use case), [code] a repository
README, [notes] taken from one of the existing notes named above, not re-derived. Publisher pages (Springer, MDPI,
Wiley, SAGE, PMC) refused this container, so each closed paper was read from arXiv, ar5iv or Europe PMC's REST
full text, and the tag says which. The web search budget ran out after 17 searches, so the sweeps of items 4 to 7
under Gaps were not run.

Reviewed on 2026-10-30 (thread "Finish the clinical reread", project symphony_5): a second reader checked 262 claims
at their sources and found 15 wrong, unsupported or imprecise; a refuter held 12, of which 11 are corrected here and
one, the README's account of VerSe's hidden L6, in the README, and refuted three (the 3,855-CT series' rounded shares
are its abstract's; the Hofmann quote is on the ResEncL and ResEncM model cards; the RibSeg sentence is its README's,
written for v1). The searches the first sweep could not run were run, and a second sweep added five rows (Yang 2025,
Nakajima 2026, MRSpineSeg, Fang 2025, and Osiowski 2024 with Henry 2018) and a bullet of four more reader-counted
series, each read again at its source by a verifier, who also found the section's Lodz 2026 to be Jankowski 2026. The
record is [review/](review/README.md).

## 1. What the existing notes already settle

- The counting corpora with reader truth are catalogued in full-spine-corpora-with-reader-counted-variants.md
  (sections 1, 2 and 4) [notes]: fourteen cohorts with per-case counts over both junctions, none open; the open
  additions are Hofmann's VertebralBodiesCT-Labels (69 L6 and 14 T13 flags over 1,460 held CTs) and Albano 2020's
  Castellvi table (906 EOS films, images not open). The prevalence figures of this family come from there and from
  morphometry-beyond-the-42-papers.md ("Every spine has 7, 12 and 5 bodies" row; the series table): Yoon 2024 (450
  whole-spine CTs, 6.7 percent not 24 presacral, 23.8 percent with any count or junction atypia, LSTV 26.4 percent,
  TLTV 15.3 percent), Doo 2020 (1,340 CTs, 12 ribs in 91.6 percent, 11 ribs 107, 13 ribs 5, LSTV 8.3 percent), Tins
  2016 (418 MRIs, 8.1 percent one mobile vertebra more or fewer), Paik 2013 (8,280 lumbar MRIs counted from C2, 4
  lumbar 2.6 percent, 6 lumbar 8.2 percent), VERIDAH's NAKO sample (6,291 MRIs, 5.8 percent 11 or 13 thoracic, 9.7
  percent 4 or 6 lumbar), Tatara 2021 (880, LSTV 111 with Castellvi II 28, III 42, IV 4; TLTV 96), Sabri 2025 (3,147
  films, 13 rib-bearing in 28, 11 in 143), Lodz 2026 (499, L6 24, T13 13, 4L 11, 11T 10). The web search here added
  only two more series, a 3,855 consecutive abdominal CT study with LSTV in 29 percent (Castellvi I 68, II 16, III 13,
  IV 3 percent of those) [abstract, PMC7248049 snippet], and a 3,607-adult abdominal radiograph series (Ucar 2013,
  Arthritis 2013:461425, PMID 23864947; 3,607 of 6,200 films eligible) with 683 (18.9 percent) LSTV (sacralisation
  17.2, lumbarisation 1.7 percent) [abstract]; the first sweep found no pooled meta-analysis before its search budget
  ended, and the review of 2026-10-30 found three (rows in section 2): Fang 2025 averages the 20 of its 83 reviewed
  studies that report LSTV prevalence, 4,290 of 28,106 people, about 15.3 percent (range 4.5 to 35.6), declining a
  meta-analysis for heterogeneity, so with no interval and no Castellvi split [full]; Osiowski 2024 pools lumbar ribs
  at 2.1 percent (95 percent CI 1.0 to 4.6; 9 studies, 5,430 people, random effects) [full]; Henry 2018 pools cervical
  ribs at 1.1 percent in healthy people (141 studies, 77,924 participants) [abstract]; no meta-analysis of eleven or
  thirteen rib pairs was found (the reader's Europe PMC search, not rerun).
- Four more reader-counted series, none open (the first bullet's Lodz 2026 is Jankowski 2026, PMC13703058): Forseen 2015
  [abstract] (244 whole-spine CTs: lumbosacral transitional anatomy with eleven ribs in 5 of 7, thirteen 8 of 11,
  twelve 24 of 234, denominators summing to 252 against 244 and differing from its lowest-rib counts of 8, 11 and
  225); Sun 2025 [full, PMC12630705, CC BY] (UK Biobank, 500 non-carriers chosen as controls, counted by hand down
  from C2 on aligned DXA and Dixon MRI, assuming 7 cervical and 12 thoracic: four lumbar 8, 1.6 percent, six lumbar
  16, 3.2, eleven rib pairs 13, 2.6, L1 ribs 10, 2.0; the deep learning there only aligns DXA to MRI, code on GitHub,
  images by UK Biobank access); Duman 2026 [full, PMC13517915, CC BY] (517 thoracic CTs, one radiologist: hypoplastic
  twelfth rib 55, 10.64 percent, absent twelfth 22, 4.26, lumbar rib 12, 2.32, cervical rib 7, 1.35, any 96, 18.57,
  women 23.33 against men 14.44, p 0.013; no count method given, data on request); Zhou 2023 [full, PMC10722060, CC
  BY-NC-ND] (6,097 whole-body PET/CT screened, 450, 7.4 percent by division, with 23 or 25 presacral vertebrae, 211
  and 239, 56 of them with a thoracolumbar transitional vertebra, 29 and 27, excluded; counted from the cervical spine
  by one musculoskeletal radiologist of 3 years, Castellvi read on the transverse processes, no posterior element
  segmented or measured, PACS VR and MPR, inter-reader ICC over 0.8 but STA 0.639 to 0.875, no data statement). Zhou
  2023 and Sun 2025 are already in SchwingNet's full-spine-corpora-with-reader-counted-variants.md, which this section
  cites.
- The level-identification methods that matter for X-ray are tabled in lumbosacral-to-cervical-extrapolation.md
  (section 2) and benchmarks-to-beat.md (section 3) [notes]: LevelCheck (Lo 2015; 20 patients, registration to the
  patient's CT, 100 percent at 25.7 s), De Silva 2016 and Manbachi 2018 (398 radiographs, localisation error 30.4
  percent unassisted against 2.4 percent assisted, most useful where the sacrum or twelfth rib is hidden), Huang 2022
  (render-trained, 88.3 percent labelling on 100 real Long-Film images of 13 cadavers), VertXNet (Chen 2024; counts
  from a detected C2 or S1, NHANES II and PREVENT), Payer 2020, Btrfly 2020, the VerSe challenge, Netherton 2025
  (external, two sites, cervical 69 and 92 percent), VERIDAH, the owner's NeurIPS poster and Kwak 2025 (there cited
  as Lee 2025). Those rows are not repeated below except where this reading added to them.
- On CT labellers the project's own measurement stands (spineps-anomaly-route.md, section 3) [notes]: on VerSe's 319
  scored persons (325 read, 6 disputed and left out), two labellers agreeing (TotalSegmentator's count against
  SPINEPS/VERIDAH's) find 22 of 83 L6 (26.5 percent) and 2 of 6 T13 with 228 of 228 specificity and 22 of 22
  precision; VERIDAH alone finds 36 of 83 L6 but calls T13 on 11 L6 spines (4 of 16 T13 calls right). On
  CTSpinoPelvic1K the two-labeller L6 calls are 7 of 7 right and find 7 of 29.
- FleXray (public-spine-and-pelvis-models-to-benchmark.md, section 1; masks_corners_magnification.md, section 5)
  [notes] has one channel per vertebra C1 to L5 plus the sacrum and ribs 1 to 12 and no L6 or T13 channel; its MOOSE
  dataset spec drops vertebra_l6 to background, so a corner or width pipeline over its masks inherits a missed sixth
  lumbar body. The classical radiograph methods (radiograph_classical_methods.md, "failure classes") name the wrong
  vertebra, off-by-one template matches and L4/L5 start ambiguity as the first failure class and have no anchor for
  which vertebra a body is. The CT intensity methods (ct_intensity_methods.md) partition the column but none counts
  it; Yao 2006's one partition error was a missed T1-T2 level and Radnostics' inferior crop "may" remove L5.

## 2. Methods swept here

Method | Dataset (public? size, modality, truth) | Code (public? licence) | Accuracy (vs what truth) | Lacks for naming levels
---|---|---|---|---
VerSe challenge, Sekuboyina 2021 (Med Image Anal; arXiv 2001.09193) [full, first half] | Public (OSF nqjyw and t98fz; the arXiv page states CC BY-NC-ND for the paper and no data licence; the project's records say CC BY-SA 4.0). 374 CTs of 355 patients, 4,505 vertebrae with voxel masks and centroids. VerSe'19: 160 scans (80/40/40), two training scans with L6 and one hidden L6; VerSe'20: 319 scans (113/103/103), 6 with T13 (2/2/2) and 47 with L6 (15/15/17). L6 is label 25, T13 label 28 | Yes, github.com/anjany/verse (evaluation and content); each team's code its own | Identification rate, hidden test: 2019 Payer 94.25, Lessmann 90.42, Chen M 86.73 (public 96.94, a one-label shift); 2020 Chen D 96.58, Payer 92.82. Per-vertebra curves drop at T13 and L6; "almost every algorithm failed" on the hidden L6 of 2019; in the cross-iteration test Payer and Zhang identified L6 where no 2019 method did | CT only; a single one-label shift is a whole-scan failure; 53 transitional scans in all, 6 of them T13; no rib labels, so the thoracolumbar count rests on the readers' labels; no view, no projection
Payer 2020, SpatialConfiguration-Net plus U-Net (VISAPP) [notes; the scitepress PDF did not render] | VerSe'19, 80 training volumes, three-fold | Yes, github.com/christianpayer/MedicalDataAugmentationTool-VerSe, the code used for VerSe'19, VerSe'20 and the VISAPP paper, GPL-3.0 by its LICENSE file [code]; the VerSe paper links no team's code [full] | Cervical 91.1 (102 of 112), thoracic 89.0 (388 of 436), lumbar 90.4 (284 of 314) percent; lumbar includes L6 | CT; the three regions' intervals overlap; no transitional stratum reported
Lessmann 2019, iterative FCN with memory (Med Image Anal; arXiv 1804.04383) [full] | Five sets: CSI 2014 thoracolumbar CT (15), xVertSeg lumbar CT (15), NLST low-dose chest CT (55, authors' own masks, not released), healthy lumbar CT (10), lumbar MR (23); four of five have public reference masks | Not stated (PyTorch) | Identification 93 percent of CT vertebrae (206 of 222, kappa 0.99), labelling correct in 97 percent of scans overall; on MR every case identified (kappa 1.0); Dice 94.9 percent on CT and 94.4 on MR bodies; visibility 97 percent of CT vertebrae (268 of 275) [full]. The one wrong scan had four lumbar vertebrae and was labelled T2 to L5 instead of T1 to L4 | Label space fixed at C1 to L5 (24), so a four- or six-lumbar spine can only be entirely offset; no training scan had an irregular count, named as future work; no cervical, no implants; CT and MR only
Chen D 2020 and Chen M 2019 (VerSe winners) [abstract, via the VerSe appendix] | VerSe | Chen M: 25 labels, "ignoring the rare L6 label"; Chen D not read | As the VerSe row | A label set with no L6 fails every L6 scan by construction
Yeah T. and others, Dong Y., Angermann C. (VerSe'20 entrants) [abstract, via the VerSe appendix] | VerSe | Not read | Not read separately | The only entrants whose label sets include T13 (Yeah T.: C1-C7, T1-T13, L1-L6; Dong and Angermann: L6 but not T13)
Yang and others, transformer-enhanced vertebrae segmentation and anatomical variation recognition (Sci Rep 2025;15:34329, doi 10.1038/s41598-025-16689-9, PMC12491412, CC BY-NC-ND) [full] | VerSe 2019 and 2020, public, 374 CTs of 355 subjects; classes Normal, T13 and L6, the variant labels derived from VerSe's centroid annotations (outlier labels, uncommon counts), radiologists confirming only the separate shape classes (Normal, Wedge, Fused); the variant test a "hold-out test set of 300 samples" evenly across the three classes, which the paper does not reconcile with VerSe's few T13 scans | The paper names github.com/anjany/verse (the challenge tooling) as its code; custom scripts on request | Mean Dice 0.953 (nnU-Net 0.921, SwinUNet 0.936) over 26 levels C1 to L6, no T13 or L6 Dice in the text; variant classification Normal 87 percent, L6 85, T13 80, AUC 0.95 / 0.96 / 0.93; age and sex fused into the classifier | A class per vertebra patch cut at VerSe's own centroids, not a count or a labelling of the column; the classifier is called binary cross-entropy yet has three classes, the attention map is called simulated, its limitations restrict it to the mid-thoracic to sacral spine while Figure 5 spans C1 to L6, no code of its own
Btrfly, Sekuboyina 2020 (Radiol Artif Intell) [notes] | 302 plus 65 CTs, sagittal and coronal maximum-intensity projections | Not read | Cervical 89.9, thoracic 86.2, lumbar 91.4 percent | The closest 3D analogue to a projection; the rib cage in a plain projection costs about 5 points; no transitional stratum
Netherton 2020, X-Net multiview labelling of palliative radiotherapy CT (Med Phys; PMC7756475) [full, Europe PMC XML] | In-house: 897 simulation CTs, 803 cross-validation, 94 final test (74 normative, 20 outliers: 6 implants, 6 abnormal anatomy, 2 pacemakers, 6 others); S2 to C1 labelled; canal model on 2,296 CTs. No data or code availability statement [full]; also tested on the public MICCAI 2014 CSI set (302 scans of 125 patients, 60 test), identification 86.8 percent, 91.3 with transfer learning [full] | Not stated | Identification, final test: ensemble 94.2 percent (cervical 97.0, thoracic 94.9, lumbar 88.4, sacral 94.4); normative 96.9; outliers 82.6 (lumbar 70.9); Btrfly on the same 90.5. Localisation 2.2 mm. The irregular-spacing QA flagged all four six-lumbar and the one T13 patient, not the four-lumbar one (5 of 6) | Labels the body above S1 as L5 whatever the count; not trained to classify transitional vertebrae (stated limitation, 35.6 percent prevalence quoted); a lumbar-only field cannot show a sixth body; CT
Elton and others 2020, L1 identification by direct 3D U-Net (SPIE; arXiv 2001.10503) [full] | CT colonography and spine CT: 52 hand-segmented L1 (37 TCIA CT Lymph Nodes, public; 15 Naval), 257 pseudo-labelled training cases, 40 Wisconsin test scans with L1 marked by hand; test and most training not public | Not stated | L1 found in 98 percent of 40 scans, median craniocaudal error 4.5 mm (mean 11.2); the iterative instance approach 30 percent. Prevalences quoted: LSTV about 10 percent (lumbarised S1 6, sacralised L5 4), 13th rib-bearing body about 1 percent, rudimentary or absent 12th rib about 8 percent | One level only; the T12-plus-rib variant "shifted up" and was dropped; an earlier direct L1 model trained on 44 hand segmentations (70 percent) shifted L1 up to T12 in about 15 percent and failed in about 5 percent of cases, 'often due to implants or other abnormalities' [full]; no handling of the variants it quotes
Glocker 2013, classification forests on pathological CT (MICCAI) [abstract, Microsoft Research page] | 224 spine CTs (scoliosis, kyphosis, implants) plus 200 mostly abdominal CTs; the 224 later became a SpineWeb set | Not stated on the page | Localisation error and identification rate reported, not read in numbers | No word on count variants; pre-deep; CT
VERIDAH on SPINEPS, Moeller 2026 (Eur Radiol; arXiv 2601.14066) [full] | In-house CT 1,536 (1,171 train, 365 test; T1 always in field) and NAKO T2w MRI 6,291 (5,291 train, 1,000 test), one rater with 3 years' experience annotated all data, the CT segmentations supervised by an expert with 24 years' experience; no public set used [full]; that the supervisor confirmed every anomaly (kappa 0.95) and that the labels are unreleased (a TUM e-mail) rest on SchwingNet's full-spine-corpora-with-reader-counted-variants.md [notes] | Yes, github.com/Hendrik-code/spineps, Apache 2.0 for the code, no licence stated for the weights [code]; T13 is id 28, L6 id 25; an --enforce-12-thoracic flag exists | Perfectly labelled subjects: CT 99.18 percent (Meng baseline 77.81), MRI 98.30 (SpineNetV2 91.49, TotalSpineSeg 94.24); thoracic enumeration anomaly recall CT 96.30 (baseline 11.11), MRI 87.80 (SpineNetV2 0.00, TotalSpineSeg 27.63); lumbar CT 97.22 (61.11), MRI 94.48 (83.72, 83.04). Thoracic count constrained to 11 to 13, lumbar 4 to 6; T13 and L6 trained as repeated T12 and L5 with a six-class transition head; a thoracic vertebra is defined by a true rib regardless of its length, read by the human rater and not the model, ambiguous cases settled by morphology such as facet orientation, and Konin's rule adapted so that a vertebra with any Castellvi anomaly is a sacralised lumbar vertebra; SPINEPS hand-corrected in 16 MRI cases (0.25 percent) [full] | No CT segmentation model or Dice is described, the CT masks being in-house annotations [full]; needs centroids first (SPINEPS mislocalised 0.53 percent); recall falls on small fields; a transitional L1 with thoracic facets and no rib made a false T13 on an L6 spine, and every compared model failed on it; the project's own screen finds it over-calls T13 on L6 spines (section 1); CT and MRI only
TotalSegmentator v2 and v3 (Wasserthal; Zenodo) [notes; page] | Public, CC BY 4.0; 1,228 (v2) and 1,939 (v3) CTs; v3 "fixed its vertebra label mix-ups"; 142 whole columns in v3 | Yes; the README lists the total task (vertebrae among its 117 classes) as openly available for any usage under Apache-2.0, some other subtasks needing a licence free for non-commercial use [code]; no CC BY-NC-SA on the README or in the project's records (SchwingNet data/licences.json and data/sources/totalsegmentator.json give the dataset CC BY 4.0) | No L6 or T13 class; on lumbarisation it shifts lumbar labels one level and junction Dice drops 29 points (the owner's NeurIPS 2026 poster) [abstract]; a 3D Slicer thread reports 5 of 10 spine CTs showing apparent transitional vertebrae, a reply by Andras Lasso (not TotalSegmentator's author) giving the variants' prevalence as 'not 50%, but rather about 10%' and that 'Transitional vertebra (L6, T13) are not labeled by the TotalSegmentator model' [page]; the NLST concordance study (arXiv 2512.15921) names invalid vertebra and rib segmentations among six models without attributing them [abstract] | Cannot name a variant it has no class for; rib labels 1 to 12 only, so a thirteenth or a cervical rib has no class either
VertebralBodiesCT-Labels and ResEncL/M, Hofmann 2026 (Eur J Radiol; Hugging Face) [page] | Public, CC BY-SA 4.0; 1,460 CTs (TotalSegmentator and VerSe images; 140 and 2 excluded), bodies only T1 to L5 plus sacrum; L6 id 18 and T13 id 21 "optional"; a fused L6 (Castellvi III or IV) is labelled sacrum; 69 L6 and 14 T13 flags in data.csv [notes]; 1,216 train, 244 test | Model weights on Hugging Face; nnU-Net (Apache 2.0); the dataset card names no model licence, while the Hugging Face API tags the three model repositories cc-by-sa-4.0 [page] | No accuracy on the card; the ResEncL and ResEncM model cards warn that residual labelling errors "could cause segmentation errors, especially in cases with transitional vertebrae"; the paper's L3 identification comparison was not readable | Bodies only; no arch, pedicle or canal; a fused L6 disappears into the sacrum, so Castellvi III and IV are not countable from it; 12 thoracic assumed where T1 is out of field
CTSpine1K, Deng 2021 (MELBA 2025; arXiv 2105.14711) [full] | Public, CC BY-NC-SA 4.0; 1,005 CTs from COLONOG, HNSCC, MSD liver and COVID-19; labels 1 to 25, C1 to L6; 17 sacral lumbarisation and 11 lumbar sacralisation cases flagged with ids in the release; semi-automatic masks (nnU-Net then junior, senior and surgeon review), no inter-rater figure | Yes, github.com/MIRACLE-Center/CTSpine1K (licence not read) | nnU-Net Dice per vertebra 0.869 public test, 0.840 private, 0.619 on VerSe; L6 Dice 0 on all three test sets, attributed to L6 "confusing the model" | The one public CT set with an L6 class and the benchmark cannot segment it; no T13; the neck is thin; no rib labels
CTSpinoPelvic1K, Schwing 2026 (arXiv 2609.22760; NeurIPS 2026 poster) [abstract, both] | Public, CC BY-NC-SA 4.0 (Zenodo 10.5281/zenodo.22139642); 802 CT records (1,153 volumes of 802 patients per the poster) with spine, pelvis, ribs and femora in one frame; classes L6, T13, separate S1 and lumbar ribs; 33 LSTV with two-reader Castellvi I to IV; rib labels are triaged pseudolabels; patient-grouped LSTV-stratified five folds; the arXiv abstract lists no held-out test set as a limitation, while the repository README (master) describes 5-fold cross-validation with a held-out test set, the holdout carried in splits_5fold.json [abstract; code] | Yes, github.com/OpenSpineConsortium/CTSpinoPelvic1K, code Apache-2.0, derived labels and splits CC BY-NC-SA 4.0, images CC BY 3.0 [code]; the NeurIPS poster abstract says the 5-fold checkpoints and a dual-spinopelvic CT segmenter with weights are released, which the README does not name [abstract] | Validation by geometric invariants (802 of 802) and rib incidence over 5,749 ribs; the poster: TotalSegmentator sacrum Dice 0.817 zero-shot, junction Dice down 29 points on any LSTV, lumbar labels shifted caudally by one; VERIDAH's L5/L6 merge isolated | The project's own; 33 transitional cases; rib labels not reader truth
SPIDER, van der Graaf 2024 (Sci Data; arXiv 2306.12217; Zenodo 10159224; PMC10908819) [full, Europe PMC XML, read in review; page] | Public, CC BY 4.0; 447 sagittal T1 and T2 series of 218 low-back-pain patients, four Dutch hospitals; vertebrae, discs and canal; 179/39/39 with the test hidden for the Grand Challenge | Challenge baseline code public | Vertebrae are numbered from the bottom up, the most caudal lumbar body 1, and the paper says this is not an anatomical label since that body "is not necessarily L5"; clinical names were "infeasible due to the risk of mislabeling"; it quotes an LSTV prevalence of 35.5 percent; the sacrum is not segmented | No level names at all, no sacrum, lumbar only: it is a segmentation set that explicitly declines to name levels
MRSpineSeg challenge and SpineParseNet, Pang 2021 (IEEE Trans Med Imaging 40(1):262-273, doi 10.1109/tmi.2020.3025087, PMID 32956047) [abstract for the paper; the dataset read in Sadu 2026 PMC13538668, Graf 2023 PMC10643734 and Yilizati-Yilihamu 2023 PMC10502997, all full] | Released through the 2nd CSIG Image and Graphics Technology Challenge at www.spinesegmentation-challenge.com, which Sadu 2026 says is no longer publicly accessible, with no verified download link (the host does not resolve from this container); 215 T2 sagittal lumbar MRI volumes from one local hospital, 172 released as training and validation; pixels 0.30 to 0.59 mm, slices 4.40 to 5.50 mm, 12 to 18 slices; 19 structures, the 10 vertebrae T9 to S and the 9 discs T9/T10 to L5/S, plus background; expert-corrected manual masks in ITK-SNAP; licence stated nowhere read | Yes, github.com/pangshumao/SpineParseNet, its README names no licence | SpineParseNet Dice 87.32 +/- 4.75 vertebrae, 87.78 +/- 4.64 discs, 87.49 +/- 3.81 over the 19; Sadu 2026 per level from T9 38.74 to L1 92.89, S 91.25 percent; Graf 2023 finds the labels exceed the bony borders (ligaments and soft tissue), re-labels 20 volumes to bone alone and scores its MRI-to-CT pipelines there at Dice up to 0.80 | Fixed labels T9 to S with no L6 or T13 class and no count variant discussed in any text read, so the lowest lumbar body is named by position above the sacrum; no count from C2; lumbar MRI only; no longer obtainable from its host
TotalSpineSeg (neuropoly) [code] | Trained on whole-spine (OpenNeuro ds005616), SPIDER, Spine Generic, with sacrum sources GoldAtlas, SynthRAD2023, MRSpineSeg; sizes not on the README | Yes, github.com/neuropoly/totalspineseg; licence not on the README | No metrics on the README; VERIDAH's comparison: 94.24 percent perfectly labelled MRI subjects, thoracic anomaly recall 27.63, lumbar 83.04 | Labels C1 to L5 (11 to 45) and sacrum (50), discs to L5-S; no L6 or T13 class; a localiser for images without C1 or sacrum, not a variant handler
Windsor 2020 (MICCAI; arXiv 2007.02606) and SpineNetV2, Windsor 2022 (arXiv 2205.01683) [full, ar5iv] | OWS: 710 or 719 whole-spine MRIs of 196 patients, in-house (37 scans, 888 vertebrae in the test table); Genodisc: 2,279 patients, 2,819 scans, in-house, 421 lumbar test scans; Zukic: 17 scans on SpineWeb, public. A radiologist labelled one scan per patient with S1 as "the first vertebra attached to the pelvis" | SpineNet: a web demo by request; no repository or licence stated in either paper | OWS: precision 99.0, recall 98.1, identification 96.5 (97.3 within one) percent, 2.4 mm; Genodisc 98.4; Zukic 90.9 | 24 classes C2 to S1; an extra body between S1 and C2 is labelled L6 by convention, so a T13 cannot be named; beam search gives a small penalty to plus or minus one lumbar; the main failure is S2 read as S1 shifting every label; no stratum for anomalous counts is reported; MRI only
Kwak 2025, LSTV present or absent on lateral lumbar radiographs (J Clin Med 14:7671; PMC12610351) [full, Europe PMC XML] | In-house, 3,116 standing lateral films of one tertiary hospital, 1,941 LSTV (62.3 percent, enriched) and 1,175 normal; truth from the MRI (or whole-spine, CT) report naming a transitional, lumbarised or sacralised segment; 313 test (195 LSTV, 118 normal). Data on request only | No code statement | ResNet-50: accuracy 76.4, sensitivity 85.1, specificity 61.9 percent, AUC 0.84; one orthopaedic surgeon 83.9 percent accuracy; DINOv2 75.4, CLIP 71.0 | Binary, no Castellvi type, no level named, one view, single centre, below the reader
Nakajima and others, deep learning alignment and implant measurement on scoliosis radiographs (npj Digit Med 2026, doi 10.1038/s41746-026-03020-7, PMID 42469410) [abstract] | Not stated as public. 4,585 radiographs of 1,671 adolescent idiopathic scoliosis patients, 10 institutions in 2 countries; training, validation and external test sets without sizes, the abstract also saying coronal external validation ran across four cohorts in four countries; the readers not in the abstract | Not stated | Major-curve Cobb MAE 2.7 deg (r 0.99), thoracic kyphosis 3.7 deg (r 0.91), implants 0.18 per image (r 0.99); vertebral numbering reaches an "accuracy of 0.97 for recognizing transitional vertebrae" | The one radiograph numbering result found that quotes a transitional-vertebra accuracy; which variant (lumbosacral, thoracolumbar, numerical) and how many cases are not in the abstract, no PMC copy and nature.com not readable here, adolescent scoliosis films only
Kim 2024, YOLOv5x finds L5 on AP lumbar films (J Int Med Res; PMC10785730) [full, Europe PMC XML] | In-house, 150 adults of one Korean spine centre, each with an AP whole-spine film and an AP lumbar film; L5 set by counting down from C2 to the sacrum on the whole-spine film; 105 train, 45 validation, no test | Not stated | mAP at 0.5 of 99.2 (98.2 in the Discussion), 42 of 45 correct at 90 percent confidence, 2 complete misses | One level, one view, 45 images, no transitional handling stated beyond "L5 is easily miscounted"; no magnification matter since it names, not measures
Moeller 2025, thoracolumbar stump ribs (arXiv 2505.05004; Zenodo 14850928) [full] | VerSe (323) and RibFrac (420), both public, plus 143 in-house for the segmenter; 648 subjects, 2,464 ribs analysed; stump rib defined as 38 mm or shorter | Yes, github.com/Hendrik-code/rib-segmentation (weights) and Zenodo masks; licence not stated for either | Rib Dice 0.997 against 0.779 for existing models; rib length succeeded in 98.2 percent; stump versus regular from partially visible ribs F1 0.84 (linear SVM); 159 stump ribs in 133 of 648 subjects (20.5 percent) | A length rule, not a reader count of rib pairs; no 11 or 13 pair prevalence; CT; the project's records list it as automatic calls only [notes]
RibSeg v2, Jin 2023 (IEEE TMI; arXiv 2210.09309; github HINTLab/RibSeg) [abstract; code] | Public images (RibFrac) with RibSeg annotations on Zenodo and Drive; 660 CTs, 15,466 ribs (README: 490 scans, 11,719 ribs, 320/50/120); centrelines shaped 24 ribs by 500 points; labels from morphology algorithms refined by hand (the README's account, given for v1's 490 scans; the v2 abstract says experts inspected them) | Yes; no licence stated | Baseline rib segmentation Dice about 95 percent; labelling metrics not on the pages read | Fixed 24-rib frame, nothing on 11 or 13 pairs, cervical or lumbar ribs; no vertebral level
von Berg and others 2019, Mask R-CNN rib segmentation and labelling on chest films (arXiv 1908.08329) [full, ar5iv] | 174 PA chest radiographs from von Berg 2016; public status not stated; ribs 1 to 9 only, "consistently visible" | Not stated | Bounding-box Dice 0.846, segmentation Dice 0.733, five-fold; accuracy 0.95 against 0.86 for Candemir's atlas | Ribs 10 to 12 left out, so the thoracolumbar count is not reachable; no cervical rib; no vertebra
Cervical rib detection: ACR AI use case (CT; a sibling for MRI) [page] | None: "No known related public datasets at this time"; status public commenting; prevalence stated under 1 percent | None | None | No algorithm and no dataset exist in the public record found; the only rib-labelling work found assumes 12 pairs; still none on 2026-10-30 (Europe PMC, 48 hits for cervical or lumbar rib with deep learning or automatic detection, none a detector); the prevalence to design against is Henry 2018's pooled 1.1 percent in healthy people (141 studies, 77,924 participants, more than half unilateral), and Duman 2026 found 7 of 517 (1.35 percent) on thoracic CT by one reader
Castellvi typing by machine | No method found: the searches returned Kwak 2025 (binary) and clinical series graded by readers (Tatara, Yoon, Albano, the 3,855-CT series) | None | None | Castellvi type needs the transverse process and the sacral ala in one view; nothing automatic was found by the first sweep, and four routes on 2026-10-30 found none either: Europe PMC (Castellvi with deep learning, convolutional, automated or automatic classification or artificial intelligence, 97 hits, the first 15 holding Kwak 2025 as the only automated method), Europe PMC again (Bertolotti or transitional vertebra with machine learning, 180 hits, the first 15 giving Kwak 2025, Yang 2025 and Nakajima 2026, none typing Castellvi, and a 2026 narrative review of AI for anatomical variation, PMC13686224, whose only LSTV study is Kwak 2025), OpenAlex (11 results, none) and one web search (none; Kwak 2025 itself says no prior study focused on automated LSTV classification); the arXiv API timed out and then answered 503, and Semantic Scholar 429, so arXiv was not swept
BUU-LSPINE (Klinwichit 2023, Applied Sciences) [notes] | Public (services.informatics.buu.ac.th); 3,600 patients' AP and lateral lumbar films with corners, spondylolisthesis and LSTV truth (15 lumbarisations, 129 sacralisations on the lateral CSV) | Yes, github.com/North-Github/BUU-LSPINE | Corner error 4.63 mm AP, 4.91 lateral; YOLOv5 precision 81.93 and 83.45 percent | The LSTV truth is a per-film flag the paper does not model; lumbar only; the records call it "unexploited"
Fang and others, systematic review and narrative analysis of lumbosacral transitional vertebrae (Brain Spine 2025;5:105628, doi 10.1016/j.bas.2025.105628, PMC12549404, CC BY) [full] | 83 studies, searched on 2023-12-28 (PubMed, Embase, Cochrane), all graded low or very low quality; the prevalence from the 20 studies that report it, 28,106 people with 4,290 LSTV | None | Average prevalence about 15.3 percent (4,290 of 28,106), range 4.5 to 35.6; meta-analysis declined for heterogeneity and small samples, so no random-effects estimate and no confidence interval; no Castellvi or sacralisation-versus-lumbarisation split (Paik 2013's 10.6 percent types II to IV, 5.3 each, quoted alone); among its prevalence series French 2014 588 of 5,941 (9.9), Nardo 2012 841 of 4,636 (18.1), Tini 1977 269 of 4,000 (6.7), Hanhivaara 2020 1,101 of 3,855 (29) | A prevalence, not a method; the 4.5 to 35.6 range is the definition's and the cohort's, so a benchmark stratum needs its own definition before any pooled figure applies
Osiowski and others, lumbar rib meta-analysis (Surg Radiol Anat 2024;46(12):2057-2066, doi 10.1007/s00276-024-03504-9, PMC11579145, CC BY) [full] and Henry and others, cervical rib meta-analysis (World Neurosurg 2018;110:e965-e978, doi 10.1016/j.wneu.2017.11.148, PMID 29203316) [abstract] | Osiowski: 9 studies, 5,430 people, 141 lumbar ribs, only series of spines with normal segmentation and 17 thoracolumbar vertebrae that state counting the whole column; Henry: 141 studies, 77,924 participants | None | Lumbar rib pooled 2.1 percent (95 percent CI 1.0 to 4.6), CT 1.6 (0.6 to 4.3; 4 studies, 2,906), radiograph 2.1 (0.4 to 11.1; 3 studies, 2,100), bilateral 65.4 (39.4 to 84.6); I2 90.11 (CT) and 95.20 (radiograph), by region under 0.001 to 97.16; LFK index -4.55; random effects in MetaXL 5.3; cervical rib 1.1 percent in healthy people and 29.5 in thoracic outlet syndrome, more than half unilateral, no CI in the abstract | No pooled estimate was found for eleven or thirteen rib pairs (the reader's Europe PMC search, not rerun here); the lumbar-rib definition requires normal segmentation and 17 thoracolumbar vertebrae, so it excludes every spine with a count variant, the stratum a naming rule needs; neither tells a thirteenth rib from a lumbar rib by a stated length rule

## 3. What the family's prior art settles and does not

Settled:
- Every public CT and MRI labeller counts 7, 12 and 5 unless told otherwise, and the ones that allow a variant allow
  it by convention: Windsor and SpineNetV2 label the extra body L6 whatever the thoracic count; Lessmann fixes 24
  labels; TotalSegmentator, TotalSpineSeg and FleXray have no L6 or T13 class; Netherton labels the body above S1 L5.
  The sole labeller that models the count (VERIDAH) constrains it to 11 to 13 thoracic and 4 to 6 lumbar and reaches
  96 to 97 percent anomaly recall on its own CT test set, and the project has measured that alone it over-calls T13
  on L6 spines; two labellers agreeing are precise and insensitive (section 1).
- The public datasets carry few transitional spines and label them unevenly: VerSe 47 L6 and 6 T13 (label 25 and
  28); CTSpine1K 17 lumbarisations and 11 sacralisations under one L6 label and no T13; Hofmann's bodies set 69 L6
  and 14 T13 with a fused L6 folded into the sacrum; CTSpinoPelvic1K 33 Castellvi-typed; SPIDER declines to name
  levels at all and omits the sacrum; BUU-LSPINE holds an LSTV flag nobody has modelled. The best benchmark on
  CTSpine1K scores L6 Dice 0; the hidden L6 of VerSe'19 beat almost every entrant.
- Prevalence is well measured by readers in closed cohorts (section 1): counts other than 24 presacral in 6 to 9
  percent, LSTV 8 to 29 percent by definition and cohort, TLTV 11 to 15 percent, 11 or 13 rib pairs in 5 to 8 percent
  (Sabri 171 of 3,147 films, 5.4 percent [abstract]; Doo 112 of 1,340 CTs, 8.4 percent [full]), cervical rib about 1
  percent (Henry 2018 pools 1.1 in healthy people) and lumbar rib 2.1 percent (Osiowski 2024's pooled estimate); for
  LSTV, Fang 2025 averages 15.3 percent over 20 studies without an interval. No open image set carries these counts
  over both junctions.
- On radiographs, the only per-level anomaly work is binary LSTV detection on a lateral lumbar film at 76 percent
  accuracy, below a surgeon, and a YOLO that finds L5 on 45 AP films; no radiograph method reports a result on L6, T13
  or a rib-count variant (Nakajima 2026 quotes 0.97 accuracy for recognising transitional vertebrae on scoliosis
  films, the variant and the number of cases not in its abstract), and no method types Castellvi.
- Rib counting is unsolved as a count: the rib labellers found assume 12 pairs (CT) or label ribs 1 to 9 (chest
  film); the one anomaly-aware rib work measures stump length on CT and reports no pair count.

Not settled:
- No method reports naming accuracy on a transitional stratum of real radiographs or fluoroscopy, in any view;
  Nakajima 2026's 0.97 is a recognition rate whose variant and count its abstract does not give, and Yang 2025's T13
  and L6 classes are patches cut at VerSe's own centroids, not a count of the column.
- No automatic Castellvi grading and no automatic cervical or lumbar rib detector with a dataset, both searched again
  on 2026-10-30; no pooled prevalence for eleven or thirteen rib pairs or for four or six lumbar vertebrae, and for
  LSTV only Fang 2025's narrative average, without an interval.
- Whether VERIDAH's 99.18 percent transfers off its in-house CT (its authors say the MRI model is NAKO-only; the
  project's VerSe screen says T13 over-calls) is measured only by the project itself.
- How Payer 2020 and Chen D 2020 treat L6 internally was not read (scitepress PDF unreadable; Chen D's appendix
  entry not reached).

## 4. Gaps: what could not be read

- The VerSe paper's sections 4.5, 4.6 and 5.2 to 5.3 were read in the first 100,000 characters of the ar5iv render;
  the second half held only references and appendices, so the Dice-with-and-without-transitional figure (Fig. 9) and
  the exact cross-iteration L6 numbers are not quoted.
- Payer 2020's PDF (scitepress) did not render; Netherton 2020's methods for how a T13 or L6 ground truth was
  written were not in either half read; Glocker 2013 only as a page; Chen D 2020's own paper not read.
- SPIDER's arXiv render failed (ar5iv fatal error); a reader in the review of 2026-10-30 read the Sci Data text whole
  at PMC10908819, which confirms the numbering convention and the 35.5 percent figure.
- Hofmann 2026's full text (Eur J Radiol 2026;204:113118) and its per-level accuracy; its PubMed abstract (42561894),
  read in the review, gives the 1,216 and 244 split and an L3 body Dice and no per-level identification figure, and
  the data.csv downloaded then counts 69 L6, 14 T13 and 244 test rows; the dataset card gives no accuracy.
- MRSpineSeg (Pang 2021) was read on 2026-10-30 through the SpineParseNet abstract (PMID 32956047) and three papers
  that use the set (Sadu 2026, Graf 2023, Yilizati-Yilihamu 2023; row in section 2): 215 T2 sagittal lumbar volumes,
  172 released, 19 structures (vertebrae T9 to S, discs T9/T10 to L5/S), no L6 or T13 class and no count variant
  discussed; Sadu 2026 says the challenge site www.spinesegmentation-challenge.com is no longer publicly accessible,
  with no verified download link, and it does not resolve from this container, so the licence and the label ids are
  unread at source; the SpineParseNet README names no licence.
- RibSeg v2's labelling accuracy and licence; the Moeller rib weights' licence; TotalSpineSeg's licence and metrics.
- Kim 2024's and Kwak 2025's code: neither paper states any.
- Searches the first sweep did not run (budget exhausted after 17) were run on 2026-10-30 for automatic Castellvi
  grading (none), cervical-rib AI with data (none; the ACR use case stands), lumbar-rib detectors (none automatic;
  Osiowski 2024 pools manual series) and MRSpineSeg (read); TotalSpineSeg variant handling, Chen D 2020's L6 treatment
  and AASCE or NHANES II count truth were not searched again.
- Refused or unreadable hosts this run: PMC (via search only), SAGE blob PDF (binary), scitepress PDF (binary),
  europepmc.org fulltextRepo (HTTP 500), neurips.cc (read), mdpi.com (403), ar5iv for 2306.12217 (conversion failed).
- In the review: the arXiv API timed out and then answered 503 and Semantic Scholar 429, so arXiv was not swept for
  Castellvi typing; www.spinesegmentation-challenge.com does not resolve; Nakajima 2026 has no PMC copy and nature.com
  was not readable, so it is read as its abstract; Yang 2025's Figure 5, the per-level Dice image, was not read.

## 5. Sources read this run

- VerSe: https://ar5iv.labs.arxiv.org/html/2001.09193 ; https://arxiv.org/abs/2001.09193
- Lessmann: https://ar5iv.labs.arxiv.org/html/1804.04383
- Windsor: https://ar5iv.labs.arxiv.org/html/2007.02606 ; SpineNetV2: https://ar5iv.labs.arxiv.org/html/2205.01683
- VERIDAH: https://arxiv.org/html/2601.14066v1 ; SPINEPS: https://raw.githubusercontent.com/Hendrik-code/spineps/main/README.md
- Netherton: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7756475/fullTextXML
- Elton: https://ar5iv.labs.arxiv.org/html/2001.10503
- Kwak: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12610351/fullTextXML
- Kim: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10785730/fullTextXML
- CTSpine1K: https://arxiv.org/html/2105.14711v4 ; CTSpinoPelvic1K: https://arxiv.org/abs/2609.22760 ;
  https://neurips.cc/virtual/2026/poster/139654
- SPIDER: https://zenodo.org/records/10159224 ; https://arxiv.org/abs/2306.12217 (search summary)
- TotalSpineSeg: https://raw.githubusercontent.com/neuropoly/totalspineseg/main/README.md
- Hofmann: https://huggingface.co/datasets/fhofmann/VertebralBodiesCT-Labels
- Stump ribs: https://arxiv.org/html/2505.05004v1 ; RibSeg: https://arxiv.org/abs/2210.09309 ;
  https://raw.githubusercontent.com/HINTLab/RibSeg/main/README.md
- Chest-film ribs: https://ar5iv.labs.arxiv.org/html/1908.08329
- Cervical rib: https://www.acr.org/Data-Science-and-Informatics/AI-in-Your-Practice/AI-Use-Cases/Use-Cases/Cervical-Rib-Detection-CT
- TotalSegmentator transitional: https://discourse.slicer.org/t/what-happens-encountering-transitional-vertebrae-when-segmenting-the-spine-in-totalsegmentator/36824 (search summary) ; https://arxiv.org/abs/2512.15921
- Glocker: https://www.microsoft.com/en-us/research/publication/vertebrae-localization-in-pathological-spine-ct-via-dense-classification-from-sparse-annotations/ (search summary)
- LSTV series: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7248049/ (search summary)
- Read in the review of 2026-10-30: Ucar 2013 https://pubmed.ncbi.nlm.nih.gov/23864947/ ; Payer's code
  https://github.com/christianpayer/MedicalDataAugmentationTool-VerSe ; TotalSegmentator
  https://raw.githubusercontent.com/wasserth/TotalSegmentator/master/README.md ; Hofmann's model cards
  https://huggingface.co/fhofmann/VertebralBodiesCT-ResEncL ; SPIDER
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10908819/ ; CTSpinoPelvic1K
  https://raw.githubusercontent.com/OpenSpineConsortium/CTSpinoPelvic1K/master/README.md ; Yang 2025 PMC12491412 ;
  Nakajima 2026 https://pubmed.ncbi.nlm.nih.gov/42469410/ ; MRSpineSeg PMID 32956047, PMC13538668, PMC10643734 and
  PMC10502997 ; Fang 2025 PMC12549404 ; Osiowski 2024 PMC11579145 ; Henry 2018 PMID 29203316 ; Sun 2025 PMC12630705 ;
  Duman 2026 PMC13517915 ; Zhou 2023 PMC10722060 ; Jankowski 2026 PMC13703058 ; the review of AI for anatomical
  variation PMC13686224
