# Irie 2021: Micro-computed tomography analysis of the lumbar pedicle wall

Source: thread "Reread every paper for clinical detail", project symphony_4, 2026-10-28.

Status: drafted by one reader from the whole PDF; not yet checked against the PDF by a second reader, because the check stopped at the session's usage limit on 2026-10-28 (HANDOFF.md says how to finish it).


Citation as printed on p. 1 (PDF 1): Tomoyo Y. Irie, Tohru Irie, Alejandro A. Espinoza Orias, Kazuyuki Segami, Norimasa Iwasaki, Howard S. An, Nozomu Inoue. "Micro-computed tomography analysis of the lumbar pedicle wall." PLoS ONE 16(7): e0253019, 2021. https://doi.org/10.1371/journal.pone.0253019. Received 8 December 2020, accepted 26 May 2021, published 8 July 2021; editor Dean Chou. Rush University Medical Center (Chicago) and Hokkaido University (Sapporo). Funded by NIH-NCCIH grant 1R01-AT006692. Data deposited at figshare, doi 10.6084/m9.figshare.14731929. PLOS ONE numbers by e-locator; the page footer prints "n / 12" and printed page n is PDF page n.

Copy read: PMC open-access Cloud Service (pmc-oa-opendata), PMC8266093.1, fetched 2026-10-28 by this thread; sha256 begins 26190d026c80bf7d. A born-digital PDF; every value below was read from the page images (the text layer agrees).

Key mismatch: the thread's key for this file is "otsuki2021", but the paper's first author is Irie (no author named Otsuki). The note is filed under the key it was given; see Gaps.

## What the paper is

- Design: cadaveric micro-CT study of the wall of the lumbar pedicle at its isthmus, measuring (a) isthmus dimensions and wall thicknesses and (b) the bone area fraction (BAF, bone pixels per ROI pixels) in four angular sectors of the wall, by side and level. p. 1 (PDF 1), pp. 2-5 (PDF 2-5).
- Specimens: six fresh-frozen lumbar spines, L1 to L5, 3 men and 3 women, from an accredited US tissue bank (Science Care, Phoenix, Arizona); mean age 60.2 +/- 7.2 years, range 50 to 67; all free of spine-related conditions and spine surgery. Ethnicity not stated. p. 2 (PDF 2), Table 1.
- Donors (Table 1, p. 2, PDF 2): 1 F 54 y, 40.8 kg, 162.6 cm, BMI 15.4 (COPD); 2 F 50 y, 108.0 kg, 160.0 cm, BMI 42.2 (heart attack); 3 F 66 y, 65.3 kg, 165.1 cm, BMI 24.0 (cardiac arrest); 4 M 67 y, 52.2 kg, 175.3 cm, BMI 17.0 (atherosclerotic heart disease); 5 M 58 y, 127.5 kg, 193.0 cm, BMI 34.2 (chronic heart failure); 6 M 66 y, 67.6 kg, 177.8 cm, BMI 21.4 (cardiac arrest). Body size spans BMI 15.4 to 42.2 and height 160 to 193 cm.
- Denominator: 60 pedicles = 6 spines x 5 levels (L1-L5) x left and right. Each pedicle was cut out at the pedicle-vertebral body junction and the pedicle-lamina junction with a low-speed diamond wafer saw (Buehler IsoMet), keeping the tissue and ligaments around it. p. 2 (PDF 2).
- Storage: -20 deg C, thawed slowly at room temperature, removed from the freezer one day before testing. p. 2 (PDF 2). IRB exempt (cadaveric tissue).
- Modality and instrument: Scanco muCT 50; specimen in distilled water in a 35 mm inner-diameter tube held by gauze, sealed with paraffin film; 55 kV, 145 microamperes, voxel 34.4 micrometres, matrix 1024 x 1024; axial DICOM imported into Mimics (Materialise) for reslicing in arbitrary planes. pp. 2-3 (PDF 2-3).
- Dimension measures in ImageJ; BAF by a custom Visual C++ routine; vertebral body attenuation (HU) in ImageJ. pp. 4-5 (PDF 4-5).
- A clinical CT of the same specimens is shown for comparison only (Fig 4, p. 10, PDF 10): Siemens Volume Zoom, 120 kV, 100 mA, FOV 272 mm, matrix 512 x 512, slices 0.625 mm thick at 1.0 mm increments, with no gap stated between them. Inference: in-plane pixel 272/512 = 0.53 mm, matching the "about 0.5 mm" the Discussion gives for clinical CT (p. 9, PDF 9).
- Level identification: not described. Specimens were supplied as L1-L5 segments; the paper does not say how L1 or L5 was confirmed, and says nothing of rib count, transitional segments or lumbar count. Inclusion and exclusion beyond "free from spine-related conditions or spine surgery" are not given.
- Statistics: paired t-test for left against right at each level; repeated-measures ANOVA with Tukey post hoc for region and level effects; Pearson correlation of BAF with vertebral body HU; mean +/- SD; alpha 0.05. p. 5 (PDF 5). No sample-size calculation; no reliability study.

## Anomalies, numbering and transitional segments

The paper says nothing about transitional vertebrae, sacralisation, lumbarisation, L6, T13, rib counts, cervical ribs or block vertebrae; it gives no prevalence and no numbering method. Levels are taken as L1 to L5 as supplied (p. 2, PDF 2).

## Measures, each as a recipe

### Pedicle axis and isthmus section (the frame for every other measure)

- Definition: the pedicle axis is the line through two approximate centre points of cross-sections at the anterior third and the posterior third of the pedicle (Fig 1, p. 3, PDF 3). These seeds drive an algorithm that finds the final cross-sections as planes perpendicular to the axis. The section is treated as an ellipse with a minor and a major axis. The isthmus is the cross-section with the shortest minor axis ("in transverse orientation"), after Sugisaki et al. (ref. 18). The major axis of the isthmus is its longest diameter. p. 3 (PDF 3).
- Inner boundary: the boundary between cortical wall and medullary cavity is a continuous cortical wall adjacent to the cavity, judged by looking at a few slices before and after the isthmus (ref. 16). p. 3 (PDF 3).
- From a 3D CT instance mask: Inference: SPINEPS gives no separate pedicle label; take the posterior-element voxels between the posterior body wall and the branching of the transverse and articular processes on one side. Take centroids of slices at the anterior and posterior thirds of that bridge, join them as the axis, reslice perpendicular to it in small steps, fit an ellipse (second moments) to each section, and take the section whose minor axis is shortest. The paper's axis is a two-point line, not a principal axis; record which was used.
- From a radiograph alone: not possible as defined (needs a true section). Inference: on an AP view the pedicle oval is an oblique projection of the isthmus tube; on a lateral view the narrowest craniocaudal neck of the superimposed pedicles approximates the major axis only where the pedicle is not tilted.

### Transverse diameter (minor axis of the isthmus)

- Definition: the length on the minor axis of the isthmus section, outer surface to outer surface (Fig 2A, horizontal yellow dotted line, p. 4, PDF 4). Measured in ImageJ. p. 4 (PDF 4); Fig 2 caption.
- Values (Table 2, p. 6, PDF 6), mm, L1 to L5: 7.1 +/- 2.4, 7.3 +/- 2.4, 9.4 +/- 2.0, 10.6 +/- 0.8, 11.8 +/- 1.7; average 9.2 +/- 2.1.
- From a 3D CT instance mask: the minor-axis extent of the narrowest section above. Inference: equivalent to Zindrick's and Krag's isthmus width and close to Panjabi's PDW when that is taken at the narrowest point.
- From a radiograph alone: Inference: AP radiograph, the mediolateral width of the pedicle oval, divided by the magnification; it overstates the true section at L4-L5 where the pedicle converges steeply.
- Across levels: rises from L1 to L5 ("gradually", p. 5, PDF 5), nearly flat from L1 to L2 (7.1 to 7.3) and then steps up. Significant pairs (Table 2 footnotes, p. 6, PDF 6): L3 > L2 (p < 0.04); L4 > L1 (p < 0.03) and L2 (p < 0.05). No footnote marks L5 against any level. Adjacent pair separated: L2/L3 only.
- Sex, age, size, population: not analysed.
- Error: no repeatability given; between-specimen SD 0.8 to 2.4 mm; muCT voxel 34.4 micrometres.

### Longitudinal diameter (major axis of the isthmus)

- Definition: the length on the major axis, the longest diameter of the isthmus section (Fig 2A, vertical yellow dotted line). p. 3-4 (PDF 3-4).
- Values (Table 2), mm, L1 to L5: 17.0 +/- 2.7, 15.8 +/- 1.7, 15.8 +/- 1.7, 18.8 +/- 1.6, 24.2 +/- 2.7; average 18.3 +/- 3.5.
- From a 3D CT instance mask: the longest diameter of the isthmus section (Inference: the major-axis extent; it need not be vertical).
- From a radiograph alone: Inference: lateral radiograph, the craniocaudal height of the pedicle neck (both sides superimposed), divided by magnification.
- Across levels: smallest at L2-L3, rises from L2 to L5 (p. 5, PDF 5); L1 is taller than L2-L3. Significant: L4 > L2 (p < 0.02) and L3 (p = 0.0001); L5 > L1 (p < 0.02), L2 (p < 0.003), L3 (p < 0.001). Adjacent pair separated: L3/L4. L4/L5 is not marked although 18.8 against 24.2.
- Ratio (Inference, ratio of the printed means): longitudinal/transverse 2.39, 2.16, 1.68, 1.77, 2.05 from L1 to L5; it falls to L3 and rises again at L5 (see Gaps for the conflict with Panjabi).
- Error: no repeatability; SD 1.6 to 2.7 mm.

### Medial, lateral, cranial and caudal wall thickness

- Definition: medial and lateral wall thickness measured on the minor axis, cranial and caudal on the major axis, each from the medullary-cavity boundary (red line) to the outer surface (Fig 2A red arrows). p. 4 (PDF 4). Inference: this is the thickness of everything outside the cavity on that axis, including porous, shell-like bone, not cortical thickness in the strict sense; the cranial and caudal "walls" of about 3 mm are visibly porous in Fig 2.
- Values (Table 2, p. 6, PDF 6), mm, L1 / L2 / L3 / L4 / L5 / average:
  - medial 0.8 +/- 0.2 / 0.8 +/- 0.2 / 0.8 +/- 0.2 / 1.3 +/- 0.5 / 1.3 +/- 0.6 / 1.0 +/- 0.3
  - lateral 0.6 +/- 0.3 / 0.7 +/- 0.2 / 0.9 +/- 0.4 / 1.1 +/- 0.5 / 1.7 +/- 0.5 / 1.0 +/- 0.5
  - cranial 3.1 +/- 0.7 / 3.5 +/- 0.9 / 3.9 +/- 0.8 / 3.2 +/- 0.8 / 4.0 +/- 1.7 / 3.5 +/- 0.4
  - caudal 2.6 +/- 0.6 / 3.2 +/- 0.5 / 2.8 +/- 0.9 / 2.5 +/- 1.1 / 2.9 +/- 1.1 / 2.8 +/- 0.3
- From a 3D CT instance mask: not possible from a binary outer mask; needs the medullary-cavity boundary, which clinical CT at about 0.5 mm cannot draw reliably (p. 9-10, PDF 9-10; Fig 4). Inference.
- From a radiograph alone: not possible. Inference.
- Across levels: lateral rises steadily L1 to L5, L5 > L1 (p < 0.03), L2 (p < 0.008), L3 (p < 0.05). Medial tends higher at L4-L5, not significant. Cranial and caudal show no gradual rise; cranial L3 > L1 (p < 0.02, footnote printed as "superior wall"). p. 5 (PDF 5), Table 2.
- Between walls: cranial and caudal thicker than lateral and medial "at all levels except L5" (p. 5, PDF 5); footnotes a to g give the tests (e.g. L2 caudal against lateral p < 0.0001, against medial p < 0.007). No medial-lateral difference at any level (p. 5, PDF 5).
- Error: no repeatability; SD 0.2 to 1.7 mm on walls of 0.6 to 4 mm.

### Whole cross-section area and medullary cavity area at the isthmus

- Definition: the area of the entire isthmus section and of the cavity inside the red line (Fig 2A). p. 4-5 (PDF 4-5).
- Values (Table 2), mm2, L1 to L5: whole 95.7 +/- 43.8, 92.5 +/- 35.7, 113.7 +/- 26.4, 152.4 +/- 13.6, 204.2 +/- 37.1 (average 131.7 +/- 47.0); cavity 53.2 +/- 28.3, 43.3 +/- 18.4, 56.3 +/- 19.4, 83.2 +/- 12.8, 118.7 +/- 25.7 (average 70.9 +/- 30.5).
- Across levels: both smallest at L2 and rise from L2 to L5 (p. 5, PDF 5). Whole: L4 > L2 (p < 0.02) and L3 (p < 0.04); L5 > L1 (p < 0.02), L2 (p < 0.009), L3 (p < 0.04). Cavity: L4 > L2 (p < 0.04); L5 > L1 (p < 0.04), L2 (p < 0.02). Adjacent pair separated: L3/L4 (whole area).
- Inference (arithmetic on the means): cavity/whole = 0.56, 0.47, 0.50, 0.55, 0.58 from L1 to L5, so the wall is roughly half the isthmus area. An ellipse on the two diameters, pi/4 x minor x major, gives 94.8, 90.6, 116.6, 156.5, 224.3 mm2, within 3 percent of the measured whole area at L1-L4 and 10 percent high at L5.
- From a 3D CT instance mask: whole area is the pixel area of the isthmus section of the mask (Inference); cavity area is not available from a mask.
- From a radiograph alone: not possible.

### Bone area fraction (BAF) of the wall by region

- Definition: on the isthmus section, the image is binarised at threshold = (cortical bone grey level - background grey level) x 0.5, described as "50% of offset cortical bone gray level"; BAF = bone pixels / all pixels in the ROI x 100 (100 percent all bone, 0 percent none). p. 5 (PDF 5). Inference: the printed formula omits the background offset; a half-way threshold between background and cortex is presumably meant.
- ROIs: four 30-deg sectors, measured from the cranial direction, the 12 o'clock position set by the major axis: cranial +/-15 deg, medial 75-105 deg, caudal 165-195 deg, lateral 255-285 deg (Fig 2B, p. 4, PDF 4). The 30-deg sectors were chosen to avoid the transitional areas between regions. Fig 2B shows each ROI running from the cavity boundary to the outer surface (Inference from the figure; the text does not state the radial extent). Together they cover 120 of 360 deg of the wall.
- Side: left and right were symmetric with no significant difference at any level, so their mean was used. p. 5 (PDF 5). Inference: n = 6 per level and region.
- Values by level (Table 4, p. 7, PDF 7), percent, lateral / medial / cranial / caudal / average of four:
  - L1 52.2 +/- 22.7 / 98.6 +/- 2.3 / 78.1 +/- 10.0 / 88.0 +/- 10.6 / 79.2 +/- 11.4
  - L2 64.0 +/- 20.9 / 98.9 +/- 2.7 / 84.1 +/- 12.2 / 89.1 +/- 6.0 / 84.0 +/- 10.5
  - L3 58.7 +/- 22.4 / 97.9 +/- 3.5 / 90.0 +/- 5.9 / 93.0 +/- 5.0 / 84.9 +/- 9.2
  - L4 55.7 +/- 21.7 / 95.1 +/- 7.6 / 86.6 +/- 13.7 / 66.7 +/- 26.0 / 76.0 +/- 17.2
  - L5 63.1 +/- 23.8 / 96.5 +/- 4.1 / 81.1 +/- 14.3 / 53.4 +/- 17.0 / 73.5 +/- 14.8
- Overall: lateral 58.8 +/- 22.3, medial 97.4 +/- 4.1, cranial 84.0 +/- 11.2, caudal 78.0 +/- 12.9 (p. 5, PDF 5). Abstract: medial median 99.8 percent, range 95.9-100 (p. 1, PDF 1).
- By donor (Table 3, p. 6, PDF 6): lateral 46.4 (donor 5, 58 M, BMI 34.2) to 74.3 (donor 4, 67 M, BMI 17.0); medial 93.0 to 99.8; cranial 79.7 to 94.6; caudal 63.7 to 85.5; donor averages 72.1 to 87.8.
- Region contrasts (p. 6, PDF 6; Fig 3, p. 8, PDF 8): lateral lowest of the four at L1, L2 and L3, and below medial at L4 (p < 0.0004) and L5 (p < 0.002). Medial highest at every level except L4, where medial against cranial was p = 0.26 (medial against lateral p < 0.004 in the text, p < 0.0004 in Fig 3 g; medial against caudal p < 0.03). Lateral against caudal significant at L1 (p < 0.002), L2 (p < 0.02), L3 (p < 0.0006), not at L4 or L5. Caudal below cranial at L5 (p < 0.0006). Medial above 95 percent at all levels; lateral below 64 percent at all levels; caudal below 67 percent at L4 and L5.
- Level contrasts within a region (p. 7, PDF 7; Table 4 footnotes): cranial L1 < L3 (p < 0.04); caudal L4 < L3 (p < 0.04); caudal L5 < L1 (p < 0.002), L2 (p < 0.0001), L3 (p < 0.0001); average L5 < L2 (p < 0.04) and L3 (p < 0.02). Caudal BAF tended above cranial at L1 (p = 0.08) and was significantly above it with L1 and L2 combined (p < 0.04) (p. 9, PDF 9).
- From a 3D CT instance mask: not possible. A binary mask holds no porosity, and clinical CT at about 0.5 mm voxels cannot show trabeculae inside the wall (p. 9, PDF 9; Fig 4, p. 10, PDF 10). The authors expect the higher porosity to appear only as lower CT values through partial volume (p. 9-10, PDF 9-10).
- From a radiograph alone: not possible.
- Sex, age, size, population: not analysed; six donors only.
- Error: no repeatability; SD up to 26 percentage points (caudal L4); the 30-deg sectors are arbitrary (p. 10, PDF 10).

### Vertebral body attenuation (HU)

- Definition: the largest possible elliptical ROI in each vertebral body on every axial CT slice of L1-L5, excluding osseous abnormalities and voids such as vascular channels, after Schreiber et al. (ref. 19); ImageJ. p. 5 (PDF 5). Inference: measured on the clinical CT of the intact spines, since the micro-CT held only the cut-out pedicles; the paper does not say which scan.
- Result: two donors (a 66-year-old man and a 50-year-old woman) had L1 attenuation below 110 HU, the Pickhardt cut-off with high specificity for osteoporosis (ref. 20); no HU values are printed. No correlation between average pedicle-wall BAF and body HU (n = 30, r = 0.06, p = 0.76). p. 5 (PDF 5). Inference: by Table 1 these are donors 6 and 2.
- From a 3D CT instance mask: Inference: the mean HU inside the body subregion of the instance, eroded away from the cortex, on calibrated CT; not from radiographs.

## Level by level and at the junctions

The paper covers L1 to L5 only; it says nothing of T12/L1 or L5/S1 as junctions.

- L1: narrow (7.1 mm) and tall (17.0 mm) isthmus; thinnest lateral wall (0.6 mm); lowest lateral BAF (52.2 percent); cranial BAF lowest of the cranial values (78.1, below L3); caudal above cranial in tendency (p = 0.08). Table 2, Table 4; p. 9 (PDF 9).
- L2: smallest isthmus (whole area 92.5 mm2, cavity 43.3 mm2, major axis 15.8 mm); transverse 7.3 mm, barely above L1; highest lateral BAF (64.0) and caudal BAF still high (89.1). Table 2, Table 4.
- L3: first clear widening (9.4 mm, above L2); major axis still 15.8 mm; thickest cranial wall of L1-L4 (3.9 mm); the highest cranial and caudal BAF (90.0, 93.0) and highest four-region average (84.9). Table 2, Table 4.
- L4: transverse 10.6 mm, major 18.8 mm (above L2 and L3); whole area 152.4 mm2 (above L2-L3); medial BAF lowest of its column (95.1) and not significantly above cranial; caudal BAF falls to 66.7 (below L3). Table 2, Table 4; p. 6 (PDF 6).
- L5: largest isthmus (11.8 x 24.2 mm, 204.2 mm2); lateral wall thickest (1.7 mm, numerically above the medial 1.3); caudal BAF lowest of any region at any level (53.4, below L1-L3) and below cranial; lowest four-region average (73.5). Table 2, Table 4. The authors relate the low caudal BAF at L4-L5 to the larger major axis: a taller ellipse has a larger area moment of inertia, so the caudal wall may carry less stress and adapt with less bone; the cranial wall transmits stress to the superior end plate. p. 9 (PDF 9).

## Measurement error and reliability

- No intra- or inter-observer study, no repeatability, no phantom. The only error figures are between-specimen SDs (Tables 2-4).
- Instrument: muCT 50 at 34.4 micrometre voxels (p. 3, PDF 3); clinical CT about 0.5 mm voxels at best (p. 9, PDF 9), 0.53 mm in-plane for the scanner in Fig 4 (Inference: 272 mm / 512).
- Threshold: a single half-way grey-level threshold per data set (p. 5, PDF 5); BAF depends on it (Inference).
- The inner wall boundary is drawn by judgement over a few slices around the isthmus (p. 3, PDF 3).
- Sample: six donors limit the power for the BAF-HU correlation and for level contrasts (p. 9, PDF 9).
- The "Average" column of Table 2 carries the SD of the five level means, not a pooled within-level SD (Inference: recomputed for transverse 2.05, longitudinal 3.51, whole area 47.0, cranial 0.40, matching 2.1, 3.5, 47.0, 0.4; lateral 0.44 against printed 0.5).

## Clinical pearls, indications and pitfalls

- Indication context: pedicle screw fixation of motion segments; penetration of the wall and screw loosening occur especially in osteoporosis (refs 1, 2); larger screws give better cortical purchase at the isthmus, which governs fixation strength (refs 3-7); cortical bone needs more insertion torque but enhances purchase (ref. 8). p. 2 (PDF 2).
- Lateral breach: lateral wall breach is the most common pedicle-screw failure in thoracolumbar fixation (refs 8-10, 12, 21). Redirecting a screw after a lateral breach cost 24.0 percent of mean pullout strength against correctly aligned screws (Goda et al., ref. 22). p. 7 (PDF 7).
- Why the lateral wall fails: not only thin (prior studies, refs 8-10, 13, 21) but porous: the lateral isthmus is shell-like or cancellous-like rather than cortical at every lumbar level, BAF under 64 percent. p. 7 (PDF 7), p. 11 (PDF 11). Inceoglu related the thick medial and thin lateral wall to loading: the lateral pedicle joins the transverse process, the medial the lamina (ref. 13). p. 9 (PDF 9).
- Medial wall: dense cortex above 95 percent BAF at all levels, within the range of long-bone cortex (tibia intracortical porosity 0.3-7.1 percent, radius 0.2-2.4 percent, Burghardt; tibia 8.8, radius 2.7 percent, Tsai). p. 8-9 (PDF 8-9).
- Caudal wall at L4 and L5: porous (under 67 percent), so the caudal wall joins the lateral as a breach-prone wall at the lower lumbar levels (abstract conclusion, p. 1, PDF 1). At L1-L2 the caudal half is the denser, as Lehman found in the thoracic pedicle (ref. 17). p. 9 (PDF 9).
- Bone density: pedicle-wall BAF did not track body HU (r = 0.06), which may support the idea that the pedicle wall and the cancellous body lose bone independently, one rationale for cortical bone trajectory screws (ref. 26); the sample is too small to settle it. p. 9 (PDF 9). Inference: a body HU screen (e.g. L1 below 110 HU) does not tell the state of the pedicle wall.
- Prior wall thicknesses quoted for comparison (p. 7-8, PDF 7-8): Inceoglu, L3 midportion, lateral 609 +/- 247 and medial 793 +/- 186 micrometres (direct); Mitra (CT), lateral 0.82, 0.55, 0.87, 0.60, 1.25 mm and medial 1.07, 1.15, 1.15, 1.37, 1.32 mm, L1 to L5; Li (CT), medial 1.4-2.3 mm in women and 1.5-2.2 mm in men, lateral 0.8-1.6 mm in women and 1.0-1.8 mm in men, increasing L1 to L5. The authors call their values comparable.
- Prior isthmus diameters: CT studies (refs 8, 11, 18) also found transverse and longitudinal isthmus diameters increasing at lower levels. p. 7 (PDF 7).
- Pitfall, clinical CT: the 34.4 micrometre muCT shows trabeculae within the wall; clinical CT at about 0.5 mm cannot, and wall characterisation on it is less accurate (Fig 4 caption, p. 10, PDF 10); porosity may show only as lower CT numbers by partial volume (p. 9-10, PDF 9-10).
- Pitfall, scope: only the isthmus was studied; cortical bone trajectory needs other parts of the pedicle (p. 9, PDF 9). The four 30-deg sectors leave the transitional areas between regions unmeasured (p. 10, PDF 10).

## Instructions for the autonomous anatomist

1. To find a lumbar pedicle isthmus in a CT instance, join the centroids of pedicle sections at its anterior and posterior thirds, reslice perpendicular to that line and take the section with the shortest minor axis (p. 3, PDF 3; Fig 1).
2. On that section read the minor (transverse) and major (longitudinal) diameters outer to outer; expect about 7.1, 7.3, 9.4, 10.6, 11.8 mm and 17.0, 15.8, 15.8, 18.8, 24.2 mm from L1 to L5 (Table 2, p. 6, PDF 6). Use relative steps along the chain, not absolute values, since six donors and SDs of 0.8-2.7 mm make single-instance values weak.
3. Use the transverse diameter for the L2/L3 boundary (the first significant step) and the major axis and section area for the L3/L4 boundary (Table 2 footnotes, p. 6, PDF 6). Do not expect this paper's data to separate L1 from L2 (7.1 against 7.3 mm wide) or L4 from L5 by significance; L5 is still the largest isthmus by every dimension.
4. Expect the isthmus area to dip at L2 and rise to L5 (92.5 to 204.2 mm2); an ellipse on the two diameters reproduces the area within about 3 percent at L1-L4 (Inference from Table 2, p. 6, PDF 6).
5. Do not compute wall thickness, medullary area or bone area fraction from a SPINEPS mask or from clinical CT at about 0.5 mm: walls of 0.6-1.7 mm span one to three voxels and their porosity is invisible (p. 9-10, PDF 9-10; Fig 4).
6. When the isthmus outline comes from intensities rather than a learned mask, expect the lateral wall (mean BAF 58.8 percent, as low as 46 percent in one donor) to read darker than the medial (97.4 percent), so a threshold can erode or break the lateral margin and under-read the transverse diameter by up to a voxel on that side (Inference from Table 3-4 and p. 9-10, PDF 9-10).
7. At L4 and L5 also expect a porous caudal wall (66.7 and 53.4 percent), so the lower margin of the pedicle may under-read in the same way, shortening the major axis (Inference from Table 4, p. 7, PDF 7).
8. Treat left and right pedicles of a level as one measurement pair: no side difference was found in BAF (p. 5, PDF 5); a large left-right difference in isthmus size suggests a segmentation fault, rotation or pathology (Inference).
9. Do not infer pedicle wall quality from body HU: they did not correlate (r = 0.06, n = 30; p. 5, PDF 5).
10. Report the reslice: an isthmus width taken on an axial slice of the vertebra rather than perpendicular to the pedicle axis reads wider where the pedicle converges (Inference; the paper defines the section perpendicular to the axis, p. 3, PDF 3).

## For bordercall's generator and classifier

(a) Anomaly priors: none. The paper gives no prevalence of any transitional or numbering anomaly.

(b) Measures:
- Pedicle width (Panjabi PDW) corresponds to the isthmus transverse diameter here, and pedicle height (PDH) to the longitudinal diameter, but the definitions differ: here the section is perpendicular to a two-point pedicle axis and the major axis is the longest diameter, not the vertical extent; Panjabi digitised the pedicle outline on dry bone. A mask extractor should take the narrowest section perpendicular to the pedicle axis and report both the minor axis and the vertical extent, so either definition can be matched.
- The definitions do not agree at L5. Here L5 is 11.8 mm wide and 24.2 mm tall, ratio about 2.0; Panjabi's L5 PDW is 18.6 mm and PDH/PDW about 1.0 (see the panjabi1992 note). Inference: a perpendicular section of the broad L5 pedicle, with its longest diameter possibly oblique, gives a narrower minor axis and a longer major axis than a dry-bone digitised outline. A mask value taken by this paper's recipe would be biased low in width and high in height against the generator's Panjabi draws at L5, and the ratio PDH/PDW would mislabel an L5 as an upper lumbar level. Choose one definition and calibrate it.
- Isthmus section area: here 95.7 to 204.2 mm2; Panjabi's PDA (by the panjabi1992 note) is about 87, 83, 94, 108, 151 mm2. Both dip at L2 and rise to L5; this paper runs larger at L4-L5. A mask-derived section area is a candidate addition, being robust (an area integrates the outline).
- Wall thicknesses, medullary area, BAF and body HU: not mask measures; leave them out of the generator.

(c) Measurement error: no reliability data. Use the between-specimen SDs as a floor on spread: transverse 0.8-2.4 mm, longitudinal 1.6-2.7 mm, area 13.6-43.8 mm2. Inference: on clinical CT at 0.5-0.6 mm voxels add about +/- 0.5 mm per wall from the mask boundary, more on the porous lateral wall and, at L4-L5, the caudal wall.

(d) Covariates: 3 men and 3 women, 50 to 67 years, BMI 15.4 to 42.2, height 160 to 193 cm, US tissue-bank donors, ethnicity unstated; no analysis by sex, age or size. Nothing usable for the size factor beyond the donor table.

## Gaps and conflicts

- Key and author: the file key is "otsuki2021" but the paper is Irie TY et al. 2021, PLoS ONE 16(7): e0253019; no Otsuki appears among the authors. Check whether a different Otsuki 2021 paper was intended.
- How levels were identified, and whether any spine had a transitional segment, is not reported.
- Table 2's n per level is not stated (6 side-averaged or 12 pedicles); the text says the dimensions "from each donor" are in Table 2, which is by level (p. 5, PDF 5).
- "Cranial and caudal thicker than lateral and medial at all levels except L5" (p. 5, PDF 5) conflicts with the footnotes: at L4 only cranial carries a mark (g); caudal L4 (2.5 +/- 1.1) has none.
- The medial-against-lateral BAF p-value at L4 is p < 0.004 in the text (p. 6, PDF 6) and p < 0.0004 in Fig 3 g (p. 8, PDF 8) and in the text's own first sentence.
- "Lateral less than 64 percent at all levels" (p. 1 and p. 6) against L2 lateral 64.0 in Table 4; the summary says "less than 67%" (p. 11, PDF 11).
- "Medial highest at all levels except L4": numerically medial is the highest at L4 too (95.1); the exception is about significance (p = 0.26 against cranial).
- At L5 the lateral wall (1.7 mm) is thicker than the medial (1.3 mm), against the general medial-thicker rule and Mitra's L5 (1.25 lateral, 1.32 medial); the text reports no medial-lateral difference at any level.
- The threshold formula lacks a background offset as printed (p. 5, PDF 5).
- The clinical CT in Fig 4 has 0.625 mm slices at 1.0 mm increment yet says "no spacing" (p. 10, PDF 10).
- Ref. 18 (Sugisaki 2009, Spine) is printed with volume 15; Spine 2009 is volume 34 (Inference from memory).
- The radial extent of the BAF ROIs and the centre of the sectors are shown only in Fig 2B, not stated.
- Against Panjabi 1992 (Inference, from the panjabi1992 note): this paper's L5 transverse 11.8 mm is far below Panjabi's 18.6 mm and nearer Berry 10.7, Scoles 9.7 and Krag 13.8; the shape ratio rises again at L5 here but falls to 1.0 in Panjabi; Panjabi separated L4/L5 by pedicle size, this paper does not (n = 6).
- Against Krag 1988 (Inference, from the krag1988 note): Krag found CT pedicle widths read small from partial volume on 4 mm slices; this paper's muCT at 34.4 micrometres carries no such bias, so its widths are not directly comparable with widths from clinical CT.
