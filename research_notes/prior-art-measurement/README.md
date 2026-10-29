# How prior art has measured the vocabulary's measures

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, step 3 of
../clinical-reread/HANDOFF.md (the owner's ask of 2026-10-29 for how prior art measures these measures, with
benchmarked public test sets and code). Web reading by one reader a measure family, each note tagging every claim
with its reading status; nothing fetched into git but links and numbers. Confidential, like the rest of this
repository. Written in the state it was in when the owner asked for it on 2026-10-29 at 23:05 UTC: seven family
notes finished, two still being read (end-plates, alignment); those two land in a later commit of the same pull request or a following one.

Starting points, read first by every reader so nothing already found was searched again: SchwingNet's
docs/research/morphometry-beyond-the-42-papers.md, benchmarks-to-beat.md and
public-spine-and-pelvis-models-to-benchmark.md, and the four notes under "../Vertebra measures without masks/".

## The families

| Family | Keys | Note | Methods tabled | Public test set with the family's truth | Public code | Closest to naming levels |
|---|---|---|---|---|---|---|
| Vertebral body dimensions | h_ant, h_mid, h_post, h_lat, body_w_mid, body_d_mid, body_w, body_d, body_area, wedge, body_index | [vertebral-body.md](vertebral-body.md) | 18 | 4, none with reader-measured heights, widths or depths by level (VerSe gives Genant grades without heights) | 2 (HealthiVert-GAN, MIT, weights not released; one unvalidated height script) | Palm 2025's T1 to L5 height-ratio matrices from TotalSegmentator masks; Hipp 2022's NHANES II ratios and wedge angles over 97,000 bodies, which acknowledge mislabelling at transitional vertebrae; VertXNet with the public C2 and S1 reference labels on NHANES II |
| Facets | facet_w_sup ... facet_gap (21 keys) | [facets.md](facets.md) | 16 | 1 (Fujiwara grades on the public Sudirman lumbar MRI set, truth at kappa 0.13); no public set carries any facet angle, area, width or interfacet distance | 4 (SPINEPS, Apache-2.0; Nikpasand, CC BY-NC-ND; one CT facet OA file; SpineToolkit, licence unstated) | Masharawi 2004's transverse facet angle by level over 4,080 dry vertebrae T1 to L5, bimodal at the thoracolumbar junction; SPINEPS's articular-process masks, which the lab's census masks already hold; no automatic CT or radiograph facet measurement exists, and no facet-based level naming anywhere |
| Posterior elements (processes, laminae, costal and uncovertebral articulations) | spinous_length ... rib_articulation_area (21 keys) | [posterior-elements.md](posterior-elements.md) | about 15 | 2 (SPINEPS on SPIDER's 218 MRI subjects, Apache-2.0, no per-subregion Dice; RibSeg v2 on 160 RibFrac CTs, rib labels 1 to 24 at 91.5 percent); public truth without a method: LumASe, 663 lumbar vertebrae with lamina, transverse and spinous process by three physicians, CC BY 4.0 | 3 (SPINEPS, RibSeg, TotalSegmentator's vertebrae_body and 24 rib classes) | Da Mutten 2026's nnU-Net over seven thoracolumbar subregions (Dice 0.98 to 0.99 externally, data private); LumASe as the test set for a lamina or process measurer; RibSeg v2 with the T12-rib cue for the rib keys; nothing automated measures any key in mm or degrees against a reader, nothing at all for the uncovertebral or costal articulation areas, and no method handles 11 or 13 rib pairs |
| End-plates | endplate, endplate_depth, endplate_lower, endplate_lower_depth, the areas, inclinations, wedge and concavity | end-plates.md (being read) | | | | |
| Pedicles | pedicle_w, pedicle_h, the areas, inclinations, chord, length, cortex, pars | [pedicles.md](pedicles.md) | 20 | 2 (Goerres 2017's atlas on SpineWeb sets 2 and 5, three levels only; Burgin 2023's graph network on the public VID keypoint set, 2,118 CTs with two pedicle points a vertebra, CC BY-SA 4.0, VerSe's L6 and T13 among them); public truth without a method: LumASe's pedicle voxel masks; C2-Net's set behind an IEEE DataPort subscription | 3 (PedicleScrewGuide GPL-3.0, SonoGym, a C2-Net fragment), none validated for a pedicle measure, and no public code computes a pedicle width, height or angle | Knez and Vrtovec 2020's automatic width and height on 540 thoracic pedicles (0.44 and 0.56 mm MAD, private); Zhang 2024's lumbar landmark CNN (ICC 0.97 width, 0.92 axial angle, private); nothing covers C2 to S1 in one person, handles a transitional vertebra, measures inner and outer width, cortex or pars automatically, or gives a pedicle width in mm on a radiograph |
| Canal and foramina | canal_w, canal_ap, canal_area, canal_index, interpedicular, lateral_recess, foramen_h, foramen_w, foramen_area | [canal-and-foramina.md](canal-and-foramina.md) | 19 | 6 (SPIDER's canal masks, Dice 0.92, which refuses level labels since sagittal MRI cannot resolve transitional vertebrae; RSNA 2024's lumbar stenosis set; three lumbar MRI stenosis sets); 13 private; no public set carries a canal or foraminal chord in mm | 5 (the SPIDER baseline, Saravi 2023, CTM-DuraSeg, LSS-MRI-AISSLab, SpineNetV2 non-commercial) | Netherton 2020's canal CNN as the counting axis, 94 percent level identification on CT with no transitional handling; Zhang 2024's CT interpedicular distance, ICC 0.91, MAE 1.25 mm, private; no CT method measures Panjabi's canal width or depth per level against public truth, the lateral recess is only graded, and foraminal millimetres exist only at L4-L5 in 100 MRI subjects |
| Discs | disc_h_ant, disc_h_mid, disc_h_post, disc_h_mean, disc_index, disc_w, disc_d | [discs.md](discs.md) | 17 | 7 | 6 | Yao 2024's lateral lumbar radiograph disc height (MAE 0.63 mm); BianqueNet 2022's disc height index and ratio on MRI (ICC 0.91 to 0.95); SpineNetV2 with McSweeney 2023's level identification at 91 to 98 percent, which calls the lumbosacral transitional vertebra a major challenge; no method reads a level from a disc measure, no deep method gives a CT disc height, and disc_w and disc_d are measured by nothing |
| Sagittal alignment and pelvic parameters | alignment | alignment.md (being read) | | | | |
| Counts and anomalies | rib, sacrum, prevalence | [counts-and-anomalies.md](counts-and-anomalies.md) | 23 | 10 (the VerSe entrants Payer, Lessmann and Chen; Lessmann 2019; Elton in part; VERIDAH's stump-rib sibling; RibSeg v2; the CTSpine1K and CTSpinoPelvic1K baselines; SpineNetV2's Zukic subset) | 9 (the VerSe tooling, Payer, SPINEPS and VERIDAH Apache-2.0, CTSpine1K, CTSpinoPelvic1K, TotalSpineSeg, Moeller's rib segmentation, RibSeg, BUU-LSPINE) | VERIDAH, the one labeller that models 11 to 13 thoracic and 4 to 6 lumbar vertebrae (96 to 97 percent anomaly recall on in-house CT, over-calling T13 on the project's own screen); the VerSe challenge's 47 L6 and 6 T13, where the hidden L6 beat almost every entrant; Kwak 2025, the one radiograph LSTV detector, binary at 76 percent and below a surgeon; no automatic Castellvi grading, no cervical or lumbar rib detector with data, no radiograph method reporting a transitional stratum, no pooled prevalence meta-analysis |

## What the finished families say about naming levels

- No public dataset carries per-level expert measurements of a vertebral body, a facet or a posterior element
  against which a measuring method is scored; the public truth is masks (VerSe, TotalSegmentator, CTSpine1K,
  SPINEPS's labels), fracture grades (VerSe's Genant grades) or landmarks (NHANES II's proprietary six-point
  landmarks, with public C2 and S1 anchors on Zenodo 10223910). A method that names levels from a measure is
  therefore scored today against masks' level labels, which the segmentation sets themselves mislabel at
  transitional vertebrae, as Hipp 2022 and ImaLife's level misnumbering in 95 of 632 people record.
- Level-dependent prior art exists in the literature's own tables rather than in code: Masharawi 2004's facet
  angles by level and Palm 2025's height ratios by level are the kind of table the paper-tables record pools, and
  neither is wrapped in a public tool.
- What is public and runnable: SPINEPS (Apache-2.0) for subregion masks including the articular processes;
  TotalSegmentator for vertebra masks; HealthiVert-GAN's code without weights. Everything that measures a
  dimension in millimetres from those masks is either unpublished, a one-file script with no validation, or
  validated only in percent on cadaver CT.

## Gaps

Each note lists what could not be read (RSNA, Springer, Nature, Spine, Wiley and MDPI pages refused from the
cloud session; read through PMC, PubMed, arXiv and university records where those exist) and what the search
budget did not reach (the vertebral-body reader ran out before Comp2Comp and the width, depth and area queries).
