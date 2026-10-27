# Gold tier 3: what is held, and what ENHANCE.PET 1.6k would add

Confidential with the rest of this repository. Written on 27 October 2026 for the owner's queue of 09:44 UTC, item 7: "see how much gold tier 3 data i have, including checking this source, https://registry.opendata.aws/enhance-pet-1-6k/".

Gold tier 3 is a whole spine, C2 to the sacrum in one study, in one modality, with a person's annotation. A mask a person drew, checked or refined counts as a person's; a machine's mask never raises a tier.

## Held now: 159 persons

Nothing held is gold 1 or gold 2. Gold 3 is 159 persons, counted from the release masks:

- TotalSegmentator, 142 persons. These are v3 subjects whose release masks hold C2 to L5 and the sacrum with at least 200 voxels each and no metal. The count may rise to 156 once the 14 subjects that the level or metal rule dropped are read. The masks are model output refined by hand, which the rule counts as a person's annotation. If the owner reads them as machine labels, these persons move to gold 4.
- VerSe, 17 persons, whose expert masks run from C1 or C2 into the lower lumbar spine with the lumbosacral junction in the field. VerSe labels no sacrum, so a look at each field on the grid must confirm the sacrum.

The source is SchwingNet's corpus-tiers draft (pull request #420, data/corpus-tiers/sources.json, whose rows add to 452 before the same persons in several copies are counted once). That thread is paused, and nothing here changes it.

## ENHANCE.PET 1.6k

What the public bucket enhance-pet-1-6k holds, read from its listing and its two small metadata files (CT-details.xlsx, 72,738 bytes; labels.json, 3,605 bytes) on 27 October 2026. No image or mask was downloaded.

| What | Count | Bytes |
| --- | --- | --- |
| Studies in the bucket | 1,597 | |
| AutoPET Challenge | 1,014 | |
| University Hospital Leipzig | 384 | |
| Azienda Ospedaliero Universitaria Careggi | 199 | |
| Vertebra masks, imaging-data/ground-truth/Vertebrae | 1,597 files | 381,439,888 |
| Rib masks, imaging-data/ground-truth/Ribs | 1,597 files | 312,882,241 |
| CT and PET volumes, imaging-data/images | 3,194 files | 250,202,834,785 |

The paper and the data card count 1,683 studies. The other 86 are UC Davis's, which are in Science Data Bank and not in the bucket. CT-details.xlsx carries their 86 rows blank, and the registry page counts 1,597 studies.

The vertebra masks name every body separately: C1 to C7 (ids 1 to 7), T1 to T12 (8 to 19), L1 to L6 (20 to 25), the two hips (26, 27) and the sacrum (28). There is an L6 and no T13. The slices are 3 mm in 1,168 studies, 2 mm in 177, 5 mm in 180, 3.75 mm in 19 and 1 mm in 52.

### How the masks were made, and the tier they reach

The paper is Ferrara D et al., "Sharing a whole-/total-body [18F]FDG-PET/CT dataset with CT-derived segmentations: an ENHANCE.PET initiative", Scientific Data 2026;13:869, doi:10.1038/s41597-026-07218-y, an advance online publication when read. MOOSE, seven nnU-Net models retrained site by site, drew the masks first. Then, by its Methods, a medical student verified and corrected each scan, a second student reviewed the first, and a radiology resident and a nuclear medicine resident reviewed both. The abstract calls the readers physicians in training. The paper does not say what share of scans needed a correction.

By the owner's rule these are a person's masks: checked and refined by people, as TotalSegmentator's are. So every ENHANCE.PET study whose field holds C2 to the sacrum is gold 3. SchwingNet's tiers draft calls them machine output (its row scidb_enhance_pet_1_6k). The paper says otherwise, and that row needs correcting when the tiers work resumes.

### How many persons

- AutoPET's 1,014 studies are 900 persons (Gatidis S et al., Scientific Data 2022;9:601).
- Leipzig's and Careggi's 583 studies carry a study number only, with no person id, so they are at most 583 persons.
- At most 1,483 persons in all.

How many of those hold C2 to the sacrum is not known without reading the masks. A whole-body FDG PET/CT runs from the skull base to mid-thigh as a rule, and the release blanks the face and skull. SchwingNet's draft guesses 720 of autoPET's 900 are whole. That is an estimate, not a count.

### What a count needs

The count needs one read of the vertebra masks, 381,439,888 bytes, applying the rule TotalSegmentator's count used: C2 and the sacrum each present with at least 200 voxels, and every level between them present. It is a fetch, so it waits for the owner's word. It has not been done.

### What it would add to what is held

AutoPET's CTs are already held on the grid as tcia_fdg_pet_ct_lesions: 900 persons, 366.8 GB (SchwingNet docs/research/data-manifest/MANIFEST.md). They are gold 4 there, because only machine labels have been run on them. ENHANCE.PET's masks of the same scans would make every whole one gold 3 with no new CT, provided each mask can be matched to its held study. A mask's NIfTI carries its CT's shape and affine, which is how they would be matched, but that has not been tried. Leipzig's and Careggi's 583 studies are not held. Their CTs would be a fetch of their own, sized first.

scanimport reads these masks under the label scheme `enhance` (scanimport/schemes.py).
