# How prior art has measured the vocabulary's measures

Source: thread "Plan clinical reread next steps", project symphony_2, 2026-10-29, step 3 of
../clinical-reread/HANDOFF.md (the owner's ask of 2026-10-29 for how prior art measures these measures, with
benchmarked public test sets and code). Web reading by one reader a measure family, each note tagging every claim
with its reading status; nothing fetched into git but links and numbers. Confidential, like the rest of this
repository. Written in the state it was in when the owner asked for it on 2026-10-29 at 23:05 UTC: three family
notes finished, six still being read; the six land in a later commit of the same pull request or a following one.

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
| Pedicles | pedicle_w, pedicle_h, the areas, inclinations, chord, length, cortex, pars | pedicles.md (being read) | | | | |
| Canal and foramina | canal_w, canal_ap, canal_area, canal_index, interpedicular, lateral_recess, foramen_h, foramen_w, foramen_area | canal-and-foramina.md (being read) | | | | |
| Discs | disc_h_ant, disc_h_mid, disc_h_post, disc_h_mean, disc_index, disc_w, disc_d | discs.md (being read) | | | | |
| Sagittal alignment and pelvic parameters | alignment | alignment.md (being read) | | | | |
| Counts and anomalies | rib, sacrum, prevalence | counts-and-anomalies.md (being read) | | | | |

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
