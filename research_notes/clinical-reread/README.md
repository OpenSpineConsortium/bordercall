# Every paper reread for its clinical detail

Source: thread "Reread every paper for clinical detail", project symphony_4, 2026-10-28, 19:04 to 21:20 UTC.
Confidential, like the rest of this repository: nothing here goes to a public place.

## Why

The papers behind the generator and the synthetic_spine tables had been read only for their printed values. On 2026-10-28
at 19:03 UTC the owner asked for every PDF he had given to be read again for what its prose holds:

> "eisensteins entire discussion is about lstv, different indications and prevalences, radiographic projection of
> morphological metrics including how to measure certain things like the posterior canal using just a lateral xray and
> the intricacies all the way down to specfic levels and pearls and pitfalls"

At 19:05 UTC he added that these details are "to at least direct the autonomous anatomist". At 19:08 UTC he gave the
direction they serve: the Bayesian generator draws per-level morphometric dimensions; code computes the same dimensions
from each vertebra instance of a real 3D CT mask; a classifier or the Bayes rule gives each instance a probability over
levels; a sequence decoder (an HMM or Viterbi chain with transitions for a missing body, an L6 or a T13) turns the
instances into named levels, a semantic segmentation. The same names are wanted on radiographs and fluoroscopy.

## What is here

- [notes/](notes/): one note per paper, 43 in all: the 42 papers of spine-program's synthetic_spine/sources.csv and
  Panjabi's facets paper of 1993. Each has the same headings: what the paper is (population and what each count is made
  of, modality, how levels were counted); anomalies, numbering and transitional segments with every prevalence and its
  denominator; every measure as a recipe (landmarks, plane, from a 3D CT instance mask, from a radiograph alone, its
  course across levels, its covariates, its error); level by level and at the junctions; measurement error; clinical
  pearls, indications and pitfalls; numbered instructions for the autonomous anatomist; what it means for bordercall's
  generator and classifier; gaps and conflicts. Every detail cites the printed page and the PDF page.
- notes/<id>.json beside every note: the same content as a structured record (anomalies, measures, level details,
  errors, pearls and pitfalls, instructions), for code and for the synthesis to read.
- [HANDOFF.md](HANDOFF.md): where the work stopped and what comes next.
- [tools/](tools/): the checks and the workflow scripts that made and will finish the notes.
  - check_notes.py holds every note to the rules below; `python3 -I tools/check_notes.py notes <folder of the PDFs>`.
  - reread_group.js is the Workflow script that read and checked the papers, one reader and one skeptic per paper.
  - synthesis.js and prep_synth.py are the synthesis, written and not yet run (HANDOFF.md).
  - PAPERS.sha256 names the exact bytes of every PDF read.

## How the notes were made

Each paper was read whole, every page as an image, by one reader, who wrote the note and its record. A second reader,
told to assume the note wrong and incomplete, then read the whole PDF again on its own, checked every number and page
against the page images, added what the first left out and labelled as Inference everything the paper does not state.
All 43 notes went through both: 39 in the first session, and the last four (kunkel2011, moncadahabib2025, otsuki2021
and twomey1985), which the first reader had drafted when that session reached its usage limit, checked by a second
reader on 2026-10-28 in the session that took the work over. The skeptics' reports that were kept (42 of the 43) list
between 13 and 37 changes per note; most were derived ratios or ranges stated too strongly, inferences not labelled as such, and details that only a
figure gives. Few were transcribed values: the readers' table values almost always matched the page images.

The rules every note keeps, held by tools/check_notes.py: no passage of a paper is copied (no run of 13 or more words
below the citation matches the paper's own text, so a quote is 12 words at most); no page image, no PDF and no
publisher download stamp is in git; every count says what it is made of; ASCII only. The PDFs stay in the project's
files (literature/synthetic_spine/ with its MANIFEST.md) and the owner's uploads.

## What the reread found first

These are the first things the notes hold for the naming model; the synthesis will gather the rest. Each is cited in
its note.

- Lumbosacral transitional anatomy in 36 of Eisenstein's 443 South African dry skeletons (8%): 9 lumbarised S1, 16 with
  persistent S1-S2 facet joints, 8 sacralised L5, 2 true sixth lumbar vertebrae (both in the 168 Sotho skeletons) and 1
  transitional vertebra; besides these, 10 sacro-transverse joints. A trefoil canal in 66 of 443 (15%), always at L5 and
  sometimes at L4; spondylolysis in 10 skeletons, 9 of them at L5 ([eisenstein1977](notes/eisenstein1977.md)). The note
  also records exactly how he measured: a vernier caliper on the dry vertebra, the canal's sagittal diameter as a minimum
  and the interpedicular distance as a maximum, and film magnification factors from 55 vertebrae of 11 skeletons at a
  110 cm tube distance, which bears on the open question in spine-program PR 239.
- Rib anomalies in 96 of 517 adult Turkish chest CTs (18.6%): a hypoplastic 12th rib in 55 (10.6%), an absent 12th rib
  in 22 (4.3%), a lumbar rib in 12 (2.3%) and a cervical rib in 7 (1.4%). The paper does not say how levels were counted
  and gives no T13, L6 or transitional rate ([duman2026](notes/duman2026.md)).
- A transitional lumbosacral vertebra in 5 of 32 adults with Marfan syndrome (15.6%), whose interpediculate distances
  are widened by dural ectasia: a red flag that makes a level read as a lower one ([ahn2001](notes/ahn2001.md)).
- Panjabi's four papers report no anomaly: all 12 spines have five lumbar vertebrae and no sacrum was kept. T11 and T12
  carry a single rib facet on the body and T12 no costotransverse facet, the thoracolumbar marker in his own specimens
  ([panjabi1991t](notes/panjabi1991t.md)). His frame, by the paper his lumbar paper points to, runs X along the upper
  posterior corners, chosen because they resist osteophytes, with a stated +/-0.5 mm point error, on boiled and bleached
  fresh autopsy spines ([panjabi1992](notes/panjabi1992.md)).
- Pedicle height falls from L1 to L5 in every series Abu-Leil and Masharawi tabulate, which makes Panjabi's rise at L5 the
  outlier ([masharawi2021](notes/masharawi2021.md)); in Bonczar's meta-analysis only pedicle width separates most
  adjacent lumbar levels by its own interval test ([bonczar2024](notes/bonczar2024.md)); Hinck's interpediculate steps
  at T12/L1 and L4/L5 are smaller than one patient-to-patient SD, so that distance alone does not name those levels
  ([hinck1966](notes/hinck1966.md)).

## The papers

| id | paper | population | modality | checked |
|---|---|---|---|---|
| [abbas2021](notes/abbas2021.md) | Abbas 2021: The role of vertebral morphometry in degenerative lumbar spinal stenosis | Israel, living patients, all aged 40 or over; ethnicity not stated. Stenosis group: 165 patients with symptomatic degenerative lumbar spinal stenosis ... | CT, Philips Brilliance 64, 120 kV, 150 to 570 mA, slice thickness 0.9 ... | yes |
| [ahmed2019](notes/ahmed2019.md) | Ahmed 2019: Radiological anatomy of the lumbar canal, an MRI study | India, Telangana state (Karimnagar), living symptomatic adults: 80 patients (36 men, 44 women) aged 20-70 years referred for lumbar MRI between June ... | MRI, GE Signa HDxt 1.5 T, sense spine coil, 4 mm slices (4.3 mm on ... | yes |
| [ahn2001](notes/ahn2001.md) | Ahn 2001: The lumbar interpediculate distance is widened in adults with the Marfan syndrome | United States, living adults: 32 volunteers with Marfan syndrome by the DePaepe (1996) criteria, 18 female and 14 male (14 by subtraction), recruited ... | Standard AP and lateral radiographs of the lumbosacral spine (printed ... | yes |
| [alonge2021](notes/alonge2021.md) | Alonge 2021: Lumbar spinal canal dimensions in Nigerians on CT | Nigeria; living adults; 120 abdominal CT examinations from the CT database of Lagoon Hospitals, Lagos, 1 July 2017 to 30 June 2019, taken as 120 ... | CT (abdominal scans, sagittal and axial reconstructions side by side ... | yes |
| [amonookuofi1982](notes/amonookuofi1982.md) | Amonoo-Kuofi 1982: Lumbar interpedicular distances in adult Nigerians | Nigeria, ethnic group within Nigeria not stated; living adults. 290 plain AP lumbar radiographs of 290 patients (150 men, 140 women), aged 20-45 ... | Plain anteroposterior lumbar radiographs only, anode-film distance ... | yes |
| [amonookuofi1985](notes/amonookuofi1985.md) | Amonoo-Kuofi 1985: Sagittal diameter of the lumbar canal in normal adult Nigerians | Nigeria; dry bone: complete sets of lumbar vertebrae of 122 adults (79 male, 43 female), aged 23-60 years, from the osteological collection of the ... | Osteometry of isolated dry vertebrae with a sliding vernier caliper ... | yes |
| [arockiaraj2025](notes/arockiaraj2025.md) | Arockiaraj 2025: CT morphometry of lumbar pedicles in 1,500 Saudi vertebrae | Saudi Arabia, one tertiary centre in Riyadh (claimed representative of the country, p. 316 (PDF 5), p. 318 (PDF 7)); 300 living adult Saudi patients, ... | Non-contrast CT, 2.5 mm contiguous axial sections from L1 to S5, 140 ... | yes |
| [bach2019](notes/bach2019.md) | Bach 2019: Lumbar intervertebral disc height on CT by level, sex and decade | 240 anonymized abdominal CT scans of living patients, 131 women and 109 men, University of South Florida (Tampa, Florida, USA), January 2010 to ... | CT (scanner, slice thickness, kernel, voxel size not reported) ... | yes |
| [bonczar2024](notes/bonczar2024.md) | Bonczar 2024: lumbar vertebral morphology, a systematic review and meta-analysis | 1481 'individuals' (abstract: 'patients') summed from the research-group column of 18 published studies (Table 1, p. 3, PDF 3). Asia 1076 in 14 ... | Systematic review and random-effects meta-analysis (PRISMA; CATAM and ... | yes |
| [busscher2010](notes/busscher2010.md) | Busscher 2010: Comparative anatomical dimensions of the complete human and porcine spine | Human: fresh frozen spines (C3-S1, ligaments and discs intact, about 3 cm of rib kept with costotransverse and costovertebral joints) of 6 male ... | CT of dissected specimens, Siemens scanner printed as 'Somaton ... | yes |
| [chaudhary2015](notes/chaudhary2015.md) | Chaudhary 2015: Lumbar interpedicular distance on plain AP radiographs in Haryana | India, Sonepat district, Haryana (North India); living adults (Inference: hospital films). 300 plain AP lumbar radiographs of 300 subjects, 150 men ... | Plain AP lumbar radiographs only, measured on the film with a scale ... | yes |
| [chen2011](notes/chen2011.md) | Chen 2011: Geometry of thoracolumbar vertebral endplates (T10 inferior to L3 superior, CT) | CT arm: 83 living patients (mean age 43, range 21 to 65) with a thoracic or abdominal CT for abdominal or thoracic symptoms and no spinal complaint, ... | CT, GE LightSpeed VCT, multiplanar reformats 0.625 mm thick; figure ... | yes |
| [cizmic2023](notes/cizmic2023.md) | Cizmic 2023: Lumbar spinal canal midsagittal and interpedicular diameters on CT in Bosnia and Herzegovina | Bosnia and Herzegovina, single centre (Radiology Department, General Hospital "Prim. dr. Abdulah Nakas", Sarajevo); 200 living adult patients with ... | CT: 40-slice Siemens Somatom Definition AS, 120 kV, 266 mAs, ... | yes |
| [duman2026](notes/duman2026.md) | Duman 2026: MDCT morphometry of the thoracolumbar junction (T11 to L2) and 12th-rib anomalies in 517 Turkish adults | Turkey, single tertiary chest diseases and thoracic surgery hospital (Izmir); 517 living adult patients (277 men, 240 women), called consecutive in ... | CT: 64-slice MDCT (Philips Brilliance), 120 kVp, AEC 150-250 mA, ... | yes |
| [eisenstein1977](notes/eisenstein1977.md) | Eisenstein 1977: Lumbar morphometry and pathological anatomy in South African skeletons, with reference to spinal stenosis | South Africa, Raymond Dart Collection (Department of Anatomy), dry macerated skeletons: 443 adult skeletons (113 'white' Caucasoid: 78 M, 35 F; 162 ... | Dry bone vernier caliper (method of Jones and Thomson 1968); ... | yes |
| [frontphys2026](notes/frontphys2026.md) | Li 2026: CT morphology of L1 to L5 bodies and regional HU distribution in 100 Chinese adults | 100 living Chinese adults (text: 50 men and 50 women; Table 1 sums to 46 men and 54 women), aged 20 to 70, five decade groups of 20 each (mean ages ... | Multidetector CT: Siemens Somatom Definition 64 AS+, 120 kV, 3.0 mm ... | yes |
| [gilad1985](notes/gilad1985.md) | Gilad 1985: Sagittal evaluation of elemental geometrical dimensions of human vertebrae | Living healthy working men, 20-38 years (mean 26.8), mean stature 174.7 cm, employees of a major transportation cooperative with periodic check-ups; ... | Plain lateral radiographs, one cervical plate (standing, neutral, ... | yes |
| [griffith2016](notes/griffith2016.md) | Griffith 2016: Population reference range for developmental lumbar spinal canal size (CT, Hong Kong Chinese) | Hong Kong; 1,080 living ambulatory adult patients having abdominopelvic CT at the authors' institution (affiliations Prince of Wales Hospital, The ... | 64-slice MDCT (GE LightSpeed VCT), reconstructive resolution 0.6 mm, ... | yes |
| [hinck1966](notes/hinck1966.md) | Hinck 1966: Normal interpediculate distances (minimum and maximum) in children and adults | USA, Portland, Oregon: white living hospital patients found by a systematic search of the University of Oregon Medical School's radiograph files, ... | AP spine roentgenograms at a 40 in (101.6 cm) target-film distance, ... | yes |
| [hou1993](notes/hou1993.md) | Hou 1993: Pedicle morphology T9 to L5 in a Chinese population | China (Chinese, called an oriental population), dry bone: disarticulated vertebrae from the anatomy department of the 4th Military Medical Institute, ... | Direct measurement of dry bone with Vernier calipers (0.1 mm), one ... | yes |
| [italianmri](notes/italianmri.md) | Pierro 2017: Sagittal normal limits of the lumbosacral spine on MRI in 604 Italian adults | Central and Southern Italy, all Caucasian; living adults whose lumbosacral MRI scans were selected from all adults referred to one radiology ... | 1.5 T MRI (GE Signa Excite HD), sagittal T1-weighted FSE (TR/TE 420/8 ... | yes |
| [krag1988](notes/krag1988.md) | Krag 1988: Morphometry of the thoracic and lumbar spine for transpedicular screws | USA (Medical Center Hospital of Vermont), living patients: 91 vertebrae T9-L5 from 41 patients (14 women, 27 men), aged 18-75 years (mean 36, median ... | Retrospective axial CT, Siemens Somatom 2 third-generation scanner, ... | yes |
| [kunkel2011](notes/kunkel2011.md) | Kunkel 2011: Thoracic disc heights and their relation to vertebral body heights | Human body donors, country and ethnicity not stated (authors at Ulm, Germany; German Research Foundation funding). 72 isolated thoracic motion ... | Two methods on the same fresh-frozen segments: lateral contact ... | yes |
| [lien2007](notes/lien2007.md) | Lien 2007: Pedicle morphometry and the peri-pedicle safe zone, T1 to L5 | Taiwan. Dry bone arm: 15 sets of human vertebrae (8 male, 7 female), each T1 to L5 separated and measured individually, obtained from the Department ... | Dry bone morphometry with Vernier calipers (0.1 mm) and a standard ... | yes |
| [makino2012](notes/makino2012.md) | Makino 2012: Lumbar pedicle morphology in degenerative spines on MPR-CT, and a screw-diameter index | Japan, one hospital (authors' orthopaedic department, Kawachinagano, Osaka; p. 1516, PDF 1): 50 consecutive living patients who had preoperative ... | Helical CT, GE Light Speed Plus; slice thickness 1.25 mm; 120 kVp; ... | yes |
| [masharawi2021](notes/masharawi2021.md) | Abu-Leil 2021: Morphology of the lumbar neural arch in degenerative spondylolisthesis | Israel (Table 6 labels the sample Israeli; no ethnicity given), living hospital patients aged 50-80, one lumbar CT each: 100 CTs randomly chosen from ... | Supine lumbar CT (scanner, slice thickness, kernel and reformats not ... | yes |
| [mitra2002](notes/mitra2002.md) | Mitra 2002: Lumbar pedicle morphometry in an Indian cadaver population | India (Nagpur), cadavers of the Department of Anatomy, Government Medical College and Hospital, Nagpur: 20 cadavers, 18 men aged 20 to 70 and 2 women ... | Three methods on the same specimens: direct measurement (Vernier ... | yes |
| [moncadahabib2025](notes/moncadahabib2025.md) | Moncada-Habib 2025: Lumbar pedicle morphometry in the Mexican population | Mexico (Mexican adults; ethnicity, birthplace and mestizo or Indigenous origin not defined), living patients at one tertiary neurosurgical centre ... | CT, 1.0 mm slices, 250 mm field of view, 120 kVp, 200 to 250 mA, ... | yes |
| [olsewski1990](notes/olsewski1990.md) | Olsewski 1990: Morphometry of the lumbar spine for transpedicular fixation | Buffalo, New York, USA; no race or ethnicity, height or weight reported. Part 1: lumbosacral spines of 49 embalmed cadavers (24 men aged 60-90, mean ... | Part 1: vernier caliper (+/-0.1 mm) and protractor (+/-1 deg) under a ... | yes |
| [otsuki2021](notes/otsuki2021.md) | Irie 2021: Micro-computed tomography analysis of the lumbar pedicle wall | USA, accredited tissue bank (Science Care, Phoenix, Arizona): six fresh-frozen cadaveric lumbar spines L1-L5, 3 men and 3 women, aged 50-67 (mean ... | Micro-CT of excised pedicles: Scanco muCT 50, each pedicle in ... | yes |
| [panjabi1991c](notes/panjabi1991c.md) | Panjabi 1991: Cervical human vertebrae, quantitative three-dimensional anatomy of the middle and lower regions | 12 fresh autopsy spines (8 men, 4 women), mean age 46.3 years (19 to 59), mean weight 67.8 kg (54 to 85), mean height 167.8 cm (157 to 178); ... | Direct 3D digitising of cleaned vertebrae with a purpose-built ... | yes |
| [panjabi1991t](notes/panjabi1991t.md) | Panjabi 1991: Thoracic human vertebrae, quantitative three-dimensional anatomy | Country and ethnicity not stated (Inference: US autopsy service; corresponding author at Yale). Cadaveric dry bone: 12 fresh autopsy whole spines C2 ... | Dry-bone 3D morphometry: bones cleaned by boiling, bleach (0.5 h) and ... | yes |
| [panjabi1992](notes/panjabi1992.md) | Panjabi 1992: Human lumbar vertebrae, quantitative three-dimensional anatomy | 12 fresh autopsy spines, C2 (axis) to the last lumbar vertebra, no sacrum; this report 60 lumbar vertebrae (L1-L5 of the 12 spines; Inference: 12 x ... | Dry-bone 3D morphometry: soft tissue removed (ref 13 p. 888: boiled, ... | yes |
| [panjabi1993f](notes/panjabi1993f.md) | Panjabi 1993: Articular facets of the human spine, quantitative three-dimensional anatomy | 12 fresh autopsy spines, axis (C2) to the last lumbar vertebra, no sacrum, disarticulated into 276 vertebrae (12 spines x 23 levels, C2-C7, T1-T12, ... | Dry-bone three-dimensional morphometry: a purpose-built morphometer ... | yes |
| [robertson2000](notes/robertson2000.md) | Robertson 2000: The radiologic anatomy of the lumbar and lumbosacral pedicles | 10 dry-bone lumbosacral spine specimens giving 100 lumbar pedicles (L1 to L5, left and right; Inference: 10 x 5 x 2) and 20 S1 pedicles (10 sacra x ... | Plain radiographs of dry bone. 0.4 mm tinned copper wire drawn tight ... | yes |
| [shin2024](notes/shin2024.md) | Shin 2025 (online 10 Dec 2024): Lumbar disc space height and neural foraminal dimensions on CT, L1-S1 | USA, single institution (authors at Loma Linda University and Loma Linda University Health, with Duke and others; Inference: Loma Linda, Southern ... | CT (GE Discovery 750 HD, 64-slice), read in the IMPAX6 PACS (printed ... | yes |
| [tan2004](notes/tan2004.md) | Tan 2004: Quantitative 3D anatomy of C3 to L5 vertebrae in Chinese Singaporeans |  |  | yes |
| [tang2016](notes/tang2016.md) | Tang 2016: Lower lumbar disc and end-plate morphometry on MRI, compared with earlier studies | USA (Salt Lake City, University of Utah hospital archive), ethnicity not reported; living adults aged 20 to 40 with clinical lumbar MRI whose report ... | Siemens MAGNETOM Avanto 1.5 T MRI, T2-weighted sagittal and ... | yes |
| [twomey1985](notes/twomey1985.md) | Twomey 1985: Age changes in lumbar intervertebral discs | 204 cadavers (post-mortem lumbar spines), block from the upper border of T12 to the lower border of S2 removed within 48 h, mostly within 24 h; ... | Dry dissection of fresh cadaveric lumbar blocks: dial vernier ... | yes |
| [vanderhouwen2009](notes/vanderhouwen2009.md) | van der Houwen 2009: Geometry of the intervertebral volume and vertebral endplates (lumbar CT) | The Netherlands (Groningen), living hospital patients, retrospective: 77 patients (46 men, 31 women), aged 21 to 86 years (mean 49.8), selected from ... | 16-detector MDCT (Siemens), supine, 120 kV, 250 mAs, 0.75 s rotation, ... | yes |
| [yadav2020](notes/yadav2020.md) | Yadav 2020: Lumbar canal and body dimensions by CT in North Indian adults | India: one North Indian tertiary care institute over one year (Inference: the authors' institute in Lucknow, named in the affiliations, p. 175, PDF ... | Unenhanced 64-slice and 128-slice multidetector CT, diaphragm to ... | yes |
| [yu2015](notes/yu2015.md) | Yu 2015: Pedicle morphometry of lumbar vertebrae (male, taller and heavier specimens have bigger pedicles) | USA (Cleveland, Ohio), dry bone: the Hamann-Todd Osteological Collection (more than 3300 treated and dried skeletons of people who died in Cleveland ... | Direct digital caliper on dry bone (precision 0.01 mm), one examiner ... | yes |
| [zindrick1987](notes/zindrick1987.md) | Zindrick 1987: Morphometry of the thoracic and lumbar pedicles | Postmortem adult spine specimens (some whole spines, some only thoracic or only lumbar segments) plus reviewed clinical CT examinations, most often ... | Two routes: (1) disarticulated vertebrae radiographed singly in the ... | yes |

The ids are those of synthetic_spine/sources.csv; otsuki2021 is Irie et al. 2021, whose first author is Irie.
