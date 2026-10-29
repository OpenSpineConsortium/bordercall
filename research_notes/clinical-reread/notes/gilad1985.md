# Gilad 1985: Sagittal evaluation of elemental geometrical dimensions of human vertebrae

Source: thread "Reread every paper for clinical detail", project symphony_4, 2026-10-28.

Citation as printed: Issachar Gilad and Moshe Nissan (Technion-Israel Institute of Technology, Haifa). Sagittal evaluation of elemental geometrical dimensions of human vertebrae. J. Anat. (1985), 143, 115-120. With 1 figure. Accepted 13 March 1985. No issue number is printed.

Copy read: greg's upload of 2026-10-28 17:00 UTC, filed as project files literature/synthetic_spine/gilad1985.pdf; sha256 begins f15c058eaf36fa62. Six pages, journal pp. 115-120 = PDF pages 1-6. Every number below was read from the page images; the skeptic re-read every page and re-rendered both tables at 220 dpi and Fig. 1 and the lumbar paragraph at 300-600 dpi to confirm each value, label and subscript.

## What the paper is

- Design: cross-sectional radiographic anthropometry. Each vertebra is reduced to a two-dimensional "simplified model" in the mid-sagittal plane, fixed by five bony reference points marked on a lateral film before any measuring; seven distances (a, b, c, d, e, f, k) are measured with calipers and two more (the angle alpha and the overall length L) are computed, the "nine dimensions" of the summary; two averages (VBH, VBW) are derived as well. p. 117 (PDF 3), p. 120 (PDF 6).
- Purpose: a data base for geometrical and biomechanical models and ergonomics, not a clinical study. The full work, with distributions, correlations of the dimensions with subjects' height, weight and age, and intervertebral spacings, is a Technion technical report (Gilad & Nissan 1982, HEIS 82-14/A & B), not this paper. p. 115 (PDF 1), refs p. 120 (PDF 6).
- Population: healthy working men aged 20 to 38 years (mean 26.8), mean stature 174.7 cm (no SD, no weight given), employees of a major transportation cooperative that ran general check-ups every few years. Living subjects, men only. Country not stated; Inference: Israel, since both authors are at the Technion, Haifa. Ethnicity not stated. p. 115 (PDF 1).
- Denominators: radiographs of 141 cervical spines and 157 lumbar spines (p. 115, PDF 1); the summary says radiographs of 157 normal healthy adult men (p. 120, PDF 6). Whether the 141 cervical films are a subset of the 157 men is not said. Measurements per level, n (Table 1 and Table 2, p. 118, PDF 4): C2 130, C3 141, C4 141, C5 141, C6 140, C7 126; L1 154, L2 157, L3 157, L4 157, L5 156. Inference (sum): 819 cervical and 781 lumbar vertebra-measurements, 1,600 in all, from at most 157 men.
- Exclusions: no subject with bone tissue degeneration or any other known disease or abnormality; the films were selected so that only clearly defined vertebrae were examined. p. 115 (PDF 1).
- Cervical film: standing, neutral relaxed posture after Meschan (1968), facing a fixed point so the neck does not rotate, shoulders relaxed and arms down; tube to film 150 cm; tube centred on C4. p. 115 (PDF 1).
- Lumbar film: lying on the side (recumbent lateral), knees in easy flexion, hands out of the field, stabilised against rotation of the hips; tube to film 100 cm; tube centred on L3. pp. 115 and 117 (PDF 1 and 3).
- Same X-ray apparatus and the same high-quality film for every subject. p. 115 (PDF 1).
- Levels: two plates per subject, one showing C2-C7, one showing L1-L5. C1 was hidden by the skull in every film and was not measured; the thoracic spine was not evaluated because the ribs overlap it on the lateral view. p. 117 (PDF 3).
- Level identification: each vertebra was "clearly identified and marked" by region and number (p. 117, PDF 3), and measured after its location had been "carefully identified" (p. 119, PDF 5); how the count was made (from C2, from the sacrum, from the twelfth rib) is not described.
- Instrument: calipers (and compass, p. 119, PDF 5) directly on the film, to the nearest 0.1 mm; L and alpha computed from the measured dimensions by trigonometry; VBH and VBW calculated as averages. p. 117 (PDF 3).
- Magnification: corrected mathematically for parallax, assuming the mid-sagittal plane of the vertebrae parallel to the film, with factors set by the distance from the mid-sagittal plane to the source. The object-to-film distance used is not given. p. 117 (PDF 3). Inference: this is the usual M = SID / (SID - OFD), with SID 150 cm (cervical) or 100 cm (lumbar) and OFD the unknown mid-sagittal-plane-to-film distance; so the tables are anatomical-scale (de-magnified) values.

## Anomalies, numbering and transitional segments

- The paper says nothing about transitional vertebrae, lumbosacral transitional vertebrae, sacralisation, lumbarisation, L6, T13, rib counts, cervical ribs or block vertebrae. No prevalence of any anomaly is given.
- Numbering assumes seven cervical and five lumbar vertebrae: the cervical plate is read as C2-C7 and the lumbar plate as L1-L5. p. 117 (PDF 3).
- Inference: the exclusion of "any other known disease or abnormality" and the selection of films with clearly defined vertebrae (p. 115, PDF 1) mean that subjects with transitional or ambiguous segmentation were most likely dropped or never recognised, so the L1 and L5 rows describe a sample filtered of such anatomy. The three missing L1, one missing L5 and one missing C6 measurements (Table 1, p. 118, PDF 4; 154, 156 and 140 against 157, 157 and 141) are not explained; only the C2 and C7 shortfalls are (p. 117, PDF 3).

## Measures, each as a recipe

### The five reference points (shared by every measure)

Defined on p. 117 (PDF 3) and drawn in Fig. 1, p. 116 (PDF 2), a photograph of three cervical vertebrae in lateral view (a specimen or model, not said) with the dashed model lines; the lowest vertebra carries the labels a, b, c, d, k, e and f, and an inset shows alpha and L.
- P1: most supero-anterior point of the body (where b meets c).
- P2: most supero-posterior point of the body (where c meets d).
- P3: most infero-anterior point of the body (where a meets b).
- P4: most infero-posterior point of the body (where a meets d).
- P5: most posterior point of the spinous process, taken "on the line parallel to b"; read with Fig. 1, the tip is where a line parallel to the anterior wall touches the process.
- Paper's naming trap: "width" in this paper is the antero-posterior extent of the body seen on the lateral film (Panjabi's end-plate depth), not the transverse width; "length" is the antero-posterior length of the whole vertebra. p. 117 (PDF 3), Fig. 1 (PDF 2).

General recipe from a 3D CT instance mask (Inference; the paper gives none): build a frame per vertebra with the left-right axis normal to the plane of symmetry of the instance, the antero-posterior axis along the inferior end plate in that plane, and the cranio-caudal axis normal to both. Take the body (and spinous process, where the segmenter gives those subregions) and either (i) cut the mid-sagittal slice or (ii) project the mask along the left-right axis to a silhouette, which is what a lateral film records. The paper's points are corners and the tip of the film silhouette, scaled back to the mid-sagittal plane, so the projection (ii) is the closer match; compute both and keep the difference as a check.

### a: inferior width of the body (lower end-plate depth)

- Landmarks: P3 to P4. Lateral radiograph; calipers. C2-C7, L1-L5. Table 1, p. 118 (PDF 4).
- Values, mean +/- SD (mm): C2 15.3+/-1.6, C3 15.6+/-1.5, C4 15.8+/-1.5, C5 16.1+/-1.5, C6 16.6+/-1.4, C7 16.3+/-1.4; L1 34.1+/-2.9, L2 34.7+/-3.0, L3 34.6+/-2.8, L4 34.9+/-2.8, L5 33.9+/-2.7.
- From a 3D CT instance mask: antero-posterior extent of the body subregion along the inferior end plate, between its antero-inferior and postero-inferior corners. Inference: corners at the ring apophysis rim; exclude osteophytes.
- From a radiograph alone: lateral only, corner to corner, divided by the magnification factor. Not available on an AP film.
- Across levels: rises slowly C2 to C6 (peak 16.6) with C7 a little lower; lumbar flat at 33.9-34.9, smallest at L5. Paper: lower and upper borders did not differ significantly among L1-L5 (p. 119, PDF 5). Inference: adjacent-level differences are at most 0.36 pooled SD (L4 to L5), so a separates regions, not neighbouring levels.
- Sex, age, size, population: men 20-38 only; no covariates here.
- Error: see the error section; SD 8.0-10.5 percent of the mean (Inference, from Table 1).

### b: anterior height of the body

- Landmarks: P1 to P3. Table 1, p. 118 (PDF 4).
- Values (mm): C2 16.6+/-2.5, C3 14.1+/-1.3, C4 13.4+/-1.3, C5 12.7+/-1.3, C6 13.0+/-1.3, C7 14.6+/-1.4; L1 25.4+/-2.2, L2 27.2+/-2.0, L3 27.9+/-2.1, L4 27.4+/-2.2, L5 28.3+/-2.1.
- From a 3D CT instance mask: cranio-caudal distance between the anterior superior and anterior inferior corners of the body silhouette. Inference: at C2 the upper corner is at the top of the body, below the dens, since heights of 16.6 and 19.0 mm cannot include the dens; a mask-derived C2 height must leave the dens out.
- From a radiograph alone: lateral only.
- Across levels: C2 tallest, then falling to a cervical minimum at C5 (12.7) and rising to C7 (14.6); lumbar rises L1 to L3, dips at L4, and L5 is the largest (28.3). The anterior wall of L1 was significantly shorter than its posterior wall (p. 119, PDF 5). Inference (pooled-SD steps, Table 1): C2 to C3 -1.25, C6 to C7 +1.18 and L1 to L2 +0.86 are the largest b steps.
- Error: SD 7.4-15.1 percent of the mean (largest at C2; Inference, from Table 1).

### c: superior width of the body (upper end-plate depth)

- Landmarks: P1 to P2. Table 1, p. 118 (PDF 4).
- Values (mm): C2 12.6+/-2.1, C3 14.8+/-1.5, C4 15.5+/-1.7, C5 15.5+/-1.7, C6 16.0+/-1.7, C7 16.4+/-1.4; L1 33.5+/-2.8, L2 34.4+/-2.9, L3 34.7+/-2.7, L4 34.3+/-2.7, L5 34.2+/-2.7.
- From a 3D CT instance mask: as a, along the superior end plate. At C2 the superior surface of the body carries the dens and the superior articular surfaces; the paper does not say where P1 and P2 were placed on C2. Inference: C2's c (12.6) is the least defined value in the table.
- From a radiograph alone: lateral only.
- Across levels: rises C2 to C7 (C4 and C5 equal at 15.5); lumbar flat 33.5-34.7, smallest at L1. Inference: C2 to C3 is the one large step (+1.21 pooled SD).
- Paper: in the cervical spine the base of one vertebra fits the roof of the one below accurately (p. 118, PDF 4). Inference from Table 1: a of each vertebra and c of the next differ by 0.1-0.5 mm in the neck (C2/C3 0.5, C3/C4 0.1, C4/C5 0.3, C5/C6 0.1, C6/C7 0.2) and by 0.0-0.7 mm in the lumbar spine (largest L4/L5).
- Error: SD 7.8-16.7 percent of the mean (largest at C2; Inference, from Table 1).

### d: posterior height of the body

- Landmarks: P2 to P4. Table 1, p. 118 (PDF 4).
- Values (mm): C2 19.0+/-3.2, C3 14.5+/-1.4, C4 13.9+/-1.2, C5 13.8+/-1.4, C6 13.9+/-1.6, C7 14.9+/-1.4; L1 27.1+/-2.1, L2 27.0+/-2.1, L3 27.9+/-2.1, L4 27.1+/-2.3, L5 25.7+/-2.5.
- From a 3D CT instance mask: cranio-caudal distance between the posterior superior and posterior inferior body corners. Inference: on a projection the posterior wall line is the most posterior body outline across its width, not the mid-sagittal (often concave) wall.
- From a radiograph alone: lateral only.
- Across levels: C2 tallest by far (19.0); C3-C6 flat about 13.8-14.5; C7 rises. In every cervical level d exceeds b (p. 118, PDF 4). Lumbar flat about 27 with L5 the shortest; the posterior wall of L5 was significantly shorter than its anterior wall (p. 119, PDF 5).
- Error: SD 7.5-16.8 percent of the mean; C2 most variable (3.2 mm) (Inference, from Table 1).

### k: diagonal of the body

- Landmarks: P3 (infero-anterior) to P2 (supero-posterior), as drawn in Fig. 1 (p. 116, PDF 2) and implied by the a-d-k triangle used on p. 119 (PDF 5). The authors measured it to fix the quadrangular shape of the body (p. 117, PDF 3).
- Values (mm): C2 24.7+/-2.4, C3 23.4+/-1.9, C4 23.0+/-1.9, C5 22.6+/-1.8, C6 22.6+/-1.7, C7 22.8+/-1.6; L1 42.8+/-2.9, L2 44.7+/-2.9, L3 45.2+/-2.7, L4 45.5+/-2.8, L5 44.9+/-3.1. Table 1, p. 118 (PDF 4).
- From a 3D CT instance mask: distance between the antero-inferior and postero-superior corners in the sagittal frame.
- From a radiograph alone: lateral only.
- Across levels: falls slowly C2 to C5-C6, C7 a little higher; lumbar rises L1 to L4 and falls slightly at L5.
- Error: SD 6.0-9.7 percent of the mean, the least variable measure (Inference, from Table 1).
- Angle between a and d: from a, d and k the authors judged it about 90 deg in all lumbar vertebrae (p. 119, PDF 5). Inference (law of cosines on the table means): L1 88.0, L2 92.0, L3 92.0, L4 93.6, L5 96.8 deg; cervical C2 91.5, C3 102.0, C4 101.3, C5 97.9, C6 95.2, C7 93.8 deg, so the cervical bodies of C3-C5 are drawn as leaning quadrilaterals, consistent with the antero-inferior lip of cervical bodies. Means of a nonlinear function are approximate.

### e and f: the spinous tip from the posterior body corners

- Landmarks: e from P2 (supero-posterior corner) to P5; f from P4 (infero-posterior corner) to P5 (Fig. 1, p. 116, PDF 2, where the inset draws f from the a-d corner; p. 117, PDF 3). Together they fix the position of the spinous tip.
- e values (mm): C2 40.0+/-3.5, C3 34.4+/-3.1, C4 33.6+/-2.8, C5 35.4+/-3.1, C6 41.5+/-4.6, C7 49.6+/-3.5; L1 52.7+/-4.5, L2 55.9+/-4.9, L3 56.8+/-4.9, L4 54.9+/-4.9, L5 51.4+/-5.3. Table 1, p. 118 (PDF 4).
- f values (mm): C2 36.6+/-2.6, C3 30.6+/-3.0, C4 30.4+/-2.6, C5 33.0+/-3.2, C6 39.7+/-5.0, C7 46.6+/-3.3; L1 47.0+/-5.0, L2 50.0+/-4.9, L3 50.6+/-4.8, L4 48.4+/-4.6, L5 43.9+/-4.9.
- From a 3D CT instance mask: P5 is the posterior-most voxel of the posterior elements along the direction normal to the anterior wall line within the sagittal frame; e and f are distances from the two posterior body corners to it. Inference: C2-C6 spinous processes are often bifid with paramedian tips, so take P5 from the lateral projection, not the mid-sagittal slice, or the cervical e and f will come out short.
- From a radiograph alone: lateral only. The paper names the clavicle, humerus and ribs as what hid about one C7 in ten (p. 117, PDF 3).
- Across levels: e exceeds f at every level (cervical and lumbar, p. 119, PDF 5), which the authors read as a downward-inclined process, explaining it by d being nearly perpendicular to a; Inference: it places the tip below mid-body height. Inference (Table 1): e - f is 1.8-3.8 mm in the neck and 5.7-7.5 mm in the lumbar spine, largest at L5. Cervical: long at C2, smaller at C3, then rising to C7 (the text implies the low point is C3; the table puts it at C4 by 0.8 and 0.2 mm, inside the SD). Lumbar: rise L1 to L3, fall to L5 (p. 119, PDF 5); the authors read L3 as having the longest spinous process. Inference (pooled-SD steps): e C5 to C6 +1.56, C6 to C7 +1.98; f C5 to C6 +1.60, C6 to C7 +1.63, L4 to L5 -0.95; with the C2 to C3 steps (f -2.14, e -1.69) these are the strongest adjacent-level separators in the paper.
- Error: SD 7.1-12.6 percent of the mean (Inference, from Table 1).

### alpha: angle of inclination of the spinous process

- Definition: computed, not measured; the Fig. 1 inset (p. 116, PDF 2) draws it at the a-d corner (P4) between the posterior prolongation of the inferior width a and the segment f, with f drawn below that line. Table 2, p. 118 (PDF 4); computed by trigonometry, p. 117 (PDF 3). No SD given.
- Values (deg): C2 10.7, C3 14.4, C4 12.1, C5 6.1, C6 3.8, C7 7.3; L1 -5.8, L2 -3.0, L3 -0.3, L4 1.9, L5 8.2.
- Sign (Inference): the inset draws a positive alpha with f below the prolonged a line, so a positive value puts the spinous tip caudal to the inferior end-plate line and the negative values at L1-L3 put it slightly cranial. The printed L equals a + f cos(alpha) within 0.05 mm at ten levels and 0.22 mm at C7, which confirms that alpha is measured from the line of a (cosine cannot fix the sign).
- Inference: alpha recomputed from the table means of a, d, k, e and f by the law of cosines matches the printed value within 1.0 deg at C3, C4, C5, C6, C7, L1, L3, L4 and L5, but not at C2 (-2.7 vs 10.7) or L2 (-0.2 vs -3.0); either alpha is a mean of per-subject values, or a value at C2 and L2 is off. Use C2 and L2 alpha with caution.
- From a 3D CT instance mask: angle in the sagittal frame between the inferior end-plate direction (P3 to P4, prolonged posteriorly) and the vector P4 to P5. Inference: independent of posture, since it is relative to the vertebra's own end plate.
- From a radiograph alone: lateral only; magnification does not change an angle.
- Across levels: cervical peak at C3, minimum at C6; lumbar rises monotonically from L1 to L5 (largest at L5, 8.2). The text says the angle increased from L1 to L3 and that the inclination grew going down the lumbar spine (p. 119, PDF 5).

### L: overall length of the vertebra

- Definition: computed; Fig. 1 (p. 116, PDF 2) draws it as the distance between the line of the anterior wall and the parallel line through the spinous tip P5. Table 2, p. 118 (PDF 4). No SD given.
- Values (mm): C2 51.3, C3 45.2, C4 45.5, C5 48.9, C6 56.2, C7 62.3; L1 80.9, L2 84.6, L3 85.2, L4 83.3, L5 77.4.
- From a 3D CT instance mask: extent of the whole instance (body plus posterior elements) along the antero-posterior axis of the vertebra's frame, from the anterior body wall to the spinous tip. Inference: equivalently a + f cos(alpha), which reproduces Table 2.
- From a radiograph alone: lateral only, divided by magnification.
- Across levels: shortest cervical at C3, longest at C7 (p. 120, PDF 6); in the lumbar spine longest at L3 and shortest at L5 (p. 120, PDF 6). Inference (Table 2): C2 to C3 -6.1 mm, C5 to C6 +7.3 mm, C6 to C7 +6.1 mm; L4 to L5 -5.9 mm.

### VBH and VBW: average body height and average body width

- Definitions: VBH, the average distance between superior and inferior surfaces; VBW, the average distance between anterior and posterior lines of the body in lateral view (p. 117, PDF 3). Inference (arithmetic): the printed values equal (b+d)/2 and (a+c)/2 of the Table 1 means exactly. Table 2, p. 118 (PDF 4); no SD.
- VBH (mm): C2 17.80, C3 14.30, C4 13.65, C5 13.25, C6 13.45, C7 14.75; L1 26.25, L2 27.10, L3 27.90, L4 27.25, L5 27.00.
- VBW (mm): C2 13.95, C3 15.20, C4 15.65, C5 15.80, C6 16.30, C7 16.35; L1 33.80, L2 34.55, L3 34.65, L4 34.60, L5 34.05.
- Across levels: C2 is the only level whose body is taller than deep; C3 to C7 are deeper than tall (p. 120, PDF 6). Cervical widths increase gradually from C2 to C7, "forming a pyramid" (p. 118, PDF 4); C2 is taller than every other cervical body and C3-C7 have nearly the same height (p. 118, PDF 4). Lumbar width exceeds height and neither differs significantly from L1 to L5 (p. 120, PDF 6). Inference: VBW/VBH is 0.78 at C2, 1.06-1.21 at C3-C7 (peak C6) and 1.24-1.29 in the lumbar spine.

## Level by level and at the junctions

- C1: never measurable on these lateral films; the skull covers it. p. 117 (PDF 3).
- C2 and the C2/C3 junction: about 10 percent of C2s were not defined clearly enough (n 130 of 141). C2 has the tallest body (b 16.6, d 19.0), the smallest superior depth (c 12.6), VBW < VBH, and a spinous process longer than C3's (e 40.0, f 36.6, L 51.3 against C3's 34.4, 30.6, 45.2). pp. 117-120 (PDF 3-6), Tables 1-2. Inference: C2 to C3 differs by -1.82 pooled SD in d, -2.14 in f, -1.69 in e, -1.25 in b and +1.21 in c, the clearest step in the neck.
- C3-C5: nearly identical bodies (VBH 13.25-14.30, VBW 15.2-15.8); the shortest vertebrae (L 45.2-48.9); largest spinous inclination (alpha 14.4 at C3). Inference: adjacent differences in a, b, c, d and k stay below 0.6 pooled SD and below 1 mm, so these three cannot be told apart from one another by body shape.
- C6: e, f and L jump (L 56.2); alpha lowest (3.8). One C6 measurement is missing (n 140), unexplained.
- C7 and the C7/T1 junction: about 10 percent of C7s were obscured by the clavicle, humerus and ribs (n 126 of 141); C7 is the longest cervical vertebra (L 62.3, e 49.6, f 46.6); b rises to 14.6. T1 not measured. pp. 117-120 (PDF 3-6).
- Thoracic and the T12/L1 junction: no thoracic data, because of rib overlap (p. 117, PDF 3). L1 is anteriorly wedged (b 25.4 < d 27.1, significantly) and has the most negative alpha (-5.8). p. 119 (PDF 5), Tables 1-2.
- L2-L4: almost cylindrical bodies of nearly equal size (the paper says this of all five lumbar bodies); L3 has the longest overall length (85.2) and the largest e and f. p. 119 (PDF 5), Tables 1-2.
- L5 and the L5/S1 junction: posteriorly wedged (d 25.7 < b 28.3, significantly), shortest lumbar vertebra (L 77.4), largest alpha (8.2), smallest lumbar a (33.9), d (25.7) and f (43.9). The sacrum was not measured. pp. 119-120 (PDF 5-6).
- The lumbar vertebrae gave the impression of five large solid bones in pronounced lordosis, with slightly inclined processes (p. 119, PDF 5); lordosis itself was not measured.

## Measurement error and reliability

- Caliper and compass error estimated below +/-0.5 mm; the parallax correction adds at most +/-1.0 mm. p. 119 (PDF 5).
- Together these may reach up to 10 percent of a cervical dimension and under 5 percent of a lumbar one, which the authors judge smaller than between-subject variability. p. 119 (PDF 5). Inference: +/-1.5 mm against cervical bodies of 13-16 mm and lumbar bodies of 26-35 mm gives those percentages.
- The SDs, which combine measurement error and subject variability, are about 10 percent overall, which the authors call small for such a study. p. 119 (PDF 5). Inference: per-measure coefficients of variation in Table 1 run 7.0-16.8 percent in the neck (C2 d highest) and 6.0-11.2 percent in the lumbar spine.
- Not reported: number of observers, intra- or inter-observer repeatability, repeat films, or any formal reliability statistic. Significance tests are mentioned ("did not differ significantly", p. 119, PDF 5) but not named.
- Resolution: readings to 0.1 mm on film. p. 117 (PDF 3).

## Clinical pearls, indications and pitfalls

The paper has no clinical indication, threshold, syndrome or implant sizing; it is a modelling reference. What it does say about measuring:
- Standardise the films: same apparatus, same film, fixed distances (150 cm cervical, 100 cm lumbar), tube centred on C4 and L3, positioning that prevents neck and hip rotation. p. 115 (PDF 1), p. 117 (PDF 3).
- Correct magnification before comparing radiographic and anatomical sizes; the authors corrected each dimension back to the mid-sagittal plane. p. 117 (PDF 3).
- C1 is lost under the skull; thoracic vertebrae are lost under the ribs; about one C2 in ten is unclear and about one C7 in ten is hidden by the clavicle, humerus and ribs. p. 117 (PDF 3).
- The model ignores the articular processes, treats the spinous process as a triangle and the body as a "square box", so finer shape is lost. p. 119 (PDF 5).
- Lateral radiographs are, in the authors' view, the major diagnostic tool in orthopaedics and biomechanics, which is why a lateral-film model is useful. p. 119 (PDF 5).
- Use level-specific values: the tables show a progressive change from level to level, so a model of a region should keep each segment's own dimensions. p. 119 (PDF 5).
- Lumbar dimensions are said to be twice or more the cervical ones, which the authors relate to the larger load carried. p. 119 (PDF 5). Pitfall: this holds for the body depths a and c only (see Gaps).
- Pitfall (Inference): with a single central ray on C4 or L3, the end plates of C2, C7, L1 and L5 are struck obliquely and show double contours, which moves the corner points; rotation doubles the posterior wall. The paper does not discuss either.
- Pitfall (Inference): the lumbar films were taken lying on the side and the cervical films standing; the measures are within one vertebra, so posture changes them only through projection, but the "pronounced lordosis" remark is of a side-lying spine.
- Pitfall: "width" here is antero-posterior depth on the lateral view; do not merge with transverse widths. p. 117 (PDF 3).

## Instructions for the autonomous anatomist

1. On a lateral cervical film, expect C1 to be unmeasurable under the skull base (it was in every film here) and anchor the cervical count on C2; confirm C2 by a body taller than deep (VBH 17.8 vs VBW 13.95) and a long posterior element (L 51.3 vs 45.2 at C3). p. 117 (PDF 3); Tables 1-2, p. 118 (PDF 4); p. 120 (PDF 6).
2. For every vertebral body on a lateral view, mark the four body corners and the spinous tip as P1-P5, the tip taken where a line parallel to the anterior wall touches the spinous process. p. 117 (PDF 3), Fig. 1 p. 116 (PDF 2).
3. Measure a, b, c, d, k, e and f between those points, and compute L = a + f cos(alpha), with alpha the angle of P4-P5 from the posteriorly prolonged inferior end-plate line, positive when the tip lies caudal to that line (Inference for the formula and the sign, checked against Table 2 and the Fig. 1 inset, pp. 116 and 118, PDF 2 and 4). Divide distances by the film's magnification before comparing with these tables (p. 117, PDF 3).
4. From a CT instance mask, compute the same points on the lateral silhouette of the instance in its own sagittal frame, take the spinous tip from the silhouette so a bifid cervical tip is not missed, and leave the dens out of C2's body heights (Inference; the paper measured films only).
5. To find the lower end of the cervical spine, use the posterior element: L, e and f step up sharply C5 to C6 to C7 (L 48.9, 56.2, 62.3; e 35.4, 41.5, 49.6). Tables 1-2, p. 118 (PDF 4).
6. Inference (Table 1, p. 118, PDF 4): do not try to separate C3, C4 and C5 by body measures; adjacent levels differ by less than 1 mm on average in a, b, c, d and k, against SDs of 1.2-1.9 mm. Use the count from C2 instead.
7. Expect C7 to be hidden by the clavicle, humerus and ribs in about one film in ten (p. 117, PDF 3). Inference (Table 2): when the last visible cervical vertebra has an L nearer the C6 mean (56.2 mm) than the C7 mean (62.3 mm), suspect it is C6, not C7; no SD is printed for L, so weigh e and f (SD 3.3-5.0 mm) too.
8. In a run already known to be lumbar, read the wedge: b/d below 1 (anterior wedge) marks L1 (0.94 at the means), b/d above 1 (posterior wedge) marks L5 (1.10), L2-L4 near 1.00. p. 119 (PDF 5); Table 1. Guard: every cervical level also has b < d (b/d 0.87-0.98, p. 118, PDF 4), and the paper has no T12, so an anterior wedge alone does not tell L1 from a thoracic vertebra (Inference).
9. Read the spinous inclination: alpha negative at L1-L2, near zero at L3, positive and largest at L5 (8.2 deg). Table 2, p. 118 (PDF 4). Inference: no SD is printed, so its power to separate levels is unknown, and L2's value does not agree with the other columns.
10. Expect L3 to be the longest lumbar vertebra and L5 the shortest (p. 120, PDF 6). Inference (Table 2): a lumbar vertebra about 6 mm shorter in L than its upper neighbour, with a posterior wedge, is the L5 candidate.
11. Inference (Table 1): the inferior depth a of one vertebra matches the superior depth c of the next within 0.7 mm at the means (stated for the neck, p. 118, PDF 4). Use this to check that two instances face each other across one disc, not to find a skipped level: a and c change so slowly that a vertebra two levels away matches almost as well.
12. Treat a difference under about 1.5 mm in any radiographic body dimension as possible method error: calipers +/-0.5 mm plus parallax correction +/-1.0 mm (p. 119, PDF 5); SDs are about 10 percent of the mean.
13. Do not draw anomaly priors, female values or older-age values from this paper; it is men aged 20-38 with abnormal spines excluded. p. 115 (PDF 1).
14. There are no thoracic data here; do not extrapolate cervical or lumbar values to T1-T12. p. 117 (PDF 3).

## For bordercall's generator and classifier

(a) Anomaly priors for the sequence decoder: none. The paper gives no prevalence of any transitional or numerical anomaly, and its exclusions remove them. It assumed, and did not test, seven cervical and five lumbar vertebrae (p. 117, PDF 3), so it is no evidence on the count.

(b) Measures:
- Direct counterparts of Panjabi-style measures the generator holds: c = upper end-plate depth, a = lower end-plate depth, b = anterior body height, d = posterior body height, for C2-C7 and L1-L5 (Table 1, p. 118, PDF 4). Bias to expect against Panjabi's dry-bone values (Inference): these are corner-to-corner distances on the radiographic silhouette, including the rim and any marginal lipping, scaled to the mid-sagittal plane by an assumed geometry; Panjabi digitised bone directly. Compare the two numerically before pooling; the generator's priors, not memory, should decide.
- Not in Panjabi's body set and candidates to add: k (body diagonal, fixes the quadrilateral's skew), e and f (spinous tip position from the posterior corners), alpha (spinous inclination relative to the inferior end plate) and L (total sagittal length). Inference (pooled-SD steps): these are the strongest level separators here at C2/C3, C5-C7 and L4/L5. If the generator holds a spinous process length defined from the lamina, it is not e, f or L, which start from the body corners.
- Table 1 gives per-level means and SDs for seven measures, usable as univariate Gaussian emissions for radiograph-derived features; no covariance between measures is printed (the correlations are in the 1982 report), and Table 2 has no SDs.
- No canal, pedicle, facet or transverse measure is given.
- For a mask: take the silhouette of the instance projected along its own left-right axis to mimic the film; the mid-sagittal slice will give shorter e, f and L wherever the spinous tip is bifid or off midline (Inference).

(c) Measurement error: method error below +/-0.5 mm (calipers) plus at most +/-1.0 mm (parallax), up to 10 percent cervical and under 5 percent lumbar; SDs of Table 1 (about 10 percent) are total spread, biology plus error. p. 119 (PDF 5). Inference: for radiograph-derived features, add a sigma of about 1 mm to the generator's anatomical spread; for CT-derived features this term does not apply.

(d) Covariates: men only, 20-38 years (mean 26.8), mean stature 174.7 cm, likely Israeli working population (Inference). No dependence on sex, age, height or weight is given here; those correlations are in the 1982 technical report, not in this paper. p. 115 (PDF 1).

## Gaps and conflicts

- Text against table: the cervical e and f are said to fall at C3 and then rise towards C7 (p. 119, PDF 5), but Table 1 puts the minimum at C4 (e 33.6 vs 34.4, f 30.4 vs 30.6), within SD.
- Text against table: alpha is said to increase from L1 to L3 (p. 119, PDF 5; the subscript checked at 600 dpi); Table 2 shows it rising through L5 (-5.8, -3.0, -0.3, 1.9, 8.2), as the same sentence's "passing down the lumbar region" implies.
- The lumbar results cite "a to k; Table 2" (p. 119, PDF 5); a to k are in Table 1.
- "All dimensions" lumbar being two or more times cervical (p. 119, PDF 5) holds for a and c only (lumbar/cervical ratios 2.04-2.75); not for b (1.53-2.23), d (1.35-2.02), k (1.73-2.01), e (1.04-1.69), f (0.94-1.66; C7's f 46.6 exceeds L5's 43.9) or L (1.24-1.88). Inference from Tables 1-2.
- Lumbar spinous processes are called inclined downward because e > f (p. 119, PDF 5), yet alpha is negative at L1-L3, so "downward" means below mid-body height, not below the end-plate line (Inference).
- "L3 has the longest spinous process in the human body" (p. 119, PDF 5) is unsupported: no thoracic vertebra was measured, and e, f and L run from the body, not along the process alone.
- Denominators: 141 cervical and 157 lumbar spines in the methods (p. 115, PDF 1) against 157 men in the summary (p. 120, PDF 6); overlap not stated. Missing measurements at L1 (3), L5 (1) and C6 (1) unexplained.
- Alpha recomputed from the means fails at C2 and L2 (see alpha); no SD is given for alpha, L, VBH or VBW.
- Unstated: object-to-film distance and the resulting magnification factor; how levels were counted; how P1 and P2 were placed on C2 below the dens; number of observers and any repeatability study; the statistical test behind "significantly"; any covariance between measures.
- No women, no subjects over 38, no anomaly counts, no thoracic or sacral values, no disc heights or intervertebral spacing (in the 1982 report only), no sagittal alignment angles, no canal, pedicle or facet measures.
- Reference list (Inference from memory): the 1982 Spine paper on reciprocal angulation is listed under "Stagmara" (p. 120, PDF 6), and the 1973 biomechanics paper's co-author as "Andriaechi" (p. 115, PDF 1); the authors are usually spelled Stagnara and Andriacchi.
- Other papers in this set (Inference from memory, not checked here): Panjabi's dry-bone series supply the same body depths and heights plus transverse, pedicle, canal and facet measures; Hinck 1966 measures the canal on lateral and AP films, which this paper does not. A numerical comparison of a, b, c and d against the generator's Panjabi priors is the check to run.
