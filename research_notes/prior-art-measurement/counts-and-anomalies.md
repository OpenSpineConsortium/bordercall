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

## 1. What the existing notes already settle

- The counting corpora with reader truth are catalogued in full-spine-corpora-with-reader-counted-variants.md
  (sections 1, 2 and 4) [notes]: fourteen cohorts with per-case counts over both junctions, none open; the open
  additions are Hofmann's VertebralBodiesCT-Labels (69 L6 and 14 T13 flags over 1,460 held CTs) and Albano 2020's
  Castellvi table (906 EOS films, images not open). The prevalence figures of this family come from there and from
  morphometry-beyond-the-42-papers.md ("Every spine has 7, 12 and 5 bodies" row; the series table): Yoon 2024
  (450 whole-spine CTs, 6.7 percent not 24 presacral, 23.8 percent with any count or junction atypia, LSTV 26.4
  percent, TLTV 15.3 percent), Doo 2020 (1,340 CTs, 12 ribs in 91.6 percent, 11 ribs 107, 13 ribs 5, LSTV 8.3
  percent), Tins 2016 (418 MRIs, 8.1 percent one mobile vertebra more or fewer), Paik 2013 (8,280 lumbar MRIs
  counted from C2, 4 lumbar 2.6 percent, 6 lumbar 8.2 percent), VERIDAH's NAKO sample (6,291 MRIs, 5.8 percent 11 or
  13 thoracic, 9.7 percent 4 or 6 lumbar), Tatara 2021 (880, LSTV 111 with Castellvi II 28, III 42, IV 4; TLTV 96),
  Sabri 2025 (3,147 films, 13 rib-bearing in 28, 11 in 143), Lodz 2026 (499, L6 24, T13 13, 4L 11, 11T 10). The
  web search here added only one more series, a 3,855 consecutive abdominal CT study with LSTV in 29 percent
  (Castellvi I 68, II 16, III 13, IV 3 percent of those) [abstract, PMC7248049 snippet], and a 3,607-adult radiograph
  series with 18.9 percent LSTV (sacralisation 17.2, lumbarisation 1.7) [abstract]; no pooled meta-analysis was
  found before the search budget ended.
- The level-identification methods that matter for X-ray are tabled in lumbosacral-to-cervical-extrapolation.md
  (section 2) and benchmarks-to-beat.md (section 3) [notes]: LevelCheck (Lo 2015; 20 patients, registration to the
  patient's CT, 100 percent at 25.7 s), De Silva 2016 and Manbachi 2018 (398 radiographs, localisation error 30.4
  percent unassisted against 2.4 percent assisted, most useful where the sacrum or twelfth rib is hidden), Huang 2022
  (render-trained, 88.3 percent labelling on 100 real Long-Film images of 13 cadavers), VertXNet (Chen 2024; counts
  from a detected C2 or S1, NHANES II and PREVENT), Payer 2020, Btrfly 2020, the VerSe challenge, Netherton 2025
  (external, two sites, cervical 69 and 92 percent), VERIDAH, the owner's NeurIPS poster and Kwak 2025 (there cited
  as Lee 2025). Those rows are not repeated below except where this reading added to them.
- On CT labellers the project's own measurement stands (spineps-anomaly-route.md, section 3) [notes]: on VerSe's
  319 read persons, two labellers agreeing (TotalSegmentator's count against SPINEPS/VERIDAH's) find 22 of 83 L6
  (26.5 percent) and 2 of 6 T13 with 228 of 228 specificity and 22 of 22 precision; VERIDAH alone finds 36 of 83 L6
  but calls T13 on 11 L6 spines (4 of 16 T13 calls right). On CTSpinoPelvic1K the two-labeller L6 calls are 7 of 7
  right and find 7 of 29.
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
Payer 2020, SpatialConfiguration-Net plus U-Net (VISAPP) [notes; the scitepress PDF did not render] | VerSe'19, 80 training volumes, three-fold | Yes (github.com/christianpayer, per the VerSe appendix; licence not read) | Cervical 91.1 (102 of 112), thoracic 89.0 (388 of 436), lumbar 90.4 (284 of 314) percent; lumbar includes L6 | CT; the three regions' intervals overlap; no transitional stratum reported
Lessmann 2019, iterative FCN with memory (Med Image Anal; arXiv 1804.04383) [full] | Five sets: CSI 2014 thoracolumbar CT (15), xVertSeg lumbar CT (15), NLST low-dose chest CT (55, authors' own masks, not released), healthy lumbar CT (10), lumbar MR (23); four of five have public reference masks | Not stated (PyTorch) | Identification 93 percent (206 of 222 vertebrae) over the CT sets, 97 percent with MR; Dice 94.9 percent; visibility 97 percent. The one wrong scan had four lumbar vertebrae and was labelled T2 to L5 instead of T1 to L4 | Label space fixed at C1 to L5 (24), so a four- or six-lumbar spine can only be entirely offset; no training scan had an irregular count, named as future work; no cervical, no implants; CT and MR only
Chen D 2020 and Chen M 2019 (VerSe winners) [abstract, via the VerSe appendix] | VerSe | Chen M: 25 labels, "ignoring the rare L6 label"; Chen D not read | As the VerSe row | A label set with no L6 fails every L6 scan by construction
Yeah T. and others, Dong Y., Angermann C. (VerSe'20 entrants) [abstract, via the VerSe appendix] | VerSe | Not read | Not read separately | The only entrants whose label sets include T13 (Yeah T.: C1-C7, T1-T13, L1-L6; Dong and Angermann: L6 but not T13)
Btrfly, Sekuboyina 2020 (Radiol Artif Intell) [notes] | 302 plus 65 CTs, sagittal and coronal maximum-intensity projections | Not read | Cervical 89.9, thoracic 86.2, lumbar 91.4 percent | The closest 3D analogue to a projection; the rib cage in a plain projection costs about 5 points; no transitional stratum
Netherton 2020, X-Net multiview labelling of palliative radiotherapy CT (Med Phys; PMC7756475) [full, Europe PMC XML] | In-house: 897 simulation CTs, 803 cross-validation, 94 final test (74 normative, 20 outliers: 6 implants, 6 abnormal anatomy, 2 pacemakers, 6 others); S2 to C1 labelled; canal model on 2,296 CTs. Not public | Not stated | Identification, final test: ensemble 94.2 percent (cervical 97.0, thoracic 94.9, lumbar 88.4, sacral 94.4); normative 96.9; outliers 82.6 (lumbar 70.9); Btrfly on the same 90.5. Localisation 2.2 mm. The irregular-spacing QA flagged all four six-lumbar and the one T13 patient, not the four-lumbar one (5 of 6) | Labels the body above S1 as L5 whatever the count; not trained to classify transitional vertebrae (stated limitation, 35.6 percent prevalence quoted); a lumbar-only field cannot show a sixth body; CT
Elton and others 2020, L1 identification by direct 3D U-Net (SPIE; arXiv 2001.10503) [full] | CT colonography and spine CT: 52 hand-segmented L1 (37 TCIA CT Lymph Nodes, public; 15 Naval), 257 pseudo-labelled training cases, 40 Wisconsin test scans with L1 marked by hand; test and most training not public | Not stated | L1 found in 98 percent of 40 scans, median craniocaudal error 4.5 mm (mean 11.2); the iterative instance approach 30 percent. Prevalences quoted: LSTV about 10 percent (lumbarised S1 6, sacralised L5 4), 13th rib-bearing body about 1 percent, rudimentary or absent 12th rib about 8 percent | One level only; the T12-plus-rib variant "shifted up" and was dropped; about 5 percent failures on implants; no handling of the variants it quotes
Glocker 2013, classification forests on pathological CT (MICCAI) [abstract, Microsoft Research page] | 224 spine CTs (scoliosis, kyphosis, implants) plus 200 mostly abdominal CTs; the 224 later became a SpineWeb set | Not stated on the page | Localisation error and identification rate reported, not read in numbers | No word on count variants; pre-deep; CT
VERIDAH on SPINEPS, Moeller 2026 (Eur Radiol; arXiv 2601.14066) [full] | In-house CT 1,536 (1,171 train, 365 test; T1 always in field) and NAKO T2w MRI 6,291 (5,291 train, 1,000 test), one rater with a supervisor confirming every anomaly; no public set used; labels not released | Yes, github.com/Hendrik-code/spineps, Apache 2.0 [code]; T13 is id 28, L6 id 25; an --enforce-12-thoracic flag exists | Perfectly labelled subjects: CT 99.18 percent (Meng baseline 77.81), MRI 98.30 (SpineNetV2 91.49, TotalSpineSeg 94.24); thoracic enumeration anomaly recall CT 96.30 (baseline 11.11), MRI 87.80 (SpineNetV2 0.00, TotalSpineSeg 27.63); lumbar CT 97.22 (61.11), MRI 94.48 (83.72, 83.04). Thoracic count constrained to 11 to 13, lumbar 4 to 6; T13 and L6 trained as repeated T12 and L5 with a six-class transition head; a thoracic vertebra is defined by a true rib | Needs centroids first (SPINEPS mislocalised 0.53 percent); recall falls on small fields; a transitional L1 with thoracic facets and no rib made a false T13 on an L6 spine, and every compared model failed on it; the project's own screen finds it over-calls T13 on L6 spines (section 1); CT and MRI only
TotalSegmentator v2 and v3 (Wasserthal; Zenodo) [notes; page] | Public, CC BY 4.0; 1,228 (v2) and 1,939 (v3) CTs; v3 "fixed its vertebra label mix-ups"; 142 whole columns in v3 | Yes, Apache 2.0 (weights CC BY-NC-SA per the project's records) | No L6 or T13 class; on lumbarisation it shifts lumbar labels one level and junction Dice drops 29 points (the owner's NeurIPS 2026 poster) [abstract]; a 3D Slicer thread reports about half of 10 spine CTs failing at transitional vertebrae, the maintainer answering that the variant's prevalence is about 10 percent [page]; the NLST concordance study (arXiv 2512.15921) names invalid vertebra and rib segmentations among six models without attributing them [abstract] | Cannot name a variant it has no class for; rib labels 1 to 12 only, so a thirteenth or a cervical rib has no class either
VertebralBodiesCT-Labels and ResEncL/M, Hofmann 2026 (Eur J Radiol; Hugging Face) [page] | Public, CC BY-SA 4.0; 1,460 CTs (TotalSegmentator and VerSe images; 140 and 2 excluded), bodies only T1 to L5 plus sacrum; L6 id 18 and T13 id 21 "optional"; a fused L6 (Castellvi III or IV) is labelled sacrum; 69 L6 and 14 T13 flags in data.csv [notes]; 1,216 train, 244 test | Model weights on Hugging Face; nnU-Net (Apache 2.0); dataset card names no model licence | No accuracy on the card; the card warns that residual labelling errors "could cause segmentation errors, especially in cases with transitional vertebrae"; the paper's L3 identification comparison was not readable | Bodies only; no arch, pedicle or canal; a fused L6 disappears into the sacrum, so Castellvi III and IV are not countable from it; 12 thoracic assumed where T1 is out of field
CTSpine1K, Deng 2021 (MELBA 2025; arXiv 2105.14711) [full] | Public, CC BY-NC-SA 4.0; 1,005 CTs from COLONOG, HNSCC, MSD liver and COVID-19; labels 1 to 25, C1 to L6; 17 sacral lumbarisation and 11 lumbar sacralisation cases flagged with ids in the release; semi-automatic masks (nnU-Net then junior, senior and surgeon review), no inter-rater figure | Yes, github.com/MIRACLE-Center/CTSpine1K (licence not read) | nnU-Net Dice per vertebra 0.869 public test, 0.840 private, 0.619 on VerSe; L6 Dice 0 on all three test sets, attributed to L6 "confusing the model" | The one public CT set with an L6 class and the benchmark cannot segment it; no T13; the neck is thin; no rib labels
CTSpinoPelvic1K, Schwing 2026 (arXiv 2609.22760; NeurIPS 2026 poster) [abstract, both] | Public, CC BY-NC-SA 4.0 (Zenodo 10.5281/zenodo.22139642); 802 CT records (1,153 volumes of 802 patients per the poster) with spine, pelvis, ribs and femora in one frame; classes L6, T13, separate S1 and lumbar ribs; 33 LSTV with two-reader Castellvi I to IV; rib labels are triaged pseudolabels; patient-grouped LSTV-stratified five folds, no held-out test | Yes, github.com/OpenSpineConsortium/CTSpinoPelvic1K; 5-fold checkpoints and a dual spinopelvic segmenter released | Validation by geometric invariants (802 of 802) and rib incidence over 5,749 ribs; the poster: TotalSegmentator sacrum Dice 0.817 zero-shot, junction Dice down 29 points on any LSTV, lumbar labels shifted caudally by one; VERIDAH's L5/L6 merge isolated | The project's own; 33 transitional cases; rib labels not reader truth
SPIDER, van der Graaf 2024 (Sci Data; arXiv 2306.12217; Zenodo 10159224) [abstract; page] | Public, CC BY 4.0; 447 sagittal T1 and T2 series of 218 low-back-pain patients, four Dutch hospitals; vertebrae, discs and canal; 179/39/39 with the test hidden for the Grand Challenge | Challenge baseline code public | Vertebrae are numbered from the bottom up, the most caudal lumbar body 1, and the paper says this is not an anatomical label since that body "is not necessarily L5"; clinical names were "infeasible due to the risk of mislabeling"; it quotes an LSTV prevalence of 35.5 percent; the sacrum is not segmented | No level names at all, no sacrum, lumbar only: it is a segmentation set that explicitly declines to name levels
TotalSpineSeg (neuropoly) [code] | Trained on whole-spine (OpenNeuro ds005616), SPIDER, Spine Generic, with sacrum sources GoldAtlas, SynthRAD2023, MRSpineSeg; sizes not on the README | Yes, github.com/neuropoly/totalspineseg; licence not on the README | No metrics on the README; VERIDAH's comparison: 94.24 percent perfectly labelled MRI subjects, thoracic anomaly recall 27.63, lumbar 83.04 | Labels C1 to L5 (11 to 45) and sacrum (50), discs to L5-S; no L6 or T13 class; a localiser for images without C1 or sacrum, not a variant handler
Windsor 2020 (MICCAI; arXiv 2007.02606) and SpineNetV2, Windsor 2022 (arXiv 2205.01683) [full, ar5iv] | OWS: 710 or 719 whole-spine MRIs of 196 patients, in-house (37 scans, 888 vertebrae in the test table); Genodisc: 2,279 patients, 2,819 scans, in-house, 421 lumbar test scans; Zukic: 17 scans on SpineWeb, public. A radiologist labelled one scan per patient with S1 as "the first vertebra attached to the pelvis" | SpineNet: a web demo by request; no repository or licence stated in either paper | OWS: precision 99.0, recall 98.1, identification 96.5 (97.3 within one) percent, 2.4 mm; Genodisc 98.4; Zukic 90.9 | 24 classes C2 to S1; an extra body between S1 and C2 is labelled L6 by convention, so a T13 cannot be named; beam search gives a small penalty to plus or minus one lumbar; the main failure is S2 read as S1 shifting every label; no stratum for anomalous counts is reported; MRI only
Kwak 2025, LSTV present or absent on lateral lumbar radiographs (J Clin Med 14:7671; PMC12610351) [full, Europe PMC XML] | In-house, 3,116 standing lateral films of one tertiary hospital, 1,941 LSTV (62.3 percent, enriched) and 1,175 normal; truth from the MRI (or whole-spine, CT) report naming a transitional, lumbarised or sacralised segment; 313 test (195 LSTV, 118 normal). Data on request only | No code statement | ResNet-50: accuracy 76.4, sensitivity 85.1, specificity 61.9 percent, AUC 0.84; one orthopaedic surgeon 83.9 percent accuracy; DINOv2 75.4, CLIP 71.0 | Binary, no Castellvi type, no level named, one view, single centre, below the reader
Kim 2024, YOLOv5x finds L5 on AP lumbar films (J Int Med Res; PMC10785730) [full, Europe PMC XML] | In-house, 150 adults of one Korean spine centre, each with an AP whole-spine film and an AP lumbar film; L5 set by counting down from C2 to the sacrum on the whole-spine film; 105 train, 45 validation, no test | Not stated | mAP at 0.5 of 99.2 (98.2 in the Discussion), 42 of 45 correct at 90 percent confidence, 2 complete misses | One level, one view, 45 images, no transitional handling stated beyond "L5 is easily miscounted"; no magnification matter since it names, not measures
Moeller 2025, thoracolumbar stump ribs (arXiv 2505.05004; Zenodo 14850928) [full] | VerSe (323) and RibFrac (420), both public, plus 143 in-house for the segmenter; 648 subjects, 2,464 ribs analysed; stump rib defined as 38 mm or shorter | Yes, github.com/Hendrik-code/rib-segmentation (weights) and Zenodo masks; licence not stated for either | Rib Dice 0.997 against 0.779 for existing models; rib length succeeded in 98.2 percent; stump versus regular from partially visible ribs F1 0.84 (linear SVM); 159 stump ribs in 133 of 648 subjects (20.5 percent) | A length rule, not a reader count of rib pairs; no 11 or 13 pair prevalence; CT; the project's records list it as automatic calls only [notes]
RibSeg v2, Jin 2023 (IEEE TMI; arXiv 2210.09309; github HINTLab/RibSeg) [abstract; code] | Public images (RibFrac) with RibSeg annotations on Zenodo and Drive; 660 CTs, 15,466 ribs (README: 490 scans, 11,719 ribs, 320/50/120); centrelines shaped 24 ribs by 500 points; labels from morphology algorithms refined by hand | Yes; no licence stated | Baseline rib segmentation Dice about 95 percent; labelling metrics not on the pages read | Fixed 24-rib frame, nothing on 11 or 13 pairs, cervical or lumbar ribs; no vertebral level
von Berg and others 2019, Mask R-CNN rib segmentation and labelling on chest films (arXiv 1908.08329) [full, ar5iv] | 174 PA chest radiographs from von Berg 2016; public status not stated; ribs 1 to 9 only, "consistently visible" | Not stated | Bounding-box Dice 0.846, segmentation Dice 0.733, five-fold; accuracy 0.95 against 0.86 for Candemir's atlas | Ribs 10 to 12 left out, so the thoracolumbar count is not reachable; no cervical rib; no vertebra
Cervical rib detection: ACR AI use case (CT; a sibling for MRI) [page] | None: "No known related public datasets at this time"; status public commenting; prevalence stated under 1 percent | None | None | No algorithm and no dataset exist in the public record found; the only rib-labelling work found assumes 12 pairs
Castellvi typing by machine | No method found: the searches returned Kwak 2025 (binary) and clinical series graded by readers (Tatara, Yoon, Albano, the 3,855-CT series) | None | None | Castellvi type needs the transverse process and the sacral ala in one view; nothing automatic was found before the search budget ran out
BUU-LSPINE (Klinwichit 2023, Applied Sciences) [notes] | Public (services.informatics.buu.ac.th); 3,600 patients' AP and lateral lumbar films with corners, spondylolisthesis and LSTV truth (15 lumbarisations, 129 sacralisations on the lateral CSV) | Yes, github.com/North-Github/BUU-LSPINE | Corner error 4.63 mm AP, 4.91 lateral; YOLOv5 precision 81.93 and 83.45 percent | The LSTV truth is a per-film flag the paper does not model; lumbar only; the records call it "unexploited"

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
  percent, LSTV 8 to 29 percent by definition and cohort, TLTV 11 to 15 percent, 11 or 13 rib pairs in about 8
  percent, cervical rib under 1 percent. No open image set carries these counts over both junctions.
- On radiographs, the only per-level anomaly work is binary LSTV detection on a lateral lumbar film at 76 percent
  accuracy, below a surgeon, and a YOLO that finds L5 on 45 AP films; no radiograph method reports a result on L6,
  T13 or a rib-count variant, and no method types Castellvi.
- Rib counting is unsolved as a count: the rib labellers found assume 12 pairs (CT) or label ribs 1 to 9 (chest
  film); the one anomaly-aware rib work measures stump length on CT and reports no pair count.

Not settled:
- No method reports naming accuracy on a transitional stratum of real radiographs or fluoroscopy, in any view.
- No automatic Castellvi grading, no automatic cervical or lumbar rib detector with a dataset, no public pooled
  prevalence meta-analysis found.
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
- SPIDER's arXiv render failed (ar5iv fatal error); the numbering convention and the 35.5 percent figure rest on the
  search summary of the paper and are tagged [abstract].
- Hofmann 2026 (Eur J Radiol) full text and its per-level accuracy; the HF card gives none.
- MRSpineSeg (Pang 2021) was not reached at all (the search returned SPIDER); its label scheme and any L6 are unread.
- RibSeg v2's labelling accuracy and licence; the Moeller rib weights' licence; TotalSpineSeg's licence and metrics.
- Kim 2024's and Kwak 2025's code: neither paper states any.
- Searches not run (budget exhausted after 17): TotalSpineSeg variant handling, thoracolumbar transitional or
  lumbar-rib detectors on CT, automatic Castellvi grading, Chen D 2020's L6 treatment, cervical-rib AI with data,
  AASCE and NHANES II for count truth (the existing notes say neither carries it), MRSpineSeg.
- Refused or unreadable hosts this run: PMC (via search only), SAGE blob PDF (binary), scitepress PDF (binary),
  europepmc.org fulltextRepo (HTTP 500), neurips.cc (read), mdpi.com (403), ar5iv for 2306.12217 (conversion failed).

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
