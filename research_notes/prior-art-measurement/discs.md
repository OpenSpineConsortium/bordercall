# Prior art for the intervertebral disc family: disc_h_ant, disc_h_mid, disc_h_post, disc_h_mean, disc_index, disc_w, disc_d

Source: the thread "Plan clinical reread next steps", 2026-10-29, web reading (PMC full texts, arXiv abstract pages and
ar5iv, GitHub, Zenodo, Mendeley Data, the IVDM3Seg challenge site, the SpineNet documentation). The family is the seven
disc keys of bordercall's vocabulary.csv (rows 62 to 68): disc height at the anterior margin, the centre and the
posterior margin, a mean or area-over-length height, a disc ratio, the transverse width and the anteroposterior depth.
Automatic disc height and disc degeneration measurement are in scope. Every claim carries a reading tag: [full] the
whole article or page was read, [abstract] only an abstract page, [page] a web page (dataset, challenge, documentation),
[code] a repository listing. Numbers are copied as the pages gave them; nothing else is copied. The web search budget
ran out after the sweep by measure name, dataset and code; the four searches not run are listed under Gaps.

## 1. What the existing notes already say about discs

- /home/user/SchwingNet/docs/research/morphometry-beyond-the-42-papers.md: the normative disc height tables it names are
  Shin 2025 (CT, 700 young adults, middle disc heights L1-L2 to L5-S1, Brain Spine 2025;5:104162), Yukawa 2012 (lateral
  radiographs of 1,230 Japanese adults, disc height C2 to C7 by sex and decade, doi 10.1007/s00586-012-2167-5) and
  Busscher 2010 (CT of six cadavers, anterior, central and posterior body and disc height C3 to L5, PMC2900026). It also
  records that NAKO's masks (Streckenbach 2022) cover the discs from C1/2 to L5/S1 and that the Wakayama Spine Study
  grades discs from C2/3 to L5/S1 without a vertebral measure; neither releases disc heights. These are tables of means,
  not benchmarked methods, and are not repeated below.
- /home/user/bordercall/research_notes/Vertebra measures without masks/ct_intensity_methods.md, section 4: the
  training-free CT partitioners find discs as intensity valleys between bony peaks along a curved axis (Radnostics
  US 8,891,848 B2, Yao 2006, Kim and Kim 2009, Stern 2010); the only accuracy against manual disc levels is Stern 2010's
  2.8 +/- 1.9 mm for body and disc centres combined. None of them measures a disc height.
- .../masks_corners_magnification.md, line 42: Yao 2024 (QIMS) defines disc height from six landmarks as the distance
  between the bottom landmarks of vertebra i-1 and the top landmarks of vertebra i, and the disc angle from the two
  end-plate vectors. Line 101: Frobin 1997 (Clin Biomech) could not be read there; its abstract is read below.
- .../radiograph_classical_methods.md, lines 98 to 102 and 132: the Siemens patents (US 6,608,917, US 7,010,151) take the
  minimum curvature sum as the disc candidate and constrain disc thickness in dynamic programming; the Lunar patent
  (US 5,228,068) finds the intervertebral spaces as profile minima on lateral DXA; the classical cue everywhere is
  "disc = profile minimum between end-plate ridges". None reports a disc height accuracy.
- /home/user/SchwingNet/docs/research/benchmarks-to-beat.md and public-spine-and-pelvis-models-to-benchmark.md name no
  disc measure (grep for disc, intervertebral, Pfirrmann returns nothing).

## 2. Methods found

### 2.1 Radiographs, deep landmark detectors

- Yao H, Zhang Z, Cheng G, Chen X, He L, Wang W, Zhou S, Wang P. Automatic measurement of anatomical parameters of the
  lumbar vertebral body and the intervertebral disc on radiographs by deep learning. Quant Imaging Med Surg
  2024;14(8):5877-5890, doi 10.21037/qims-23-1859 [full, read at
  https://qims.amegroups.org/article/view/127000/html and PMC11320507]. Two-stage HRNet with distribution-aware
  coordinate decoding, six landmarks per vertebra (anterior, middle, posterior points of both end plates). 1,318 standing
  lateral lumbar radiographs from one hospital's PACS, split 722/305/291; vertebrae T12 to S1; body height T12 to L5,
  disc height and disc angle T12 to S1. Truth: the mean of three radiologists. Disc height: MAE 0.63 mm, ICC 0.94 (95% CI
  0.90-0.96), SD of differences 0.89 mm, mean disc height 10.40 +/- 3.91 mm; disc angle MAE 1.15 deg, ICC 0.93; body
  height MAE 0.61 mm, ICC 0.98. Anterior, middle and posterior heights are pooled; no per-position figure. Landmark PCK
  at 3 mm 94 to 99% except T12 and S1 (PCK at 1 mm 64% and 44%). Data and code: not stated as public; two authors are at
  the company whose software this is (Hangzhou Jianpei). Exclusions: implants, severe deformity, severe hyperosteogeny.
  Transitional vertebrae, magnification and level naming are not discussed; the levels are assumed from S1 upward.
- Chen Z, Wang W, Chen X, Dong F, Cheng G, He L, Ma C, Yao H, Zhou S. Deep learning-based quantitative morphological
  study of anteroposterior digital radiographs of the lumbar spine. Quant Imaging Med Surg 2024;14(8), published online
  2023-02-22 [full, https://qims.amegroups.org/article/view/110366/html; the PMC copy PMC11320550 was behind a browser
  check]. Two-stage cascaded DARK model on HRNet-32, four landmarks per vertebra (20 in all), L1 to L5 on AP films,
  disc height L1-2 to L4-5 as the mean of the left and right gaps. 1,368 AP lumbar radiographs, split 893/269/206;
  truth the mean of three radiologists. Disc height MAE / ICC by level: L1-2 0.62 / 0.84, L2-3 0.51 / 0.90, L3-4
  0.57 / 0.88, L4-5 1.88 / 0.54 (the article does not print the unit of the MAE; the body heights are in the same
  column and read as mm). Landmark PCK at 3 mm: 99.8% at L1 falling to 77.4% at L5. The authors say the model struggled
  with transitional vertebrae. Data and code not public. This is the one AP-view disc measure found, so the only one
  that approaches disc_w (the disc's transverse extent is not itself measured, only its height on the AP view).
- Yeh YC, Weng CH, Huang YJ, Fu CJ, Tsai TT, Yeh CY. Sci Rep 2021;11:7618 [full, PMC8027006]: 45 landmarks and 18
  alignment parameters on 2,210 whole-spine lateral films; none of the 18 is a disc height or disc angle; data on
  request, no code. Listed only to record that the largest public-facing whole-spine landmark model measures no disc.
- Kwak D, Ro DH, Kang DH. Automated detection of lumbosacral transitional vertebrae on plain lumbar radiographs using a
  deep learning model. J Clin Med 2025;14(21):7671 [full, PMC12610351]. ResNet-50 classifier, 3,116 standing lateral
  lumbar films (2,803 train, 313 test: 195 LSTV, 118 normal), truth from whole-spine imaging, CT or MRI. Accuracy 76.4%,
  sensitivity 85.1%, specificity 61.9%, AUC 0.84; an orthopaedic surgeon 83.9% accuracy. Binary output, no Castellvi
  type, no level named, no disc measured; data on request, no code. It is the only work found that puts the transitional
  vertebra question beside a lumbar radiograph, and it measures nothing.

### 2.2 Radiographs and scout views, classical landmark protocols

- Frobin W, Brinckmann P, Biggemann M, Tillotson M, Burton K. Precision measurement of disc height, vertebral height and
  sagittal plane displacement from lateral radiographic views of the lumbar spine. Clin Biomech 1997 [abstract,
  https://pure.hud.ac.uk/en/publications/precision-measurement-of-disc-height-vertebral-height-and-sagitta/]. Contour
  landmarks and derived parameters computed automatically from operator-traced contours; heights dimensionless, so
  independent of magnification and stature; displacement in units of mean vertebral depth. Errors from specimen films and
  serial flexion-extension films: vertebral height 2.2% (about 0.7 mm on a 30 mm body), disc height 4.15% (about 0.5 mm
  on a 10 mm disc), displacement 0.015 of vertebral depth (about 0.5 mm). Normative base 892 archive lateral lumbar
  films, ages 16 to 57. No public data, no code. This is the method the disc_index key's "disc height over body depth"
  reading descends from (distortion compensated roentgen analysis, DCRA).
- Allaire BT, DePaolis Kaluza MC, Bruno AG, Samelson EJ, Kiel DP, Anderson DE, Bouxsein ML. Evaluation of a new approach
  to compute intervertebral disc height measurements from lateral radiographic views of the spine. Eur Spine J 2017
  [full, PMC5350627]. Modified DCRA that does not depend on vertebral shape: disc height is the sum of the perpendicular
  distances from the superior and inferior six-point landmarks to a midline joining the adjacent end-plate midpoints,
  anterior, mid and posterior averaged "if desired". 1,186 Framingham participants aged 50 and over, lateral CT scout
  images T4 to S1, 13 levels, six points per vertebra placed by SpineAnalyzer (Optasia) after operator centroids.
  Standard versus modified DCRA concordance 0.9998 (lumbar) and 0.9997 (thoracic); intra-operator ICC 0.79 and 0.84,
  inter-operator 0.85, lower in the upper thoracic spine; standard DCRA left 13.9% of discs unevaluable or excluded,
  the modified 3.3%. Supine scouts only; no public data or code; levels counted by the operator.
- Hipp JA, Grieco TF, Newman P, Patel VV, Reitman CA. Reference data for diagnosis of spondylolisthesis and disc space
  narrowing based on NHANES-II X-rays. Bioengineering 2024;11(4):360 [full, PMC11048070, first 100,000 characters].
  Neural networks plus coded logic (Spine CAM, Medical Metrics Inc., FDA-cleared; three authors hold stock) place four
  corner landmarks on L1 to S1 of the NHANES-II lateral lumbar films; metrics for 36,051 levels, L1-L2 to L5-S1, with
  1,041 levels (2.8%) unmeasured. Method 1 gives anterior and posterior disc height, disc angle and sagittal offset;
  method 2 (after Frobin) ventral and dorsal disc height and mid-plane angle; also an average disc height and a
  shoelace disc area. No scaling object on the films, so every height is a percentage of the AP width of the inferior
  vertebra's superior end plate, which sidesteps magnification rather than correcting it. About half the levels were
  trimmed (osteophyte or sclerosis flagged by a network, abnormal width or height-to-width ratios, outside the 95% CI),
  so the tables describe normal discs only. No accuracy against manual readers on real films; simulated films give a
  median error of 0.13 SD in average disc height, about 1 SD when far out of plane. Images public through the CDC;
  reference tables in Supplementary File S5; the landmarking code is proprietary. Transitional vertebrae not addressed.
  Films are side-lying, 86.9% white, under-representing women and older adults.

### 2.3 MRI, segmentation then measurement

- Zheng HD, Sun YL, Kong DW, Yin MC, Chen J, Lin YP, Ma XF, Wang HS, Yuan GJ, Yao M, Cui XJ, Tian YS, Wang YJ.
  Deep learning-based high-accuracy quantitation for lumbar intervertebral disc degeneration from MRI (BianqueNet).
  Nat Commun 2022;13:841 [full, PMC8837609]. DeepLabv3+ with added modules on mid-sagittal T2 slices; five discs L1/L2
  to L5/S1 from four Chinese hospitals; data set A 223 subjects and B 63 subjects split into train and test (sizes not
  given), data set C 1,051 individuals aged 20 to 90 for the reference curves, 5,255 discs. Truth: masks in LabelMe;
  Pfirrmann by six residents with two seniors arbitrating. Mean Dice 97.03% bodies, 94.80% discs. Definitions: disc
  height DH from the central 80% of the disc area divided by the disc diameter (an area-over-length height, the
  disc_h_mean reading); DHI = 2 x DH / (VH_i + VH_i+1); HDR = DH / maximum disc diameter (a disc_index reading that
  uses the disc's own sagittal depth, so the denominator is disc_d). Agreement with the residents' mean: ICC 0.954 (DH),
  0.908 (DHI), 0.917 (HDR); inter-resident ICC 0.944, 0.913, 0.881; no absolute error in mm. Reproducibility across
  resolutions ICC 0.958 (DHI), 0.956 (HDR), 0.874 (signal difference) on 46 subjects. Code: "some of the core code" at
  github.com/no-saint-no-angel/BianqueNet [code]: main.py, function/calcu_DHI_512.py, calcu_signal_strength.py,
  quantitative_analysis.py, weights from an external pCloud link, no licence file visible. Data on request,
  non-commercial. Chinese patients only; level labelling and transitional vertebrae not described.
- Natalia F, Sudirman S, Ruslim D, Al-Kafri A. Lumbar spine MRI annotation with intervertebral disc height and
  Pfirrmann grade predictions. PLOS ONE 2024 [full, PMC11086861, first 100,000 characters]. DeepLabv3 with ResNet-50 on
  515 mid-sagittal T2 slices from the public Mendeley Lumbar Spine MRI Dataset (Sudirman 2019, 515 patients, CC BY 4.0
  [page, https://data.mendeley.com/datasets/k57fr854j2/2]); discs labelled from the sacrum upward along an A* spine
  line; disc height is the bisecting line between refined end points, converted to mm by pixel spacing; L3/L4, L4/L5,
  L5/S1 only, 1,545 discs. Truth: one radiologist's heights and Pfirrmann grades. Height error (predicted minus manual):
  first to third quartile within 1 mm, worst outlier 12.8 mm (end-plate trauma segmented as disc); no ICC or MAE.
  Pfirrmann: 88.1% mean accuracy (ensemble of decision trees, 10-fold CV), grade 5 assigned by the rule height under
  3.0 mm. Derived data public: https://data.mendeley.com/datasets/x6ggzp2ycn/1 [page], CC BY 4.0, 515 DICOM and PNG
  slices, manual masks, inferred masks, IVD mid-height per image (the Pfirrmann labels are not listed among the files).
  Code: MATLAB, not released. Levels come from counting up from the sacrum; no transitional handling.
- Kowlagi N, Kemppainen A, McSweeney T, Saarakkala S, Noailly J, Williams FMK, Cheung JPY, Karppinen J, Nguyen HH,
  Tiulpin A. Open lumbar spine image analysis (OLSIA, SpineSlicer): a 3D Slicer extension for segmentation, grading and
  intervertebral disc height index with multi-data set validation. Spine 2025;51(2):E35-E44 [full, PMC12695293;
  project page https://imedslab.github.io/spineslicer/ [page]]. Trained on NFBC1966 (n = 1,500, Finland), mid-sagittal
  T2 fat-suppressed slices, bodies L1 to S1 and discs L1/2 to L5/S1; validated on 30 participants from each of six
  external sets, two public (SPIDER, sampled from 257; Mendeley, sampled from 515) and four private (HKDDC, TwinsUK,
  CETIR, NCSD). Truth: two readers in ITK-SNAP, scored against the radiologist. Dice by set about 89 to 95 (SPIDER
  91.6, CETIR 95.2, TwinsUK 88.9), inter-rater 92.9 to 95.4; the article says it beats TotalSegmentator on bodies and
  discs. DHI = 2 x disc height / (cranial + caudal body height) from the masks. The DHI agreement printed is reader
  versus reader (mean difference 0.02, SD 0.12 to 0.13, R-squared 0.78 at L1/2 to 0.92 at L4/5 and L5/S1), not model
  versus reader; no Pfirrmann accuracy in the article. Code at the project page; licence not stated; the download is a
  Windows package. The authors name lumbosacral transitional vertebrae as needing further work and attribute the lower
  Dice on TwinsUK and SPIDER to sacral differences in transitional anatomy.
- Windsor R, Jamaludin A, Kadir T, Zisserman A. SpineNetV2: automated detection, labelling and radiological grading of
  clinical MR scans. arXiv:2205.01683, 2022 [full via ar5iv; the arXiv abstract page gives less]. Detection and level
  labelling on sagittal MRI of any field of view, grading of lumbar T2 discs T12/L1 to L5/S1. Data: Oxford Whole Spine
  (710 or 719 scans of 196 patients, private), Genodisc (2,279 patients, 2,819 scans, private, graded by one expert
  radiologist), Zukic (public, SpineWeb, 17 scans, 154 vertebrae). Identification rate (right detection and right level)
  96.5% OWS, 98.4% Genodisc, 90.9% Zukic; localisation error 1.6 to 2.4 mm. Labelling uses appearance and spatial
  context with penalties for transitional vertebrae and numerical variants and needs no anchor vertebra, but no separate
  accuracy is given for those cases. Grading, balanced accuracy on withheld Genodisc: Pfirrmann 70.9% (5 classes), disc
  narrowing 76.3% (4 classes), end-plate defects 84.9/89.6%, marrow changes 88.9/88.2%, spondylolisthesis 95%, central
  canal stenosis 93.2% binary. Disc narrowing is an ordinal grade, never a height in mm. Code: github.com/rwindsor1/SpineNet
  [code]; LICENCE.md allows research use only, no commercial use [full]. The first SpineNet (Jamaludin 2017, Med Image
  Anal 41:63-73) trained on disc-level labels without masks; McSweeney et al, Spine 2023 [full, PMC9990601] validated it
  on 1,331 NFBC1966 participants (6,655 discs, L1-L2 to L5-S1): Pfirrmann balanced accuracy 78%, kappa 0.68; Modic 86%,
  kappa 0.74; disc narrowing was not evaluated; they name transitional vertebrae as "a major challenge", since a
  mislabelled L5/S1 shifts every level.
- Hess M, Gao K, Tibrewala R, Inamdar G, Bharadwaj U, Chin C, Pedoia V, Majumdar S (UCSF). Towards clinical translation
  of fully automatic segmentation and 3D biomarker extraction of lumbar spine MRI. ISMRM 2021 abstract 4059 [abstract].
  Deep segmentation of bodies, discs and paraspinal muscles; disc height MAE 2.09 mm; no dataset size, truth or code.
- Shastry P et al. AI and deep learning for automated segmentation and quantitative measurement of spinal structures in
  MRI. arXiv:2503.11281, 2025 [abstract]. UNet and nnU-Net on a proprietary cervical, dorsal and lumbar MRI set; Dice
  0.94 lumbar, 0.91 cervical, 0.90 dorsal; disc height regressed in mm by a fully connected layer; no error figure, no
  data, no code. The only cervical and thoracic disc height automation found, and unverifiable.
- Molinier N, Marth AA, Sutter R, Germann C, Connolly JA, Guay-Paquet M, Schilaty ND, Weber KA, Cohen-Adad J.
  SpineReport. arXiv:2606.10021, 2026-06-08 [abstract]. Open-source pipeline over anatomical segmentations extracting 3D
  metrics of canal, cord, vertebrae, discs and foramina with cohort comparison; validated against stenosis grades
  (AUC 0.95 central canal), no disc height accuracy on the page; project page ivadomed.github.io/SpineReport, licence not
  stated.
- Huang J et al. Spine Explorer, Spine J 2020;20(4):590-599 [abstract only, via search snippet]: CNN on 50 train and 50
  test lumbar T2 sagittal MRIs of the Hangzhou Lumbar Spine Study; agreement with ImageJ measurements ICC 0.81 to 1.00;
  code not stated. Not verified at the source.
- Zhang W et al, systematic review and meta-analysis of deep learning lumbar disc segmentation [full, PMC11337880]: 45
  studies, pooled disc Dice 0.900 (95% CI 0.887-0.914, 14 studies); only three studies measured disc height or area
  automatically, with "good agreement" and no pooled figure; the one public source named is the MICCAI challenge data;
  most studies single-centre, mid-sagittal, retrospective, high risk of bias in 8 for selection and 5 for reference
  standard.

### 2.4 CT

- Tan S, Yao J, Yao L, Ward MM. High precision semiautomated computed tomography measurement of lumbar disk and
  vertebral heights. Med Phys 2013, doi 10.1118/1.4769412 [full, PMC3537710]. Operator seed, geodesic active contour
  level sets in 3D, end plates extracted by a surface level set on curvedness and normals, heights as mean distances
  between corresponding end-plate points, with anterior, middle and posterior local heights. Eight patients with
  ankylosing spondylitis scanned twice the same day, T10 to L4, four discs each. No truth; precision from repeat scans:
  disc height mean absolute difference 0.056 mm (95% limits -0.14 to 0.15 mm), rmsCV 0.94%, local disc CVs 1.27 to
  2.34%; computed local vertebral heights about 1 mm larger than manual. No public data or code; one minute per
  vertebra. The only CT disc height method with a precision figure; it is classical and tiny.
- No deep learning CT method that outputs a disc height in mm with a validation figure was found. TotalSegmentator's
  tasks vertebrae_body (CT) and total_mr carry one class intervertebral_discs, not split by level, under Apache-2.0
  [page, README]. VerSe 2019/2020 (374 scans, 355 patients, CC BY-SA 4.0 data, MIT code) annotates vertebral masks and
  centroids with labels for L6 and T13 and no disc [page, github.com/anjany/verse]. CTSpine1K (1,005 CTs, over 11,100
  vertebrae) labels vertebrae only [abstract, arXiv:2105.14711]. So no public CT set carries disc truth; a CT disc
  height would be read from the gap between vertebral masks, as bordercall does.

### 2.5 Public datasets and challenges that carry disc truth

- SPIDER (van der Graaf IM et al, Sci Data 2024;11:264) [full, PMC10908819; Zenodo 10.5281/zenodo.10159290, CC BY 4.0].
  447 sagittal T1 and T2 series of 218 low back pain patients from four Dutch hospitals; masks of vertebrae, discs and
  canal; vertebrae numbered from the most caudal lumbar vertebra upward as 1, which "should not be interpreted as an
  anatomical label", because the field of view did not allow anatomical numbering and transitional vertebrae
  (prevalence cited about 35.5%) were neither flagged nor excluded. Per disc, one radiologist graded Modic, end-plate
  change, spondylolisthesis, herniation, narrowing, bulging (binary) and Pfirrmann 1 to 5 (training 1,240 discs,
  validation 280). Hidden test 39 studies, 97 series: Dice vertebrae 0.93 (IIS baseline) and 0.92 (nnU-Net), discs
  0.84 and 0.86, canal 0.92 and 0.92. Baseline code github.com/DIAGNijmegen/SPIDER-Baseline-IIS, Apache-2.0 [code];
  evaluation code DIAGNijmegen/SPIDER-Evaluation. No disc height in mm; no inter-reader agreement. The challenge site
  spider.grand-challenge.org answered 403.
- Mendeley Lumbar Spine MRI Dataset (Sudirman 2019) and its 2024 derivative (above): the derivative is the one public
  set found with a per-disc height in mm, from one reader, for the lowest three discs.
- IVDM3Seg, MICCAI 2018 [page, ivdm3seg.weebly.com]: 12 subjects, 24 multi-modality Dixon sets (in-phase, opposed,
  fat, water), 16 training sets from 8 subjects, at least seven lower-spine discs, binary manual masks, training data
  after a signed registration form; leaderboard best Dice 0.9112 and localisation error 0.76 mm (smartsoftV2, 10
  teams). No height, no levels named. The MICCAI 2015 T2 challenge (Zheng 2017, Med Image Anal; best Dice 91.8%, best
  localisation 0.8 mm per the search summary) could not be read: boris.unibe.ch returned an empty page.
- RSNA 2024 Lumbar Spine Degenerative Classification (LumbarDISC) [abstract, arXiv:2506.09162]: 2,697 patients, 8,593
  series, 8 institutions; canal, subarticular and foraminal stenosis graded per disc level L1/L2 to L5/S1; CC BY-NC-SA
  4.0 via Kaggle and RSNA MIRA; no disc height or Pfirrmann; transitional handling not stated.
- MRSpineSeg (CSIG challenge, 10 vertebrae and 9 discs, organiser Qianjin Feng) [search summary only; the
  paperswithcode page answered 503]: no height truth is claimed anywhere read.
- BUU-LSPINE (Thai lumbar radiographs, Appl Sci 2023) [search summary only]: vertebral corner coordinates on 400 image
  pairs by request, spondylolisthesis labels, no disc annotation.
- NHANES II lateral cervical and lumbar films: public images; the only disc truth is the NLM atlas of four grades of
  disc space narrowing [search summary, not fetched] and Hipp 2024's derived normalised tables (above).
- AASCE (scoliosis radiographs), TotalSegmentator, VerSe, CTSpine1K: no disc truth.
- TotalSpineSeg (neuropoly) [page, github.com/neuropoly/totalspineseg, LGPL-3.0]: nnU-Net two-step instance
  segmentation and labelling of vertebrae C1 to L5 and sacrum and discs C2_C3 to L5_S on MRI of any contrast, trained
  on the public whole-spine set (OpenNeuro ds005616), SPIDER and Spine Generic plus internal sets; levels fixed by four
  landmark discs (C2-C3, C7-T1, T12-L1, L5-S) and an iterative count, with localizer support when C1 or the sacrum is
  out of view; no Dice on the page, no morphometry. It is the one open tool found that labels discs by level across the
  whole spine, and it does so by counting from landmarks, so a transitional vertebra shifts the count.

## 3. Table

| Method | Dataset (public? size, modality, truth) | Code (public? licence) | Accuracy (vs what truth) | Lacks for naming levels |
|---|---|---|---|---|
| Yao 2024 QIMS, HRNet 6 landmarks [full] | Private, 1,318 lateral lumbar films, T12-S1, mean of 3 radiologists | No | Disc height MAE 0.63 mm, ICC 0.94; disc angle MAE 1.15 deg; ant/mid/post pooled | Lumbar only, one view, S1 and T12 weakest, no transitional, no magnification, levels assumed from S1 |
| Chen 2024 QIMS, HRNet-32 4 landmarks, AP view [full] | Private, 1,368 AP lumbar films, L1-L5, mean of 3 radiologists | No | Disc height MAE 0.51-0.62 (L1-2 to L3-4), 1.88 at L4-5; ICC 0.84-0.90, 0.54 at L4-5 | AP only, L5 PCK 77%, "struggled with transitional vertebrae", no magnification |
| Frobin 1997 DCRA, contour landmarks, classical [abstract] | Private, 892 lateral lumbar films plus specimens | No | Disc height error 4.15% (about 0.5 mm per 10 mm), dimensionless | Operator contours, lumbar, levels by operator |
| Allaire 2017 modified DCRA, SpineAnalyzer 6 points [full] | Private, 1,186 Framingham lateral CT scouts, T4-S1 | No (MATLAB, unreleased) | CCC 0.9998 vs standard DCRA; ICC 0.79-0.85 operator reliability; no truth | Supine scouts, operator centroids, upper thoracic weak, no transitional |
| Hipp 2024 Spine CAM, neural corner landmarks [full] | NHANES II lateral lumbar films (public images), 36,051 levels L1-S1, no reader truth | No (proprietary, FDA-cleared) | Simulated films: median 0.13 SD on average disc height; no real-film accuracy | Heights as % of end-plate width, no mm, half the levels trimmed, no transitional, side-lying films |
| BianqueNet 2022, DeepLabv3+ on mid-sagittal T2 [full] | Private (on request), 286 subjects train/test plus 1,051 reference, L1/2-L5/S1, residents' masks and Pfirrmann | Partial, github no-saint-no-angel/BianqueNet, no licence file, weights off-site | ICC vs residents: DH 0.954, DHI 0.908, HDR 0.917; Dice 94.8% discs; no mm error | Lumbar, mid-sagittal 2D, Chinese cohort, level labelling not described |
| Natalia 2024 PLOS ONE, DeepLabv3 ResNet-50 + A* labelling [full] | Public Mendeley 515 T2 mid-sagittal slices, L3/4-L5/S1, 1,545 discs, one radiologist's heights and Pfirrmann; derived set CC BY 4.0 | No (MATLAB) | Height error IQR within 1 mm, worst 12.8 mm; Pfirrmann 88.1% | Three discs only, counted up from the sacrum, single reader, no transitional |
| OLSIA / SpineSlicer 2025, 3D Slicer, 2D U-Net family [full] | NFBC1966 1,500 train (private); 6 x 30 external, SPIDER and Mendeley public; two readers | Yes, link on project page, licence not stated, Windows package | Dice 89-95 by set; DHI agreement printed only reader vs reader (SD 0.12-0.13) | Lumbar T2 fat-sup mid-sagittal only; authors name LSTV as unsolved |
| SpineNetV2 2022 (and SpineNet 2017) [full] | OWS and Genodisc private; Zukic public 17 scans; one radiologist's grades | Yes, github rwindsor1/SpineNet, research-only licence | Level identification 90.9-98.4%; disc narrowing 76.3% balanced accuracy (4 grades); Pfirrmann 70.9%; external kappa 0.68 Pfirrmann (NFBC1966) | Narrowing is a grade not a height; grading lumbar T2 only; LSTV "a major challenge" (McSweeney 2023) |
| Hess 2021 UCSF ISMRM [abstract] | Not stated | No | Disc height MAE 2.09 mm | Nothing else known |
| Shastry 2025 arXiv [abstract] | Proprietary cervical, dorsal, lumbar MRI | No | Dice 0.90-0.94; disc height "precise", no figure | Unverifiable |
| Tan 2013 Med Phys, level sets, semiautomatic CT [full] | Private, 8 AS patients x 2 scans, T10-L4 | No | Repeat-scan precision 0.056 mm disc height, rmsCV 0.94%; no truth | Seed per vertebra, 8 patients, 1 min per vertebra, no levels named |
| SPIDER baseline IIS and nnU-Net [full, code] | Public CC BY 4.0, 447 series / 218 patients, lumbar T1 and T2, masks plus one radiologist's grades incl. narrowing and Pfirrmann; hidden test 97 series | Yes, Apache-2.0 | Dice discs 0.84 / 0.86, vertebrae 0.93 / 0.92 | Labels count from the lowest lumbar vertebra and are declared non-anatomical; LSTV not flagged; no height |
| TotalSpineSeg [page] | Public whole-spine (OpenNeuro), SPIDER, Spine Generic plus internal; MRI any contrast | Yes, LGPL-3.0 | None on the page | Levels by counting from four landmark discs; no morphometry |
| TotalSegmentator vertebrae_body / total_mr [page] | TotalSegmentator's own CT and MR sets | Yes, Apache-2.0 | None for discs | One disc class, not by level |
| IVDM3Seg 2018 [page] | 12 subjects, Dixon MRI, 7+ lower discs, masks, registration form | Challenge entries, licences vary | Best Dice 0.9112, localisation 0.76 mm | No height, no level names, tiny |
| Kwak 2025 LSTV classifier [full] | Private, 3,116 lateral lumbar films, truth from whole-spine imaging/CT/MRI | No | AUC 0.84, accuracy 76.4% (surgeon 83.9%) | Binary presence only, no level, no measure |

## 4. What the family's prior art settles and does not

Settled:
- On lateral lumbar radiographs a six-landmark deep detector reaches about 0.6 mm MAE and ICC 0.94 for disc height
  against three radiologists (Yao 2024), and on AP films about 0.5 to 0.6 mm at L1-2 to L3-4 (Chen 2024); both degrade
  sharply at the lumbosacral junction (S1 PCK at 1 mm 44%; L4-5 MAE 1.88, ICC 0.54). Human reference error for disc
  height is about 0.5 mm (Frobin 1997's 4.15%). So a disc height is measurable to within reader error on a radiograph
  wherever the end plates are clear, and least measurable exactly where the level question is hardest.
- On mid-sagittal lumbar MRI, mask-derived disc height and the two ratios (DHI = 2 DH / (VH above + VH below); HDR = DH
  / disc depth) agree with readers at ICC 0.91 to 0.95 (BianqueNet), the same as inter-reader agreement; disc Dice from
  nnU-Net-class models sits at 0.84 to 0.95 depending on the set (SPIDER hidden test 0.86; OLSIA 89 to 95; meta-analysis
  0.90). The disc_index key's two readings both exist in the literature: Frobin's dimensionless height over vertebral
  depth on radiographs and BianqueNet's DHI over body heights on MRI.
- Public truth for disc height in mm barely exists: one derived Mendeley set (515 slices, lowest three discs, one
  reader, CC BY 4.0). SPIDER gives masks and ordinal narrowing, not heights. No public CT set has disc truth; CT disc
  height automation is one 2013 semiautomatic study of eight patients.
- Degeneration grading (Pfirrmann, narrowing) is ordinal everywhere: SpineNet's narrowing is a four-grade balanced
  accuracy of 76%, Pfirrmann kappa 0.68 externally; none of these outputs a height.
- disc_w (transverse width) and disc_d (AP depth) are measured by no benchmarked method found. BianqueNet's maximum
  disc diameter on the mid-sagittal slice is the only disc_d-like quantity, used as a denominator and not validated on
  its own. Chen 2024's AP film gives a height, not a width. The search for axial disc dimension automation was not run
  (budget).

Not settled:
- No method found reads a vertebral level from a disc measure. Every pipeline assigns levels by counting (from S1 or the
  sacrum upward: Yao, Natalia, SPIDER's non-anatomical numbering, TotalSpineSeg's landmark count) or by appearance
  context (SpineNetV2), and every one that mentions transitional vertebrae calls them unsolved (Chen 2024, OLSIA 2025,
  McSweeney 2023, SPIDER). The one LSTV detector on radiographs (Kwak 2025) is a binary classifier at AUC 0.84 that
  measures nothing. So the prior art gives disc heights per counted level, never a level per disc height.
- Per-position heights: only Yao 2024 (pooled), Tan 2013 (CT, 8 patients) and Allaire 2017 (averaged "if desired")
  measure anterior, middle and posterior separately; no published accuracy by position exists in what was read.
- Magnification: radiograph methods either ignore it (Yao, Chen) or normalise it away (Frobin, Hipp); none corrects it.
- Cervical and thoracic disc height automation: only normative tables (Yukawa 2012, Busscher 2010, from the earlier
  note) and one unverifiable preprint (Shastry 2025). Allaire 2017 reaches T4 on scouts with lower reliability.

## 5. Gaps

- Could not be read: PMC11320550 (Chen 2024, read instead at the QIMS page), the Nature and Springer article pages
  (redirect to a sign-in; read the PMC copies instead), SpineNetV2's arXiv PDF (too large; read ar5iv), Zheng 2017
  (MICCAI 2015 IVD challenge; boris.unibe.ch returned an empty page, so its 91.8% Dice and 0.8 mm figures rest on a
  search summary), spider.grand-challenge.org (403), the MRSpineSeg paperswithcode page (503), the NLM NHANES II disc
  narrowing atlas pages, Huang 2020 Spine Explorer (abstract via search summary only), the BUU-LSPINE paper (search
  summary only), the second halves of Hipp 2024 and Natalia 2024 (first 100,000 characters read).
- Searches not run because the shared web search budget was exhausted: automatic axial disc width and AP depth
  measurement (disc_w, disc_d); cervical radiograph disc height landmark detectors; the MICCAI 2015 IVD challenge data
  terms; confirmation of VerSe's disc-free labels at the paper rather than the repository (the repository was read).
- Not found at all: a deep method with a disc height validated in mm on CT; any method validated on transitional
  vertebrae; any public set with anterior, middle and posterior disc heights by expert readers; the licence of OLSIA
  and of BianqueNet's partial code.
