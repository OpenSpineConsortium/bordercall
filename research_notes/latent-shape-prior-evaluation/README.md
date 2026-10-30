# Latent shape priors against explainable measurements: the evaluation plan

Thread "Plan evaluating latent shape priors against explainable metrics", 2026-10-30, project symphony_3, for greg's ask
of 2026-10-29 23:58 UTC: "please start planning for evaluating these approaches alongside purely human understandable
metrics as features", pasted with a conversation he had with another assistant that proposes a latent point-distribution
model (PDM) under the auto-anatomist, pure or hybrid; and for his words of 2026-10-30 02:33 and 02:39 UTC on where this leads
(section 14). Confidential with the rest of this repository: nothing here goes to a public place before the provisional
is filed, and the method is not shown.

This is a plan. Nothing in it ran: no training, no grid job, no data read. Every number quoted names the record it was
read from. The pasted conversation is thinking material; section 3 says where it is right and where it is wrong about
the code, and section 11 which of its citations are real. The code it speaks of is bordercall's autoanatomist package
(on main since pull request 27, extended by the blocks, the session, the calibration and the architecture block on
pull request 40, branch claude/project-thread-f0dity, commit 7d5fecb at the time of reading), the morphometry engine on
pull request 44 (claude/project-thread-e89pjg, ae22126) and SchwingNet's search design (pull request 483,
docs/checkpoints/2026-10-29-autoanatomist-flow/HANDOFF.md). Another thread, "Restart the auto-anatomist probe", is
working on those branches now; this plan touches none of them. Stage 1 needs one change on the engine's branch (the
export of the line ends) and, to ride in the morphometry jobs already counted, a re-vendor of bordercall under
SchwingNet's grid/bordercall/, each a pull request of its own; stages 2 and 3 need no change to PR 40 or PR 483; stage 4
needs the pieces section 10 lists. Three adversarial reviews of the first draft (2026-10-30 02:10 to 02:33 UTC) are
answered in this version; the pull request's body records what they found.

## 1. The question, and what the evaluation decides

Does a latent shape prior (a point-distribution model over the real masks' landmarks, pure or under the explainable
rules) measure, calibrate and name better than the rules as they stand, on real spines, and what does it cost in
explainability? The decision it informs: which head and which feature space the auto-anatomist carries into version 1,
and whether the Panjabi rule keeps reading named measurements or starts reading latent coefficients.

The plan crosses three axes, with the arms of section 4 chosen so that each pair gives one named contrast (the table
there says which); it is not a full factorial, since the pure latent arm has no form without its prior:

| axis | values |
| --- | --- |
| the head (how landmarks come out of the network) | heatmap and soft-argmax, as now; latent coefficients b through a linear map and a pose |
| the features (what the naming rule and the loss read) | named measurements (the Panjabi rule, as now); latent coefficients under a Gaussian |
| the feature set, within the named column | the seven chords the specs define; the wider pool the engine measures (32 and the size-free ratios) |

Figure fig1_design (figures/) draws the arms against what each is scored on; figure fig2_stages the stages with the
jobs each needs. Every count below is a proposal for greg's word; none is a request sent.

## 2. What stands today

Read from bordercall PR 40 (autoanatomist/README.md and records/autoanatomist-2026-10-29/smoke.json), PR 44
(research_notes/morphometry/README.md) and SchwingNet's docs/research/gold3-ct/README.md.

| what | as it stands | where read |
| --- | --- | --- |
| the network | two encoders fused F = (1 - w) F_ct + w F_mask, a decoder giving one heatmap per landmark at half the crop's resolution, the landmark its soft-argmax, its spread the heatmap's covariance; crop 48 x 56 x 32 voxels at 2 mm; 579,230 parameters; the architecture a block (residual-unet, plain-unet, probe) | autoanatomist/README.md, model.py |
| the values | nine measurements defined once in specs.py (seven chords used), each a smooth rule over its points: a length sqrt(max(d.d, 1e-12)), an angle by atan2, an area by the shoelace rule; the value's spread by the delta method var(v) = sum J S J' | specs.py, model.py |
| the prior in the loss | the naming layer: schwingcheck's exact Bayes rule over Panjabi's per-level means and SDs with a shared patient size and a per-measure offset, enumerated over every name path (chain.path_logev), four column types; nothing in the loss is an inequality bound | naming.py, train.py, schwingcheck/rule.py |
| the smoke run | 8 synthetic phantoms trained, 4 held out, 150 steps on 4 CPUs: held-out landmark distance 2.98 mm, value MAE 1.3 to 2.6 mm, the delta spread 25 mm uncalibrated (39 untrained), named right 0 of 12 with that spread, 5 of 12 from the values alone, 9 of 12 from the oracle's values; 38 ms a crop, no latency number under the 97 ms rule | smoke.json, README.md |
| the calibration | calibrate.py fits a factor per measure on validation (scale or quantile) so that the one-spread interval holds 0.68 of the validation errors; evaluate reports the calibrated spread, coverage at one and two spreads and the bodies named right three ways; no run has measured it | calibrate.py, train.py |
| the real masks | 1,733 gold tier 3 studies: ENHANCE.PET 1,558 (229 at 1.25 mm or finer, most at 3 mm; MOOSE's masks checked by students and residents), VerSe 21, TotalSegmentator 154; at most 1,654 persons; 68 whole ENHANCE.PET studies name an L6 (67 below an L5) and 39 set L4 on the sacrum | gold3-ct/README.md, holdings/gold-tier-3.md |
| the truth on real masks | the engine: 81 keys a vertebra in the vertebra's own frame, each measure also a line with two world ends (morphoview.lines); 228 thin-slice studies measured on 2026-10-29 in the older frame; the frame since turned onto the vertebra's own axis, so every study is to be measured again; rows.csv carries values, not the ends; the pinned copy on the grid (SchwingNet's grid/bordercall/) carries morphometry, scanimport and screening and no morphoview | PR 44 README, morphoview/lines.py, measure.py, SchwingNet grid/bordercall/VENDORED |
| the frames | training crops come from the oracle's frame (scanimport's column line through the neighbours' centroids), turned by up to 8 degrees and moved by up to 4 mm so the network cannot learn it; crops on a raw CT come from the mask-free mode (crops.from_found); the engine's frame is a third, the bisector of the end-plates, a median 16.7 degrees off the column line at C3 and 18.1 at L5; none of the three gaps is measured | crops.py perturbed, oracle.py, PR 44 README |
| the search flow | one plan JSON (blocks, seeds, rungs, the split's salt and shares), successive halving on the validation reward, a REINFORCE controller, the test part read once by the best trial; phantom rows only; the kept share strictly between 0 and 1; a trial with no landmark distance has no reward | SchwingNet HANDOFF.md section 4, src/schwingnet/autoanatomist_search.py |
| the fully latent objective | the thread "Restart the auto-anatomist probe" is building, on greg's word of 02:03 to 02:25 UTC on 2026-10-30, a block objective=mask: the decoder gives the privileged masks back from the fused features, no oracle and no measurement, with a per-vertebra name head on the bottleneck; its latent is the network's own, not a PDM | that thread's note to this one, 02:28 UTC |

## 3. What the pasted conversation gets right and wrong about the code

The transcript's diagnosis is right in its figures and wrong in its causes. Each row names the file the correction is read from.

| the transcript says | what is the case |
| --- | --- |
| the delta spread "exploded to 25 mm" because specs' rules are "hinge losses, ReLUs or strict bounded intervals" with "discontinuous or non-linear rules (arccos, tan)" | the spread fell from 39 mm untrained to 25 mm after 150 steps; it is the heatmap's covariance carried through smooth length rules (specs.py has no bound, no hinge, no arccos, no tan); a wide heatmap after a short run is the cause, and calibrate.py is the built answer not yet measured |
| the network "predicts raw coordinates directly", "the final dense layer outputs a flat matrix of raw coordinates" | the head is a convolutional decoder giving heatmaps read by the soft-argmax (integral regression), not a dense coordinate layer (model.py) |
| the Bayesian prior "relies on manually choosing which distances or angles to penalize", with "loopholes" where a ratio is missed | the prior is a generative model over named measurements, Panjabi's per-level mean and SD for each, a shared size and a per-measure offset (schwingcheck/rule.py); it penalises no bound; what it lacks is measures the table does not hold, which the wider pool (32) and the engine's keys supply |
| naming.py is "MCMC / Prior" and "Viterbi chains" | naming.py is exact enumeration over name paths, exact at any rho, plus a temperature forward pass that is the forward algorithm at gamma 1, Viterbi as gamma goes to 0, and exact only at rho 0; it samples nothing; PyMC lives in schwingcheck/chain_pymc.py |
| phantom.py uses "manual procedural generation rules" and "manual bone dimensions" | phantom.py sizes every level from one draw of schwingcheck's generator, Panjabi's means and SDs with the size law, the per-measure offset and the phenotypes; what is procedural is the shape primitive (an elliptic frustum, an elliptic canal, straight processes) |
| "2000 real masks", "2000 gold-tier human masks" | 1,733 gold tier 3 studies, at most 1,654 persons; the ENHANCE.PET masks were drawn by MOOSE and checked by people, a person's annotation by the owner's rule, not hand-drawn |
| "35 unit tests"; the oracle test "confirms sub-voxel edge gap placement (geometry.edge_gap)" | 70 tests now (35 before project.py); the oracle test holds each line end to the mask's boundary within 1.5 voxels and the values to measure_volume to the bit; edge_gap itself is tested in scanimport/tests/test_geometry.py, not by the oracle test, and no test calls its placement sub-voxel |
| "38 ms per crop ... real-time clinical workflows" | 38 ms is the jitted network alone on the container's 4 CPUs, random input, best of three; no device of the owner's, no ONNX parity, no p95, and the mask-free frame is not in it: no latency number under SchwingNet's rule |
| "each vertebral level possesses its own localized L-PDM sub-prior" (as a new thing) | the existing rule already holds a per-level, per-measure prior (Panjabi's table); a per-level PDM would add a prior over the points' joint configuration, which the measures' rule lacks, and duplicate the per-level means |
| "the mapping is linear so the Jacobian is constant" and the delta method stabilises | the map from b to landmarks would be linear; the rules from landmarks to values stay the same nonlinear functions, so J is constant only for the first factor; what changes is S, the covariance of b instead of each heatmap's, which is smaller by construction (K about 10 numbers in place of 3 per landmark) and is the thing to measure, not to assume |
| jax.linalg.svd | there is no jax.linalg; it is jax.numpy.linalg.svd or jax.scipy.linalg.svd |
| the citations (SpineNeuroSym, "Li et al.", "Zheng et al.", DeepSSM's Gaussian) | section 11: one invented, several real but misdescribed, one real and very new |

## 4. The arms

Every arm keeps the same crop, encoders, degradation ladder, schedule, calibration and naming layer; only the head and
what the rule reads change. The names are the block values the plan proposes (section 10). The PDM's Gaussian is
defined once (section 6): b whitened, so that ||b||^2 is its Mahalanobis distance, and a residual variance sigma^2 for
what the K modes leave out, as probabilistic PCA gives both; the prior term of every arm that has one is the PDM's full
negative log-likelihood (the in-subspace term plus the residual over sigma^2), at a fixed weight w_prior of 1, so that
it is a likelihood and not a tuned weight.

| arm | head: what the network predicts | prior in the loss | readout and the naming rule's features | lines drawn? | the contrast it gives |
| --- | --- | --- | --- | --- | --- |
| A rules (as now) | one heatmap per landmark; the soft-argmax | none beside the naming rule | specs' values from the landmarks; the rule reads the seven named measurements with the calibrated spread as each value's error, under the table re-estimated from the training persons (section 5); A-Panjabi, the same under the printed table, is reported beside it | yes, every value | the baseline, and A against A-Panjabi the table's own sample size |
| B latent | K coefficients b and a rigid pose T (three translations, three rotations, a log-scale); landmarks = T(mean + P b) from a per-vertebra PDM fit on the real masks' line ends | the PDM's negative log-likelihood of b | the naming rule's emission is a per-level Gaussian over the size-free b under the rule's own shared size (section 6); specs' values are computed from the reconstructed landmarks for the record only | only after reconstruction, and the loss never saw them | the transcript's pure latent proposal; B against C the feature space, with the head held |
| C hybrid | as B | the PDM's negative log-likelihood and the naming rule over the named measurements | specs' values from the reconstructed landmarks, as A | yes, every value | the transcript's recommended form; C against A changes the head and adds the prior at once, which D and C0 take apart |
| C0 latent, no prior | as B | the naming rule over the named measurements alone | as C | yes | the latent head by itself (Wang 2022's and Base-DeepSSM's form, section 11); C against C0 the prior on the latent head |
| D heatmap with the PDM penalty | as A | the naming rule and the PDM's negative log-likelihood of the heatmap landmarks (b_hat their projection, the residual what the projection leaves) | as A | yes | D against A the prior on the heatmap head; D against C the parameterisation |
| E values direct | the named values and their log-spreads, no landmarks | the naming rule over the named measurements | the rule reads the predicted values | no | what the landmarks and their lines cost or buy; the arm with human-named features and no geometry |

Two readings of greg's "purely human understandable metrics as features" are both kept: the column of arms A, C, C0, D
and E, whose rule reads named measurements, against B, whose rule reads coefficients; and, within the named column,
the feature set itself, seven chords against the wider pool (section 5), which is measured first with no network at all
(stage 2), on the engine's own measurements, since the question "do named measurements name as well as a latent" does
not need a network to be answered at the feature level. Stage 2 asks it twice: under the exact rule, whose answer
depends on the rule's model (the table, the size law, rho), and under a discriminative classifier over the same rows (a
multinomial regression over a body's keys and its neighbours', leave-persons-out), so that a latent's gain, if any, is
told apart from the rule's misfit.

A learnt latent (an encoder to a Gaussian code with a KL, the form VIB-DeepSSM found better than the fixed PCA basis,
section 11) is not an arm of version 1: version 1 tests the PCA form because it is the transcript's proposal and keeps
the readout linear, and a null for B does not close the learnt-latent question. The objective=mask the auto-anatomist
thread is building (section 2) is that learnt latent in all but the KL; its bottleneck vectors, written for the
validation studies, enter stage 2 as one more feature set, and a run of it as arm F is a second run (section 12).

## 5. The human-understandable features, concretely

- The seven chords the specs define and the rule reads today: EPWu, EPDu, EPWl, EPDl, VBHp, SCW, SCD
  (autoanatomist/specs.py SEVEN; schwingcheck's registry).
- The pool of 32 Panjabi measures the exact rule scores over C3 to L5 (schwingcheck/measures.py pool; the clinical
  reread's measures.md section 11 lists each with its mask recipe): the end-plate areas and inclinations, the canal
  area, the pedicles' width, height, area and two angles, the spinous length, the transverse width, the facets'
  widths, heights, areas, interfacet distances and angles.
- The engine's 81 keys a vertebra (PR 44): the above where the engine takes them, with the anterior and middle heights,
  the waist, Genant's ratios, the canal's least depth and area, the interpedicular distance, Eisenstein's lateral-film
  construction, the pedicle chord, the Torg and Jones indices, the laminae and the processes; 12 keys a disc.
- The size-free ratios measures.md section 11.9 names (anterior over posterior height, pedicle height over width,
  TPW over EPWu, SPL over EPDu, width over depth), which a 2-D view keeps without its magnification.

A feature set is "human understandable" here when every entry has a name, a unit, a definition in a paper and a line
that can be drawn on the mask (the engine's morphoview.lines draws every one of its measures). A latent coefficient
has none of these; section 7 says how much of each can be given back to it (the nameability of a mode).

How the features enter: the rule's table holds Panjabi's mean and SD for the 32, from twelve cadavers; a table from 12
people names 13.2 points fewer three-body fields exactly with the seven than the table as printed (TODO item P step
e), more than the bar section 12 proposes, so a latent emission fit on 1,100 persons would beat the printed table by
sample size alone. The reference named emission is therefore the table re-estimated from the training persons of the
same split (item P's data axis on gold 3, leave-persons-out, so no person is scored by a table that saw it), and the
printed table is a second, reported arm; a measure outside the printed table (a ratio, Genant's index) enters only
through the re-estimated table.

## 6. The point-distribution model

- The points: the two ends of every line the engine draws for a vertebra (morphoview.lines.vertebra_lines: the three
  heights, the wedge's two plate lines, the waist's two chords, Panjabi's four plate chords, the canal's least depth,
  Eisenstein's line at L1 to L4, the spinous length, the transverse span, the pedicles' width, height and chord each
  side, the interpedicular distance: 21 to 25 lines a vertebra by level, 150 over study 0004's six, 42 to 50 ends,
  some coincident, de-duplicated before the fit), or the minimal set, the 14 ends of the seven chords the specs define.
  Two sets, two PDMs, both measured. The ends are of two kinds: true landmarks (a plate's rim, a pedicle's isthmus)
  and ends defined by an extremum that slides along the bone between specimens (the waist's narrowest point, the
  canal's least depth, the ring the interpedicular width came from), which are semi-landmarks with no point
  correspondence; the minimal PDM holds true landmarks only, and the full one names which ends are which.
- The frame: the PDM is fit in the engine's frame, the vertebra's own (z the bisector of the end-plates' planes, y to
  the body, x to the right), on vertebrae whose frame settled on the bisector; where the engine fell back to the
  column's line and flagged it, the axis flag is missingness. The crop is not in that frame (section 2: the oracle's
  column line in training, jittered; the mask-free frame in use; the bisector a median 16.7 degrees off the column
  line at C3 and 18.1 at L5), so a latent head with no pose would have to absorb a rigid misalignment the PDM never
  modelled, a handicap the heatmap arms do not carry. Every latent head therefore predicts a pose T beside b (three
  translations, three rotations, a log-scale) and gives landmarks = T(mean + P b) in the crop's frame; the stated
  alternative, a PDM fit in the crop's frame with the training crops' own jitter, is kept for a second run. Stage 1
  measures all three frame gaps (engine to oracle, oracle to mask-free, engine to mask-free) before any network is
  judged in them.
- Size: divided out of the PDM and carried as the patient size s, the same shared size the rule integrates over the
  field's bodies by Gauss-Hermite (rule.py), so the latent emission has the rule's hierarchy (a size shared by the
  field, shape coefficients conditionally independent given s and the level) and not a flat per-body Gaussian; a
  second fit keeps size as a mode, to see what the first mode is. The per-measure offset (rho 0.5) has no counterpart
  in a Gaussian over b and the report says the comparison is hierarchical on size alone.
- Per vertebra, not per column: a column-wide vector over C3 to L5 has no slot for an L6, a T13 or a missing L5, which
  are the cases the owner keeps (section 2), and a crop shows one body with its neighbours' edges. The emission's
  alphabet is the chain's 24 names (schwingcheck's DRAW_LEVELS: C3 to L5, L6 and T13): one mean per name and one shared
  P in one fit, a P per name in another, both measured; L6's mean and covariance are fit from the 67 ENHANCE.PET L6
  labels below an L5; T13 has no label in ENHANCE.PET's scheme and VerSe's two T13 persons are in the anomaly holdout,
  so its Gaussian is built as chain.extended_table builds the table's row, half-way between T12 and L1, and never
  fit; C2's ends are exported and in the PDM's point fit, not in the emission, since the rule has no C2. Meng 2020's
  full-spine PPCA (section 11) is the published way to a column model and stays out of version 1.
- Missing ends (a pedicle not read at L5 or in the neck, a plate withheld, a level cut by the volume's edge, a frame
  flagged) are missing data to the fit (probabilistic PCA), never zeros.
- K: chosen on validation persons by the reconstruction error of held-out points and by the naming accuracy of the
  latent emission, reported as a curve, never fixed in advance; the transcript's "K = 10 captures over 98 per cent" is a
  guess to be measured. Bookstein's warning (section 11) that leading modes of a PCA over many landmarks and few
  specimens are partly noise is the reason K is chosen on held-out persons, the modes' stability across folds is
  reported, and the count of landmark coordinates (up to 150 a vertebra) is set against the training persons (about
  1,100) before any mode is read.
- Fit on training persons only; validation chooses K and the calibration; test persons are read once.

## 7. What is measured, and how each is read

Each quantity is one figure in the report (plots with short notes, the owner's rule); the table says which.

| quantity | definition | figure |
| --- | --- | --- |
| accuracy of the values | each predicted value against the engine's on the same vertebra, from the CT alone (w 0, lambda 1): mean absolute error, bias and 95 per cent limits of agreement, per measure, per level, per slice thickness and per site; the 95th percentile and the largest error beside the mean, since a shape prior trims the tail and can worsen the mean (Choi 2024, section 11) | Bland-Altman panels per measure; error by level |
| accuracy of the landmarks | the distance from each predicted end to the engine's, mean, median and 95th percentile, per end | distance by landmark |
| calibration of the spread | coverage of the calibrated interval at one and two spreads (nominal 0.68 and 0.95) per measure on the test persons; the raw spread before calibration, to say how much the calibration had to do; sharpness, the mean calibrated spread per measure, since the calibration makes every arm's one-spread coverage land near 0.68 on validation by construction and only the width tells a useful spread from a useless one; a reliability curve of coverage by spread quantile, which a spread that carries information makes monotone; the naming posterior's reliability (the share named right among bodies named at posterior p, against p) | coverage and width by measure; two reliability curves |
| naming | bodies named right, exact and within one level, on fields of 1, 3 and 5 consecutive bodies cut from every test column, three ways: from the predicted values with the calibrated spread, from the values alone, from the engine's values (the ceiling); with and without the anchors; per column class by the ribs (section 8), the anomaly strata read on every fold | named right by field length and arm; by class |
| E1 drawability | the share of reported values whose two ends lie within 1.5 voxels of the mask's boundary (the oracle test's rule) and, on the CT, within a stated distance of maskedge's bone edge | a bar per arm |
| E2 attributability | when the true name's posterior falls below 0.5, the per-measure (or per-mode) log-likelihood terms name what is responsible; the share of such failures where the named measure is the one the engine reads as off | a bar per arm |
| E3 nameability | the partial R^2 of each kept mode after the seven chords and after the 32 measures, with the smallest named set (at most three measures, by a sparse regression) that explains it at 0.8 or more, so a mode is nameable when a few named measures explain it and not when all 81 keys do; and the naming accuracy lost when b is replaced by its projection onto the named measures (stage 2 fits the rule on both); a plain R^2 of a mode on all the measures is close to circular, since modes and measures are functions of the same ends, and is not reported | partial R^2 by mode; named right with b against its projection |
| E4 transparency | the count of a prior's parameters that carry a name and a unit (Panjabi's per-level means and SDs do, eigenvectors do not) and whether an implausibility verdict can be read as a named violation ("canal depth 3 SD above L3's") | a table |
| latency | milliseconds a crop of the CT-only path, recorded as the smoke run records it; never rewarded, never called real time without ONNX parity and a p95 on a device of the owner's | one line in the table |
| training behaviour | the spread's trajectory and the loss terms by step; whether the latent arms reach a lower raw spread before calibration, which is the transcript's claim | spread by step |

What is scored and what is only reported: the primary endpoints are the value MAE averaged over the seven chords and
the bodies named right on three-body fields with the calibrated spread, both on the test persons. The calibration gate
is two-sided and pooled over the seven chords: coverage on the test persons within 0.60 to 0.76 at one spread and
0.90 to 0.98 at two, and sharpness, the mean calibrated spread no more than 1.2 times arm A's at the same coverage;
an arm outside either is read as miscalibrated or as uninformative whatever else it does. The explainability indices
and the latency are reported beside them, since they are the price, not the score. Whether a latent arm's gain is
worth its price is greg's call, which section 12 asks him to set as bars before the PREREG is frozen.

## 8. Data, splits and the analysis

- Data: the gold tier 3 CTs with their masks (ENHANCE.PET's CTs and labels are on the grid's data root since
  2026-10-29; VerSe's and TotalSegmentator's masks through the carries SchwingNet's morphometry word uses). Truth is the
  engine's reading of each mask in the new frame, with its line ends exported (stage 1). The thin-slice studies (229)
  are the first arm of every comparison; the thick ones (3 to 5 mm) are a stratum, since heights and discs move about a
  quarter of a slice there (PR 44 README).
- Splits by person, in the form of SchwingNet's data/splits/rule.json (a salted sha256 of the person id), with the
  shares set in the stage 4 plan file, as the search flow's split keys are (salt, validation_share, test_share):
  validation 0.1 and test 0.2 are the proposal, so of at most 1,654 persons about 165 are validation, 331 test and
  1,158 training. rule.json itself holds a validation share only, and its test list (test-persons.json) names five
  C-ArmLSpine fluoroscopy persons and no CT person, so without the plan file's share no gold 3 person is test; the
  anomaly-holdout persons (VerSe) are never trained on. A hash cannot stratify: the L6 and L4-on-sacrum strata fall
  in each part as the hash places them, the counts per part are reported, and if the test part holds fewer than 10
  columns of a stratum the pre-registered alternative is a listed test set drawn by the gold3-ct store's anomaly
  classes, in test-persons.json's form.
- Persons: every ENHANCE.PET study is its own person until the census's grid match (gold3-ct README section 7) assigns
  autoPET's; Leipzig and Careggi carry no person id at all. autoPET's 1,014 studies come from 865 to 900 persons, so
  some 80 to 114 are repeat studies that a hash by study could place on both sides of a split; the leak holds at all
  three sites and no arm of the data is clean of it. The match is a dependency of stage 1; until it lands, the leak's
  test is a near-duplicate check on the engine's own rows (two studies whose per-level measure vectors agree within
  measurement error are one person), and repeats found go to one part.
- The truth name on the anomaly columns, pre-registered by the ribs (holdings/gold-tier-3.md): the gold 3 census's rib
  classes are the truth and the masks' names the record. Of the 67 L6 columns 51 have twelve rib pairs and 14 have
  thirteen, the thirteenth on the label L1, which the chain names a T13 column and the scheme cannot; of the 39
  L4-on-sacrum columns 24 have twelve rib pairs (the sacralisation candidates, which the ribs cannot tell from a
  column one body short) and 8 have eleven, a class of their own. Naming is reported exact and within one level per
  rib class; T13 as a type is scored only on the holdout's VerSe persons, if at all, and no emission for it is fit from
  data (section 6).
- Fields for naming: every window of 1, 3 and 5 consecutive bodies of each test column, so a column of 22 bodies gives
  22, 20 and 18 fields; the share named right is over fields, its interval by a bootstrap over persons, since fields of
  one column are not independent, and a column's size estimate and type are shared by all its fields, so naming
  errors come in runs and the effective sample is nearer the test columns (about 330) than the fields (about 6,600).
- Pairing and the decision rule: every arm is read on the same test vertebrae, so the comparison of two arms is a paired
  difference per vertebra (or per field), its 95 per cent interval by the person bootstrap at fixed seeds; three seeds
  an arm, the seed-to-seed spread reported and required to be smaller than the bar, the arms compared on the seed means.
  One primary contrast, C against A on three-body fields with the calibrated spread; B against A decides the features,
  D against A and C against C0 the prior, C0 against A the head; the rest are secondary, and a bar is met when the
  lower bound of the paired difference's interval exceeds it.
- Power, from the counts alone: a test fifth is about 331 persons and about 7,000 vertebrae. For the value endpoint a
  paired MAE difference of 0.3 mm against a paired SD of about 2 mm a vertebra needs about 350 vertebrae at 80 per cent
  power, about 1,750 after a design effect of 5 for clustering within a person, so the typical stratum is never the
  limit. For the naming endpoint the column is the cluster: with about 330 columns and the two arms discordant on 15
  per cent of fields, the standard error of a paired difference is near 2 points, so the 3-point bar section 12
  proposes sits near 1.5 standard errors and is underpowered as it stands; the within-column correlation is measured in
  stage 2 from the engine's rows, and the bar or the test share (0.3 would give about 500 columns) is set from it before
  the PREREG is frozen. The anomaly strata are small (about 14 L6 and 8 L4-on-sacrum columns in a fifth), so they are
  cross-fitted at stage 2 and reported with Wilson intervals at stage 4, not tested.
- Nothing from CTSpinoPelvic1K (dropped for good), nothing from the morphometry phantoms (deferred); the
  autoanatomist phantoms serve stage 3 only, as a smoke test of the code path.

## 9. The stages and the jobs

In order, each with what it decides and the jobs it would ask for; the count is a proposal for greg's word, and a
later stage waits for the one before it. No job is sent by this plan.

| stage | what runs | where | jobs proposed | depends on | what it decides |
| --- | --- | --- | --- | --- | --- |
| 1 export | the engine over every gold 3 mask in the new frame, with each measure's two line ends and the vertebra's frame written beside the value (a `--lines` output of `python -m morphometry run`, to add on the engine's branch) and, on the CTs, the mask-free frame (crops.from_found) and the oracle's beside the engine's; aggregates in the report, rows on the grid | grid, CPU | 0 only if the `--lines` output and morphoview reach the pinned copy under SchwingNet's grid/bordercall/ (tools/bordercall_vendor.py copy, VENDORED) before `morphometry enhance` and `morphometry verse`, the two jobs the owner counted on 2026-10-29 15:19 UTC, are sent; else 1, or a re-run that needs a new count | the export flag on PR 44's branch; the re-vendor; the morphometry re-run in the new frame; the CTs landed; the autoPET person match | the truth table and the PDM's points exist; the three frame gaps are numbers |
| 2 features, no network | on the engine's rows: the exact rule with the seven chords, with the 32-measure pool, with the pool and the ratios, with a per-level Gaussian over b (the two PDMs, K on a curve), and with b beside the seven, under the re-estimated table and the printed one; a discriminative classifier over the same feature sets; leave-persons-out, five folds; naming by field length and rib class; the within-column correlation for the power of section 8; E3 nameability | grid, CPU; or a container, only if the exported ends and values (no image, no mask) are carried off the grid as a per-study table, a choice for greg, since the rows stay on the grid under SchwingNet's morphometry rule | 1 | stage 1 | whether named measurements name as well as a latent at the feature level; how many named measures the latent is worth; K; the naming bar's power; whether arm B is worth training at all |
| 3 smoke of the heads | the six arms on the existing autoanatomist phantoms, a few hundred steps each, the code path from the oracle to the named bodies for every head; the GPU step time measured, which the cost below needs | grid, CPU, batch class, on the launched autoanatomist flow | 0 if the heads join the phantom_smoke plan the auto-anatomist thread is writing (one value more of one block); else 1, as a second plan `heads_smoke` of the same flow, its bytes added to that PREREG's Covers line | the head block built (section 10); probe_smoke first, as the owner asked | the arms run end to end; nothing is read as a result |
| 4 real spines | a fixed design on the launched flow, not the search's halving: the six arms times three seeds, eighteen trials, every trial trained for the same nine passes over the training vertebrae, every other block fixed at the smoke run's, w_prior 1; calibration on validation; the test persons read once for every finished trial | grid, GPU, the launched flow under this evaluation's own frozen PREREG (section 10) | 2 (one array of the eighteen trials, one for the calibration and the test read); the minimal form, A against C alone with two seeds, is 1 | stages 1 to 3; the flow's fixed mode and volume rows landed (section 10); the PREREG frozen | the primary endpoints per arm with intervals; the calibration gate; the explainability indices |
| 5 report | the figures of section 7 and the CLAIM report, from the run folders; the paired differences and the bootstrap | the flow's end step, or a container from the records | 0 | stage 4 | greg's decision on the head and the features, against the bars he set |

The search flow as PR 483 designs it retires half the trials at each rung on the validation reward and reads the test
part for the best trial only, so it gives one arm's test numbers and no paired comparison; its reward is also a
function of landmark distance, which arm E has none of. Stage 4 therefore needs a fixed mode of that flow (every trial
to the end, the test part read for every trial, a trial with no landmarks ranked on its values), listed in section 10
as an ask of PR 483's thread; the search's halving and controller are for a later sweep of w_prior and K, with the
anomaly strata in its objective, since a weight chosen on a validation part that is 96 per cent typical anatomy would
pick the value that hurts the strata.

The cost, with its basis; the GPU step time is the smoke's to measure at stage 3 before any hours are claimed:

| stage | unit of work | count | basis record |
| --- | --- | --- | --- |
| 1 | the engine over 1,733 masks | the whole set is the 32-CPU, 24-hour job SchwingNet's grid/morphometry.sbatch already is; the 229 thin studies took one morning in a container | PR 44 README; the morphometry memory |
| 2 | the rule and the classifier over the rows, five folds | minutes once the rows exist | item P's data axis timings |
| 3 | six arms, a few hundred steps each, on 4 CPUs | the smoke's 150 steps on 6 crops a step took 313 s, 2 s a step | smoke.json |
| 4 | one pass over about 30,000 training vertebrae at a batch of 8 | about 3,750 steps; nine passes about 34,000 steps a trial; eighteen trials about 600,000 steps; at a fifth of the smoke's step time about two hours a trial on one GPU, so an array of eighteen is a few hours and one GPU in series about a day and a half | the smoke's step time; the pass count is the plan's |

The total ask, in the owner's units: 1 to 2 CPU jobs (stages 1 and 2) and 1 to 2 GPU jobs (stage 4), with stage 3
folded into a plan another thread is already writing or one CPU job more. Every one waits for his word and count, and
the size rule applies to nothing here, since no fetch is made.

## 10. How it fits the swappable-block design and the search flow

- The network is already a block (blocks.py's `architecture`, model.ARCHITECTURES). The head is the second spot the
  model offers: a block `head` with the values heatmap (as now), latent (arm B), hybrid (C), latent-noprior (C0),
  heatmap-pdm (D) and values (E), with `pdm` naming the fitted model's file by its digest, which needs one new kind in
  blocks.py's table (a digest string, spelled as given; its kinds today are choice, switch, int, float, pair and
  triple), `pdm_k` the coefficients kept, `w_prior` the prior term's weight (1 in version 1, 0 for C0) and `emission`
  choosing what the naming layer reads, measures or latent. None of the five keys is in the table today, and
  autoanatomist/pdm.py is a free name. The latent head is a dense layer from the fused features' pooled eighth scale
  to K + 7 numbers (b and the pose); the hybrid differs from it only in the loss and the emission; arm E's head gives
  2 x 7 numbers. Each head returns landmarks, values and a spread in the same shapes, so the loss terms, the
  calibration, the naming layer, the session and the search run over any of them unchanged, as the probe does today.
  No block named is still the smoke run to the bit.
- The PDM is an asset built by one command from the exported ends (a module `autoanatomist/pdm.py`: fit, project,
  reconstruct, the negative log-likelihood, with tests holding the round trip to 1e-6 and the gradient of the
  reconstruction to a finite difference), kept with its digest so a run names the model it used; it is never fit
  inside training.
- The naming layer takes a second emission: a per-level Gaussian over the size-free b whose means and covariances the
  same asset holds, under the rule's shared size (section 6), so `posteriors` and `body_loss` run on either feature
  space; the exact enumeration is unchanged.
- The data: the search module takes phantom rows only, and the autoanatomist's examples are rendered phantoms read by
  the stand-in oracle; a real-CT source exists in neither branch. Stage 4 needs a volume row kind in SchwingNet's
  autoanatomist_search.py and an examples loader in the autoanatomist that cuts crops from a landed CT and its mask
  with the exported ends as targets, and the flow's fixed mode (section 9).
- The plan file for stage 4 is one JSON under SchwingNet's grid/searches/, the folder the HANDOFF plans, in the layout
  of its section 4, with the six heads as the block space, w_prior fixed, the split's salt and shares, and the data
  source the gold 3 volume rows. The PREREG the auto-anatomist thread is writing (docs/research/autoanatomist-search/,
  not yet there) asks which blocks give the lowest validation landmark error on phantoms, with no bars, and once
  frozen may never change, so this evaluation's question, endpoints, gate, strata and bars cannot enter it. Stage 4
  therefore runs as a flow kind of its own: a line in SchwingNet's flows/registry.txt and a PREREG under SchwingNet's
  docs/research/latent-shape-prior-evaluation/, to be written and frozen before the first job, with the plan file's
  bytes in its Covers line; a departure is a dated line in its DEVIATIONS.md.
- Order of landing: the export flag on the engine's branch (PR 44's thread) and the re-vendor of bordercall under
  SchwingNet's grid/bordercall/; the head block, pdm.py and the examples loader on the auto-anatomist's branch after
  PR 40 merges (or on a branch of this thread's own from it, once that thread's work is in); the volume row kind and the
  fixed mode in SchwingNet's search module after PR 483 merges; the plan file, the registry line and the PREREG in
  SchwingNet with the flow. Stages 2 and 3 ask nothing of PR 40 or PR 483 as they stand; stage 1 asks the export flag of
  PR 44's thread; stage 4 asks the pieces above of whoever lands them.

## 11. Prior art, as verified

Every citation of the transcript was looked up on 2026-10-30 (four searches, each entry resolved to its record or
declared not found; the full entries are in this folder's prior-art.md, whose four status words the verdict column
uses). The two verdicts that change the plan: the transcript's named precedent for differentiable clinical readouts
does not exist, and the one published trial of a learned latent shape constraint as a loss on spine landmarks found a
small gain.

| the transcript's citation | status | what it is |
| --- | --- | --- |
| Glocker et al. 2012, regression forests and an HMM | real but misdescribed | MICCAI 2012: forests regress 26 centroids, a hidden Markov model over sampled candidates with a Gaussian on adjacent offsets scaled by one global size, solved by dynamic programming; median 5.3 mm, 81 per cent identified within 20 mm on 200 CTs; no shape manifold, no L6 or T13. The 2013 follow-up (dense classification, no prior) shows the parametric prior helping on normal spines and hurting on pathological ones (51 against 70 per cent) |
| "Zheng et al." as a co-pioneer | uncertain | the forest-plus-HMM design is Glocker's; Chu et al. 2015 (PLOS ONE, Zheng senior author) adopts it at fixed lumbar levels; Kelm et al. 2013 (Zheng a middle author) is marginal space learning with a column prior |
| Hanaoka et al. 2017, numerical anomalies by competing hypotheses | real | IJCARS 12(5):719-732: five count hypotheses (normal, 11 or 13 thoracic, 4 or 6 lumbar) over a landmark point-distribution model, the most plausible by posterior, 300 neck-to-pelvis CTs; the L-PDM framework itself is Hanaoka et al., Medical Image Analysis 35 (2017), 197 landmarks, 70 per cent vertebra identification |
| "Anatomical Prior-Based Vertebral Landmark Detection", "Li et al.", 2024 | real but misdescribed (misattributed) | Yang et al., Artificial Intelligence in Medicine 159:103011 (online November 2024): distance and order priors as a loss, a sequential inference and plausibility metrics, on 1,410 AP radiographs; the margin formulas are the transcript's reconstruction, not confirmed from the text |
| "A vertebral level-wise data augmentation scheme" from VerSe | real but misdescribed | Wu et al., SPIE Medical Imaging 2021: articulated augmentation from one spine for PointNet++ segmentation; no VerSe connection, no landmark error |
| spatial variance regularisation of soft-argmax heatmaps | real but misdescribed | Nibali et al. 2018 pull the heatmap's variance toward a target, not to zero, and their own table shows it hurting; no MICCAI paper using it was found |
| "SpineSAM / Pix2Point", Daridon et al. | real (very new) | Daridon, Sifaoui et al., arXiv:2610.36951, submitted 27 October 2026: a contrastive pixel-embedding heatmap stage and a PCA Gaussian shape model over normalised landmarks read as a Mahalanobis term at inference, on AP and dual-view radiographs; its own ablation lowers landmark error while a plain heatmap method still ranks better on the clinical parameters |
| Sekuboyina's "adversarial latent shape constraints" with a contractive autoencoder | real but misdescribed (two works fused) | Btrfly Net (MICCAI 2018, Radiology AI 2020) is an adversarial energy prior on label heatmaps during training; the contractive autoencoder with a latent distance loss is Kordon, Maier and Kunze, BVM 2021, on SpineWeb16, with small improvements |
| "SpineNeuroSym" with a "differentiable radiographic geometry module" | not found | invented; the nearest real work computes clinical parameters after detection, and the design described is closest to the auto-anatomist's own specs.py values with the delta method |
| DeepSSM "forcing outputs to live within the Gaussian" | real but misdescribed | Bhalodia et al. 2018 and 2024: a fixed PCA decoder with a loss on loadings (2018) then on points (2024, the loadings loss found worse); no Mahalanobis term; the Gaussian latent penalty is VIB-DeepSSM (Adams and Elhabian 2022, a KL on a learnt latent), which beat the fixed PCA form on points error; no spine application |
| Bayat et al. 2022, "a statistical shape model by region" | real but misdescribed | Tomography 8(1): an atlas deformed by an affine and a free-form field from two radiographs; no PCA, no coefficients |
| Lessmann et al. 2019; Chu et al. 2015; Sekuboyina's TUM dissertation | real | iterative FCN labelling by maximum likelihood over consecutive labels (no prior); forests with an HMM at fixed levels; the 2024 dissertation of the Btrfly line |

Found beside them, each more use to the plan than most of the above:

| work | what it is | what it sets in the plan |
| --- | --- | --- |
| Wang et al. 2022 (Fundamental Research 4(6), arXiv:2206.02087) | a cascaded CNN regressing PCA coefficients with a linear map back to vertebral landmarks on AP radiographs, no penalty on the coefficients | arm C0, the latent head with no prior, as the latent baseline |
| Choi and Jang 2024 (J Imaging Informatics in Medicine 38(1)) | a heatmap-plus-PDM fit on 3,600 lateral lumbar radiographs where the prior trimmed the worst error and slightly worsened the mean | the tail of the error reported beside its mean |
| Kordon, Maier and Kunze, BVM 2021 | the one trial of a learnt latent shape constraint as a loss on spine landmarks, small gains | a null outcome for the latent arms pre-registered as plausible |
| Meng et al. 2020 (ShapeMI) | a full-spine PPCA from partial VerSe scans with no slot for an L6 | the per-vertebra PDM and the strata read apart; missing ends as PPCA missing data |
| Frysz et al.; Roberts et al.; Paul et al. | hip shape modes against named angles in one regression; a latent against two or three angles in one classifier | the adjustment form of E3 (partial R^2) and the discriminative arm of stage 2 |
| Bookstein 2017 | the noise in leading modes when landmark coordinates outnumber specimens | K on held-out persons, fold stability, the coordinate count against the persons |
| Yang et al. 2024 | plausibility metrics (inter-level distance, monotone order) beside the landmark error, in 2-D | not in version 1: the naming layer's posterior and the engine's own flags are the plan's plausibility reading in 3-D; a 3-D counterpart of Yang's metrics is kept for a second run |
| Ansart et al. 2022 (prior-art.md) | an L2 on PCA coefficients is PPCA's regulariser, a clip its hard form | the prior term is the PPCA negative log-likelihood, not a bare L2; the clip is out |
| VIB-DeepSSM (Adams and Elhabian 2022) | a learnt latent with a KL beat the fixed PCA basis on points error | the learnt latent is not an arm of version 1 (section 4, with the reason); arm F in a second run |

## 12. Risks, and what greg is asked

Risks the design answers, and how:

- A fixed-slot shape model has no L6, T13 or missing L5: the PDM is per vertebra, the emission's alphabet is the
  chain's 24 names, and the strata are read apart by rib class.
- The prior and the rule double-count: the PDM's term and the naming term both pull toward typical anatomy; w_prior is
  fixed at 1 (a likelihood, not a weight), C0 has none, and D against A tells the prior's own effect on the heatmap head.
  The latent arms are expected to lose on the anomaly strata, as every fixed-slot prior so far has (Glocker 2013), and
  the strata are reported first.
- Size in the PDM: divided out and carried as the rule's shared s, so the latent emission has the rule's hierarchy;
  kept as a mode in a second fit.
- The frames: three gaps measured in stage 1 before any network is judged in them; the latent heads carry a pose, so a
  rigid misalignment is not read as shape.
- The engine's own biases (end-plate widths read wide against the papers, cervical pedicles not right, L5's pedicle
  fused with the process) are the truth's biases: every arm learns them alike, the report says so, and the pedicle ends
  the engine flags are missing data to the PDM and to the loss.
- Leakage by person: every ENHANCE.PET study is its own person until the census's match assigns autoPET's, and
  Leipzig and Careggi have no person id; the match is a dependency of stage 1 and the near-duplicate check on the
  engine's rows is the leak's test until then (section 8).
- MOOSE's masks checked by people are the annotation; nothing here raises a tier, and the maskedge offset (+0.14 to
  +0.20 mm on the phantom) is what a network trained on masks learns.
- The latent arms may win on landmark distance and lose on the named values or the naming, as Daridon's and Choi's
  ablations did: the endpoints are the values and the naming, not the landmarks.
- The calibration cannot fail its own gate on validation, so the gate is read on test and carries a sharpness bound
  (section 7).

What greg is asked, once, so the PREREG can be frozen:

1. The count and class per stage (section 9): 1 or 2 CPU jobs for stages 1 and 2, 1 or 2 GPU jobs for stage 4, stage 3
   folded into the phantom_smoke plan or one more CPU job.
2. The bars, two decisions apart: for the features (B against A), what gain in the two primary endpoints a latent
   emission must show to displace the named measurements as the rule's features; for the head (C against A, with C0 and
   D telling why), what gain a latent head must show to replace the heatmaps. The proposal to accept or change: at least
   0.3 mm of value MAE over the seven chords, and on three-body fields a naming gain whose points are set from stage
   2's within-column correlation (3 points is underpowered at a test fifth, section 8), each with the lower bound of its
   interval above the bar and the seed spread below it; the calibration gate of section 7 met; and, for the features
   decision alone, every kept mode nameable by at most three measures at a partial R^2 of 0.8. Short of any one, the
   named features and the heatmaps stand.
3. Whether stage 2 may run in a container, which means the exported ends and values (no image, no mask) leaving the
   grid as a per-study table, or stays on the grid as one CPU job.
4. Whether the wider pool (32 measures and the ratios) is the reference named feature set, or the seven chords alone
   until the extractors deliver the rest with their points.
5. Whether arms C0, D and E are in the first run or kept for a second, and whether arm F (the learnt latent, the
   auto-anatomist thread's objective=mask) joins a second run.
6. Whether stage 4 runs as a flow kind of its own, with its registry line and PREREG under SchwingNet's
   docs/research/latent-shape-prior-evaluation/ as section 10 proposes, this note staying here.
7. The test share, 0.2 as proposed or 0.3 for the naming bar's power, and whether a listed test set drawn by anomaly
   class replaces the hash's draw where a stratum falls below 10 test columns.

## 13. What this plan does not do

No training, no job, no data read, no change to PR 40, PR 44 or PR 483. The 2-D transfer (FluXray synthetics, the
view=2d block) is designed in SchwingNet's handoff and is not evaluated here; once the 3-D answer is in, the same
arms project through project.py and the same figures are drawn on the detector. The morphometry phantoms stay
deferred; the CTSpinoPelvic1K cross-check stays dropped. A column-wide model (Meng 2020), a learnt latent with a KL
and the search's sweep of w_prior and K are second runs, not this one.

## 14. Where this leads: 2-D landmarks that identify the vertebra bearing them

greg, 2026-10-30 02:33 and 02:39 UTC: "i think eventually something id like to try would be placing landmarks on a 2d
xray which can be operated on in 2d space with functions to estimate 3d properties, which should reach into a higher
dimensional space and let you classify the seemingly flattened flat xrays according to higher dimensional
properties"; "essentially i want you to find landmarks which exist in 2d which when operated on with other nearby
landmarks uniquely identify the vertebra bearing them".

So the question is identifiability: which landmarks a radiograph shows, and which functions of a landmark with its
neighbours (on the same vertebra and on the adjacent ones), name the level, alone or in a small set, and how much of
that naming comes through a 3-D property the function estimates. It is the feature-level question of stage 2 carried
to the 2-D view, and the gold tier 3 set answers it with no new data: each CT gives the engine's ends in world
coordinates (stage 1's export), project.py gives their 2-D positions under a stated camera, and the level is known,
so every candidate function can be scored on paired examples before a single radiograph is read. The pieces this plan
lays down for it:

- The landmarks: the ends of the engine's lines as the view keeps them (a plate's rim, the pedicle's isthmus, the
  spinous tip, the canal's walls where the view shows them), each with its name, so a landmark found to identify is a
  landmark a person can point to.
- The functions: for each landmark, every function of it with its nearby landmarks that survives projection: the
  distances and the size-free ratios of section 5, the angles between chords, the relation to the neighbours above
  and below (the disc's height, the plates' convergence, the pedicle-to-pedicle step), and the 3-D estimates a
  function gives back (depth from a width and a known ratio, the pedicle's angle from its foreshortening). Each
  function carries the name of its inputs, so the set stays human-understandable in greg's sense.
- The search: a forward selection over the functions, scored by the share of vertebrae named right under the exact
  rule (the re-estimated table over the chosen functions) and under the discriminative classifier of stage 2, with the
  level as the class and leave-persons-out; the gain of each function read as named right with it against without it,
  and the per-landmark identifiability as the best gain any function of that landmark gives. The output is a ranked
  list of landmarks and functions, not a network.
- The 3-D reach: a function's value is set beside the 3-D key it estimates (the engine's truth on the same vertebra),
  so the report says whether a function names the level because it recovers a 3-D property (the canal's depth, the
  pedicle's angle, the PDM's b) or because the 2-D quantity itself varies by level; the latent coefficients b, fit in
  3-D, enter the same search as a candidate feature set, which is the plan's own question asked of the view.
- The anomaly classes: the rib-class truth of section 8 gives L6, L4-on-sacrum and T13 columns in the 2-D set too, so
  identifiability is reported per class, and a landmark that names typical levels and fails on the strata is said so.

What it needs that this plan does not provide: project.py's camera model and the view=2d block landed (SchwingNet's
handoff), FluXray's realism for the synthetic to real step (docs/research/flux-realism), and a 2-D truth of its own on
real radiographs (C-ArmLSpine's, the film corpora) to say whether what the paired CTs teach holds on a real
radiograph with a real detector and a real pose. It is written here so the stage 1 export keeps what it will need:
every end in world coordinates with its vertebra's frame and its name, so that any camera can project it later and
every function keeps its inputs' names.
