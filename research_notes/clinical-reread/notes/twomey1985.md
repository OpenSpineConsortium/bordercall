# Twomey 1985: Age changes in lumbar intervertebral discs

Source: thread "Reread every paper for clinical detail", project symphony_4, 2026-10-28.

Status: drafted by one reader from the whole PDF; not yet checked against the PDF by a second reader, because the check stopped at the session's usage limit on 2026-10-28 (HANDOFF.md says how to finish it).


Citation as printed on the first page: Lance Twomey, James Taylor. Age changes in lumbar intervertebral discs. Acta Orthop Scand 56, 496-499, 1985. (The issue number is not printed on the page; Inference: issue 6.)

Copy read: publisher's free copy (Acta Orthop Scand), project files literature/synthetic_spine/twomey1985.pdf, sha256 begins 13750a89f310ef1a. Four pages; printed pp. 496-499 are PDF pages 1-4. Every number below was read from the page images (the text layer garbles Table 2).

## What the paper is

- Design: cross-sectional post-mortem study of lumbar discs across the whole age range, measuring disc diameters, disc heights, disc shape and macroscopic disc quality, to test whether loss of stature in old age comes from disc thinning. p. 496 (PDF 1).
- Population and denominators: 204 cadavers, from each of which a block running from the top of T12 to the bottom of S2 was taken, within 48 h of death and in most within 24 h; psoas major and the erector spinae were dissected off. p. 496 (PDF 1). Country, ethnicity, cause of death and inclusion or exclusion criteria are not stated. Inference: the cadavers are Western Australian, since both authors' institutions are in Western Australia (p. 496, PDF 1); the paper does not say where the bodies came from.
- Age and sex groups (Table 1, p. 496, PDF 1), mean age (range), n; the text calls these "six age groups", the four older split by sex:
  - infants, sexes pooled: 9, ages 0-1.5 (no mean printed);
  - children, sexes pooled: 28, mean 8 (1.5-12);
  - adolescents: 17 males, mean 16 (13-19); 6 females, mean 14 (13-17);
  - young adults: 24 males, mean 25 (20-36); 24 females, mean 23 (18-35);
  - middle-aged: 24 males, mean 47 (36-59); 24 females, mean 49 (36-59);
  - old: 24 males, mean 68 (60+); 24 females, mean 73 (60+).
  - Sum 204 (37 of unrecorded or pooled sex, 89 males, 78 females). Inference: the sex split of the 37 infants and children is not given.
- Sub-samples: disc height (Table 2) is reported only for young adults (20-35) and old (60+) of each sex; the convexity index (Table 3) only for males 20-35 and 60+ and females 18-35 and 60+; the Rolander grading (Table 4) on 140 specimens (6 + 18 + 13 + 35 + 34 + 34). pp. 496-498 (PDF 1-3). Inference: the n behind each cell of Tables 2 and 3 is not printed; 24 per sex per age group is the likely figure from Table 1.
- Modality and instruments: direct measurement of the intact disc with dial vernier calipers "accurate to 0.05 mm" for horizontal antero-posterior (AP) and transverse diameters; after midline sagittal sectioning of each specimen, anterior, mid-disc and posterior heights with the same calipers; the area of each disc in median section traced and measured with a MOP Image Analyser. p. 496 (PDF 1).
- Levels: the five lumbar discs L1-2, L2-3, L3-4, L4-5, L5-S1. T12-L1 lies inside the block but is not reported. p. 496 (PDF 1), Tables 1-4.
- How levels were identified or counted: not stated. Transitional segments: not mentioned; no exclusion of anomalous spines is described.

## Anomalies, numbering and transitional segments

The paper says nothing about lumbosacral transitional vertebrae, sacralisation, lumbarisation, L6, T13, rib counts or block vertebrae, and nothing about how the lumbar levels were numbered. Inference: with a block taken from T12 to S2, a lumbarised S1 or a sacralised L5 would fall inside the block and would have been labelled by whatever convention the dissectors used, unrecorded; a sixth lumbar disc, if present, is not reported.

## Measures, each as a recipe

### 1. Disc antero-posterior diameter (AP diameter)

- Definition: the horizontal AP diameter of the intact disc, measured with dial vernier calipers before sectioning. Landmarks are not specified beyond "horizontal"; Inference: from the anterior to the posterior outer surface of the anulus, at its widest, in the midsagittal direction. p. 496 (PDF 1).
- Plane: the disc's own horizontal plane (perpendicular to the spinal axis at that level). Instrument: dial vernier calipers, 0.05 mm. Levels: L1-2 to L5-S1.
- Values (Table 1, p. 496, PDF 1), mean mm, no SD printed, order L1-2, L2-3, L3-4, L4-5, L5-S1:
  - infants 0-1.5 (MF, 9): 15, 17, 17, 17, 16
  - children 1.5-12 (MF, 28): 26, 28, 28, 29, 26
  - adolescent males 13-19 (17): 39, 39, 39, 40, 39
  - adolescent females 13-17 (6): 34, 36, 36, 36, 35
  - young adult males 20-36 (24): 40, 40, 40, 40, 38
  - young adult females 18-35 (24): 35, 36, 37, 37, 35
  - middle-aged males 36-59 (24): 39, 40, 40, 40, 39
  - middle-aged females 36-59 (24): 35, 36, 37, 37, 36
  - old males 60+ (24): 40, 41, 41, 41, 41
  - old females 60+ (24): 38, 40, 40, 40, 38
- From a 3D CT instance mask: Inference. A CT shows the disc only as the soft-tissue gap between two body masks; if the segmenter gives a disc label, take the disc's extent along the AP axis of the local vertebral frame (the axis in the midsagittal plane perpendicular to the spinal axis) at mid-disc height. Without a disc label, the nearest surrogate is the AP depth of the adjacent end plates (inferior end plate of the upper body, superior end plate of the lower), which excludes the anular bulge and so will read smaller than this caliper value on an unloaded disc. The definition here is not Panjabi's end-plate depth.
- From a radiograph alone: lateral radiograph only, and only as the bony end-plate depth, since the anulus is not seen; magnification must be corrected (Inference: about 1.1 to 1.2 on a lumbar lateral film). The AP radiograph cannot give it.
- Across levels: the middle discs (L2-3 to L4-5) are "consistently larger" than the end discs L1-2 and L5-S1. p. 497 (PDF 2). The spread is small, 1-3 mm in adults, and in old males L5-S1 equals L2-3 to L4-5 (41 mm). It separates no adjacent pair reliably.
- Sex, age, size, population: males larger than females in every age group (Inference from Table 1: by 3 to 5 mm in adolescents and young adults, 3 to 4 mm in the middle-aged, 1 to 3 mm in the old). p. 497 (PDF 2). It grows from 15-17 mm in infancy to 26-29 mm in childhood and reaches adult size by adolescence in males. The paper states that it increased with age, by 10 per cent in females and 2 per cent in males, without saying which groups are compared. p. 497 (PDF 2). Inference: from Table 1 the five-disc mean rises from 36.0 to 39.2 mm in females (+9 per cent, young adult to old; +11 per cent adolescent to old) and from 39.6 to 40.8 mm in males (+3 per cent young adult to old; +4 per cent adolescent to old), so the printed 2 per cent for males does not match the table exactly.
- Error: only the general statement that inter-trial tests of the calipers correlated at r = 0.97 across all age groups; caliper accuracy 0.05 mm. p. 496 (PDF 1). No SD per cell is printed.

### 2. Disc transverse diameter

- Measured on every intact disc with the same calipers. p. 496 (PDF 1). No value, table or figure reports it. Gap.

### 3. Anterior, mid-disc and posterior disc heights (A, M, P)

- Definition: heights of the disc on the midline sagittal section at the anterior margin (A), at mid-disc (M) and at the posterior margin (P), taken with dial vernier calipers after midline sagittal sectioning; Figure 1 draws them as vertical dashed arrows between the two end plates at the front, middle and back of the disc. p. 496 (PDF 1); Figure 1, p. 497 (PDF 2).
- Values: not reported. The discussion only says that A and P decline "very small" amounts in old age, citing Twomey and Taylor 1983b. p. 498 (PDF 3).
- From a 3D CT instance mask: Inference. In the midsagittal plane of the motion segment (the body's left-right centroid plane), along the local spinal axis, take the gap between the inferior surface of the upper body mask and the superior surface of the lower body mask at the anterior rim (A), at the AP midpoint (M) and at the posterior rim (P).
- From a radiograph alone: lateral radiograph, as disc-space heights at the anterior corners, the centre and the posterior corners; Inference: projection of the end-plate rims and any obliquity of the beam narrow the visible space, and magnification must be corrected for absolute values.
- Across levels, sex, age: not reported here beyond the slight decline of A and P with age. p. 498 (PDF 3).
- Error: as for the calipers (r = 0.97, 0.05 mm). p. 496 (PDF 1).

### 4. "True average disc height" (mean disc height)

- Definition: the area of the disc in median (midline sagittal) section divided by its AP diameter, in mm. It was devised to avoid errors from local irregularities at the disc-vertebral interface. Area traced with a MOP Image Analyser. p. 496 (PDF 1); Table 2 caption, p. 497 (PDF 2).
- Levels: L1-2 to L5-S1.
- Values (Table 2, p. 497, PDF 2), mean (SD) mm, young adults 20-35 against old 60+, with the age test:
  - L1-2: M 9.2 (1.0) vs 9.2 (1.3), NS; F 6.1 (2.5) vs 7.9 (1.6), p < 0.05
  - L2-3: M 9.8 (1.2) vs 10.9 (1.9); F 8.0 (1.3) vs 8.5 (1.4); p < 0.01
  - L3-4: M 10.3 (1.0) vs 11.0 (2.0); F 8.2 (1.2) vs 8.5 (2.3); NS
  - L4-5: M 11.3 (1.3) vs 12.2 (1.8); F 8.5 (1.3) vs 9.2 (1.8); p < 0.05
  - L5-S1: M 10.6 (1.6) vs 11.2 (2.9); F 8.1 (1.2) vs 8.8 (1.7); p < 0.05
- Statistics: two-way ANOVA (sex by age) with stature as covariate. Sex differences at all levels; an age by sex interaction only at L1-2, which was therefore tested separately by sex (hence the separate NS for males and p < 0.05 for females there); at the other levels the age F tests come from the ANOVA. p. 497 (PDF 2).
- From a 3D CT instance mask: Inference. In the midsagittal plane of the motion segment, the area of the region between the inferior surface of the upper body mask and the superior surface of the lower body mask, bounded by the anterior and posterior rims, divided by the AP length of that region; equivalently the mean, over AP positions, of the gap along the local spinal axis. A slab a few mm thick about the midline, averaged, reduces voxel noise. Body subregion masks (SPINEPS corpus) are the right part to use; posterior elements must be excluded. The mask gives the bony gap of a living, loaded spine, whereas this paper measured an unloaded cadaveric disc, so absolute values will differ.
- From a radiograph alone: a lateral radiograph gives a close analogue (the area of the disc space outline divided by its AP length) once magnification is corrected; the AP radiograph cannot. Inference: since the end-plate centres are concave, the mean height includes the "sink" of the disc into the bodies that point heights at the rims miss.
- Across levels: in all four sex-age groups the mean height rises from L1-2 to a peak at L4-5 and falls at L5-S1 (males young 9.2 to 11.3 then 10.6; old 9.2 to 12.2 then 11.2; females young 6.1 to 8.5 then 8.1; old 7.9 to 9.2 then 8.8). Table 2, p. 497 (PDF 2). The step between adjacent levels is 0.3 to 1.9 mm against SDs of 1.0 to 2.9 mm, so no single disc separates one level from the next; the L4-5 peak and the L5-S1 fall give a shape across the sequence. The young female L1-2 value (6.1) is markedly lower than L2-3 (8.0), with the largest SD (2.5).
- Sex, age, size, population: males thicker than females at every level (young adults by 1.8 to 3.1 mm, old by 1.3 to 3.0 mm; Inference, from Table 2). Disc height increases from young adult to old in both sexes at every level except male L1-2 (unchanged): Inference from Table 2, males +0.6 to +1.1 mm (6 to 11 per cent) and females +0.3 to +1.8 mm (4 to 30 per cent, the 30 per cent at L1-2). The ANOVA showed a linear trend of disc thickness with stature for both sexes at each level (p < 0.05); since young adults were on average taller than old adults, adjusting for stature strengthened the increase with age. p. 497 (PDF 2). Stature values are not printed.
- Error: no error is reported for the image-analyser area or the derived mean height; only the caliper inter-trial r = 0.97. p. 496 (PDF 1).

### 5. Disc convexity index

- Definition: mid-disc height divided by the sum of the anterior and posterior disc heights, M/(A + P), all on the midline sagittal section; printed in the Figure 1 caption as "M/A + P", which the text makes clear means M over (A + P). p. 496 (PDF 1); Figure 1 and Table 3 caption, p. 497 (PDF 2). It shows the disc-vertebral shape change from the disc's side. Inference: a disc with flat or straight-wedged end plates scores 0.5; above 0.5 the disc is biconvex (the end plates are concave into the bodies).
- Values (Table 3, p. 497, PDF 2), order L1-2, L2-3, L3-4, L4-5, L5-S1:
  - males 20-35: 0.57, 0.60, 0.56, 0.58, 0.43
  - males 60+: 0.65, 0.66, 0.61, 0.56, 0.53
  - females 18-35: 0.58, 0.61, 0.60, 0.54, 0.49
  - females 60+: 0.68, 0.63, 0.65, 0.54, 0.48
  - Test printed in the caption: t = -2.38, p < 0.025. Text: an increase (p < 0.025) in seven of the ten indices for both sexes from young adult to old age. p. 497 (PDF 2). The seven increases are male L1-2, L2-3, L3-4, L5-S1 and female L1-2, L2-3, L3-4; male L4-5 falls, female L4-5 is unchanged, female L5-S1 falls by 0.01.
- From a 3D CT instance mask: Inference. A, M and P as in measure 3, then M/(A + P). Dimensionless, so independent of voxel size and magnification.
- From a radiograph alone: lateral radiograph, from the disc-space heights at the anterior margin, the centre and the posterior margin; magnification cancels in the ratio. Inference: beam obliquity at the end plates and rim osteophytes bias A and P on a film.
- Across levels: in young adults the index is about 0.56 to 0.61 at L1-2 to L3-4 and lowest at L5-S1 in both sexes (males 0.43, females 0.49); in females L4-5 is also low (0.54). In the old the upper three levels are 0.61 to 0.68 and L4-5 and L5-S1 0.48 to 0.56. Table 3, p. 497 (PDF 2). Inference: the index falls at the lower two discs, so a low index helps mark the L4-5 and L5-S1 discs as a pair but does not separate them from each other reliably except in young males.
- Sex, age, size, population: rises with age at the upper three discs in both sexes, consistent with the end plates collapsing into the bodies; paralleled by the vertebral concavity index of Twomey and Taylor 1983a. p. 497 (PDF 2). No SDs, no size covariate.
- Error: none reported. Inference: a paired t over the ten printed young-old pairs of means gives about 3.1, not the printed 2.38, so the printed test must use per-specimen data or another design; the paper does not say.

### 6. Disc quality (Rolander 1966 macroscopic grade)

- Definition: Rolander's 4-point grade of the sectioned disc's appearance, paraphrased (p. 497, PDF 2):
  - 0: macroscopically normal, nucleus and anulus white and clearly distinct;
  - 1: normal appearance but the nucleus more fibrous, a distinct boundary still present;
  - 2: a less distinct nucleus-anulus boundary, colour change from white to yellowish-brown, possibly an isolated anular fissure;
  - 3: frank degeneration with desiccation, multiple fissures in nucleus and anulus, and disc thinning.
- Applied to 140 specimens (5 discs each). p. 496 (PDF 1).
- Counts (Table 4, p. 498, PDF 3), by age group and n, for L1-2, L2-3, L3-4, L4-5, L5-S1:
  - 0-1.5 (n 6): all grade 0 at every level.
  - 1.5-12 (n 18): grade 0 13, grade 1 5 at every level.
  - 13-20 (n 13): grade 1 13, 13, 13, 12, 12; grade 2 at L4-5 1; grade 3 at L5-S1 1.
  - 20-35 (n 35): grade 1 33, 34, 35, 15, 30; grade 2 1, 1, 0, 1, 4; grade 3 1, 1, 0, 1, 1.
  - "36-39" (n 34; Inference: a misprint for 36-59): grade 1 27, 30, 30, 28, 25; grade 2 2, 3, 2, 2, 6; grade 3 5, 1, 2, 4, 3.
  - 60+ (n 34): grade 1 17, 17, 16, 10, 12; grade 2 9, 7, 10, 14, 11; grade 3 8, 10, 8, 10, 11.
  - No grade 0 disc after age 12.
- From a 3D CT instance mask: not possible; this is a gross pathology grade of the cut disc. Inference: on CT only grade 3's thinning (and a vacuum or calcification, which the paper does not mention) could show.
- From a radiograph alone: not possible, except disc thinning as a proxy of grade 3. Inference.
- Across levels: the lower discs carry the highest grades, particularly in the two oldest groups. p. 497 (PDF 2). Inference from Table 4: in the 60+ group grade 2 or 3 at L1-2 17/34 (50 per cent), L2-3 17/34 (50), L3-4 18/34 (53), L4-5 24/34 (71), L5-S1 22/34 (65); grade 3 alone 8, 10, 8, 10, 11 of 34 (24 to 32 per cent). In the 36-59 group grade 2 or 3 at 7, 4, 4, 6, 9 of 34, but grade 3 alone is most frequent at L1-2 (5/34), which goes against the text's statement for that group.
- Age: grade 0 only in infancy and childhood; grades associated with ageing and degeneration become more frequent from adult life to old age. p. 497 (PDF 2).
- Error: no reliability for the grading is reported.

### 7. Central vertebral height (C), drawn only

- Figure 2 (p. 498, PDF 3) draws the anterior vertebral structures of a young adult (solid line) against an old adult (dotted line), with arrows marking where height is lost: A (anterior disc height), P (posterior disc height) and C, the central vertebral height, from the middle of the upper end plate to the middle of the lower end plate of the body. In the old shape the end plates bow into the body and the disc bulges into the hollow. No values are given here; the authors cite Ericksen 1974 and 1975 and Twomey, Taylor and Furniss 1983 for vertebral height loss. p. 498 (PDF 3).
- From a 3D CT instance mask: Inference. In the body's midsagittal plane, the distance along the local spinal axis between the superior and inferior end-plate surfaces at the AP midpoint of the body mask; compare with the body's anterior and posterior heights for a concavity measure.
- From a radiograph alone: lateral radiograph, centre of the upper to centre of the lower end-plate line. Inference.

## Level by level and at the junctions

- L1-2: among the smallest discs in AP diameter in most adult groups, with L5-S1 (Table 1, p. 496, PDF 1) and the thinnest in mean height in every group (Table 2, p. 497, PDF 2). The only level with an age by sex interaction: no age change in males (9.2 to 9.2 mm), a rise in females (6.1 to 7.9 mm, p < 0.05). p. 497 (PDF 2). Convexity index rises with age in both sexes (male 0.57 to 0.65, female 0.58 to 0.68). In the 36-59 group L1-2 had the most grade 3 discs (5/34). Table 4, p. 498 (PDF 3).
- L2-3: the most significant age increase in mean height (p < 0.01; males 9.8 to 10.9, females 8.0 to 8.5). p. 497 (PDF 2).
- L3-4: age change in mean height not significant. p. 497 (PDF 2). The only level at which all 35 young adults (20-35) were grade 1. Table 4, p. 498 (PDF 3).
- L4-5: the thickest disc at every age and sex (males 11.3 young, 12.2 old; females 8.5, 9.2). p. 497 (PDF 2). Convexity index does not rise with age (male 0.58 to 0.56; female 0.54 both). The most discs of grade 2 or 3 in the 60+ group (24/34). Table 4, p. 498 (PDF 3).
- L5-S1 (lumbosacral junction): AP diameter smaller than the middle discs except in old males (Table 1); mean height lower than L4-5 in all four groups (Table 2); convexity index the lowest of all levels in young males (0.43) and young females (0.49) (Table 3, p. 497, PDF 2); the most grade 3 discs in the 60+ group (11/34) and the most grade 2 or 3 in the 36-59 group (9/34) (Table 4, p. 498, PDF 3).
- T12-L1 (thoracolumbar junction): inside the removed block (from the upper border of T12) but no data reported. p. 496 (PDF 1).
- Cervical and thoracic junctions: not covered.

## Measurement error and reliability

- Dial vernier calipers accurate to 0.05 mm; inter-trial tests of the calipers gave r = 0.97 across all age groups. p. 496 (PDF 1). No intra- or inter-observer error in mm, no error for the image-analyser area, the derived mean height, the convexity index or the Rolander grade.
- Between-specimen SDs of the mean disc height are 1.0 to 2.9 mm (Table 2, p. 497, PDF 2), largest in the old (up to 2.9 mm at male L5-S1) and at young female L1-2 (2.5 mm).
- Sources of error the paper addresses: local irregularities at the disc-vertebral interface make point heights unreliable, hence the area-based mean height. p. 496 (PDF 1).
- Inference: cadaveric, unloaded, sectioned discs measured up to 48 h post mortem; disc height in a loaded living spine and on CT or film will differ in absolute value, and sectioning can deform soft tissue.

## Clinical pearls, indications and pitfalls

- Loss of stature in old age is not mainly from disc thinning: average disc height is maintained or increased in old age, and loss of vertebral height is the main cause of stature loss. pp. 496, 498 (PDF 1, 3).
- The small decline of anterior and posterior disc heights is more than offset by the increased convexity of the disc as the end plates collapse; the discs "sink" into the vertebrae. End-plate collapse from osteoporosis is described as the most obvious and widespread age change of the lumbar spine. p. 498 (PDF 3); Figure 2. The abstract attributes the shape change of vertebrae and discs in the elderly mainly to loss of the transverse trabeculae of the lumbar vertebrae. p. 496 (PDF 1).
- Pitfall: "disc degeneration" is often used loosely for disc thinning or for marginal osteophytes. The authors separate normal age change from "pathological" degeneration (Rolander grades 2 and 3), and only the latter involves disc thinning and desiccation. p. 498 (PDF 3). Old discs are usually neither thin nor desiccated; both grades may still go with functional change such as disc stiffness. p. 498 (PDF 3).
- Degeneration becomes more frequent in old age, but 72 per cent of the elderly discs examined showed no evidence of it. p. 498 (PDF 3). Inference: 72 per cent matches the discs of the 60+ group that are not grade 3 (123/170 = 72.4 per cent), not those that are neither grade 2 nor 3 (72/170 = 42 per cent), so "such change" here means grade 3.
- Causes of disc thinning would be loss of material by herniation or loss of volume by dehydration; interspongious (end-plate) herniation and anular rupture lose too little volume to matter. The stiffer old disc does not prolapse readily into end-plate microfractures, although these become more frequent in the elderly. p. 498 (PDF 3).
- Hydration: from Puschel 1930, as the authors read him, the greatest water loss of the disc happens in childhood and adolescence; anular water is steady through adult life and nuclear water falls by only 6 per cent from early adult life to old age; glycosaminoglycan content is maintained and collagen rises slightly (Adams and Muir 1976, Bushell 1977). Brown 1957 found minimal bulging of discs under extreme compression. The authors reject the "underinflated tyre" simile for the normal elderly disc. pp. 498-499 (PDF 3-4).
- No stenosis thresholds, syndromes, screw sizing or safe zones are discussed.

## Instructions for the autonomous anatomist

1. Measure lumbar disc height on the midsagittal plane as area divided by AP length, not as a single point height; point heights are thrown off by end-plate irregularities. p. 496 (PDF 1).
2. Expect the mean disc height to rise from L1-2 to a maximum at L4-5 and to drop slightly at L5-S1, in both sexes and in young and old adults (Table 2, p. 497, PDF 2). Use this as a sequence shape across five gaps; never name a single disc from its height alone, since adjacent steps (0.3 to 1.9 mm) are below one SD (1.0 to 2.9 mm).
3. Score the disc convexity index M/(A + P) on lateral images or the mask's midsagittal plane; it is free of magnification. Expect about 0.56 to 0.68 at L1-2 to L3-4 and lower values at L4-5 and L5-S1, lowest at L5-S1 in young adults (0.43 male, 0.49 female). Table 3, p. 497 (PDF 2).
4. Adjust disc expectations for sex: male discs are 1.3 to 3.1 mm thicker (young and old adults) and 1 to 5 mm deeper (3 to 5 mm in young adults, 1 to 3 mm in the old) than female discs at every lumbar level. Tables 1-2, pp. 496-497 (PDF 1-2).
5. In an elderly spine, do not read stature loss as disc collapse: expect discs of maintained or greater mean height, more convex, sunk into biconcave end plates, with reduced central vertebral height. Compare the body's central height with its anterior and posterior heights before calling a fracture or a level. pp. 497-498 (PDF 2-3), Figure 2.
6. Expect AP disc diameter to be largest at L2-3 to L4-5 and slightly smaller at L1-2 and L5-S1 (1 to 3 mm), and to rise somewhat with age, more in women. Table 1, p. 496 (PDF 1). Treat it as a weak feature only.
7. A thin, desiccated disc at L4-5 or L5-S1 in an older patient is common (grade 2 or 3 in 65 to 71 per cent of 34 discs at age 60+; grade 3 in 29 to 32 per cent). Table 4, p. 498 (PDF 3). Inference: do not take a thin lowest disc as a rudimentary transitional disc without a body-shape or rib sign; this paper gives no transitional data.
8. Do not let marginal osteophytes stand for degeneration, nor degeneration for thinning; they are separate findings. p. 498 (PDF 3).
9. In children, expect much smaller discs (AP 15 to 17 mm in infancy, 26 to 29 mm in childhood) and macroscopically normal grades; scale any adult prior by age. Tables 1 and 4, pp. 496, 498 (PDF 1, 3).

## For bordercall's generator and classifier

(a) Anomaly priors for the sequence decoder: none. The paper reports no transitional vertebra, L6, T13, rib count or block vertebra. Its degeneration counts (Table 4, p. 498, PDF 3) could serve as a prior for a thin or missing-looking lower disc in older patients, not as an anomaly prior.

(b) Measures:
- The generator (Panjabi's four papers) draws vertebral dimensions, not disc dimensions. This paper offers three disc measures it could add per lumbar gap: mean disc height (area/AP, Table 2), disc convexity index M/(A + P) (Table 3), and disc AP diameter (Table 1). Mean disc height would be the most useful sequence feature because of its consistent L4-5 peak and L5-S1 drop.
- Definition differences that would bias a mask-derived value: (i) these are unloaded cadaveric discs, so mask-derived gaps in a living supine CT should be compared after calibration, not raw; (ii) the AP diameter here is the soft-tissue disc including the anular bulge, larger than a bony end-plate depth from a mask or Panjabi's end-plate depth (Inference); (iii) the mean height is the area of the whole disc section over its AP length, which includes the parts of the disc sunk into concave end plates; a mask-derived bony gap measures the same thing only if the gap is taken to the actual end-plate surfaces, not to the rims (Inference); (iv) the convexity index uses rim heights A and P; on a mask these should be read at the anterior and posterior body margins of the midsagittal plane.
- Inference: the convexity index of the disc is the mirror of a vertebral end-plate concavity measure; if the generator draws central and peripheral body heights it already encodes part of this.

(c) Measurement error to use: none in mm is given. Caliper inter-trial r = 0.97; between-specimen SD of mean disc height 1.0 to 2.9 mm (Table 2), which can serve as the generator's within-level spread for adults. For mask extraction, Inference: assume at least one voxel (about 0.5 to 1 mm on clinical CT) of error per height, which is large against the 0.3 to 1.9 mm steps between levels.

(d) Covariates: sex (large: males thicker and deeper at every level), stature (disc thickness rises linearly with stature at every level, p < 0.05, slope not given), age (mean disc height and convexity rise from young adult to 60+, AP diameter rises with age, more in females; children's discs much smaller). Population: unstated; Inference: Western Australian cadavers, ethnicity unrecorded.

## Gaps and conflicts

- Not reported: transverse diameters (measured on every disc), raw anterior, mid and posterior heights, the middle-aged group's disc heights and convexity, the n per cell of Tables 2 and 3, stature values and the stature slope, the size of the sex effect's test, any error in mm, the reliability of the image analyser and of the Rolander grade, and T12-L1.
- Population: country, ethnicity, cause of death, selection and exclusion criteria are not stated; the sex of the 37 infants and children is not given.
- Age bands disagree between tables: young adult males 20-36 (Table 1) against 20-35 (Tables 2-3); adolescents 13-19 and 13-17 (Table 1) against 13-20 (Table 4); "36-39" in Table 4, Inference a misprint for 36-59.
- Table 4, 20-35 group (n 35): L4-5 sums to 17 (15 + 1 + 1), Inference a misprint for 33 at grade 1; L2-3 sums to 36 (34 + 1 + 1), one more than n. Other rows sum to their n.
- The text's "lower disc levels showed the highest grades" holds for the 60+ group but not for grade 3 in the 36-59 group, where L1-2 has the most (5/34). p. 497 against Table 4.
- The text says AP diameter rose 2 per cent in males; Table 1 gives about 3 to 4 per cent depending on the groups compared (Inference); the compared groups are not named.
- The Table 3 caption gives one t statistic (-2.38, p < 0.025) for ten young-old contrasts; what it tests is not stated, and a paired t over the printed means gives about 3.1 (Inference).
- The young female L1-2 mean height (6.1 mm, SD 2.5) is out of line with L2-3 (8.0) and with the old females (7.9); Inference: possibly a few thin or degenerated discs in a small cell.
- "72 per cent" of elderly discs normal fits grade 3 only as "degenerated", although the text defines pathological degeneration as grades 2 and 3 (Inference, from Table 4). p. 498 (PDF 3).
- Inference, from memory of other papers in this set: the conclusion that disc height is kept or increased with age conflicts with radiographic studies that report disc-space narrowing with age; the difference may lie in the area-based mean height of the cadaveric disc against point heights of the radiographic disc space. This paper's finding agrees with its own cited Nachemson 1979 that age and degeneration are not necessarily linked and degeneration is not the same as thinning. p. 496 (PDF 1).
