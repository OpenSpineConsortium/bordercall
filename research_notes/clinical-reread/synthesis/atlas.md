# Level by level, and a playbook for the autonomous anatomist

Source: a synthesis of the 43 notes of the thread "Reread every paper for clinical detail" (project symphony_4,
2026-10-28), kept under bordercall/research_notes/clinical-reread/notes/, written 2026-10-29. Facts about code come
from bordercall's schwingcheck (README.md, measures.py, data/panjabi_long.csv) and scanimport/schemes.py, and are
named as code wherever they are used. The notes are the authority; where a note and this part differ, the note wins.

## How to read this part

- A citation "(eisenstein1977 p. 177)" names the note by its id and the paper's printed page as the note records
  it. "(... note)" marks a reading that the note itself makes and the paper does not print.
- Each value carries its material in brackets:
  - [DB] dry or macerated bone measured directly;
  - [cad] a cadaver specimen measured directly, by contact film or by specimen CT;
  - [CT] living patients on CT; [MRI] living patients on MRI;
  - [AP] or [LAT] living patients on an AP or lateral radiograph;
  - [DB12] Panjabi's series: 12 fresh autopsy spines, C2 to L5 with no sacrum, 8 men and 4 women aged 19 to 59
    (mean 46.3), mean height 167.8 cm, digitised in 3D after maceration; every cell is a mean over the 12 spines
    with its SEM (panjabi1991c p. 861; panjabi1991t p. 889; panjabi1992 p. 299; panjabi1993f p. 1299). The lumbar
    paper's donors are the same 12 by the note's Inference (panjabi1992 note).
- "step/SD" is Inference throughout, computed here from schwingcheck's data/panjabi_long.csv, which transcribes
  Panjabi's tables:
  - SD = SEM x sqrt(12), since each cell is a mean of 12 spines.
  - step/SD = (mean of the lower level - mean of the upper level) / ((SD upper + SD lower) / 2).
  - Paired facet measures are the mean of left and right, with the right side's sign flipped for the sagittal
    angle and the card angle Y, as schwingcheck mirrors them.
  - A step that crosses two of Panjabi's papers (C7/T1, cervical to thoracic; T12/L1, thoracic to lumbar)
    assumes that the two papers define the measure alike. The notes do not confirm that, so treat those steps as
    upper bounds.
  - What a step/SD means for naming (Inference): two normal classes of equal SD whose means differ by d SD are
    told apart from one observation with probability Phi(d/2): 0.69 at d = 1, 0.84 at d = 2 and 0.93 at d = 3.
    A single measure under 1 SD names nothing by itself.
- Measure names are schwingcheck's (README "The measures"), with the paper's own mnemonic where it helps:
  endplate (EPWu), endplate_depth (EPDu), endplate_lower (EPWl), endplate_lower_depth (EPDl), h_post (VBHp),
  canal_w (SCW), canal_ap (SCD), canal_area (SCA), pedicle_w (PDW), pedicle_h (PDH), pedicle_incl_sag (PDIs, the
  medial convergence seen in the axial plane), pedicle_incl_trans (PDIt, the cranio-caudal tilt seen in the sagittal
  plane), spinous_length (SPL), transverse_width (TPW), interfacet_w_sup and _inf (IFWs, IFWi), interfacet_h (IFH),
  facet_sag (S), facet_trans (T). tan2004's note warns that Panjabi's naming of the two pedicle angles is easy to
  invert (tan2004 note).
- schwingcheck's pool is 32 measures over C3 to L5 (README "The table"). C2 and S1 lie outside it. Seven measures
  have a mask measurer today (measures.py, SPINEPS_7: endplate, endplate_depth, endplate_lower,
  endplate_lower_depth, h_post, canal_w, canal_ap). transverse_width and spinous_length are in the pool with no
  measurer (README "The measures").
- "Inference:" marks every reading of mine: a computed ratio, a pooled rate, a recommended rule.

## The sources at a glance

Every count below is the paper's own, with the page where the note records it.

| Id | Material and place | Who, how many | Levels | Page |
|---|---|---|---|---|
| abbas2021 | [CT] Haifa, Israel | 165 patients with degenerative stenosis (80 M, 85 F, 40-88 y) and 180 controls (90 M, 90 F) | L1-L5 | p. 2 |
| ahmed2019 | [MRI] Telangana, India | 80 symptomatic adults (36 M, 44 F), 20-70 y | L1-L5 | pp. 21-22 |
| ahn2001 | [AP, LAT] USA | 32 adults with Marfan syndrome (18 F, 14 M), set against Hinck's 1966 norms | L1-L5 | pp. 67-68 |
| alonge2021 | [CT] Lagos, Nigeria | 120 abdominal CTs (66 F, 54 M), 18-65 y | L1-L5 | pp. 69-70 |
| amonookuofi1982 | [AP] Ilorin, Nigeria | 290 films of 290 adults (150 M, 140 F), 20-45 y, no bony injury | L1-L5 | pp. 225-226 |
| amonookuofi1985 | [DB] Ibadan, Nigeria | lumbar sets of 122 adults (79 M, 43 F), 23-60 y | L1-L5 | p. 69, p. 71 |
| arockiaraj2025 | [CT] Riyadh, Saudi Arabia | 300 adults (150 M, 150 F), 18-60 y | L1-L5 | pp. 313-314 |
| bach2019 | [CT] Tampa, USA | 240 abdominal CTs (131 F, 109 M), 10-80 y | discs T12/L1 to L5/S1 | p. e107 |
| bonczar2024 | review of 18 studies | 1,481 individuals pooled across CT, film, MRI, caliper and digitiser | L1-L5 | p. 3 |
| busscher2010 | [cad] specimen CT, Groningen | 6 male spines, 55-84 y, mean height 182 cm | C3-L5 | p. 1105 |
| chaudhary2015 | [AP] Haryana, India | 300 films read as normal (150 M, 150 F), 25-40 y | L1-L5 | pp. 33-34 |
| chen2011 | [CT] China (note's Inference) | 83 patients, 21-65 y, no spinal complaint | end plates T10 inf to L3 sup | p. 1815 |
| cizmic2023 | [CT] Sarajevo | 200 patients with lumbar pain (100 M, 100 F) | L1-L5 | p. 201 |
| duman2026 | [CT] Izmir, Turkey | 517 adults (277 M, 240 F), mean 48.6 y | T11-L2; ribs | p. 3, p. 6 |
| eisenstein1977 | [DB] Raymond Dart Collection, South Africa | 443 skeletons (113 Caucasoid, 162 Zulu, 168 Sotho), 16-96 y; 2,166 lumbar vertebrae | L1-L5; lumbosacral survey | p. 177 |
| frontphys2026 | [CT] Zhengzhou, China | 100 healthy adults, 20-70 y | L1-L5 bodies | pp. 2-3 |
| gilad1985 | [LAT] Israel (note's Inference) | 141 cervical and 157 lumbar films of healthy men, 20-38 y | C2-C7, L1-L5 | p. 115 |
| griffith2016 | [CT] Hong Kong | 1,080 Chinese adults (540 M, 540 F), 21-80 y | L1-L5 canal | p. 672 |
| hinck1966 | [AP] Portland, USA | 474 films of white patients: 121 adults and 353 children of 3-18 y | C3-L5 | pp. 141-142 |
| hou1993 | [DB] Xi'an, China | 40 columns T9-L5 (25 M, 15 F) | T9-L5 | pp. 1850-1851 |
| italianmri | [MRI] Italy | 604 Caucasian adults (302 M, 302 F), 20-45 y, transitional spines excluded | L1-S1 | p. 2 |
| krag1988 | [CT] Vermont, USA | 91 vertebrae of 41 patients (14 F, 27 M), 18-75 y | T9-L5 | p. 27 |
| kunkel2011 | [cad] contact film and direct, Germany (note's Inference) | 72 thoracic motion segments from 30 donors, 37-80 y | C7-T12 | p. 377 |
| lien2007 | [DB] and [cad], Taiwan | 15 dry-bone sets (8 M, 7 F); 6 cadavers | T1-L5 | p. 1216 |
| makino2012 | [CT] Japan | 50 surgical patients (23 M, 27 F), 52-85 y | L1-L5 | p. 1517 |
| masharawi2021 | [CT] Israel | 100 adults aged 50-80: 50 with an L4-L5 degenerative slip, 50 controls | L1-S1 | p. 2 |
| mitra2002 | [cad], film and CT, Nagpur, India | 20 cadavers (18 M, 2 F) | L1-L5 | p. 453 |
| moncadahabib2025 | [CT] Mexico City | 37 patients, mean 60.4 y | L1-L5 | p. 2 |
| olsewski1990 | [cad], film and CT, Buffalo, USA | 49 embalmed cadavers (24 M, 25 F), 60-98 y; 51 living patients, 20-50 y | L1-L5 | pp. 542-543 |
| otsuki2021 | [cad] USA | 6 lumbar spines (3 M, 3 F), 50-67 y | L1-L5 | p. 2 |
| panjabi1991c | [DB12] | the 12 spines | C2-C7 | p. 861 |
| panjabi1991t | [DB12] | the 12 spines | T1-T12 | p. 889 |
| panjabi1992 | [DB12] | the 12 spines | L1-L5 | p. 299 |
| panjabi1993f | [DB12] | the 12 spines, facets | C2-L5 | p. 1299 |
| robertson2000 | [DB] films of disarticulated bone, Auckland authors | 10 lumbosacral specimens: 100 lumbar and 20 S1 pedicles | L1-S1 | p. 709 |
| shin2024 | [CT] Loma Linda, USA | 700 adults 18-35 y (809 screened, 109 excluded) | L1-L2 to L5-S1 discs | p. 3 |
| tan2004 | [DB] Singapore | 10 Chinese cadavers, 56-77 y, sex not reported | C3-L5 | p. 137 |
| tang2016 | [MRI] Utah, USA | 109 adults (55 F, 54 M), 20-40 y | discs and end plates L3/L4 to L5/S1 | p. 4117 |
| twomey1985 | [cad] Australia (note's Inference) | 204 lumbar blocks, infants to elderly | discs L1-2 to L5-S1 | p. 496 |
| vanderhouwen2009 | [CT] Groningen | 77 patients (46 M, 31 F), 21-86 y; 25 per end plate | end plates T12 inf to S1 sup | p. 34 |
| yadav2020 | [CT] North India | 302 adults (174 M, 128 F), 20-40 y | T12-S1 | p. 176 |
| yu2015 | [DB] Hamann-Todd, Cleveland | 503 skeletons (404 M, 99 F; 281 Caucasian, 222 African American), 17-93 y | L1-L5 | pp. 1640-1641 |
| zindrick1987 | [cad] specimen film and [CT], USA | 2,905 measurements; specimens and patients not counted | T1-L5 | p. 160 |

No paper in the set states how it identified or numbered its levels, and none reports a measurement taken on a
transitional segment (abbas2021 p. 2; panjabi1992 p. 299; yadav2020 p. 176; hinck1966 p. 142; and the LEV line of
every other note). Inference: every level norm below silently assumes 7 cervical, 12 thoracic and 5 lumbar
vertebrae over a sacrum of five, and a norm for "L5" may hold a few transitional segments (bonczar2024 p. 10;
griffith2016 note).

# Part 1. The atlas, level by level

Each section gives what sets the level apart, a table of the measures in which it is extreme or turns, and its
pearls and pitfalls. Steps in the tables run from the level above to the level below unless the row says otherwise.

## C2

What sets it apart:

- The deepest, largest and roundest cervical canal: SCD 21.0 mm, SCA 374.5 mm2, width/depth 1.17 [DB12]
  (panjabi1991c p. 864, Table 3).
- The largest cervical pedicles: width 7.7/8.3 mm, height 9.4/11.1 mm and area 32.3/51.8 mm2 (right/left), the left
  area 60% above the right [DB12] (panjabi1991c p. 864, Table 4; p. 866). The authors tie the deep canal to motion
  without cord encroachment, and the large pedicles to the posteriorly placed load-bearing facets and the muscles on
  the large spinous process (panjabi1991c p. 868).
- An uncovertebral surface below and none above [DB12] (panjabi1991c p. 865, Table 6).
- The largest superior facets of the whole column, width 16.8/16.0, height 18.0/17.7, area 211.3/205.1, and an
  orientation unlike any other cervical facet, S 114.1/118.5 and T 40.7/33.5 deg [DB12] (panjabi1993f
  pp. 1301-1303, Tables 2, 4, 6). Its inferior facets are the size of the lower cervical ones (panjabi1993f
  p. 1301).
- The narrowest superior interfacet width relative to the inferior, IFWs 30.3 against IFWi 35.9 (ratio 0.84, the
  column's minimum), and IFH 20.1/20.2 [DB12] (panjabi1993f p. 1302, Table 5).
- The largest left-right asymmetry of the superior card angle Y, 38.9 right against -59.9 left [DB12]
  (panjabi1993f p. 1304, Table 8).
- On the lateral film the body is taller behind than in front (posterior height d 19.0, anterior b 16.6 mm), the
  upper end-plate depth c is the smallest of the neck (12.6 mm) and the spinous tip lies further from the body than
  at C3 (overall length L 51.3 against 45.2 mm) [LAT] (gilad1985 p. 118, Tables 1-2).
- The set holds no measurement of the dens or of the atlanto-axial joints. Inference: recognising C2 by its dens is
  anatomy from outside the set.

Where C2 is extreme or turns (C2 to C3):

| Measure | C2 -> C3 | step/SD (Inference) | Material, source |
|---|---|---|---|
| facet_area_sup | 208.2 -> 91.6 mm2 | -3.50 | [DB12] panjabi1993f p. 1302 |
| facet_sag_sup (S) | 116.3 -> 74.2 deg | -3.52 | [DB12] panjabi1993f p. 1303 |
| interfacet_h | 20.1 -> 12.6 mm | -3.35 | [DB12] panjabi1993f p. 1302 |
| facet_w_sup | 16.4 -> 11.1 mm | -3.06 | [DB12] panjabi1993f p. 1301 |
| interfacet_w_sup | 30.3 -> 35.9 mm | +2.69 | [DB12] panjabi1993f p. 1302 |
| pedicle_h | 10.2 -> 7.4 mm | -2.33 | [DB12] panjabi1991c p. 864 |
| pedicle_w | 8.0 -> 5.6 mm | -2.01 | [DB12] panjabi1991c p. 864 |
| canal_ap | 21.0 -> 16.2 mm | -1.65 | [DB12] panjabi1991c p. 864 |
| canal_area | 374.5 -> 248.7 mm2 | -1.54 | [DB12] panjabi1991c p. 864 |
| spinous_length | 33.7 -> 29.6 mm | -1.09 | [DB12] panjabi1991c p. 864 |
| posterior height d, spinous f, e | d -1.82, f -2.14, e -1.69 pooled SD | as printed by the note | [LAT] gilad1985 p. 118 (note's Inference) |

The authors call C2/C3 the upper transition: the canal depth falls 4.8 mm (significant), pedicle size falls in three
of four dimensions (significant), while the fall of canal area (126 mm2) and of SPL (4.1 mm) is not significant
(panjabi1991c p. 864; p. 868). At the facets, superior S falls from about 116 to 75 deg, the superior card angle Y
changes sign and IFW/IFH rises from 1.64 to 2.93 (panjabi1993f p. 1304, p. 1305; p. 1302, Table 5).

Pearls and pitfalls:

- Only three papers measure C2: panjabi1991c, panjabi1993f and gilad1985. tan2004 and busscher2010 start at C3
  (tan2004 p. 137; busscher2010 p. 1105). C2 is outside schwingcheck's pool (README "The table").
- C1 is never measurable on the lateral film; about 1 in 10 C2s is unclear there (130 of 141 measured) [LAT]
  (gilad1985 p. 117). C1 and C2 are not measurable on AP films [AP] (hinck1966 p. 142).
- The note recomputes gilad1985's spinous angle alpha and finds it off at C2 (-2.7 against 10.7 printed), so the C2
  alpha is not to be trusted (gilad1985 p. 118, note).
- Inference: on a CT mask, an instance with uncovertebral contact only on its lower side, the largest superior
  facets and the roundest canal of the neck is C2. Its dens confirms it, but the set cannot tell you how to measure
  the dens.

## C3 to C5: the plateau

What sets them apart: almost nothing.

- No measure separates any two of C3, C4 and C5 significantly [DB12] (panjabi1991c pp. 863-866, Tables 2-6).
- On lateral films the three bodies are nearly identical and the vertebrae the shortest of the neck (L 45.2 to
  48.9 mm); the note computes adjacent differences under 1 mm and under 0.6 pooled SD [LAT] (gilad1985 p. 118,
  Tables 1-2, note).
- In Singaporean bone, body widths, depths and heights are fairly constant from C3 to C5 [DB] (tan2004 p. 139).
- In Dutch specimens the body heights are low and equal (VBHa 13.4 to 14.5, VBHc 12.1 to 12.6 mm) and the upper
  end-plate is wider than the lower at C3-C4 [cad] (busscher2010 p. 1107, Table 3; Figs. 3-8, pp. 1109-1112).
- Pedicle axes run about 40 to 44 deg medially and 6 to 9 deg below the transverse plane [DB12] (panjabi1991c
  p. 866, Table 4).
- The canal is oval at C3 and triangular from C4, by the note's reading of the area ratios (panjabi1991c note).
- Panjabi's facet study splits the neck into three subregions, C2, C3-C4 and C5-C7, by the sign change of the
  superior card angle Y between C4 and C5 (right -8.4 to +9.2) and a higher facet width/height ratio at C5-C7
  [DB12] (panjabi1993f p. 1307; p. 1304, Table 8).

What orders them, and how weakly:

| Measure | C3, C4, C5 | step/SD (Inference) | Material, source |
|---|---|---|---|
| spinous length | 25.6, 30.3, 33.6 mm | not computed (SD uncertain) | [DB] tan2004 pp. 140-141, Table 1 |
| transverse width | 41.4, 44.9, 47.6 mm | not computed | [DB] tan2004 pp. 140-141, Table 1 |
| endplate_lower | 17.2, 17.0, 19.4 mm | C3/C4 -0.15, C4/C5 +1.56 | [DB12] panjabi1991c p. 863 |
| endplate | 15.8, 17.2, 17.5 mm | +0.72, +0.14 | [DB12] panjabi1991c p. 863 |
| uncovertebral frontal angle, upper | 76.6, 76.2, 82.7 deg | -0.05, +0.96 | [DB12] panjabi1991c p. 865 |
| pedicle tilt PDIt | sign change C4/C5 | not computed | [DB] tan2004 p. 143 |

Inference: the C4/C5 rise of the lower end-plate width (2.4 mm, 1.56 SD) is the one sizeable step inside the
plateau, yet the authors found no C3-C5 pair significant (panjabi1991c pp. 863-866). tan2004's note puts the
between-specimen SD of SPL and TPW at about 1.3 to 3 mm, close to the 3 to 5 mm step, so these two order the levels
only jointly and with the sequence (tan2004 note, instruction 8). Disagreement: tan2004 puts the sign change of the
pedicle's sagittal tilt at C4/C5 (tan2004 p. 143), Panjabi at C5/C6 (panjabi1991c p. 866, Table 4). The two series
differ in population ([DB] 10 Singaporean Chinese against [DB12] 12 US autopsy spines) and both used a digitiser.

Pearls and pitfalls:

- The adult interpedicular distance on AP films is a plateau peaking at C5-C6 (29.4, 29.3 mm) [AP] (hinck1966
  p. 142, Table IA).
- busscher2010's spinous lengths (13.5 to 15 mm at C3-C5) are about half Panjabi's (29.6 to 30.3) [cad, DB12]
  (busscher2010 Fig. 7a, p. 1111; panjabi1991c p. 864). Inference: Busscher measured the free process and Panjabi
  from the end-plate centre, as tan2004's note says Fig. 1c draws it (tan2004 note, instruction 17). Never mix the
  two definitions in one likelihood.
- tan2004's bony mid-sagittal canal at C3 to C6 is 10.3 mm, at the usual absolute stenosis threshold, against
  Panjabi's 15 to 18 mm; the note reads this as a landmark difference as much as anatomy (tan2004 note).
- Inference: name C3, C4 and C5 by counting down from C2 or up from C7, never by their own measures (panjabi1991c
  pp. 863-866; gilad1985 p. 118).

## C6

What sets it apart:

- The orientation break of the lower neck at C5/C6, all significant [DB12] (panjabi1991c pp. 864-866, Tables 4, 6):
  - the pedicle's cranio-caudal tilt (PDIt) changes sign, about -6 to +6.5 deg;
  - the pedicle's medial convergence (PDIs) falls from about 40 to 32 deg;
  - the upper uncovertebral frontal angle crosses 90 deg.
- The widest cervical canal width, SCW 25.8 mm [DB12] (panjabi1991c p. 864, Table 3), and the widest lower
  end-plate step of the neck (C5/C6) (panjabi1991c p. 863).
- The authors recall Fife and Kraus's high incidence of cord injury at C6 (panjabi1991c p. 868).
- On lateral films the spinous measures and the overall length jump at C6: L 48.9, 56.2, 62.3 and e 35.4, 41.5,
  49.6 mm at C5, C6, C7; the spinous angle alpha is lowest here (3.8 deg); one C6 was missing (140 of 141) [LAT]
  (gilad1985 p. 118, Tables 1-2).
- In Singaporean bone the lower end-plate width jumps 3.6 mm at C5/C6 (15.9 to 19.5) and SPL rises 6.9 mm [DB]
  (tan2004 pp. 140-141, Table 1).
- In Dutch specimens SPL reaches 22.5 mm at C6 and the spinous angle dips to about 20 deg [cad] (busscher2010
  Figs. 6-7, pp. 1110-1111).

| Measure | C5 -> C6 | step/SD (Inference) | Material, source |
|---|---|---|---|
| uncovertebral frontal angle, upper | 82.7 -> 104.0 deg | +3.20 | [DB12] panjabi1991c p. 865 |
| pedicle_incl_trans (PDIt) | -6.0 -> 6.5 deg | +2.14 | [DB12] panjabi1991c p. 864 |
| endplate_lower | 19.4 -> 22.0 mm | +1.31 | [DB12] panjabi1991c p. 863 |
| spinous_length | 28.5 -> 34.2 mm | +1.15 | [DB12] panjabi1991c p. 864 |
| endplate_area | 182.9 -> 221.2 mm2 | +1.44 | [DB12] panjabi1991c p. 863 |
| pedicle_incl_sag (PDIs) | 40.2 -> 31.9 deg | -0.71 | [DB12] panjabi1991c p. 864 |

Pearls and pitfalls:

- Inference: the C5/C6 angle break is the one cervical cue a CT mask can read without counting, since the
  uncovertebral angle step is about 3 SD. It needs the uncinate processes in the mask's body label and a frame on
  the posterior wall.
- Printed left-right gaps beside the angle break: upper uncovertebral area at C6 48.8 right against 58.1 left
  (panjabi1991c p. 868; Table 6). The authors test no side difference (panjabi1991c p. 868).

## C7

What sets it apart:

- The cervicothoracic transition, at the cervical side [DB12] (panjabi1991c pp. 863-868, Tables 2-6):
  - the upper end-plate jumps, EPWu 18.5 -> 21.8 mm and EPAu 221.2 -> 278.3 mm2 (significant against C6);
  - the lower end-plate depth falls 18.5 -> 16.8 mm, which the authors call a distinct transition (p. 867);
  - the posterior body height rises to 12.8 mm (significant against C6);
  - the canal is the smallest of the neck, SCD 15.2 mm and SCA 223.8 mm2, width/depth 1.61; the authors note that
    the canal narrows while the cord does not, raising the risk of impingement in trauma (p. 868);
  - SPL 45.7 mm and TPW 66.6 mm, each significant against C2 to C6;
  - the upper uncovertebral frontal angle reaches 115.6 deg, and C7 carries both an upper and a lower uncovertebral
    surface (p. 865, Table 6).
- The longest cervical vertebra on lateral films, L 62.3, e 49.6, f 46.6 mm [LAT] (gilad1985 p. 118, Tables 1-2).
- The longest cervical spinous process in Singaporean bone, 46.9 mm, with EPWu +3.2 mm and TPW +5.4 mm at C6/C7
  [DB] (tan2004 pp. 140-141, Table 1).
- In Dutch specimens the transverse process length steps from about 64 to 75 mm and SPL from about 22.5 to 33 mm
  at C6/C7 [cad] (busscher2010 Figs. 6, 7a, pp. 1110-1111).
- The smallest body of the thoracic motion-segment series (VBHA 13.89, VBHP 14.38 mm), and the C7-T1 disc is the
  only unwedged one (ADH = PDH = 4.5 mm) [cad] (kunkel2011 p. 380; Tables 1-3).
- The largest adult sex difference of the IPD profile is at C7, 2.2 mm [AP] (hinck1966 pp. 143-144, Tables IB-IC,
  note).

| Measure | C6 -> C7 | step/SD (Inference) | Material, source |
|---|---|---|---|
| transverse_width | 49.5 -> 66.6 mm | +3.05 | [DB12] panjabi1991c p. 864 |
| spinous_length | 34.2 -> 45.7 mm | +2.44 | [DB12] panjabi1991c p. 864 |
| endplate (EPWu) | 18.5 -> 21.8 mm | +1.57 | [DB12] panjabi1991c p. 863 |
| endplate_area | 221.2 -> 278.3 mm2 | +1.60 | [DB12] panjabi1991c p. 863 |
| h_post | 10.9 -> 12.8 mm | +1.52 | [DB12] panjabi1991c p. 863 |
| uncovertebral frontal angle, upper | 104.0 -> 115.6 deg | +1.32 | [DB12] panjabi1991c p. 865 |
| interfacet_h | 13.7 -> 17.3 mm | +1.26 | [DB12] panjabi1993f p. 1302 |
| canal_ap | 18.1 -> 15.2 mm | -1.04 | [DB12] panjabi1991c p. 864 |
| endplate_lower_depth | 18.5 -> 16.8 mm | -0.97 | [DB12] panjabi1991c p. 863 |
| interfacet_w_inf | 38.8 -> 33.6 mm | -1.88 | [DB12] panjabi1993f p. 1302 |

Pearls and pitfalls:

- About 1 in 10 C7s is hidden by the clavicle, humerus and ribs on the lateral cervical film (126 of 141
  measured) [LAT] (gilad1985 p. 117).
- A cervical rib was found in 7 of 517 Turkish adults on CT (1.35%; 1 of 277 men, 6 of 240 women), its vertebra
  not named [CT] (duman2026 p. 10, Table 5). Inference: such a rib, or an elongated transverse process, sits on
  C7's strongest single cue, its transverse width (panjabi1991c p. 864, note); keep any separate bone out of the
  width.
- The inferior C7 facets (T 49.8/49.1 deg) and the superior T1 facets (62.2/57.7) differ by up to 12 deg, so the
  two halves of the C7-T1 joint are not mirror images in Panjabi's frames [DB12] (panjabi1993f p. 1303, Tables 6-7,
  note).

## T1

What sets it apart:

- The first rib's facet: T1's upper costovertebral facet is 1.6 to 1.9 times T2's (45.3/56.6 against 29.0/29.5 mm2;
  the note reads it as rib 1's facet), and the total rib-articulation area falls from 132.0 at T1 to 95.9 mm2 at T2
  [DB12] (panjabi1991t p. 893; p. 895, Table 6).
- The longest transverse processes of the thorax, TPW 75.3 mm, and the second-widest thoracic canal, SCW 21.8 mm
  (width/depth 1.3) [DB12] (panjabi1991t pp. 892-894, Tables 3-5).
- A round pedicle, height/width 1.1 (8.5 x 9.6 mm), converging about 27 deg with a tilt of only 7.6 deg, against
  17.9 at T2 [DB12] (panjabi1991t pp. 894-895, Tables 5, 7).
- The largest lower end-plate inclination (3.9 deg) and wedge (5.7 deg) of the thorax [DB12] (panjabi1991t p. 892,
  Table 3).
- In Taiwanese bone the widest thoracic pedicle (7.65 mm), the lowest pedicle height (8.65 mm), the largest
  transverse angle (28.2 deg) and a sagittal angle of 11.6 against 18.9 deg at T2 [DB] (lien2007 p. 1218,
  Tables 1-2). The note computes T1 against T2 at 2.3 SD for width, 1.7 for height and 2.6 for the sagittal angle
  (lien2007 note).
- In zindrick1987's pooled specimens and CTs, the narrowest sagittal pedicle width (9.9 mm) and the largest thoracic
  transverse angle (26.6 deg) [cad, CT] (zindrick1987 pp. 161-162).
- In Singaporean bone, the largest cervicothoracic step of the whole table, on many measures at once: EPWu
  19.0 -> 24.7, EPWl 20.3 -> 27.1, VBHp 11.8 -> 14.0, TPW 53.8 -> 63.8 (its thoracic maximum), mean pedicle width
  5.65 -> 7.45 and height 6.3 -> 8.5 mm, and the lower end-plate inclination flips from +5.1 to -2.9 deg [DB]
  (tan2004 pp. 140-141, Table 1).
- In Dutch specimens pedicle width and transverse process length peak at T1 (about 8.4 and 81 mm); the lower
  end-plate width rises 30.7 -> 35.4 while the upper falls 31.5 -> 28.8 mm [cad] (busscher2010 Figs. 3-8,
  pp. 1109-1112).
- On AP films the IPD makes the largest drop of its whole profile: adult 28.0 at C7, 24.0 at T1 and 20.5 mm at T2,
  about 2 SD per step, present at every age [AP] (hinck1966 p. 142, Table IA; note).

| Measure | C7 -> T1 (or T1 -> T2) | step/SD (Inference) | Material, source |
|---|---|---|---|
| interfacet_w_inf | 33.6 -> 28.2 mm | -2.23 | [DB12] panjabi1993f p. 1302 |
| endplate_lower_depth | 16.8 -> 19.7 mm | +1.99 (crosses two papers) | [DB12] panjabi1991c p. 863; panjabi1991t p. 892 |
| transverse_width | 66.6 -> 75.3 mm | +1.75 (crosses two papers) | [DB12] panjabi1991c p. 864; panjabi1991t p. 894 |
| interfacet_w_sup | 38.6 -> 33.2 mm | -1.73 | [DB12] panjabi1993f p. 1302 |
| pedicle_h | 7.5 -> 9.6 mm | +1.57 (crosses two papers) | [DB12] panjabi1991c p. 864; panjabi1991t p. 894 |
| endplate_lower | 23.4 -> 27.8 mm | +1.57 (crosses two papers) | [DB12] panjabi1991c p. 863; panjabi1991t p. 892 |
| facet_trans_inf | 49.5 -> 64.2 deg | +1.27 | [DB12] panjabi1993f p. 1303 |
| pedicle_w | 6.5 -> 8.4 mm | +1.26 (crosses two papers) | [DB12] panjabi1991c p. 864; panjabi1991t p. 894 |
| T1 -> T2: facet_sag_sup | 85.8 -> 75.0 deg | -2.10 | [DB12] panjabi1993f p. 1303 |
| T1 -> T2: interfacet_w_sup | 33.2 -> 28.2 mm | -1.92 | [DB12] panjabi1993f p. 1302 |
| T1 -> T2: costovertebral area, upper | 51.0 -> 29.2 mm2 | -1.43 | [DB12] panjabi1991t p. 895 |
| T1 -> T2: transverse_width | 75.3 -> 69.4 mm | -1.29 | [DB12] panjabi1991t p. 894 |
| T1 -> T2: canal_w | 21.8 -> 19.5 mm | -1.26 | [DB12] panjabi1991t p. 893 |

Pearls and pitfalls:

- The facet rule fails here. Panjabi's own cervical rule, IFW/IFH above 1.5, admits T1 (IFW/IFH 2.09, 1.68 and 1.25
  at C7, T1 and T2), so the facet threshold falls between T1 and T2, not at C7/T1 (panjabi1993f p. 1302, Table 5;
  p. 1306; note). The superior transverse-plane angle rises only gradually, C7 59.4/51.6, T1 62.2/57.7, T2
  66.5/66.6 deg (panjabi1993f p. 1302).
- The size of the body-width jump at C7/T1 depends on the sample: Panjabi's implied EPWu step is 21.8 -> 24.5 mm
  against tan2004's 19.0 -> 24.7, and the Dutch absolute widths are larger than both (tan2004 note; busscher2010
  Figs. 3-8). Busscher's six men were tall (mean 182 cm) (busscher2010 p. 1105). Inference: weight the transverse
  process and the pedicle more than the body width here (tan2004 note, instruction 3).
- Upper thoracic posterior corners are hidden by overlapping shadows on film [cad] (kunkel2011 p. 383). The AP
  spine against PA chest difference in IPD is largest at T1-T3 (1.10 mm mean), so chest films are least reliable
  there [AP] (hinck1966 pp. 148-149, Table IV).

## T2 and T3: the upper transition

What sets them apart:

- T2/T3 holds the largest step of the upper end-plate depth (19.6 -> 22.7 mm), a steep fall of the transverse
  processes (69.4 -> 60.8 mm), and falls of the pedicle's convergence (28.6 -> 19.4 deg) and tilt (17.9 -> 8.8 deg);
  T3 has the smallest canal area (180 mm2 in the table, 189 in the text) and the smallest lower end-plate width
  (25.9 mm) [DB12] (panjabi1991t pp. 892-895, Tables 3-5, 7-8; p. 891).
- The authors call T1-T4 the upper transition, where the end-plate and canal widths narrow with constant depths. The
  note checks Tables 3-4: true for the canal (SCW 21.8 -> 17.0, SCD constant), but the upper end-plate width is flat
  and both end-plate depths grow 4.8 mm (panjabi1991t p. 897; note).
- T2 has the largest sagittal pedicle angle in Taiwanese bone, 18.9 deg [DB] (lien2007 p. 1219), and the largest
  cephalad sagittal angle (17.5 deg, range 7.0 to 32.0) with the shortest pedicle-axis depth (35.7 mm) in
  zindrick1987 [cad, CT] (zindrick1987 p. 162).
- The T2-3 disc is the most convex (index 0.83) and has the smallest posterior height on film (1.95 mm) [cad]
  (kunkel2011 p. 380, Tables 1, 3).

| Measure | T2 -> T3 | step/SD (Inference) | Material, source |
|---|---|---|---|
| transverse_width | 69.4 -> 60.8 mm | -2.03 | [DB12] panjabi1991t p. 894 |
| interfacet_w_sup | 28.2 -> 24.6 mm | -1.73 | [DB12] panjabi1993f p. 1302 |
| endplate_depth (EPDu) | 19.6 -> 22.7 mm | +1.54 | [DB12] panjabi1991t p. 892 |
| interfacet_w_inf | 24.3 -> 22.3 mm | -0.89 | [DB12] panjabi1993f p. 1302 |
| endplate_area | 333 -> 373 mm2 | +0.82 | [DB12] panjabi1991t p. 892 |
| pedicle_incl_sag (PDIs) | 28.6 -> 19.4 deg | -0.53 (T2 SD 25.5 is wide) | [DB12] panjabi1991t pp. 894-895 |

Pearls and pitfalls:

- Do not order T1 to T6 by end-plate width, which falls from T1 to T4 or T5 before it rises; use the end-plate
  depth, which rises nearly linearly from T1 to T12 [DB] (tan2004 p. 139; Table 1, instruction 7).
- In Singaporean bone the pedicle width falls from 7.45 at T1 to about 4 mm by T4, and TPW from 63.8 to 49.8 mm
  [DB] (tan2004 p. 142; Table 1).
- Panjabi's T2 convergence has a very wide spread (SD about 25.5 deg by the conversion above), so one T2 pedicle
  angle names nothing (Inference from panjabi1991t pp. 894-895).

## T4 to T9: the middle

What sets them apart: their sameness.

- Panjabi's middle region: a round, narrow canal (SCW about 17.4 mm), round end plates, the narrowest tall-oval
  pedicles (about 6 mm wide, height/width about 1.9), TPW about 60 mm, and the critical vascular zone with the
  least cord blood supply, which calls for strict care in surgery [DB12] (panjabi1991t p. 897; Tables 3-7). The
  region's bounds vary within the paper: T3 to T9 (abstract, p. 888), T4 to T9 (p. 891), T4 through T9 or T10
  (p. 897), and the authors note that Grant, Gray, Hollingshead and Parke disagree on its membership (p. 897).
- The smallest facets and interfacet widths of the column (IFW 20.8 mm at T5) and nearly uniform linear and areal
  facet sizes, so single thoracic levels are hard to tell apart; the most level-specific facet cue is IFWs/IFWi,
  falling from 1.18 at T1 to 0.93 at T8-T9 (the discussion says 1.15 to 0.95) [DB12] (panjabi1993f p. 1307;
  p. 1302, Table 5).
- Every rib articulates with its own vertebra and the one above from T1 to T10, and the costotransverse facet is
  present from T1 to T10 (40.0 to 65.0 mm2) [DB12] (panjabi1991t p. 893; p. 895, Table 6).
- The narrowest pedicles of the column: T4 3.5 and T5 3.8 mm in Taiwanese bone [DB] (lien2007 p. 1218); T5 4.5 and
  T4 4.7 mm mean transverse width, single values down to 2.5 mm at T4 and T8 [cad, CT] (zindrick1987 p. 161,
  Table 1); 4.3 to 5.4 mm at T4-T7 in Dutch specimens [cad] (busscher2010 p. 1110, Fig. 5); a mean of 4.0 mm at T4
  and T5 in Singaporean bone [DB] (tan2004 p. 142; Table 1).
- The narrowest canal: on AP films the IPD is narrowest and least variable from T3 to T10, minimum at T6 (adult
  17.3 mm), adult lower limit 14 mm at T5-T7 [AP] (hinck1966 pp. 145-146, Tables IA, III); in Singaporean bone SCW
  13.5 and SCD 11.5 mm at T4-T5, with SCA 140.1 mm2 at T4 the column's minimum [DB] (tan2004 p. 142; p. 144).
- The steepest and longest spinous processes (spinous angle 55 to 62 deg at T5-T7, length 40 to 45 mm at T4-T7,
  peak at T6) and the deepest kyphotic body wedge (VBHa/VBHp about 0.88, the note's computation) [cad]
  (busscher2010 p. 1110; Figs. 5, 6, 8; Table 3).
- The thinnest disc at T4-5 (mean 3.2, ADH 3.0 mm) and the lowest posterior height at T3-4 (3.2 mm) [cad]
  (kunkel2011 p. 380, Fig. 3; Tables 1-3).
- The least end-plate wedge at T9 and T10 (2.1 and 1.7 deg); from T8 the pedicle height and width climb about 1 and
  0.7 mm per level [DB12] (panjabi1991t p. 891; Table 3).
- T9 has the narrowest pedicle of hou1993's series (5.7 mm; women 5.2, men 6.0, P = 0.031), single widths down to
  3 mm [DB] (hou1993 pp. 1852-1853, Tables 1-3). In living CT, 3 of 14 T9 pedicles were under 5 mm wide and 2 under
  4 mm, and T9 has the longest chords [CT] (krag1988 pp. 28-31, Table 2).

Where the middle turns, if at all (step/SD over 0.8 between T4 and T9, Inference):

| Measure | Step | step/SD | Material, source |
|---|---|---|---|
| facet_trans_sup | T8 -> T9, 73.8 -> 78.0 deg | +1.15 | [DB12] panjabi1993f p. 1302 |
| facet_area_inf | T8 -> T9, 78.3 -> 94.2 mm2 | +1.00 | [DB12] panjabi1993f p. 1302 |
| endplate_lower | T8 -> T9, 30.5 -> 33.0 mm | +0.80 | [DB12] panjabi1991t p. 892 |
| endplate_area | rises every level, +45 to +73 mm2 | +0.58 to +0.82 | [DB12] panjabi1991t p. 892 |
| every other measure | | under 0.8 | panjabi1991t, panjabi1993f |

Pearls and pitfalls:

- Inference: do not name T4 to T9 from their own measures. Carry the names by count from a named neighbour, T1 or
  T12 (panjabi1991t p. 897; panjabi1993f p. 1307). The end-plate area and depth rise steadily (0.6 to 0.8 SD per
  level), which checks the order of a run but does not name it.
- Rib overlap hides the thoracic vertebrae on lateral films; gilad1985 measured none for that reason [LAT]
  (gilad1985 p. 117). The largest radiographic shortfall of disc height is at T8-9 (ADH 19.22%, PDH 50.12%) [cad]
  (kunkel2011 p. 378, Table 1).
- In Singaporean bone the pedicle's axial angle reverses sense at T7/T8 (right +8.6 -> -7.6 deg), and the authors
  report a slight divergence at T8-T12 (tan2004 p. 143; Fig. 11; p. 145). The note suspects a sign convention
  error; do not use it as a level marker until CT confirms it (tan2004 note, instruction 9).

## T10

What sets it apart:

- The last vertebra with a lower costovertebral surface (30.0/26.9 mm2) and a full costotransverse facet [DB12]
  (panjabi1991t p. 893; p. 895, Table 6).
- In Chinese bone: pedicle width 6.8 mm (single minimum 4.2), height 14.3 mm [DB] (hou1993 Tables 1-3,
  pp. 1852-1853).
- In living CT the pedicle is the smallest share of the chord (40%) and 2 of 18 T10 pedicles were under 4 mm [CT]
  (krag1988 p. 29; p. 30, Table 2).
- T10-11 is the tallest thoracic disc (ADH 7.2 mm, mean 6.5) [cad] (kunkel2011 Tables 1, 3, pp. 378-379).
- The lower T10 end plate is wider than the upper T11 (35.6 against 34.5 mm in men; 30.7 against 29.6 in women)
  [CT] (chen2011 p. 1818, Table 3).
- The smallest transverse pedicle angles of the thorax lie from T10 to L1, about 8 to 9 deg [DB] (lien2007 p. 1220;
  p. 1218, Table 2).

| Measure | T10 -> T11 | step/SD (Inference) | Material, source |
|---|---|---|---|
| pedicle_h | 14.8 -> 17.4 mm | +1.91 | [DB12] panjabi1991t p. 894 |
| costotransverse area | 55.8 -> 14.2 mm2 | -1.72 | [DB12] panjabi1991t p. 895 |
| interfacet_h | 26.0 -> 29.9 mm | +1.36 | [DB12] panjabi1993f p. 1302 |
| transverse_width | 58.4 -> 52.2 mm | -1.30 | [DB12] panjabi1991t p. 894 |
| endplate_lower | 35.4 -> 39.1 mm | +1.26 | [DB12] panjabi1991t p. 892 |
| endplate | 31.9 -> 34.9 mm | +1.06 | [DB12] panjabi1991t p. 892 |

## T11

What sets it apart:

- It loses the lower costovertebral facet and nearly loses the costotransverse one (62.3/49.3 -> 16.7/11.7 mm2);
  it has the largest upper costovertebral facet (71.9/60.0 mm2); ribs 11 and 12 float, with less stiffness [DB12]
  (panjabi1991t pp. 897-898; p. 895, Table 6).
- The pars area peaks (145/179 mm2), and the pedicle height, width and moments of inertia peak [DB12]
  (panjabi1991t Tables 5-7, pp. 894-895; p. 897).
- In living CT it has the narrowest end plate of the thoracolumbar run (T11 superior 34.5/29.6 mm, men/women),
  widening within the body to 37.7/33.4 mm (P < 0.00006 and < 0.0000003) [CT] (chen2011 pp. 1817-1818, Tables 1,
  3).
- In Turkish CT it is the bottleneck for screws: the narrowest pedicles (7.62 mm men, 7.21 women), and 57 of 517
  patients (about 11%) had a T11 pedicle under 6 mm [CT] (duman2026 p. 7, p. 11; Tables 2-3).
- In Chinese bone its width (8.1 mm) is the only level not different from Zindrick's, and its inclination is about
  0 deg [DB] (hou1993 Tables 1-3; p. 1854). In living CT the pedicle angle falls to about 0 deg and the body length
  is lowest (about 30.2 mm) with the widest SD [CT] (krag1988 p. 29, Fig. 4; p. 31, Fig. 6). zindrick1987 gives the
  widest sagittal pedicle width (17.4 mm) and a transverse angle near neutral (1.2 deg) [cad, CT] (zindrick1987
  p. 161, Tables 1-4).
- T11 and T12 have the tallest pedicles in Taiwanese bone (15.1 mm), roots nearly parallel to the ribs, and the
  smallest medial distance to the dura (1.0 to 1.5 mm) [DB] (lien2007 pp. 1218-1219, Tables 1, 3, 4).
- On AP films the IPD rises 2.0 to 3.0 mm from T11 to T12 at every age (adult 20.2 -> 23.2 mm) [AP] (hinck1966
  p. 142, Table IA). The note reads this as the steadier thoracolumbar signal in children, where the T12/L1 step is
  only 0.6 mm at 3-5, 6-8 and 13-14 years (hinck1966 note).

| Measure | T11 -> T12 | step/SD (Inference) | Material, source |
|---|---|---|---|
| facet_sag_inf (S) | 71.3 -> 139.2 deg | +2.77 | [DB12] panjabi1993f p. 1303 |
| endplate | 34.9 -> 39.0 mm | +1.53 | [DB12] panjabi1991t p. 892 |
| canal_ap | 16.0 -> 18.1 mm | +1.12 | [DB12] panjabi1991t p. 893 |
| canal_area | 220 -> 280 mm2 | +1.08 | [DB12] panjabi1991t p. 893 |
| endplate_lower | 39.1 -> 42.1 mm | +1.07 | [DB12] panjabi1991t p. 892 |
| pedicle_incl_trans (PDIt) | 8.7 -> 5.0 deg | -1.01 | [DB12] panjabi1991t pp. 894-895 |
| transverse_width | 52.2 -> 46.9 mm | -0.98 | [DB12] panjabi1991t p. 894 |
| canal_w | 19.4 -> 22.2 mm | +0.78 | [DB12] panjabi1991t p. 893 |

Pearls and pitfalls:

- On lateral fluoroscopy the radiographic blind spot shrinks as a pedicle tip nears the body's midline, except at
  T11 and T12, where a convergent screw can still breach the anterior cortex unseen [cad, CT] (zindrick1987 p. 165).
- duman2026's pedicle transverse angles at T11-L2 (21 to 28 deg) are 15 to 28 deg larger at every level than
  Zindrick's, whose landmarks it claims to follow; do not mix the two series (duman2026 note; zindrick1987 p. 163,
  Table 3).

## T12

What sets it apart, in order of strength:

- Ribs: a costovertebral facet on its body, no lower costovertebral surface and no costotransverse facet; T11 and
  T12 are uniarticular [DB12] (panjabi1991t p. 893; p. 895, Table 6).
- Facets: its superior facets are thoracic (S 72.5/67.4 deg) and its inferior facets lumbar (S 139.7/138.8 deg); the
  authors say T12 is easily identified by this abrupt change between its own superior and inferior facets [DB12]
  (panjabi1993f p. 1304, p. 1307; p. 1303, Tables 6-7). The lumbar-type inferior facets are why its pars area drops
  (panjabi1991t p. 893).
- Transverse processes: the narrowest of the thoracolumbar spine, 46.9 mm in Panjabi and 41.0 in Singaporean bone,
  with a jump at L1 [DB12, DB] (panjabi1991t p. 894; tan2004 pp. 140-141, Table 1). In Dutch specimens the
  transverse process length jumps from about 54 to 79 mm at T12/L1 and the ratio of process length to upper
  end-plate width has its minimum, 1.15, at T12 [cad] (busscher2010 p. 1107; Figs. 6-8, pp. 1110-1112).
- Canal: SCW 22.2, SCD 18.1 and SCA 280, all up from T11 [DB12] (panjabi1991t p. 893, Tables 3-4). In Indian CT,
  D12 has the largest canal depth, lateral recess and foramen and the smallest upper end-plate width and depth and
  interfacet distance of the series [CT] (yadav2020 pp. 177-178, Tables 2-3).
- Pedicles: the widest (8.3 mm; men 8.8, women 7.5, P = 0.043) and tallest (16.6 mm) lower thoracic pedicle in
  Chinese bone, with the axis tilted about 2.5 deg laterally (sign by the note) [DB] (hou1993 pp. 1851-1852,
  Tables 1-3, note). zindrick1987's only lateral mean transverse angle, -4.2 deg (SD 9.5, range -17.0 to +14.5)
  [cad, CT] (zindrick1987 p. 161, Tables 1, 3). In living CT the angle is about 0 or slightly negative (krag1988 p. 31,
  Fig. 6) and the on-axis width the narrowest of the series, about 6.8 mm [CT] (krag1988 p. 30, Fig. 5).
- Body: the largest body of the thoracic motion-segment series (VBHA 20.80, VBHP 23.12 mm) [cad] (kunkel2011
  Table 2, p. 379). Its upper and lower end-plate widths are equal (38.0 against 37.6 mm in men, P = 0.674),
  against a 4.3 mm caudal widening at L1 [CT] (chen2011 p. 1817; p. 1818, Table 3).
- Disc below: T12/L1 is the smallest of six discs in every height (anterior 6.29/4.81, middle 6.66/6.13, posterior
  3.75/3.29 mm, men/women) [CT] (bach2019 p. e113, Table 6).
- Sex: the only level of duman2026 with no sex difference in pedicle width (P = 0.168 and 0.251), though body
  heights still differ by 11.5 to 11.9% [CT] (duman2026 pp. 7-8, Tables 1-2).

| Measure | T12 -> L1 | step/SD (Inference) | Material, source |
|---|---|---|---|
| transverse_width | 46.9 -> 71.2 mm | +4.01 (crosses two papers) | [DB12] panjabi1991t p. 894; panjabi1992 pp. 301-304 |
| spinous_length | 47.4 -> 67.7 mm | +3.99 (crosses two papers) | [DB12] panjabi1991t p. 894; panjabi1992 pp. 301-304 |
| facet_sag_sup (S) | 70.0 -> 136.6 deg | +2.78 | [DB12] panjabi1993f p. 1303 |
| pars_area | 92.0 -> 62.1 mm2 | -2.07 (crosses two papers) | [DB12] panjabi1991t p. 895; panjabi1992 pp. 301-304 |
| facet_area_inf | 90.4 -> 126.9 mm2 | +1.37 | [DB12] panjabi1993f p. 1302 |
| pedicle_incl_trans (PDIt) | 5.0 -> 2.5 deg | -0.82 (crosses two papers) | [DB12] panjabi1991t pp. 894-895; panjabi1992 pp. 301-304 |
| endplate | 39.0 -> 41.2 mm | +0.79 (crosses two papers) | [DB12] panjabi1991t p. 892; panjabi1992 pp. 301-304 |
| canal_area | 280 -> 320 mm2 | +0.67 (crosses two papers) | [DB12] panjabi1991t p. 893; panjabi1992 pp. 301-304 |

Other series at T12/L1 (each its own material):

| Series | Step at T12 -> L1 | Source |
|---|---|---|
| [DB] Singapore | TPW 41.0 -> 53.6; pedicle-axis chord 31.5 -> 41.4; pedicle width 7.55 -> 5.55; SCA 177.8 -> 200.0 mm2; the pedicle's sagittal tilt changes sign | tan2004 pp. 140-141, Table 1; p. 143 |
| [cad, CT] zindrick1987 | transverse angle -4.2 -> 10.9 deg; sagittal angle 11.6 -> 2.4 deg; pedicle-axis depth 38.6 -> 50.7 mm; width 7.1 -> 8.7 mm | zindrick1987 Tables 1, 3-5, pp. 161-165 |
| [DB] China | width 8.3 -> 7.0 mm; chord LI 42.9 -> 49.5 mm, the largest step; inclination about -2.5 -> 3 deg | hou1993 Tables 1, 3, pp. 1852-1853 |
| [DB] Taiwan | width 7.55 -> 6.45, height 15.1 -> 13.65 mm; sagittal angle 10.7 -> 6.1 deg | lien2007 p. 1218, Tables 1-2 |
| [CT] Vermont | transverse angle about 0 -> about 12 deg (note's reading of Fig. 6; the text keeps L1 with 0-10 deg) | krag1988 p. 31, Fig. 6; p. 30 |
| [CT] North India | upper end-plate width +3.2 mm in men (36.99 -> 40.15); interfacet distance +2.2 mm (15.12 -> 17.27) | yadav2020 pp. 177-178, Tables 2-3 |
| [CT] Turkey | no step: every body height, pedicle diameter and angle rises smoothly T11 to L2 | duman2026 pp. 7-8, Tables 1-2 (note's Inference) |
| [AP] Portland adults | IPD 23.2 -> 25.0 mm | hinck1966 p. 142, Table IA |

Pearls and pitfalls:

- The facet switch is the least reliable of the T12 cues in a single spine: the SEM of S at the T12-L1 joint is 8.2
  to 9.5 deg against 0.9 to 2.8 at T1-T10, and Malmivaara's superior T12 angle (98 deg) sits against Panjabi's 70
  [DB12] (panjabi1993f p. 1303, Tables 6-7; p. 1308, Table 10). The note reads spreads of about 28 to 33 deg, so the
  switch may sit one joint high or low (panjabi1993f note).
- By size the T12-L1 facet joint is still small (inferior T12 width 9.5/9.8 mm, area 90.8/90.0 mm2); the size jump
  comes at L1-L2 (panjabi1993f pp. 1301-1302, Tables 3-4).
- A 12th rib was hypoplastic (under 4 cm) in 55 of 517 Turkish adults (10.64%) and absent in 22 (4.26%; 4 of 277
  men, 18 of 240 women), sides not reported [CT] (duman2026 p. 10, Table 5). The authors warn that top-down and
  bottom-up counts then disagree on planning images and on intraoperative fluoroscopy and lead to wrong-level
  surgery (duman2026 pp. 12-13).
- The lower T12 end plate is deeper posteriorly (1.82 mm) than L1's, breaking the caudal trend; the authors suggest
  measurement error on a shallow end plate or nearby fractures, since T12-L1 is a common injury level [CT]
  (vanderhouwen2009 pp. 36-38).
- 50 to 60% of spinal column injuries are at the thoracolumbar junction, the commonest site of traumatic and
  osteoporotic compression fractures (duman2026 p. 2). Inference: an anterior wedge at T12 or L1 is as likely a
  fracture as anatomy.

## L1

What sets it apart:

- Lumbar facets from its top: superior S 139.1/134.2 deg against T12's 72.5/67.4; its inferior facets have the
  largest S of the column (152.1/154.8), 15 to 17 deg off L2's superior facets (135.4/139.7); IFWs/IFWi exceeds 1
  at L1 alone (1.06) [DB12] (panjabi1993f p. 1303, Tables 6-7; p. 1302, Table 5).
- The narrowest lumbar end plates and transverse processes: EPWu 41.2, EPWl 43.3, TPW 71.2 mm; the tallest and
  narrowest pedicles (height/width 2.00 right, 1.72 left); the smallest pars area [DB12] (panjabi1992 pp. 301-304,
  Tables 2-5). The same holds in other series: end plates 41.09 x 31.04 mm [review] (bonczar2024 p. 5, Table 2);
  41.8 superior and 44.8 inferior [CT] (frontphys2026 p. 5, Table 2); body width 40.3 mm [CT] (moncadahabib2025
  pp. 4-5, Tables 1-2).
- A body taller behind than in front, the lumbar end of the thoracolumbar kyphosis:
  - 27.2 against 25.1 mm [CT] (frontphys2026 p. 5);
  - 26.9 against 24.3 mm [CT] (moncadahabib2025 pp. 4-5);
  - 26.57 against 24.54 mm [review] (bonczar2024 p. 5, Table 2);
  - anteriorly wedged on lateral films, anterior b 25.4 against posterior d 27.1 mm, significant [LAT] (gilad1985
    p. 119).
- The end plate widens caudally within the body, by 4.3 mm in men (the largest of the series) and 3.3 in women;
  the upper L1 end plate is the flattest in the coronal plane (175.7 deg) [CT] (chen2011 Tables 1-3,
  pp. 1816-1818).
- The narrowest lumbar pedicles in most series:
  - 7.0 mm, narrower than T12 and L2 in every one of 40 columns, which the Discussion calls the smallest pedicle
    though T9 and T10 are narrower in its own table [DB] (hou1993 pp. 1851-1852, Table 1);
  - 8.52 mm, with the most narrow pedicles of the lumbar spine: under 4.5 mm in 4 of 503 skeletons (0.80%) and
    under 5.5 mm in 24 (4.77%) [DB] (yu2015 p. 1640; Tables 3-5, pp. 1642-1645);
  - 7.05 mm by direct measure in men, with two specimens under 5 mm at the upper levels [cad] (mitra2002 p. 454;
    p. 455, Table 1);
  - 6.7 mm right, 7.0 left [CT] (moncadahabib2025 pp. 4-5);
  - width/height about 0.5 to 0.56, the tallest and narrowest lumbar pedicle [cad] (olsewski1990 p. 545, Table I).
- The canal, by population:
  - the widest mid-sagittal canal of the lumbar spine in Indian MRI (14.28 men, 14.38 women) [MRI] (ahmed2019
    pp. 22-24), Nigerian dry bone [DB] (amonookuofi1985 p. 76), Bosnian CT (19.06 mm) [CT] (cizmic2023 pp. 202-203)
    and Italian MRI (18.7 mm) [MRI] (italianmri pp. 4-5, Tables 2-5);
  - the narrowest interpedicular distance in every series that measures it: 22.6 men, 21.3 women [AP]
    (amonookuofi1982 p. 228, Table 1); 24.06 and 21.64 [AP] (chaudhary2015 p. 34, Table I); 24.78 [CT] (cizmic2023
    p. 202); adult 25.0 [AP] (hinck1966 p. 142, Table IA).
  - The authors of three series explain the wide L1 canal by Davis's thoracolumbar "mortice": the functional switch
    from stiff thoracic to mobile lumbar spine, the conus and the lumbar enlargement housed here, and the dorsal
    shift of the cord where thoracic convexity turns to lumbar concavity (amonookuofi1985 p. 76; ahmed2019 p. 24;
    cizmic2023 pp. 204-205).

| Measure | L1 -> L2 | step/SD (Inference) | Material, source |
|---|---|---|---|
| facet_area_sup | 98.0 -> 143.1 mm2 | +1.25 | [DB12] panjabi1993f p. 1302 |
| facet_h_sup | 12.4 -> 14.6 mm | +1.08 | [DB12] panjabi1993f p. 1301 |
| transverse_width | 71.2 -> 76.1 mm | +0.90 | [DB12] panjabi1992 pp. 301-304 |
| facet_area_inf | 126.9 -> 152.2 mm2 | +0.85 | [DB12] panjabi1993f p. 1302 |
| canal_area | 320 -> 281 mm2 | -0.67 | [DB12] panjabi1992 pp. 301-304 |
| every body and pedicle measure | | under 0.7 | [DB12] panjabi1992 pp. 301-304 |

Pearls and pitfalls:

- Nothing separates L1 from L2, or L2 from L3, at P < .05 in Panjabi's lumbar tables [DB12] (panjabi1992
  pp. 301-304, Tables 2-5). In men L1 and L2 are indistinguishable by IPD (22.6 against 22.7 mm) and pedicle index
  [AP] (amonookuofi1982 p. 228; p. 229). The note on arockiaraj2025 calls L1 and L2 the hardest adjacent pair to
  separate by pedicle measures (arockiaraj2025 p. 316, Table 2, note).
- The canal cue depends on the population: L1 is not the widest in Chinese CT, where L5 is (cited in cizmic2023
  p. 203), nor in Nigerian women on CT (alonge2021 pp. 73-74).
- Routine low-back CT usually omits L1 [CT] (olsewski1990 p. 546). Chest CT may stop near L1-L2 (duman2026 p. 3,
  note).
- In Marfan syndrome the L1 IPD (29.5 mm) equals a normal L5 (29.7 mm) [AP] (ahn2001 p. 68). The note calls Marfan
  a numbering pitfall, not only a diagnosis (ahn2001 note).
- Inference: an anterior compression of L1 (eisenstein1977 p. 177: 17 of 443 skeletons, levels not given) imitates
  the normal posterior-taller body; never name L1 from its wedge alone.
- Seven of the 18 interpedicular stenoses in Eisenstein's skeletons were at L1 (eisenstein1977 p. 175, Table II,
  note).

## L2

What sets it apart: little, alone.

- In Panjabi's lumbar tables L2 has the smallest pedicle width (8.2 mm by the text), area (83 mm2) and convergence
  (PDIs 14.1 deg); its canal area (281 mm2) is near L3's minimum [DB12] (panjabi1992 p. 301; Tables 3-4).
- The superior facets jump in size at L2: height 14.6/14.6 mm and area 138.0/148.2 mm2, against the inferior L1
  facets [DB12] (panjabi1993f pp. 1301-1302, Tables 2-5).
- The most sagittal facets of the lumbar spine in Israeli CT, superior transverse facet angle 29 to 34 deg [CT]
  (masharawi2021 p. 6, Table 2).
- The tallest posterior body: 28.1 +/- 2.6 mm [CT] (frontphys2026 p. 5, Tables 2-3); 27.02 mm [review]
  (bonczar2024 p. 6, Table 3).
- The widest lower end plate of chen2011's run (44.5/38.3 mm) and the largest superior-inferior coronal angle
  difference (4.2 deg) [CT] (chen2011 Tables 1, 3).
- Pedicles nearly the same as L1's: 8.66 against 8.52 mm [DB] (yu2015 pp. 1642-1643, Tables 3-4); 7.0 mm with
  height 12.3 to 12.5 [CT] (moncadahabib2025 pp. 4-5); width barely above L1 [cad] (olsewski1990 p. 545);
  isthmus 10.0/9.6 against L1's 9.9/8.7 mm [DB] (robertson2000 p. 711, Table 1).
- The L1-2 disc is the thinnest in every group of twomey1985 [cad] (twomey1985 p. 497, Table 2) and the second
  smallest in bach2019 [CT] (bach2019 pp. e113-e114, Tables 6-8).

| Measure | L2 -> L3 | step/SD (Inference) | Material, source |
|---|---|---|---|
| transverse_width | 76.1 -> 85.7 mm | +1.41 | [DB12] panjabi1992 pp. 301-304 |
| facet_w_sup | 11.2 -> 13.9 mm | +0.91 | [DB12] panjabi1993f p. 1301 |
| pedicle_w | 8.2 -> 10.1 mm | +0.86 | [DB12] panjabi1992 pp. 301-304 |
| interfacet_w_sup | 26.4 -> 28.6 mm | +0.67 | [DB12] panjabi1993f p. 1302 |
| facet_sag_inf (S) | 139.6 -> 126.9 deg | -0.64 | [DB12] panjabi1993f p. 1303 |

Pearls and pitfalls:

- Inference: L2 is named by count from L1 or from L5, never by its own measures; its strongest single step
  (TPW into L3, 1.41 SD) needs a transverse-process measurer that schwingcheck does not have yet (README "The
  measures").
- griffith2016's L2 is its only level with no unadjusted sex difference in canal area (P 0.212) [CT] (griffith2016
  p. 675, Tables 2-4).
- moncadahabib2025's L2 body-width minimum (28.6 mm) sits below L1's minimum, about 3.2 SD out by the note's
  reckoning, probably an outlier (moncadahabib2025 pp. 4-5, note).

## L3

What sets it apart:

- The waist of the lumbar canal in most series:
  - narrowest canal depth (17.5 mm) and area (280 mm2), largest lower end-plate area (1290 mm2), local peaks of
    TPW (85.7 mm) and convergence, tied by the authors to the lordotic apex [DB12] (panjabi1992 p. 301; p. 304;
    Tables 2-5);
  - narrowest mid-sagittal diameter, 12.63 men and 12.12 women [MRI] (ahmed2019 p. 22, Table 1);
  - narrowest antero-posterior diameter, 15.25 women and 14.92 men by Table 3 (the text swaps the sexes) [CT]
    (alonge2021 pp. 73-74);
  - narrowest male canal, 14.9 mm [DB] (amonookuofi1985 p. 71, Table 1; p. 76);
  - narrowest mid-sagittal gap, 16.66 mm both sexes [CT] (cizmic2023 p. 202);
  - narrowest canal area and depth in both sexes [CT] (griffith2016 p. 673; Figure S1);
  - canal depth 14.69 mm and area 213.87 mm2, both minima [review] (bonczar2024 p. 7, Table 4).
- The body about even front and back: 27.1 against 27.3 mm, not significant [CT] (frontphys2026 p. 5); 26.83
  against 26.67 mm [review] (bonczar2024 p. 7); 25.6 against 26.1 mm [CT] (moncadahabib2025 pp. 4-5). Inference:
  the body turns from posterior-taller at L1-L2 to anterior-taller at L5 through an even L3.
- The pedicle first widens clearly at L3: 11.7 mm in men, 9.6 in women [cad] (olsewski1990 p. 545, Table I); 9.4 mm,
  above L2 [cad] (otsuki2021 p. 6, Table 2); the coronal tilt of the pedicle's section first rises significantly
  (18.04 deg) [CT] (makino2012 p. 1517; p. 1518, Table 1).
- The lowest lumbar pedicle height: 14.4 mm [DB12] (panjabi1992 Tables 2-5); 14.7 mm pooled [DB] (hou1993 p. 1851,
  Tables 1-3).
- The longest spinous process with L2 (71.7 mm) [DB12] (panjabi1992 Tables 2-5); 65.67 mm [review] (bonczar2024
  p. 7); and the transverse-process peak, 71.4 mm in Singaporean bone [DB] (tan2004 Table 1, pp. 140-141).
- Fawcett's frontal outline of the facet tips, cited by Panjabi: an upright rectangle at L3, a square at L4 and a
  horizontal rectangle at L5 (IFW/IFH 0.90, 1.16, 1.44); the superior acute sagittal angle rises 48, 58 and 61 deg
  from L3 to L5 [DB12] (panjabi1993f pp. 1307-1308; p. 1302, Table 5; p. 1303, Table 6).

| Measure | L3 -> L4 | step/SD (Inference) | Material, source |
|---|---|---|---|
| pedicle_w | 10.1 -> 14.1 mm | +2.45 | [DB12] panjabi1992 pp. 301-304 |
| interfacet_h | 32.0 -> 28.4 mm | -1.07 | [DB12] panjabi1993f p. 1302 |
| interfacet_w_inf | 29.1 -> 34.8 mm | +1.03 | [DB12] panjabi1993f p. 1302 |
| facet_sag_inf (S) | 126.9 -> 113.7 deg | -0.71 | [DB12] panjabi1993f p. 1303 |
| endplate | 44.1 -> 46.6 mm | +0.69 | [DB12] panjabi1992 pp. 301-304 |
| transverse_width | 85.7 -> 79.4 mm | -0.58 | [DB12] panjabi1992 pp. 301-304 |

Panjabi's lower pedicle width separates L3 from L4, the only significant L3/L4 difference in his lumbar tables
[DB12] (panjabi1992 Tables 2, 4, 6).

Pearls and pitfalls:

- Disagreement on where the waist lies, L3 or L4:
  - L4 in women: Nigerian dry bone (14.1 mm at L4) [DB] (amonookuofi1985 p. 73, Table 1); Bosnian CT, where Table 5
    puts L4 lower than L3 in women (17.14 against 17.21) [CT] (cizmic2023 p. 202);
  - L3 and L4 indistinguishable in Indian men (13.45 and 13.29 mm) [CT] (yadav2020 pp. 177-178);
  - L2 to L4 as one narrow waist in dry bone [DB] (eisenstein1977 pp. 174-175);
  - in Italian MRI the minimum is 16.9 mm at both L3 and L4 [MRI] (italianmri pp. 3-4, Tables 2-3).
  Inference: a canal minimum places a vertebra at L3 or L4, not at one of them.
- The canal shape at L3 is mixed in Nigerian CT, about two thirds oval and one third trefoil [CT] (alonge2021
  pp. 74-75). Inference: a trefoil canal at L3 must not force an L5 label.
- About 33% of men and 46% of women in ahmed2019 fall under 12 mm at L3 by the note's normal approximation
  (ahmed2019 p. 22, note); the authors, after Kapoor, call L3 the pivot of the level-to-level change and the level
  likeliest to suffer stenosis (ahmed2019 pp. 23-24).

## L4

What sets it apart:

- The pedicle jumps: width 14.1 mm in Panjabi, against 10.1 at L3 [DB12] (panjabi1992 Tables 2, 4, 6); width and
  height nearly equal, 13.19 against 13.81 mm, the two curves crossing just below L4 [DB] (yu2015 p. 1641,
  Figure 2); the only level with no significant difference between transverse and sagittal width (9.01, 9.36 mm)
  [CT] (makino2012 p. 1519, Fig. 3); the first clear step of the pedicle angle (18.6 deg) [CT] (moncadahabib2025
  pp. 4-5); transverse width 12.9 mm [cad, CT] (zindrick1987 pp. 161-163).
- The widest lower end plate (49.5 mm), the deepest upper end plate (35.5 mm) and the largest upper end-plate area
  (1239 mm2) of Panjabi's lumbar tables [DB12] (panjabi1992 Tables 2, 4, 6); the largest lower end plate in the
  pooled review, 50.63 x 34.07 mm [review] (bonczar2024 p. 8, Table 5).
- The body slightly taller in front: 27.6 against 26.3 mm [CT] (frontphys2026 p. 5); 26.86 against 25.76 mm
  [review] (bonczar2024 p. 8); about equal, 25.4 against 25.0 mm [CT] (moncadahabib2025 pp. 4-5).
- The interpedicular distance begins its steep rise: 27.32 mm [CT] (cizmic2023 p. 202); adult 26.9 mm [AP]
  (hinck1966 p. 142).
- The lower interfacet width is 36 to 37 mm at L4 against 46 to 49 at L5 [CT] (masharawi2021 p. 6, Table 2); the
  note calls this 10 to 11 mm jump (1.4 to 1.6 pooled SD) the strongest L4/L5 step of the series (masharawi2021
  note).
- The L4-5 disc is the thickest in both sexes and both age groups of twomey1985 [cad] (twomey1985 p. 497, Table 2),
  with the tallest middle (9.31 mm) and posterior (4.88 mm) height in shin2024 [CT] (shin2024 p. 4; Tables 2, 6, 7).

| Measure | L4 -> L5 | step/SD (Inference) | Material, source |
|---|---|---|---|
| pedicle_w | 14.1 -> 18.6 mm | +1.95 | [DB12] panjabi1992 pp. 301-304 |
| pedicle_h | 15.4 -> 19.6 mm | +1.72 | [DB12] panjabi1992 pp. 301-304 |
| pedicle_incl_sag (PDIs) | 16.5 -> 24.5 deg | +1.15 | [DB12] panjabi1992 pp. 301-304 |
| transverse_width | 79.4 -> 92.5 mm | +1.01 | [DB12] panjabi1992 pp. 301-304 |
| interfacet_w_inf | 34.8 -> 40.6 mm | +0.91 | [DB12] panjabi1993f p. 1302 |
| facet_trans_sup | 81.2 -> 85.5 deg | +0.79 | [DB12] panjabi1993f p. 1302 |
| canal_w | 25.4 -> 27.1 mm | +0.72 | [DB12] panjabi1992 pp. 301-304 |
| facet_sag_inf (S) | 113.7 -> 126.3 deg | +0.66 | [DB12] panjabi1993f p. 1303 |
| h_post | 24.1 -> 22.9 mm | -0.34 | [DB12] panjabi1992 pp. 301-304 |
| endplate, endplate_lower | +0.7, -0.1 mm | +0.17, -0.02 | [DB12] panjabi1992 pp. 301-304 |

Panjabi separates L4 from L5 by pedicle width, height and lower area and by TPW at P < .05 [DB12] (panjabi1992
pp. 301-304, Tables 2-5).

Pearls and pitfalls:

- L4 and L5 are the most variable levels of the IPD profile (adult SD 3.0 and 3.7 mm), and in normal adults L4 and
  L5 are occasionally smaller than L1 to L3, so a lumbar reversal alone is weak evidence [AP] (hinck1966 p. 145;
  Tables II, III).
- L4 was the commonest level of mid-sagittal stenosis in dry bone (13 of 28 stenotic vertebrae, the note's reading
  of Table III), with an occasional trefoil canal [DB] (eisenstein1977 p. 175, Table III; p. 177). The one
  unilateral pars defect of the series was at L4, left, with an enlarged left inferior facet (eisenstein1977
  p. 178, Fig. 7).
- An L4 IPD over 33 mm is the best single screen for Marfan syndrome (sensitivity 75%, specificity 95% as stated)
  [AP] (ahn2001 p. 67; p. 68; p. 70).
- L4-L5 is the slip level of degenerative spondylolisthesis by selection in masharawi2021: the foramen height there
  falls about 3.9 mm (15.78 -> 11.84 in men, 15.30 -> 11.46 in women), and the women's L4 facets are more sagittal
  (left transverse angle about 33 against 41 deg) [CT] (masharawi2021 pp. 5-9, Tables 2-5).
- Within the L4 body the superior end plate is larger than the inferior in women by 11% (P < 0.001) [MRI]
  (tang2016 p. 4119; p. 4123).
- A screw sized by axial transverse width can be too wide at L4: 7 of 67 pedicles with a transverse width of 8 mm or
  more had a minimum width under 6 mm [CT] (makino2012 p. 1519, note).

## L5

What sets it apart (the strongest caudal signature of the column):

- The widest pedicles: 18.6 mm [DB12] (panjabi1992 Tables 2-5); 18.33 mm, range 9.09 to 29.06 [DB] (yu2015
  pp. 1641-1645); 18.0 mm [cad, CT] (zindrick1987 pp. 161-162); 21.1 mm men, 18.4 women [cad] (olsewski1990
  pp. 544-545, Table I); 17.6 mm [DB] (lien2007 p. 1218, Table 1); 21.6/21.5 mm [DB] (robertson2000 p. 711,
  Table 1); 16.19 mm direct [cad] (mitra2002 p. 455).
- A pedicle wider than tall in most series:
  - the only lumbar level so [cad] (olsewski1990 pp. 544-545);
  - transverse 18.0 against sagittal 14.0 mm, the only level with transverse above sagittal [cad, CT]
    (zindrick1987 pp. 161-162);
  - 18.33 against 13.67 mm [DB] (yu2015 pp. 1641-1645);
  - 12.86 against 8.95 mm [CT] (makino2012 p. 1519);
  - width/height 1.41 by the note [DB] (lien2007 p. 1218, note);
  - the lowest pedicle height of the lumbar spine, 10.2 mm [CT] (moncadahabib2025 pp. 4-5); 8.9 to 9.9 mm [CT]
    (masharawi2021 Tables 2-5).
  Disagreement: taller than wide in Chinese bone (width 12.9, height 19.8 mm) [DB] (hou1993 pp. 1852-1853,
  Tables 1-3), and near round, both about 19 mm, in Panjabi [DB12] (panjabi1992 pp. 301-304, Tables 2-5).
  Inference: the shape depends on where and along which axis the height is taken. Series that take the narrowest
  point find L5 height still falling (yu2015 p. 1645, Table 5), and the coaxial view shows L5 as an oblique ellipse
  whose isthmus is far narrower than its bounding width (robertson2000 p. 711, Table 1). Define the shape on the
  mask and calibrate it on your own data.
- An oblique pedicle: an ellipse tilted 55.0/50.3 deg whose isthmus is only 13.2/14.0 mm though its width is
  21.5 mm, and whose lateral border projects onto the lateral border of the L5 body [DB] (robertson2000 p. 711,
  Table 1; pp. 713-714).
- The steepest convergence, jumping at L4/L5: 14 -> 35 deg [cad] (busscher2010 Figs. 5-8, pp. 1110-1112);
  17.47 -> 28.23 deg [CT] (arockiaraj2025 p. 316, Table 2); about 18.5 -> 30 deg [DB] (hou1993 Tables 1-3); about
  28 deg [CT] (krag1988 p. 31, Fig. 6); 29.8 deg [cad, CT] (zindrick1987 p. 161); 29.33 deg direct [cad] (mitra2002
  p. 456).
- A body taller in front than behind:
  - 22.0 against 20.0 mm, the only level of the Singaporean table with VBHa above VBHp (ratio 1.10) [DB] (tan2004
    pp. 140-141, Table 1);
  - VBHp falls 3.1 mm and VBHa rises 1.7 mm from L4 [cad] (busscher2010 p. 1107, Table 3);
  - anterior above posterior by 3.1 mm [CT] (frontphys2026 p. 5);
  - 26.2 against 22.5 mm [CT] (moncadahabib2025 pp. 4-5);
  - 27.44 against 24.11 mm [review] (bonczar2024 p. 9, Table 6);
  - anterior b 28.3 against posterior d 25.7 mm on lateral films, significant [LAT] (gilad1985 pp. 119-120).
- The widest body and end plates (50.7 and 52.4 mm [CT] frontphys2026 p. 5; body width 49.5 mm [CT]
  moncadahabib2025 pp. 4-5), with a lower end plate smaller than the upper: by 12 to 16% in area [MRI] (tang2016
  p. 4119; p. 4123); 46.93 against 48.79 mm in men [CT] (yadav2020 pp. 177-178, note); a dip against L4 in
  Singaporean bone [DB] (tan2004 Table 1).
- The widest canal and interpedicular distance: SCW 27.1 mm and SCA 330 mm2 [DB12] (panjabi1992 p. 304); IPD 28.7
  men, 28.4 women [AP] (amonookuofi1982 p. 228); 31.34 and 29.01 [AP] (chaudhary2015 p. 34); 31.94 [CT]
  (cizmic2023 p. 202); adult 29.7 [AP] (hinck1966 p. 142). The L4 -> L5 rise is +2 to 3 mm in dry bone [DB]
  (eisenstein1977 p. 174, Table I), +4.19 men and +3.30 women [AP] (chaudhary2015 p. 34), +2.7 and +3.0 [AP]
  (amonookuofi1982 p. 228).
- The most coronal superior facets (transverse facet angle 43 to 47 deg), the widest facets (17.5 to 19.5 mm) and
  the widest lower interfacet span (46 to 49 mm) [CT] (masharawi2021 Tables 2-5). Its inferior facets articulate
  with the sacrum and copy no measured superior facet; L5 has the largest IFWi (40.6 mm) and a superior facet area
  (211.9 mm2) like C2's [DB12] (panjabi1993f p. 1306; Tables 5, 7). Its inferior facets stand closer to the sagittal
  plane than L4's (|S| 127.6/125.1 against 112.7/114.7 deg) [DB12] (panjabi1993f p. 1303, Table 7).
- The widest transverse processes, TPW 92.5 mm [DB12] (panjabi1992 p. 304).
- A trefoil canal, "always" at L5 by p. 177 and "almost invariably" by p. 179, from laminar bars; 66 of 443
  skeletons (14.9%) had one [DB] (eisenstein1977 p. 177; p. 179).
- On the lateral film the posterior canal limit at L5 lies just anterior to the radiolucent lake of the spinous
  process, further back than clinicians usually place it [DB films] (eisenstein1977 p. 175; p. 178).

Pearls and pitfalls:

- Spondylolysis: 9 of 443 skeletons (2.0%) had a bilateral L5 pars defect, one with a completely bifid spinous
  process; all 9 of the 10 defects at L5 were bilateral [DB] (eisenstein1977 p. 177).
- The sagittal angle of the L5 pedicle is bimodal: caudad in 12 of 83 elderly cadaver pedicles (8 of 46 male, 4 of
  37 female; both pedicles of a vertebra always the same way) against 2 of 94 on films of living patients aged 20 to
  50 [cad, LAT] (olsewski1990 pp. 544-546). zindrick1987's L5 is the only level with a caudal mean sagittal angle,
  -1.8 deg (range -8.0 to +8.0) [cad, CT] (zindrick1987 p. 162). The authors advise separate means for cephalad and
  caudad pedicles (olsewski1990 pp. 546-547).
- AP films underestimate the L5 pedicle, width 16.6 against 20.1 mm and height 13.8 against 16.2 mm, even on a
  disarticulated spine, possibly because the lateral L5 border is unclear [cad film] (olsewski1990 p. 548; p. 544,
  Table II). On coaxial views the L5 lateral border is occasionally unseen [DB film] (robertson2000 p. 713).
- L5 carries the largest spread of almost every measure: IPD SD 3.7 mm [AP] (hinck1966 Table II, p. 145); male IPD
  SD 5.9 mm, giving a printed range of 13.34 to 49.34 mm [AP] (chaudhary2015 p. 34); the largest SDs of every body
  and canal measure [CT] (griffith2016 Tables 2-5; moncadahabib2025 Tables 1-2). The largest single mid-sagittal gap
  of cizmic2023, 30.80 mm in a man, is 4.6 SD above the male mean; the note asks whether it is a transitional or
  misnumbered segment (cizmic2023 p. 202, note). bonczar2024 says its pooled L5 may include transitional segments
  (bonczar2024 p. 10).
- The L5/S1 disc is the most wedged: anterior 11.92/11.36, posterior 5.27/5.23 mm, and the smallest foramen
  (14.30/14.36 mm) [CT] (bach2019 p. e113, Table 6); anterior 10.76 with posterior 3.80 mm and the smallest foramen
  [CT] (shin2024 pp. 3-5, Tables 2, 4); a wedge of about 15 deg supine [CT] (vanderhouwen2009 p. 39, Fig. 3).
- Osteophytosis worsens from L1 to L5 in dry bone (eisenstein1977 p. 175, note).
- The CT gantry could not always be set parallel to the L5-S1 end plates, so L5 axial angles carry extra error [CT]
  (olsewski1990 p. 543); 23 of 109 MRI subjects lacked oblique slices of the L5/S1 end plates [MRI] (tang2016
  p. 4117).

## S1

What sets it apart:

- Its lower surface collapses and the "disc" below it is about 3.5 mm: lower body width 46.93 -> 30.78 mm and depth
  31.66 -> 22.78 mm from L5's lower surface to S1's in men; disc below S1 3.55 mm; S1 has the minimum canal depth
  (11.00 men, 11.19 women), the maximum interfacet distance (27.91, 26.89) and the minimum foramen (5.77, 5.80); its
  upper width (49.08 mm) barely exceeds L5's (48.79) [CT] (yadav2020 pp. 177-178, Tables 2-3). The note calls the
  S1 lower surface and the disc below the strongest single sign of S1, and reads them as the fused S1-S2 junction
  (yadav2020 note).
- In Italian MRI every measure but the dural sac ratio drops from L5 to S1: body depth 29.6 -> 22.4 mm, canal
  17.3 -> 14.9 mm, sac 12.9 -> 9.9 mm; S1 has the largest pooled SD of every measure; the S1 lines are drawn
  obliquely along the sacral inclination [MRI] (italianmri pp. 3-5, Tables 2-5, Figure 2).
- The S1 superior end plate: area 14.63 +/- 2.39 cm2, width 5.19, depth 3.57 cm; no other series in tang2016's
  comparison gives it [MRI] (tang2016 p. 4120; pp. 4127-4128).
- The S1 superior end plate is concave (middle 1.42, posterior 1.62 mm) and narrower (41.2 mm) than L5's inferior
  (44.1 mm) [CT] (vanderhouwen2009 p. 37, Fig. 2; p. 38).
- On films of dry bone the S1 pedicle is a triangle whose lateral side merges into the ala; on PA films rotated 10
  to 15 deg its superior and medial borders show; its medial image is a trabecular line often 3 to 4 mm inside the
  true wall; its inferior limit is the upper margin of the S1 foramen; its lateral border is always lateral to the
  S1-S2 foramen and never seen on coaxial views [DB film] (robertson2000 pp. 712-714, Figures 8-9).

Pearls and pitfalls:

- S1 is outside schwingcheck's pool (README "The table") and unmeasured in most of the set: Panjabi kept no sacrum
  (panjabi1992 p. 299); busscher2010 had S1 in its specimens but did not measure it (busscher2010 p. 1105);
  masharawi2021 uses the S1 pedicle only as the lower border of the L5-S1 foramen (masharawi2021 p. 3); hinck1966
  gives no sacral norms for want of a sample (hinck1966 p. 142).
- Inference: a degenerated L4-L5 or L5-S1 disc can imitate the 3.5 mm S1-S2 "disc" (yadav2020 Table 3, p. 178);
  3 of 54 young men in tang2016 had a Pfirrmann V disc at L5/S1 (tang2016 p. 4117). Require the collapse of the
  body's lower surface as well before calling an instance S1.

## L6, a lumbarised S1, and a sacralised L5

What the set holds:

- Counts only, all from one dry-bone series of 443 South African skeletons [DB] (eisenstein1977 p. 177; p. 180):
  - lumbarisation of S1, 9/443 (2.0%);
  - persistent S1-S2 zygapophysial joints, 16/443 (3.6%), which the author calls possibly the least form of
    lumbarisation;
  - a true sixth lumbar vertebra, 2/443 (0.45%), both Sotho (2/168);
  - a true transitional lumbosacral vertebra, 1/443, Zulu;
  - sacralisation of L5, 8/443 (1.8%), none among 35 Caucasoid women;
  - all transitional variation 36/443, printed as 8% (the plain sum of the five rows);
  - a sacro-transverse joint, patent or ankylosed, 10/443 (2.3%), with notably smaller lumbosacral facets on that
    side.
- A lumbosacral transitional vertebra of unstated type in 5 of 32 adults with Marfan syndrome (15.6%) [AP, LAT]
  (ahn2001 p. 68).
- Nothing else: no paper says how an L6 was told from a lumbarised S1, none grades a transitional vertebra by
  Castellvi's or any scheme, none measures an L6 or a transitional segment, and none counts them in a living
  general population (eisenstein1977 p. 177; italianmri p. 2 and masharawi2021 p. 2 excluded them; bonczar2024
  p. 10 did not).
- The note reads 2,166 measured lumbar vertebrae as 443 x 5 - 49, so the two L6 were not entered as a sixth level
  (eisenstein1977 p. 177, note).

Inference, what each does to the measures and the count (no paper measures it):

- An L6 or a lumbarised S1 carries the caudal signature (wide, round or wide-oval pedicles, the IPD jump, anterior
  wedge, coronal facets) one level down; the true L5 then reads as an L4-L5 intermediate. Counting up from the
  sacrum names everything above one level too low; counting down from C2 names everything correctly and leaves a
  sixth lumbar-type segment.
- A sacralised L5 leaves four free lumbar-type segments; counting up from the sacrum names everything above one
  level too high. The fused side shows smaller lumbosacral facets (eisenstein1977 p. 177).
- An L6 sits over a sacrum of five segments, a lumbarised S1 over a sacrum of four.

## T13, and a rib on the first lumbar-type vertebra

What the set holds:

- No count of T13, of 13 thoracic vertebrae or of 13 rib pairs anywhere; duman2026 names them in its methods and
  never reports them (duman2026 p. 5).
- A lumbar (supernumerary) rib in 12 of 517 Turkish adults (2.32%; 10 of 277 men, 2 of 240 women), the bearing
  vertebra not named, with no criterion against an unfused transverse process or a T13; Fig. 5B shows it as a
  separate bony element jointed to a transverse-process tip [CT] (duman2026 p. 10; p. 5).
- No measurement of a T13 in any paper.

Inference: a rib on the first lumbar-type vertebra is an L1 with a lumbar rib when that vertebra has lumbar-type
superior facets (panjabi1993f p. 1304) and no costovertebral facet on its body (panjabi1991t p. 895), and a T13
candidate when it has thoracic facets, a costovertebral body facet and the rib, with 13 rib-bearing vertebrae
counted down from T1. Since duman2026 would file any rib below the 12th as a lumbar rib, a T13 cannot be commoner
than 12/517 in that population; the set gives no lower bound.


# Part 2. The playbook

Part 2 turns the atlas into an order of work. Each step is an instruction, then why, then its sources. A rule that
no paper states but that I build from several is marked "Inference:" and names what it is built from. Two things
hold throughout:

- No paper in the set gives a rule for numbering a spine that has a transitional segment, and none reports a
  measure taken on one (eisenstein1977 p. 177; italianmri p. 2 and masharawi2021 p. 2 excluded them; the LEV line
  of every other note). Every rule below for such a spine is therefore Inference.
- Name a vertebra from its place in a sequence, never from one value. Neighbours from C3 to C5 and from T4 to T9
  differ by about one SD or less [DB12] (panjabi1991c pp. 863-865, Tables 2-6; panjabi1991t p. 892, Table 3) and
  [LAT] (gilad1985 p. 118, Table 1), and L1 against L2 is unresolved by every pedicle series (olsewski1990 p. 544,
  Table I; makino2012 p. 1518, Table 1; yu2015 p. 1645, Table 5).

## 2A. Naming every instance on a 3D CT

### Step 1. Check the volume

1. Read the field of view from the images, not from the protocol name.
   - Do not call the top instance of a low-back CT L1: routine low-back CT usually left L1 out (olsewski1990
     p. 546). Count from the sacrum and confirm on the scout or a wider series (olsewski1990 p. 546, note).
   - Expect an abdominal CT to miss C7 and a chest CT to stop near L1 or L2 (duman2026 p. 3, note).
   - Record which of C2, the first rib pair, the twelfth rib pair, the sacrum and the iliac crests lie in the
     field, since they decide which anchors exist (Step 4).
2. Read the slice spacing dz, because it sets the error of every length along z. Inference: give h_post
   sigma = sqrt(0.65^2 + (0.41 dz)^2) mm and never less than 1 mm; that is 0.77 at dz = 1 mm, 1.21 at 2.5 mm and
   2.15 at 5 mm. 0.65 mm is the top of the repeat SEM that the note derives from duman2026's ICCs (duman2026 p. 6,
   note); 0.41 dz is the SD of a length between two boundaries each placed uniformly within a voxel
   (sqrt(2) x dz / sqrt(12)).
3. Reslice every vertebra into its own frame (Step 2) rather than trust the scanner's axial plane. The gantry
   could not always be set parallel to the L5-S1 end plates [CT] (olsewski1990 p. 543), and 23 of 109 MRI
   stacks lacked oblique slices of the L5/S1 end plates [MRI] (tang2016 p. 4117).
4. Check thin walls against HU. duman2026 read every value in a bone window (W 1500, L 300 HU) on 0.625 mm
   slices (duman2026 pp. 3-4); vanderhouwen2009 set bone edges at the steepest HU drop beside the local maximum,
   not at a fixed threshold (vanderhouwen2009 p. 35). The porous lateral pedicle wall may threshold away and
   under-read width by up to a voxel (otsuki2021 pp. 6-10, note).

### Step 2. Put each instance in its own frame

1. Fit the frontal plane to the four corners of the posterior body wall. Take z along its anterior normal, x
   left-right through the upper corners, y cranial, and put the origin at the centroid of the upper end plate
   (panjabi1991c p. 862, Figure 1; panjabi1991t p. 889, Figure 1; panjabi1992 p. 299; panjabi1993f p. 1299).
   Why: the posterior wall varied least and was least disturbed by osteophytes (tan2004 p. 139), and end-plate
   references drift with osteoporotic and degenerative change (abbas2021 p. 6).
2. Never measure along the scanner's axes. A left-right chord across a converging pedicle reads about
   1/cos(angle) too wide, and the angle is 18 to 30 deg at L4 and L5 (hou1993 p. 1851, note; moncadahabib2025
   p. 2, note); scanner axes fold lordosis into widths and inclinations (makino2012 p. 1517, note).
3. Take the median plane from the mirror symmetry of the whole instance and check it against the line joining the
   two transverse-process tips (krag1988 pp. 27-28, note). Flag visible axial rotation or lateral slant, which
   chen2011 excluded (chen2011 p. 1815).
4. Take body depth and width at mid-height, the waist, when the norm you compare with was taken there, since that
   keeps border osteophytes out (eisenstein1977 p. 173). Take end-plate depth at the rim when the norm is
   Panjabi's: mid-centrum depth reads 1.2 to 4.1 mm smaller in the neck [DB12] (panjabi1991c p. 868, Table 7;
   panjabi1991t p. 898).

### Step 3. Check that each instance is one vertebra

1. Check that facing end plates match across each disc. Depths matched within about 1 mm, and the upper
   vertebra's lower width was at least the lower vertebra's upper width at 9 of 11 thoracic junctions [DB12]
   (panjabi1991t p. 890, Table 3). Inference (the note's): a large mismatch suggests a missing or extra instance
   or a split.
2. Check that the inferior facets of each instance match the superior facets of the next, in orientation and in
   interfacet width, except C2's superior and L5's inferior facets. Allow about 12 deg at C7-T1, 15 to 17 deg at
   L1-L2 and L4-L5, and about 2.5 mm of interfacet-width mismatch from T11-T12 to L3-L4 [DB12] (panjabi1993f
   p. 1306, Tables 5-7; the tolerances are the note's Inference).
3. Do not read a missing disc gap as a block vertebra by itself: collapsed (Pfirrmann V) discs occurred in 9 of
   327 discs of adults aged 20 to 40, all men [MRI] (tang2016 p. 4117). The set counts no block vertebra; its one
   illustrated hemivertebra is a child's film with focal IPD collapse (hinck1966 pp. 152-153, Fig. 8). Inference:
   an instance about twice the usual height with an end-plate remnant inside it is a block candidate.
4. Keep a separated arch with its body before counting. Spondylolysis was found in 10 of 443 skeletons, nine
   bilateral at L5 and one left-sided at L4 [DB] (eisenstein1977 p. 177). Inference: a segmenter may detach the
   arch of such a vertebra and count it as a piece of its own.
5. In children and adolescents expect unfused neural arches up to 3 to 6 years and five secondary centres from
   puberty to about 25 years (bonczar2024 p. 7). Inference: check the mask for split or missing pieces there.
6. Check left against right. Mean side differences were at most 0.6 mm in pedicle width, 0.4 mm in height and
   0.1 deg in angle [CT] (moncadahabib2025 p. 5, Table 2), but individual sides differ by 1 to 2 mm in pedicle
   width [CT] (duman2026 p. 8, Table 3, note). Inference: a larger asymmetry means segmentation error, rotation or
   pathology before it means anything about the level.

### Step 4. Find the anchors

Find the anchors before you name anything between them. An anchor is a vertebra whose form, not its size, names
it, so it survives a size factor and a population shift.

| Anchor | What names it | Material, source |
|---|---|---|
| S1 | Lower surface far narrower and shallower than the upper (about 31 x 23 against 49 x 31 mm in men), with a disc of about 3.5 mm below | [CT] yadav2020 p. 178, Table 3; the S1 rule is the note's Inference |
| S1 | Pedicle seen as a triangle with clear superior and medial borders, no lateral cortex, the lateral side merging into the ala | [DB films] robertson2000 p. 712, Figure 8 |
| L5/S1 | The largest drop of the lower spine: body depth falls about 7 mm, canal depth about 2.4 mm, dural sac about 3 mm | [MRI] italianmri pp. 4-5, Tables 2-5 |
| L5/S1 disc | The largest anterior height and anterior-minus-posterior difference (about 7 against 4.4 mm at L4-L5); wedge about 15 deg supine | [CT] shin2024 p. 3, Table 2 (note's Inference); vanderhouwen2009 p. 39, Fig. 3 |
| T12 | One costovertebral facet on the body and no costotransverse facet; T11 has a small costotransverse facet, T10 a full one and lower facets | [DB12] panjabi1991t p. 893; p. 895, Table 6 |
| T12 | Thoracic-type superior facets (S about 67 to 77 deg) over lumbar-type inferior facets (S about 139 deg) on average | [DB12] panjabi1993f p. 1304; p. 1307; Tables 6-7 |
| T12/L1 | TPW at its minimum at T12, then the largest rise of the column: 41.0 -> 53.6 mm; 46.9 -> 71.2 mm; tip to tip about 54 -> 79 mm | [DB] tan2004 pp. 140-141, Table 1; [DB12] panjabi1991t p. 894 with panjabi1992 pp. 301-304; [cad] busscher2010 p. 1111, Fig. 7a |
| T12/L1 | Sagittal chord LI jumps 6 to 7 mm (about 43 at T12, 49.5 at L1 to L3) | [DB] hou1993 p. 1853, Table 3 |
| T12/L1 | Transverse pedicle angle: T11 about 1 deg, T12 about 4 deg lateral, L1 about 11 deg medial | [cad, CT] zindrick1987 p. 163, Table 3 |
| T12/L1 | Pedicle sagittal angle against the superior end plate drops from 10.7 to 6.1 deg (2.8 SD) | [DB] lien2007 p. 1218, Table 2 |
| C2 | The largest superior facets of the column (area about 208 mm2) with S above 90 deg; an uncovertebral surface below and none above; the deepest canal (21.0 mm) | [DB12] panjabi1993f pp. 1301-1303; panjabi1991c p. 864; p. 865, Table 6 |
| C7 | TPW about 67 mm, 17 more than C6; SPL about 46 mm; the smallest cervical canal (about 224 mm2) | [DB12] panjabi1991c pp. 863-864, Tables 2, 3, 5 |
| T1 | Canal about 22 mm wide; a round pedicle (height/width 1.1); TPW about 75 mm; a large upper rib facet | [DB12] panjabi1991t p. 897; Tables 3-8 |
| C7/T1 | IPD falls about 4.0 mm, about 2 SD, and T1/T2 another 3.5 mm | [AP] hinck1966 p. 142, Table IA (SD multiples are the note's Inference) |

Pearls for the anchors:

- Do not name T12 only as the lowest rib-bearing vertebra. In 517 Turkish adults on CT the twelfth rib was absent
  in 22 (4.3%), hypoplastic in 55 (10.6%), and a lumbar rib was present in 12 (2.3%) (duman2026 p. 10, Table 5).
- Do not look for T12/L1 in body heights, pedicle width, pedicle height or the transverse angle measured as
  duman2026 measured it: all four rise smoothly from T11 to L2 [CT] (duman2026 pp. 7-8, Tables 1-2).
- Do not take IFW/IFH above 1.5 as cervical: T1 (1.68) passes and C2 (1.64) only just. Separate C7 from T1 by
  IFWs (38.6 against 33.2 mm) and IFW/IFH (2.09 against 1.68) [DB12] (panjabi1993f p. 1307, Table 5).
- Look for a cervical rib or a long C7 transverse process before naming C7 by its TPW (panjabi1991c p. 864,
  note); a cervical rib was found in 7 of 517 (1.35%) [CT] (duman2026 p. 10).
- Do not hard-code the facet switch at T12: Malmivaara's superior T12 angle of 98 deg stands beside Panjabi's 70
  (panjabi1993f p. 1308, Table 10), and the spread of S at the T12-L1 joint is 16 to 33 deg against 3 to 10 in the
  mid-thoracic spine (panjabi1993f p. 1303, Tables 6-7, note).
- The set holds no measure of the dens. Inference: recognising C2 by its dens is anatomy from outside the set.

### Step 5. Count from both ends

1. With C2 and S1 both in the field, count the instances between them. Expect C2 to T12 to be 18 instances, C2
   included, and five lumbar-type instances between T12 and S1. Why: every norm in the set assumes 7 cervical, 12
   thoracic and 5 lumbar vertebrae; Panjabi's facet count of 276 = 12 x 23 means each spine gave exactly C2-C7,
   T1-T12 and L1-L5 (panjabi1993f p. 1299, note).
2. Count the ribs on each side separately and trace each rib to its vertebra; one patient had a hypoplastic right
   and an absent left twelfth rib (duman2026 p. 9, Figure 4A-B).
3. When the two counts disagree, report a candidate numerical variant and take it to Step 8; never average the two
   names. When the twelfth rib is rudimentary or absent, top-down and bottom-up counts often disagree on planning
   images and on fluoroscopy, and that leads to wrong-level surgery (duman2026 p. 12).
4. With only one end in the field, say which end, and carry its known failure. Inference (Part 1, the L6 section):
   counting up from the sacrum names every level one too low above an L6 or a lumbarised S1 and one too high above
   a sacralised L5; counting down by ribs fails in the 14.9% with a short or absent twelfth rib (duman2026 p. 10);
   a count down from C2 is untouched by any lumbosacral variant.

### Step 6. Read the ribs and the costal facets

1. Give the ribs an evidence arm of their own, read from the CT. The instance volume carries no rib: its alphabet
   runs C1-7 = 1-7, T1-12 = 8-19, L1-5 = 20-24, L6 = 25, sacrum = 26, T13 = 28, and the spineps subregion scheme
   has no rib label (bordercall scanimport/schemes.py, code).
2. Read the costal facets of each thoracic-form instance: T1 a large upper rib facet; T10 lower facets and a full
   costotransverse facet; T11 a small costotransverse facet; T12 none; T11 and T12 one costovertebral facet each
   [DB12] (panjabi1991t p. 893; p. 895, Table 6; p. 897).
3. Set the rib priors from duman2026's counts (517 Turkish adults, CT, all cells from p. 10, Table 5):

   | Finding | Count / denominator | Rate | By sex |
   |---|---|---|---|
   | Twelfth rib absent | 22/517 | 4.3% | women 18/240 (7.5%), men 4/277 (1.4%) |
   | Twelfth rib hypoplastic | 55/517 | 10.6% | not given in the note by sex |
   | Short or absent, together (categories exclusive) | 77/517 | 14.9% | Inference: sum |
   | Lumbar rib, bearing vertebra not named | 12/517 | 2.3% | men 10/277 (3.6%), women 2/240 (0.8%) |
   | Cervical rib | 7/517 | 1.35% | women 6/240, men 1/277; may be low if scans missed C7 (note) |
   | T13 | not counted | no value | Inference: at most the lumbar-rib count, since duman2026 would file any rib below the twelfth as a lumbar rib |

4. Call a separate costal element jointed to a lumbar-type transverse process a lumbar rib on L1 only if twelve
   thoracic vertebrae lie above it by count from C2 or T1; otherwise consider T13 (duman2026 p. 10, Figure 5B; the
   rule is the note's Inference, since the paper gives none).
5. Do not apply duman2026's 4 cm hypoplasia cut-off to a rib you have not traced in 3D (duman2026 p. 5, note).
6. Confirm that C7 lies in the field before you call a cervical rib absent (duman2026 p. 10, note).
7. Keep the rib out of the vertebra's own measures. Measure TPW tip to tip of the transverse process, excluding
   the rib (busscher2010 p. 1111, Fig. 7a; tan2004 p. 138, note); bach2019 cut T12 free of its rib before placing points
   (bach2019 p. e107); check T1 to T5 end-plate widths for rib-head contamination (busscher2010 pp. 1109-1112, Figs. 3, 7a, 8a, note).

### Step 7. Read the facet orientation

1. Fit a least-squares plane to each joint face, orient its normal up and back, and compute T = arccos(n_y) and the
   acute sagittal angle; compare with Panjabi's tables as min(|S|, 180 - |S|) (panjabi1993f p. 1300; Tables 6-8;
   the conversion is the note's Inference).
2. Use T as a regional cue: superior T is 33 to 59 deg at C2-C7, 58 to 78 deg at T1-T12 and 81 to 86 deg at L1-L5
   [DB12] (panjabi1993f p. 1307, Table 6). It separates cervical from thoracic well and thoracic from lumbar by only
   a few degrees.
3. Use S for thoracic against lumbar. Call a vertebra lumbar when its facets stand 120 to 150 deg from the sagittal
   plane on Panjabi's scale and the facets are large (panjabi1993f pp. 1307-1308). Expect lumbar-sized facets to
   begin one joint below the orientation switch, at L1-L2 (panjabi1993f pp. 1301-1302, Tables 2-4).
4. Do not mix scales. On axial CT the lumbar facet-to-sagittal angle in the CT studies of Panjabi's Table 10 sits
   11 to 21 deg more sagittal than his (panjabi1993f p. 1308, Table 10). In masharawi2021 the joints were most
   sagittal at L2 (29 to 34 deg) and most coronal at L5 (43 to 47 deg), with SDs of 7 to 13 deg against a 12 to
   17 deg rise [CT] (masharawi2021 p. 6, Table 2).
5. In the neck, read the facing: superior facets face lateral at C2 and C5-C7 and medial at C3-C4, but where the
   facet stands 83 to 86 deg from the sagittal plane a 4 to 7 deg fit error flips it (panjabi1993f p. 1307, Tables
   6, 8; facing is the note's Inference).
6. Expect variants: 6 of 443 skeletons had flat coronal and 8 flat sagittal superior articular surfaces, level not
   given (eisenstein1977 pp. 176-177); the lumbosacral facets were notably smaller on the side of a sacro-transverse
   joint (eisenstein1977 p. 177); in women over 50, more sagittal L4 facets went with an L4-L5 degenerative slip
   (masharawi2021 p. 5, Table 2).

### Step 8. Resolve a transitional segment

The set's only counts of lumbosacral variants are two: eisenstein1977's 443 dry skeletons from South Africa and
ahn2001's 32 Marfan adults on films. Set the decoder's transitions from them, and state the population.

| State or transition | Count / denominator | Rate | Material, source |
|---|---|---|---|
| Lumbarised S1 | 9/443 | 2% | [DB] eisenstein1977 p. 177; p. 180 |
| True L6 | 2/443 | 0.45% | [DB] eisenstein1977 p. 177; both Sotho |
| Sacralised L5 | 8/443 | 1.8% | [DB] eisenstein1977 p. 177; none among 35 Caucasoid women |
| Transitional vertebra | 1/443 | 0.23% | [DB] eisenstein1977 p. 177 |
| Persistent S1-S2 facet joints | 16/443 | 3.6% | [DB] eisenstein1977 p. 177 |
| Sacro-transverse joint, patent or ankylosed | 10/443 | 2.3% | [DB] eisenstein1977 p. 177 |
| Six lumbar-type segments (L6 or lumbarised S1) | 11/443 | 2.5% | Inference: (2 + 9)/443 |
| Any count-changing state | 19/443 | 4.3% | Inference: (2 + 9 + 8)/443 |
| Lumbosacral transitional vertebra, type unstated, in Marfan syndrome | 5/32 | 15.6% | [AP, LAT] ahn2001 p. 68 |

Then work down this list:

1. Decide how many free lumbar-type segments lie between the last thoracic-form vertebra (Steps 4, 6, 7) and the
   sacrum: four, five or six. Name the thoracic form by facets and costal facets, not by the rib alone (Step 4).
2. Six lumbar-type segments: tell an L6 over a sacrum of five segments from a lumbarised S1 over a sacrum of four
   by counting the fused sacral segments (Inference; Part 1, the L6 section). Before you accept either, rule out a
   split S1: an S1 with free S1-S2 facets may be cut off by a segmenter and miscounted as L6 (eisenstein1977
   p. 177, note). Expect the caudal signature one level down, so that the true L5 reads like an L4-L5 intermediate
   (Inference).
3. Four free lumbar-type segments: suspect a sacralised L5, and look for the smaller lumbosacral facets on the
   fused side (eisenstein1977 p. 177).
4. Five segments with an odd last one: suspect a transitional vertebra or a sacro-transverse joint, which leave the
   count unchanged (eisenstein1977 p. 177).
5. A rib on the first lumbar-type segment: apply Step 6, rule 4.
6. At L5/S1, name a level only on two or more independent cues: pedicle form (an oblique ellipse whose lateral
   border lies on the body's edge at L5, a triangle with no lateral cortex at S1; robertson2000 pp. 711-713),
   anterior body wedge (tan2004 pp. 140-141, Table 1), the IPD step (hinck1966 p. 142), facet orientation (panjabi1993f p. 1303)
   and the disc below (shin2024 p. 3). Why: each cue fails alone in a known condition (Step 10). Inference: treat a
   pedicle between the two forms as a transitional candidate, since no transitional spine was studied (robertson2000
   pp. 711-713, note).
7. Decide which disc is the last mobile one before you apply any L5/S1 norm (bach2019 note; the paper is silent on it),
   and do not call a thin lowest disc transitional without a body-shape or rib sign: grade 2 to 3 degeneration was
   found at L5-S1 in 22 of 34 spines over 60 [cad] (twomey1985 p. 498, Table 4).
8. Raise the transitional prior in a widened-canal state, and count from a cranial anchor rather than from the
   sacrum (ahn2001 p. 68; p. 70; the counting rule is the note's Inference).
9. Never apply an L5 norm to a transitional segment: no paper measured one, and the pooled L5 of the meta-analysis
   may hold some (bonczar2024 p. 10).
10. Report every competing name with its probability, never only the winner. Inference: the priors above are
    point values from one dry-bone series; run their Wilson ranges as a sensitivity study and report how often the
    top path changes.

### Step 9. Extract the measures for the Bayes rule

#### 9a. Which measures carry each junction

The table ranks schwingcheck's measures by Panjabi's step/SD at each junction (Part 1 tables, [DB12], Inference
from data/panjabi_long.csv). The last column says whether a mask measurer exists today (schwingcheck measures.py,
SPINEPS_7, code).

| Junction | Strongest measures, step/SD | Measurer today |
|---|---|---|
| C2/C3 | facet_sag_sup -3.52, facet_area_sup -3.50, interfacet_h -3.35, pedicle_h -2.33, canal_ap -1.65 (panjabi1993f pp. 1301-1303; panjabi1991c p. 864) | canal_ap only; C2 is outside the pool |
| C3 to C5 | none above 1.6; endplate_lower +1.56 at C4/C5 (panjabi1991c p. 863) | endplate_lower |
| C5/C6 | uncovertebral frontal angle +3.20, PDIt +2.14 (panjabi1991c pp. 864-865) | none |
| C6/C7 | transverse_width +3.05, spinous_length +2.44, endplate +1.57, h_post +1.52 (panjabi1991c pp. 863-864) | endplate, h_post |
| C7/T1 | interfacet_w_inf -2.23 (panjabi1993f p. 1302); endplate_lower_depth +1.99 and transverse_width +1.75, both across two papers (panjabi1991c pp. 863-864; panjabi1991t pp. 892-894) | endplate_lower_depth |
| T1/T2 | facet_sag_sup -2.10, interfacet_w_sup -1.92 (panjabi1993f pp. 1302-1303) | none |
| T2/T3 | transverse_width -2.03, endplate_depth +1.54 (panjabi1991t pp. 892-894) | endplate_depth |
| T3 to T9 | none above about 1.2 per level (panjabi1991t p. 892; panjabi1993f p. 1302) | carry by count |
| T10/T11 | pedicle_h +1.91, costotransverse area -1.72, transverse_width -1.30, endplate_lower +1.26 (panjabi1991t pp. 892-895) | endplate_lower |
| T11/T12 | facet_sag_inf +2.77, endplate +1.53, canal_ap +1.12 (panjabi1993f p. 1303; panjabi1991t pp. 892-893) | endplate, canal_ap |
| T12/L1 | transverse_width +4.01 and spinous_length +3.99 across two papers, facet_sag_sup +2.78, pars_area -2.07 across two papers (panjabi1991t pp. 894-895; panjabi1992 pp. 301-304; panjabi1993f p. 1303) | none of the four |
| L1/L2 | facet_area_sup +1.25; nothing else above 1.1 (panjabi1993f p. 1302) | none |
| L2/L3 | transverse_width +1.41 (panjabi1992 pp. 301-304) | none |
| L3/L4 | pedicle_w +2.45 (panjabi1992 pp. 301-304) | none |
| L4/L5 | pedicle_w +1.95, pedicle_h +1.72, PDIs +1.15, transverse_width +1.01; h_post only -0.34 (panjabi1992 pp. 301-304) | none of the four |

Inference, from the table: the seven measurers carry only the cervicothoracic and lower thoracic steps; at T12/L1
and from L3 to L5 none of the strongest measures has one. Add measurers in this order, by the number of junctions
each serves: transverse_width (C6/C7, C7/T1, T2/T3, T12/L1, L2/L3), pedicle_w and pedicle_h (C2/C3, T10/T11,
L3/L4, L4/L5), then facet S (C2/C3, T1/T2, T11/T12, T12/L1).

Measures outside the pool that the set shows to step at a junction (each a likelihood, not a rule):

| Measure | What it does | Material, source |
|---|---|---|
| Lower interfacet width IIFW | jumps 10 to 11 mm from L4 to L5, 1.4 to 1.6 pooled SD; unchanged by a degenerative slip | [CT] masharawi2021 p. 6, Table 2 (SD multiple is the note's Inference) |
| Pedicle width/height | crosses 1 between L4 and L5 | [cad] olsewski1990 p. 544, Table I; [DB] yu2015 p. 1645, Table 5; [DB] lien2007 p. 1218, Table 1 |
| Pedicle transverse angle | rises more than 10 deg from L4 to L5 (about 18.5 to 30 deg) | [DB] hou1993 Figure 7, p. 1854; [cad] mitra2002 p. 455; [CT] arockiaraj2025 p. 316, Table 2 |
| Sagittal chord LI | jumps 6 to 7 mm at T12/L1 | [DB] hou1993 p. 1853, Table 3 |
| VBHa/VBHp | about 1.10 to 1.18 at L5 only; 0.85 to 0.97 above | [DB] tan2004 pp. 140-141, Table 1; [cad] busscher2010 p. 1107, Table 3; [CT] frontphys2026 p. 5; [CT] moncadahabib2025 p. 4 |
| Canal shape CSA/(width x depth) | about 0.85 at L1 falling to 0.59 at L5 | [CT] griffith2016 p. 675, Tables 2-4, note |
| Canal transverse width (IPD) | the largest lumbar step is L4 to L5, about 4.6 mm | [CT] cizmic2023 p. 202, Table 4 |
| Anterior disc height | rises at every step to L5-S1 | [CT] shin2024 pp. 3-4, Tables 2-3 |

#### 9b. How to measure on the mask

The SPINEPS subregions are 41 arcus, 42 spinosus, 43 and 44 the left and right costal (transverse) processes, 49
corpus, 52 and 53 the superior and inferior end plates, 60 cord and 61 canal (bordercall scanimport/schemes.py,
code). There is no pedicle label, and label 61 is the canal's contents, not the bony foramen (panjabi1992 note).

| Measure | Recipe on the mask | Source |
|---|---|---|
| endplate, endplate_depth (and lower) | width along x and depth along z of the end-plate rim (labels 52, 53); in the neck take the upper width between the uncus bases and leave the uncovertebral facets out | panjabi1991c p. 862, Figure 1; p. 868; panjabi1991t p. 898 |
| h_post | midline posterior-wall height along y | panjabi1991c p. 868, Table 7 |
| canal_w, canal_ap | the closed bony ring of the instance on the mid-pedicle slice: width between the medial pedicle cortices, depth in the midline from the posterior body wall to the inner arch at the spinous base; never label 61 | griffith2016 p. 672, Figure 1A; p. 673; cizmic2023 p. 201, Figure 1, note; panjabi1992 p. 301 |
| pedicle_w, pedicle_h | the bony bridge of the arch (41) between the body and the processes, lateral to the canal; the narrowest chord perpendicular to the pedicle axis, outer cortex to outer cortex; report the convention | olsewski1990 p. 542, note; hou1993 p. 1851; otsuki2021 p. 3 |
| transverse_width | extent along x between the most lateral voxels of labels 43 and 44, rib excluded | tan2004 p. 138, note; busscher2010 p. 1111, Fig. 7a |
| spinous_length | from the upper end-plate centroid to the most inferoposterior spinous tip; busscher2010 measured from the base, so add the base-to-mid-body offset before comparing | panjabi1992 p. 302; panjabi1991t p. 893; busscher2010 p. 1112 |
| facet S and T | a plane fitted to each joint face (Step 7) | panjabi1993f p. 1300 |
| PDIs, PDIt | against the vertebra's own midline and its own superior end plate | lien2007 p. 1216; olsewski1990 p. 543 |

Definitions differ between series, and the difference is a mean offset, not noise:

- Canal depth was taken as the minimum chord near the canal's cranial end in dry bone (amonookuofi1985 p. 72;
  eisenstein1977 p. 173) and on the mid-pedicle slice on CT (griffith2016 p. 672). Record which.
- Pedicle width runs larger in Panjabi's digitised sections than at Hou's isthmus (T12 8.7 against 8.3, L1 8.6
  against 7.0, L5 about 18.6 against 12.9 mm) (hou1993 note). Inference: a mask extractor that takes the isthmus
  minimum will read nearer Hou than Panjabi.
- Pedicle height at L5 falls to its lowest in series that take the narrowest point (yu2015 p. 1645, Table 5;
  masharawi2021 p. 11, Table 5) and rises in Panjabi's (panjabi1992 pp. 301-304). Fix the definition before you
  use PDH to name L5.

#### 9c. The error to give each measure

Inference throughout, built from the error figures of the notes; an error set too small breaks calibration, so
take the upper end of every bracket.

| Family | sigma | Built from |
|---|---|---|
| End-plate widths and depths, at voxels <= 1 mm | 1.0 mm (0.8 to 1.3) | CT against caliper SD 0.66 mm (vanderhouwen2009 p. 38, Fig. 4 p. 39) plus quantisation 0.41 mm |
| h_post | sqrt(0.65^2 + (0.41 dz)^2), at least 1 mm | duman2026 p. 6, note; Step 1 |
| Canal width and depth | 1.0 mm; it is 4 to 7% of a canal depth against 2 to 3% of an end plate | as end plates; busscher2010's canal depth was its least reliable measure (busscher2010 p. 1106, Table 1) |
| Pedicle width | 1.0 mm, 14 to 20% of a 5 to 7 mm thoracic pedicle | partial volume 10 to 20% at 1 mm voxels (hou1993 note); duman2026's SEM (duman2026 p. 6, note) |
| Pedicle height | 1.0 to 1.4 mm by slice spacing | as pedicle width, with dz |
| transverse_width, spinous_length | sqrt(1 + (c L)^2) mm, c between 0.013 and 0.05; not measured | tan2004's calibration, 1.3% of a 20 mm length (tan2004 p. 138), against Panjabi's 5% method error (panjabi1992 p. 300) |
| Angles | 3 deg; lumbar facet S is weak | panjabi1993f p. 1303, Tables 6-7, note; duman2026 p. 6, note |

### Step 10. Check the red flags

Each condition below moves a measure the Bayes rule leans on. Detect it first, then down-weight or drop the measure
it distorts.

| Flag | What it distorts | How to see it | What to do | Source |
|---|---|---|---|---|
| Marfan syndrome (widened canal) | IPD widened by 4.5 mm at L1 to 9.9 mm at L5, growing caudally; Marfan L1 (29.5) reads like a normal L5 (29.7); steps L3-L4 +2.7 and L4-L5 +4.8 against +0.9 and +2.8 | IPD over the cut-offs L1 29.4, L2 30.1, L3 31.4, L4 32.9, L5 37.1 mm on film; widened dural sac or anterior sacral meningocele | Stop using absolute IPD; use the within-patient rise and form anchors; raise the transitional prior to 5/32 | [AP] ahn2001 p. 68; p. 70; dural ectasia by DSR and S1/L4 sac ratio [MRI] italianmri pp. 5-6 |
| Narrow-IPD states: achondroplasia, osteopetrosis, trisomy 21 | IPD fails to widen caudally or falls; pedicles massive and dense in osteopetrosis | L5 IPD below L4's; values below T10 at the floor | Drop the IPD gradient for that spine; expect the opposite level bias | [AP] hinck1966 pp. 152-153; amonookuofi1982 p. 232; ahn2001 p. 69 |
| Trefoil canal | canal outline and area at L5, sometimes L4; about a third of L3 canals are trefoil in Nigerian CT | laminar bars on axial CT; shape factor near 0.6 | Treat it as anatomy, not segmentation error; a weak L5 cue, never an L5 label by itself | [DB] eisenstein1977 p. 177 (66/443); [CT] alonge2021 p. 74; griffith2016 p. 675, note |
| Spondylolysis and isthmic slip | arch detached; the L4 case had an enlarged inferior facet on the defect side | pars gap on CT | Join the arch to its body before counting (Step 3) | [DB] eisenstein1977 p. 177; ahn2001 p. 68 |
| Degenerative slip at L4-L5 | foramen height lower by 1.85 to 3.94 mm, most (about 3.9) at L4-L5; L4 superior interfacet width rises to near a control L5 | listhesis on the sagittal reformat | Do not use the superior interfacet width to find L5; use the lower one, which the slip did not change | [CT] masharawi2021 p. 6, Table 2; p. 9, Table 4 |
| Disc degeneration | disc heights and the "last disc" cue | collapsed or grade 2 to 3 discs, common at L4-L5 and L5-S1 after 60 | Do not read a thin disc as a transitional or block level; check the end plates | [cad] twomey1985 p. 498, Table 4; [MRI] tang2016 p. 4117 |
| Osteophytes and facet arthrosis | end-plate rims, body chords, facet planes; worse from L1 to L5 and with age; severe facet arthrosis in 38.5 to 58.3% of controls at L4-L5 aged 50 to 80 | rim spurs, enlarged articular processes | Frame on the posterior wall; take chords at mid-height; trim osteophytes; widen landmark tolerance at the lowest two joints | [DB] eisenstein1977 p. 173; p. 175; [DB] tan2004 p. 139; [CT] chen2011 p. 1815; [CT] masharawi2021 p. 8, Table 3 |
| Large osteophytes on films | anterior disc and body heights | anterior osteophytes over 2 mm, grade iv discs | Exclude such levels from film norms | [cad] kunkel2011 pp. 379, 384-385 |
| Anterior wedge fracture | VBHa/VBHp, the L5 wedge cue | wedged body; in the thoracic spine an anterior height at or above the posterior is itself abnormal | Down-weight height cues at that level; do not call a fracture for an L1 or L2 front 1.5 to 2 mm below the back, which is the normal wedge | [DB] eisenstein1977 p. 177 (17/443); [CT] frontphys2026 p. 5, Table 2; [cad] kunkel2011 p. 379, Table 2, note |
| Thoracolumbar injury | T11 to L2 measures | 50 to 60% of spinal injuries fall at the thoracolumbar junction | Treat T12-L1 values with caution; skip fractured vertebrae | [CT] duman2026 p. 2; vanderhouwen2009 p. 34; p. 38 |
| Osteoporosis | end-plate planes and concavity; the anterosuperior body is the weakest region | under 100 HU on non-contrast CT | Refer angles to the posterior cortex; skip osteoporotic end plates | abbas2021 p. 6; frontphys2026 p. 7; vanderhouwen2009 p. 34 |
| Rotation or scoliosis | IPD and every angle measured against the median plane | a lumbar curve over about 20 deg; a one-sided excess of pedicle angle | Mark IPD unreliable in the curve; measure in the instance's own frame | [AP] ahn2001 p. 67; arockiaraj2025 p. 315, Table 1, note; hou1993 p. 1851 |
| Hemivertebra, irregular bodies | IPD and the count | focal IPD collapse, irregular body sizes | Count with care; expect a widened sagittal diameter at that level | [AP] hinck1966 pp. 152-153, Fig. 8 |
| Sex and size | absolute widths: a woman's L4 pedicle is as wide as a man's L3 to L4 and her L3 as a man's L1 to L2 | sex known or not | Condition on sex and size, or a female vertebra tends to be named a level too cranial | [cad, AP] olsewski1990 p. 544, Table I; p. 545, Table III (naming bias is the note's Inference) |

### Step 11. Decide when to answer with uncertainty

Inference throughout, from the steps above.

1. Answer with a distribution over names, not a single name, whenever:
   - the counts from the two ends disagree (Step 5);
   - only one anchor lies in the field and the other end's failure applies (Step 5, rule 4);
   - the lumbosacral segment has fewer than two agreeing cues (Step 8, rule 6);
   - the twelfth rib is short or absent on either side and the facet switch is not clear (Steps 4, 6, 7);
   - a red flag of Step 10 removes the measures that carry the nearest junction.
2. Do not answer a name for C3, C4 or C5 or for T4 to T9 from their own measures; carry them by count from a named
   neighbour, and pass the neighbour's uncertainty on to them (panjabi1991c Tables 2-6, pp. 863-865; panjabi1991t
   p. 892, Table 3).
3. Abstain, and say why, when the instance chain is broken (Step 3) and cannot be repaired, or when no anchor lies
   in the field: then every name is a guess about the field of view, not about the spine.
4. Report the population behind each prior: the lumbosacral rates are South African dry bone (eisenstein1977
   p. 177), the rib rates Turkish CT (duman2026 p. 10), and the size norms mostly Panjabi's twelve.

## 2B. Naming on an AP and a lateral radiograph or fluoroscopy frame

A projection loses what CT gives: the ribs and the thoracic spine overlap on the lateral, C1 and C2 vanish on the
AP, both pedicles and the rib heads superimpose, and every length carries an unknown magnification. Name on a film
from form first, then from ratios, and only last from millimetres.

### Step 1. Set the scale before you compare a length

1. Treat every film length as magnified, and divide it by the set-up's factor before you compare it with dry-bone
   or CT values: 1.23 on the lateral and 1.14 on the AP at 110 cm tube to film (eisenstein1977 p. 175). Recompute
   it for any other geometry (eisenstein1977 p. 175, note).
2. Know which norms are uncorrected film values: hinck1966 at 40 inches, 101.6 cm (hinck1966 p. 141);
   amonookuofi1982 at 100 cm (amonookuofi1982 p. 226); ahn2001 at 101 cm, printed as "mm" (ahn2001 p. 68, note);
   chaudhary2015 at an unstated distance (chaudhary2015 p. 34). Inference (the hinck1966 note's): at 101.6 cm and a
   pedicle 7 to 15 cm from the film, M is about 1.07 to 1.17.
3. Prefer ratios between structures at one depth on one film, since they cancel magnification: within-patient
   ratios rather than absolute millimetres (chaudhary2015 p. 34); the canal-to-body ratio, which needs no
   magnification factor (amonookuofi1982 p. 231). Inference: on one lateral film M changes by about 1/(SID - OFD)
   per cm of depth, 1.1% per cm at SID 110 cm and OFD 20 cm, so anterior and posterior structures are not quite on
   one scale.
4. Inference: when the factor is unknown, let it act as size. Shift the prior mean of log size by log M, about
   +0.14 when only "100 to 110 cm" is known (log 1.07 = 0.068 to log 1.23 = 0.207), and widen its SD to
   sqrt(0.07^2 + 0.040^2) = 0.081, where 0.040 = 0.139 / sqrt(12) is the SD of a uniform spread over that log range
   and 0.07 the SD of schwingcheck's size prior, log s ~ N(..., 0.07^2) (eisenstein1977 p. 175; hinck1966 note;
   schwingcheck README, "The PyMC models", code).
5. Give each film reading a random error of about 1.0 mm before magnification: hinck1966's reading error is about
   0.3 mm with occasional misreads of 1 to 3.6 mm (hinck1966 p. 142, note), and gilad1985 treats differences under
   about 1.5 mm as possible method error, 0.5 mm of calipers plus 1.0 mm of parallax (gilad1985 p. 119). Inference:
   give superimposed or low-contrast structures (pedicle height on the lateral, the posterior disc, the canal depth
   on the lateral) at least 1.5 mm.
6. Put the known film offsets into the mean, not the error. On a disarticulated spine the AP film read the L5
   pedicle 3.5 mm narrow and 2.4 mm short against the caliper, and L1 to L3 heights 1.5 to 1.8 mm tall [cad film]
   (olsewski1990 p. 544, Table II; p. 548); the dense pedicle ring is the inner cortex, 1 to 3 mm inside the true
   border on each side [DB film] (robertson2000 p. 711); the posterior disc height on thoracic films reads about 37%
   short [cad] (kunkel2011 p. 380; Table 1, p. 378). The two pedicle-width sources disagree: within 0.6 mm at L1-L4
   by caliper against film (olsewski1990 Table II, p. 544) against up to 2 to 6 mm short by a wire on the cortex
   (robertson2000 p. 711, note). Take the offset from the set-up that matches the clinic's.

### Step 2. Check what the view can show

| View | Shows | Cannot show | Source |
|---|---|---|---|
| AP | IPD from C3 down; pedicle ovals; end-plate and body widths; transverse processes; ribs; the AP outline of the facet tips | C1 and C2; sacral IPD against norms; any depth or height | hinck1966 p. 142; panjabi1991t p. 890; p. 898; panjabi1993f p. 1308 |
| Lateral, neck | C2 to C7 body corners and spinous tips | C1, always; C2 unclear in 11 of 141; C7 hidden by clavicle, humerus and ribs in 15 of 141 (healthy men 20 to 38) | gilad1985 p. 117 |
| Lateral, thorax | body heights and discs, C7 to T12, from contact films of specimens | thoracic levels on clinical films, lost under the ribs; upper thoracic posterior corners, hidden | gilad1985 p. 117; kunkel2011 p. 383 |
| Lateral, lumbar | L1 to L5 bodies, discs, canal depth by construction, foramina, pedicle sagittal angle | pedicle width, transverse angle, IPD | gilad1985 p. 117; hinck1966 p. 149; zindrick1987 p. 160, note |

Never take an IPD from a lateral view, and never a pedicle width, transverse angle or pedicle-axis depth (hinck1966
p. 149; zindrick1987 p. 160, note; mitra2002 p. 453, note).

### Step 3. On the AP, find the anchors and read the profile

1. Find the cervicothoracic step in the IPD: in 121 adults it fell 4.0 mm from C7 to T1 and 3.5 mm from T1 to
   T2, about 2 SD each [AP, uncorrected film] (hinck1966 p. 142, Table IA; SD multiples are the note's Inference).
2. Find the thoracolumbar rise: T10 18.7, T11 20.2, T12 23.2, L1 25.0 mm (hinck1966 p. 142, Table IA). In
   children use the T11/T12 step (+2.0 to +3.0 mm at every age), since the T12/L1 step is only 0.6 mm at 3 to 5, 6
   to 8 and 13 to 14 years (hinck1966 p. 142, Table IA, note).
3. Find the L4/L5 jump: +2.8 mm in Hinck's adults (hinck1966 p. 142); +2.7 in men and +3.0 in women of 290
   Nigerian adults (amonookuofi1982 p. 228, Table 1); +4.2 and +3.3 in 300 North Indian adults (chaudhary2015 p. 34,
   Table I). Read it as the L5 cue, but confirm with the sacrum and iliac crests, since a transitional segment can
   move it one level (ahn2001 p. 68, note).
4. Read a profile, not a value: normal spines share one IPD shape and differ mainly in overall level (hinck1966
   p. 146). Inference: neighbours within T4 to T10 and within L1 to L3 cannot be told apart by IPD, differing by
   under one SD (hinck1966 pp. 142, 145, Tables IA, II).
5. The adult IPD norms, sexes combined, mm, uncorrected film at 101.6 cm (hinck1966 p. 142, Table IA; SD p. 145,
   Table II; 90% range p. 146, Table III):

   | Level | Mean | SD | Range | Level | Mean | SD | Range |
   |---|---|---|---|---|---|---|---|
   | C3 | 28.0 | 1.5 | 25-31 | T8 | 17.7 | 1.5 | 15-21 |
   | C5 | 29.4 | 1.7 | 26-33 | T10 | 18.7 | 1.6 | 16-22 |
   | C7 | 28.0 | 2.0 | 24-32 | T11 | 20.2 | 1.8 | 17-24 |
   | T1 | 24.0 | 1.8 | 20-28 | T12 | 23.2 | 2.0 | 19-27 |
   | T2 | 20.5 | 1.7 | 17-24 | L1 | 25.0 | 2.2 | 21-29 |
   | T3 | 18.8 | 1.5 | 16-22 | L3 | 26.0 | 2.7 | 21-31 |
   | T6 | 17.3 | 1.5 | 14-20 | L5 | 29.7 | 3.7 | 23-37 |

   Males ran about 1 mm larger (hinck1966 p. 143). A PA chest film reads T1 to T3 about 1.1 mm and T4 to T12 about
   0.4 mm below the AP spine value, in 10 patients aged 10 to 15 (hinck1966 pp. 148-149, Table IV).
6. Read the transverse processes against the end plate, a ratio free of magnification. TPW over EPWu falls to its
   minimum, about 1.19, at T12, and is about 1.48 at L1 and 1.6 to 1.8 from L2 to L5; it is 3.0 to 3.2 at C3 to
   C6, 2.83 at C7 and 2.58 at T1 [DB] (tan2004 pp. 140-141, Table 1; ratios are the note's Inference).
   busscher2010's tip-to-tip ratio has its minimum, 1.15, at T12 and its maximum, 2.8, at T1-T2 [cad]
   (busscher2010 pp. 1109-1112, Figs. 4, 5b, 7b, 8c). Check that a long process at the top of the lumbar run is
   not a rib (bonczar2024 pp. 5-9, note).
7. Read the ribs, but never settle a level from the AP rib count alone (duman2026 pp. 12-13). A short or missing
   lowest rib warns that counts may disagree; and a projected rib under 4 cm does not prove hypoplasia, since the
   rib runs obliquely backward and is foreshortened (duman2026 p. 5; p. 9; note).
8. Read the pedicle ovals:
   - Width over height is free of magnification. Expect about 0.4 to 0.6 at L1-L2, 0.55 to 0.75 at L3, 0.7 to 0.9
     at L4 and 1.0 to 1.25 at L5, and only about 1.0 at L5 in women on films (olsewski1990 p. 544, Table I; p. 545,
     Table III; p. 547; ranges are the note's Inference). L5 is the only lumbar pedicle wider than tall in most
     series (olsewski1990 p. 547; lien2007 p. 1218, Table 1; yu2015 p. 1645, Table 5).
   - A small-looking L5 pedicle on the AP is still compatible with L5, since the film read it 3.5 mm narrow
     (olsewski1990 p. 548; p. 544, Table II).
   - The AP oval of a converging pedicle is not its isthmus width: at L5 the pedicle runs about 24 deg medially and
     is seen obliquely (lien2007 p. 1218, note; zindrick1987 p. 160, note).
   - A pedicle oval lateral to the superior facet is an L5 cue: the entry point lay lateral to the facet at L5 in
     every cadaver (mitra2002 pp. 456-457; the AP reading is the note's Inference), and the pedicle centre lay at or
     beyond a third of a facet width lateral to it in 36, 38 and 40 of 40 columns at L3, L4 and L5 (hou1993 p. 1852;
     Figure 6, p. 1854). Use it only with the beam square to the vertebra (hou1993 p. 1851, note).
9. Read the S1 pedicle as a triangle with clear superior and medial borders, no lateral cortex and its lateral side
   running into the ala, on a view rotated 10 to 15 deg from PA [DB films] (robertson2000 p. 712, Figure 8).
10. Read the facet tips in outline: the superior interfacet width exceeds the inferior only at L1 (ratio 1.06), and
    IFW/IFH is 0.90 at L3, 1.16 at L4 and 1.44 at L5 [DB12] (panjabi1993f p. 1308, Tables 5-6).
11. Check rotation before you compare sides or levels. One wide pedicle with the spinous process turned away from
    it and a narrowed opposite pedicle means the beam has turned toward that pedicle's axis (robertson2000 p. 710,
    Figure 4; the reading is the note's Inference). Mark IPDs unreliable in a lumbar curve over about 20 deg
    (ahn2001 p. 67). Rotation foreshortens the projected IPD (hinck1966 note).

### Step 4. On the lateral, find the anchors and read the ratios

1. In the neck, anchor the count on C2: its body is taller than deep (VBH 17.8 against VBW 13.95 mm) and its
   posterior element long (overall length L 51.3 against 45.2 mm at C3) [LAT] (gilad1985 p. 117; pp. 118-120,
   Tables 1-2). Do not separate C3, C4 and C5 by body measures, whose means differ by under 1 mm against SDs of 1.2
   to 1.9 mm; count from C2 (gilad1985 p. 118, Table 1, note).
2. Find the lower neck by the posterior element: L, e and f step up sharply from C5 to C6 to C7 (L 48.9, 56.2,
   62.3; e 35.4, 41.5, 49.6 mm) [LAT] (gilad1985 p. 118, Tables 1-2). Expect C7 hidden in about 1 film in 10
   (gilad1985 p. 117). Inference (the note's): if the last visible cervical vertebra's L is nearer 56.2 than 62.3,
   suspect C6, weighing e and f too, since L has no SD.
3. Read the cervical facets: on the lateral, facet inclination T is about 41 to 55 deg at C3 to C6, 49 to 66 at
   C7-T1 and 72 to 78 at T4 to T12; at C2 expect about 27 deg (superior) and 29 deg (inferior) on the image though
   the true T is 31 to 41 (panjabi1993f p. 1309, Tables 6-7; the projection reading is the note's Inference). Read
   the lumbar facets on the lateral not at all.
4. In the thoracic spine, do not name one vertebra from body height: about 0.6 mm per level against SDs of 1 to
   2.4 mm (kunkel2011 p. 379, Table 2). Fit the trend over four or more bodies anchored to a junction (kunkel2011
   p. 379, note). Expect the posterior body taller than the anterior at every level from C7 to T12 (ratio about 1.03 at C7
   and 1.07 to 1.18 from T2 to T12) [cad] (kunkel2011 p. 379, Table 2; ratios derived by the note). Use the disc
   over cranial body ratio I1 to place a run: 0.30 to 0.32 at C7-T1 and T1-2, 0.19 to 0.20 at T3-4 and T4-5, and
   0.25 to 0.33 from T8-9 to T11-12 anatomically, about 0.14 to 0.25 on films (kunkel2011 p. 379, Table 3, note).
5. In a run known to be lumbar, read the wedge. b/d below 1 marks L1 (0.94) and above 1 marks L5 (1.10), with L2
   to L4 near 1.00, in 157 healthy men aged 20 to 38 [LAT] (gilad1985 p. 119; Table 1, p. 118). Every cervical
   level also has b < d and no T12 was measured, so an anterior wedge alone does not prove L1 (gilad1985 p. 118,
   note). The same ratio, VBHa/VBHp, in other series:

   | Series | L1 | L2 | L3 | L4 | L5 | Material, source |
   |---|---|---|---|---|---|---|
   | tan2004 | 0.90 | 0.90 | 0.97 | 1.00 | 1.10 | [DB] pp. 140-141, Table 1 (note's ratios) |
   | frontphys2026 | 0.92 | 0.94 | 0.99 | 1.05 | 1.13 | [CT] p. 5, Table 2 (note's ratios) |
   | moncadahabib2025 | 0.90 | 0.94 | 0.98 | 1.02 | 1.16 | [CT] p. 4, Table 1 (note's ratios) |
   | bonczar2024 | 0.92 | 0.95 | 1.01 | 1.04 | 1.14 | pooled review, pp. 5-9, Tables 2-6 (note's ratios) |

   abbas2021 plots AH/pH x 100 at about 93 to 104 across L1 to L4 and about 117 at L5 in non-stenotic adults, with
   no SD [CT] (abbas2021 pp. 4-5, Figs. 5-6). busscher2010 warns that 0.94 to 1.01 is shared by C3-C7, T3-T4 and L3-L4, so combine the ratio with other
   features there [cad] (busscher2010 p. 1107, Table 3). Inference (tan2004 values L1 20.2/22.4, L2 20.8/23.1):
   the tan2004 L1 and L2 cells both round to 0.90.
6. Expect L3 to be the longest lumbar vertebra and L5 the shortest; a lumbar vertebra about 6 mm shorter in L than
   its upper neighbour and taller in front than behind is the L5 candidate (gilad1985 p. 120; Table 2, p. 118;
   the 6 mm rule is the note's Inference).
7. Read the canal against the body, free of magnification:
   - canal to body depth about 0.57 to 0.61 at L1, 0.52 to 0.55 at L2 and 0.45 to 0.50 at L3 to L5 [DB]
     (amonookuofi1985 p. 74, Table 4; p. 75);
   - APD over VAPD 0.70 at L1, 0.64 at L2 and 0.58 at L3 to L5, separating L1, L2 and L3 only [CT]
     (alonge2021 pp. 73-74);
   - canal depth over upper body depth about 0.60 at T12 falling to 0.42 at L4, 0.45 at L5 and 0.35 at S1 [CT]
     (yadav2020 pp. 177-178, Tables 2-3; ratios are the note's Inference).
   Place the canal's posterior limit at L1 to L4 on the line joining the apex of the superior articular process and
   the inverted apex of the inferior one of the same vertebra, and at L5 just in front of the radiolucent lake of
   the spinous process; a guessed limit falls too far anterior (eisenstein1977 pp. 174-175; p. 178; Fig. 2, p. 176).
8. Read the discs as a sequence, never one disc alone:
   - anterior disc height rises at every step from L1-L2 (about 5.7 mm) to L5-S1 (about 10.8 mm) [CT] (shin2024
     pp. 3-4, Tables 2-3);
   - anterior over posterior is about 1.4 to 1.8 at T12/L1 to L4/5 and about 2.2 at L5/S1, and T12/L1 is the
     smallest of the six discs measured [CT] (bach2019 p. e113, Table 6; ratios are the note's Inference);
   - mean disc height peaks at L4-5 and drops at L5-S1 in both sexes, young and old [cad] (twomey1985 p. 497,
     Table 2); the convexity index M/(A + P) is 0.56 to 0.68 from L1-2 to L3-4 and lowest at young L5-S1 (0.43 men,
     0.49 women) (twomey1985 p. 496; p. 497, Table 3; its use on a film is the note's Inference);
   - prefer anterior disc height on films and do not use the posterior one for naming (kunkel2011 p. 380; p. 383).
9. Read the foramen height: about 16.5 to 17 mm at its L2-L3 and L3-L4 peak and about 13.5 mm at L5-S1 [CT]
   (masharawi2021 p. 9, Table 4); about 17 to 19 mm from L1-L2 to L4-L5 and about 15 mm at L5-S1 [CT] (shin2024
   p. 5, Table 6). A foramen 3 to 4 mm lower than expected at L4-L5, with lower foramina above it, suggests a
   degenerative slip, not a shift of level (masharawi2021 p. 10, note).
10. Read the pedicle's sagittal angle against the superior end plate where the pedicle is seen:
    - about 10 to 12 deg at T11 and T12 and about 5 to 6 deg at L1 and L2, a drop of about 4.6 deg at T12/L1, with
      lumbar SDs up to 2.1 deg [DB] (lien2007 p. 1218, Table 2; its film use is the note's Inference);
    - lumbar near 0, T12 about 12 and T2 to T11 about 15 to 17.5 deg [cad, CT] (zindrick1987 p. 164, Table 4);
      check the sign convention first;
    - at L5 expect two populations, about +5 to +8 and -8 to -10 deg, and never average them (olsewski1990 p. 543;
      pp. 545-547). Film values run 3 to 6 deg below bone (mitra2002 p. 453; p. 455, Table 2).
11. Check the beam: end plates must project edge-on as single lines before a disc height or a corner is used
    (kunkel2011 pp. 377, 383; shin2024 note). With one central ray on C4 or L3, the end plates of C2, C7, L1 and L5
    are struck obliquely and show double contours (gilad1985 note). A minimally rotated lateral film hid the
    sagittal canal diameter in hinck1966's Case I (hinck1966 p. 149).

### Step 5. On a fluoroscopy frame

1. Know what the set lacks: no paper measures on fluoroscopy, and none gives a C-arm's geometry or magnification.
   Inference: treat a C-arm frame as a film of unknown M (Step 1, rule 4) and work in ratios.
2. Do not settle a thoracolumbar level from the AP frame and its ribs alone. Where the twelfth rib is rudimentary
   or absent, top-down and bottom-up counts on intraoperative fluoroscopy often disagree; the authors advise
   tracing the whole rib cage on a preoperative CT (duman2026 pp. 12-13). Inference: carry the name from that CT to
   the frame by a landmark both show, not by a fresh count.
3. On a lateral frame, distrust a screw tip far from the midline: the radiographic blind spot is largest there, and
   a laterally placed tip can lie outside the anterolateral cortex while projecting inside the body (zindrick1987
   p. 165; the second clause is the note's Inference).
4. On an en-face (coaxial) view of a lumbar pedicle, use the ellipse's tilt as a level cue: within about 8 deg of
   vertical at L1 to L3, about 30 deg with a wide spread at L4 and 50 to 55 deg at L5, its upper pole toward the
   midline [DB films] (robertson2000 p. 711, Table 1, Figure 5). Do not lean on L4's tilt alone, whose SD is 17 to
   21 deg (robertson2000 p. 711, Table 1). Inference: only a view along the pedicle axis approximates the
   cross-section perpendicular to it (makino2012 note).
5. Treat the safe-zone widths and the breach margins as upper bounds, since they come from dry bone and cadavers;
   the authors call the safe zone practicable in fluoroscopy-guided surgery (lien2007 p. 1220; p. 1219, Table 4;
   p. 1221).

### Step 6. A limited field of view

Inference throughout, from the steps above.

1. List the anchors in the frame before naming anything: the sacrum and ala (S1), the lowest rib and the TPW/EPWu
   minimum (T12 on an AP), the C7/T1 IPD drop and the widest transverse process (T1 on an AP), C2 (on a cervical
   lateral).
2. With one anchor in view, count from it and carry its failure: from the sacrum, the 4.3% count-changing
   lumbosacral states of dry bone (eisenstein1977 p. 177); from the lowest rib, the 14.9% short or absent twelfth
   ribs of Turkish CT (duman2026 p. 10).
3. With no anchor in view, name the instances only relative to one another, as an ordered run, and answer with a
   distribution over the run's absolute position. Where a full-field image exists (a scout, a preoperative CT or a
   long film), take the absolute names from it.
4. In a mid-thoracic frame expect no help from IPD (T4 to T10 differ by at most 1.4 mm in all; hinck1966 p. 142,
   Table IA, note) or from body height (kunkel2011 p. 379); use the disc ratios to place the run in the upper, middle or lower
   thorax (kunkel2011 p. 379, Table 3).
5. Give the decoder's missing-body transition the observation rates of the films: C2 unclear in 11 of 141 and C7
   hidden in 15 of 141 lateral cervical films of healthy young men (gilad1985 p. 117); C1 and C2 absent on every AP
   (hinck1966 p. 142).

### Step 7. When to answer with uncertainty on a film

Inference throughout.

1. Answer with a distribution whenever the frame holds no anchor, the IPD and the wedge disagree at L5, the lowest
   rib is short or missing, the view is rotated beyond what Step 3, rule 11 can correct, or a red flag of Part 2A,
   Step 10 is present.
2. Never name a level from one film value: every film norm in the set is a population mean with between-subject
   SDs larger than most adjacent steps (hinck1966 p. 142; gilad1985 p. 118; amonookuofi1982 p. 228).
3. Never name a thoracolumbar or lumbosacral level from an AP frame alone (duman2026 pp. 12-13).
4. Abstain, and say why, when the view cannot show the measures that carry the nearest junction (Step 2).

## What the set does not give

Each line is one gap; the anomalies and error parts list them with their sources.

- No count of T13, or of 11 or 13 thoracic vertebrae or rib pairs, anywhere (duman2026 p. 5 names them and never
  reports them).
- No grading of a transitional vertebra (Castellvi or any scheme), no side of a transitional joint, and no
  measure of any kind taken on a transitional segment (eisenstein1977 p. 177).
- No prevalence of a lumbosacral variant in a living general population; the counts are dry bone (eisenstein1977)
  and Marfan films (ahn2001).
- No joint rate of rib and lumbosacral variants in one person.
- No prevalence of block vertebrae or hemivertebrae.
- No measured effect of any variant on any measure, except smaller facets beside a sacro-transverse joint
  (eisenstein1977 p. 177) and the syndromic IPD changes (ahn2001 p. 68; hinck1966 pp. 152-153).
- No living-patient thoracic film norm except hinck1966's AP IPD; kunkel2011's thoracic heights are from specimen
  contact films (kunkel2011 p. 377).
- No C-arm geometry, magnification or fluoroscopic measurement study.
- No error figure for a SPINEPS mask against manual measurement, and no rate of instances split or merged at the
  sacrum or lost from a field of view.
- No rib and no pedicle label in SPINEPS (bordercall scanimport/schemes.py, code); TPW and SPL are in the pool
  with no measurer, and C2 and S1 lie outside the pool (schwingcheck README, code).
- No measure of the dens or the atlanto-axial joint.
- No confirmation that Panjabi's cervical, thoracic and lumbar papers define each measure alike, which the steps at
  C7/T1 and T12/L1 assume.
