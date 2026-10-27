# coarse: what a field can say when it cannot name its level

Confidential with the rest of this repository: nothing here goes to a public place before the provisional is filed.

The owner's queue of 27 October 2026, 09:44 UTC, item 6, third line: "extend to other coarse predictions such as below T12, below T5, and any others with citable clinically beneficial utility". The exact rule's posterior over places is a posterior over the level of every body in the field. So a coarse claim about one body is a sum of that posterior: "the middle body is below T12" is the mass on L1 to L5. The claim is made only when that sum reaches 0.99 (or the opposite claim, when it falls to 0.01). While the generator is the truth, a claim made this way is right at least 99 per cent of the times it is made, whatever the claim ([archive/bordercall/exact.py](../archive/bordercall/exact.py), guarantee 3). What varies from claim to claim is how often a field lets one make it.

Every number here comes from synthetic columns drawn from Panjabi's tables: 400 typical columns at the archive's score seed, every window of each width, the claim about the window's middle body. Nothing here is a patient.

## The claims and why each matters

| Claim about the middle body | Why it matters |
| --- | --- |
| below T5 (T6 or lower) | The T5 to T12 sagittal curve grades the Lenke classification's sagittal thoracic modifier, and so the extent of a scoliosis fusion (Lenke LG, Betz RR, Harms J, et al. J Bone Joint Surg Am 2001;83(8):1169-1181). |
| at or above T6 | Autonomic dysreflexia follows spinal cord injury at or above T6, so the injured level's side of the T6/T7 border sets the monitoring (Krassioukov A, Warburton DE, Teasell R, Eng JJ. Arch Phys Med Rehabil 2009;90(4):682-695; the level is in the review's background, not its abstract). |
| below T12 (lumbar) | Half of the spine surgeons surveyed reported operating at a wrong level at least once in their careers (Mody MG, Nourbakhsh A, Stahl DL, et al. Spine 2008;33(2):194-198). The count from the lowest rib or from the sacrum is the one a transitional column misleads. |
| below L2 (L3 or lower) | Anaesthetists identified a marked lumbar interspace correctly in only 29 per cent of patients, and placed it one space higher than they assumed in 51 per cent (Broadbent CR, Maxwell WB, Ferrie R, et al. Anaesthesia 2000;55:1122-1126). The conus was damaged where spinal anaesthesia was given above the intended space (Reynolds F. Anaesthesia 2001;56:238-247). |
| within T11 to L2 | The junction of the rib-stiffened thoracic spine and the mobile lumbar spine. Injuries of the thoracolumbar spine are classified and treated by the Thoracolumbar Injury Classification and Severity Score (Vaccaro AR, Lehman RA Jr, Hurlbert RJ, et al. Spine 2005;30(20):2325-2333). |
| below C7 (thoracic) | The cervicothoracic junction. It is kept as a reference border, and no source for its clinical use was checked here. |

Each citation was checked on 27 October 2026 against its abstract or a library record: the T5 to T12 basis of the Lenke modifier, Mody's half of surgeons, and Broadbent's 29 and 51 per cent are in the abstracts. Krassioukov's T6 is the field's standard level, stated in the review's background and not in its abstract.

## What the fields allow

The share of fields where the claim is decided at 0.99 either way, with all seven measures, on the nominal world (the generator is the truth). In brackets is the share decided among middle bodies within two levels of the claim's border, where the claim is hard and matters most:

| Claim | n = 1 | n = 3 | n = 5 | n = 9 |
| --- | --- | --- | --- | --- |
| its exact level | 0.006 | 0.166 | 0.371 | 0.729 |
| below C7 | 0.906 (0.564) | 0.985 (0.929) | 0.995 (0.979) | 0.998 (0.990) |
| below T5 | 0.671 (0.039) | 0.759 (0.135) | 0.833 (0.357) | 0.971 (0.899) |
| at or above T6 | 0.672 (0.046) | 0.747 (0.119) | 0.817 (0.290) | 0.962 (0.866) |
| below T12 | 0.706 (0.068) | 0.849 (0.460) | 0.933 (0.734) | 0.978 (0.902) |
| below L2 | 0.708 (0.033) | 0.824 (0.207) | 0.919 (0.528) | settled by the window |
| within T11 to L2 | 0.574 | 0.696 | 0.829 | 0.961 |

1. **Coarse claims come far sooner than names.** One body is named at 0.99 in 0.6 per cent of fields, but it says thoracic or lumbar in 71 per cent. Three bodies are named in 17 per cent and say it in 85 per cent; five bodies say it in 93 per cent.
2. **Near the border, a few bodies are not enough.** The decided share near the border is small at one body (4 to 7 per cent) and grows with the field: at five bodies, 73 per cent of middle bodies within two levels of T12/L1 are called lumbar or thoracic, and 90 per cent at nine. The far cases, which nobody gets wrong, make most of the decided share at one body.
3. **The promise holds where the rule is told the truth.** In the nominal and film worlds, with all seven measures or one film's, and with either rule, every claim made at 0.99 was right at least 99.2 per cent of the time. With all seven measures it was right at least 99.86 per cent of the time ([tests/test_study.py](tests/test_study.py) holds the record to 99 per cent). The promise is an average over all fields, not over the hard ones. Near a border the counts are small, and they can fall short: the scale-free rule's "below T12" at one body was wrong in 4 of the 20 decisions near the border.
4. **One film's measures say less.** An AP film (EPWu, EPWl, SCW) decides "below T12" at five bodies in 0.825 of fields, and a lateral film (EPDu, EPDl, VBHp, SCD) in 0.702, against 0.933 with all seven. Both still keep the promise.
5. **A wrong magnification breaks the promise near the border, and the scale-free rule does not see it.** With every film magnified 1.35 while the rule assumes 1.15 (two of its spreads off), overall precision stays above 0.996. Near the border it does not: "below T5" at one body was wrong in 18 of the 174 decisions near T5/T6, and "at or above T6" in 19 of 160, a precision of 0.88 to 0.90 there. The scale-free exact rule does not see the scale, so its results are the same in every world. It decides less at one body ("below T12" 0.461 against 0.706) and nearly as much by nine (0.976 against 0.978). Where a film's magnification is not known to be right, the coarse claim should come from the scale-free rule.

`TABLE.md` beside the record gives every world, every plane and both rules.

## Commands

```sh
~/venv-sc/bin/python -m coarse --outdir coarse/records/coarse-2026-10-27
~/venv-sc/bin/python -m unittest discover -s coarse/tests -t .
```

The study imports [combinations/study.py](../combinations/study.py) for its worlds and its scale-free rule, and runs in the environment of [requirements-schwingcheck.txt](../requirements-schwingcheck.txt). [records/coarse-2026-10-27/](records/coarse-2026-10-27/) holds the record (`coarse.json`: each claim's decided share, errors, precision with its cluster standard error, and the same within two levels of the border) and `TABLE.md`. The claims' reasons and sources in the record were corrected after the run. The borders, and so every number, are as run, and the record says so.
