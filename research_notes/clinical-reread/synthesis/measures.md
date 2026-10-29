# Every measure, as a recipe for a CT mask and a radiograph

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29: the synthesis of the 43 checked notes in ../notes/, drafted by one writer, read by an accuracy critic and four completeness critics, fixed and checked again.

Every statement cites a note by its id and the paper's printed page, as (eisenstein1977 p. 175); each id is the note ../notes/<id>.md, linked from the table of section 1. A statement drawn from a note's own reasoning, not from its paper, says "Inference:" and gives its arithmetic or its source. The generator's keys come from schwingcheck/measures.py and schwingcheck/mnemonics.py, and the archive's measurer is archive/bordercall/spineps_map.py; a statement about that code cites the file.

## How to read this part

The generator, schwingcheck, draws each vertebra's dimensions from Panjabi's four papers: panjabi1991c (C2 to C7), panjabi1991t (T1 to T12), panjabi1992 (L1 to L5) and panjabi1993f (the facets, C2 to L5). Those four describe one sample: 12 fresh autopsy spines, 8 men and 4 women, mean 46.3 y (19 to 59), 67.8 kg, 167.8 cm, cleaned to dry bone and digitised with a 3D morphometer, sexes pooled (panjabi1992 p. 299; panjabi1993f p. 1299; panjabi1991t p. 889 Table 1). Their tables print means with the standard error of the mean over 12 spines, so the between-spine SD is SEM x sqrt(12) = SEM x 3.46 (panjabi1992 pp. 301 to 304; panjabi1991c pp. 863 to 865). Inference: every "SD" quoted for Panjabi below is that product.

For each measure, five headings follow:

- (a) Definitions: every definition in the set, by paper, marked SAME where the landmarks and frame are Panjabi's and DIFFERS where they are not, with the sign of the bias a mask value taken by that other definition would carry against the generator.
- (b) Mask recipe: one consolidated recipe for a 3D CT instance mask. Every recipe is Inference unless a page is cited, because no paper in the set measured a segmentation mask.
- (c) Radiograph: how to take the measure from a lateral or an AP radiograph alone, and what magnification does to it.
- (d) Course C2 to S1: the values stitched across papers, where the measure peaks or bottoms out, and which adjacent levels it separates or fails to.
- (e) Covariates: sex, age, stature, ethnicity, disease.

"Separates" means an adjacent-level step that is large against the between-person SD of the same series (Inference: a step of more than about one SD is called a separation, less than half an SD a failure). The generator's error terms (1 mm per length, sqrt(pi A / 2) for an area, 3 deg per angle, schwingcheck/measures.py) are not repeated per measure.

Contents:

1. The sources.
2. The frame, the labels and the operations.
3. The vertebral body.
4. End-plate concavity.
5. Disc heights.
6. The canal.
7. The pedicles.
8. The facets.
9. Laminae and processes.
10. Ribs and costal facets.
11. The feature-extraction specification, one row per generator key.
12. What the set does not give.

The prevalence of anomalies, the junction criteria and the decoder's priors are in the part "Anomalies, numbering and the junctions". Error terms and covariate models are in the part "Measurement error, modality agreement and covariates". This part points to them and does not repeat them.

## 1. The sources: what every count is made of

| id | Who, and how many | Living, cadaver or dry bone | Modality | Levels |
|---|---|---|---|---|
| [abbas2021](../notes/abbas2021.md) | Israel; 165 with degenerative stenosis (80 M, 85 F) and 180 controls (90 M, 90 F), aged 40 and over (abbas2021 p. 2) | living | CT, axial and midsagittal reformats | L1-L5 |
| [ahmed2019](../notes/ahmed2019.md) | India (Telangana); 80 adults with back pain (36 M, 44 F), 20-70 y (ahmed2019 p. 22) | living | MRI 1.5 T, 4 mm slices | L1-L5 |
| [ahn2001](../notes/ahn2001.md) | USA; 32 adults with Marfan syndrome (18 F, 14 M), compared with Hinck's normals (ahn2001 p. 68) | living | AP and lateral radiographs | L1-L5 |
| [alonge2021](../notes/alonge2021.md) | Nigeria (Lagos); 120 abdominal CTs (66 F, 54 M) (alonge2021 p. 71) | living | CT | L1-L5 |
| [amonookuofi1982](../notes/amonookuofi1982.md) | Nigeria (Ilorin); 290 AP films (150 M, 140 F), 20-45 y (amonookuofi1982 p. 226) | living | AP film at 100 cm, not corrected | L1-L5 |
| [amonookuofi1985](../notes/amonookuofi1985.md) | Nigeria (Ibadan); lumbar sets of 122 adults (79 M, 43 F), 23-60 y (amonookuofi1985 p. 69) | dry bone | vernier caliper | L1-L5 |
| [arockiaraj2025](../notes/arockiaraj2025.md) | Saudi Arabia (Riyadh); 300 adults (150 M, 150 F), 18-60 y (arockiaraj2025 p. 314) | living | CT, 2.5 mm axial | L1-L5 |
| [bach2019](../notes/bach2019.md) | USA (Tampa); 240 abdominal CTs (131 F, 109 M), 10-80 y (bach2019 p. e107) | living | CT, 3D models | discs T12/L1-L5/S1 |
| [bonczar2024](../notes/bonczar2024.md) | 1481 people summed over 18 published studies, 1076 of them Asian (bonczar2024 p. 3 Table 1) | mixed | random-effects meta-analysis | L1-L5 |
| [busscher2010](../notes/busscher2010.md) | Netherlands; 6 male cadaver spines, mean 72 y, 182 cm, 132 vertebrae (busscher2010 p. 1105) | fresh-frozen cadaver, discs intact | CT, 1 mm | C3-L5 |
| [chaudhary2015](../notes/chaudhary2015.md) | India (Haryana); 300 AP films (150 M, 150 F), 25-40 y (chaudhary2015 p. 34) | living | AP film, not corrected | L1-L5 |
| [chen2011](../notes/chen2011.md) | 83 CT patients (Inference: 43 M, 40 F), 21-65 y, 830 end plates; a check on 10 cadaver spines (chen2011 p. 1815) | living and cadaver | CT, 0.625 mm reformats | T10 inf to L3 sup |
| [cizmic2023](../notes/cizmic2023.md) | Bosnia (Sarajevo); 200 CTs (100 M, 100 F) with lumbar pain (cizmic2023 p. 201) | living | CT, 2 mm | L1-L5 |
| [duman2026](../notes/duman2026.md) | Turkey (Izmir); 517 adults (277 M, 240 F) (duman2026 p. 3) | living | CT, 0.625 mm | T11-L2, 12th rib |
| [eisenstein1977](../notes/eisenstein1977.md) | South Africa; 443 skeletons (113 Caucasoid, 162 Zulu, 168 Sotho), 2,166 lumbar vertebrae; film substudy 55 vertebrae of 11 skeletons (eisenstein1977 p. 173) | dry bone | caliper, calibration films | L1-L5 |
| [frontphys2026](../notes/frontphys2026.md) | China; 100 adults (46 M, 54 F by Table 1), 20-70 y (frontphys2026 p. 3) | living | CT | L1-L5 bodies |
| [gilad1985](../notes/gilad1985.md) | Healthy working men 20-38 y (Inference: Israel); 141 cervical and 157 lumbar lateral films (gilad1985 p. 115) | living | lateral film, magnification corrected | C2-C7, L1-L5 |
| [griffith2016](../notes/griffith2016.md) | Hong Kong; 1,080 adults (540 M, 540 F), 21-80 y (griffith2016 p. 672) | living | CT, mid-pedicle axial | L1-L5 |
| [hinck1966](../notes/hinck1966.md) | USA (Portland); 474 AP films, 121 of adults (hinck1966 p. 141) | living | AP film at 40 in, not corrected | C3-L5 |
| [hou1993](../notes/hou1993.md) | China (Xian); 40 T9-L5 columns (25 M, 15 F) (hou1993 p. 1851) | dry bone | caliper | T9-L5 |
| [italianmri](../notes/italianmri.md) | Italy; 604 adults (302 M, 302 F), 20-45 y, transitional vertebrae excluded (italianmri p. 2) | living | MRI 1.5 T | L1-S1 |
| [krag1988](../notes/krag1988.md) | USA (Vermont); 41 patients (27 M, 14 F), 91 vertebrae, 182 pedicles (krag1988 p. 27) | living | CT, 4 mm | T9-L5 |
| [kunkel2011](../notes/kunkel2011.md) | 72 thoracic motion segments from 30 donors (15 F, 15 M), mean 57 y (kunkel2011 p. 375) | cadaver | contact films and sections | C7-T12 |
| [lien2007](../notes/lien2007.md) | Taiwan; 15 dry T1-L5 sets (8 M, 7 F); 6 cadavers for T11-L5 (lien2007 p. 1216) | dry bone and cadaver | caliper, goniometer | T1-L5 |
| [makino2012](../notes/makino2012.md) | Japan; 50 preoperative patients (23 M, 27 F), 52-85 y (makino2012 p. 1516) | living | CT, 1.25 mm | L1-L5 |
| [masharawi2021](../notes/masharawi2021.md) | Israel; 100 CTs, 50 spondylolisthesis and 50 controls (25 M, 25 F each), 50-80 y (masharawi2021 p. 2) | living | CT | L1-L5 |
| [mitra2002](../notes/mitra2002.md) | India (Nagpur); 20 cadavers (18 M, 2 F) (mitra2002 p. 453) | cadaver | direct, CT 5 mm, films | L1-L5 |
| [moncadahabib2025](../notes/moncadahabib2025.md) | Mexico; 37 patients (Inference: 20 M, 17 F), 185 vertebrae (moncadahabib2025 p. 2) | living | CT, 1 mm | L1-L5 |
| [olsewski1990](../notes/olsewski1990.md) | USA (Buffalo); 49 embalmed cadavers (24 M, 25 F), 60-98 y; 21 also filmed and scanned (olsewski1990 p. 542) | embalmed cadaver | direct, AP film, CT | L1-L5 |
| [otsuki2021](../notes/otsuki2021.md) | USA; 6 fresh-frozen spines (3 M, 3 F), 50-67 y, 60 pedicles; first author Irie (otsuki2021 p. 2) | cadaver | micro-CT, 34.4 um | L1-L5 |
| [panjabi1991c](../notes/panjabi1991c.md), [panjabi1991t](../notes/panjabi1991t.md), [panjabi1992](../notes/panjabi1992.md), [panjabi1993f](../notes/panjabi1993f.md) | 12 fresh autopsy spines, 8 M, 4 F, mean 46.3 y (panjabi1992 p. 299) | dry bone | 3D morphometer | C2-L5 |
| [robertson2000](../notes/robertson2000.md) | 10 dry lumbosacral spines; 100 lumbar and 20 S1 pedicles (robertson2000 p. 709) | dry bone | wire-marked films | L1-L5, S1 |
| [shin2024](../notes/shin2024.md) | USA (Loma Linda); 700 adults (350 M, 350 F), 18-35 y (shin2024 p. 2) | living | CT | discs L1/2-L5/S1 |
| [tan2004](../notes/tan2004.md) | Singapore; 10 Chinese cadavers, sex not reported, mean 65.7 y, 220 vertebrae (tan2004 p. 137) | dry bone | 3D digitiser | C3-L5 |
| [tang2016](../notes/tang2016.md) | USA (Utah); 109 adults (55 F, 54 M), 20-40 y, 318 discs (tang2016 p. 4117) | living | MRI 1.5 T | L3-S1 discs and end plates |
| [twomey1985](../notes/twomey1985.md) | 204 cadaver lumbar blocks (Inference: Western Australia) (twomey1985 p. 496) | cadaver | dissection, calipers | discs L1/2-L5/S1 |
| [vanderhouwen2009](../notes/vanderhouwen2009.md) | Netherlands; 77 patients (46 M, 31 F), 21-86 y, 25 end plates per position (vanderhouwen2009 p. 34) | living | CT, 0.75 mm | T12 inf to S1 sup |
| [yadav2020](../notes/yadav2020.md) | India (Inference: Lucknow); 302 adults (174 M, 128 F), 20-40 y (yadav2020 p. 176) | living | CT | T12-S1 |
| [yu2015](../notes/yu2015.md) | USA (Hamann-Todd collection); 503 skeletons (404 M, 99 F), 17-93 y (yu2015 p. 1640) | dry bone | digital caliper | L1-L5 |
| [zindrick1987](../notes/zindrick1987.md) | USA; specimens and clinical CTs of unstated number; 2,905 measurements (zindrick1987 p. 160) | cadaver films and living CT | axial films, CT | T1-L5 |

## 2. The frame, the labels and the operations every recipe uses

### 2.1 Panjabi's frame

Panjabi set each vertebra in its own frame before measuring anything. Four points digitised at the left and right, upper and lower corners of the posterior wall of the body define, by least squares, the frontal plane; the transverse and sagittal planes are perpendicular to it; X runs to the vertebra's left, Y cranially and Z anteriorly; the origin is the centre of the upper end plate (panjabi1993f p. 1299; panjabi1991t p. 889; panjabi1992 p. 299). tan2004 built the same frame from the posterior wall because that wall changed least with osteophytes (tan2004 p. 139). Every area is the root-sum-square of the three projected areas, which is the vector area of the outline (panjabi1993f p. 1300; panjabi1992 p. 300). Method accuracy on a Plexiglas phantom was under 5% for lengths, angles and areas, and the point-location error +/-0.5 mm (panjabi1992 p. 300; panjabi1991t p. 889). A naming pitfall for whoever transcribes the thoracic tables: in panjabi1991t the suffix l means lower in the end-plate rows (Table 2 p. 890) and left in the pedicle, costotransverse and pars rows (Tables 5 to 7 pp. 894 to 895), and CVAll is lower-left (panjabi1991t note).

Why it matters for a mask: a width or a depth taken along scanner axes mixes lordosis, kyphosis and scoliosis into the value; at L4 and L5, lordotic tilt inflates end-plate depth and posterior height (panjabi1992 note, generator section). The archive measurer takes every extent along RAS scanner axes after canonicalising the image (archive/bordercall/spineps_map.py, measure_vertebra and axes_from), so all of its values carry this bias.

### 2.2 Recipe F: build the vertebral frame from an instance mask

Inference throughout, after Panjabi's construction (panjabi1991t p. 889; panjabi1991t note, frame; panjabi1993f note, frame section; tan2004 note, common frame):

1. Take the body subregion of the instance. In SPINEPS that is label 49 (Vertebra_Corpus_border) with the end-plate labels 52 and 53 (archive/bordercall/spineps_map.py, label table).
2. Find the dorsal surface of the body: body voxels that border the canal side, between the pedicle roots. Fit a plane to them by least squares (PCA, least-variance axis). Its normal pointing away from the canal is +Z.
3. Set X parallel to the line through the two cranial (superior) corners of that wall, right to left, projected into the wall's plane, as Panjabi set it through his points A and B (panjabi1991t p. 889). Set Y = Z x X, which points cranially. A Y taken from the midpoints of the wall's caudal and cranial edges differs from this by the wall's in-plane skew, which changes the frontal and sagittal parts of every angle (EPIt, PDI, facet T and S, UJI); if that construction is kept for robustness, store both and report the angle between the two X axes.
4. Set the origin at the centroid of the cranial end-plate surface voxels.
5. Rotate the instance into this frame and measure every quantity below in it. Store the rotation, so that a fluoroscopic view angle can later be expressed against the same frame.

### 2.3 What SPINEPS labels give and do not give

- Labels: 41 arch (laminae, pedicles and process bases together), 42 spinous process, 43 and 44 costal (transverse) processes left and right, 45 and 46 superior articular processes, 47 and 48 inferior articular processes, 49 body, 52 and 53 superior and inferior end plates, 60 cord, 61 canal, 62 unassigned end plate, 100 disc (archive/bordercall/spineps_map.py).
- No pedicle label: the pedicle lies inside label 41, so it must be cut out geometrically (otsuki2021 note, isthmus section; yu2015 note, mask recipe). The archive measurer refuses pedicle width and height for that reason (archive/bordercall/spineps_map.py).
- Label 61 is the canal's contents along the column, not one vertebra's bony foramen, so it is the wrong object for canal width and depth (panjabi1992 note, generator section; cizmic2023 note).
- No ribs: rib articulations cannot be read from a vertebra mask (panjabi1991t note, CVA section).

### 2.4 Operations used below

- O1, end-plate surface: the voxels of label 52 or 53, or the outermost 1 to 2 mm of label 49 along Y. Use the rim (the outline of the face projected on its fitted plane), not the curved surface, for widths, depths and areas (panjabi1992 note, generator section).
- O2, vector area: triangulate the outline or surface (marching cubes), sum the triangle area vectors and take the length of the sum. This equals Panjabi's root-sum-square of projected areas (panjabi1993f p. 1300). A scalar mesh area reads high on a curved face (panjabi1992 note, generator section).
- O3, pedicle isthmus: on each side take the arch voxels between the dorsal body wall and the branching of the transverse and articular processes. Take section centroids at the anterior and posterior thirds of that bridge; the line through them is the pedicle axis. Reslice perpendicular to the axis in 0.5 mm steps, fit an ellipse by second moments to each section, and keep the section with the shortest minor axis (otsuki2021 p. 3, the method of its ref. 18, built for clinical CT). Record which section and which axis was used.
- O4, facet plane: the boundary voxels of an articular process (labels 45 to 48) that lie within 2 to 3 mm of the partner process of the neighbouring instance; fit a plane by PCA; orient the normal up and back (panjabi1993f note, frame section). The superior facets of C2 need C1, the inferior facets of L5 need S1, in the segmentation.
- O5, ray cast: march along a ray through the instance mask and record where it enters and leaves bone.

### 2.5 Magnification and other projection effects

Inference: a structure at distance OFD from the film, with source-to-image distance SID, is enlarged by M = SID / (SID - OFD); a ratio of two lengths at about the same depth cancels M.

| Source | Setting | Factor or effect |
|---|---|---|
| eisenstein1977 | 110 cm tube-film, measured on 55 vertebrae of 11 skeletons | AP 1.14, lateral 1.23 (eisenstein1977 p. 175) |
| hinck1966 | AP spine at 40 in against PA chest at 72 in, interpedicular distance | AP spine 0.57 mm larger on average; 1.10 mm at T1-T3, 0.38 mm at T4-T12 (hinck1966 pp. 148 to 149 Table IV) |
| hinck1966, ahn2001, amonookuofi1982, chaudhary2015 | film values not corrected (40 in, 101 cm, 100 cm, not stated) | values carry M; Inference: about 1.05 to 1.17 by the formula above |
| gilad1985 | lateral films corrected to the midsagittal plane for parallax | correction error up to +/-1.0 mm; combined method error up to 10% cervical, under 5% lumbar (gilad1985 p. 119) |
| kunkel2011 | contact films, scale on the rig | anterior disc height reads 9% short and posterior 37% short against sections (kunkel2011 p. 375) |
| robertson2000 | wire-marked dry pedicles | the densest film image of the pedicle lies 1 to 3 mm inside the true outer cortex (robertson2000 p. 711) |
| olsewski1990 | AP film against direct measure | pedicle width L5 3.5 mm low; height 1.5 to 1.8 mm high at L1-L3, 2.4 mm low at L5 (olsewski1990 p. 544 Table II) |
| mitra2002 | lateral film against direct | pedicle height within 0.9 mm; sagittal angle 3.4 to 6.1 deg low (mitra2002 p. 455 Table 2) |
| panjabi1991c | lateral view against midsagittal posterior height | lateral reads 1.8 to 3.0 mm higher, because the uncovertebral region projects above the midline (panjabi1991c p. 868 Table 7) |
| panjabi1993f | facet angles | a lateral film reads the angle to the transverse plane accurately only where the facet is near-sagittal; axial CT reads the angle to the sagittal plane accurately only where the facet is near-vertical (panjabi1993f p. 1309) |

## 3. The vertebral body

### 3.1 End-plate width: endplate (EPWu), endplate_lower (EPWl)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Lateral width of the digitised end-plate loop along the frame's X; the cervical upper width is drawn between the bases of the unci, the lower across the lower corners (panjabi1991c p. 862 Fig 1; panjabi1991t p. 891 Fig 3A; panjabi1992 p. 300 Fig 1, p. 301) | SAME; this is the generator |
| tan2004 | Panjabi's drawings and frame, digitiser on dry bone; cervical upper width between the uncinate processes (tan2004 p. 138 Fig 1a, p. 139) | SAME landmarks; 10.2% (upper) and 10.4% (lower) below Panjabi on average, a population and age difference (tan2004 p. 144 Table 2) |
| busscher2010 | Side-to-side width, horizontal arm of a crosshair with the midline depth line, CT reformat in the vertebra's plane (busscher2010 p. 1105 Fig 1) | DIFFERS at C3-C7: the values (27.6 mm at C3 against Panjabi's 15.8) fit a full body width that includes the unci (Inference); elsewhere 4 to 8 mm above Panjabi in six men 182 cm tall |
| yadav2020 | UVW, LVW: lateral borders of the body "in the plane of" the upper or lower end plate, axial CT; the example slice looks mid-body (yadav2020 p. 176 Fig 1C) | DIFFERS in plane: a slab inside the plate, not the rim; lower than upper at L5 in men, unlike Panjabi (yadav2020 note, LVW) |
| vanderhouwen2009 | T: rim-to-rim chord between the right and left rim points in the frontal plane through the widest body points (vanderhouwen2009 p. 35) | DIFFERS: rim to rim, about 5 mm below an outer extent (vanderhouwen2009 note, T); reads low |
| chen2011 | TD: rim-to-rim chord on the coronal section through the deepest point of the end plate (chen2011 p. 1815, p. 1819) | DIFFERS: not the maximum width (chen2011 p. 1819); reads low |
| frontphys2026 | Outermost lateral edges of the end plate; plane ambiguous, values fit a mid-coronal width (frontphys2026 note, EPWu) | SAME in kind; within about 0.2 to 1.8 mm of Panjabi at L1-L4, but 3.4 mm above at L5 for the upper plate and 3.0 for the lower (Inference: 50.7 - 47.3 and 52.4 - 49.4, frontphys2026 p. 5 Table 2); its SDs of 0.6 to 1.0 mm are implausibly small (frontphys2026 note) |
| bonczar2024 | Pooled mediolateral extent; its Fig 2 swaps the width and depth labels (bonczar2024 p. 4 Fig 2) | pooled from mixed definitions |
| tang2016 | FD: lateral side of the bounding rectangle of one oblique MRI slice at the end plate (tang2016 p. 4119 Table 1) | DIFFERS: MRI soft-tissue edge, one 3 to 4.5 mm slice |
| abbas2021 VW, eisenstein1977 Body T.V., amonookuofi1982 B, moncadahabib2025 CW | Waist widths at mid-height, axial CT or dry bone or AP film (abbas2021 p. 2; eisenstein1977 p. 173; amonookuofi1982 p. 226; moncadahabib2025 p. 2 Fig 1) | DIFFERS: a waist is narrower than a plate; never feed these to the generator |
| archive measurer | Lateral extent of label 52 (53) along the scanner's left-right axis (archive/bordercall/spineps_map.py) | DIFFERS in frame: scanner axes; see the bias below |

Biases a mask value carries against the generator (Inference unless cited):

- Scanner axes: the extent along a scanner axis of a plate of width w and depth d turned by an angle a about the vertical is w cos a + d sin a. At a = 10 deg, w = 45 and d = 35 mm that is 44.3 + 6.1 = 50.4 mm, 5.4 mm high. Rotate into recipe F first.
- Unci: at C3 to C7 an extent of the whole cranial surface includes the uncinate processes and reads high (tan2004 note, generator section; panjabi1991c p. 868, where the end-plate areas exclude the uncovertebral surfaces).
- Marginal lipping and ring apophysis: the dry-bone loop included them (panjabi1992 note, EPW mask recipe); a mask that drops a thin rim reads low by about one voxel per side.

(b) Mask recipe

1. Build frame F (section 2.2).
2. Take the cranial end-plate surface by O1 (label 52, or the top 2 mm of label 49 along Y). For endplate_lower take label 53 or the bottom 2 mm.
3. Project the surface onto its own fitted plane and take the extent along the in-plane direction nearest X.
4. At C3 to C7 for the upper plate only: drop the uncinate processes. Inference: remove the cranial-surface voxels that lie more than 2 mm above the fitted end-plate plane at the lateral margins, then take the extent.
5. Report one value per plate in mm.

(c) Radiograph

AP view only: the width of the end-plate line between its lateral corners, divided by the AP magnification (1.14 at 110 cm tube-film, eisenstein1977 p. 175). The upper and lower plates superimpose unless the beam is parallel to the disc (tan2004 note, EPW radiograph). A lateral view cannot give it. The ratio of width to depth (below) needs both views but no magnification once each view is corrected.

(d) Course, mm (Panjabi T1 to T12 from panjabi1991t p. 892 Table 3; C2 to C7 from panjabi1991c p. 863 Table 2; L1 to L5 from panjabi1992 p. 301 Table 2; tan2004 pp. 140 to 141 Table 1; busscher2010 p. 1109 Fig 3, values read from the figure; yadav2020 men, p. 178 Table 3; vanderhouwen2009 rim-to-rim T, p. 37 Fig 2)

| Level | Panjabi EPWu | Panjabi EPWl | tan2004 u / l | busscher2010 u / l | yadav2020 men u / l | vanderhouwen2009 T, sup / inf |
|---|---|---|---|---|---|---|
| C2 | - | 17.5 | - | - | - | - |
| C3 | 15.8 | 17.2 | 13.8 / 14.3 | 27.6 / about 24 | - | - |
| C4 | 17.2 | 17.0 | 14.7 / 15.0 | 26.4 / - | - | - |
| C5 | 17.5 | 19.4 | 14.9 / 15.9 | 27.6 / 27.6 | - | - |
| C6 | 18.5 | 22.0 | 15.8 / 19.5 | 30.3 / 28.0 | - | - |
| C7 | 21.8 | 23.4 | 19.0 / 20.3 | 31.5 / 30.7 | - | - |
| T1 | 24.5 | 27.8 | 24.7 / 27.1 | 28.8 / 35.4 | - | - |
| T2 | 24.9 | 27.4 | - / 25.3 | 26.8 / 35.0 | - | - |
| T3 | 24.6 | 25.9 | - / 24.4 | 27.2 / 33.9 | - | - |
| T4 | 24.5 | 26.0 | 22.5 / 25.0 | 27.1 / 33.5 | - | - |
| T5 | 24.9 | 27.0 | 23.3 / 23.8 | 29.3 / 34.2 | - | - |
| T6 | 26.2 | 28.2 | 23.7 / 24.8 | 31.6 / 35.0 | - | - |
| T7 | 27.8 | 29.1 | 24.6 / 26.8 | 33.7 / 35.9 | - | - |
| T8 | 29.5 | 30.5 | 25.9 / 27.9 | 35.2 / 38.2 | - | - |
| T9 | 30.6 | 33.0 | 27.0 / 29.2 | 38.0 / 39.4 | - | - |
| T10 | 31.9 | 35.4 | 28.8 / 31.9 | 39.9 / 43.3 | - | - |
| T11 | 34.9 | 39.1 | 31.6 / 35.3 | 44.1 / 46.5 | - | - |
| T12 | 39.0 | 42.1 | 34.5 / 36.4 | 46.5 / 48.9 | 36.99 / 39.30 | - / 36.93 |
| L1 | 41.2 | 43.3 | 36.3 / 39.2 | 48.7 / 50.4 | 40.15 / 42.26 | 36.28 / 37.33 |
| L2 | 42.6 | 45.5 | 38.2 / 41.4 | 50.3 / 51.2 | 42.55 / 44.35 | 36.16 / 37.43 |
| L3 | 44.1 | 48.0 | 39.9 / 43.5 | 51.8 / 53.9 | 44.34 / 46.66 | 37.18 / 39.66 |
| L4 | 46.6 | 49.5 | 42.0 / 45.3 | 53.8 / 53.2 | 46.42 / 46.86 | 40.01 / 44.63 |
| L5 | 47.3 | 49.4 | 41.6 / 43.7 | 53.8 / 53.9 | 48.79 / 46.93 | 41.73 / 44.10 |
| S1 | - | - | - | - | 49.08 / 30.78 | 41.24 / - |

tan2004's upper widths at T2 and T3 are not in its note; it says the upper width falls slightly from T1 to T4 (tan2004 p. 139). Other lumbar series: frontphys2026 EPWu 41.8, 43.4, 45.2, 47.7, 50.7 and EPWl 44.8, 45.7, 48.7, 51.3, 52.4 (frontphys2026 p. 5 Table 2); bonczar2024 pooled EPWU 41.09, 42.98, 44.82, 47.50, 48.81 and EPWL 43.97, 46.10, 49.12, 50.63, 49.82 (bonczar2024 pp. 5 to 9 Tables 2 to 6); tang2016 FD, MRI, 4.78, 4.79, 4.83 cm for the inferior plates of L3, L4, L5 and 5.05, 5.21, 5.19 cm for the superior plates of L4, L5, S1 (tang2016 p. 4120 Table 4; tang2016 note, structures).

Where it peaks, bottoms out and separates:

- Cervical: EPWu rises from C3 to C7; it jumps 3.3 mm from C6 to C7, and C7 differs significantly from C3 to C6 (panjabi1991c p. 863 Table 2). EPWl does not rise from C3: it is flat from C2 to C4 (17.5, 17.2, 17.0), then rises +2.4 mm at C4/C5 (1.56 SD) and +2.6 at C5/C6 (1.31 SD); EPWl C6 differs from C2 to C4 and C7 from C2 to C5, and the paper places the greatest lower-width increase at C6 (panjabi1991c p. 863 Table 2; panjabi1991c note, EPW; the SD multiples are Inference from the long table). tan2004 has the same upper step (+3.2 mm C6 to C7) and a larger one into T1 (+5.7 mm) (tan2004 note, EPW).
- C7 to T1: +2.7 mm upper, +4.4 mm lower in Panjabi (computed from the two tables). Inference: +2.7 mm upper is 1.03 SD and +4.4 mm lower is 1.57 SD (SEM 0.64 to 0.98 x 3.46, mean SD 2.6 and 2.8 mm), so the lower plate separates C7 from T1 and the upper only just does; both are weaker than the transverse-process step (section 9.2).
- T1 to T5: flat, 24.5 to 24.9 mm (panjabi1991t p. 892 Table 3); EPWl even dips to 25.9 at T3. Fails to separate any pair in T1 to T5.
- T5 to T12: rises 1.1 to 4.1 mm per level, steepest T10 to T12 (+3.0, +4.1). Inference: each step from T5 to T10 is under one SD (SEM 0.67 to 1.06, SD 2.3 to 3.7 mm).
- L1 to L5: rises about 14% (panjabi1992 p. 301); only L4 and L5 differ from L1, and no adjacent pair differs (panjabi1992 p. 301 Table 2). The lower width plateaus at L4-L5 (49.5, 49.4). Living CT does not share the plateau: frontphys2026's EPWl rises +1.1 mm from L4 to L5 against Panjabi's -0.1 (frontphys2026 p. 5 Table 2).
- S1: the superior S1 plate is narrower than the L5 inferior plate on CT rim chords (41.24 against 44.10, vanderhouwen2009 p. 37 Fig 2) and yadav2020's S1 lower width collapses to 30.78 mm because its "lower plate" is the fused S1-S2 junction (yadav2020 note, LVW).
- Within a vertebra the lower plate is wider than the upper at every thoracic and lumbar level of Panjabi, by 1.0 (T8) to 4.2 mm (T11) in the thorax and 2.1 (L1, L5) to 3.9 mm (L3) in the lumbar spine (computed from panjabi1991t p. 892 and panjabi1992 p. 301). busscher2010 disagrees in the neck: its lower width is below the upper at C3-C4 and 5 to 8 mm above it at T1-T5 (busscher2010 p. 1109 Fig 3). yadav2020 disagrees at L5 in living men: lower below upper by 1.9 mm (yadav2020 note, LVW). chen2011 disagrees at T12 on living CT (83 patients, rim-to-rim chords): T12's superior and inferior widths do not differ, 38.0 against 37.6 mm in men (P 0.674) and 32.9 against 33.1 in women (P 0.848), while at T11, L1 and L2 the superior is about 91% of the inferior (all P < 0.008) (chen2011 p. 1817; Table 3 p. 1818). Panjabi has T12's lower plate 3.1 mm wider (42.1 against 39.0).
- Width over depth, a size-free ratio: cervical lower 1.12 (C2), 1.10, 1.07, 1.08, 1.19, 1.39 (C7) (panjabi1991c p. 863 Table 2); thoracic 1.3 (upper) and 1.4 (lower) at T1, near 1.0 for the upper plate from T4 to T10 and for the lower only from T5 to T8, rising to 1.12 at T10 and 1.2 to 1.3 at T12 (panjabi1991t p. 890, p. 892 Table 3; the T10 lower ratio is Inference from the means, panjabi1991t note); lumbar lower 1.23, 1.30, 1.38, 1.46, 1.49 (panjabi1992 p. 301 Table 2). Inference: the lower ratio rises 0.07 to 0.08 per level from L1 to L4, the most regular gradient among the body measures (panjabi1992 note), and the C6 to C7 rise (1.19 to 1.39) marks C7.

(e) Covariates

- Sex: men wider by 2.4 to 3.2 mm (6.1 to 8.7%) at every level from T12 to S1 for the upper plate, by 1.0 to 2.7 mm for the lower (yadav2020 p. 178 Table 3; 174 men, 128 women, living, CT). Female over male median rim chord 0.88 (vanderhouwen2009 p. 39 Table 2; 46 men, 31 women). Panjabi pooled 8 men and 4 women (panjabi1992 p. 299).
- Population: Chinese Singaporean dry bone runs 0.86 / 0.91 / 0.90 of Panjabi in the cervical / thoracic / lumbar spine (tan2004 note, generator section, from p. 144 Table 2). Six Dutch men of 182 cm read 4 to 8 mm above Panjabi in the thoracolumbar spine (busscher2010 p. 1109 Fig 3).
- Stenosis: no end-plate width in abbas2021; its waist width differs by group (abbas2021 p. 4 Table 1).

### 3.2 End-plate depth: endplate_depth (EPDu), endplate_lower_depth (EPDl)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Anteroposterior extent of the end-plate loop along Z, anterior rim to posterior rim, in the side view (panjabi1992 p. 300 Fig 1, p. 301; panjabi1991c p. 862) | SAME |
| tan2004 | Panjabi's landmarks along Z; Inference in its note: take it at the midline (tan2004 p. 138 Fig 1) | SAME landmarks; 15.6% (upper) and 14.7% (lower) below Panjabi (tan2004 p. 144) |
| busscher2010 | Dorsal-to-ventral depth along the midline, vertical arm of the crosshair (busscher2010 p. 1105 Fig 1) | SAME in kind; 2 to 5 mm above Panjabi in its six tall men |
| gilad1985 | c (upper) and a (lower): the superior and inferior body corners P1-P2 and P3-P4 on a lateral film, corrected to the midsagittal plane (gilad1985 p. 117) | SAME in kind; lumbar values within 1 mm of Panjabi (computed from gilad1985 p. 118 Table 1 and panjabi1992 p. 301) |
| yadav2020 | UVD, LVD: anterior to posterior ends of the body in the plane of the plate, midline, stopping at the canal (yadav2020 p. 176 Fig 1C) | DIFFERS: 2 to 6 mm below Panjabi (yadav2020 note, UVD) |
| vanderhouwen2009 | S: rim to rim on the sagittal tangent line, points 1 and 5 (vanderhouwen2009 p. 35) | DIFFERS: rim to rim; an outer mask extent runs 6 to 8 mm larger (vanderhouwen2009 note, S) |
| chen2011 | SD: rim to rim on the midsagittal plane (chen2011 p. 1815) | DIFFERS: reads low |
| tang2016 | APD: anteroposterior side of the bounding rectangle; MSD: the midline chord, which stops at the posterior notch (tang2016 p. 4119 Table 1) | APD close to an outer extent; MSD reads low by an amount that depends on level. Inference (tang2016 note, MSD, from Table 4 p. 4120): MSD/APD is 0.88 to 0.90 at L3/L4, 0.91 to 0.93 at L4/L5 and 0.99 at L5/S1, a ratio of means with no per-subject spread; so a midline depth reads 2.7 to 4.5 mm short above L5/S1 (the notch, APD - MSD) and about equal at L5/S1 (0.4 to 0.5 mm). That is a soft L5/S1 shape cue, but the notch is about one between-subject SD, so never use it alone (tang2016 note, instruction 3) |
| bonczar2024 | Pooled anteroposterior extent (bonczar2024 p. 4 Fig 2, labels swapped) | pooled |
| eisenstein1977, amonookuofi1985, abbas2021 VL, krag1988, italianmri VBD, moncadahabib2025 CL, alonge2021 VAPD | Mid-height or mid-waist body depth (eisenstein1977 p. 173; amonookuofi1985 p. 72; abbas2021 p. 2; krag1988 p. 28; italianmri p. 2; moncadahabib2025 p. 2; alonge2021 p. 71) | DIFFERS: a waist depth is 1 to 5 mm below an end-plate depth; never feed these to the generator |
| archive measurer | Anteroposterior extent of label 52 (53) along the scanner axis (archive/bordercall/spineps_map.py) | DIFFERS in frame: lordotic tilt inflates depth at L4-L5 (panjabi1992 note, generator section) |

Inference, the tilt bias: a plate of depth d and thickness t tilted by an angle b in the sagittal plane has a scanner-axis extent of d cos b + t sin b; for d = 35 mm, a 2 mm slab and b = 20 deg that is 32.9 + 0.7 = 33.6 mm, so a thin plate reads slightly low, while a thick slab of the whole body (t = 24 mm) reads 32.9 + 8.2 = 41.1 mm, far high.

(b) Mask recipe

1. Build frame F.
2. Take the plate surface by O1.
3. In the midsagittal band |X| <= 3 mm (Inference), take the extent of the plate along Z from the anterior rim to the posterior rim, including the ring apophysis.
4. Do not take the maximum Z extent of the whole body: posterolateral lobes and osteophytes reach further (tang2016 note, APD against MSD).

(c) Radiograph

Lateral view only: the end-plate line from anterior to posterior corner, divided by the lateral magnification (1.23 at 110 cm, eisenstein1977 p. 175). Corrected living films match Panjabi's lumbar dry-bone depths within about 1 mm (gilad1985 p. 118 Table 1; panjabi1992 p. 301 Table 2). The beam must be tangent to the plate (vanderhouwen2009 note, S radiograph); a double contour means it is not.

(d) Course, mm (sources as in 3.1, plus gilad1985 p. 118 Table 1)

| Level | Panjabi EPDu | Panjabi EPDl | tan2004 u / l | busscher2010 u / l | gilad1985 c / a | yadav2020 men u / l |
|---|---|---|---|---|---|---|
| C2 | - | 15.6 | - | - | 12.6 / 15.3 | - |
| C3 | 15.0 | 15.6 | 13.6 / 15.1 | 16.5 / - | 14.8 / 15.6 | - |
| C4 | 15.3 | 15.9 | 14.0 / 15.2 | about 17 / - | 15.5 / 15.8 | - |
| C5 | 15.2 | 17.9 | 14.3 / 15.1 | about 17 / 19.4 | 15.5 / 16.1 | - |
| C6 | 16.4 | 18.5 | 14.6 / 15.7 | 19.5 / 20.4 | 16.0 / 16.6 | - |
| C7 | 18.1 | 16.8 | 15.1 / 15.6 | 19.9 / 18.5 | 16.4 / 16.3 | - |
| T1 | 18.5 | 19.7 | 14.9 / 15.8 | 18.8 / 20.0 | - | - |
| T2 | 19.6 | 21.6 | 16.3 / 17.7 | 19.9 / - | - | - |
| T3 | 22.7 | 23.3 | 18.0 / 19.0 | 22.2 / - | - | - |
| T4 | 23.3 | 24.5 | 18.9 / 20.0 | 24.1 / - | - | - |
| T5 | 24.3 | 25.8 | 20.5 / 21.6 | 26.4 / - | - | - |
| T6 | 26.0 | 26.9 | 21.8 / 23.0 | 28.7 / - | - | - |
| T7 | 27.4 | 28.5 | 22.7 / 23.5 | 30.3 / - | - | - |
| T8 | 27.9 | 29.4 | 23.3 / 24.7 | 32.2 / - | - | - |
| T9 | 29.3 | 31.0 | 24.4 / 25.5 | 34.5 / - | - | - |
| T10 | 30.5 | 31.6 | 25.4 / 26.2 | 33.7 / - | - | - |
| T11 | 31.9 | 31.8 | 25.4 / 26.9 | 35.2 / 35.8 | - | - |
| T12 | 32.8 | 33.4 | 26.7 / 27.7 | 35.6 / about 34.8 | - | 27.09 / 27.88 |
| L1 | 34.1 | 35.3 | 27.5 / 28.5 | 36.4 / 36.2 | 33.5 / 34.1 | 28.61 / 29.49 |
| L2 | 34.6 | 34.9 | 28.3 / 29.2 | 39.1 / about 37.5 | 34.4 / 34.7 | 30.37 / 30.60 |
| L3 | 35.2 | 34.8 | 29.9 / 30.2 | 39.5 / about 37.5 | 34.7 / 34.6 | 31.37 / 31.25 |
| L4 | 35.5 | 33.9 | 30.8 / 30.3 | 37.9 / 37.7 | 34.3 / 34.9 | 31.56 / 32.15 |
| L5 | 34.7 | 33.2 | 30.4 / 28.7 | 36.7 / 36.2 | 34.2 / 33.9 | 32.41 / 31.66 |
| S1 | - | - | - | - | - | 31.16 / 22.78 |

Rim-to-rim series: chen2011 SD, men 27.6 to 29.4 mm and women 23.8 to 26.0 mm from T10 to L3 (chen2011 p. 1819 Table 5); vanderhouwen2009 S about 27 to 28 mm from T12 inferior to S1 superior, smallest at L5 inferior (26.4) and not separating lumbar levels (vanderhouwen2009 p. 37 Fig 2). Pooled: bonczar2024 EPDU 31.04, 32.12, 33.17, 33.83, 34.09 and EPDL 32.27, 32.91, 33.76, 34.07, 33.18 (bonczar2024 pp. 5 to 9). Mid-height depths, L1 to L5: Caucasoid men 31, 32, 33, 34, 33 (eisenstein1977 p. 174 Table I); Nigerian men 29.2, 30.6, 32.2, 34.0, 32.2 (amonookuofi1985 p. 74 Table 4); about 32 mm flat from T9 to L5 (krag1988 p. 29 Fig 4); Italian MRI 26.5, 27.6, 28.9, 29.6, 29.6 and S1 22.4 (italianmri p. 4 Table 3).

Where it peaks, bottoms out and separates:

- Cervical: EPDu is flat from C3 to C5 (15.0 to 15.3) and rises at C6 and C7; C7 differs from C3 to C5 (panjabi1991c p. 863 Table 2). EPDl is not flat: it rises +2.0 mm at C4/C5 (1.28 SD, Inference from the long table), the largest lower-depth step by the paper, to a peak at C6 (18.5, which differs from C2 to C4), then falls at C7 (16.8), which the authors read as the transition to the thoracic spine (panjabi1991c p. 863, p. 867; panjabi1991c note, EPD). tan2004 is flat from C3 to T1 and cannot separate the cervical levels or C7 from T1 (tan2004 note, EPD).
- C7 to T1: EPDl +2.9 mm (16.8 to 19.7), 1.99 SD, the strongest end-plate depth step in Panjabi's series; EPDu +0.4 mm (0.16 SD); EPDl T1/T2 adds +1.9 mm (0.95 SD) (Inference from the long table, across panjabi1991c p. 863 and panjabi1991t p. 892, so it joins two papers' tables). The lower depth separates C7 from T1; the upper does not.
- Thoracic: the most nearly linear measure, about +1.3 mm per level (panjabi1991t p. 892 Table 3; tan2004 p. 139). Inference: with SD 1.4 to 4.2 mm (SEM 0.41 to 1.21 x 3.46), only T2 to T3 (+3.1 mm upper) is a one-SD step; the rest order the column but separate no adjacent pair.
- T12 to L1: +1.3 mm upper, +1.9 mm lower (Panjabi). chen2011 puts the step in rim-to-rim depth between T12 and L1 (vertebral mean 27.6 at T10-T12 against 29.3 at L1-L3 in men, chen2011 p. 1819 Table 5).
- Lumbar: flat, 34.1 to 35.5 upper, 35.3 falling to 33.2 lower, no level difference significant (panjabi1992 p. 301). Depth alone does not separate lumbar levels.
- S1: the S1 "lower depth" of 22.78 mm in yadav2020 is the fused S1-S2 junction (yadav2020 note, LVD).
- Two thoracic series read 4 to 5 mm below Panjabi, which the authors explain by a mid-body measurement (panjabi1991t p. 898); Liu's cervical depths run 1.2 to 4.1 mm below for the same reason (panjabi1991c p. 868).

(e) Covariates

- Sex: women's rim-to-rim depth is about 88% of men's (chen2011 p. 1819 Table 5; 43 men, 40 women, living CT); female over male median 0.91 (vanderhouwen2009 p. 39 Table 2); men 1.4 to 2.1 mm deeper, 4.8 to 7.9% (yadav2020 p. 178 Table 3).
- Population: tan2004's factors 0.90 / 0.83 / 0.85 of Panjabi (tan2004 note, generator section). Pakistani men deeper than yadav2020's at every level (yadav2020 p. 181 Table 8).
- Age: no age effect reported for depth in the set.

### 3.3 Body heights: h_post (VBHp), and the anterior and middle heights the generator lacks

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Height of the body at the posterior wall between the end plates; cervical: midsagittal (panjabi1992 p. 300 Fig 1; panjabi1991c p. 868). Which posterior points were used is not stated (panjabi1992 note, VBHp) | SAME; no anterior height in any of the four papers (panjabi1992 p. 301 Table 1 defines the suffix a but tabulates none) |
| tan2004 | Y distance between the plates at the posterior body margin (tan2004 p. 138 Fig 1) | SAME; 4.0% below Panjabi on average, 8.2% in the lumbar spine, 12.7% at L5 (tan2004 p. 144) |
| busscher2010 | SI height at the posterior margin, lateral view of a CT reformat (busscher2010 p. 1105 Fig 1) | SAME in kind; 3 to 6 mm above Panjabi in six tall men |
| gilad1985 | d: posterior corners P2 to P4 on a corrected lateral film (gilad1985 p. 117) | DIFFERS: a projected height; 3 to 5 mm above Panjabi in the lumbar spine (panjabi1992 p. 304, p. 305 Table 6) |
| kunkel2011 | VBHP: Farfan's posterior superior and inferior corners on a contact film, magnification corrected (kunkel2011 p. 377) | 0.2 to 2 mm above Panjabi (kunkel2011 note) |
| frontphys2026, duman2026, moncadahabib2025, abbas2021, bonczar2024 | Posterior edge of the upper plate to posterior edge of the lower, midsagittal CT (frontphys2026 p. 5; duman2026 p. 4; abbas2021 p. 2) | SAME in kind, but most run above Panjabi. Inference, from the tables in (d): frontphys2026 1.7 to 3.8 mm above at L1-L5; moncadahabib2025 -0.4 to +3.1; bonczar2024 pooled 1.2 to 2.9; duman2026 men 1.8 to 2.8 at T11-L2. abbas2021 prints no height, only the ratio's plot (abbas2021 note) |
| panjabi1991c, own check | A lateral view of the cervical body reads 1.8 to 3.0 mm higher than the midsagittal height, because the uncovertebral region projects above the midline (panjabi1991c p. 868 Table 7) | lateral views bias h_post high at C3-C7 |
| archive measurer | Median column height along the scanner's SI axis in the posterior 20% of label 49 (archive/bordercall/spineps_map.py, _posterior_height) | DIFFERS in frame: columns along the scanner axis in a body tilted by b read h / cos b; at b = 20 deg that is 6.4% high, about +1.5 mm on 24 mm (Inference) |

(b) Mask recipe

1. Build frame F.
2. Take the body voxels (labels 49, 52, 53) in a slab from the posterior wall plane to 2 mm anterior of it. Inference: the archive's 20% of the depth (about 7 mm) also works, since the height changes by under 0.3 mm over 7 mm even in L5's wedge (L5 anterior minus posterior about 3 mm over 35 mm, computed from frontphys2026 p. 5 Table 2).
3. Within that slab, in the midsagittal band |X| <= 3 mm, take each column's extent along Y and report the median.
4. Record also the heights at the left and right posterior corners; Panjabi's frame points were there (panjabi1992 note, VBHp).
5. For the anterior height and the ratio below, repeat at the anterior wall; for the middle height, at the centre of the plates.

(c) Radiograph

Lateral view: the posterior wall from end plate to end plate, divided by the lateral magnification (1.23 at 110 cm, eisenstein1977 p. 175). In the neck add the 1.8 to 3.0 mm the lateral view reads above the midsagittal height to the generator's value before comparing (panjabi1991c p. 868 Table 7). The ratio of anterior to posterior height needs no magnification. On contact films of thoracic segments, intra-observer error was 1.7 to 5.1% and inter-observer agreement 0.95 to 0.98 for body heights (kunkel2011 p. 380). Inference: on an AP view the posterior wall is not seen apart from the rest of the body, yet schwingcheck's ap regime lists h_post (schwingcheck/measures.py REGIMES) while mnemonics.py marks it mask and lateral only; an AP height equals h_post only when the beam is parallel to both plates.

(d) Course, mm (Panjabi as in 3.1; tan2004 Table 1; busscher2010 p. 1107 Table 3; gilad1985 p. 118 Table 1; kunkel2011 p. 379 Table 2; duman2026 men, p. 7 Table 1; frontphys2026 p. 5 Table 2)

| Level | Panjabi VBHp | tan2004 | busscher2010 | gilad1985 d | kunkel2011 | Other |
|---|---|---|---|---|---|---|
| C2 | - | - | - | 19.0 | - | - |
| C3 | 11.6 | 11.2 | 15.1 | 14.5 | - | - |
| C4 | 11.4 | 11.3 | - | 13.9 | - | - |
| C5 | 11.4 | 11.3 | - | 13.8 | - | - |
| C6 | 10.9 | 11.3 | 13.9 | 13.9 | - | - |
| C7 | 12.8 | 11.8 | 15.9 | 14.9 | 14.38 | - |
| T1 | 14.1 | 14.0 | 18.8 | - | 15.28 | - |
| T2 | 15.6 | 15.2 | - | - | 16.11 | - |
| T3 | 15.7 | 15.3 | - | - | 17.41 | - |
| T4 | 16.2 | 15.8 | - | - | 18.15 | - |
| T5 | 16.2 | 16.4 | - | - | 17.33 | - |
| T6 | 17.4 | 17.0 | 21.7 | - | 18.22 | - |
| T7 | 18.2 | 17.4 | - | - | 18.67 | - |
| T8 | 18.7 | 17.8 | - | - | 20.05 | - |
| T9 | 19.3 | 18.0 | - | - | 20.25 | - |
| T10 | 20.2 | 19.1 | - | - | 20.35 | - |
| T11 | 21.3 | 20.4 | - | - | 22.67 | duman men 23.08 |
| T12 | 22.7 | 21.5 | 28.5 | - | 23.12 | duman men 24.83 |
| L1 | 23.8 | 22.4 | 28.5 | 27.1 | - | duman 25.94; frontphys 27.2 |
| L2 | 24.3 | 23.1 | 29.8 | 27.0 | - | duman 27.12; frontphys 28.1 |
| L3 | 23.8 | 22.1 | 29.8 | 27.9 | - | frontphys 27.3 |
| L4 | 24.1 | 21.6 | 28.0 | 27.1 | - | frontphys 26.3 |
| L5 | 22.9 | 20.0 | 24.9 | 25.7 | - | frontphys 24.6 |

Other lumbar posterior heights: bonczar2024 26.57, 27.02, 26.67, 25.76, 24.11 (bonczar2024 pp. 5 to 9); moncadahabib2025 26.9, 26.8, 26.1, 25.0, 22.5 (moncadahabib2025 p. 4 Table 1).

Where it peaks, bottoms out and separates:

- Cervical: flat C3 to C6 (10.9 to 11.6), minimum C6, and C7 differs from C6 (12.8, panjabi1991c p. 863 Table 2). busscher2010 also bottoms at C6 (13.9) (busscher2010 p. 1107 Table 3).
- C7 to T1: +1.3 mm (Panjabi), +2.9 mm (busscher2010 p. 1107).
- Thoracic: rises about 0.8 mm per level (panjabi1991t p. 892 Table 3); Inference: with SD 1.4 to 3.6 mm (SEM 0.41 to 1.04), no adjacent pair separates.
- Lumbar: flat L1 to L4 (23.8, 24.3, 23.8, 24.1), lowest at L5 (22.9), no significant difference (panjabi1992 p. 301 Table 2). Every CT series puts the maximum at L2-L3 and a drop at L5: busscher2010 L4 to L5 -3.1 mm (p. 1107), frontphys2026 L4 to L5 -1.7 mm (p. 5), moncadahabib2025 -2.5 mm (p. 4). Inference: h_post cannot separate L1 to L4; only L5's drop shows.

The anterior over posterior height ratio, magnification-free (computed from each source's means):

| Level | tan2004 | busscher2010 | gilad1985 b/d | frontphys2026 | moncadahabib2025 | abbas2021 control men |
|---|---|---|---|---|---|---|
| C3-C7 | 0.85-0.95 | 0.94-1.01 | 0.97, 0.96, 0.92, 0.94, 0.98 | - | - | - |
| T5-T12 | 0.85-0.95 | 0.88-0.92 | - | - | - | - |
| L1 | 0.90 | 0.89 | 0.94 | 0.92 | 0.90 | about 0.93 |
| L2 | 0.90 | 0.92 | 1.01 | 0.94 | 0.94 | about 0.97 |
| L3 | 0.97 | 0.96 | 1.00 | 0.99 | 0.98 | about 0.99 |
| L4 | 1.00 | 0.99 | 1.01 | 1.05 | 1.02 | about 1.03 |
| L5 | 1.10 | 1.18 | 1.10 | 1.13 | 1.16 | about 1.17 |

(tan2004 p. 139 Table 1; busscher2010 p. 1107 Table 3; gilad1985 p. 118 Table 1; frontphys2026 p. 5 Table 2; moncadahabib2025 p. 4 Table 1; abbas2021 pp. 4 to 5 Figs 5 and 6, read from figures.) duman2026 covers only T11 to L2: ACH/PCH 0.929, 0.951, 0.955 and 0.970 in 277 men and 0.924, 0.950, 0.957 and 0.966 in 240 women at T11, T12, L1 and L2 (Inference: ratios of the means of duman2026 Table 1 p. 7; duman2026 note), so anterior wedging lessens down the junction, most from T11 to T12. Inference: every series agrees that only L5 is taller in front by 10% or more, so this ratio is the strongest single body marker of L5 in the set, and it is free of magnification and patient size. It needs the anterior height the generator does not hold.

Middle (central) height: busscher2010 VBHc C3 12.6, C5 12.1, C7 14.3, T1 16.1, T6 18.1, T12 25.5, L1 24.5, L2 24.7, L3 25.5, L4 24.1, L5 25.3 mm (busscher2010 p. 1107 Table 3); frontphys2026 VBHm 23.5, 24.3, 24.4, 23.7, 23.0 (frontphys2026 p. 5 Table 2). It falls with age as the plates bow (twomey1985 p. 498 Fig 2). It belongs to end-plate concavity (section 4). duman2026's MCH lies between ACH and PCH at every level of its Table 1, against its own Fig 2A example of 27.0 / 24.2 / 27.3 mm with the middle lowest, so its printed MCH is not a mid-height that carries the concavity; do not use it as one (duman2026 p. 5, p. 7 Table 1; duman2026 note, gaps).

Two more size-free cues from frontphys2026 (100 living Chinese adults, CT). Inference (frontphys2026 note, from Table 2 p. 5): VBHm/VBHa is 0.94, 0.92, 0.90, 0.86 and 0.83 at L1 to L5, falling steadily; with VBHa/VBHp it is that paper's best L4/L5 separator; and with Panjabi's upper end-plate depths the anterior-minus-posterior height difference corresponds to a body wedge of about -3.5 deg at L1 (taller behind) and +5.1 deg at L5 (taller in front), so the wedge changes sign across the lumbar spine.

(e) Covariates

- Sex: men's posterior height 9 to 12% above women's at T11 to L2 (duman2026 p. 7 Table 1; 277 men, 240 women).
- Population: tan2004's factors 0.98 / 0.97 / 0.92 (tan2004 note, generator section).
- Age and degeneration: kunkel2011 chose only mildly to moderately degenerated segments and did not analyse age or sex (kunkel2011 p. 375); central height falls with age (twomey1985 p. 498).
- Stenosis: abbas2021's beveling ratio (AH / pH x 100) is lower in men with degenerative stenosis at L1 to L5 (Fig 5) and in women at L4 only (Fig 6). It entered the men's adjusted model at L2 (OR 0.919, 95% CI 0.852-0.991) and at L4 (OR 0.930, 0.873-0.990) (abbas2021 Table 5 p. 6; pp. 4 to 5 Figs 5 and 6).

### 3.4 End-plate area: endplate_area (EPAu), endplate_lower_area (EPAl)

(a) Definitions

- panjabi1991c, panjabi1991t, panjabi1992: the root-sum-square of the three projected areas of the digitised rim loop, which is the vector area enclosed by the rim, not the curved surface (panjabi1992 p. 300; panjabi1992 note, EPA). Cervical areas exclude the uncovertebral surfaces (panjabi1991c p. 868). SAME.
- tan2004: the best-fit plane of the outline polygonised into a triangle mesh (tan2004 p. 139). SAME in kind; its cervical lower areas exceed the product of width and depth, which no planar outline bounded by them can do, so do not fit a mask's planar area to them (tan2004 note, gaps).
- tang2016: area inside the traced outline on one oblique MRI slice at the plate (tang2016 p. 4119 Table 1). DIFFERS: a slab outline, soft-tissue edge.
- griffith2016 VB CSA: the body section at mid-pedicle (griffith2016 p. 673 Fig 1C). DIFFERS: a waist section, smaller than a plate.
- bonczar2024: pooled, with an unexplained contour in its figure (bonczar2024 p. 4 Fig 2).
- Bias of a mask value: a scalar mesh area of the curved, concave plate reads high against the vector area (panjabi1992 note, generator section).

(b) Mask recipe: take the plate surface by O1, compute its vector area by O2 (or, equivalently, the area enclosed by the plate's outline projected onto its fitted plane, panjabi1992 note EPA). At C3 to C7 exclude the unci as in 3.1 step 4.

(c) Radiograph: not measurable. An ellipse on the AP width and the lateral depth, pi x EPW x EPD / 4, stands in for the area. What each paper says and what its own table gives, side by side:

- Lumbar: under 10% over (panjabi1992 p. 305). Inference, from its Table 2: 1.7 to 7.5% over (panjabi1992 note, EPA).
- Cervical: about 10% over at every level (panjabi1991c pp. 864, 868). Inference, from its Table 2: 7 to 14% over, the measured area being 0.69 to 0.74 of W x D (panjabi1991c note, EPA).
- Thoracic: within 10% at all levels (panjabi1991t p. 900). Inference, from its Table 3: 11 to 19% over at T1 to T5 and 3 to 8% over from about T6 or T7 down, so the paper's claim fails in the upper thorax (panjabi1991t note, EPA).
- tan2004 points the other way. Its EPAu / (EPWu x EPDu) is 0.77 to 0.94 (cervical 0.77 to 0.91, thoracic 0.83 to 0.92, lumbar 0.89 to 0.94), so the ellipse's 0.785 reads about 12 to 16% low on its lumbar plates (Inference: 0.785 / 0.891 = 0.88 at L1 and 0.785 / 0.937 = 0.84 at L3, the largest ratio; tan2004 note, EPA, from Table 1 pp. 140 to 141), the opposite sign to Panjabi's. Apply neither factor to tan2004's cervical lower plates, whose areas exceed width x depth (tan2004 note, EPA).
- MRI: the APD x FD ellipse was 2% low at L3/L4 and L4/L5 and 3% high at L5/S1, with no result for the L5/S1 caudal plate; the MSD x FD ellipse was 10% low at the upper two levels (tang2016 pp. 4119, 4122).

(d) Course, mm2: cervical EPAu 169.4, 183.0, 182.9, 221.2, 278.3 (C3 to C7) and EPAl 194.4, 190.7, 199.2, 246.2, 289.9, 280.3 (C2 to C7) (panjabi1991c p. 863 Table 2); thoracic EPAu 300, 333, 373, 381, 426, 483, 547, 605, 678, 727, 842, 954 and EPAl 376, 398, 412, 444, 495, 552, 603, 664, 755, 834, 945, 1024 (panjabi1991t p. 892 Table 3); lumbar EPAu 1057, 1136, 1194, 1239, 1237 and EPAl 1117, 1197, 1290, 1273, 1218 (panjabi1992 p. 301 Table 2). tan2004 EPAu runs 154.7 (C3) to 1151.8 (L4) and 1127.3 (L5); its L3 lower area is misprinted 172.0, likely 1,172 (tan2004 note, EPA). MRI, cm2: inferior plates of L3, L4, L5 13.85, 13.75, 13.08; superior plates of L4, L5, S1 15.13, 15.15, 14.63 (tang2016 p. 4120 Table 4; tang2016 note, structures). Pooled upper area 932, 1018, 1132, 1151, 1183 (bonczar2024 pp. 5 to 9).

- The upper area grows from C3 to L4, flat at C4/C5 (183.0 to 182.9), and holds at L5 (1239 to 1237) (panjabi1991c p. 863; panjabi1992 p. 301); tan2004's upper area rises to L4 (1151.8) and falls a little at L5 (1127.3) (tan2004 Table 1 pp. 140 to 141; p. 143). The lower area is not monotone. Panjabi's EPAl falls from C2 to C3 (194.4 to 190.7), peaks at C6 (289.9) and falls at C7 (280.3) (panjabi1991c p. 863; panjabi1991c note, EPA); in the lumbar spine it peaks at L3 (1290) and falls to 1273 at L4 and 1218 at L5, with no level difference significant (panjabi1992 p. 301 Table 2; panjabi1992 note, EPA). tan2004's EPAl dips at T3 (387.1 against 399.2 at T2) and peaks at L4 (1199.3) (tan2004 Table 1 pp. 140 to 141).
- Inference, from Panjabi's long table over C3 to L5: adjacent steps run -55 to +115 mm2 (EPAu -2.0 to +115, EPAl -55 to +111) against SDs of about 20 to 223 mm2 (SEM 5.74 to 64.35 x 3.46). Four steps exceed one SD: EPAu C5/C6 +38.3 (1.44 SD), EPAu C6/C7 +57.1 (1.60 SD; C7 differs from C3 to C6, panjabi1991c p. 863), EPAl C4/C5 +47.0 (1.40 SD) and EPAl C7/T1 +95.7 (1.96 SD, a step that joins the cervical and thoracic tables). No step from T1/T2 to L4/L5 reaches 0.9 SD (largest EPAu T10/T11, +115 mm2, 0.86 SD; T11/T12 +112, 0.76 SD). So the area orders the column and marks the lower neck and C7/T1, but separates no thoracic or lumbar pair alone.
- Across one disc, Panjabi's upper vertebra's lower plate is larger than the next vertebra's upper plate (for example L3 lower 1290 against L4 upper 1239, panjabi1992 p. 301). tang2016's MRI disagrees: at each disc the superior plate of the vertebra below exceeds the inferior plate of the vertebra above, by 12% in women and 9% in men, P < 0.001 (tang2016 p. 4119). Populations: 12 dry spines against 109 living adults aged 20 to 40 on MRI. The series tang2016 compiles split three ways: Brinckmann's caudal plates are larger, as in Tang; Panjabi's and Tan's cranial plates are larger in area and width and Zhou's in depth and width; Seidel, Wang, Berry and van der Houwen are mixed (tang2016 Tables 6 and 7 pp. 4125 to 4128; tang2016 note, instruction 5).

(e) Covariates: women's plate areas are 83 to 86% of men's on MRI (tang2016 p. 4120 Table 4; computed). Body section area rises with age in women and with height (r 0.331 men, 0.264 women) (griffith2016 p. 675 Table 5). Population: tan2004's factors 0.92 / 0.92 / 0.90 upper, 1.16 / 0.91 / 0.91 lower (tan2004 note, generator section).

### 3.5 End-plate inclination and wedge: endplate_incl (EPItu), endplate_lower_incl (EPItl), endplate_wedge (EPIt)

In the pool as printed, by the owner's choice of 2026-10-29 09:01 UTC to keep all 32 measures (bordercall TODO.md step b), though this part recommended leaving out endplate_incl and endplate_lower_incl, because Panjabi's lumbar L1 to L5 rows of these two angles reprint his cervical C3 to C7 rows, so his lumbar paper most probably prints no lumbar value of either ([panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md), sections 1 and 3). As the code stands, measures.pool still takes both (the pool of 32); that note's section 3 gives the exclusion list that would drop them, and endplate_wedge is outside the pool already (no spread).

(a) Definitions

- Panjabi: the angle between the plate's least-squares plane and the frame's transverse plane, which is perpendicular to the posterior wall (panjabi1992 p. 300; panjabi1991t p. 890). Inference in both notes: an angle between planes is unsigned, so the means are of magnitudes and mix sagittal and coronal tilt (panjabi1992 note, EPIt). panjabi1991t's Fig 3B shows the upper plate sloping down anteriorly and the lower up, so its sum EPIt is an anterior (kyphotic) wedge (panjabi1991t note, EPIt).
- tan2004: the angle of each plate's best-fit plane in the side view against Z, signed: upper cephalad, lower changes sign (tan2004 p. 143 Table 1). DIFFERS: signed and sagittal only.
- bonczar2024: not defined or drawn (bonczar2024 note). Unusable.
- vanderhouwen2009 wedge of the disc: angle between the two plates facing a disc (vanderhouwen2009 p. 35). Not a vertebral wedge.

Bias of a mask value: a signed sagittal angle, or one taken against the scanner, differs from Panjabi's unsigned 3D angle; the mean of magnitudes of a near-zero angle is biased upward (panjabi1992 note, generator section).

(b) Mask recipe: fit planes to the cranial and caudal plate surfaces (O1); the angle of each plane's normal to the frame's Y axis is EPItu or EPItl, unsigned; endplate_wedge is their sum, as Panjabi printed it. Record also the signed sagittal and coronal components, since the frame-free angle between the two plates is the robust quantity (panjabi1991t note, EPIt mask).

(c) Radiograph: lateral view, the angle between each plate line and the perpendicular to the posterior body line gives the sagittal part only (panjabi1992 note, EPIt radiograph). On ten lateral films the mean angle between the two plates was 3.9 deg against 3.8 deg on bone (panjabi1991t p. 890, p. 898), with no per-level agreement statistic. No magnification correction is needed.

(d) Course, deg: cervical EPItu 2.7, 3.5, 1.7, 4.7, 2.2 (C3 to C7) and EPItl 4.2, 4.0, 2.1, 2.7, 2.7, 1.8 (C2 to C7), no level different (panjabi1991c p. 863 Table 2); thoracic EPItu 1.8, 1.7, 2.4, 1.5, 2.1, 2.1, 1.6, 1.3, 0.9, 0.5, 2.3, 2.2 and EPItl 3.9, 1.9, 2.1, 2.3, 2.0, 1.8, 2.2, 2.3, 1.2, 1.2, 2.2, 1.8, EPIt 5.7, 3.6, 4.5, 3.8, 4.1, 3.9, 3.8, 3.6, 2.1, 1.7, 4.5, 4.0, summing to 45.3 deg (panjabi1991t p. 892 Table 3); lumbar EPItu 2.7, 3.5, 1.7, 4.7, 2.2 and EPItl 4.0, 2.1, 2.7, 2.7, 1.8 as printed, a reprint of the cervical C3 to C7 rows (panjabi1992 p. 301 Table 2; below). tan2004, signed: the lower plate's sign changes at C7/T1 (+5.1 to -2.9) and its L5 value is +10.5 deg (tan2004 p. 143 Table 1).

- A copy in the source: the cervical Table 2 at C3 to C7 and the lumbar Table 2 at L1 to L5 carry the same 20 numbers in the same order, mean and SEM alike (2.7 +/- 0.77, 3.5 +/- 1.5, 1.7 +/- 0.43, 4.7 +/- 1.1, 2.2 +/- 0.54 upper; 4.0 +/- 0.84, 2.1 +/- 0.4, 2.7 +/- 1.1, 2.7 +/- 0.69, 1.8 +/- 0.42 lower) (panjabi1991c p. 863 Table 2; panjabi1992 p. 301 Table 2, both read on the page images). That one set is printed twice is near certain; which paper holds the original is probable but not proven, most probably the cervical, whose text describes the row (panjabi1991c p. 864) while no lumbar text names it. If so, the lumbar rows are cervical numbers. The two same-definition lumbar series in reach put the L5 lower plate far from the printed 1.8: tan2004 at 10.5 deg, and Tan 2002 at about 12 by a back-out from bonczar2024's pool ([panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md), sections 1 and 2.2). Hence both angles are left out of the pool for now, at C3 to C7 as well, since the pool runs over C3 to L5 (that note, section 3).
- None of these angles separates adjacent levels; the lumbar values have no trend (panjabi1992 note, EPIt). The thoracic wedge falls to 2.1 and 1.7 deg at T9 and T10 and rises again at T11 (panjabi1991t p. 892).

(e) Covariates: none reported; Panjabi pooled.

### 3.6 Waist and mid-height dimensions (no generator key)

These are not plate measures and enter no generator key; they are listed so they are never mixed with endplate or endplate_depth.

| Source | Population and method | Waist width L1-L5 (mm) | Mid-height depth L1-L5 (mm) |
|---|---|---|---|
| abbas2021 (p. 4 Table 1) | 90 control men, axial CT at mid-height | 39.7, 40.9, 42.8, 44.7, 49.1 | 29.9, 31.1, 32.6, 32.8, 32.9 |
| abbas2021 (p. 4 Table 1) | 90 control women | 35, 36.8, 38.8, 40.8, 45 | - |
| amonookuofi1982 (p. 231 Table 4) | 150 men, AP film at 100 cm, not corrected, narrowest waist | 41.3, 42.9, 45.8, 49.6, 52.8 | - |
| amonookuofi1982 (p. 231 Table 4) | 140 women, as above | 37.5, 39.7, 42.5, 45.7, 50.5 | - |
| eisenstein1977 (p. 174 Table I) | Caucasoid men, dry bone | 39, 40, 43, 44, 46 | 31, 32, 33, 34, 33 |
| amonookuofi1985 (p. 74 Table 4) | 79 men, dry bone, mid-waist | - | 29.2, 30.6, 32.2, 34.0, 32.2 |
| moncadahabib2025 (p. 4 Table 1) | 37 patients, CT; what CW and CL are is inferred from Fig 1, whose labels do not match its drawn lines, so take the values from Table 1 only (moncadahabib2025 p. 2; its note, instruction 14) | 40.3, 42.2, 44.0, 45.5, 49.5 | 29.4, 30.8, 31.7, 31.8, 32.4 |
| griffith2016 (p. 675 Table 5) | 540 men, body section area at mid-pedicle, mm2 | 1201, 1273, 1399, 1512, 1711 | - |

Inference: waist widths run 1 to 5 mm below Panjabi's end-plate widths at the same level, and mid-height depths 2 to 5 mm below his end-plate depths. A waist width is what an AP radiograph shows most clearly, so a radiograph pipeline should measure the plate lines, not the waist, or carry a separate waist reference.

## 4. End-plate concavity (no generator key)

(a) Definitions

- vanderhouwen2009: perpendicular distance from surface points to a least-squares plane through four rim points; sagittal profile at the posterior quarter, middle and anterior quarter, frontal at three matching points (vanderhouwen2009 p. 34 to 35).
- chen2011: sagittal concave angle A-Cm-P with its vertex at the deepest point on the midsagittal plane (180 deg is flat); the deepest point's position from the posterior rim as a share of the depth; the coronal angle R-Cs-L (chen2011 p. 1815).
- busscher2010 and frontphys2026: indirectly, as the central height against the mean of the anterior and posterior heights (busscher2010 p. 1107 Table 3; frontphys2026 p. 5 Table 2).
- twomey1985: disc convexity index M / (A + P), which mirrors the plates' concavity (twomey1985 p. 497).

(b) Mask recipe (Inference): on each plate in frame F, fit a plane to the rim (the outermost ring of plate voxels); sample the plate surface along the midsagittal line and along the frontal line through the deepest point; report the largest perpendicular depth, its position from the posterior rim as a share of the depth, and the sagittal angle A-Cm-P. Use 0.75 mm or finer voxels: the depths are 1 to 3 mm.

(c) Radiograph (Inference, vanderhouwen2009 note): on a true lateral the sagittal profile is the dip of the plate below the line joining its anterior and posterior corners; on AP the frontal profile; double contours and tilt spoil it.

(d) Course

- Depth: smallest anteriorly, largest in the middle or posteriorly; maximum posterior at T12 and L1 inferior plates, middle at L3 to L5 inferior; inferior middle depth rises from 1.46 mm at L1 to 2.96 mm at L5, about 0.3 mm per level; superior plates flatter, 0.83 (L1) to 1.42 mm (S1) (vanderhouwen2009 pp. 36 to 37 Fig 2; 77 living patients). Every inferior plate is deeper than the superior plate across the same disc (vanderhouwen2009 p. 37). Inference in its note: the inferior over superior middle ratio across a disc is largest at L4-L5 (2.5) and L5-S1 (2.1); one vertebra's value only shifts odds between upper and lower lumbar.
- Angle: about 163 deg, flat from T10 inferior to L3 superior (ANOVA P 0.843); deepest point at 42.5 to 44.2% of the depth from the posterior rim; coronal angle 170.9 to 175.7 deg; superior flatter than inferior at T12, L1 and L2 (chen2011 p. 1817 Table 1; 83 living patients). The angle on CT agreed with cadavers within 0.3 deg (162.4 against 162.1, chen2011 p. 1818 Table 4). Inference in its note: depth about 1.9 to 2.2 mm in men, 1.65 to 1.9 in women. It does not separate T10 to L3.
- Indirect: busscher2010's central over mean marginal height is 0.85 to 0.88 at C3 to C6 and L2 to L4 and 0.91 to 0.95 at T7 to T12 (computed from busscher2010 p. 1107 Table 3); frontphys2026's mean marginal minus middle height is 2.65, 3.00, 2.80, 3.25, 3.15 mm at L1 to L5 (computed from frontphys2026 p. 5 Table 2).
- The two direct series disagree in kind more than in number: chen2011 says the angle is constant from T10 to L3; vanderhouwen2009 says the inferior depth grows steadily from L1 to L5. They overlap only at T12 to L3, where vanderhouwen2009's inferior depth runs about 1.5 to 2.2 mm, close to chen2011's derived 1.65 to 2.2 mm.

(e) Covariates: no sex effect; superior depth +0.01 mm per year of age at all points (vanderhouwen2009 p. 36, p. 38), so 21 to 86 years spans about 0.65 mm (its note). chen2011 grouped by age over or under 40 and by sex (chen2011 p. 1815). Plate cortex 0.8 mm anteriorly and 0.9 to 1.0 mm posteriorly, at the CT resolution limit (frontphys2026 p. 5; frontphys2026 note).

(f) Modality: vanderhouwen2009's CT depths run about 1 to 1.7 mm deeper than Eijkelkamp's MRI and X-ray depths at the caudal plates of T12, L1, L4 and L5 (for example L4 inferior posterior about 2.6 against 0.95), and S1 superior is 1.2 to 1.6 mm against about 0; the superior plates L1 to L5 agree within about 0.4 mm (vanderhouwen2009 Fig 5 p. 39, bars read approximately; Table 1 p. 34; p. 38). The gap between modalities is larger than the between-subject SD, so compare a concavity only with values of the same modality and method (vanderhouwen2009 note, instruction 15).

## 5. Disc heights (no generator key; needs two instances)

(a) Definitions

- bach2019: anterior, middle and posterior heights between the facing plates at the anterior edge, centre and posterior edge, midsagittal, CT 3D models; its Table 6 row called Average is (A + P) / 2 (bach2019 p. e107; bach2019 note).
- shin2024: shortest distances between the plates at the anterior and posterior margins and at the centre of the interspace, sagittal CT (shin2024 p. 2). Which sagittal slice is not stated, and its Fig 1 may show a parasagittal slice through the foramen (shin2024 p. 2; Inference in its note), so record the plane with every value.
- busscher2010 IDH: disc height at the central midpoint, one value per vertebra, the disc below (busscher2010 p. 1105).
- kunkel2011: anatomical heights on the midsagittal section including cartilaginous plates, and radiographic heights between body corners (kunkel2011 p. 377).
- twomey1985: true average disc height, the midsagittal disc area over its AP length; convexity index M / (A + P) (twomey1985 p. 496 to 497).
- vanderhouwen2009 IDH: the distance between points of the same number on the two plates facing a disc (vanderhouwen2009 p. 35); no IDH value is reported anywhere in the paper (vanderhouwen2009 note).
- yadav2020 IVDH: not defined (yadav2020 p. 176).

(b) Mask recipe (Inference): it needs two instances. In the frame of the upper vertebra, project the caudal plate of the upper body and the cranial plate of the lower body on the midsagittal line; take the distance at the anterior rim, the centre and the posterior rim, and the mean gap over the overlapping plate area (twomey1985's area over length, in 3D).

(c) Radiograph: lateral view between corresponding body corners, divided by the magnification. Films read anterior height 9% short and posterior 37% short against sections (kunkel2011 p. 375), and the middle height cannot be read on film (kunkel2011 p. 383, citing Edmondston 1999).

- For a film's posterior height, predict it from the film's anterior height with the ADH-to-PDH equation of Table 4 rather than measure it: the prediction runs 13 to 17% low, against 29 to 50% low for a measured film PDH (kunkel2011 Fig 9a p. 386; Table 4 p. 382; p. 375).
- Do not use Table 4's cubics in VBHA or VBHP as printed: their three-decimal coefficients do not reproduce the paper's own means (Inference in the kunkel2011 note, by evaluating them at the table means). Never take any of them outside the fitted range, VBHA 13.9 to 20.8 mm and VBHP 14.4 to 23.1 mm (kunkel2011 note, instruction 12; Fig 9b p. 386).
- The wedging index I3 = ADH/PDH reads larger on film, about 1.2 to 1.8 (Inference in the kunkel2011 note, from Table 1's radiographic means), because film PDH is short; compare a film I3 only with a film I3.

(d) Course, mm

| Interspace | bach2019 men A / M / P | bach2019 women A / M / P | shin2024 A / M / P | busscher2010 central |
|---|---|---|---|---|
| T12/L1 | 6.29 / 6.66 / 3.75 | 4.81 / 6.13 / 3.29 | - | 9.3 (T12) |
| L1/L2 | 7.59 / 8.20 / 4.96 | 5.92 / 7.18 / 4.31 | 5.68 / 6.61 / 3.11 | 10.3 (L1) |
| L2/L3 | 8.70 / 9.79 / 5.67 | 7.13 / 8.51 / 5.14 | 6.53 / 7.90 / 4.02 | 11.5 (L2) |
| L3/L4 | 9.66 / 10.41 / 5.90 | 8.11 / 9.16 / 5.59 | 7.72 / 8.83 / 4.66 | 11.8 (L3) |
| L4/L5 | 10.94 / 10.64 / 6.05 | 9.82 / 9.70 / 5.98 | 9.27 / 9.31 / 4.88 | 12.7 (L4) |
| L5/S1 | 11.92 / 9.34 / 5.27 | 11.36 / 9.13 / 5.23 | 10.76 / 8.14 / 3.80 | 8.8 (L5) |

(bach2019 p. e113 Table 6, 240 living patients; shin2024 p. 3 Table 2, 700 living adults 18 to 35; busscher2010 p. 1107 Table 3, 6 cadaver men.) busscher2010's central height runs 6.1 at C3, a minimum of 4.4 at C6 and 4.5 to 5.3 from T2 to T9 (busscher2010 p. 1107 Table 3). Thoracic anatomical heights from C7-T1 to T11-T12: anterior 4.5, 4.5, 3.4, 3.3, 3.0, 3.5, 4.1, 4.2, 5.6, 5.4, 7.2, 6.0; posterior 4.5, 4.3, 3.5, 3.2, 3.3, 3.6, 4.1, 3.6, 5.0, 4.2, 5.8, 4.8; middle 5.6, 5.7, 5.8, 4.4, 5.0, 4.7, 5.5, 5.3, 6.1, 5.5, 6.7, 6.5 (kunkel2011 p. 378 Table 1). yadav2020's undefined heights rise to 10.60 mm at L4 in men and fall to 3.55 at S1 (yadav2020 p. 178 Table 3). twomey1985's true average height, area over length, in mm from L1-2 to L5-S1: men 20 to 35 9.2, 9.8, 10.3, 11.3, 10.6; men 60+ 9.2, 10.9, 11.0, 12.2, 11.2; women 20 to 35 6.1, 8.0, 8.2, 8.5, 8.1; women 60+ 7.9, 8.5, 8.5, 9.2, 8.8; SD 1.0 to 2.9 (twomey1985 p. 497 Table 2; 204 cadavers, of which the young adult and 60+ groups only, n per cell not printed, likely 24 per sex per group, its note). These are unloaded cadaver discs, and area over length takes in the part of the disc sunk into concave plates, so a mask gap compared with them must run to the plate surfaces, not to the rims (Inference, twomey1985 note).

- The middle height peaks at L3/L4 to L4/L5 and falls at L5/S1 in every lumbar series (bach2019, shin2024, busscher2010 above; twomey1985 p. 497 for the true average height, which peaks at L4-5). The anterior height keeps rising to L5/S1 (bach2019, shin2024). Inference, ratios of the table's means: in shin2024 anterior over middle height is above 1 only at L5/S1 (10.76/8.14 = 1.32; L4/L5 9.27/9.31 = 1.00); in bach2019 it already exceeds 1 at L4/L5 (men 1.03, women 1.01; bach2019 note) and is largest at L5/S1 (men 1.28, women 1.24). The size of the ratio, not where it crosses 1, marks the lumbosacral disc.
- shin2024 does not separate L3/L4 from L4/L5 by posterior height (-.17 mm, p .174) or L2/L3 from L5/S1 by middle height (p .062) (shin2024 Table 3 p. 4).
- The convexity index is lowest at L5-S1 in young adults (0.43 men, 0.49 women), the only values below 0.5 apart from old women's 0.48 there; in the old L4-5 and L5-S1 are both low (men 0.56, 0.53; women 0.54, 0.48), and young women's L4-5 is low too (0.54). The index marks the lowest two discs as a pair and separates them only in young men (0.58 against 0.43) (twomey1985 p. 497 Table 3; its note). Table 3 covers only men 20 to 35 and 60+ and women 18 to 35 and 60+ of the 204 cadavers, n per cell not printed, likely 24 per sex per group (twomey1985 note).
- Wedge between the facing rim planes, supine CT, read from the bars: T12-L1 about 5, L1-L2 6.7, L2-L3 6, L3-L4 7, L4-L5 9.5, L5-S1 15.4 deg; SD about 1.7 to 3.8 deg, about 5 at L5-S1; one negative L4-L5 angle was dropped, leaving 24 there (vanderhouwen2009 Fig 3 p. 39; p. 38). Eijkelkamp (MRI and X-ray) about 5 to 13.2 deg and Nissan (X-ray) about 3.7 to 15.4 deg from the same figure. Inference (vanderhouwen2009 note): only L4-L5 and L5-S1 stand out, and they overlap within one SD; on standing or intraoperative images use the order, not the degrees.
- Wedging index I3 = ADH/PDH, thoracic, on sections: 1.00 at C7-T1, 0.89 to 1.06 at T1-2 to T6-7, 1.13 to 1.29 at T7-8 to T11-12 (kunkel2011 Table 3 p. 379; p. 380), a size-free regional marker; for film see (c).
- Inference, each source on its own: bach2019's adjacent steps run 0.15 to 1.71 mm in size against SDs of 0.82 to 2.94 mm, at most about 1.2 SD (computed from bach2019 p. e113 Table 6); twomey1985's run 0.0 to 1.9 mm against SDs of 1.0 to 2.9 mm (twomey1985 note, from Table 2). Disc height is a sequence shape, not a single-level discriminator.

(e) Covariates

- Sex: bach2019 men up to 1.67 mm taller anteriorly (L1/2); no sex difference at L5/S1 in any height (P 0.123, 0.444, 0.851), nor in posterior height at L3/4 to L5/S1 (P 0.079, 0.705, 0.851) (bach2019 Table 6 p. e113; differences computed in its note). shin2024 anterior gap 1.59, 1.40, 1.20, 1.13, 0.76 mm from L1-2 to L5-S1, middle 0.50 to 0.63 and posterior 0.27 to 0.44 mm to L4-5, none at L5-S1 (p .311, .606) (shin2024 Table 4 p. 4; differences computed in its note).
- Stature and weight, side by side: twomey1985 (cadavers, all ages) finds a linear trend with stature at every level in both sexes, slope not printed (twomey1985 p. 497); shin2024 (living, 18 to 35) finds r .000 to .050 with height within sex and r .05 to .35 with weight (shin2024 Table 7 p. 5). Keep both; do not average them.
- Age: heights increase from young adult to over 60 at most levels in cadavers (twomey1985 p. 497 Table 2).
- Ethnicity: shin2024's Asian group has anterior and posterior heights up to about 1 mm above White, no middle effect (shin2024 Table 5 p. 4; 60 patients).
- One ICC of .842 covers all of shin2024's measures (shin2024 p. 5).

## 6. The canal

Every canal measure has one trap in common. SPINEPS label 61 is the canal's contents along the whole column, not one vertebra's bony foramen (section 2.3), so a canal width, depth or area taken from label 61 measures the wrong object. Build the bony foramen from labels 49, 41 and 42 instead, as below. The set never measured a canal from a mask; every recipe here is Inference.

Recipe C, the bony foramen of one instance (Inference, used by 6.1 to 6.4):

1. Build frame F (section 2.2).
2. Find the pedicle range: the Y interval over which the arch (label 41) touches the body (label 49) on both sides of X = 0.
3. In each transverse section (a plane of constant Y, 0.5 mm apart) within that range, take the instance's bone (labels 49, 41, 42) and fill holes; the filled area minus the bone is the foramen. A section in which the foramen is not closed (above or below the pedicles, where the facets and the disc bound the canal) is no section of the bony foramen; skip it.
4. Call the section through the centroid of the two pedicle cuts (O3) the mid-pedicle section.

### 6.1 Canal depth: canal_ap (SCD)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Midline anteroposterior depth from the posterior body wall to the inner surface of the arch at the base of the spinous process, top view (panjabi1991c p. 862; panjabi1992 p. 301, p. 300 Fig 1); the thoracic value is the midline depth of the digitised canal contour, whose height is not stated (panjabi1991t p. 891) | SAME; the generator. No paper of the four says at what height in the vertebra the depth was taken |
| tan2004 | Panjabi's landmarks, digitiser on dry bone (tan2004 note, SCD) | SAME landmarks; 31.8% below Panjabi on average, 43.1% at C6 (tan2004 note, computed from p. 144 Table 2); its note suspects a landmark difference as much as anatomy |
| busscher2010 | Midline depth from the posterior body wall to the inner posterior arch, the vertical arm of a crosshair on a CT transverse reformat; slice height not stated (busscher2010 p. 1105) | SAME in kind |
| griffith2016 | Posterior body margin to the cortex of the arch at the base of the spinous process, on the mid-pedicle axial reformat (griffith2016 p. 673 Fig 1B) | SAME in kind, mid-pedicle; 3.3 to 3.6 mm below Panjabi in men at L1-L4, equal at L5 (griffith2016 note) |
| masharawi2021 VCL, cizmic2023 MSG | Posterior body wall to the inner arch where the spinous process leaves it, on an axial slice through the pedicles (masharawi2021 p. 3 Fig 1; cizmic2023 p. 201 Fig 1) | SAME in kind; cizmic2023 within 0.8 to 1.9 mm of Panjabi (cizmic2023 note); masharawi2021 2.6 to 5.3 mm below (computed: 19.0 - 16.42 at L1 to 19.7 - 14.39 at L5; masharawi2021 note) |
| abbas2021 AP | Longest line from the posterior body border to the posterior canal border on the mid-body axial slice at the basivertebral foramen (abbas2021 p. 2) | DIFFERS in height: mid-body, not mid-pedicle; agrees with Panjabi within about 1 mm (abbas2021 note) |
| eisenstein1977, amonookuofi1985 | The MINIMUM midline chord, near the canal's cranial end, opposite a slight anterior bulge of the posterior wall; caliper on dry bone (eisenstein1977 p. 173; amonookuofi1985 p. 72) | DIFFERS: a minimum reads low against a mid-pedicle or median value; Caucasoid men 1.0 to 2.6 mm below Panjabi (eisenstein1977 note) |
| alonge2021 APD | Perpendicular from the posterior body border to the lamina on the midsagittal CT, about mid-body height (alonge2021 p. 71 Fig 1) | DIFFERS slightly; 2.4 to 3.4 mm below Panjabi (alonge2021 note) |
| italianmri | Bony canal perpendicular to its long axis, from the mid-third of the posterior body wall to the spinolaminar junction; MRI (italianmri pp. 2 to 4 Fig 1) | DIFFERS in modality |
| ahmed2019 MS | T2 MRI midsagittal, mid-body wall to the spinolaminar junction (ahmed2019 p. 22) | DIFFERS: MRI soft-tissue edges; 4.7 to 6.1 mm below Panjabi (ahmed2019 note) |
| yadav2020 | Midsagittal canal diameter A-B on CT (yadav2020 p. 176 Fig 1) | 3 to 5 mm below Panjabi at L1-L5 with the same L3-L4 trough (yadav2020 note) |
| bonczar2024 | Pooled; posterior body wall to the inner arch in the midline (bonczar2024 p. 4 Fig 2) | pooled from mixed definitions |
| archive measurer | Anteroposterior extent of label 61 along the scanner axis (archive/bordercall/spineps_map.py) | DIFFERS in object and frame |

Biases a mask value carries (Inference unless cited):

- Label 61: its anterior boundary at a disc level is the disc and its posterior boundary the ligamentum flavum, not bone, and it is not one vertebra's foramen (panjabi1992 note, generator section; cizmic2023 note). The set does not measure the size of the error.
- Scanner axes: the extent along the scanner's AP axis of a canal slab of depth d and height h tilted by b in the sagittal plane is d cos b + h sin b; with d = 18 mm, h = 10 mm, b = 20 deg that is 16.9 + 3.4 = 20.3 mm, 2.3 mm high.
- Height in the vertebra: the cranial minimum (eisenstein1977) lies below a mid-pedicle value; a mask median over the middle of the body reads higher than a minimum (eisenstein1977 note).

(b) Mask recipe

1. Build recipe C.
2. In the mid-pedicle section, cast a ray (O5) along -Z from the dorsal surface of the body at X = 0 to the first arch voxel; take the median over rays at |X| <= 1 mm.
3. Report that value as canal_ap. Also store the minimum over all closed sections, to compare with eisenstein1977 and amonookuofi1985.
4. Never take it from label 61.

(c) Radiograph

Lateral view only. Anterior limit: the posterior cortex of the body in the midline. Posterior limit: at L1-L4 a point opposite the cranial half of the body on the line joining the apex of the superior articular process and the inverted apex of the inferior facet; at L5 just in front of the radiolucent lake in the spinous process (eisenstein1977 pp. 174 to 175, p. 178). Divide by 1.23 at 110 cm tube-film (eisenstein1977 p. 175). The film lower limit of normal is 15 mm against 13 mm on bone (eisenstein1977 p. 175). Size-free forms: canal depth over body depth (alonge2021's Torg ratio, p. 71; tan2004 note).

(d) Course, mm

| Level | Panjabi SCD | tan2004 | busscher2010 |
|---|---|---|---|
| C2 | 21.0 | - | - |
| C3 | 16.2 | 10.3 | 15.3 |
| C4 | 17.7 | 10.3 | 15.0 |
| C5 | 17.4 | 10.3 | 15.2 |
| C6 | 18.1 | 10.3 | 16.1 |
| C7 | 15.2 | 11.0 | 15.6 |
| T1 | 16.4 | 11.6 | 16.1 |
| T2 | 15.3 | 11.7 | 16.6 |
| T3 | 15.9 | 12.0 | about 16.3 to 16.8 |
| T4 | 16.2 | 11.8 | about 16.3 to 16.8 |
| T5 | 16.3 | 11.5 | about 16.3 to 16.8 |
| T6 | 16.5 | 11.6 | about 16.3 to 16.8 |
| T7 | 16.1 | 11.9 | about 16.3 to 16.8 |
| T8 | 15.9 | 11.9 | about 16.3 to 16.8 |
| T9 | 15.7 | 11.8 | 16.1 |
| T10 | 15.5 | 11.9 | 17.6 |
| T11 | 16.0 | 11.8 | 18.4 |
| T12 | 18.1 | 12.4 | 19.7 |
| L1 | 19.0 | 12.5 | 19.7 |
| L2 | 18.2 | 11.7 | 18.6 |
| L3 | 17.5 | 11.2 | 17.1 |
| L4 | 18.6 | 11.2 | 17.9 |
| L5 | 19.7 | 11.4 | 21.8 |

(Panjabi: panjabi1991c p. 864 Table 3, panjabi1991t p. 893 Table 4, panjabi1992 p. 302 Table 3; tan2004 pp. 140 to 141 Table 1; busscher2010 p. 1110 Fig 5, read from the figure.)

Lumbar and sacral series, mm, L1 to L5 (and S1 where given):

| Series | Population | Values |
|---|---|---|
| griffith2016 | 540 men, 540 women, living CT, mid-pedicle (griffith2016 p. 675 Table 3) | men 15.46, 14.58, 14.04, 15.34, 19.67; women 15.58, 14.87, 14.18, 15.03, 18.12 |
| cizmic2023 | 100 men, 100 women, living CT (cizmic2023 p. 202 Tables 3 to 5) | both sexes 19.06, 18.05, 16.66, 16.79, 17.81 |
| abbas2021 | 90 control men, living CT, mid-body (abbas2021 p. 5 Table 2) | 18.7, 17.8, 16.9, 17.6, 18.8 |
| masharawi2021 | 25 control men, living CT (masharawi2021 p. 9 Table 4) | 16.42, 14.81, 13.49, 13.62, 14.39 |
| alonge2021 | 120 living CT, sexes pooled by its note (alonge2021 p. 73 Table 3) | 16.28, 15.64, 15.10, 15.73, 16.30 |
| eisenstein1977 | Caucasoid men, dry bone, minimum chord (eisenstein1977 p. 174 Table I) | 18, 17, 16, 16, 18 |
| amonookuofi1985 | 79 men, dry bone, minimum chord (amonookuofi1985 p. 71 Table 1) | 16.6, 15.8, 14.9, 15.6, 16.0 |
| yadav2020 | 174 men, living CT (yadav2020 p. 177 Table 2) | T12 16.19; 15.68, 14.57, 13.45, 13.29, 14.73; S1 11.00 |
| italianmri | 302 men, 302 women, MRI (italianmri pp. 2 to 4 Table 2) | 18.7, 17.9, 16.9, 16.9, 17.3; S1 14.9 |
| ahmed2019 | 80 adults, MRI (ahmed2019 p. 22 Table 1) | 14.34, 13.43, 12.35, 12.70, 13.63 |
| bonczar2024 | pooled studies | 16.02, 15.08, 14.69, 15.06, 15.69 |

Where it peaks, bottoms out and separates:

- C2 is deepest (21.0) and differs from C3 and C7; C3 to C6 is a plateau; C7 is shallowest (15.2) (panjabi1991c p. 864 Table 3, its note). busscher2010 and tan2004 show no C7 drop, so the C6/C7 step is not reproduced.
- T1 to T11: flat at 15.3 to 16.5 mm, mean 16.2 (panjabi1991t p. 893 Table 4); flat in tan2004 and busscher2010 too. Fails to separate any thoracic pair.
- T11 to T12: +2.1 mm in Panjabi, and busscher2010 rises from T9 to T12. The T12 rise is the only thoracic signal, and the text and table disagree on its significance (panjabi1991t note).
- L1 to L5: a shallow U with its floor at L3 or L4 in every series above (panjabi1992 p. 302; abbas2021 p. 5; griffith2016 p. 675; eisenstein1977 p. 179, "venturi tube"). Adjacent steps of 0.7 to 1.2 mm against SDs of 1.4 to 2.2 mm (abbas2021 note) fail to separate. L1 and L5 are equal or within 1 mm in every eisenstein1977 group (eisenstein1977 note). The one exception is griffith2016's L4 to L5 rise, in both sexes: +4.3 mm in men and +3.09 mm in women. Inference: 4.33 / mean(2.99, 3.76) = 1.3 SD in men, and 1.02 SD in women (griffith2016 note). Kumar's Telangana CT women show no L5 rebound (14.5 to 14.25 mm; yadav2020 p. 179 Table 4), so the U is not universal: weigh the L5 rebound lightly. yadav2020's S1 SD in women (4.73 mm on a mean of 11.19) puts mean - 2 SD near 1.7 mm, so its S1 row gives no usable lower limit (yadav2020 note).
- L5 to S1: -2.4 mm on MRI, about 1 SD (italianmri note); -3.7 mm in yadav2020 men, about 1.2 SD (yadav2020 note). The fall into the sacral canal is the cue for S1.
- Size-free: canal depth over body depth falls 0.70, 0.64, 0.58, 0.58, 0.58 (alonge2021 p. 73), so it separates L1, L2 and L3 but not L3 to L5; yadav2020's SCD/UVD falls 0.60 to 0.42 from T12 to L4 in men (yadav2020 note). On Nigerian dry bone the paper states 0.6 at L1 and 0.5 at L2 to L5 (amonookuofi1985 p. 74 Table 4); to two decimals about 0.57 (men) and 0.61 (women) at L1, 0.52 and 0.55 at L2, and 0.45 to 0.50 at L3 to L5, with women higher at L1 to L3, so the ratio is not wholly sex-free (Inference, amonookuofi1985 note). On MRI, with a mid-body body depth, SCD/VBD from L1 to S1 is men 0.66, 0.60, 0.55, 0.54, 0.56, 0.64 and women 0.76, 0.70, 0.63, 0.61, 0.61, 0.70, a U with its floor at L4 (Inference, ratios of the table means in the italianmri note, from Tables 2 and 3 p. 4); a lateral film can give it. Each is a ratio of group means with no SD; do not pool them.

(e) Covariates

- Sex, side by side: none in controls (abbas2021 p. 5; yadav2020 p. 177) and none on Indian MRI (ahmed2019 p. 22 Table 1); women equal or 0 to 1 mm deeper on South African dry bone (eisenstein1977 note) and deeper at L1-L4 on CT (cizmic2023 p. 202); women narrower at every level on Nigerian dry bone, by at most 0.8 mm at L1-L3 and about 1.5 mm at L4-L5 (amonookuofi1985 p. 73; Table 1 p. 71; per level 0.8, 0.7, 0.7, 1.5, 1.4 mm is the note's Inference); griffith2016 unadjusted, women deeper at L2 and men at L5, and after adjustment for height and weight women deeper at L1-L3 (griffith2016 p. 675; Table 3); men deeper only at L5 and S1 on MRI (italianmri note). The series disagree; do not pool them.
- Stature and age: no correlation with height or weight (italianmri note, R squared < 0.1; masharawi2021 note); griffith2016 (living Hong Kong CT) finds a weak correlation with height, r 0.163 in men and 0.255 in women (P < 0.001), and a slight fall with age in women only (r -0.102) (griffith2016 Table 1 p. 674), weak and of a size consistent with italianmri's R squared < 0.1; the midsagittal diameter is fixed early in life (abbas2021 note, refs 32 and 33).
- Population: African skeletons 0 to 2 mm shallower than Caucasoid (eisenstein1977 p. 174 Table I); Chinese dry bone about one third below Panjabi (tan2004 note).
- Disease: degenerative stenosis 0.9 to 2.9 mm shallower at every level (abbas2021 p. 5 Table 2).

### 6.2 Canal width: canal_w (SCW), the interpedicular distance

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c | Lateral width of the canal, top view; axial level not stated (panjabi1991c p. 862) | SAME; the generator |
| panjabi1991t | The widest transverse diameter of the digitised canal contour (panjabi1991t p. 891 Fig 3C) | SAME; the only Panjabi paper that says which width |
| panjabi1992 | A transverse arrow across the canal near mid-depth; level not stated (panjabi1992 p. 300 Fig 1) | SAME; "at the pedicles" is Inference in its note |
| mnemonics.py | "the transverse diameter of the canal at the level of the pedicles" (schwingcheck/mnemonics.py) | The generator's gloss: an Inference written as a definition |
| tan2004 | Panjabi's landmarks (tan2004 p. 138) | SAME landmarks; 0.81 / 0.79 / 0.82 of Panjabi in the cervical / thoracic / lumbar spine (tan2004 note) |
| busscher2010 | Side-to-side width of the vertebral foramen, crosshair, CT; slice height not stated (busscher2010 p. 1105) | SAME in kind |
| eisenstein1977 | The GREATEST interpedicular distance, medial pedicle surfaces, caliper (eisenstein1977 p. 173) | SAME as the thoracic "widest"; within -0.2 to +1.4 mm of Panjabi (eisenstein1977 note) |
| griffith2016, ahmed2019, alonge2021, cizmic2023, masharawi2021 VCW | Medial pedicle margin to medial pedicle margin on an axial image at mid-pedicle (griffith2016 p. 673; ahmed2019 p. 22, MRI), at the slice of maximum pedicle width (alonge2021 p. 71), at the canal's widest point (cizmic2023 p. 201), or on the pedicle slice (masharawi2021 p. 3) | SAME in kind; L5 values in living CT run 2.5 mm below to 5.6 mm above Panjabi, so the slice rule matters (griffith2016 note; cizmic2023 note) |
| abbas2021 ML | Longest line joining the medial pedicle borders on the mid-body slice at the basivertebral foramen (abbas2021 p. 2) | DIFFERS: L5 34.9 mm, 8 mm above Panjabi's 27.1 (abbas2021 note); not poolable |
| hinck1966, ahn2001, amonookuofi1982, chaudhary2015 | The SHORTEST distance between the medial pedicle surfaces on an AP film, uncorrected for magnification (hinck1966 p. 141; ahn2001 p. 68; amonookuofi1982 p. 226; chaudhary2015 p. 34) | DIFFERS: a projected minimum, magnified; reads high by M and low by taking the minimum |
| archive measurer | Left-right extent of label 61 along the scanner axis (archive/bordercall/spineps_map.py) | DIFFERS in object and frame |

Biases a mask value carries (Inference unless cited):

- Rotation about the vertical by a: w cos a + d sin a; with w = 24, d = 18 mm, a = 10 deg that is 23.6 + 3.1 = 26.7 mm, 2.7 mm high.
- Section height: a width taken where facets or laminae bound the canal reads narrower than at the pedicles, most of all at a trefoil L5 (eisenstein1977 note).
- Label 61: the dural sac is narrower than the bony canal, and at L5 the canal contents do not fill the lateral recesses.

(b) Mask recipe

1. Build recipe C.
2. In every closed section, take the X extent of the foramen between the medial pedicle surfaces.
3. Report the greatest over the closed sections as canal_w (panjabi1991t's widest; eisenstein1977's greatest). Store the mid-pedicle value too, to compare with griffith2016.
4. Film-equivalent IPD, stored beside the section value: project the pedicle voxels of both sides along the frame's AP axis onto the coronal plane and take, over the rows that cross both pedicles, the smallest gap between the most medial voxels of the two projected pedicles (chaudhary2015 note recipe; its definition p. 34). It is true size: multiply by the film's magnification before comparing with film tables, or compare ratios between levels, which cancel it (chaudhary2015 note).

(c) Radiograph

AP view: the gap between the medial cortices of the end-on pedicle rings; divide by 1.14 at 110 cm (eisenstein1977 p. 175). The film lower limit is 20 mm against 18 mm on bone (eisenstein1977 p. 175). Hinck's adult values are film values at 40 in, uncorrected (hinck1966 p. 141); his AP spine films read 0.57 mm wider than PA chest films on average, 1.10 mm at T1-T3 and 0.38 mm at T4-T12 (hinck1966 pp. 148 to 149 Table IV). Rotation makes the projected distance inaccurate (ahn2001 p. 67). Width over end-plate width is magnification-free on one AP view (Inference).

(d) Course, mm

| Level | Panjabi SCW | hinck1966 adult IPD (film) | tan2004 | busscher2010 |
|---|---|---|---|---|
| C2 | 24.5 | - | - | - |
| C3 | 22.9 | 28.0 | 19.2 | 25.9 |
| C4 | 24.7 | 28.8 | 19.3 | - |
| C5 | 24.9 | 29.4 | 20.3 | 28.3 |
| C6 | 25.8 | 29.3 | 20.6 | - |
| C7 | 24.5 | 28.0 | 19.7 | 27.3 |
| T1 | 21.8 | 24.0 | 17.7 | 23.9 |
| T2 | 19.5 | 20.5 | 15.2 | 20.7 |
| T3 | 18.3 | 18.8 | 14.2 | - |
| T4 | 17.0 | 18.1 | 13.5 | about 17.7 to 18.3 |
| T5 | 17.1 | 17.6 | 13.6 | about 17.7 to 18.3 |
| T6 | 17.3 | 17.3 | 13.8 | about 17.7 to 18.3 |
| T7 | 17.3 | 17.4 | 13.9 | about 17.7 to 18.3 |
| T8 | 17.7 | 17.7 | 14.1 | about 17.7 to 18.3 |
| T9 | 17.9 | 18.2 | 14.2 | about 17.7 to 18.3 |
| T10 | 18.2 | 18.7 | 14.2 | - |
| T11 | 19.4 | 20.2 | 15.3 | - |
| T12 | 22.2 | 23.2 | 17.9 | 24.9 |
| L1 | 23.7 | 25.0 | 19.4 | 26.7 |
| L2 | 23.8 | 25.5 | 19.5 | - |
| L3 | 24.3 | 26.0 | 19.4 | - |
| L4 | 25.4 | 26.9 | 20.2 | - |
| L5 | 27.1 | 29.7 | 23.4 | 31.9 |

(Panjabi: panjabi1991c p. 864 Table 3, panjabi1991t p. 893 Table 4, panjabi1992 p. 302 Table 3; hinck1966 pp. 141 to 147 Table IA, 121 adult films; tan2004 pp. 140 to 141 Table 1; busscher2010 p. 1110 Fig 5, read from the figure.)

Lumbar series, mm, L1 to L5:

| Series | Population and method | Values |
|---|---|---|
| eisenstein1977 | Caucasoid men, dry bone, greatest (p. 174 Table I) | 23, 24, 23, 24, 26 |
| griffith2016 | 540 men, living CT, mid-pedicle (p. 675 Table 4) | 20.87, 21.19, 22.13, 24.55, 29.55 |
| cizmic2023 | 100 men, living CT, widest (p. 202 Table 5) | 25.01, 25.32, 26.22, 27.81, 32.69 |
| masharawi2021 VCW | 25 control men, living CT (p. 9 Table 4) | 22.68, 22.59, 22.47, 22.59, 25.23 |
| alonge2021 | 120 living CT, pooled (alonge2021 note, pooled from p. 74 Table 4) | 22.46, 22.93, 24.37, 27.00, 32.36 |
| ahmed2019 | 80 adults, MRI (p. 24 Table 2) | 22.42, 22.64, 23.45, 24.52, 27.68 |
| abbas2021 ML | 90 control men, living CT, mid-body (p. 5 Table 2) | 25.5, 26, 27, 28.6, 34.9 |
| amonookuofi1982 | 150 men, AP film, uncorrected (p. 228 Table 1) | 22.6, 22.7, 24.5, 26.0, 28.7 |
| amonookuofi1982 | 140 women, AP film, uncorrected (p. 228 Table 1) | 21.3, 22.5, 23.7, 25.4, 28.4 |
| chaudhary2015 | 150 men, AP film, uncorrected (p. 34 Table I) | 24.06, 24.73, 26.01, 27.15, 31.34 |
| bonczar2024 | pooled studies | 22.04, 22.15, 22.62, 23.19, 26.46 |

Where it peaks, bottoms out and separates:

- Cervical: a plateau at about 25 mm, widest at C6 (panjabi1991c p. 864 Table 3); no cervical level differs.
- C7 to T1 and T1 to T2: -2.7 and -2.3 mm in Panjabi; -4.0 and -3.5 mm on Hinck's films, about 2 SD each, at every age group (hinck1966 note). Separates C7 from T1 and T1 from T2 on an AP view.
- T4 to T10: flat, the column's minimum (Panjabi 17.0 to 18.2; Hinck 17.3 to 18.7, lowest at T6). Fails to separate any pair.
- T11 to T12: +2.8 mm in Panjabi; +3.0 mm on film, 1.6 SD (hinck1966 note). Separates.
- T12 to L1: +1.5 mm in Panjabi, +1.8 on film, under 1 SD (hinck1966 note). Weak.
- L1 to L3: nearly flat in every series; alonge2021 L1/L2 +0.5 mm (about 0.2 SD) and L2/L3 +1.4 (about 0.7 SD) (Inference in its note, from Table 4 p. 74). Fails.
- L4 to L5: +1.7 mm in Panjabi and +2.8 on film, under 1 SD (hinck1966 note); +5.0 mm in griffith2016 men and +4.9 in cizmic2023 men; alonge2021 pooled +5.4 mm, about 1.4 SD, with L3/L4 +2.6 mm, about 1 SD (Inference in its note, from Table 4 p. 74); on Indian MRI +2.66 mm in men and +3.57 in women, 1.03 and 1.72 SD (ahmed2019 p. 24 Table 2; the SD multiples are the note's Inference). Inference: 5.0 / mean(3.24, 4.25) = 1.3 SD and 4.88 / mean(3.06, 4.18) = 1.3 SD. Living CT and MRI separate L4 from L5 better than the dry-bone series do.
- Width over depth, a size-free shape: 1.17 at C2, 1.40 to 1.43 at C3-C6, 1.61 at C7, which Panjabi names a marker of the cervicothoracic transition (panjabi1991c p. 864 Table 3, p. 867); 1.3 at T1-T2, 1.0 to 1.1 at T4-T9, 1.2 at T10-T12 (panjabi1991t p. 893 Table 4); 1.25, 1.31, 1.39, 1.37, 1.38 at L1-L5 (panjabi1992 p. 302 Table 3). In living CT the ratio rises further caudally: 1.30, 1.39, 1.55, 1.63, 1.79 (cizmic2023 note, from p. 202 Tables 3 to 4). On Indian MRI, transverse over midsagittal diameter is 1.56, 1.69, 1.90, 1.93, 2.03 at L1 to L5, both sexes (men 1.63 to 2.01, women 1.51 to 2.05), steepest from L1 to L3 (Inference: ratios of the means of ahmed2019 Tables 1 and 2, pp. 22 and 24; its note).

(e) Covariates

- Sex: men about 1 mm wider (hinck1966 note: 0.4 to 2.2 mm, mean 1.25, computed); men wider at every level, all P < 0.0001, still after adjusting for height and weight (griffith2016 p. 675 Table 4, Table S3); on Indian films men 1.42 to 2.42 mm wider at L1 to L5, a female/male ratio of 0.90 to 0.95, p < 0.001 at every level (chaudhary2015 Table I p. 34; differences computed); on Nigerian films only 0.2 to 1.3 mm (amonookuofi1982 Table 1 p. 228).
- Stature: r 0.126 in men and 0.143 in women (griffith2016 note).
- Age: grows 4.5 to 5.2 mm in the lumbar spine from 3-5 y to adult, mostly before 9-10 y (hinck1966 note).
- Population: African skeletons 1 to 3 mm narrower than Caucasoid at L1 to L4 and 0 to 1 mm at L5 (eisenstein1977 p. 174 Table I; its note), confounded with age, the Caucasoid groups being 17 to 25 years older (eisenstein1977 note, Table IV p. 176); Chinese dry bone about 0.8 of Panjabi (tan2004 note).
- Normal limits on film: amonookuofi1982's 95% limits of IPD on AP film, uncorrected, L1 to L5, mm: men 18.8-26.4, 19.3-26.1, 21.5-27.5, 22.6-29.4, 24.1-33.3; women 17.3-25.3, 18.5-26.5, 20.1-27.3, 22.2-28.6, 24.4-32.4 (amonookuofi1982 Table 2 p. 229; each is the Table 1 mean +/- 2 SD, Inference in its note). A carefully measured value outside them should raise suspicion of pathology or anomaly, while a value inside them does not clear the canal (amonookuofi1982 p. 228).
- Disease: Marfan syndrome widens the lumbar interpedicular distance to 29.5 to 39.6 mm on film (ahn2001 p. 68); degenerative stenosis leaves it unchanged (abbas2021 p. 5, P 0.064 to 0.725).

### 6.3 Canal area: canal_area (SCA)

(a) Definitions

- Panjabi: the area of the digitised canal contour, by the projected-area (vector) method (panjabi1991t p. 891; panjabi1992 p. 300); section level not stated in any of the three (panjabi1991c p. 864). SAME; the generator.
- griffith2016: the osseous canal on the mid-pedicle axial reformat, seed-grown and corrected by hand (griffith2016 p. 672 Fig 1A). SAME in kind.
- abbas2021 CSA: the area bounded by the posterior body cortex, the medial pedicle borders and the arch, on the mid-body slice (abbas2021 p. 2). DIFFERS in height.
- tan2004: Panjabi's; 31.7% below Panjabi on average (tan2004 note, computed from p. 144 Table 2).
- bonczar2024: pooled, axial (bonczar2024 p. 4 Fig 2).

(b) Mask recipe: recipe C; the area of the foramen in the mid-pedicle section; store the minimum over closed sections too. A transverse section of frame F is planar, so its vector area is its plain area (O2).

(c) Radiograph: not measurable. From the two diameters: pi x SCW x SCD / 4 overestimates by 10 to 30% and SCW x SCD / 2 underestimates by 20 to 30% (panjabi1992 p. 305). In the neck use the ellipse at C2-C3 and the triangle at C4-C7 (panjabi1991c p. 866, p. 868); SCA/(SCW x SCD) is 0.73 at C2 and 0.57 to 0.60 at C5-C7 (Inference, panjabi1991c note).

The factor SCA/(SCW x SCD), by series and level, not pooled:

- Panjabi lumbar: about 0.71 at L1 falling to about 0.61 to 0.62 at L4-L5 (Inference: 0.785/1.105 and 0.785/1.27 to 1.28, from the ellipse's 10.5% and 27 to 28% excess in the panjabi1992 note, Table 3 p. 302).
- tan2004: cervical 0.76 to 0.80, thoracic 0.80 to 0.90, L1-L3 0.77 to 0.82, L4 0.72, L5 0.70 (tan2004 note, computed from Table 1).

A single factor of 0.78 at L4-L5 would read about 26% over Panjabi's areas (Inference: 0.78/0.62). Use the factor of the series whose definition the mask copies.

(d) Course, mm2

| Region | Panjabi | Other series |
|---|---|---|
| C2 to C7 | 374.5, 248.7, 272.0, 249.5, 266.5, 223.8 (panjabi1991c p. 864 Table 3) | - |
| T1 to T12 | 213, 200, 180, 192, 201, 206, 199, 194, 200, 202, 220, 280 (panjabi1991t p. 893 Table 4) | tan2004 minimum 140.1 at T4 (tan2004 note) |
| L1 to L5 | 320, 281, 280, 290, 330 (panjabi1992 p. 302 Table 3) | griffith2016 men 273.7, 256.3, 247.8, 276.3, 338.3; women 264.8, 252.7, 241.8, 258.1, 296.9 (p. 675 Table 2); abbas2021 control men 296, 283, 279, 305, 370 (p. 5 Table 2); bonczar2024 251, 227, 214, 215, 245; tan2004 L1 200.0, L4 163.8, L5 186.6 (tan2004 note) |

- C2 is largest and only C2 against C7 is significant (panjabi1991c note); a step of -126 mm2 from C2 to C3. The cervical SCA SEMs imply SDs of 45 to 126 mm2, a CV up to 56% at C7, far larger than SCW and SCD imply; take no likelihood width from them (panjabi1991c note).
- T2 to T10: flat at about 198 (panjabi1991t note); fails.
- T11 to T12: +60 mm2; the large thoracolumbar enlargement (panjabi1991t note), though no level is marked significant.
- L1 to L2 falls, L2 to L4 is flat, L4 to L5 rises (panjabi1992 p. 301); griffith2016 men L4 to L5 +62 mm2. Inference: 62.0 / mean(64.4, 82.6) = 0.84 SD.
- Shape: the ellipse overestimates by 10.5% at L1 and 27 to 28% at L4-L5 (panjabi1992 note, computed from Table 3), so the canal turns from oval to triangular caudally.
- Canal over body area: griffith2016's canal CSA over body CSA is men 0.23, 0.20, 0.18, 0.18, 0.20 and women 0.28, 0.25, 0.21, 0.21, 0.21 at L1 to L5, nearly flat from L3 down; relative to the body, women's canals are larger, also after adjustment (griffith2016 Table 6 p. 676). To tell L1, L2 and L3 apart use the body CSA, which rises about 70 to 125 mm2 a level, not canal size (griffith2016 Table 5 p. 675; its note, instruction 12).

(e) Covariates: men larger at L1, L3, L4 and L5 (griffith2016 p. 675 Table 2); height r 0.186 in men and 0.298 in women (griffith2016 note); degenerative stenosis 22 to 60 mm2 smaller (abbas2021 p. 5 Table 2, computed); Chinese dry bone about one third smaller (tan2004 note).

### 6.4 Canal shape, lateral recess, facet-level width and foramen (no generator key)

These are not generator keys. They are listed because each separates lower lumbar or junction levels that the generator's canal keys do not.

Canal shape:

- Oval at L1-L2, trefoil at L4-L5, and at L3 about two thirds oval and one third trefoil, in 120 living CTs (alonge2021 pp. 74 to 75). A trefoil canal was found in 66 of 443 skeletons (15%), almost always at L5 and sometimes at L4, made by laminar bars (eisenstein1977 p. 177, p. 179).
- Mask recipe (Inference): in the mid-pedicle section, compute SCA / (pi x SCW x SCD / 4) and count the concavities of the foramen outline; two posterolateral lobes mark a trefoil (alonge2021 note).
- Radiograph: none.

Lateral recess diameter, LRD:

- Definition: from the posterior body surface to the anteromedial point of the facet joint, on each side, on an axial CT slice near the end plate or disc (yadav2020 p. 176 Fig 1B).
- Course, men right, T12 to S1: 11.45, 11.36, 10.52, 9.24, 8.60, 7.71, 7.50 mm (yadav2020 p. 177 Table 2). Adjacent separations 0.07, 0.77, 1.09, 0.67, 1.06, 0.33 SD (yadav2020 note). It separates L2/L3 and L4/L5 a little and fails at T12/L1 and L5/S1.
- Mask recipe (Inference): in the transverse section at the instance's cranial end plate, draw the line tangent to the anterior margins of both superior articular processes (labels 45 and 46); on each side, take the perpendicular from the posterior body surface to that line, just medial to the process.
- Covariates: about 2 mm (21%) larger in men at T12-L1, small caudally (yadav2020 note).
- Radiograph: none.

Interfacet distance at the canal, IFD and SIFW:

- yadav2020 IFD: between the anteromedial points of the facet joints, across the back of the canal on an axial slice (yadav2020 p. 176 Fig 1D). Men, T12 to S1: 15.12, 17.27, 17.53, 17.67, 19.08, 22.69, 27.91 mm (yadav2020 p. 177 Table 2). Steps +2.15 at T12/L1, a flat L1 to L3, then +3.61 at L4/L5 and +5.22 at L5/S1 (1.0 and 1.2 SD; yadav2020 note).
- masharawi2021 SIFW: between the anteromedial ends of the two facet joint lines on the axial slice (masharawi2021 p. 3 Fig 1). Control men: 16.12, 16.58, 15.56, 17.13, 22.74 mm; L4 to L5 +5.6 mm, about 1.1 to 1.5 pooled SD (masharawi2021 p. 6 Table 2; its note).
- Neither equals Panjabi's interfacet width, which joins facet centroids (section 8.3).
- Mask recipe (Inference): in the transverse section through the joint, the distance between the most anteromedial voxels of the left and right superior articular processes of the lower vertebra.

The intervertebral foramen (two instances):

- Definitions, each between the caudal border of the upper pedicle and the cranial border of the lower one: FH is the greatest such distance on a CT bone model (bach2019 p. e107); VFH the vertical distance on a parasagittal slice (masharawi2021 p. 3 Fig 1); NFH the greatest notch-to-notch distance on sagittal CT (shin2024 p. 2 Fig 2). yadav2020's IVFD is not defined (yadav2020 p. 176).
- Course, T12/L1 to L5/S1:
  - bach2019 FH, men: 16.27, 18.34, 19.46, 18.58, 17.65, 14.30 mm (bach2019 p. e113 Table 6).
  - masharawi2021 VFH, control men, L1/2 to L5/S1: 16.66, 17.10, 17.07, 15.78, 13.64 (masharawi2021 p. 9 Table 4).
  - shin2024 NFH, left, L1/2 to L5/S1: 17.31, 18.38, 18.42, 17.81, 15.33 (shin2024 p. 5 Table 6).
- Pattern: the foramen peaks at L2/3 to L3/4 and is lowest at L5/S1 in all three. The L4/5 to L5/S1 drop of about 3.3 mm is 1.6 to 1.7 SD, the largest adjacent contrast in bach2019 (bach2019 note).
- The axial and sagittal AP foraminal widths narrow to L4/5 and rise slightly at L5/S1; the foraminal area peaks at L3/4 and is smallest at L5/S1 (shin2024 p. 5 Table 6).
- Mask recipe (Inference): in the upper vertebra's frame, take the parasagittal plane through each pedicle's centroid (O3). Measure the largest Y distance from the caudal surface of the upper pedicle cut to the cranial surface of the lower instance's pedicle cut.
- Radiograph: a lateral view, pedicle to pedicle, with both sides superimposed; divide by the magnification (masharawi2021 note; bach2019 note).
- Covariates: FH falls with age, r -0.24 to -0.45 (bach2019 note); men higher at L1/2 to L3/4 only (bach2019 p. e113); degenerative spondylolisthesis lowers VFH by 1.85 to 3.94 mm (masharawi2021 p. 9 Table 4).

The inferior vertebral notch, N (one instance):

- Definition: the greatest horizontal span from the back of the lower body to the inner surface of the lamina, below the pedicle, on dry bone. The author offers it as an index of the foramen's size; which side was taken is not stated (amonookuofi1985 p. 72, p. 75; p. 70 Fig 1b). Population: lumbar sets of 122 Nigerian adults, 79 men and 43 women (amonookuofi1985 p. 69).
- Course, mm, L1 to L5: men 8.8, 8.4, 7.5, 7.6, 7.0; women 8.1, 7.8, 7.5, 7.4, 7.3 (amonookuofi1985 p. 74 Table 5). It falls slightly and not strictly from L1 to L5. Steps of 0.1 to 0.9 mm against SDs of 0.7 to 1.3 mm separate no adjacent pair (amonookuofi1985 note).
- Mask recipe (Inference, amonookuofi1985 note): in the parasagittal plane through each pedicle, below the pedicle, take the largest gap along Z between the back of the body (label 49) and the front of the arch (label 41 or 47/48). Report each side and their mean.
- Radiograph (Inference): lateral view, the width of the foramen's upper bay below the pedicle, divided by the magnification.
- Notch over body depth, magnification-free: printed 0.3 at L1-L2 and 0.2 at L3-L5 in men, and the same in women except 0.3 at L3 (amonookuofi1985 p. 75 Table 6). To two decimals (Inference, its note) men 0.30, 0.27, 0.23, 0.22, 0.20-0.22 and women 0.31, 0.28, 0.26, 0.24, 0.23, a steadier fall than canal over body, which flattens below L3. The author offers these ratios for lateral films, where magnification cancels (p. 75). Ratios of group means with no SD; N alone separates no adjacent pair, and whether the ratio does is not known.

Pedicle-to-pedicle spacing between neighbours, mitra2002's "IPD" (two instances):

- Definition: never given in words. Inference from the paper's statements: the craniocaudal distance between the pedicles of adjacent vertebrae, labelled by the upper one. It is not the transverse interpediculate distance of 6.2 (mitra2002 note).
- Course, men, direct on 18 cadavers: 32.4, 32.8, 33.4, 34.1 mm at L1 to L4; L5 not given (mitra2002 p. 455 Table 2).
- Lateral films read 4.9, 5.7, 4.6 and 3.0 mm higher. The authors blame the overlap of the two sides' pedicles, while the magnification factor is printed as zero, so part of the excess may be magnification (mitra2002 p. 456, p. 458; mitra2002 note).
- Mask recipe (Inference): the 3D distance between the pedicle isthmus centroids (recipe P) of instances k and k+1, left with left and right with right, then averaged. It is roughly a body height plus a disc height, so it adds little that sections 3.3 and 5 do not.

## 7. The pedicles

Every pedicle measure shares one trap: SPINEPS has no pedicle label. The pedicle lies inside label 41 with the laminae and the bases of the processes, so an extent of label 41 is not a pedicle dimension, and the archive measurer refuses pedicle width and height for that reason (archive/bordercall/spineps_map.py, MAPPING). Cut the pedicle out geometrically by recipe P. No paper in the set measured a pedicle on a segmentation mask; every recipe below is Inference unless a page is cited.

A second trap is which section and which diameter. Panjabi took the width and height of a section perpendicular to the pedicle axis, horizontal and vertical as drawn (panjabi1991t p. 891 Fig 3C, p. 893; panjabi1991c p. 862, p. 866), and none of his three papers says the section was the narrowest (panjabi1992 p. 301; panjabi1991c p. 862). otsuki2021 and robertson2000 report the minor and major axes of the section's best-fit ellipse instead (otsuki2021 p. 4 Fig 2A; robertson2000 p. 710). At L4 and L5 the section's long axis rolls 39 to 52 deg away from the vertical on CT sections (makino2012 p. 1518 Table 1). On coaxial radiographs of dry bone, a different method, the ellipse tilts 31.0/33.5 deg at L4 (SD 17.1/20.8) and 55.0/50.3 deg at L5 (SD 8.8/7.4), left/right, against -2.4 to 7.5 deg at L1 to L3 (robertson2000 p. 711 Table 1). Either way its minor axis is far smaller than its horizontal extent there. Inference, arithmetic: an ellipse with otsuki2021's L5 axes, 24.2 by 11.8 mm (otsuki2021 p. 6 Table 2), rolled 51.8 deg (makino2012 p. 1518 Table 1), is 2 x sqrt(5.9^2 cos^2 51.8 + 12.1^2 sin^2 51.8) = 20.4 mm wide horizontally and 17.6 mm tall vertically. Panjabi's L5 width and height are 18.6 and 19.6 mm (panjabi1992 p. 302 Table 4). The same arithmetic gives 7.2, 7.4, 10.2, 14.4 and 20.4 mm horizontally at L1 to L5, against Panjabi's 8.6, 8.2, 10.1, 14.1 and 18.6. So Panjabi's width is the horizontal extent of a rolled section, not its minor axis. The two series are different samples; the agreement supports the reading but does not prove it.

Recipe P, the pedicle of one instance on one side (Inference, after otsuki2021 p. 3, whose isthmus method was built for clinical CT):

1. Build frame F (section 2.2).
2. Take the label-41 voxels on that side of X = 0. Keep those between the dorsal surface of the body (label 49) and the most anterior voxel of the superior articular process (label 45 or 46) or the transverse process (label 43 or 44), whichever is more anterior at that height. At T1 to T10 do not bound the pedicle by the body's lateral wall, and at T1 to T6 not by the upper end plate: there the pedicle cortex projects beyond the body outline, laterally and cranially; from T11 to L5 it lies inside the outline (lien2007 Fig 2 caption p. 1217; p. 1220; its note, instruction 8).
3. Fit the axis by O3: section centroids at the anterior and posterior thirds of that bridge, and the line through them. Reslice perpendicular to the axis every 0.5 mm.
4. In each section, fit a second-moment ellipse. Call the section with the shortest minor axis the isthmus (otsuki2021 p. 3).
5. In the isthmus section, let v be frame Y projected onto the section plane and normalised, and u = v x axis. Record the extent of the section along u (the width), the extent along v (the height), the section's area, the ellipse's minor and major axes, and the roll of the major axis from v.
6. Record the axis direction in frame F, the isthmus position along the axis, and whether the bridge's boundary with label 49 was ambiguous.

The mask's outer boundary is the outer (periosteal) cortex. That matches Panjabi and the caliper series (olsewski1990 p. 542; yu2015 p. 1640; arockiaraj2025 p. 313 Fig 1). It does not match makino2012, which measured inner cortex to inner cortex (makino2012 p. 1518 Table 1), nor a radiograph's ring, which lies 1 to 3 mm inside the outer cortex (robertson2000 p. 711).

### 7.1 Pedicle width: pedicle_w (PDW)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Transverse dimension of the pedicle section perpendicular to its axis, digitised by points around it; position along the pedicle not stated (panjabi1991t p. 891, p. 893; panjabi1991c p. 862; panjabi1992 p. 301) | SAME; the generator. mnemonics.py calls it the smallest transverse diameter (schwingcheck/mnemonics.py), a word the papers do not use |
| tan2004 | Panjabi's drawings; position not stated (tan2004 p. 138) | SAME landmarks; 25.7% below Panjabi on average, about 41% at T4 and L5 (tan2004 p. 144) |
| zindrick1987 TW | Narrowest dimension in the transverse plane, on axial films of single vertebrae and on clinical CT (zindrick1987 p. 160, p. 161 Fig 1) | SAME in kind (isthmus, horizontal); mixed modality and unknown sample |
| olsewski1990, yu2015, lien2007, hou1993 A, mitra2002 TD | Narrowest mediolateral dimension, outer cortex to outer cortex, caliper on bone (olsewski1990 p. 542 Fig 1; yu2015 p. 1640, p. 1641 Fig 1B; lien2007 p. 1217 Fig 1; hou1993 p. 1851 Fig 1; mitra2002 p. 454 Fig 1) | SAME in kind |
| arockiaraj2025, duman2026, moncadahabib2025, masharawi2021 PW | Width across the pedicle on axial CT, outer cortex where stated; at the isthmus in the first two, position not stated in the last two (arockiaraj2025 p. 313 Fig 1; duman2026 p. 4, p. 5 Fig 2E; moncadahabib2025 p. 2 Fig 1A, p. 3 Fig 2B; masharawi2021 p. 3 Fig 1). moncadahabib2025's Figure 1 labels do not match its drawn lines (moncadahabib2025 p. 2; its note, Gaps): take its definition from Figure 2 and its values from Tables 1 and 2 only | SAME in kind; living CT |
| krag1988 | Width perpendicular to the pedicle axis on the mid-pedicle CT cut, and two corridor widths at 0 and 15 deg (krag1988 p. 28 Figs 1B, 1D) | SAME for the perpendicular width |
| otsuki2021, robertson2000 isthmus diameter | Minor axis of the isthmus ellipse (otsuki2021 p. 4 Fig 2A; robertson2000 p. 710) | DIFFERS: reads low at L4-L5 where the section rolls (above) |
| robertson2000 coaxial width | Medial to lateral extent within the wire marking the outer cortex, on a coaxial radiograph (robertson2000 p. 710) | DIFFERS: the bounding width of a tilted ellipse; at L5 about 3 mm above the horizontal chord through the centre (about 18.3) and about 8 mm above the minor axis (13.2/14.0) (robertson2000 Table 1 p. 711; its note, internal consistency) |
| makino2012 TPW | Minimum inner-cortex width perpendicular to the axis, on the axial plane parallel to the upper end plate (makino2012 p. 1517, p. 1518 Fig 1a) | DIFFERS: endosteal, reads about two cortices low |
| busscher2010 PedW | Pedicle width on CT of dissected spines (busscher2010 p. 1105) | SAME in kind |
| amonookuofi1982 C | Width of the right pedicle ring on an AP film (amonookuofi1982 pp. 226 to 227 Fig 2) | DIFFERS: projection, magnified |
| bonczar2024 | Pooled from mixed definitions (bonczar2024 p. 4 Fig 2) | pooled |

Biases a mask value carries (Inference unless cited):

- Scanner axes: a pedicle of width w inclined at angle a to the sagittal plane has a horizontal chord of w / cos a in the scanner's axial plane: 1.10 w at L5 (a = 24.5, panjabi1992 p. 302), 1.39 w at C4 (a = 44.2, panjabi1991c p. 864). The arockiaraj2025 note gives 13% at L5 from its own 28 deg angle.
- Minor axis instead of horizontal extent: low at L4 and L5 by 4 to 7 mm (the arithmetic above).
- Label 41 extent: not a pedicle at all (archive/bordercall/spineps_map.py).
- Section position: a minimum over sections reads at or below any single section; Panjabi's position is not stated, so the size of this bias is not known.
- Four width quantities are in play and differ at L4 and L5: the bounding width of the section (robertson2000's coaxial width), the horizontal chord through its centre (an axial CT cut), the minor axis of its ellipse (otsuki2021, robertson2000's isthmus), and Panjabi's horizontal extent of the section perpendicular to the axis (a bounding width by the arithmetic above, of a section cut another way than robertson2000's projection). Say which one a value is.

(b) Mask recipe

1. Run recipe P on each side.
2. Report the extent along u of the isthmus section as pedicle_w on that side; pedicle_w:mean is the mean of the two sides.
3. Store the ellipse minor axis too, to compare with otsuki2021 and robertson2000, and the H/W ratio (7.3).

(c) Radiograph

AP view only. Measure the outer edges of the pedicle ring and divide by the magnification, 1.14 for an AP film at 110 cm (eisenstein1977 p. 175). Expect a low reading at L5. On films of disarticulated vertebrae, the radiograph minus the direct width was 0, -0.1, -0.2, -0.6 and -3.5 mm at L1 to L5 (olsewski1990 p. 544 Table II). The densest image of the pedicle lies 1 to 3 mm inside the outer cortex (robertson2000 p. 711). krag1988 warns that its CT widths may bear little relation to widths read from an AP film (krag1988 p. 32). The AP ring is an oblique projection, since the pedicle converges 10 to 29 deg in the thorax (panjabi1991t note). The height-to-width ratio of the same ring is magnification-free (panjabi1992 note).

(d) Course, mm

| Level | Panjabi PDW | zindrick1987 TW | lien2007 | tan2004 |
|---|---|---|---|---|
| C2 | 8.0 | - | - | - |
| C3 | 5.6 | - | - | 4.45 |
| C4 | 5.4 | - | - | 4.55 |
| C5 | 5.6 | - | - | 4.8 |
| C6 | 5.9 | - | - | 5.25 |
| C7 | 6.5 | - | - | 5.65 |
| T1 | 8.4 | 7.9 | 7.65 | 7.45 |
| T2 | 8.2 | 7.0 | 5.45 | 5.95 |
| T3 | 6.8 | 5.6 | 4.0 | 4.6 |
| T4 | 6.2 | 4.7 | 3.5 | 4.0 |
| T5 | 6.0 | 4.5 | 3.8 | 4.0 |
| T6 | 6.0 | 5.2 | 3.95 | 4.35 |
| T7 | 5.8 | 5.3 | 4.4 | 4.45 |
| T8 | 6.7 | 5.9 | 4.8 | 4.5 |
| T9 | 7.7 | 6.1 | 5.25 | 4.95 |
| T10 | 9.0 | 6.3 | 5.65 | 5.95 |
| T11 | 9.8 | 7.8 | 7.2 | 7.0 |
| T12 | 8.7 | 7.1 | 7.55 | 7.55 |
| L1 | 8.6 | 8.7 | 6.45 | 5.55 |
| L2 | 8.2 | 8.9 | 7.2 | 6.3 |
| L3 | 10.1 | 10.3 | 9.15 | 7.6 |
| L4 | 14.1 | 12.9 | 11.9 | 8.85 |
| L5 | 18.6 | 18.0 | 17.6 | 11.55 |

(Panjabi side means: panjabi1991c p. 864 Table 4, panjabi1991t p. 894 Table 5, panjabi1992 p. 302 Table 4; zindrick1987 p. 161 Table 1; lien2007 p. 1218 Table 1, side means; tan2004 pp. 140 to 141 Table 1, side means.)

Lumbar series, mm, L1 to L5:

| Series | Population and method | Values |
|---|---|---|
| yu2015 | 503 Hamann-Todd skeletons, 404 men and 99 women, dry bone, sides averaged (yu2015 p. 1645 Table 5) | 8.52, 8.66, 10.46, 13.19, 18.33 |
| olsewski1990 | embalmed cadavers, 24 men and 25 women, caliper (olsewski1990 p. 544 Table I) | men 9.5, 9.6, 11.7, 14.7, 21.1; women 7.7, 7.9, 9.6, 12.5, 18.4 |
| olsewski1990 | 51 living patients, CT (olsewski1990 p. 545 Table III) | men 9.0, 9.9, 11.8, 13.7, 16.7; women 6.3, 7.1, 8.2, 10.0, 13.5 |
| robertson2000 | 10 dry spines, coaxial radiograph within the wire (robertson2000 p. 711 Table 1) | left 10.3, 10.3, 13.0, 16.3, 21.6 |
| hou1993 | 40 Chinese dry columns, T9 to L5 (hou1993 p. 1852 Table 1) | T9 5.7, T10 6.8, T11 8.1, T12 8.3; 7.0, 7.4, 9.2, 10.5, 12.9 |
| krag1988 | 41 living patients, CT, perpendicular to the axis, read from Fig 5 (krag1988 p. 30) | T9 7.0, T10 7.15, T11 7.4, T12 6.8; 7.2, 8.6, 9.3, 11.0, 13.85 |
| mitra2002 | 18 Indian men, direct (mitra2002 p. 455 Table 1) | 7.05, 7.85, 9.01, 11.6, 16.19 |
| bonczar2024 | 18 pooled studies (bonczar2024 pp. 5 to 9 Tables 2 to 6) | 7.51, 8.23, 9.71, 11.52, 14.58 |
| masharawi2021 | 25 control men, CT, left (masharawi2021 p. 11 Table 5) | 7.63, 8.83, 10.50, 10.78, 15.51 |
| moncadahabib2025 | 37 Mexican adults, CT, left (moncadahabib2025 p. 5 Table 2) | 7.0, 7.0, 8.1, 9.3, 11.8 |
| arockiaraj2025 | 300 Saudi adults, CT (arockiaraj2025 p. 316 Table 2) | 5.76, 6.34, 8.11, 9.82, 13.62 |
| duman2026 | 277 Turkish men, CT, T11 to L2 (duman2026 p. 8 Table 2) | T11 7.62, T12 8.46; 9.53, 10.08 |
| busscher2010 | 6 Dutch men, CT (busscher2010 p. 1112 Fig 8, read from the figure) | minimum T4 4.3; L1 7.3; L5 14.3 |
| otsuki2021 minor axis | 6 cadaver spines, micro-CT (otsuki2021 p. 6 Table 2) | 7.1, 7.3, 9.4, 10.6, 11.8 |
| makino2012 endosteal | 50 Japanese patients, CT (makino2012 p. 1518 Table 1) | 5.46, 5.76, 7.25, 9.01, 12.86 |

Where it peaks, bottoms out and separates (steps over the mean SD of the two levels, from Panjabi's long table, Inference):

- C2 is widest (8.0) and C3 to C6 flat at 5.4 to 5.9 (panjabi1991c p. 864). The C2/C3 step reads -2.0 SD, but the C2 left SEM of 0.07 is implausibly small (panjabi1991c note), so the size of that separation is not trusted.
- C7/T1: +1.9 mm, 1.26 SD. Separates.
- T3 to T8: the narrowest stretch in every series. The minimum is T5 in zindrick1987 (4.5, p. 161), T4 in lien2007 (3.5, p. 1218) and busscher2010 (4.3), and T7 in Panjabi (5.8). No pair from T3 to T8 separates (0.02 to 0.44 SD).
- T11/T12 and T12/L1: widths fall at T12 in Panjabi and zindrick1987, and fall again at L1 in lien2007 (7.55 to 6.45), hou1993 (8.3 to 7.0), tan2004 (7.55 to 5.55) and krag1988's T12 (6.8). The T12/L1 step is -0.03 SD in Panjabi's means, a between-spine step that does not test a dip within one spine. Within a spine, L1 was narrower than both T12 and L2 in every one of 40 Chinese columns (hou1993 p. 1851; Table 1 p. 1852: 8.3, 7.0, 7.4 mm). Use the within-spine dip at L1 as a junction cue, not the absolute width. tan2004's note calls its T12/L1 drop sample-specific, since the Panjabi widths implied by its Table 2 show none (tan2004 note).
- L2/L3 0.86, L3/L4 2.45 and L4/L5 1.95 SD in Panjabi. Every lumbar series rises from L2 to L5, and the L4/L5 step is the largest pedicle-width step in most series (olsewski1990 men 2.1 SD, its note; zindrick1987 1.6 SD, its note; makino2012 1.74, its note; arockiaraj2025 +3.80 mm, about 2.8 pooled SD, against 0.6 at L1/L2, its note; mitra2002 men +2.59 mm at L3/L4 and +4.59 at L4/L5, no SD printed, its note). L1/L2 never separates (0.04 to 0.2 SD in olsewski1990, zindrick1987 and makino2012 notes).

(e) Covariates

- Sex: women narrower by 12 to 20% (Inference: yu2015 female/male 7.06/8.88 = 0.80 to 16.47/18.78 = 0.88, p. 1643 Table 4); women significantly smaller at every level in cadavers and the living (olsewski1990 p. 544 Table I, p. 545 Table III); men larger at T11, L1 and L2 but not T12 (duman2026 p. 8 Table 2).
- Stature: +2.07 to +7.59 mm per metre of height, adjusted (yu2015 p. 1641 Table 2). Age: +0.008 to +0.026 mm per year (yu2015 p. 1641 Table 2); no age effect in duman2026 (p. 8 Table 4).
- Population: Chinese dry bone 25.7% below Panjabi (tan2004 p. 144); Indian men 16.19 against white men 21.1 at L5 (mitra2002 p. 457); the Saudi CT series is the narrowest in the set (arockiaraj2025 p. 316). Narrow pedicles under 5.5 mm in 4.77% at L1 and 2.78% at L2 (yu2015 p. 1643 Fig 3).

### 7.2 Pedicle height: pedicle_h (PDH)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Vertical dimension of the same perpendicular section (panjabi1991t p. 891 Fig 3C; panjabi1991c p. 862; panjabi1992 p. 301) | SAME; the generator |
| tan2004 | Panjabi's drawings (tan2004 p. 138) | SAME landmarks; 16.1% below Panjabi (tan2004 p. 144) |
| zindrick1987 SW, olsewski1990, yu2015, lien2007, hou1993 B, mitra2002 SD | Narrowest craniocaudal dimension at the isthmus, between the superior and inferior notches (zindrick1987 p. 162 Fig 2; olsewski1990 p. 542 Fig 2; yu2015 p. 1640, p. 1641 Fig 1A; lien2007 p. 1217 Fig 1; hou1993 p. 1851; mitra2002 p. 454 Fig 2) | SAME in kind |
| arockiaraj2025, duman2026, moncadahabib2025, masharawi2021 | Craniocaudal height at the isthmus on sagittal CT (arockiaraj2025 p. 313 Fig 3; duman2026 p. 5 Fig 2C; moncadahabib2025 p. 3 Fig 2A; masharawi2021 p. 3 Fig 1) | SAME in kind; living CT |
| otsuki2021 major axis, robertson2000 coaxial height | Major axis of the isthmus ellipse; coaxial outer extent (otsuki2021 p. 4; robertson2000 p. 710) | DIFFERS at L4-L5: the major axis is longer than the vertical extent of a rolled section |
| makino2012 SPW | Minimum inner-cortex height perpendicular to the axis (makino2012 p. 1518 Fig 1b) | DIFFERS: endosteal; and its cranial and caudal walls are 2.5 to 4.0 mm thick (otsuki2021 p. 6 Table 2), so endosteal heights should read 5.7 to 6.9 mm below outer heights (Inference: the sum of the cranial and caudal walls at L1 to L5) |

Biases (Inference): the vertical extent of a pedicle tilted by PDIt in the sagittal plane reads high by 1 / cos(PDIt) if taken along scanner or frame Y without reslicing, a small effect (cos 11.6 deg = 0.98 at T7 and T8, the largest thoracic mean, panjabi1991t p. 894). A mask extent of label 41 at the pedicle includes the notches' rims only if the bridge is cut correctly; recipe P's step 2 controls it.

(b) Mask recipe: recipe P, the extent along v of the isthmus section. Store the major axis too. pedicle_h:mean is the side mean.

(c) Radiograph

Lateral view, the narrowest vertical dimension of the pedicle between the notches, both sides superimposed (panjabi1992 note). Divide by 1.23 (eisenstein1977 p. 175). On films of disarticulated vertebrae the radiograph minus the direct height was +1.8, +1.8, +1.5, +0.2 and -2.4 mm at L1 to L5 (olsewski1990 p. 544 Table II); mitra2002's lateral films agreed with direct heights within 0.9 mm in men (mitra2002 p. 455 Table 2). The AP ring gives a height too, distorted by the pedicle's convergence (panjabi1992 note).

(d) Course, mm

| Level | Panjabi PDH | zindrick1987 SW | lien2007 | tan2004 |
|---|---|---|---|---|
| C2 | 10.2 | - | - | - |
| C3 | 7.4 | - | - | 6.75 |
| C4 | 7.3 | - | - | 6.65 |
| C5 | 7.0 | - | - | 6.1 |
| C6 | 7.3 | - | - | 6.0 |
| C7 | 7.5 | - | - | 6.3 |
| T1 | 9.6 | 9.9 | 8.65 | 8.5 |
| T2 | 11.3 | 12.0 | 10.3 | 9.5 |
| T3 | 11.9 | 12.4 | 10.4 | 9.8 |
| T4 | 12.1 | 12.1 | 10.3 | 9.15 |
| T5 | 11.3 | 11.9 | 10.55 | 9.05 |
| T6 | 11.8 | 12.2 | 10.2 | 8.9 |
| T7 | 12.0 | 12.1 | 10.4 | 9.55 |
| T8 | 12.5 | 12.8 | 10.85 | 10.35 |
| T9 | 13.9 | 13.8 | 12.35 | 10.9 |
| T10 | 14.8 | 15.2 | 13.65 | 12.9 |
| T11 | 17.4 | 17.4 | 15.1 | 14.25 |
| T12 | 16.6 | 15.8 | 15.1 | 14.1 |
| L1 | 15.9 | 15.4 | 13.65 | 13.1 |
| L2 | 14.9 | 15.0 | 14.05 | 12.85 |
| L3 | 14.4 | 14.9 | 13.9 | 12.5 |
| L4 | 15.4 | 14.8 | 12.75 | 13.2 |
| L5 | 19.6 | 14.0 | 12.5 | 17.4 |

(Panjabi: the same tables as 7.1; zindrick1987 p. 162 Table 2; lien2007 p. 1218 Table 1; tan2004 pp. 140 to 141 Table 1.)

Lumbar series, mm, L1 to L5: yu2015 15.75, 15.06, 14.59, 13.81, 13.67 (503 skeletons, p. 1645 Table 5); olsewski1990 cadaver men 17.0, 16.0, 16.1, 16.4, 17.4 (p. 544 Table I); mitra2002 men direct 15.68, 15.27, 15.03, 14.79, 15.67 (p. 455 Table 2); masharawi2021 control men left 12.68, 12.07, 11.85, 10.91, 9.50 (p. 11 Table 5); moncadahabib2025 left 12.8, 12.3, 12.1, 11.3, 10.2 (p. 5 Table 2); arockiaraj2025 9.75, 9.32, 9.11, 8.71, 8.3 (p. 316 Table 2); makino2012 SPW 11.89, 10.44, 10.23, 9.36, 8.95 (p. 1518 Table 1); hou1993 15.8, 15.1, 14.7, 15.0, 19.8 (40 Chinese dry columns, p. 1852 Table 2); otsuki2021 major axis 17.0, 15.8, 15.8, 18.8, 24.2 (p. 6 Table 2); robertson2000 coaxial heights, flat at 17.4 to 19.9 (its note); duman2026 men T11 14.17, T12 14.65, L1 15.21, L2 16.24 (p. 8 Table 2).

Where it peaks and separates:

- C2/C3 -2.33 SD (inflated by C2's small left SEM, as for width); C3 to C7 flat.
- C7/T1 +1.57 and T1/T2 +1.20 SD: height marks the cervicothoracic junction in Panjabi, and T1 is the shortest thoracic pedicle in zindrick1987 (9.9) and lien2007 (8.65).
- T10/T11 +1.91 SD: T11 is the peak in Panjabi (17.4) and zindrick1987 (17.4); lien2007 ties T11 and T12 (15.1); hou1993 T9 12.9, T10 14.3, T11 16.2, T12 16.6 (p. 1852 Table 2).
- L1 to L4: 0.28 to 0.53 SD a step (-0.40, -0.28 and +0.53 SD, Inference from the long table); height separates no lumbar pair but L4/L5 in Panjabi (+1.72 SD).
- Disagreement at L5. Panjabi rises to 19.6 and hou1993 to 19.8 (p. 1852 Table 2); olsewski1990 and mitra2002 rise a little. zindrick1987 (14.0), yu2015 (13.67), lien2007 (12.5), masharawi2021, moncadahabib2025, arockiaraj2025 and makino2012 all fall to L5. Panjabi's own text records that Berry and Zindrick found a fall where his series and Scoles found a rise (panjabi1992 p. 305). Inference from the ellipse arithmetic above: the vertical extent of a section rolled 50 deg is about 18 mm at L5, near Panjabi's, while a caliper laid craniocaudally across the narrowest part reads less; the direction of the L5 step depends on how the section is cut.
- Disagreement at T11 to L2. duman2026 rises from T11 to L2 in men (14.17 to 16.24) while Panjabi, zindrick1987 and lien2007 fall from T11 or T12 to L2. duman2026's levels are not defined by any counting rule (duman2026 note), so the cause is not known.

(e) Covariates: men larger by 1.07 to 1.47 mm, and +4.97 to +5.68 mm per metre of height, adjusted (yu2015 p. 1643 Table 4, p. 1641 Table 2); women smaller in cadavers and the living (olsewski1990 p. 544); men taller at every level on CT (arockiaraj2025 p. 316 Table 2); Chinese dry bone 16.1% below Panjabi (tan2004 p. 144).

### 7.3 Pedicle area, shape and isthmus: pedicle_area (PDA), with H/W and MPD (no key for the last two)

(a) Definitions

- Panjabi: area of the pedicle section perpendicular to its axis, by the projected-area method (panjabi1992 p. 300; panjabi1991c p. 866; panjabi1991t p. 893). The generator.
- tan2004: the same section, digitiser (tan2004 p. 138). SAME.
- otsuki2021: whole isthmus section area and medullary cavity area, micro-CT (otsuki2021 pp. 4 to 5). SAME in kind for the whole section, which is the isthmus by its own rule.
- bonczar2024 PA: plane not stated (bonczar2024 p. 4 Fig 2). Not comparable.
- makino2012 MPD: the largest circle about the axis inside the inner cortex, in the section perpendicular to the axis (makino2012 p. 1518 Fig 1c). A screw diameter, not an area; no generator key.
- Ratio PDH/PDW: derived by Panjabi per side (panjabi1992 p. 302 Table 4; panjabi1991t p. 894 Table 5; panjabi1991c p. 864 Table 4). The generator does not hold it; it follows from pedicle_w and pedicle_h.

Biases (Inference): a mask section's plain area equals Panjabi's projected area only if it is cut perpendicular to the axis; an axial-plane cut through a pedicle inclined by a reads high by 1 / cos a. Partial volume matters: a boundary error of half a voxel (0.5 mm at 1 mm voxels) moves the area of a 6 by 12 mm thoracic section by about 0.5 x its perimeter, about 15 mm2 of 57 mm2, roughly 25% (Inference: Ramanujan's perimeter of that ellipse is 29 mm).

(b) Mask recipe: recipe P, the area of the isthmus section (a planar section, so its plain area is its vector area, O2). Also store H/W from 7.1 and 7.2, the ellipse roll, and MPD as twice the distance from the axis point to the nearest boundary voxel, which the outer mask boundary makes an outer-cortex MPD, not makino2012's.

(c) Radiograph: area is not measurable on a film (panjabi1992 note). Shape estimates from AP width and lateral height: the triangle W x H / 2 matched the section well at T2 to T12 (panjabi1991t p. 900; Inference in its note, from Table 5: within about 11% at T2 to T9, 18% over on the left at T10, and 16 to 26% under at T11 and T12) and came closest in the neck (panjabi1991c p. 866, p. 868); in the lumbar spine the ellipse fits best at L1 and L2 and the triangle at L4 and L5 (panjabi1992 p. 305). At L5, though, Panjabi's areas (143.9 right, 158.7 left) are below even the triangle W x H / 2 (176 and 187, computed), so no convex section has his L5 width, height and area at once; a mask can match at most two of them there, and the L5 area should be treated as a source inconsistency (panjabi1992 Table 4 p. 302; its note, generator section). tan2004's PDA / (PDH x PDW) is 0.77 to 1.05 (tan2004 note), nearer an ellipse's 0.785 than a triangle's 0.5 at most levels. Inference: the shape rule is level-dependent; do not use one shape factor for all levels. The H/W ratio is the radiograph-ready shape measure: magnification-free on one AP ring.

(d) Course

| Level | Panjabi PDA, mm2 | Panjabi H/W (side mean) | tan2004 PDA |
|---|---|---|---|
| C2 | 42.0 | 1.28 | - |
| C3 | 22.8 | 1.30 | 28.1 |
| C4 | 24.4 | 1.37 | 28.3 |
| C5 | 23.9 | 1.27 | 28.0 |
| C6 | 26.2 | 1.22 | 31.2 |
| C7 | 29.1 | 1.13 | 32.9 |
| T1 | 53.3 | 1.14 | 56.5 |
| T5 | 32.4 (minimum) | 1.90 | 33.6 |
| T10 | 63.2 | 1.65 | 73.0 |
| T11 | 93.3 | 1.78 | 93.1 |
| T12 | 94.0 | 1.91 | 95.6 |
| L1 | 87.5 | 1.86 | 68.2 |
| L2 | 83.4 | 1.81 | 72.0 |
| L3 | 94.1 | 1.42 | 93.0 |
| L4 | 107.5 | 1.10 | 101.3 |
| L5 | 151.3 | 1.06 | 157.6 |

(Panjabi: panjabi1991c p. 864 Table 4; panjabi1991t p. 894 Table 5 and p. 893; panjabi1992 p. 302 Table 4. H/W: side means of the printed ratios in the neck and the lumbar spine; in the thorax the ratio of the side-mean height to the side-mean width, Inference, since the printed thoracic left ratios at T3 and T4 disagree with their own means (panjabi1991t note). tan2004 pp. 140 to 141 Table 1, side means, Inference.)

- otsuki2021 whole isthmus area, L1 to L5: 95.7, 92.5, 113.7, 152.4, 204.2 mm2; cavity 53.2, 43.3, 56.3, 83.2, 118.7 (otsuki2021 p. 6 Table 2). It runs 8 to 53 mm2 above Panjabi's lumbar areas (Inference: 95.7 - 87.5 and 204.2 - 151.3). The cause is not known: the samples differ, and Panjabi's section position is not stated.
- makino2012 MPD, L1 to L5: 5.09, 5.39, 6.52, 6.83, 7.36 mm; it falls 5.5 mm short of TPW at L5 (makino2012 p. 1518 Table 1, its note). robertson2000's isthmus diameter plateaus at 12 to 14 mm from L3 down while the width keeps rising (robertson2000 p. 711).
- H/W crosses 1 only at L5 in most series. Ratios at L5 of 1.09 and 1.02 by side (panjabi1992 p. 302); W/H 1.21 in men and 1.14 in women at L5 (olsewski1990 note); TPW/SPW 1.44 at L5 (makino2012 note); W/H about 1.1 to 1.2 at L5 (robertson2000 note); TW/SW over 1 only at L5 (zindrick1987 note). W/H is 1.34 at L5 and 0.96 at L4 in yu2015 (Table 5 p. 1645; Inference in its note), 1.41 and 0.93 in lien2007 (Table 1 p. 1218; Inference in its note), and 1.16 to 1.22 and 0.82 in moncadahabib2025 (Table 2 p. 5; Inference in its note), so L4 comes near 1 in two series. In the thorax the text gives H/W 1.1 at T1 and near 1.8 to 2.0 from T5 to T12 (panjabi1991t p. 893); Table 5's side means run 1.65 (T10) to 2.05 (T7), with T11 1.78 (Inference, computed). lien2007's dry bone is steeper: W/H 0.88 at T1, 0.53 at T2 and 0.34 to 0.50 from T3 to T12, H/W about 2.0 to 2.9 below T2 (Inference from Table 1 p. 1218, its note). Both series put T1 apart as the marker.
- duman2026 TPD/SPD, width over height, 0.53, 0.57, 0.61, 0.63 at T11 to L2 (Inference from Table 2 p. 8, its note), rising steadily with no step at T12/L1; free of scale and magnification.
- Roll of the isthmus section (recipe P step 5) is makino2012's cephalocaudal inclination CI, the long axis against the normal to the upper end plate: 3.47, 5.01, 18.04, 39.06, 51.81 deg at L1 to L5 (SD 4.75, 7.60, 9.39, 8.36, 5.18; makino2012 p. 1518 Table 1). Adjacent separations about 0.24, 1.53, 2.36 and 1.83 SD (Inference, its note): the best single L3, L4 and L5 cue in that paper, blind at L1/L2. Its sign is not stated, and it is not defined for a near-round section.
- Separations of area: C2/C3 -2.99 SD (C2's suspect SEM again), C7/T1 +1.73, T10/T11 +1.49, L4/L5 +1.46 SD; nothing else above 0.7 SD.

(e) Covariates: none in Panjabi (sexes pooled, panjabi1992 p. 299). Area follows width and height (7.1, 7.2). Wall thickness by level is in 7.6.

Second moments: if pedicle second moments are used, compute pi H^3 W / 64 and pi H W^3 / 64 from H and W (panjabi1991t p. 893); Figure 6E's plotted values are 16 times larger (Inference, panjabi1991t note: T11 left plotted about 47,000 mm4 against about 2,960 from the printed formula; Fig 6E p. 897).

### 7.4 Pedicle angles: pedicle_incl_sag (PDIs) and pedicle_incl_trans (PDIt)

Panjabi's names are the reverse of the clinical ones. PDIs, the inclination to the sagittal plane, is the clinical transverse (axial) angle of convergence. PDIt, the inclination to the transverse plane, is the clinical sagittal angle (panjabi1992 p. 302, p. 300 Fig 1; panjabi1991t p. 891 Figs 3B and 3C).

(a) Definitions, PDIs (convergence)

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Angle of the pedicle centre line, normal to its section, to the vertebra's sagittal plane (panjabi1992 p. 302; panjabi1991t p. 891 Fig 3C, p. 893; panjabi1991c p. 862) | SAME; the generator. No divergent value was found (panjabi1991t p. 898) |
| tan2004 | Panjabi's drawing, after Zindrick's definition (tan2004 p. 138) | SAME; signed; T8 to T12 reversed, possibly a sign error (tan2004 pp. 140 to 141 Table 1; its note, Gaps) |
| zindrick1987 TA | Line perpendicular to the transverse isthmus against a line parallel to the midline; positive medial (zindrick1987 p. 163 Fig 3) | SAME in kind; signed |
| krag1988 | Visually fitted pedicle axis against the sagittal plane on the mid-pedicle CT cut; anteromedial positive (krag1988 p. 28 Fig 1B) | SAME in kind |
| olsewski1990, lien2007, hou1993, mitra2002, arockiaraj2025, duman2026 | Pedicle axis against the midline or a line parallel to it, in the transverse plane (olsewski1990 pp. 542 to 543 Fig 4; lien2007 p. 1217 Fig 1a; hou1993 p. 1851; mitra2002 p. 454 Fig 1; arockiaraj2025 p. 313 Fig 2; duman2026 p. 5 Fig 2D) | SAME in kind; references to the image's vertical in arockiaraj2025 (its note) carry the vertebra's axial rotation |
| moncadahabib2025 | Vertex on the midline at the anterior body cortex (moncadahabib2025 p. 3 Fig 2D) | DIFFERS: its note finds the range compressed by this convention |
| busscher2010 PedA | From the anterior midline point of the body through the pedicle (busscher2010 p. 1105 Fig 1, by its note) | DIFFERS in the same way |

Biases (Inference): a midline taken from the image rather than frame F adds the vertebra's axial rotation to one side and subtracts it from the other; the side mean cancels it (panjabi1991t note). A centre line fitted to the whole label-41 bridge, rather than normal to the isthmus section, follows the bridge's curve.

(a) Definitions, PDIt (sagittal tilt)

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c, panjabi1991t, panjabi1992 | Angle of the centre line to the vertebra's transverse plane; drawn with the posterior end higher in all three papers; signed in the neck (negative "below") and thorax; the lumbar paper states no sign convention (panjabi1992 p. 302), and Inference: its values are unsigned (panjabi1992 note, PDI) (panjabi1991c p. 862, p. 866; panjabi1991t p. 891 Fig 3B; panjabi1992 p. 300 Fig 1) | SAME; the generator |
| zindrick1987 SA | Deviation of the axis from the perpendicular to the posterior body wall, positive cephalad, which end not stated (zindrick1987 p. 164 Fig 4) | SAME reference plane (the posterior wall, as frame F); sign unclear |
| olsewski1990, mitra2002 | Axis against the superior end plate; positive when the anterior end is higher (olsewski1990 p. 543 Fig 5; mitra2002 p. 454 Fig 2) | DIFFERS: end-plate reference, so it differs from PDIt by the end-plate inclination EPItu (section 3.5); the sign may be opposite to Panjabi's drawing |
| lien2007 SA | Axis against the superior border of the body (lien2007 p. 1217 Fig 1b) | DIFFERS: end-plate reference |
| tan2004 | Side view, axis against Z; positive is what the paper calls cephalad (tan2004 note, sign by Inference) | SAME reference; lumbar values negative |

(b) Mask recipe

1. Take the axis from recipe P, oriented from posterior to anterior.
2. PDIs = the angle between the axis and frame F's YZ plane: arcsin(|a_x|), with a the unit axis. Positive when the axis runs anteromedially; store the sign.
3. PDIt = the angle between the axis and the XZ plane: arcsin(|a_y|). Store the sign as positive when the posterior end is cranial, Panjabi's drawing.
4. Report side means for pedicle_incl_sag:mean and pedicle_incl_trans:mean; store the right-left difference.

(c) Radiograph: PDIs needs an axial image; it cannot be read on an AP or a lateral film (panjabi1992 note; panjabi1991t note). PDIt can be approximated on a lateral film as the pedicle's tilt from the perpendicular to the posterior body line, where the pedicle outline shows (panjabi1992 note); in the neck the pedicle overlaps the lateral mass (panjabi1991c note). Lateral films read the end-plate-referenced sagittal angle 3.4 to 6.1 deg low in men (mitra2002 p. 455 Table 2). Axial radiographs of disarticulated vertebrae read the transverse angle higher than direct at L2 to L5 (8, 13, 16, 29 against 6, 7, 11, 22 deg; olsewski1990 Table II p. 544; p. 545); no clinical AP or lateral film gives this angle.

(d) Course, PDIs, deg

| Level | Panjabi (side mean) | zindrick1987 | lien2007 | krag1988 | tan2004 (magnitude mean) |
|---|---|---|---|---|---|
| C3 | 42.2 | - | - | - | 41.3 |
| C4 | 44.2 | - | - | - | 41.5 |
| C5 | 40.2 | - | - | - | 42.2 |
| C6 | 31.9 | - | - | - | 40.2 |
| C7 | 29.9 | - | - | - | 30.5 |
| T1 | 27.1 | 26.6 | 28.2 | - | 24.2 |
| T2 | 28.6 | 19.1 | 26.35 | - | 17.3 |
| T3 | 19.4 | 14.6 | 23.3 | - | 12.0 |
| T4 | 19.5 | 12.6 | 22.85 | - | 8.65 |
| T5 | 15.6 | 9.4 | 18.2 | - | 9.45 |
| T6 | 16.4 | 9.6 | 15.4 | - | 7.15 |
| T7 | 20.7 | 8.7 | 12.8 | - | 6.9 |
| T8 | 19.6 | 8.1 | 13.8 | - | 8.6 (divergent) |
| T9 | 14.8 | 7.6 | 12.5 | 6.6 | 6.75 (divergent) |
| T10 | 12.4 | 4.6 | 9.0 | 5.85 | 5.2 (divergent) |
| T11 | 13.1 | 1.2 | 8.0 | 0.3 | 6.85 (divergent) |
| T12 | 9.8 | -4.2 | 7.9 | -0.3 | 6.25 (divergent) |
| L1 | 14.4 | 10.9 | 8.45 | 11.7 | 4.8 |
| L2 | 14.2 | 12.0 | 12.35 | 13.35 | 7.4 |
| L3 | 18.5 | 14.4 | 15.25 | 18.0 | 14.35 |
| L4 | 16.5 | 17.7 | 18.9 | 19.5 | 11.1 |
| L5 | 24.5 | 29.8 | 24.35 | 27.8 | 19.9 |

(Panjabi: panjabi1991c p. 864, panjabi1991t p. 894, panjabi1992 p. 302; zindrick1987 p. 163 Table 3; lien2007 p. 1218 Table 2; krag1988 p. 31 Fig 6, read from the figure; tan2004 pp. 140 to 141 Table 1, the mean of the two magnitudes, Inference.)

Lumbar series, L1 to L5, deg: olsewski1990 cadaver men 7, 7, 8, 11, 17 (p. 544 Table I); mitra2002 men direct 9, 10.05, 12.33, 14.72, 29.33 (p. 455 Table 1); arockiaraj2025 12.68, 13.26, 15.47, 17.47, 28.23 (p. 316 Table 2); moncadahabib2025 left 16.8, 16.5, 17.0, 18.6, 21.9 (p. 5 Table 2); duman2026 men T11 21.18, T12 23.45, L1 25.55, L2 27.79 (p. 8 Table 2); hou1993 T12 about -2.5 to L5 about 30.5 (p. 1854 Fig 7, read from the figure); busscher2010 T12 about 0, L1 13.8, L5 about 35, C4 52.2 (p. 1112 Fig 8b, read from the figure).

Where it separates:

- C5/C6: -8.4 deg (0.71 SD); convergence falls through the lower neck (panjabi1991c p. 866).
- T2/T3: about 9 deg, the largest thoracic step in Panjabi (panjabi1991t note), but T2's SD is 25.5 deg and the step is 0.53 SD.
- T11 to L1: the series disagree. Panjabi stays convergent (9.8 at T12) and steps up 4.7 deg at L1 (0.51 SD). zindrick1987 goes divergent at T12 (-4.2) and steps 15.1 deg to L1, 2.2 SD by its note; krag1988 steps about 12 deg, about 3 SD by its note; hou1993 steps T12/L1 1.1 SD (its note). lien2007 stays flat, T11, T12 and L1 within 0.1 to 0.3 SD (its note); tan2004 reverses sign from T8 to T12 (tan2004 note). That reversal is abrupt and uniform (right +8.6 at T7 to -7.6 at T8; left -5.2 to +9.6), both sides flip back at L1, and with the sign flipped T8 to T12 would join T7 and L1 smoothly, which suggests a sign or handedness error; against that, its Table 3 implies Zindrick's own T12 value is slightly negative (tan2004 Table 1 pp. 140 to 141; Table 3 p. 144; its note, Gaps and instruction 9). Do not use tan2004's sign as a level marker until CT confirms it. The populations are 12 autopsy spines (Panjabi), specimens and CTs of unknown number (zindrick1987), 41 living patients (krag1988), 40 Chinese dry columns with 10 for angles (hou1993), 15 Taiwanese dry sets (lien2007) and 10 Chinese cadavers (tan2004). Inference: in four of six series the thoracolumbar pedicles are near-parallel or divergent at T11 and T12 and converge again at L1; treat a near-zero convergence as a T11/T12 cue with a wide error, and do not draw it from Panjabi alone.
- L4/L5: +8.0 deg, 1.15 SD in Panjabi; +12.1 in zindrick1987 (2.1 SD, its note), +10.76 in arockiaraj2025 (about 3 pooled SD, its note), +14.6 in mitra2002 men. The one lumbar step every series shows.

(d) Course, PDIt, deg

| Level | Panjabi | zindrick1987 SA | lien2007 SA | tan2004 |
|---|---|---|---|---|
| C3 to C5 | -8.1, -7.5, -6.0 | - | - | -5.65, -4.3, 3.75 |
| C6, C7 | 6.5, 11.3 | - | - | 5.4, 4.45 |
| T1 | 7.5 | 12.6 | 11.6 | 4.05 |
| T2 | 17.9 | 17.5 | 18.9 | 7.2 |
| T3 to T11 | 7.0 to 11.6 | 15.0 to 17.3 | 12.15 to 17.85 | 3.65 to 7.8 |
| T12 | 5.0 | 11.6 | 10.7 | 3.75 |
| L1 | 2.5 | 2.4 | 6.1 | -1.65 |
| L2 | 2.7 | 1.8 | 5.45 | -2.15 |
| L3 | 2.6 | 0.2 | 5.0 | -3.8 |
| L4 | 3.9 | 0.2 | 3.35 | -6.8 |
| L5 | 5.5 | -1.8 | 2.9 | -7.05 |

(Panjabi: the same tables; zindrick1987 p. 164 Table 4; lien2007 p. 1218 Table 2; tan2004 pp. 140 to 141 Table 1, side means, Inference.)

- C5/C6: the sign changes, +12.5 deg, 2.14 SD in Panjabi (panjabi1991c p. 866); tan2004 changes sign one level higher, at C4/C5 (tan2004 note).
- T11/T12 -1.01 SD and T12/L1 -0.82 SD in Panjabi; zindrick1987's L1/T12 step is 1.9 SD and lien2007's 2.8 SD (their notes); tan2004 changes sign at T12/L1. Every series flattens the pedicle at the thoracolumbar junction. This is the most consistent pedicle-angle cue for T12 against L1.
- Lumbar: Panjabi rises from 2.5 to 5.5; zindrick1987 falls to -1.8 and tan2004 to -7.05. Olsewski's end-plate-referenced angle is flat at +5 to +7 cephalad at L1 to L4, with L5 bimodal: caudad in 12 of 83 cadaver pedicles and 2 of 94 living ones (olsewski1990 p. 544 Table I; pp. 545 to 547). The lumbar sign is not settled across conventions; score the lumbar magnitude only.
- T2: 17.9 deg with SD 30.7 in Panjabi, an outlier (panjabi1991t note).

(e) Covariates: sex significant only at L1 and L2 and below 1 deg (arockiaraj2025 p. 316 Table 2); none in duman2026 (p. 8 Table 2) or moncadahabib2025 (p. 6 Table 3), where age correlates weakly, rho -0.16 to -0.19 (p. 6 Table 4); women 1 to 2 deg smaller at L1 and L2 in cadavers (olsewski1990 p. 547). Population: Indian men converge 29.3 deg at L5 against 17 in olsewski1990's white series (mitra2002 p. 456); tan2004 offers its T8 to T12 divergence as an ethnic difference (tan2004 p. 145), but its note suspects a sign error (above), so do not use it as an ethnic factor until CT confirms it. Right exceeds left by 4.0 to 9.2 deg at T3 to T10 in Panjabi, which may be a frame yaw (panjabi1991t note).

### 7.5 Pedicle length and chord length (no generator key)

These are not generator keys. They are listed because the screw-path chord steps at T12/L1 and can be predicted from a lateral film.

| Paper | Definition | L1 to L5 (and junction) |
|---|---|---|
| krag1988 CL0, CL15 | Chord from line B (the posterior lamina surface; methods p. 28, chosen so that facet anatomy does not enter; the Fig 1C caption and p. 32 say posterior cortex, so the paper contradicts itself) through the isthmus centre to the anterior cortex, at 0 and 15 deg to the AP midline axis (krag1988 p. 28 Fig 1C; its note) | CL0 42.8, 44.4, 40.7, 39.8, 36.0; T12 40.9; means 42 at 0 deg and 50 at 15 deg (krag1988 p. 28 Fig 2, p. 29) |
| zindrick1987 Dpa | From the most posterior aspect of the transverse process to the anterior cortex along the transverse pedicle angle (zindrick1987 p. 165 Fig 5) | 50.7, 51.9, 51.9, 49.7, 51.0; T12 38.6, a 1.45 SD step at T12/L1 by its note (zindrick1987 p. 165 Table 5) |
| zindrick1987 Dma | Same start, parallel to the midline (zindrick1987 p. 165) | 44.7, 45.5, 44.4, 40.7, 33.7 |
| olsewski1990 | Posterior laminar cortex to anterior body cortex through the pedicle middle (olsewski1990 pp. 542 to 543 Fig 6) | men 45.0, 46.8, 49.0, 50.4, 46.2 (olsewski1990 p. 544 Table I) |
| tan2004 PL | Facet cortex to anterior body cortex along PDIs (tan2004 p. 145) | 41.4, 43.8, 42.2, 39.7, 39.2; T12 31.5, a +9.9 mm step (tan2004 pp. 140 to 141) |
| arockiaraj2025 CL, mitra2002 CL, moncadahabib2025 PL, duman2026 PL | Screw-path chords on CT or bone (arockiaraj2025 p. 313 Fig 1; mitra2002 p. 454 Fig 1; moncadahabib2025 p. 3 Fig 2C; duman2026 p. 5 Fig 2B) | arockiaraj2025 49.18 to 47.63 (p. 316 Table 2); mitra2002 about 46; moncadahabib2025 about 40; duman2026 T11 41.2 (their notes) |
| krag1988 A-B | Line A (tangent to the most anterior point of the canal) to line B (the posterior lamina surface) along the AP axis; in effect canal depth plus lamina thickness, not a pedicle length (krag1988 p. 28 Fig 1A; its note) | T9 20.18, T12 18.06, L5 15.00 (text means, krag1988 p. 29); the clear steps are T9/T10 about -2.4 and L4/L5 about -2 mm (read from Fig 3 p. 29, its note) |
| masharawi2021 PL, arockiaraj2025 PL | Short anatomical pedicle lengths (masharawi2021 p. 3 Fig 1; arockiaraj2025 p. 313 Fig 2) | defined differently from the chords; not comparable |

Mask recipe (Inference): cast a ray (O5) along recipe P's axis from the first bone voxel behind the pedicle to the last anterior body voxel; that is the 0-deg chord. Radiograph: on a lateral film, CL0 is about 1.32 x the mid-body AP depth and CL15 about 1.60 x (krag1988 p. 29), with about +/-3 to 4 mm of scatter and no magnification correction in the paper (krag1988 note). Separates: T12/L1 in zindrick1987 and tan2004; hou1993's length LI steps 1.5 SD at T12/L1 (hou1993 note). L4/L5: olsewski1990 about -1.0 SD in each sex (men 50.4 to 46.2, women 45.9 to 42.3 mm); zindrick1987 Dma 40.7 to 33.7, -1.4 SD; arockiaraj2025 PL -2.25 mm, about 1.8 SD; krag1988's CL0 is shortest at L5 (36.0) (their notes). zindrick1987's Dpa minus Dma tracks the transverse angle, 17.3 mm at L5, about 0 at T11 and -4.6 at T12 (Inference in its note, from Table 5 p. 165); use it as a consistency check on a measured angle. Covariates: women 2.5 to 4.5 mm shorter in cadavers and 3.6 to 6.3 mm on CT (olsewski1990 p. 544, p. 545).

### 7.6 Cortical wall, entry zones and safe zones (no generator key)

- Wall thickness at the lumbar isthmus, L1 to L5: medial 0.8, 0.8, 0.8, 1.3, 1.3 mm; lateral 0.6, 0.7, 0.9, 1.1, 1.7; cranial 3.1, 3.5, 3.9, 3.2, 4.0; caudal 2.6, 3.2, 2.8, 2.5, 2.9 (otsuki2021 p. 6 Table 2, micro-CT of 60 cadaver pedicles). Its note warns these include porous shell bone, not strictly cortex. mitra2002 gives lateral 0.55 to 1.25 and medial 1.07 to 1.37 mm (mitra2002 p. 455 Table 2). A mask cannot give a wall thickness; it needs the CT intensities. Inference: the thin lateral and medial walls are why an outer-cortex mask width and an endosteal width differ by about 1.5 to 3 mm (makino2012 TPW against the outer widths in 7.1).
- Radiographic ring: the densest image lies 1 to 3 mm inside the outer cortex; at S1 the medial line of the ring is trabecular bone, not cortex (robertson2000 p. 711, pp. 712 to 714).
- Entry point: the pedicle centre lies at the upper edge of the transverse process at T9 to T11 and at its middle at L3 to L5, moving laterally down the column; at L5 it lies 4.9 mm lateral to the facet (hou1993 p. 1852, p. 1854 Fig 6). mitra2002 places it at the middle of the transverse process, lateral to the facet at L5 (mitra2002 p. 457 Fig 3).
- Safe zones and nerve distances: lien2007 gives safe-zone widths and heights and the pedicle-to-root and pedicle-to-dura distances at T11 to L5 (lien2007 p. 1218 Table 1, p. 1219 Table 4); the transverse root angle falls from 70.6 to 75.2 deg at T11 to 28.6 to 29.0 at L5 (lien2007 p. 1218 Table 3). Safe-zone width (medial pedicle wall to lateral body wall, side means) T11 7.4, T12 8.35, L1 8.4, L2 9.9, L3 10.15, L4 12.5, L5 17.7 mm, 0.1 to 2.7 mm above the pedicle width, most at L1-L2; safe-zone height exceeds the pedicle height by 0.75 to 2.55 mm from T11 to L5 (Inference in its note, from Table 1 p. 1218). At T1 to T10 the measured safe zone was smaller than the pedicle, so the authors set it equal to the pedicle: those columns of Table 1 copy the pedicle values and are not measurements (lien2007 p. 1216; p. 1220). The width can be read on an AP view, medial pedicle edge to lateral body edge, which the authors call practicable in fluoroscopy-guided surgery (lien2007 p. 1220). A mask should record the raw value, without the T1 to T10 rule (lien2007 note).
- Pedicle index on the AP film, men, L1 to L5: 173.1, 175.6, 190.0, 207.7, 234.6, the product of ring width and height (amonookuofi1982 p. 230 Table 3); 290 Nigerian patients, film at 100 cm, not corrected. Its note finds adjacent separations of 0.07 to 0.64 SD in men (the women's reach 0.78), a weak cue.

## 8. The facets

Panjabi's facet paper is the generator's only source for every facet key, and its twelve spines carry no sex, size or ethnicity split (panjabi1993f p. 1299). Two other papers measure lumbar facets on living CT by different definitions (masharawi2021, yadav2020); no paper in the set measured a facet on a mask.

Recipe J, one facet of instance k (Inference, from panjabi1993f note, frame section, and O4):

1. Build frame F for instance k (section 2.2).
2. Superior facet on the left: the boundary voxels of label 45 of instance k that lie within 3 mm of label 47 of instance k-1. On the right, labels 46 and 48. Inferior facet: labels 47 or 48 of k within 3 mm of 45 or 46 of k+1. The C2 superior facets need C1 in the segmentation; the L5 inferior facets need the sacrum (label 26) (panjabi1993f note).
3. If the two instances touch, because the mask bridges the 1 to 2 mm joint gap (panjabi1993f note, generator section), take the voxels of k that face k-1 across the interface.
4. Fit a plane by PCA to the patch; its normal n is the least-variance axis. Orient n so that n_y > 0 and n_z < 0, up and back, for every facet, superior and inferior, as Panjabi's card normals point (panjabi1993f note, card angles).
5. Let v be frame Y projected onto the plane and normalised (the facet's own "up"), and u = n x v (its in-plane horizontal). Every in-plane extent below is taken along u or v.
6. Store the centroid, n, the patch's point count and whether step 3 was used.

### 8.1 Facet width and height: facet_w_sup, facet_w_inf (FCW), facet_h_sup, facet_h_inf (FCH)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1993f | In-plane dimensions of the facet seen along its normal; width across it, height along it, as drawn; computed by software as major and minor dimensions, though the ratio exceeds 1 at C5 to T1 (panjabi1993f p. 1299 Fig 1, p. 1301 Table 2) | SAME; the generator |
| schwingcheck mnemonics | The facet's "transverse extent" and "craniocaudal extent" (schwingcheck/mnemonics.py) | DIFFERS from its own source: an extent along the vertebra's axes is foreshortened by about sin T; FCH reads low by up to 30% at C3-C6 (panjabi1993f note, generator section; Inference: sin 45 deg = 0.71) |
| masharawi2021 FW | Length of the facet joint line on an axial CT slice, anteromedial to posterolateral end; which joint a vertebra's value belongs to is not stated (masharawi2021 p. 3 Fig 1) | DIFFERS: a joint-line chord in one axial slice, not a facet's in-plane width; for the near-vertical lumbar facets it approximates the width (Inference) |

Biases (Inference): a scalar extent of the whole articular process (labels 45 to 48), not of the articular patch, measures the process, not the facet. Partial volume: a 10 to 16 mm facet is 10 to 16 voxels at 1 mm, so widths carry about one voxel of error (panjabi1993f note, generator section).

(b) Mask recipe: recipe J; width = extent of the patch along u, height = extent along v. Report each side; the pool keys are the side means facet_w_sup:mean, facet_w_inf:mean, facet_h_sup:mean and facet_h_inf:mean. Store also the ratio FCW/FCH.

(c) Radiograph: width is not readable; on a lateral view of the neck and thorax the joint is seen nearly edge-on and the length of the joint line approximates FCH, divided by 1.23 (panjabi1993f note; eisenstein1977 p. 175); in the lumbar spine the joint is oblique to a lateral beam and FCH cannot be read (panjabi1993f note).

(d) Course, side means, mm

| Level | FCW sup | FCW inf | FCH sup | FCH inf |
|---|---|---|---|---|
| C2 | 16.4 | 10.9 | 17.9 | 12.4 |
| C3 | 11.1 | 11.3 | 11.6 | 12.4 |
| C4 | 11.5 | 11.6 | 12.2 | 12.2 |
| C5 | 12.1 | 11.8 | 11.6 | 11.2 |
| C6 | 12.4 | 12.9 | 10.9 | 12.2 |
| C7 | 12.6 | 13.2 | 11.4 | 12.7 |
| T1 | 13.7 | 12.6 | 12.6 | 12.9 |
| T2 | 11.9 | 11.1 | 12.6 | 11.5 |
| T3 | 10.7 | 10.2 | 11.2 | 10.8 |
| T4 | 10.4 | 10.1 | 11.2 | 11.0 |
| T5 | 10.2 | 9.7 | 11.5 | 11.1 |
| T6 | 9.8 | 9.6 | 11.8 | 10.7 |
| T7 | 9.8 | 10.1 | 11.4 | 10.8 |
| T8 | 10.2 | 10.6 | 11.6 | 11.2 |
| T9 | 10.8 | 12.2 | 11.9 | 12.4 |
| T10 | 12.2 | 11.7 | 12.2 | 12.1 |
| T11 | 11.4 | 11.2 | 12.2 | 12.9 |
| T12 | 10.8 | 9.7 | 12.9 | 12.6 |
| L1 | 10.3 | 11.6 | 12.4 | 15.5 |
| L2 | 11.2 | 12.7 | 14.6 | 16.1 |
| L3 | 13.9 | 13.6 | 15.9 | 16.0 |
| L4 | 14.7 | 14.4 | 16.7 | 15.9 |
| L5 | 15.6 | 15.9 | 17.4 | 17.9 |

(panjabi1993f p. 1301 Tables 2 and 3, side means from the long table, Inference.)

masharawi2021 FW, control men, left, L1 to L5: 16.72, 16.93, 18.45, 18.16, 19.45 mm; women 15.03, 15.50, 16.02, 16.73, 17.71 (masharawi2021 p. 6 Table 2; 25 men and 25 women aged 50 to 80, living CT). It runs 2 to 6 mm above Panjabi's lumbar widths (Inference: 16.72 - 10.3 at L1 superior, 19.45 - 15.9 at L5 inferior). The cause is not known: the definitions differ, and a joint line in an axial slice of a curved lumbar joint is longer than a flat facet's chord (Inference).

Where it peaks and separates (Inference from the long table):

- C2's superior facet is the largest in width and height (16.4, 17.9), and C2/C3 is the only cervical separation (width -3.06 SD, height -2.69 SD). C2's inferior facet is the size of the lower cervical ones (panjabi1993f p. 1301).
- T3 to T8 are the smallest and nearly uniform (panjabi1993f p. 1307); no thoracic pair separates by width or height (0.0 to 0.98 SD).
- T12/L1: the inferior height jumps +2.9 mm (1.34 SD) and the inferior width +1.9 (0.88 SD). The right inferior width of T12, 9.5 mm, is the smallest of the column (panjabi1993f p. 1301 Table 3).
- L1/L2: the superior height jumps +2.2 mm (1.08 SD). By size, the lumbar-type joint starts at L1-L2; by orientation it starts at T12-L1 (panjabi1993f note, Inference from Tables 2, 3, 6 and 7).
- L2 to L5: widths and superior heights rising, the inferior height flat to L4 (16.2, 16.1, 15.9) and up at L5 (17.9); steps under 0.95 SD; FCW/FCH is lowest at L1-L2 (inferior left L1 0.68, superior right L2 0.76; panjabi1993f p. 1301).

(e) Covariates: none in Panjabi, 8 men and 4 women pooled (panjabi1993f p. 1299). masharawi2021: men wider at left L1 to L3 and right L1 and L3, by 1.4 to 2.4 mm; women with degenerative spondylolisthesis wider at right L4 and at L5 (masharawi2021 p. 6 Table 2, its note).

### 8.2 Facet area: facet_area_sup, facet_area_inf (FCA)

(a) Definitions

- panjabi1993f: the facet outline projected onto the three anatomic planes; the area is the root-sum-square of the three projected areas (panjabi1993f p. 1299). The generator. For a flat facet that is its true area; for a curved one it is the area of its flat shadow along the mean normal (panjabi1993f note).
- The ellipse pi x FCW x FCH / 4 was offered as an approximation that slightly overestimates (panjabi1993f p. 1303, p. 1309). Inference in its note, over 92 cells: it exceeds the measured area at 90 of them, by a median of about 17%, up to 46%, and falls short only at superior L2.
- No other paper in the set measured a facet area.

Bias (Inference): the scalar area of a meshed curved lumbar facet exceeds the vector area (panjabi1993f note, generator section).

(b) Mask recipe: recipe J; the vector area of the triangulated patch (O2), or the area of the patch's outline projected onto its fitted plane. Never the scalar mesh area.

(c) Radiograph: not measurable from one projection (panjabi1993f note). The ellipse from a film's width and height is not available either, since width is not readable (8.1).

(d) Course, side means, mm2: superior C2 208.2; C3 to T12 75.2 to 108.8 (T1 108.8 a local peak); L1 98.0, L2 143.1, L3 167.4, L4 184.7, L5 205.5. Inferior C2 89.8; C3 to T12 71.6 to 104.4; L1 126.9, L2 152.2, L3 163.9, L4 175.0, L5 190.0 (panjabi1993f p. 1302 Table 4).

- Separations: superior C2/C3 -3.50 SD; superior C7/T1 +1.02; superior L1/L2 +1.25; inferior T8/T9 +1.00; inferior T12/L1 +1.37. Everything else under 0.9 SD.
- The superior lumbar rise comes at L2 and the inferior at L1, so the T12-L1 joint is small on both sides and the jump is at the L1-L2 joint (panjabi1993f p. 1302 to 1303, its note).
- Noise: SEMs 2.0 to 21.8 mm2; the cervical areas have coefficients of variation of about 35 to 73% (panjabi1993f note).

(e) Covariates: none (panjabi1993f p. 1299). Inference: an area scales with the square of size, as the generator assumes.

### 8.3 Interfacet widths and height: interfacet_w_sup, interfacet_w_inf (IFWs, IFWi), interfacet_h (IFH)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1993f | IFW: distance between the centroids of the two superior (or two inferior) facets; IFH: distance between the superior and inferior facets of one side; whether full 3D distances or their X and Y components is not stated (panjabi1993f p. 1300, pp. 1303 to 1304) | SAME; the generator. The two readings should agree within about a millimetre for IFW; for lumbar IFH the centroids also differ in Z (panjabi1993f note) |
| masharawi2021 SIFW, IIFW | Distance between the anteromedial (SIFW) or the posterolateral (IIFW) ends of the left and right joint lines on an axial slice (masharawi2021 p. 3 Fig 1) | DIFFERS: two ends of the joint, not its centre |
| yadav2020 IFD | Between the anteromedial points of the facet joints across the back of the canal (yadav2020 p. 176 Fig 1D) | DIFFERS; section 6.4 |
| schwingcheck mnemonics | IFWs centre to centre; IFH centre of superior to centre of inferior facet of one side (schwingcheck/mnemonics.py) | SAME |

Inference, a bridge between the two: the midpoint of masharawi2021's two ends, (SIFW + IIFW) / 2, in control men at L1 to L5 is 24.0, 23.8, 24.5, 27.2 and 35.7 mm (from 16.12 and 31.92, 16.58 and 31.08, 15.56 and 33.51, 17.13 and 37.19, 22.74 and 48.56; masharawi2021 p. 6 Table 2). Panjabi's IFWs is 26.2, 26.4, 28.6, 31.4 and 35.0 (panjabi1993f p. 1302 Table 5). They agree within 2.2 to 4.2 mm at L1 to L4 and 0.7 mm at L5; the joint-line midpoint is not the facet centroid, so do not expect equality.

(b) Mask recipe

1. Run recipe J on all four facets of instance k; it needs both neighbours segmented.
2. interfacet_w_sup = the distance between the left and right superior centroids; interfacet_w_inf the same for the inferior. Store the X components too.
3. interfacet_h on each side = the distance between that side's superior and inferior centroids; the pool key is the side mean, interfacet_h:mean. Store the Y components too.
4. Check congruence between neighbours (Inference, panjabi1993f note): IFWi of level k should match IFWs of level k+1 within 0.6 mm from the C2-C3 joint to the T10-T11 joint, within 2.5 mm from T11-T12 to L3-L4, and within 0.2 mm at L4-L5. A larger miss flags a mis-fitted facet.

(c) Radiograph

AP view: the X separation of the facet centres is IFW times the magnification; divide by 1.14 (panjabi1993f note; eisenstein1977 p. 175). IFH on an AP view along each facet column, or on a lateral view where both sides superimpose. The ratio IFW/IFH needs only an AP view and is magnification-free: the most usable facet number for fluoroscopy (panjabi1993f note). Ratio course: C2 1.64, C3 2.93, C4 2.38, C5 3.04, C6 2.88, C7 2.09, T1 1.68, T2 1.25, about 0.79 to 0.98 from T5 to L3 (lowest at L1, 0.79), L4 1.16, L5 1.44 (panjabi1993f p. 1304, p. 1302 Table 5). By the paper's own cervical rule (IFW/IFH above 1.5), T1 would be called cervical; the threshold falls between T1 and T2 (panjabi1993f note). Fawcett's lower lumbar frontal shapes, tall at L3, square at L4, wide at L5, fit those ratios (panjabi1993f p. 1308). IFWs/IFWi: 0.84 at C2, 1.15 at C7, 1.18 at T1, 0.93 at T9, 1.06 at L1 and 0.86 at L5 (panjabi1993f p. 1304, p. 1302 Table 5); a few millimetres at 20 to 30 mm widths, near what a film resolves (panjabi1993f note).

(d) Course, mm

| Level | IFWs | IFWi | IFH (side mean) |
|---|---|---|---|
| C2 | 30.3 | 35.9 | 20.1 |
| C3 | 35.9 | 37.8 | 12.6 |
| C4 | 37.6 | 38.0 | 15.9 |
| C5 | 38.3 | 40.5 | 13.0 |
| C6 | 39.9 | 38.8 | 13.7 |
| C7 | 38.6 | 33.6 | 17.3 |
| T1 | 33.2 | 28.2 | 18.3 |
| T2 | 28.2 | 24.3 | 21.0 |
| T3 | 24.6 | 22.3 | 21.3 |
| T4 | 22.1 | 21.1 | 20.5 |
| T5 | 20.8 | 20.8 | 21.1 |
| T6 | 20.9 | 21.4 | 21.9 |
| T7 | 21.0 | 22.3 | 23.8 |
| T8 | 21.8 | 23.4 | 24.6 |
| T9 | 23.0 | 24.6 | 25.8 |
| T10 | 24.2 | 24.6 | 26.0 |
| T11 | 25.2 | 24.6 | 29.9 |
| T12 | 25.9 | 24.9 | 31.4 |
| L1 | 26.2 | 24.8 | 32.1 |
| L2 | 26.4 | 26.6 | 32.7 |
| L3 | 28.6 | 29.1 | 32.0 |
| L4 | 31.4 | 34.8 | 28.4 |
| L5 | 35.0 | 40.6 | 26.2 |

(panjabi1993f p. 1302 Table 5.)

masharawi2021, control men, L1 to L5: SIFW 16.12, 16.58, 15.56, 17.13, 22.74; IIFW 31.92, 31.08, 33.51, 37.19, 48.56 mm (masharawi2021 p. 6 Table 2). Both are flat at L1 to L3 and step at L4/L5: +5.6 mm SIFW (about 1.1 to 1.5 pooled SD) and +10 to 11 mm IIFW (about 1.4 to 1.6 SD), the paper's strongest L4/L5 step (masharawi2021 note).

Where it separates (Inference from the long table):

- Cervicothoracic: the strongest facet signal of the column. IFWs falls C7/T1 -1.73, T1/T2 -1.92 and T2/T3 -1.73 SD; IFWi falls C6/C7 -1.88, C7/T1 -2.23 and T1/T2 -1.88 SD. The minimum is T5, 20.8 for both (panjabi1993f p. 1304).
- C2/C3: IFWs +2.69 SD; IFH -3.35 SD.
- IFH: C6/C7 +1.26, T1/T2 +1.18, T10/T11 +1.36 and L3/L4 -1.07 SD; peak at L2 (32.7). C4's IFH (15.9 with SD about 12 mm) is an outlier, probably one aberrant spine (panjabi1993f note); do not trust its spread.
- Lumbar: IFWi L3/L4 +1.03 SD; IFWs steps are 0.08 (L1/L2) and 0.56 to 0.67 SD (L2/L3 to L4/L5). No interfacet measure separates T12/L1 (0.05 to 0.22 SD).

(e) Covariates: none in Panjabi (panjabi1993f p. 1299). masharawi2021: men wider at L1, L2 and L5 (SIFW) and at L1 and L2 (IIFW); degenerative spondylolisthesis widens SIFW at L3 and L4 (masharawi2021 p. 6 Table 2, its note). Ratios should not scale with size (Inference).

### 8.4 Facet orientation: facet_trans_sup, facet_trans_inf (T), facet_sag_sup, facet_sag_inf (S), facet_card_x_sup, facet_card_x_inf, facet_card_y_sup, facet_card_y_inf (CAX, CAY)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1993f T | Angle between the facet's best-fit plane and the vertebra's transverse plane; all values positive (panjabi1993f p. 1300 Fig 2A, p. 1303 Tables 6 and 7) | SAME; the generator. Inference: T = arccos(abs(n_y)) (panjabi1993f note) |
| panjabi1993f S | Angle to the vertebra's sagittal plane, left positive and right negative, on a 0 to 180 scale (panjabi1993f p. 1300, p. 1303) | SAME; the generator holds the mirrored mean. Inference from Tables 6 to 8: the printed magnitude is arccos(n_lat) from the C4-C5 joint down and 180 minus that above it, n_lat being the normal's component toward the facet's own side (panjabi1993f note) |
| panjabi1993f CAX, CAY | Rotations of a card from the transverse plane, first about X, then about Y, into the facet plane; computed from the mean planar angles, no SEM (panjabi1993f p. 1300 Fig 2B, p. 1304 Table 8, pp. 1304 to 1305) | SAME. Inference: CAX = -T exactly in 87 of 92 cells and within 0.1 deg in 91; the one exception, superior left T1, is a misprint in CAX (panjabi1993f note, CAX); and abs(cos S) = sin T x abs(sin CAY) at 89 of 92; the sign of CAY alone carries something new, the facet's lateral or medial facing (panjabi1993f note) |
| masharawi2021 TFA | Angle on an axial CT slice between one facet joint line and the midsagittal line drawn from a midline apex in the body to the spinous tip; smaller is more sagittal (masharawi2021 p. 3 Fig 1) | DIFFERS: a joint-line trace in one slice, against an image midline; compare with the acute S |
| masharawi2021 TIFA | Angle between the left and right joint lines (masharawi2021 p. 3 Fig 1) | DIFFERS; Inference: within 0.6 to 5.5 deg of the sum of the two TFAs at L1 to L4, 14 to 20 deg less at L5 (masharawi2021 note) |

Biases (Inference unless cited):

- Frame: Panjabi's angles are to the vertebra's own posterior-wall frame. Angles from scanner axes or from a principal-axes frame of the whole instance tilt T and S by the vertebra's sagittal and axial rotation (panjabi1993f note, generator section).
- Curvature: a plane fitted to the convex and to the concave side of one curved joint differ, so the inferior L4 and superior L5 means differ (70.5 and 80.3 against 86.0 and 85.1 for T; panjabi1993f note). Do not demand exact congruence across a joint.
- The S branch: the generator draws S on Panjabi's 0 to 180 scale; a mask extractor computes the same number only once it knows whether the level lies above the C4-C5 joint. Score in the frame below.
- Axial-slice traces: an axial CT trace of the joint falls short of the true acute angle to the sagittal plane by 0.1 to 1.8 deg in the lumbar and thoracic spine (lumbar superior 0.1 to 0.6, lumbar inferior 0.8 to 1.3, thoracic superior 0.3 to 1.4, thoracic inferior 0.3 to 1.8), 1.5 to 6.3 deg at C3 to C7, and 15 to 21 deg at C2 (panjabi1993f note, computed from Tables 6 and 7).

(b) Mask recipe

1. Recipe J; take the unit normal n, oriented up and back, in frame F.
2. T = arccos(abs(n_y)).
3. Acute S = arccos(abs(n_x)). Facing: lateral when n_x points toward the facet's own side (n_x < 0 on the right, > 0 on the left, +X being left), medial otherwise (panjabi1993f note).
4. The generator's number: s = arccos(n_lat), with n_lat = n_x on the left and -n_x on the right. For a level hypothesis at or below the C4-C5 joint compare s with the generator's mirrored mean; for C2, C3 and C4 superior and C2 and C3 inferior facets compare 180 - s (panjabi1993f note). The likelihood is evaluated per hypothesised level anyway, so apply the branch there, not in the extractor.
5. Cards: CAX = -arccos(n_y); CAY = atan2(-n_x, -n_z) (panjabi1993f note). Store them, but enter no card magnitude as a feature: they repeat T and S. Enter the sign of CAY, or the facing of step 3, as a categorical feature.
6. Store n itself; every angle derives from it (panjabi1993f pp. 1306 to 1307, where the authors name direction cosines as the alternative they did not choose).

(c) Radiograph

- T: on a lateral view the joint line gives T accurately only where S is near 90 deg, the neck and thorax (panjabi1993f p. 1309). Measure it against the perpendicular to the posterior body line, not the image horizontal. Inference, by projection: the lateral-view angle, arccos(cos T / sin S'), with S' the acute S, is within 2 deg of T from C3 to T12 and about 10 deg low at C2's superior facet (panjabi1993f note). In the lumbar spine no sharp joint line shows on a lateral view (panjabi1993f note).
- S: an axial CT slice gives S accurately only where T is near 90 deg, the lumbar spine (panjabi1993f p. 1309). Not from a plain AP or lateral film. Inference, general radiographic knowledge in the note, not the paper: on an AP view the sagittal upper lumbar joints show end-on as joint spaces and the more coronal lower ones do not (panjabi1993f note).
- Cards: not directly.

(d) Course, deg

| Level | T sup | T inf | S sup, printed (mirrored mean) | S sup, acute | S inf, printed | S inf, acute |
|---|---|---|---|---|---|---|
| C2 | 37.1 | 33.8 | 116.3 | 63.7 | 72.5 | 72.5 |
| C3 | 52.0 | 42.6 | 74.2 | 74.2 | 77.3 | 77.3 |
| C4 | 48.4 | 46.3 | 84.6 | 84.6 | 74.7 | 74.7 |
| C5 | 45.5 | 51.7 | 83.6 | 83.6 | 73.5 | 73.5 |
| C6 | 47.6 | 54.9 | 79.0 | 79.0 | 82.3 | 82.3 |
| C7 | 55.5 | 49.5 | 82.8 | 82.8 | 81.2 | 81.2 |
| T1 | 60.0 | 64.2 | 85.8 | 85.8 | 75.5 | 75.5 |
| T2 | 66.5 | 69.8 | 75.0 | 75.0 | 76.2 | 76.2 |
| T3 to T8 | 69.4 to 74.0 | 73.6 to 77.3 | 72.7 to 75.9 | same | 72.9 to 75.0 | same |
| T9 | 78.0 | 77.7 | 73.7 | 73.7 | 75.6 | 75.6 |
| T10 | 78.1 | 77.3 | 75.1 | 75.1 | 75.4 | 75.4 |
| T11 | 75.8 | 75.8 | 74.3 | 74.3 | 71.3 | 71.3 |
| T12 | 77.7 | 76.9 | 70.0 | 70.0 | 139.2 | 40.8 |
| L1 | 82.1 | 81.6 | 136.6 | 43.4 | 153.4 | 26.6 |
| L2 | 84.8 | 80.8 | 137.6 | 42.4 | 139.6 | 40.4 |
| L3 | 83.0 | 76.7 | 132.3 | 47.7 | 126.9 | 53.1 |
| L4 | 81.2 | 75.4 | 122.2 | 57.8 | 113.7 | 66.3 |
| L5 | 85.5 | 76.3 | 118.7 | 61.3 | 126.3 | 53.7 |

(panjabi1993f p. 1303 Tables 6 and 7, side means from the long table, with S mirrored as (left - right) / 2; acute S = min(S, 180 - S); Inference for the derived columns.)

masharawi2021 TFA, control men, left, L1 to L5: 33.10, 29.13, 31.58, 37.70, 46.58 deg; right 31.38, 29.71, 33.08, 36.22, 44.17 (masharawi2021 p. 6 Table 2). The two sources disagree: masharawi2021's living CT traces run about 10 to 22 deg below Panjabi's acute superior S (43.4, 42.4, 47.7, 57.8, 61.3): left 10.3, 13.3, 16.1, 20.1, 14.7 and right 12.0, 12.7, 14.6, 21.6, 17.1 at L1 to L5 (Inference by subtraction; the masharawi2021 note gives 8 to 22) and between Panjabi's superior and inferior acute values only at L1 (26.6 to 43.4); at L2 they lie below both (40.4 and 42.4). The joint a vertebra's value belongs to is not stated in masharawi2021 (its note), and the definitions differ (above); do not pool them.

Where it separates (Inference from the long table, steps over the mean SD):

- T12/L1 for superior S (+66.7 deg, 2.78 SD) and T11/T12 for inferior S (+67.9, 2.77 SD): the thoracolumbar switch, at the inferior facets of T12 and the superior facets of L1 (panjabi1993f p. 1304). T12 is identified by the abrupt change of S and CAY between its own superior and inferior facets (panjabi1993f p. 1307). Inference in its note: the switch may fall one joint off in some spines; the T11-T12 and T12-L1 SEMs are 4.7 to 9.5 deg. Use it as a feature with its own level uncertainty, never as the T12 label alone (panjabi1993f note, generator section).
- C2/C3: superior S -3.52 SD (116 to 74) and superior T +1.31 SD; CAY changes sign (panjabi1993f p. 1305).
- C3/C4: superior S +1.01 SD; and the superior CAY changes sign again between C4 and C5, making C2, C3-C4 and C5-C7 three cervical subregions (panjabi1993f p. 1305, p. 1307).
- T1/T2: superior S -2.10 SD. C7/T1: inferior T +1.27 SD.
- T8/T9: superior T +1.15 SD. Otherwise T rises gradually from about 35 deg at C2 to about 75 at T4 and about 80 in the lumbar spine (panjabi1993f p. 1304).
- Lumbar: superior S falls from L2 to L5 (acute 42.4 to 61.3 deg; L1 43.4); inferior S falls from L1 to L4 and rises at L5 (+12.7 deg); adjacent steps 0.03 to 0.71 SD on spreads of 10 to 32 deg; weak for telling one lumbar level from the next (panjabi1993f note). masharawi2021's TFA likewise rises 12 to 17 deg from L2 to L5 with SDs of 7 to 13 deg (masharawi2021 note).
- Cards: superior CAX runs almost linearly from about -41 at C2 to -86 at L5 (panjabi1993f p. 1305); superior right CAY is +38.9 at C2, -17.6 at C3, -8.4 at C4, +9.2 at C5, about +16 through the thorax with a dip at T1 (+4.1), +18.0 at T12, -50.5 at L1 and -27.7 at L5 (panjabi1993f p. 1304 Table 8, p. 1306). By the facing reading, superior facets face laterally at C2 and C5 to T12 and medially at C3 to C4 and L1 to L5 (panjabi1993f note). Inference: the facing is a categorical feature with three switches, C2/C3, C4/C5 and T12/L1; near-sagittal normals at C4, C5, left C7 and T1 tilt only 4 to 7 deg, so expect errors there (panjabi1993f note).

(e) Covariates: none in Panjabi (panjabi1993f p. 1299). masharawi2021: no sex difference in TFA; women with degenerative spondylolisthesis are more sagittal at left L4 (33.25 against 41.25 deg) and right L1 and L4 (masharawi2021 p. 6 Table 2). Arthrosis: Pathria grade 3 in controls is highest at L5-S1 in every group, 57.7 to 66.7% (masharawi2021 p. 8 Table 3); a degenerate joint's surface is a worse plane (Inference).

### 8.5 Tropism (no generator key)

- Panjabi prints right and left means but never compares them per spine and assumes mirror symmetry for the cards (panjabi1993f p. 1300; its note, gaps). The largest right-left gaps of the means are inferior T at L5 (71.0 against 81.6 deg) and L4 (70.5 against 80.3), superior T at C7 (59.4 against 51.6) and C2 (40.7 against 33.5), and inferior S at L3 (130.6 against 123.3) (panjabi1993f p. 1303 Tables 6 and 7). A gap of means is not a per-person tropism.
- masharawi2021's left and right TFA means in control men differ by 0.6 to 2.4 deg (Inference: 33.10 - 31.38, 29.71 - 29.13, 33.08 - 31.58, 37.70 - 36.22, 46.58 - 44.17; masharawi2021 p. 6 Table 2). No per-person difference is reported.
- The set holds no per-person tropism rate or distribution. Mask recipe (Inference): store abs(acute S left - acute S right) per joint; give it no prior.

### 8.6 Uncovertebral joints: uncovertebral_area_upper, uncovertebral_area_lower (UJA), uncovertebral_incl_frontal_upper, uncovertebral_incl_sag_upper, uncovertebral_incl_frontal_lower, uncovertebral_incl_sag_lower (UJI)

These six keys are not in the pool, since they are printed at C2 or C3 to C7 only (schwingcheck/measures.py, left_out).

(a) Definitions: panjabi1991c only. UJA: area of the uncovertebral articulating surfaces, upper and lower, up to 20 points each (panjabi1991c p. 861, p. 866); Inference for which surface each name means, upper on the uncinate process and lower on the inferolateral body margin, following from C2 having only a lower surface (panjabi1991c note, UJA). UJI: angles of each surface's least-squares plane to the frontal and sagittal planes; one value per level, sides combined in a way not stated; values above 90 deg mean an oriented angle from an undefined reference direction (panjabi1991c p. 862, p. 867 Fig 6).

(b) Mask recipe (Inference, panjabi1991c note): the upper surface is the patch of instance k's body surface (label 49 or 52) on the uncinate process within 3 mm of instance k-1; the lower is the patch on the inferolateral body of k within 3 mm of the uncus of k+1. Vector area by O2; plane by PCA; the angles of the plane to frame F's XY and YZ planes. Which branch above 90 deg is not defined in the paper; record the normal and compare magnitudes with care.

(c) Radiograph: UJIs is the slope of the uncinate process on an AP view (Inference, panjabi1991c note); UJIf needs an axial image; areas are not readable.

(d) Course: UJA upper 37.0 to 58.1 mm2 (C3 to C7), lower 17.7 to 30.5 (C2 to C7), no significant trend; the upper averages 44.2 against 23.4 for the lower (panjabi1991c p. 865 Table 6, p. 866). UJI frontal, upper: 76.6, 76.2, 82.7, 104.0, 115.6 deg at C3 to C7; lower: 78.4, 81.6, 83.5, 84.9, 106.2, 113.4 at C2 to C7. It passes 90 deg between C5 and C6 on both surfaces, and the upper C7 differs from C6 (panjabi1991c p. 865 Table 6, p. 866). UJI sagittal: upper 38.7 to 47.3, lower 45.0 to 63.7, relatively constant (panjabi1991c p. 866). Separates C5/C6 and C6/C7 by the frontal angle.

(e) Covariates: none, sexes pooled (panjabi1991c p. 863).

## 9. Laminae and processes

SPINEPS gives the spinous process (label 42) and the two transverse, or costal, processes (labels 43 and 44) labels of their own, but the laminae lie inside label 41 with the pedicles and the process bases (section 2.3). Panjabi measured three things here: the spinous process length, the transverse process width and the pars area (panjabi1991c p. 866; panjabi1991t p. 893; panjabi1992 p. 302). The laminae themselves were measured by one paper only (abbas2021).

### 9.1 Spinous process length: spinous_length (SPL)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1992 | From the centre of the superior end plate, the frame's origin, to the most inferoposterior tip of the spinous process (panjabi1992 p. 302, read on the page image; p. 300 Fig 1) | SAME; the generator's lumbar rows. It is the reach of the whole vertebra from its upper end-plate centre, not the free process (panjabi1992 note) |
| panjabi1991t | From the centroid of the superior end plate to the most inferoposterior tip (panjabi1991t p. 893; p. 891 Fig 3B) | SAME; the thoracic rows |
| panjabi1991c | The text starts it at the vertebral body centroid; Fig 1 draws it to about the upper end-plate centre (panjabi1991c p. 866, p. 862) | SAME in intent; the two start points lie about half a body height apart (panjabi1991c note) |
| tan2004 | Not defined in the text; Fig 1c draws it from the upper end-plate centroid (tan2004 p. 138) | SAME by the drawing; thoracic values within 2% of Panjabi on average, lumbar 22.8% below, 25.9% at L5 (tan2004 p. 144; tan2004 note, computed) |
| busscher2010 | Along the process's own axis in the midline, from the tip to where that axis meets a reference line through the posterior arch (busscher2010 p. 1105 Fig 1); the authors say Panjabi measured to the middle of the body instead (busscher2010 p. 1112) | DIFFERS: the free process. Lumbar values 32.0 to 37.8 mm against Panjabi's 67.7 to 71.7 |
| bonczar2024 | Drawn in an axial view from the tip to the base at the laminae (bonczar2024 p. 4 Fig 2) | Unclear: the drawing says free process, but values near 60 mm fit a more anterior start (bonczar2024 note) |
| gilad1985 e, f | From the posterosuperior (e) or posteroinferior (f) body corner to the most posterior point of the spinous process, lateral film corrected to the midsagittal plane (gilad1985 p. 117; p. 116 Fig 1) | DIFFERS: starts at the posterior wall |
| schwingcheck mnemonics.py | From the canal's posterior wall "to the tip of the process" (schwingcheck/mnemonics.py); measures.py repeats that Panjabi starts at the canal's posterior wall (schwingcheck/measures.py, comment above SPINEPS_MAP) | DIFFERS from all three source papers. A mask value taken by this text would read roughly half the table (panjabi1992 note) |
| archive measurer | Centroid of label 49 to the farthest voxel of label 42 (archive/bordercall/spineps_map.py, measure_vertebra) | Close to the cervical text; in the thorax and lumbar spine it starts about half a posterior body height caudal to Panjabi's start |

Biases a mask value carries (Inference unless cited):

- The start point. A start at the body centroid lies about half the posterior body height caudal to the upper end-plate centre, 11.5 to 12.2 mm at L1 to L5 (half of panjabi1992 p. 301 Table 2's VBHp). The length changes by less than that; how much depends on the height of the tip, which no paper reports. Use the end-plate centre.
- The free process. busscher2010's lumbar lengths run 30 to 40 mm below Panjabi's (from the tables above; different samples, 6 Dutch men against 12 autopsy spines), which is the size of the error mnemonics.py's text would put into a mask value.
- Bifid tips. C2 to C6 spinous processes are often bifid; take the farthest point of either limb (panjabi1991c note; gilad1985 note). A midsagittal slice misses paramedian tips and reads short (gilad1985 note).

(b) Mask recipe

1. Build frame F (section 2.2).
2. Take the start at the centroid of the cranial end-plate surface (O1), the frame's origin (panjabi1992 p. 302; panjabi1991t p. 893).
3. Among the voxels of label 42 of the instance, take the one farthest from the start. Inference: for a process pointing back and down this is the inferoposterior tip; check that it lies at the caudal end of the process, and in the neck take either limb of a bifid tip.
4. Report the 3D distance as spinous_length.
5. Store also the angle of the start-to-tip line below the frame's transverse plane, and the free process length from the tip to the spinolaminar junction along the process axis (busscher2010's), so either convention can be compared.

(c) Radiograph

Lateral view only. Take the midpoint of the upper end-plate line and the spinous tip; both lie near the midsagittal plane (panjabi1992 note), so divide by the lateral magnification, 1.23 at 110 cm tube-film (eisenstein1977 p. 175). The C7 tip was hidden by the clavicle, humerus and ribs in about one film in ten (gilad1985 p. 117); thoracic tips overlap the ribs and scapulae (busscher2010 note). A magnification-free form is SPL over end-plate depth: Inference, from Panjabi's tables, 1.97 at C3, 2.52 at C7, 2.71 at T1, falling to 1.43 at T11 and 1.45 at T12, then 1.99 at L1 and 1.97 to 2.07 to L5 (spinous_length over endplate_depth, panjabi1991c p. 864, panjabi1991t p. 895, panjabi1992 p. 304 and the body tables of section 3.2).

(d) Course, mm

| Level | Panjabi SPL | tan2004 | busscher2010 (free process) | gilad1985 e |
|---|---|---|---|---|
| C2 | 33.7 | - | - | 40.0 |
| C3 | 29.6 | 25.6 | 13.9 | 34.4 |
| C4 | 30.3 | 30.3 | about 13.5 | 33.6 |
| C5 | 28.5 | 33.6 | 15.2 | 35.4 |
| C6 | 34.2 | 40.5 | about 22.5 | 41.5 |
| C7 | 45.7 | 46.9 | about 33 | 49.6 |
| T1 | 50.1 | 48.3 | about 35 | - |
| T2 | 52.1 | 48.3 | about 34 | - |
| T3 | 51.7 | 49.0 | hidden | - |
| T4 | 51.1 | 48.4 | about 40 | - |
| T5 | 52.1 | 49.8 | 42.1 | - |
| T6 | 53.8 | 50.7 | about 45 | - |
| T7 | 50.5 | 51.8 | about 43 | - |
| T8 | 52.8 | 51.9 | about 38 | - |
| T9 | 51.3 | 51.5 | about 33 | - |
| T10 | 49.3 | 49.8 | 29.9 | - |
| T11 | 45.6 | 48.4 | about 27 | - |
| T12 | 47.4 | 48.5 | 27.7 | - |
| L1 | 67.7 | 51.5 | 32.0 | 52.7 |
| L2 | 71.7 | 54.4 | 36.4 | 55.9 |
| L3 | 71.7 | 57.6 | 37.8 | 56.8 |
| L4 | 70.1 | 55.1 | 34.2 | 54.9 |
| L5 | 68.3 | 50.6 | about 28.5 | 51.4 |

(Panjabi: panjabi1991c p. 864 Table 5, panjabi1991t p. 895 Table 7, panjabi1992 p. 304 Table 5; tan2004 pp. 140 to 141 Table 1; busscher2010 p. 1110 Fig 6, read from the figure; gilad1985 p. 118 Table 1, 141 cervical and 157 lumbar films of healthy men aged 20 to 38.) Pooled lumbar values: 59.94, 63.37, 65.67, 63.36, 59.47 mm (bonczar2024 pp. 5 to 9).

Where it peaks, bottoms out and separates (steps over the mean SD of the two levels, from Panjabi's long table, Inference):

- C2/C3 -1.09 SD; C3 to C5 flat; C5/C6 +1.15; C6/C7 +11.5 mm, 2.44 SD, and C7 differs from C2 to C6 (panjabi1991c p. 866). Every series has the C6/C7 step: tan2004 +6.4 mm, busscher2010 about +10.5, gilad1985 e +8.1. The vertebra prominens is the one cervical level SPL names.
- C7/T1 +1.11 SD. T1 to T12: no level differs significantly (panjabi1991t p. 893); steps 0.08 to 0.98 SD. The thoracic minimum is T11 (45.6) in Panjabi. SPL fails inside the thorax.
- T12/L1: +20.3 mm, 3.99 SD in the generator. This step crosses from the thoracic paper's table to the lumbar paper's. tan2004, measuring by the same drawing, has +3.0 mm (48.5 to 51.5), and busscher2010's free process +4.3 mm. Inference: the generator's strongest T12/L1 length step rests on two papers' tables of the same 12 spines and is not reproduced by the one other series with the same definition; widen its spread at L1 or check it on CT before trusting it.
- L1 to L5: maximum at L2-L3 (panjabi1992 p. 304, tied by the authors to the lordotic apex), at L3 in tan2004, busscher2010, gilad1985 and bonczar2024; no lumbar level differs significantly (panjabi1992 p. 302). L4/L5 is -0.37 SD in Panjabi and -0.95 pooled SD for gilad1985's f (gilad1985 note). It fails to separate lumbar neighbours.
- A disagreement in the neck: gilad1985's e starts closer to the tip than Panjabi's SPL, yet runs 4 to 7 mm longer at C2 to C7 (40.0 against 33.7 at C2, 49.6 against 45.7 at C7). Populations: living men on corrected films against 12 dry spines. The cause is not known.

(e) Covariates

None in Panjabi, 8 men and 4 women pooled (panjabi1992 p. 299). tan2004's ratios to Panjabi, cervical / thoracic / lumbar: 1.05 / 0.98 / 0.77 (tan2004 note). gilad1985 is men aged 20 to 38 only (gilad1985 p. 115); busscher2010 six men of mean 182 cm (busscher2010 p. 1105). The set holds no sex, age or stature effect on spinous length. Error: busscher2010's free length ICC 0.92 intra and 0.95 inter (busscher2010 p. 1106 Table 1); gilad1985's SDs are 7.1 to 12.6% of the means (gilad1985 note).

### 9.2 Transverse process width: transverse_width (TPW)

(a) Definitions

| Paper | Definition | Against the generator |
|---|---|---|
| panjabi1991c | 3D distance between the left and right transverse process tips; which tubercle is the tip is not stated (panjabi1991c p. 866; p. 862 Fig 1) | SAME; the generator |
| panjabi1991t, panjabi1992 | Tip of the left transverse process to the tip of the right (panjabi1991t p. 893, p. 891 Fig 3A; panjabi1992 p. 302) | SAME |
| tan2004 | Between the two tips along X (tan2004 p. 138 Fig 1); the text calls it TPL three times (tan2004 note) | SAME landmarks; 15.6% below Panjabi on average, 24.7% at L1 (tan2004 p. 144) |
| busscher2010 TPL | One straight line across both tips; a tip-to-tip span despite its name (busscher2010 p. 1105 Fig 1); its authors find it strikingly like Panjabi's (busscher2010 p. 1112) | SAME in kind |
| bonczar2024 | Not drawn or defined (bonczar2024 note) | pooled, definition unknown |
| archive measurer | Left-right extent of labels 43 and 44 together along the scanner axis (archive/bordercall/spineps_map.py) | DIFFERS in frame: an extent along one axis, not a 3D distance |

Biases a mask value carries (Inference unless cited):

- Axis against distance: an extent along X ignores any craniocaudal or anteroposterior offset between the tips, so it reads at or below the 3D distance; axial rotation by a shortens it by about the factor cos a (1.5% at 10 deg).
- Ribs: in the thorax the rib meets the transverse process at the costotransverse joint, and a mask that merges rib with process reads high (busscher2010 note; tan2004 note). A SPINEPS instance carries no rib, but a cervical rib at C7 or a lumbar rib at L1 fused to its process would inflate the value (panjabi1991c note; duman2026 note).
- Cervical tubercles: the cervical process has anterior and posterior tubercles around the foramen transversarium; which one Panjabi took is not stated (panjabi1991c note).

(b) Mask recipe

1. Build frame F.
2. On each side take the voxel of label 43 (left) or 44 (right) of the instance with the largest absolute X. In the neck take the most lateral voxel of either tubercle and store which.
3. Report the 3D distance between the two tips as transverse_width; store its X component too.
4. Where a separate costal element is jointed or fused to a process, compute the value with and without it and flag the instance for the rib features of section 10.

(c) Radiograph

AP view, tip to tip, divided by the AP magnification (1.14 at 110 cm, eisenstein1977 p. 175); the tips lie near the frontal plane, so the projection loses little (panjabi1992 note). The magnification-free form is TPW over the upper end-plate width on the same AP view: 3.0 to 3.2 at C3 to C6, 2.83 at C7, 2.58 at T1, falling almost steadily to 1.19 at T12, then 1.48 to 1.79 at L1 to L5 (tan2004 note, computed from Table 1); TPL/UEPW 2.0 to 2.2 at C3 to C5, 2.36 at C7, 2.8 at T1 and T2, 1.15 at T12 and 1.6 to 1.8 at L1 to L5 (busscher2010 p. 1111 Fig 7b, read from the figure). Inference, from Panjabi's tables (transverse_width over endplate): 3.18 at C3, 2.65 to 2.82 at C4 to C6, 3.06 at C7, 3.07 at T1, falling to 1.50 at T11 and 1.20 at T12, then 1.73, 1.79, 1.94, 1.70 and 1.96 at L1 to L5. All three series put the minimum at T12 and a jump at L1.

(d) Course, mm

| Level | Panjabi TPW | tan2004 | busscher2010 TPL |
|---|---|---|---|
| C2 | 52.6 | - | - |
| C3 | 50.3 | 41.4 | 55.0 |
| C4 | 48.5 | 44.9 | 57.8 |
| C5 | 46.4 | 47.6 | 61.3 |
| C6 | 49.5 | 48.4 | 63.7 |
| C7 | 66.6 | 53.8 | 74.7 |
| T1 | 75.3 | 63.8 | 81.2 |
| T2 | 69.4 | 57.5 | 75.3 |
| T3 | 60.8 | 51.3 | about 66.6 to 70.1 (T3 to T9) |
| T4 | 56.9 | 49.8 | as above |
| T5 | 61.1 | 49.7 | as above |
| T6 | 61.3 | 50.2 | as above |
| T7 | 60.4 | 49.7 | as above |
| T8 | 59.9 | 47.8 | as above |
| T9 | 59.3 | 47.9 | as above |
| T10 | 58.4 | 45.4 | 63.1 |
| T11 | 52.2 | 43.0 | 59.0 |
| T12 | 46.9 | 41.0 | 54.2 |
| L1 | 71.2 | 53.6 | 78.8 |
| L2 | 76.1 | 64.3 | 85.8 |
| L3 | 85.7 | 71.4 | 94.6 |
| L4 | 79.4 | 67.7 | 92.2 |
| L5 | 92.5 | 71.3 | 97.6 |

(Panjabi: panjabi1991c p. 864 Table 5, panjabi1991t p. 895 Table 7, panjabi1992 p. 304 Table 5; tan2004 pp. 140 to 141 Table 1; busscher2010 p. 1111 Fig 7a, read from the figure.) Pooled lumbar values: 68.08, 75.07, 83.59, 79.31, 85.91 mm (bonczar2024 pp. 5 to 9).

Where it peaks, bottoms out and separates (Panjabi steps over the mean SD, Inference):

- C2 to C5 slightly falling (52.6 to 46.4), C6 49.5 (+3.1 mm, 0.35 SD), then C6/C7 +17.1 mm, 3.05 SD; C7 differs from C2 to C6 (panjabi1991c p. 866). tan2004 has only +5.4 mm there and busscher2010 about +11.
- C7/T1 +8.7 mm, 1.75 SD; tan2004 +10.0, busscher2010 about +6.5. T1 has the widest transverse processes of the thorax in all three series, and T1 differs from T3 to T12 (panjabi1991t p. 895 Table 7).
- T1/T2 -1.29 and T2/T3 -2.03 SD; T3 to T10 flat (0.03 to 0.43 SD), and TPW fails there.
- T10/T11 -1.30 and T11/T12 -0.98 SD. T12 is the column's minimum in tan2004 and busscher2010 and the thoracolumbar minimum in Panjabi.
- T12/L1 +24.3 mm, 4.01 SD, again across two papers' tables; tan2004 has +12.6 mm and busscher2010 about +24.6. Inference: unlike SPL, every series reproduces this step, so TPW is the most robust single T12/L1 length in the generator.
- L1 to L5: L3 exceeds L4 in all four lumbar series (Panjabi 85.7 against 79.4, tan2004 71.4 against 67.7, busscher2010 about 94.6 against 92.2, bonczar2024 83.59 against 79.31). L2/L3 +1.41 and L4/L5 +1.01 SD; L5 differs from L1, L2 and L4 (panjabi1992 note, Table 5). The lumbar SDs reach about 13 mm at L4 and L5 (panjabi1992 note).

(e) Covariates

None in Panjabi (pooled). tan2004 runs 8.8% (cervical), 17.1% (thoracic) and 18.9% (lumbar) below Panjabi (tan2004 note). busscher2010 links the long human thoracic processes to the postural muscles (busscher2010 p. 1111). No sex, age or stature effect is reported in the set. Error: busscher2010's ICCs, 1.00 intra and 0.98 inter, are its best (busscher2010 p. 1106 Table 1).

### 9.3 Pars interarticularis area: pars_area (PIA)

(a) Definitions

- panjabi1991t: the cross-sectional area of the pars, the bone between the superior and inferior articular processes; the plane is not stated; T1 and T2 were not measured (panjabi1991t p. 893; p. 891 Fig 3B).
- panjabi1992: named a cross-sectional area, with no landmark, plane or digitising rule (panjabi1992 p. 301 Table 1, p. 302).
- No other paper in the set measures the pars. mnemonics.py's text ("pars interarticularis cross-sectional area") matches.
- Not in the pool: printed at T3 to L5 only (schwingcheck/measures.py, left_out).
- Biases (Inference): any recipe is an assumption, since the section is undefined (panjabi1992 note); a section oblique to the bar reads high by about 1 / cos of the obliquity; at 1 mm voxels partial volume moves a section of this size by a share like the pedicle's (section 7.3).

(b) Mask recipe (Inference)

1. Build frame F.
2. On each side take the centroids of the superior articular process (label 45 or 46) and the inferior articular process (47 or 48).
3. Between them, reslice label 41 of that side perpendicular to the line joining the two centroids every 0.5 mm; keep the connected bone lateral to the canal.
4. Report the smallest section's area per side; the pool would take pars_area:mean. Store the section's position along the line.
5. If no section holds bone, report zero, flag a pars defect and keep the instance. Spondylolysis was found in 10 of 443 skeletons (2.3%), nine bilateral at L5 and one left-sided at L4 (eisenstein1977 p. 177).

(c) Radiograph: not measurable (panjabi1991t note; panjabi1992 note). The set gives no radiographic method for the pars.

(d) Course, side means, mm2 (Inference, from panjabi1991t p. 895 Table 7 and panjabi1992 p. 304 Table 5): T3 95.5, T4 70.5, T5 85.0, T6 78.0, T7 105.5, T8 117.0, T9 132.0, T10 139.5, T11 162.0, T12 92.0; L1 62.1, L2 69.8, L3 72.5, L4 81.8, L5 82.3.

- It rises from T4 to a peak at T11 and drops at T12, which the authors explain by T12's lumbar-type inferior facets (panjabi1991t p. 893). L1 to L5 rise gradually; only the right side's L5 against L1 is significant (panjabi1992 p. 302).
- Separations (Inference, long table): T12/L1 -29.9 mm2, 2.07 SD, across two papers' tables; T3/T4 -1.03 SD; T11/T12 -70 mm2 but only 0.89 SD, because T11's left SEM of 45.6 inflates its SD to 135 mm2. Nothing else exceeds 0.8 SD.
- Doubts: the right SEMs at T3 and T4 (1.3 and 2.8) are implausibly small and the right and left means differ by up to 45 mm2 (panjabi1991t note); the right L3 is printed 70.0 where the paper's Figure 5 plots 80 (panjabi1992 note, Inference: a misprint).

(e) Covariates: none (pooled). The defect rates above are the only population fact.

### 9.4 Laminae (no generator key)

Only abbas2021 measured the laminae: 180 controls and 165 patients with degenerative stenosis, Israel, living CT, aged 40 and over (abbas2021 p. 2).

| Measure | Definition | Control men, L1 to L5, deg (mean +/- SD) | Control women |
|---|---|---|---|
| Laminar inclination (LI) | On a parasagittal plane through the middle of one lamina, the angle between the lamina's long axis and the posterior cortex of the same body, on the caudal side; modified from Xu, who used the body's horizontal plane (abbas2021 p. 2; p. 4 Fig 4; p. 6) | 22.6 +/- 5, 26.4 +/- 6, 31.4 +/- 6, 39.5 +/- 6, 46.7 +/- 8 | 26.5, 29.5, 34, 42.3, 49.8 |
| Interlaminar angle (ILA) | On an axial slice through the upper third of the laminae, the angle between the two laminae's long axes, opening toward the canal (abbas2021 p. 2; p. 3 Fig 3) | 116 +/- 10, 116 +/- 9, 113 +/- 11, 102 +/- 11, 98 +/- 11 | 114, 112, 108, 98, 94 |

(abbas2021 p. 6 Table 4.)

- Mask recipes (Inference, abbas2021 note). LI: in frame F, take the YZ-parallel plane through the centre of one lamina, fit a line to the posterior cortex of the body (labels 49, 52, 53) between the plates and one to the lamina's long axis (label 41 posterior to the canal), and take the angle on the caudal side; do both sides and store each, since the paper does not say which it used. ILA: take the transverse section one sixth of the laminae's craniocaudal extent below their top, fit the principal axis of each lamina's section, and take the angle on the canal side.
- Radiograph: ILA cannot be taken from a film (an axial angle). LI might be drawn on a lateral view, which superimposes both laminae and the facets; not validated (abbas2021 note).
- Course and separation: LI rises steadily, with steps of 3 to 8 deg against SDs of 4 to 8; the L3/L4 and L4/L5 steps exceed one SD. ILA falls most from L3 to L4 (10 to 11 deg) against SDs of 9 to 13 and separates L1 to L3 from L4 and L5, not neighbours (abbas2021 note). LI is the steadiest monotone level gradient in that paper (abbas2021 note). No thoracic, cervical or sacral value exists.
- Covariates: control women's LI 2.6 to 3.9 deg larger and ILA 2 to 5 deg smaller than men's (abbas2021 note, from Table 4). Stenosis lowers LI at L2 to L4 in men and L1 to L4 in women, not at L5; it lowers ILA at L4 and L5 in men and raises it at L2 to L4 in women (abbas2021 p. 6 Table 4).
- What others say without measuring: an increased interlaminar angle, with short laminae, not short pedicles, is the structural cause of a narrow midsagittal canal (eisenstein1977 p. 174); laminar inclination, the interlaminar angle and laminar thickness probably set the canal depth more than pedicle height does (amonookuofi1985 pp. 76 to 77). Spina bifida, a complete separation of the two laminae, was found in the lumbar spine of 7 of 443 skeletons (1.6%), level not given (eisenstein1977 p. 177; eisenstein1977 note). The set holds no laminar thickness, height or length.

### 9.5 The spinous process's position and angle (no generator key)

- Spinous process angle, SPA (busscher2010): the sagittal angle between the process axis and a reference line through its base at right angles to the body's long axis, positive with the tip caudal (busscher2010 p. 1105 Fig 1; the reference is Inference in its note). Read from Fig 6: C3 25.3, C4 26.1, C5 28.3, C6 19.6, C7 22.5, T1 about 30, T3 34.8, T4 44.7, T5 55.2, T6 62.2 (the maximum, p. 1110), T8 53.6, T10 37.8, T12 20.4, L1 10.3, L2 13.9, L3 12.5, L4 13.9, L5 about 22.5 deg (busscher2010 p. 1110 Fig 6). It sets T5 to T8 (above 50 deg) apart from everything and the lumbar spine (10 to 14 deg at L1 to L4) apart from the thorax, and rises again at L5 (busscher2010 note). Its inter-observer ICC is only 0.83 (busscher2010 p. 1106 Table 1). Six cadaver men.
- Spinous inclination alpha (gilad1985): the angle at the posteroinferior body corner between the prolonged lower end-plate line and the line to the spinous tip, computed by trigonometry, no SD: C2 10.7, C3 14.4, C4 12.1, C5 6.1, C6 3.8, C7 7.3; L1 -5.8, L2 -3.0, L3 -0.3, L4 1.9, L5 8.2 deg (gilad1985 p. 118 Table 2). Positive puts the tip caudal to the lower end-plate line (gilad1985 note, Inference on the sign). Recomputed from the table means, alpha matches the printed value within 1.0 deg at every level except C2 (-2.7 deg against the printed 10.7) and L2 (-0.2 deg against the printed -3.0), so use C2 and L2 with caution (gilad1985 note).
- Overall vertebral length L (gilad1985): the distance from the anterior wall line to the parallel line through the spinous tip: C2 51.3, C3 45.2, C4 45.5, C5 48.9, C6 56.2, C7 62.3; L1 80.9, L2 84.6, L3 85.2, L4 83.3, L5 77.4 mm (gilad1985 p. 118 Table 2). The shortest cervical is C3 and the longest C7; the longest lumbar is L3 and the shortest L5 (gilad1985 p. 120). Steps C5/C6 +7.3, C6/C7 +6.1, L4/L5 -5.9 mm (gilad1985 note).
- Spinous tip from the posterior corners, e and f (gilad1985): values in 9.1; e exceeds f at every level, so the tip lies below mid-body height, by 1.8 to 3.8 mm more in the neck and 5.7 to 7.5 mm in the lumbar spine, most at L5 (gilad1985 p. 119; gilad1985 note). The strongest adjacent steps are f C2/C3 -2.14, e C6/C7 +1.98 and f C6/C7 +1.63 pooled SD (gilad1985 note).
- Mask recipe (Inference, gilad1985 note): build frame F; project the instance along X to a silhouette, which is what a lateral film records; take the body corners and the most posterior point of the process on the silhouette; compute e, f, alpha and L from them. Compute the midsagittal-slice version too and keep the difference as a check. For SPA take the principal axis of label 42 in the midsagittal band against frame Z.
- Radiograph: all of these are lateral-view measures; alpha and SPA need no magnification; e, f and L are divided by it (gilad1985 note).

## 10. Ribs and costal facets

Three papers bear on the ribs:

- panjabi1991t digitised the costovertebral and costotransverse articular surfaces of its 12 thoracic columns, 144 vertebrae cleaned to dry bone (panjabi1991t p. 888, p. 890). It is the generator's only source for the five rib keys.
- duman2026 counted 12th-rib and supernumerary-rib anomalies on CT in 517 living Turkish adults (duman2026 p. 5; p. 10 Table 5).
- busscher2010 kept about 3 cm of rib with both joints on its six cadaver spines (busscher2010 p. 1105). That bears on how ribs contaminate other measures.

No paper in the set measured a rib facet on CT or on a mask, a distribution of rib lengths, or a rib on fluoroscopy. SPINEPS segments no rib (duman2026 note), so every rib measure needs the independent rib arm the duman2026 note names. Every recipe in this section is Inference.

What the generator holds (schwingcheck/measures.py, left_out; schwingcheck/README.md, "The pool"):

- Five rib keys, none in the pool.
- Three are printed at only part of C3 to L5: costovertebral_area_upper (T1 to T12, per side), costovertebral_area_lower (T1 to T10, per side) and costotransverse_area (T1 to T11, per side).
- Two are printed with no spread: costovertebral_area and rib_articulation_area (T1 to T12, whole).
- Its two rib phenotypes, lumbar_rib and no_rib_t12, carry no rib feature. They draw the L1 or the T12 body half-way between the T12 and L1 profiles (schwingcheck/columns.py, phenotype_levels; SYNTH blend 0.5).

Inference: a rib seen or missed on an image enters the rule nowhere today. The presence features of 10.4 would be its first rib evidence.

Recipe R, the rib articulations of one thoracic instance k (Inference, from the panjabi1991t note and the duman2026 note):

1. Build frame F (section 2.2).
2. Take the rib arm's segmentation as one connected component per rib per side. By the authors' rule, rib n meets the upper part of Tn and the lower part of Tn-1 (panjabi1991t p. 893). So name a rib by the instance whose upper body surface its head touches, and keep the name the count from C2 gives that instance. Caveat (panjabi1991t note, Gaps): the rule is loosely stated. By it, T10's lower facet (30.0 right, 26.9 left mm2) would be rib 11's, which the authors call uniarticular on T11, and rib 1 would reach C7. Classical anatomy has rib 1 on T1 alone and rib 10 often on T10 alone, which the paper neither confirms nor counts. Treat T10's lower facet as present or absent, not as rib 11's.
3. Head contact: take the body-surface voxels of instance k (the boundary of labels 49, 52 and 53) within 2 mm of a rib-head voxel. Inference on 2 mm: it spans a joint gap and a voxel of partial volume, since no paper gives a joint-space width. Split the patch at the body's mid-height along Y: the cranial part is the upper facet (rib k), the caudal part the lower facet (rib k+1).
4. Tubercle contact: take the voxels of label 43 (left) or 44 (right) of instance k within 2 mm of the rib of that side. That is the costotransverse facet, on the anterior face of the process tip (panjabi1991t note).
5. Areas: take the vector area (O2) of each patch, per side.
   - costovertebral_area is the mean of the two upper areas plus the mean of the two lower areas, as Panjabi's total is built (panjabi1991t note, by arithmetic).
   - rib_articulation_area is that total plus the side mean of the costotransverse area.
6. Presence, per side: whether a rib touches the body, whether there is a lower facet, whether there is a costotransverse facet, and the rib's length (10.3). Store presence as a state, not as an area of zero.
7. Without a rib segmentation, do not attempt the areas. Inference: Panjabi's facets measure 11.7 (CTA T11 left) to 71.9 mm2 (CVAu T11 right) (panjabi1991t p. 895 Table 6). On a 1 mm instance mask that is a few dozen surface voxels, in a shallow cortical hollow with no edge any label marks, so the vertebra alone cannot give its outline.

Biases common to the rib areas (Inference unless cited):

- What is measured: Panjabi outlined the articular surface on dry bone. Recipe R's patch is defined by nearness to the rib, so its area grows with the threshold and with the cartilage left between rib and body, which the set never measures. No paper gives an offset between a CT patch and a dry-bone facet.
- Names: mnemonics.py calls the upper and lower surfaces demifacets and the two totals "the total per rib" (schwingcheck/mnemonics.py). At T11 and T12 the single facet is whole and no lower facet exists (panjabi1991t p. 893; p. 895 Table 6). At T1 the upper facet is, Inference, rib 1's whole facet (panjabi1991t note). Both totals are per side for one vertebra, not per rib: by the authors' own rule the upper and lower facets belong to two different ribs (panjabi1991t note, by arithmetic).
- Contamination of other measures: a whole-vertebra mask may take in rib heads at the end-plate margins and rib voxels at the costotransverse joint. Exclude them from end-plate widths and from transverse_width (busscher2010 note; section 9.2, step 4). Inference: busscher2010's T1 lower end-plate width of about 35.4 mm against T2's upper of about 26.8 across one disc may carry rib heads (busscher2010 p. 1109 Fig 3; busscher2010 note).

### 10.1 Costovertebral areas: costovertebral_area_upper (CVAu), costovertebral_area_lower (CVAl), costovertebral_area (CVA)

(a) Definitions

- panjabi1991t defines the area of the rib-head articular surface on the body, upper and lower, right and left. Each is outlined by up to 20 digitised points in five rows of three to four (panjabi1991t p. 888; p. 891 Fig 3B), and its area is the projected (vector) area of the outline (panjabi1991t p. 889). SAME; this is the generator.
- CVA is printed in Table 6 as a total "per rib" (panjabi1991t p. 895). It equals the mean upper area plus the mean lower area of one vertebra, for example at T1 51.0 + 23.7 = 74.7 mm2 (panjabi1991t note; Inference, by arithmetic).
- schwingcheck/mnemonics.py uses the same numbers under the names demifacet and per rib. It DIFFERS in words, not in values (see the biases above).
- No other paper in the set measured a costovertebral facet.

(b) Mask recipe: recipe R, steps 1 to 3, 5 and 6. The lower facet is absent by definition at T11 and T12, so model it there as absent, not as a mean with noise (panjabi1991t note).

(c) Radiograph

- No film gives these areas (panjabi1991t note).
- Inference: an AP view, or AP fluoroscopy, shows a rib head beside the body only as an overlap with the pedicle and the lateral body margin. Whether a rib is present at a level can be read where the rib is long enough (duman2026 p. 9 Fig 4B); which facet the rib uses cannot.
- On a lateral film the ribs and scapulae overlap the thoracic posterior elements (busscher2010 note).

(d) Course, mm2. Side means and SD (Inference: the mean of the two sides' SEM x 3.46; panjabi1991t p. 895 Table 6). Presence follows the table's dashes.

| Level | CVAu mean (SD) | CVAl mean (SD) | CVA total (no spread) |
|---|---|---|---|
| T1 | 51.0 (22.5) | 23.7 (6.5) | 74.7 |
| T2 | 29.2 (7.9) | 16.6 (7.4) | 45.8 |
| T3 | 30.5 (9.5) | 21.2 (12.1) | 51.7 |
| T4 | 34.1 (16.3) | 21.4 (9.5) | 55.5 |
| T5 | 42.0 (15.4) | 25.4 (15.8) | 67.4 |
| T6 | 52.4 (20.3) | 36.4 (19.7) | 88.8 |
| T7 | 50.6 (20.6) | 35.7 (14.6) | 86.3 |
| T8 | 41.8 (24.2) | 35.0 (18.0) | 76.8 |
| T9 | 42.9 (13.9) | 32.5 (13.6) | 75.4 |
| T10 | 54.1 (20.6) | 28.4 (15.4) | 82.6 |
| T11 | 66.0 (22.3) | absent | 66.0 |
| T12 | 54.5 (22.5) | absent | 54.5 |

- Shape of the course: the total drops sharply from T1 to T2, rises to T6, holds from T6 to T10 and falls at T11 and T12 (panjabi1991t p. 893; p. 898 Fig 7).
- Peaks: the upper surface is largest at T11 on both sides, 71.9 mm2 right and 60.0 left (panjabi1991t p. 895 Table 6). T1's upper surface, 45.3 right and 56.6 left, is 1.6 and 1.9 times T2's, 29.0 and 29.5 (panjabi1991t note).
- T10 still carries lower surfaces, 30.0 right and 26.9 left (panjabi1991t p. 895 Table 6). By the authors' rule these would belong to rib 11, which they call uniarticular on T11. Inference: the rule is the textbook pattern loosely stated, and the paper neither confirms nor counts rib 10 on T10 alone (panjabi1991t note).
- Separation (Inference, step over the mean of the two levels' SDs): CVAu T1/T2 -21.7 mm2 (-1.43 SD) and CVAl T1/T2 -7.1 (-1.03 SD). From T2 to T12 no area step exceeds 0.66 SD; the largest are CVAu T9/T10 +0.65 and T10/T11 +0.55, and CVAl T5/T6 +0.62. The one strong signal below T1 is categorical: the lower facet is there at T10 and absent at T11 and T12. So the areas separate T1 from T2, and the presence of the lower facet separates T10 from T11. Nothing separates T3 to T9 from each other.
- The set holds no costovertebral value for C7, a T13 or L1. Inference: a lumbar rib meets the tip of the transverse process, not the body (duman2026 p. 10 Fig 5B), so it would show as a costotransverse-type joint, not a costovertebral one.

(e) Covariates: none. Panjabi pooled 8 men and 4 women (panjabi1991t p. 889 Table 1). The set holds no age, stature or population data on these areas.

### 10.2 Costotransverse area and the rib total: costotransverse_area (CTA), rib_articulation_area (CVA + CTA)

(a) Definitions

- panjabi1991t defines the area of the rib-tubercle articular surface on the transverse process, per side (panjabi1991t p. 891 Fig 3B; p. 895 Table 6). SAME; the generator.
- CVA + CTA is CVA plus the side mean of CTA (panjabi1991t note; Inference, by arithmetic). mnemonics.py calls it the total per rib; it is per side for one vertebra, as with CVA.
- No other paper in the set measured it.

(b) Mask recipe: recipe R, steps 4 to 6.

- Read presence even without the rib: a costotransverse facet sits on the anterior face of the costal-process tip at T1 to T11 and is absent at T12 (panjabi1991t note).
- Inference: on a mask with a rib arm, a rib tubercle within 2 mm of the process tip marks it. On a mask without one, nothing does.

(c) Radiograph

- Not measurable (panjabi1991t note).
- Inference: on an AP view the rib crosses the transverse-process tip, so a rib reaching the tip can be seen, but no joint surface can.

(d) Course, mm2. Side means and SD (Inference, as in 10.1; panjabi1991t p. 895 Table 6).

| Level | CTA mean (SD) | CVA + CTA (no spread) |
|---|---|---|
| T1 | 57.4 (15.8) | 132.0 |
| T2 | 50.1 (13.2) | 95.9 |
| T3 | 58.7 (21.5) | 110.4 |
| T4 | 60.2 (11.6) | 115.7 |
| T5 | 51.3 (10.7) | 118.7 |
| T6 | 48.5 (18.0) | 137.3 |
| T7 | 46.4 (13.7) | 132.7 |
| T8 | 51.9 (56.6) | 128.7 |
| T9 | 54.8 (19.3) | 130.1 |
| T10 | 55.8 (45.0) | 138.4 |
| T11 | 14.2 (3.4) | 80.2 |
| T12 | absent | 54.5 |

- Shape of the course: CTA is flat at about 40 to 65 mm2 per side from T1 to T10. At T11 it is small, 16.7 right and 11.7 left, and at T12 it is absent (panjabi1991t p. 895 Table 6). The total falls at T11 and T12 because of that drop and because those bodies are uniarticular (panjabi1991t p. 893).
- Two right-side SEMs are doubtful: 26.7 at T8 (mean 63.8) and 17.3 at T10 (mean 62.3). They may be misprints of 2.67 and 1.73; the paper does not comment (panjabi1991t note). They inflate the SD at T8 and T10 above.
- Separation (Inference, as in 10.1): the T10/T11 step is -41.6 mm2, which is -1.72 SD with the sides pooled. On the left alone it is -37.6 mm2 (-2.41 SD); on the right alone -45.6 mm2 (-1.39 SD), with the doubtful T10 SEM. The T11/T12 step is categorical: present against absent. T4/T5 is -0.80 SD; every other step is 0.5 SD or less. The total's T1/T2 step, 132.0 to 95.9, has no spread to judge it by.
- So this measure separates T10, T11 and T12 from each other: full, small and absent. It separates no pair from T1 to T10.

(e) Covariates: none; Panjabi pooled (panjabi1991t p. 889 Table 1).

### 10.3 The 12th rib, lumbar ribs and cervical ribs (no generator key)

(a) Definitions and counts (duman2026 p. 5; p. 10 Table 5). Population: 517 living adults on CT, 277 men and 240 women, from a tertiary chest hospital in Izmir (duman2026 p. 1, p. 3).

| Anomaly | Definition | All | Men | Women |
|---|---|---|---|---|
| Hypoplastic 12th rib | shorter than 4 cm; how length was measured is not stated | 55/517 (10.64%) | 25/277 (9.03%) | 30/240 (12.50%) |
| Absent 12th rib | no 12th rib | 22/517 (4.26%) | 4/277 (1.44%) | 18/240 (7.50%) |
| Lumbar rib | supernumerary rib below T12 | 12/517 (2.32%) | 10/277 (3.61%) | 2/240 (0.83%) |
| Cervical rib | supernumerary rib in the neck | 7/517 (1.35%) | 1/277 (0.36%) | 6/240 (2.50%) |
| Any rib anomaly | sum of the four | 96/517 (18.57%) | 40/277 (14.44%) | 56/240 (23.33%) |

- Laterality was to be recorded (duman2026 p. 5) but is never reported. So unilateral and bilateral absence cannot be told apart, and an absent 12th rib cannot be read as eleven rib pairs (duman2026 note).
- The four types sum exactly to 96, so each patient sits in one category. Yet one patient in Figure 4A to B has a hypoplastic right and an absent left 12th rib, and the filing rule is not given (duman2026 p. 9; duman2026 note).
- Sex: by recomputation, the female excess of absent ribs (Fisher p about 0.0007) and the male excess of lumbar ribs (p about 0.042) stand. The female excess of cervical ribs rests on 7 cases, and Fisher p is about 0.053 (duman2026 note, recomputed from Table 5).
- Not given anywhere: how levels were counted, any criterion separating a lumbar rib from an elongated transverse process, and any criterion for L1 with a rib against a T13 (duman2026 note). Bifid and foramen ribs were recorded but never counted (duman2026 p. 5; duman2026 note).
- The other papers: panjabi1991t reports no rib anomaly in its 12 spines and says nothing of how it numbered them (panjabi1991t note). busscher2010's six spines all had 7 cervical, 12 thoracic and 5 lumbar vertebrae (busscher2010 p. 1105). Neither is a prevalence.

(b) Mask recipe (Inference)

1. Take the lowest rib on each side from the rib arm.
2. Measure its length two ways and store both, since duman2026 does not say which it used:
   - along its centreline, the longest path of its skeleton from the head to the tip;
   - as the chord from head to tip.
3. Flag hypoplastic below 40 mm by each length.
4. Call the rib absent on a side when no rib touches the instance the count from C2 names T12. Record the side.
5. Lumbar rib: a costal element jointed to the transverse process of the first lumbar-type instance (duman2026 p. 10 Fig 5B). Call it a lumbar rib on L1 only if the count from C2 gives twelve thoracic instances above it; otherwise consider T13 (duman2026 note; the paper gives no rule).
6. Cervical rib: look at the lowest cervical instance. Inference: that is C7, since the paper names no level (duman2026 p. 10 Fig 5A; duman2026 note). Confirm that C7 is in the field of view before calling a cervical rib absent.

(c) Radiograph and fluoroscopy

- An AP radiograph can show a hypoplastic or absent 12th rib (duman2026 p. 9 Fig 4B). The authors warn that an AP view alone is not enough to fix the level (duman2026 pp. 12 to 13).
- The 4 cm cut-off was applied on CT. A rib running obliquely back and down is foreshortened on an AP projection, so a projected length under 4 cm does not prove hypoplasia (duman2026 note, Inference).
- Inference, not measured: AP fluoroscopy behaves as an AP film with a smaller field. A short or missing lowest rib on either side warns that a count from above and a count from below may disagree (duman2026 pp. 12 to 13), and it should send the naming to CT. A lateral view gives no usable rib reading.

(d) Course: these are presence features at three places, C7, T12 and L1, not a course. The anomaly priors, the junction criteria and their use in the decoder are in the part "Anomalies, numbering and the junctions", sections 1.2, 2.4 to 2.6, 4.2 and 4.3. They are not repeated here. In duman2026's own measures, every body height and pedicle dimension rises smoothly from T11 to L2, with no step at T12/L1 (duman2026 note, from pp. 7 to 8 Tables 1 and 2). Inference: the rib and its facets are the evidence there, which is why they matter.

(e) Covariates

- Sex, as tabulated above.
- Age: not reported for the anomalies (duman2026 note).
- Population: Turkish, from one chest centre; mixed thoracic and abdominal fields of view. The cervical-rib rate may be an undercount, since the 517 may include scans without C7 (duman2026 note).
- No reliability is given for the anomaly calls or for rib length (duman2026 note).

### 10.4 Rib features the generator lacks (Inference)

Store these per side for every instance from C7 to L1, as states with probabilities, never as continuous values with zero-mean noise (panjabi1991t note):

- Rib present: touching the body or the costal process.
- Lower costovertebral facet present: expected at T1 to T10, absent at T11 and T12 (panjabi1991t p. 895 Table 6).
- Costotransverse facet: full at T1 to T10, small at T11, absent at T12 (panjabi1991t p. 895 Table 6).
- Upper facet larger than the next level's: expected at T1 against T2 (panjabi1991t note).
- Lowest-rib length, both ways (10.3).
- Lumbar-rib and cervical-rib flags (10.3).

The normal pattern comes from 12 dry spines. The departures come from 517 living Turkish adults. That pairs a pattern with no counted variation with rates that carry no laterality and no counting rule, so treat both as weak (panjabi1991t note; duman2026 note).

## 11. Feature-extraction specification

This section lists every measure of the generator, one row per key, in mnemonics.py's order. These are the 49 measures the four papers print (schwingcheck/measures.py; schwingcheck/README.md, "The pool").

How to read a row:

- A per-side measure is extracted on each side under its plain key and enters the pool as its side mean, key:mean.
- For the four mirrored keys, facet_sag_sup, facet_sag_inf, facet_card_y_sup and facet_card_y_inf, the generator's mean is (left - right) / 2 (schwingcheck/measures.py).
- "Pool" says whether the key is among the 32 the rule scores over C3 to L5 as the code stands. Where it is not, the reason is the one measures.py's left_out gives. Two of the 32, endplate_incl and endplate_lower_incl, were recommended for leaving out (3.5), which would leave 30; the owner kept all 32 as printed on 2026-10-29.
- Every mask algorithm is Inference, since no paper in the set measured a mask (section 2).
- "Same definition" names the papers whose landmarks match Panjabi's. Their values may still differ for population, age or modality; the section cited gives the offsets.
- The common steps are frame F (2.2), recipe C (6), recipe P (7), recipe J (8) and recipe R (10), and the operations O1 to O5 (2.4).

Rules for the extractor that hold for every row (Inference):

- Work in frame F, never in scanner axes. Every scanner-axis extent in the archive measurer carries a rotation or tilt bias of the size shown in 3.1, 3.3, 6.1 and 6.2.
- Store raw geometry beside every value: centroids, normals, axes, section positions and side.
- Store a status for every value: measured, absent by anatomy, absent by segmentation, neighbour missing, or ambiguous. A missing value is NaN to the rule (schwingcheck/README.md, "Missing values"), and an anatomical absence is a feature in its own right (10.4).
- Never take a canal value from label 61, a pedicle value from an extent of label 41, or a facet value from an extent of the whole articular process.

### 11.1 The vertebral body

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| endplate (EPWu) | length mm; C3-L5; pool; mask and AP | O1 cranial plate (label 52, else the top 2 mm of 49); the extent on the plate's fitted plane along the in-plane direction nearest X; at C3-C7 drop the unci first (3.1) | panjabi1991c, panjabi1991t, panjabi1992; tan2004 (about 10% lower); frontphys2026 at L1-L5 | Scanner axes read high (+5.4 mm at 10 deg rotation, 3.1); the unci read high at C3-C7; a dropped rim reads a voxel per side low; never pool waist widths (3.6) or busscher2010's cervical full-body width |
| endplate_depth (EPDu) | length mm; C3-L5; pool; mask and lateral | O1 cranial plate; the extent along Z in the band abs(X) <= 3 mm, rim to rim with the ring apophysis (3.2) | Panjabi's three; tan2004 (15.6% lower); busscher2010; gilad1985 (lumbar within 1 mm) | Lordotic tilt in scanner axes inflates L4-L5; the whole body's maximum Z reads high (lobes, osteophytes); waist depths read 1-5 mm low |
| endplate_lower (EPWl) | length mm; C2-L5; pool; mask and AP | As endplate, on label 53 or the bottom 2 mm | As endplate | As endplate; at T1 a mask may include rib heads (busscher2010 note; 10) |
| endplate_lower_depth (EPDl) | length mm; C2-L5; pool; mask and lateral | As endplate_depth, on the caudal plate | As endplate_depth | As endplate_depth |
| h_post (VBHp) | length mm; C3-L5; pool; mask and lateral | Body voxels (49, 52, 53) within 2 mm in front of the posterior wall, in the band abs(X) <= 3 mm; the median Y extent of the columns (3.3) | Panjabi's three; tan2004 (4% lower); busscher2010; in kind the living CT series, which mostly run above Panjabi: frontphys2026 1.7 to 3.8 mm at L1-L5, moncadahabib2025 -0.4 to +3.1, duman2026 men 1.8 to 2.8 at T11-L2 (3.3); abbas2021 prints no height | The archive measurer takes label 49 only along scanner SI, reading h / cos b (+1.5 mm at 20 deg tilt). Inference: where labels 52 and 53 lie outside 49 it also drops the plates and reads low; check on one mask. A lateral view reads 1.8-3.0 mm high at C3-C7 (panjabi1991c p. 868). The ap regime lists h_post, though an AP view does not show the posterior wall (schwingcheck/measures.py) |
| endplate_area (EPAu) | area mm2; C3-L5; pool; mask | O1 + O2: the vector area of the cranial plate; drop the unci at C3-C7 (3.4) | Panjabi's three; tan2004 in kind | The scalar area of a concave mesh reads high; the ellipse from width and depth reads 1.7-19% high against Panjabi's areas and about 12-17% low against tan2004's lumbar plates, opposite signs (3.4); never substitute it |
| endplate_lower_area (EPAl) | area mm2; C2-L5; pool; mask | As endplate_area, caudal plate | As endplate_area | As endplate_area |
| endplate_incl (EPItu) | angle deg; C3-L5; in the pool as printed by the owner's choice of 2026-10-29, though Panjabi's lumbar L1-L5 rows reprint his cervical C3-C7 rows (3.5; [panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md)); mask and lateral | Plane fit to the cranial plate; the unsigned angle of its normal to frame Y; store the signed sagittal and coronal parts too (3.5) | Panjabi only | Signed or sagittal-only angles (tan2004) differ; a mean of magnitudes near zero is biased upward; the lumbar rows carry the same 20 numbers as the cervical rows, most probably cervical numbers, so most probably no lumbar value of Panjabi's exists to score against |
| endplate_lower_incl (EPItl) | angle deg; C2-L5; in the pool as printed by the owner's choice of 2026-10-29, despite the same reprint (3.5; [panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md)); mask and lateral | As endplate_incl, caudal plate | Panjabi only | As endplate_incl; at L5 the same-definition series read about 10.5 to 12 deg against the printed 1.8 (3.5) |
| endplate_wedge (EPIt) | angle deg; T1-T12; not in pool (no spread); mask and lateral | The sum of the two unsigned inclinations, as printed; store the frame-free angle between the two plates (3.5) | panjabi1991t only | Unsigned sum, not a signed wedge; no spread printed |

### 11.2 The canal

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| canal_w (SCW) | length mm; C2-L5; pool; mask and AP | Recipe C; the greatest X extent between the medial pedicle surfaces over the closed transverse sections; store the mid-pedicle value too (6.2) | Panjabi's three; tan2004 (0.79-0.82 of Panjabi); busscher2010; eisenstein1977 (greatest); in kind griffith2016, ahmed2019, alonge2021, cizmic2023, masharawi2021 | The archive measures label 61, the dural sac, narrower than bone and not filling the L5 recesses; rotation reads +2.7 mm at 10 deg; a section at the facets reads narrow; film interpediculate distances are magnified minima (6.2) |
| canal_ap (SCD) | length mm; C2-L5; pool; mask and lateral | Recipe C; in the mid-pedicle section, rays along -Z at abs(X) <= 1 mm from the body's back to the first arch voxel, the median; store the minimum over sections (6.1) | Panjabi's three; tan2004 (31.8% lower); busscher2010; griffith2016; masharawi2021 VCL; cizmic2023 MSG | Label 61 is bounded by disc and flavum at the disc and is not one vertebra's foramen; sagittal tilt reads +2.3 mm at 20 deg; minima (eisenstein1977, amonookuofi1985) read below mid-pedicle values |
| canal_area (SCA) | area mm2; C2-L5; pool; mask | Recipe C; the foramen's area in the mid-pedicle section; store the minimum (6.3) | Panjabi's three; griffith2016 in kind; tan2004 (31.7% lower) | Label 61 as above; the ellipse on SCW and SCD reads 10-30% high (panjabi1992 p. 305); abbas2021's mid-body section differs |

### 11.3 The pedicles

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| pedicle_w, pool pedicle_w:mean (PDW) | length mm; C2-L5; pool; mask and AP | Recipe P; the extent of the isthmus section along u; store the minor axis and roll (7.1) | Panjabi's three; tan2004 (25.7% lower); in kind zindrick1987 TW, olsewski1990, yu2015, lien2007, hou1993, mitra2002, krag1988, robertson2000 coaxial width, busscher2010 PedW, and the living-CT series (arockiaraj2025, duman2026, moncadahabib2025, masharawi2021) | An extent of label 41 is no pedicle (the archive refuses it); an axial chord reads w / cos a (+10% at L5, +39% at C4); a minor axis reads 4-7 mm low at L4-L5; makino2012's endosteal width reads about two cortices low; Panjabi's section position is unstated |
| pedicle_h, pool pedicle_h:mean (PDH) | length mm; C2-L5; pool; mask and lateral | Recipe P; the extent of the isthmus section along v; store the major axis (7.2) | Panjabi's three; tan2004 (16.1% lower); the caliper and CT series of 7.2 | Without reslicing, reads high by 1 / cos(PDIt), small; a major axis differs at L4-L5 (otsuki2021, robertson2000); makino2012 endosteal |
| pedicle_area, pool pedicle_area:mean (PDA) | area mm2; C2-L5; pool; mask | Recipe P; the plain area of the isthmus section (7.3) | Panjabi's three; tan2004; otsuki2021 whole section in kind | An axial cut reads 1 / cos a high; partial volume moves a thoracic section about 25% at 1 mm voxels (7.3) |
| pedicle_incl_sag, pool pedicle_incl_sag:mean (PDIs) | angle deg; C3-L5; pool; mask | Recipe P axis in frame F; arcsin(abs(a_x)), signed positive anteromedial (7.4). This is the clinical convergence angle | Panjabi's three; tan2004; zindrick1987 TA; krag1988; olsewski1990, lien2007, hou1993, mitra2002, arockiaraj2025 | Panjabi's names are the reverse of the clinical ones; an image midline adds axial rotation (the side mean cancels it); moncadahabib2025 and busscher2010 PedA differ in convention |
| pedicle_incl_trans, pool pedicle_incl_trans:mean (PDIt) | angle deg; C3-L5; pool; mask and lateral | Recipe P axis; arcsin(abs(a_y)), positive with the posterior end cranial (7.4). This is the clinical sagittal angle | Panjabi's three; zindrick1987 SA; tan2004 | olsewski1990, mitra2002 and lien2007 measure against the end plate and differ by EPItu |

### 11.4 Laminae and processes

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| spinous_length (SPL) | length mm; C2-L5; pool; mask and lateral | 3D distance from the cranial end-plate centroid (frame origin) to the farthest label-42 voxel; store the free process length too (9.1) | panjabi1992, panjabi1991t; panjabi1991c in intent; tan2004 | mnemonics.py's text, and the comment in measures.py, start at the canal's back wall. That is wrong against panjabi1992 p. 302, panjabi1991t p. 893 and panjabi1991c p. 866, and reads about half the table. The archive starts at the body centroid, 11.5-12.2 mm below the plate centre at L1-L5. busscher2010's free process reads 30-40 mm short. Bifid cervical tips: take either limb. The T12/L1 step of +20.3 mm joins two papers' tables, while single series show +3.0 (tan2004) and +4.3 (busscher2010) (9.1) |
| transverse_width (TPW) | length mm; C2-L5; pool; mask and AP | 3D distance between the most lateral voxels of labels 43 and 44; store the X component; flag a jointed costal element (9.2) | Panjabi's three; tan2004 (15.6% lower); busscher2010 TPL | An extent along X reads at or below the 3D distance; rib merged with the process reads high (10); which cervical tubercle Panjabi took is unstated; the archive's tp_span is a scanner-axis extent |
| pars_area, pool pars_area:mean (PIA) | area mm2; T3-L5; not in pool (part of C3-L5); mask | The smallest label-41 section perpendicular to the line between the two articular-process centroids, each side; zero flags a pars defect (9.3) | panjabi1991t, panjabi1992 only (plane unstated) | Any section is an assumption; an oblique section reads 1 / cos high; partial volume as for the pedicle |

### 11.5 The uncovertebral joints

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| uncovertebral_area_upper, pool key :mean (UJAu) | area mm2; C3-C7; not in pool (part of C3-L5); CT | The body-surface patch of instance k on the uncus within 3 mm of instance k-1; its vector area (8.6) | panjabi1991c only | The area depends on the proximity threshold; no other series to check |
| uncovertebral_area_lower, pool key :mean (UJAl) | area mm2; C2-C7; not in pool; CT | The patch on the inferolateral body of k within 3 mm of the uncus of k+1 (8.6) | panjabi1991c only | As above |
| uncovertebral_incl_frontal_upper (UJIfu) | angle deg; C3-C7; not in pool; CT | PCA plane of the upper patch; its angle to frame F's XY plane (8.6) | panjabi1991c only | Values above 90 deg follow an undefined reference; how the sides were combined is unstated; store the normal |
| uncovertebral_incl_sag_upper (UJIsu) | angle deg; C3-C7; not in pool; CT | The same plane's angle to the YZ plane | panjabi1991c only | As above |
| uncovertebral_incl_frontal_lower (UJIfl) | angle deg; C2-C7; not in pool; CT | PCA plane of the lower patch, angle to XY | panjabi1991c only | As above |
| uncovertebral_incl_sag_lower (UJIsl) | angle deg; C2-C7; not in pool; CT | The same plane's angle to YZ | panjabi1991c only | As above |

### 11.6 The rib articulations

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| costovertebral_area_upper, pool key :mean (CVAu) | area mm2; T1-T12; not in pool (part of C3-L5); CT | Recipe R steps 2, 3 and 5: the vector area of the body-surface patch within 2 mm of the rib head, cranial half of the body (10.1) | panjabi1991t only | Needs a rib segmentation, which SPINEPS lacks; a proximity patch against a dry-bone outline has an unknown offset; "demifacet" is wrong at T1, T11 and T12 |
| costovertebral_area_lower, pool key :mean (CVAl) | area mm2; T1-T10; not in pool; CT | As above, caudal half; at T11 and T12 store absent as a state (10.1) | panjabi1991t only | As above; zero-mean noise would misstate an anatomical absence |
| costovertebral_area (CVA) | area mm2; T1-T12; not in pool (no spread); CT | The mean upper plus the mean lower area (10.1) | panjabi1991t only | Per side for one vertebra, not "per rib" as mnemonics.py says |
| costotransverse_area, pool key :mean (CTA) | area mm2; T1-T11; not in pool; CT | Recipe R step 4: the patch of label 43 or 44 within 2 mm of the rib; T12 absent as a state (10.2) | panjabi1991t only | As CVAu; the right-side SEMs at T8 and T10 are doubtful |
| rib_articulation_area (CVA + CTA) | area mm2; T1-T12; not in pool (no spread); CT | CVA plus the side mean of CTA (10.2) | panjabi1991t only | Per side for one vertebra, not per rib |

### 11.7 The facets

| Key | Kind, levels, pool | Mask algorithm | Same definition | Known biases |
|---|---|---|---|---|
| facet_w_sup, pool facet_w_sup:mean (FCWs) | length mm; C2-L5; pool; mask | Recipe J (label 45 or 46 of k within 3 mm of 47 or 48 of k-1); the patch's extent along u (8.1) | panjabi1993f only | mnemonics.py's extent along the vertebra's axes is foreshortened by about sin T; an extent of the whole process measures the process; about one voxel of partial volume; C2 needs C1 in the mask |
| facet_w_inf, pool facet_w_inf:mean (FCWi) | length mm; C2-L5; pool; mask | Recipe J (47 or 48 of k against 45 or 46 of k+1); extent along u | panjabi1993f only | As above; L5 needs the sacrum (label 26) |
| facet_h_sup, pool facet_h_sup:mean (FCHs) | length mm; C2-L5; pool; mask | Recipe J; extent along v (8.1) | panjabi1993f only | The axis-extent reading of mnemonics.py makes FCH read low; partial volume |
| facet_h_inf, pool facet_h_inf:mean (FCHi) | length mm; C2-L5; pool; mask | As above, inferior facet | panjabi1993f only | As above |
| facet_area_sup, pool facet_area_sup:mean (FCAs) | area mm2; C2-L5; pool; mask | Recipe J; the vector area of the patch (8.2) | panjabi1993f only | A scalar mesh area of a curved lumbar facet reads high; the ellipse on FCW and FCH reads a median 17% high (8.2) |
| facet_area_inf, pool facet_area_inf:mean (FCAi) | area mm2; C2-L5; pool; mask | As above, inferior facet | panjabi1993f only | As above |
| interfacet_w_sup (IFWs) | length mm; C2-L5; pool; mask and AP | The distance between the left and right superior facet centroids (8.3) | panjabi1993f; mnemonics.py's text | Needs both neighbours; 3D distance or X component is unstated, within about 1 mm (panjabi1993f note); masharawi2021 SIFW and yadav2020 IFD join other points (6.4); check that IFWi of k matches IFWs of k+1 (8.3) |
| interfacet_w_inf (IFWi) | length mm; C2-L5; pool; mask and AP | The same for the inferior centroids | As above | As above |
| interfacet_h, pool interfacet_h:mean (IFH) | length mm; C2-L5; pool; mask and lateral | Per side, the distance between the superior and inferior facet centroids (8.3) | panjabi1993f | Whether Panjabi took the 3D distance or its Y component is unstated; for lumbar IFH the centroids also differ in Z, so the two readings differ (panjabi1993f note); store both |
| facet_trans_sup, pool facet_trans_sup:mean (Ts) | angle deg; C2-L5; pool; mask | Recipe J normal, oriented up and back; T = arccos(abs(n_y)) (8.4) | panjabi1993f only | Scanner or principal-axes frames tilt T; the convex and concave sides of one joint differ (inferior L4 against superior L5) |
| facet_trans_inf, pool facet_trans_inf:mean (Ti) | angle deg; C2-L5; pool; mask | As above, inferior facet | panjabi1993f only | As above |
| facet_sag_sup, pool facet_sag_sup:mean (Ss), mirrored | angle deg; C2-L5; pool; mask | s = arccos(n_lat); compare 180 - s for a hypothesis at C2, C3 or C4 superior; apply the branch in the likelihood, not in the extractor (8.4) | panjabi1993f only | The 0-180 branch; an axial-slice trace (masharawi2021 TFA) falls short of the acute angle by 0.1-1.8 deg in the lumbar and thoracic spine, 1.5-6.3 deg at C3-C7 and 15-21 deg at C2 (8.4) |
| facet_sag_inf, pool facet_sag_inf:mean (Si), mirrored | angle deg; C2-L5; pool; mask | As above; 180 - s for C2 and C3 inferior | panjabi1993f only | As above |
| facet_card_x_sup (CAXs) | angle deg; C2-L5; not in pool (no spread); mask | CAX = -arccos(n_y); store only (8.4) | panjabi1993f only | CAX = -T exactly in 87 of 92 cells and within 0.1 deg in 91; the one exception, superior left T1, is a misprint (panjabi1993f note, CAX; 8.4); never a second feature |
| facet_card_x_inf (CAXi) | angle deg; C2-L5; not in pool; mask | As above | panjabi1993f only | As above |
| facet_card_y_sup (CAYs), mirrored | angle deg; C2-L5; not in pool; mask | CAY = atan2(-n_x, -n_z); store; enter only its sign, the facing, as a categorical feature (8.4) | panjabi1993f only | Its magnitude repeats T and S |
| facet_card_y_inf (CAYi), mirrored | angle deg; C2-L5; not in pool; mask | As above | panjabi1993f only | As above |

### 11.8 Corrections the generator's own text needs

- spinous_length: mnemonics.py defines SPL from the canal's posterior wall, and measures.py's comment says the same. The lumbar and thoracic papers start it at the upper end-plate centre, the frame's origin (panjabi1992 p. 302; panjabi1991t p. 893). The cervical text starts it at the body centroid while its Fig 1 draws the end-plate centre (panjabi1991c p. 866, p. 862; section 9.1). The archive's body-centroid start matches the cervical text; for T1 to L5 it is the wrong start, about half a body height from the end-plate centre (panjabi1991c note; 9.1).
- costovertebral_area_upper and costovertebral_area_lower: "demifacet" holds only at T2 to T10. costovertebral_area and rib_articulation_area are per side for one vertebra, not per rib (section 10).
- endplate_incl and endplate_lower_incl: the lumbar L1 to L5 rows reprint the cervical C3 to C7 rows, mean and SEM, in the papers themselves, the cervical most probably being the original; this part recommended leaving both out of the pool by one exclusion list that measures.pool, measures.left_out and measures.select all read, and the owner chose on 2026-10-29 to keep all 32 as printed (section 3.5; [panjabi-endplate-inclination.md](../../panjabi-endplate-inclination.md), section 3).
- h_post: the ap regime takes a measure that an AP view does not show (schwingcheck/measures.py, REGIMES; section 3.3).
- SPINEPS_MAPPING.md calls Panjabi's spines embalmed; they were fresh autopsy specimens, boiled, bleached and cleaned to dry bone (panjabi1992 p. 299; panjabi1991t p. 888; panjabi1992 note).
- pedicle_w, pedicle_h, pedicle_area: mnemonics.py calls them the smallest diameters and the area at its narrowest; the papers give the pedicle section with no isthmus claim (panjabi1992 p. 299, p. 301; panjabi1992 note, generator section).

### 11.9 Features the set supports that the generator lacks (Inference)

| Feature | Where | Why it helps |
|---|---|---|
| Anterior over posterior body height | 3.3 | Free of magnification. Every series has L5 alone 10% or more taller in front |
| Disc heights, anterior, middle and posterior | 5 | The middle height peaks at L3/L4 to L4/L5 and falls at L5/S1; a shape along the sequence, not one level |
| Canal shape (SCW / SCD; trefoil lobes) | 6.2, 6.4 | Trefoil at L4-L5 against oval at L1-L2 |
| Lateral recess depth; IFD and SIFW | 6.4 | Steps at L4/L5 of about 1 SD or more |
| Foramen height (two instances) | 6.4 | Lowest at L5/S1; the L4/5 to L5/S1 drop is 1.6-1.7 SD in bach2019 |
| Pedicle height over width | 7.3 | Free of size and magnification; T1 near round, mid-thorax tall |
| Laminar inclination and interlaminar angle | 9.4 | The steadiest lumbar gradient in abbas2021 |
| Spinous process angle; gilad1985's e, f, alpha and L | 9.5 | The thoracic SPA above 50 deg at T5-T8; lateral-film measures |
| Facet facing (sign of CAY) | 8.4 | A categorical state from the normal already stored |
| TPW / EPWu and SPL / EPDu | 9.1, 9.2 | Ratios a single view gives without magnification |
| Rib states: rib present, lower facet, costotransverse facet, lowest-rib length | 10.4 | The only T10/T11/T12 evidence that does not change smoothly |
| End-plate concavity | 4 | The caudal plate is deeper than the cranial plate across every lumbar disc, an orientation check; inferior middle depth 1.46 to 2.96 mm from L1 to L5 (vanderhouwen2009 Fig 2 p. 37) |
| Disc wedge angle (two instances) | 5 | L5-S1 largest, about 15 deg supine, then L4-L5, overlapping within one SD (vanderhouwen2009 Fig 3 p. 39) |
| Transverse over sagittal rim-chord ratio | 3.1, 4 | About 1.29 to 1.36 at T12 to L3 against 1.52 to 1.67 at L4 inferior to L5 inferior (Inference in the vanderhouwen2009 note, from Fig 2); rim-to-rim chords, not poolable with Panjabi's EPW/EPD |
| Disc anterior over posterior height (two instances) | 5 | bach2019 1.4 to 1.8 at T12/L1 to L4/5 and 2.2 to 2.3 at L5/S1 (computed from Table 6 p. e113); shin2024 1.62 to 1.90 and 2.83 (its note, from Table 2 p. 3); ratios of means |
| Pedicle ellipse tilt and isthmus minor axis | 7, 7.1, 7.3 | Tilt -2.4 to 7.5 deg at L1-L3, 31 to 34 at L4, 50 to 55 at L5 on coaxial views (robertson2000 Table 1 p. 711); makino2012's CI on CT sections (7.3) |
| Body ACH/PCH; pedicle TPD/SPD | 3.3, 7.3 | duman2026, T11 to L2 (Tables 1 and 2 pp. 7 to 8); both size-free |
| CT attenuation (HU), not a level feature | 3 | Order L1 > L2 > L5 > L3 > L4, but adjacent gaps of 1.5 to 9.2 HU sit against SDs of 8.4 to 30.4 HU (frontphys2026 Tables 3 to 6 pp. 5 to 7; its note, instruction 9). At most a weak within-patient tie-breaker, on non-contrast CT only |

## 12. What the set does not give

- No paper measured a segmentation mask or fluoroscopy. Every mask recipe and every fluoroscopy statement in this part is Inference, and no definition offset between a mask and a paper has been measured.
- Panjabi prints only level means and SEMs of 12 pooled spines (8 men, 4 women). No per-spine value exists, so no covariance between measures and no coefficient of size, sex, age or stature can be taken from the generator's own source (schwingcheck/README.md, "What they can and cannot do").
- Panjabi has no S1 and no sacrum (panjabi1991t p. 888). The set's S1 values come from a few lumbar series only: the L5/S1 disc and foramen, the S1 lateral recess and IFD, the S1 end-plate concavity and the S1 pedicles. No generator key reaches L5/S1 from the S1 side.
- None of the four papers says where in the vertebra the canal sections and pedicle sections were taken (6.1, 7.1). Their section positions are assumptions in every recipe.
- Facet measures come only from panjabi1993f in 3D, and from lumbar axial-slice traces in two living CT series by other definitions (8). Nothing checks Panjabi's facet values in another sample.
- Radiographic magnification was measured only by eisenstein1977: 1.14 AP and 1.23 lateral at 110 cm (eisenstein1977 p. 175). Every other film correction in this part is that paper's factor or M = SID / (SID - OFD) with distances the papers mostly do not give (2.5).
- The set has no laminar thickness and no laminar height or length (9.4). It has no distribution of rib length, no laterality of rib anomalies, and no rib facet measured on CT (10).
- No paper reports per-person facet tropism, so its spread is not known (8.5).
- The steps at C7/T1 and T12/L1 compare values from two different Panjabi papers. The spines are the same, but the tables were made separately. Check each such step against a single series that spans the junction: SPL at T12/L1 does not reproduce in tan2004 or busscher2010, while TPW at T12/L1 does (9.1, 9.2).
- Panjabi's lumbar end-plate inclination rows carry the same 20 numbers as his cervical C3 to C7 rows, one set printed twice and most probably cervical (3.5), so the set most probably has no lumbar inclination of his; the owner chose on 2026-10-29 to keep both in the pool as printed. The thoracic CTA has two doubtful SEMs (10.2). gilad1985's alpha does not recompute at C2 and L2 (9.5). Each is a source error to fix or fence off before any likelihood uses those cells.
