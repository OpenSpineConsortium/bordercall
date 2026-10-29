# DRR domain-gap study: drafts of your 13 CLAIM and REFORMS answers

Drafted 2026-10-29 for run 2 (prepare 40859208), from the study's records in SchwingNet: docs/research/drr-domain-gap/ (README, PREREG, DEVIATIONS, both runs' summaries) and the notes they cite. Confidential: this file is for you and stays out of git.

The report now answers 63 of its 76 items by code from the run's own files (SchwingNet #455): the record lines, the summary, the groups table, the frozen PREREG.md and what README section 6 records each run does not support. These 13 are what no file of the study says. Each is one key of data/reporting/studies/drr-domain-gap.json, with a proposed answer and, under "Yours to decide", what only you can settle. A field that does not apply starts with "Not applicable:" and gives the reason.

To answer, reply in the thread with the numbers you accept as written (for example "accept 1-13"), and give your own words for the rest. A session copies your words into the file as written, naming your message (your choice of 2026-10-29 03:34 UTC).

## 1. title (CLAIM 1)


Asks: Title naming an AI-methods study and its technology category.

Measuring the gap between synthetic and real X-rays with deep convolutional features and two-sample tests: a pre-registered comparison of digitally reconstructed radiographs made by FleXray's recipe, and of its FluXray edits, with real fluoroscopy and plain film, and a replication test of the recipe's renderer.

Yours to decide: The owner chooses the wording. The owner also decides whether a public title may name FleXray, the encoders or the method before the provisional is filed. The README allows the method in public and keeps the numbers confidential; docs/project.md says nothing goes public before the filing. Moved here: the draft no longer calls the DRRs "FleXray's". The replication read "not replicated", so under PREREG.md section 5 every comparison made through the blocks is of this project's renders, not FleXray's. Keeping "FleXray's DRRs", as the README's own title does, is the owner's call.

## 2. abstract (CLAIM 2)


Asks: Summary of design, methods, results and conclusions.

In a pre-registered study of existing images, 10,127 images in 21 groups (11 synthetic, 3 fluoroscopy, 7 plain film; 20 groups tested, the one-person hip phantom plotted only) were decoded one way and embedded in FleXray's own encoder and an ImageNet ResNet-18, read inversion-invariant. Groups were compared by person-grouped classifier two-sample tests (logistic AUC with a person-cluster bootstrap interval and a permutation p), the unbiased MMD with person-level permutations and Benjamini-Hochberg q, FD64 and PRDC, calibrated by split-half nulls and real-against-real baselines. Each of the seven synthetic sets whose family contrasts the summary prints was told apart from real fluoroscopy and from film. For the primary endpoints, against fluoroscopy and then film: this project's render of FleXray's recipe with the attenuation randomisation off gave AUC 0.94 [0.89, 0.98] and 0.96 [0.94, 0.98]; the same physics from the CT alone gave 0.89 [0.83, 0.94] and 0.93 [0.90, 0.96]; FluXray gave 1.00 [0.99, 1.00] and 0.95 [0.94, 0.96]. The split-half nulls flagged nothing (median AUC 0.49 in FleXray's space). No primary endpoint read "indistinguishable". Every one read "closer than two real corpora", a word at its ceiling here, because two real corpora were told apart at least as surely (median AUC 1.00, least 0.97, over 36 pairs). Rendering the same recipe through this project's blocks and through FleXray's own code read "not replicated": MMD q 0.046 (0.043 without the nulls) with an AUC of 0.50 [0.50, 0.50]. That word rests on the MMD alone, its q 0.004 under the bar and within the permutations' Monte Carlo margin, and under it every comparison through the blocks is of this project's renders, not FleXray's.

Yours to decide: The owner chooses which run is reported. The draft uses run 40859208, the one with FluXray and the frozen MMD family; run 40828920 came first. The owner also states the conclusion in the owner's own words. "A pre-registered study of existing images" should match what you choose for the design (item 4). Moved here: the earlier draft called flexray_drr and flexray_drr_ct "FleXray's physical render" and "its CT-only render" and said every synthetic set was told apart. Both overreached. The README says the comparisons through the blocks are of this project's renders. The four replication-only groups have their family contrasts only in results.json on the grid. These numbers are confidential-results, and the README says no result is final until these 13 answers are in.

## 3. background (CLAIM 3)


Asks: Background, intended use and role of the AI approach.

SchwingNet names vertebral levels on intraoperative fluoroscopy. There, real frames exist but their level labels are the cost, so DRRs rendered from CT are a candidate source of training data. In the record, a detector trained on renders alone found 71.67 percent of vertebral bodies on real film. One trained on film found 97.6, 99.14 or 99.2 percent: three readings of the same three misses in 243 that the record has not settled. FleXray is a segmenter trained on CT-projected labels and FluXray's FLUX.2-edited renders, with real radiographs only of the limbs (arXiv 2609.26756v2). Given C-ArmLSpine's truth boxes, it named 99.14 percent of them. It is zero-shot on those frames by its configs, though not yet confirmed by file (audit item 6). This study measures how far such synthetic images lie from real fluoroscopy and film, compared with the distance between two real corpora. It also asks whether this project's render blocks reproduce FleXray's own renders. It informs the FleXray audit (#391, items 6 to 11). Its AI is an instrument: frozen pretrained encoders and two-sample classifiers that measure a distribution gap. No model is built for any clinical use.

Yours to decide: The owner states the intended use and role. The owner also decides whether to quote the record's figures at all. The 71.67 is graded Reported (docs/textbook/13-renders-physics-and-the-sim-to-real-gap.md table; docs/research/drr-realism-against-our-results.md, STATUS.md C3.6), not in project-status. The film-trained figure is unsettled. FleXray's 99.14 is naming given the boxes, not detection, and is zero-shot only by its configs until audit item 6's census. Moved here: the earlier draft gave the film figure as a settled 99.14 and FleXray as trained with no real spine frame without that caveat, and its source "item 8" of project-status points to that note's section Not checked, which says nothing on this. Confidentiality: the background names project methods.

## 4. study_design (CLAIM 5)


Asks: Prospective or retrospective study.

Retrospective: no person was imaged or enrolled for this study. The real groups are image corpora the project already held, which the sample index lists (PREREG.md section 2); the seven render groups are rendered in the job from held CTs; and the other synthetic groups are sets made before the study, FluXray's from the FleXray data fetched on 2026-10-26. The analysis was pre-registered: PREREG.md froze it on 2026-10-27, before any number of the study was read (its section 7).

Yours to decide: No file of the study uses the word "retrospective" or says no person was enrolled; the second review found the report's earlier code answer said both in its own words, so the item came back to you. You confirm "retrospective", or word it as you prefer, for example "a retrospective analysis of existing image corpora under a pre-registered analysis plan".

## 5. deidentification (CLAIM 11)


Asks: De-identification methods.

The study added no de-identification step of its own. The real corpora are their publishers' releases, read from the grid's copies and banks (C-ArmLSpine through the project's PNG bank). The record states de-identification only for KUB-StoneX, whose record says every image is de-identified (IRB REC-FSIT-2025/No: 12732). C-ArmLSpine's record notes that case134's headers carry a real PatientID, never printed; case134 is a frozen test person, left out of every group. The renders are of public CTs (TotalSegmentator v2.0.1, CC BY 4.0). Wayne State IRB determination HPR 2026-269 covers de-identified public datasets that download without an agreement. Its supplement HPR 2026-330 covers VinDr-SpineXR, which this run did not read. No file that names an image or a person left the grid: results.json, the plan and render-subjects.json stay in the run folder under umask 077. Only BENCH.md and summary.txt, through grid/redact.sed, were copied out.

Yours to decide: The owner confirms which determination covers the corpora held under an agreement: BUU-LSPINE's end-user agreement, AASCE's request form and IEEE DataPort's subscription. The memory says HPR 2026-269 covers datasets that download without an agreement, which is why VinDr needed its supplement. The owner said on 2026-10-14 that permission and the agreements are in hand for all the data. The owner also confirms each publisher's de-identification statement; the repository records one only for KUB-StoneX. Corrected: the earlier draft stated that the work falls under HPR 2026-269 for every corpus, and that only summary.txt left the grid, while BENCH.md left it too.

## 6. acquisition (CLAIM 13)


Asks: Image acquisition protocol.

The render groups' images were made in the job from 26 held TotalSegmentator v2.0.1 CTs (27 chosen, 26 kept by every group) by FleXray's released MOOSE recipe, through this project's render blocks or FleXray's own code, each group changing the blocks the groups table names: flexray_drr (MOOSE labels, attenuation randomisation off), flexray_drr_ct (no labels, FleXray's axial crops drawn uniformly, each aimed at its own centre, attenuation off), flexray_replica (MOOSE labels) and flexray_reference (the same through FleXray's own code), flexray_spineps (SPINEPS labels), and fluxray_raw and fluxray_raw_reference (the paper's raw recipe: whole volume, FluXray's pose grid, cone projection, attenuation off, min-max scaling, 4 views at 1,024 pixels, through the blocks and through FleXray's code). FluXray's images were made by its authors: by the paper (README section 2.3), FLUX.2 klein 9B edited each raw render (4 steps, bfloat16, guidance 1), pixels whose raw DRR was below 0.05 were set to 0, a paired-difference filter dropped about 4 percent of the edits per pose, and the release resized the 1,024-pixel edits to 512, where the project's notes record the stored images at 256. The other synthetic sets are the project's own earlier renders and styled images. The real corpora were acquired by their publishers under their own protocols, which this study does not record beyond what it notes of them: C-ArmLSpine's AP and lateral spot frames of one mobile C-arm, narrow and centred on the lumbar spine; DeepFluoro's vendor fluoroscopy of cadaver pelves, six specimens and two phantoms; a resin hip phantom's fluoroscopy; and plain films (lumbar, whole-spine, cervical, abdominal and cephalometric) from their releases, as JPEG re-exports, 16-bit scans or DICOM.

Yours to decide: The study's files record the render recipes and no real corpus's acquisition protocol: of the real corpora they note only what the groups table's labels and notes and README sections 2, 5 and 6 say (the field of view, the anatomy, the specimens, the file formats), so the second review held that the item cannot be marked answered by code. You choose: accept the sentence above, which says the real corpora's protocols are their publishers'; or give each corpus's device and protocol from its own paper in your words.

## 7. characteristics (CLAIM 36)

Asks: Demographic and clinical characteristics per partition.

Not applicable: the study compares sets of images and records no person's age, sex, pathology or device; what it records of each group, its family, what one of its persons is and how many it holds, is in CLAIM 35 and REFORMS 3a.

Yours to decide: This is the one item no file can answer and no rerun will fill, because the study's design reads no demographic or clinical field. You choose one of three: accept the "Not applicable" sentence above; give the characteristics from the corpora's own papers in your words; or have them measured, which means the covariates census (tools/covariates.py, #66, not built) and a grid job on your word, and reading them in the study would be a departure for DEVIATIONS.md. What the record does hold, for your words if you write them: C-ArmLSpine 144 cases from lumbar intraoperative sessions on one mobile C-arm; DeepFluoro six cadaver specimens plus phantoms under 14 DICOM patient ids; Geneva one resin phantom; BUU-LSPINE 1,000 patients, whose file names carry sex and age that the study does not keep; KUB-StoneX patients of two hospitals; NHANES II films of 1976 to 1980; the render groups 26 TotalSegmentator v2.0.1 CTs.

## 8. implications (CLAIM 41)


Asks: Implications for practice, intended use and clinical role.

The study has no clinical role and supports no diagnostic use. It is a measurement that informs the FleXray audit's items 6 to 11. On the record, none of the seven synthetic sets whose family contrasts the summary prints is indistinguishable from real fluoroscopy or film in these feature spaces. Those seven include this project's renders of FleXray's recipe and FluXray's released FLUX-edited images, so none passes for real frames by this test. Because the replication read "not replicated", every comparison made through this project's render blocks is of this project's renders, not FleXray's (PREREG.md section 5). Separability alone does not predict that a network trained on such images fails on real frames. FleXray, trained with no real spine frame by its configs, named 99.14 percent of C-ArmLSpine's truth boxes when given the boxes.

Yours to decide: Only the owner can state the intended use and clinical role, including whether the study informs which synthetic data SchwingNet's training may lean on; the record says only that it informs the audit. The owner also decides whether to draw any practice implication from a study near its test's ceiling. Corrected: the earlier draft counted "FleXray's renders" among the sets measured against the real families. FleXray's own-code renders (flexray_reference) have those contrasts only in results.json, and the draft's own replication sentence makes the printed ones this project's renders.

## 9. availability (CLAIM 43)


Asks: Availability of software, model and data.

No model was trained, so none is released. The code and the study's records are in a private repository and are confidential; nothing of them goes public before the provisional patent is filed. The code is tools/domain_gap.py, tools/domain_gap_stats.py, tools/flexray_render.py, tools/render_blocks.py, and src/schwingnet/domain_gap.py, render_blocks.py and segmenters.py. results.json, the figures and the plan stay on Wayne State's grid; only BENCH.md and summary.txt left it. The real images and FluXray are third-party corpora under their own terms, several non-commercial or held by agreement: DeepFluoro and FluXray under CC BY-NC 4.0, BUU-LSPINE under its end-user agreement, AASCE by request form, and IEEE DataPort's set by subscription. They are not redistributed and are available from their publishers. The project's own synthetic sets and renders stay on the grid.

Yours to decide: The owner decides what will be released, when and under what terms (code, summary, figures), within the confidentiality rule. Corrected: the earlier draft said "confidential until" the filing, which implies a release after it; that is the owner's decision. It also said only summary.txt left the grid and that all the images are third-party.

## 10. funding (CLAIM 44)


Asks: Funding sources and role of funders.

No funding source for this study is recorded in the repository. Its computing ran on Wayne State University's research grid.

Yours to decide: The funding statement is the owner's alone: a funder and its role, or "This study received no specific funding." Do not write a placeholder into data/reporting/studies/drr-domain-gap.json. Any non-empty text there counts as the owner's declared answer, so the earlier draft's bracketed placeholder would have marked the item declared. The record names an AIDaS seed-grant proposal submitted on 2026-10-16 for the wider spine programme (docs/research/README.md line 142, spine-program grants/aidas_2027). It asks for 1 January to 31 December 2027 (docs/textbook/20-readiness-for-the-operating-room.md); no award is recorded and nothing links it to this study. docs/research/llc/PLAN.md notes that WSU grid use and possibly the AIDaS grant bear on rights in the invention, which also bears on what "other support" the owner states.

## 11. model_rationale (REFORMS 5b)


Asks: Why these model types.

The two two-sample classifiers are of different kinds: logistic regression after scaling and PCA to 64, a linear boundary, and 15 nearest neighbours after the same, a local non-parametric one. The unbiased MMD with a Gaussian kernel at the median distance gives a test with an exact person-level permutation null. FD64 and KID64 are the generative-model distances, taken at 64 components so every space is compared at one dimension with a stable covariance. PRDC (Naeem et al. 2020) separates fidelity from coverage. The first encoder is FleXray's flagship member flux0375, a network trained on CT renders of FleXray's recipe and on FluXray's edits. It is read at the input of its last instance norm, because the norm's output has one spatial mean for every image. The second is torchvision's ImageNet ResNet-18, the conventional FID-style space.

Yours to decide: No file of the study says why the classifiers are logistic regression and 15 nearest neighbours, or why the C2ST and the MMD rather than other tests, so the report cannot answer this item from the files and it came back to you. README section 1 gives reasons only for testing at all, for FD and KID in 64 components, for PRDC and for the three spaces, and the report's other items quote those. The owner confirms the rationale. That flux0375 was trained on 37.5 percent FluXray edits is read from the member names (flux000 is recorded as 0 percent enhanced), not from its config. The reason for pairing a linear and a local classifier, that a difference one misses the other can catch, is inferred; the record does not state it. Corrected: the earlier draft called flux0375 "the network trained on these DRRs". It was trained on its own renders of other CT sets and on FluXray, not on this study's renders.

## 12. external_validity (REFORMS 8a)


Asks: External validity.

The findings hold for these corpora, these renders and these readings: images decoded at 256 pixels after a centre crop, the feature spaces read, the 26 TotalSegmentator v2.0.1 CTs rendered under FleXray's pose profile or FluXray's fixed poses, and one spine fluoroscopy device. Each held corpus enters as a group of its own, so no external set is held back to test the claim on. Because the real corpora are themselves told apart almost perfectly, the study cannot say whether a synthetic set is closer to fluoroscopy in general than to these corpora.

Yours to decide: The owner decides how far the claim reaches. Corrected: the earlier draft said no set from another site was evaluated separately, which conflicts with the report's item 33. Every corpus, each from its own site, is a group of its own.

## 13. non_generalization (REFORMS 8b)


Asks: Where the findings will not hold.

The findings do not carry to:
- other renderers, recipes or realism edits;
- FleXray's own dataset (ENHANCE-PET CTs labelled by an unstated moosez version);
- other fluoroscopy devices, fields of view, or cine video (only a cine's middle frame is read);
- other resolutions or encoders.
They also say nothing of how a network trained on these images performs on real frames, since separability in feature space is not task failure. FleXray, trained with no real spine frame by its configs, named 99.14 percent of C-ArmLSpine's truth boxes when given the boxes. The replication verdict concerns one recipe on 26 CTs at one seed.

Yours to decide: The owner confirms the boundaries to state, and whether to cite FleXray's 99.14 before audit item 6's census settles whether it is zero-shot by file.
