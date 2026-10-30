# Latent shape priors against explainable measurements: the evaluation plan

Thread "Plan evaluating latent shape priors against explainable metrics", 2026-10-30, project symphony_3, for greg's ask
of 2026-10-29 23:58 UTC: "please start planning for evaluating these approaches alongside purely human understandable
metrics as features", pasted with a conversation he had with another assistant that proposes a latent point-distribution
model (PDM) under the auto-anatomist, pure or hybrid; for his words of 2026-10-30 02:33 to 02:41 UTC on where this leads
(section 14), and for his rule of 02:46 UTC on how it runs: "whatever you do just make sure it fits into the block
style metaflow pipeline and then you can just evaluate as many in parallel as possible on short 50 epoch runs that will
give you some idea of the feasability of each or at least evaluate the performance"; and at 02:49 UTC: "yes just
please build them up encapsulated and swappable, like i dont want two networks for the seven and 32 measure pool, make
sure it just accepts pymc code like natively, and adapts to what is provided, the same for others it should be seemless
like a fighter jet and maintain this swappable configurable easy switching". Confidential with the rest of this repository: nothing here goes to a public place before the provisional
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
SchwingNet's grid/bordercall/, each a pull request of its own; stage 2 needs no change to PR 40 or PR 483; stage 3 asks PR 483's plan for the
head block only in its no-job form; stages 4 and 5 need the pieces section 10 lists. Three adversarial reviews of the first draft (2026-10-30 02:10 to 02:33 UTC) are
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
jobs each needs. How it runs is greg's rule: every arm a block of the auto-anatomist, every run a plan of the launched
Metaflow flow, and the arms screened side by side in parallel short runs of 50 epochs before any long one. Every count
below is a proposal for greg's word; none is a request sent.

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
| the real masks | 1,738 gold tier 3 studies: ENHANCE.PET 1,558 (229 at 1.25 mm or finer, most at 3 mm; MOOSE's masks checked by students and residents), VerSe 21, TotalSegmentator 159; at most 1,659 persons, 1,620 units once probable repeat scans are joined (section 8); 68 whole ENHANCE.PET studies name an L6 (67 below an L5) and 39 set L4 on the sacrum | gold3-ct/README.md, holdings/gold-tier-3.md, PR 44 README (the 229) |
| the truth on real masks | the engine: 81 keys a vertebra in the vertebra's own frame, each measure also a line with two world ends (morphoview.lines); 228 thin-slice studies measured on 2026-10-29 in the older frame; the frame since turned onto the vertebra's own axis, so every study is to be measured again; rows.csv carries values, not the ends; the pinned copy on the grid (SchwingNet's grid/bordercall/) carries morphometry, scanimport and screening and no morphoview | PR 44 README, morphoview/lines.py, measure.py, SchwingNet grid/bordercall/VENDORED |
| the frames | training crops come from the oracle's frame (scanimport's column line through the neighbours' centroids), turned by up to 8 degrees and moved by up to 4 mm so the network cannot learn it; crops on a raw CT come from the mask-free mode (crops.from_found); the engine's frame is a third, the bisector of the end-plates, which over the 228 thin-slice studies lies a median 16.7 degrees off the column line at C3 and 18.1 at L5 (the run's axis_offset key; on study 0004 alone 21.7 and 16.7); none of the three gaps between the frames is measured | crops.py perturbed, oracle.py, PR 44 README (the axis section) |
| the search flow | designed in PR 483's handoff and its module: one plan JSON (search, class, rows, split, space, fixed, seeds, rungs, keep, trials, controller, objective, latency_crops, wandb_project, every key required), successive halving on the validation reward, a REINFORCE controller, the test part read once by the best trial, a row's person its id; phantom rows only; the kept share strictly between 0 and 1; a trial with no landmark distance has no reward; the flow file flows/autoanatomist.py, its registry line and its PREREG are not on the branch yet (d8cadc3 at the time of reading) | SchwingNet HANDOFF.md section 4, src/schwingnet/autoanatomist_search.py, flows/registry.txt |
| a GPU job and its trials | a gpu-class job gets one card and a launched flow's foreach runs its tasks inside that job, one after another at --max-workers 1 or sharing the card above it; trials each on a card of their own are the DRR study's form, a Slurm array whose every task starts a launcher run of its own, and a merge job afterany the array, itself a launcher run | SchwingNet flows/README.md (drr_gap), grid/drr-gap.sbatch, grid/sweep-driver.sbatch on PR 483 |
| the auto-anatomist's rows | rows.py already reads a CT and its label NIfTI as a volume row through the oracle interface (kind, id, ct, labels, scheme or names, seed), crops and jitters every vertebra the oracle read and caches the row by its digest; with the naming term on, every example of a batch must hold the same number of crops, and a volume row is one whole column | PR 40 rows.py, session.py, train.py |
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
| "2000 real masks", "2000 gold-tier human masks" | 1,738 gold tier 3 studies, at most 1,659 persons; the ENHANCE.PET masks were drawn by MOOSE and checked by people, a person's annotation by the owner's rule, not hand-drawn |
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
  side, the interpedicular distance: counted by reading vertebra_lines' ten builders, about 22 lines a vertebra where
  Eisenstein's line is drawn and fewer where a builder withholds, with the discs' lines beside them, 150 lines over
  study 0004's six vertebrae and their discs in PR 44's README; the count per level is stage 1's export to record;
  two ends a line, some coincident, de-duplicated before the fit), or the minimal set, the 14 ends of the seven chords the specs define.
  Two sets, two PDMs, both measured. The ends are of two kinds: true landmarks (a plate's rim, a pedicle's isthmus)
  and ends defined by an extremum that slides along the bone between specimens (the waist's narrowest point, the
  canal's least depth, the ring the interpedicular width came from), which are semi-landmarks with no point
  correspondence; the minimal PDM holds true landmarks only, and the full one names which ends are which.
- The frame: the PDM is fit in the engine's frame, the vertebra's own (z the bisector of the end-plates' planes, y to
  the body, x to the right), on vertebrae whose frame settled on the bisector; where the engine fell back to the
  column's line and flagged it, the axis flag is missingness. The crop is not in that frame (section 2: the oracle's
  column line in training, jittered; the mask-free frame in use; the bisector a median 16.7 degrees off the column
  line at C3 and 18.1 at L5 over the 228 thin-slice studies, 21.7 and 16.7 on study 0004), so a latent head with no pose would have to absorb a rigid misalignment the PDM never
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
  P in one fit, a P per name in another, both measured; in the first run, which sees normal spines alone (section 8),
  L6 is built as T13 is below and never fit; in the full run L6 takes a mean of its own fit from the six lumbar columns
  of the anomaly train part (38 at 0.2, TotalSegmentator's two by names left out, Bookstein's case, so its covariance
  is the pooled one of the shared-P fit);
  T13 has no label in ENHANCE.PET's scheme and of VerSe's four T13 persons one is in the anomaly holdout and one in doubt (section 8),
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
- Fit on training persons only, all of them, in the screen as in the full run, while the screen's network trains on a
  fifth of them (the same PDM and the same re-estimated table for every arm); validation chooses K and the
  calibration; test persons are read once, by the full run.

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
| E4 transparency | the count of a prior's parameters that carry a name and a unit (Panjabi's per-level means and SDs do, eigenvectors do not) and whether an implausibility verdict can be read as a named violation ("canal depth 3 SD above L3's") | a bar per arm, named parameters over all, with latency as a point on the same panel's right axis: the two counts with no axis of their own |
| latency | milliseconds a crop of the CT-only path, recorded as the smoke run records it; never rewarded, never called real time without ONNX parity and a p95 on a device of the owner's | the point on E4's panel |
| training behaviour | the spread's trajectory and the loss terms by step; whether the latent arms reach a lower raw spread before calibration, which is the transcript's claim | spread by step |
| literature bounds, an outside check | bordercall PR 38's bounds card (research_notes/synthetic-validation/synthval/bounds.py at 4801753, check(cohort, card) with the card of every paper together, kind all): per measure and level, the 95 per cent interval 33 published populations give a new population's mean, SD and level-to-level step, a cohort passing where its step pass rate reaches 0.89 and its mean and SD rates reach 0.58 and 0.53 (the 10th percentile of the papers' own rates, each paper held out), every cell scored as if the cohort had 40 people. Scored on the measures the card and the 32-measure pool share by key (the seven chords among them, schwingcheck's SPINEPS_7), twice: the engine's values on the first run's training persons (stage 2), whether the truth every arm learns from sits where the papers put a population, a failing step being read as a frame or label-map error to render before any network trains; and a cohort drawn from each fitted prior (the re-estimated table with its size and offset; each PDM through the chords its drawn ends give), a prior predictive check of whether its level-to-level steps are ones the papers allow. Reported only, never an endpoint, a gate or a reason to drop an arm, since the arms are chosen by held-out accuracy and naming; on normal spines alone, since the card holds no L6 or T13 series, and it cannot bound one person's correlation across levels, which is what a PDM adds | mean, SD and step pass rates against their bars, one cohort a row, with the mean square of the z-scores |

What is scored and what is only reported: the primary endpoints are the value MAE averaged over the seven chords and
the bodies named right on three-body fields with the calibrated spread, both on the test persons, which only the full
run of stage 5 reads; the screen of stage 4 reports the same quantities on the validation persons, as feasibility and
a ranking, never as the decision. The calibration gate
is two-sided and pooled over the seven chords: coverage on the test persons within 0.60 to 0.76 at one spread and
0.90 to 0.98 at two, and sharpness, the mean calibrated spread no more than 1.2 times arm A's at the same coverage;
an arm outside either is read as miscalibrated or as uninformative whatever else it does. The explainability indices
and the latency are reported beside them, since they are the price, not the score. Whether a latent arm's gain is
worth its price was greg's to set as bars; he declined (02:46 UTC), so section 12, item 2, sets them in his place until
he says otherwise. The full run reads the test persons once per trial, and no choice follows that read: the arms it
runs are fixed by the screen's dated keep record before its plan is frozen (section 8).

## 8. Data, splits and the analysis

- Data: the gold tier 3 CTs with their masks (ENHANCE.PET's CTs and labels are on the grid's data root since
  2026-10-29; VerSe's masks through the carry and TotalSegmentator's from the Zenodo release on the data root, both
  already under SchwingNet's morphometry word and its size rule, none a fetch of this plan's). Truth is the engine's
  reading of each mask in the new frame, with its line ends exported (stage 1). The thin-slice studies (229, PR 44's
  README) are the first arm of every comparison; the thick ones (3 to 5 mm) are a stratum, since heights and discs
  move about a quarter of a slice there (PR 44 README).
- The training example on a real column: a window of a fixed number of consecutive bodies (three, as the phantoms
  are; five as a second value), each window a row of its own carrying the column's person, since with the naming term
  on every example of a batch must hold the same number of crops (session.py) and whole columns hold 22 to 25. The
  loader holds one crop per vertebra and indexes the windows into them, so the memory a trial holds is the crops of
  its columns (about a megabyte a crop at 48 x 56 x 32 x 3 channels: about 5 GB for a fifth of the training persons,
  about 26 GB for all of them, inside a 64 GB job), not the crops of its windows.
- Splits by person, in the form of SchwingNet's data/splits/rule.json (a salted sha256 of the person id), with the
  shares set in the plan files of stages 4 and 5, as the search flow's split keys are (salt, validation_share,
  test_share): validation 0.1 and test 0.2 (decision 7). rule.json itself holds a validation share only, and its test
  list (test-persons.json) names five C-ArmLSpine fluoroscopy persons and no CT person, and a hash cannot stratify (at
  0.2 the L4-on-sacrum stratum would get about 8 test columns), so the test part is a listed one, written before any
  run trains by draw_test_reserve.py beside this note, whose docstring is the rule of record:
  - the unit is a person as far as the records tell: a group of one patient's repeat scans (next bullet), else one
    study; a unit is hashed by its group's lowest study key, counts once in its stratum, and its studies always share
    a part, and any fallback to the hash draws by that unit key, never by a row's own person key;
  - every class belongs to one of greg's families (his rule of 2026-10-30 09:43 UTC), ribs first, as the truth name
    below is: thirteen rib-bearing bodies are a T13 (l6_thirteen_ribs, thirteen_ribs, VerSe's t13); eleven, or eleven
    on one side and twelve on the other, are a thoracic rib anomaly (eleven_ribs, asymmetric_ribs); twelve go by the
    column's length, an L6 below an L5 a six lumbar column (l6_twelve_ribs) and L4 on the sacrum a four lumbar one
    (four_lumbar_twelve_ribs); VerSe draws no ribs, so its readers' l6 and four_lumbar go by the read (verse581's,
    7/11/6/5, is a rib anomaly by its ribs, but it is a held fold person in no part), and TotalSegmentator's ribs are
    not read against its levels, so the l6 its masks name is a family of its own, six lumbar by names, reported apart
    and never pooled with six lumbar until its ribs are counted;
  - the first run, the smoke and the screen of section 9, trains, validates and tests on normal spines alone, as greg
    asked: the store's class normal confirmed by the masks (status confirmed_by_masks: twelve rib pairs, C2 to L5
    named, every structural check passed), the set the annealer screen takes too, and two of the three VerSe holdout
    persons its readers read normal, verse759 and verse809, who are test; the third, verse573, is test but read by no
    counted number, since its masks leave a fused, sacralised L5 undrawn (admission.json's flag no_l5); the 251
    class-normal studies the masks do not confirm and the 166 unread keep their part for a later run and are read by
    none of the counted ones;
  - a plain unit (class normal or unread) is validation below 0.1 and test in the band 0.1 to 0.1 plus the share;
  - each anomaly stratum (the member, the store's class and the call by names, so the eleven-rib columns with L4 on the
    sacrum are a stratum apart from those with L5) lies inside one family and takes as test the first min(n,
    max(ceil(share x n), min(10, floor(n / 2)))) of its n units in a second salted rank (spelled out in the
    docstring), the rest train: the anomalies are split across test and train alone, each family cell by cell, a
    cell of one unit wholly test (ENHANCE.PET's asymmetric ribs with L4 on the sacrum), and a run's choices are made
    on the normal validation part;
  - a study in doubt is in no part until a person has looked: the store's classes look, open, labelling_error and
    not_whole, anomaly-holdout.json's disputed persons, and, for every member, a study whose release masks lack a level
    from C2 to L5 (admission.json's complete list), since a segmenter's level is never pooled with the release's;
    doubt comes before every other branch, so a holdout study in doubt is held;
  - anomaly-holdout.json's five holdout persons are test at every share and never trained on, count in no stratum and
    carry no weight in a number pooled over strata; its three fold persons,
    which the route's other fine-tunes train on, are in no part.
  At SchwingNet 3abc2fa (export sha256 ac95c7c1...) the 1,738 studies are 1,620 units: at 0.2, 327 test (353
  studies), 167 validation and 1,091 train, with 32 units (35 studies) in doubt and 3 held; at 0.3, 495 test (533
  studies), 167 validation and 923 train. The first run's normal spines are 1,060 units (1,157 studies): at 0.2, 732
  train, 124 validation and 204 test (223 studies); at 0.3, 611, 124 and 325 (356 studies). The anomalies by family,
  as drawn units test and train at 0.2: four lumbar 10 and 16, six lumbar 10 and 36 (and VerSe's three fold persons
  held), six lumbar by names 1 and 2, T13 8 and 9, thoracic rib anomalies 16 and 19; 45 test units and 82 train in
  all, the same at 0.3 but for six lumbar, 14 and 32; two holdout persons, verse549 (four lumbar) and verse547 (T13),
  are test beside them in no stratum. The strata, as units and test units at 0.2 (at 0.3 where it differs):
  ENHANCE.PET l6_twelve_ribs 46 and 10 (14), l6_thirteen_ribs 13 and 6, four_lumbar_twelve_ribs 26 and 10, eleven_ribs with L5 23 and 10, eleven_ribs with L4 on the sacrum 8 and
  4, asymmetric_ribs with L5 3 and 1 and with L4 1 and 1, thirteen_ribs 2 and 1; TotalSegmentator l6 3 and 1; VerSe
  t13 2 and 1. The anomaly families are read apart and never pooled with the normal part; a number that pools the strata of
  one family weights each stratum by N_h / n_h, its units over its test units, a holdout person weighing nothing in
  it, and the person bootstrap resamples within strata, so the drawn strata never tilt it toward the cells drawn
  hardest.
- The reserve, latent-prior-test-reserve.json (584 studies at 3abc2fa, sha256 cd9ddfed...), with
  latent-prior-repeat-groups.json beside it (the 85 units of more than one study, by the export's person keys, sha256
  a45797c3...) and a report that pins every input and both files by sha256: every unit not held that is test at 0.3
  or whose hash is in the band 0.1 to 0.4 whatever its kind, every study of it listed with its own why, and the
  studies outside the export that admission.json waits on, reserved with their unit where they have one and else by
  their own key's band (today verse531 for a look and enhance_pet 1347 for its repaired mask). It holds the test part at either
  share, decision 7's fallback hash draw at either share, and every study a look could move into a class or out of
  doubt, so none of them can become test after a run trained on it. The auto-anatomist flow leaves every listed person
  out of every part it trains or validates on (section 10). The evaluation reads its test part from the parts file the
  generator writes at the frozen share and never draws it again from a later export: a person not listed is never test.
- Persons: every ENHANCE.PET study is its own person in the store until the census's grid match (gold3-ct README
  section 7) assigns autoPET's; Leipzig and Careggi carry no person id at all. autoPET's 979 whole studies come from 865
  to 900 persons, so 79 to 114 are repeat studies; the census matched 900 CTs to 867 persons, about what one CT a
  patient gives, so the match probably cannot name the repeats either, and the near-duplicate check is the rule
  (facts.jsonl, repaired masks left out, every study of the facts in the export or not, joined by union-find). Two
  autoPET studies at most 3 ids apart are linked when their vertebral volumes C3 to L4 agree to a mean absolute log
  ratio under 0.03 over at least 15 whole levels: adjacent pairs fall under 0.03 at 127 of 3,036, against 0.05 per
  cent of other autoPET pairs and 0.02 per cent across sites. Two studies of one site at any ids, Leipzig and Careggi
  included, are linked when their volumes agree under 0.05 and either the distances between consecutive vertebral
  centroids agree under 0.015 over at least 12 pairs (no pair across sites or far apart in autoPET, 0 of 1,131,744,
  meets both) or their rib volumes agree under 0.04 over at least 16 whole ribs (0 of 503,506 autoPET pairs 11 or
  more ids apart). That gives 88 groups in the facts and 85 units of 203 studies in the export (80 autoPET units
  holding 113 repeat studies, inside the 79 to 114 autoPET's counts allow, and 5 Leipzig pairs); every unit holds one
  rib class today (0702 to 0704 count once in their stratum, 1008 to 1010 once in theirs), and a unit whose studies a
  later reading puts in two classes is in doubt as a whole until a person settles it. Two units probably join two
  people (1000 with 1003, 0097 with 0114, by their ribs), which keeps studies together and leaks nothing.
  aliases.json takes over once it lists anything. A repeat every link misses is the leak this plan cannot close, and
  the PREREG says so.
- The truth name on the anomaly columns, pre-registered by the ribs (holdings/gold-tier-3.md): the gold 3 census's rib
  classes are the truth and the masks' names the record. In the store's classes, 50 L6 columns have twelve rib pairs
  (the holdings note's 51 counts one the store classes look) and 14 have thirteen, the thirteenth on the label L1,
  which the chain names a T13 column and the scheme cannot; of the 39 columns named with L4 on the sacrum, 28 have
  twelve rib pairs (the sacralisation candidates, which the ribs cannot tell from a column one body short; the holdings
  note's 24 leaves out 0702, 0926, 1145 and 1534, classed by rib count alone), 8 have eleven, a stratum of their own, 1
  has asymmetric ribs and 2 are in doubt. Naming is reported exact and within one level per stratum. Gold 3 holds four
  VerSe T13 persons: verse547 is in the anomaly holdout and test here, verse588 is in doubt (its release masks lack
  C2), and verse602 and verse631 are the listed stratum, which draws one; T13 as a type is reported descriptively on
  those two test columns, never tested, and no emission for it is fit from data (section 6).
- Fields for naming: every window of 1, 3 and 5 consecutive bodies of each test column, so a column of 22 bodies gives
  22, 20 and 18 fields; the share named right is over fields, its interval by a bootstrap over persons, since fields of
  one column are not independent, and a column's size estimate and type are shared by all its fields, so naming
  errors come in runs and the effective sample is nearer the test columns (the first run's 223 normal ones at 0.2)
  than its three-body fields (about 4,500).
- Pairing and the decision rule, in the full run (stage 5): the full run trains on the first run's training part
  and the anomaly train part (greg's choice of 2026-10-30 10:03 UTC, over keeping every counted run on normal
  spines and giving the anomalies a later run of their own), its choices made on the normal validation part,
  and reads the normal test part, where the contrasts below are decided, and the anomaly test part by family beside
  it. Every arm is read on the same test vertebrae, so the
  comparison of two arms is a paired difference per vertebra (or per field), its 95 per cent interval by the person
  bootstrap at fixed seeds; three seeds an arm, the seed-to-seed spread reported and required to be smaller than the
  bar, the arms compared on the seed means. One primary contrast, C against A on three-body fields with the calibrated
  spread; B against A decides the features, D against A and C against C0 the prior, C0 against A the head; the rest are
  secondary, and a bar is met when the lower bound of the paired difference's interval exceeds it. A goes to the full
  run whatever the screen shows, and C too unless it fails the screen's numbered rule, in which case that failure is
  the head question's answer and the full run's primary contrast is D against A, pre-registered as the alternative.
- The screen (stage 4), on greg's rule: every arm side by side, one seed each and arm A at three seeds, on a fifth of
  the first run's training persons by the same hash, for 50 epochs, read on the validation persons alone and never on test. It
  ranks, and drops an arm only on three numbered failures, written in the PREREG before it is sent: it does not train
  (the validation landmark distance, or arm E's value MAE, at the end not below half of its value at the start, or
  the loss not falling over the last ten epochs); it does not calibrate (sharpness, since the quantile fit puts
  one-spread coverage at 0.68 on validation by construction: the calibrated spread more than twice arm A's at the same
  validation coverage, or coverage at two spreads outside 0.90 to 0.98, which the one-quantile fit does not fix); or it
  names worse than the engine's values on three-body fields by more than 7 points, twice the screen's standard error.
  What the screen can resolve: on the first run's 124 validation units with naming errors clustered by column, one
  standard error of a paired naming difference is about 3.5 points and of the value MAE about 0.08 mm, so arms within twice that
  are ties and both go on; arm A's three seeds give the seed spread on validation as a number, and every drop margin
  sits above it. The screen trains, validates and reads normal spines alone, the first run's set above; no anomaly
  column is in it. The keep list, with each arm's validation numbers, is written as a dated record in this folder before the
  stage 5 plan file's bytes enter the PREREG's Covers line, so the full run's test read follows no choice.
- Power, under the rule as written: the primary contrast is read on the first run's normal test part, at 0.2 204
  units (223 columns) and about 4,500 vertebrae. A paired MAE difference of 0.3 mm against a paired SD of about 2 mm a
  vertebra is told from zero at 80 per cent power with about 350 vertebrae, about 1,750 after a design effect of 5 for
  clustering within a person; but the rule asks the interval's lower bound to clear the bar, so the true gain the
  design finds at 80 per cent power is the bar plus 2.8 standard errors: about 0.5 mm of value MAE (a standard error
  near 0.065 mm at 4,500 vertebrae under the design effect) and, for naming with the column as the cluster (223
  columns, two arms discordant on 15 per cent of fields, a standard error near 2.5 points), about 10 points on
  three-body fields against the 3-point bar first proposed. The
  within-column correlation is measured in stage 2 from the engine's rows, and the naming bar is set from it before the
  PREREG is frozen; the share stays 0.2 (decision 7), and 0.3 (325 normal test units) is the alternative decision 7
  names if the bar stage 2 gives is wider than three points. The anomaly families are small even listed (10 four
  lumbar, 10 six lumbar, 8 T13 and 16 rib-anomaly test units drawn at 0.2), so they are cross-fitted at stage 2 and
  reported by family and stratum with Wilson intervals at stage 5, never tested and never pooled with the normal
  part.
- Nothing from CTSpinoPelvic1K (dropped for good), nothing from the morphometry phantoms (deferred); the
  autoanatomist phantoms serve stage 3 only, as a smoke test of the code path.

## 9. The stages and the jobs

In order, each with what it decides and the jobs it would ask for; the count is a proposal for greg's word, and a
later stage waits for the one before it. No job is sent by this plan.

| stage | what runs | where | jobs proposed | depends on | what it decides |
| --- | --- | --- | --- | --- | --- |
| 1 export | the engine over every gold 3 mask in the new frame, with each measure's two line ends and the vertebra's frame written beside the value (a `--lines` output of `python -m morphometry run`, to add on the engine's branch) and, on the CTs, the mask-free frame (crops.from_found) and the oracle's beside the engine's; aggregates in the report, rows on the grid | grid, CPU | 0 only if the `--lines` output and morphoview reach the pinned copy under SchwingNet's grid/bordercall/ (tools/bordercall_vendor.py copy, VENDORED) before `morphometry enhance` and `morphometry verse`, the two jobs the owner counted on 2026-10-29 15:19 UTC, are sent; else 1, or a re-run that needs a new count | the export flag on PR 44's branch; the re-vendor; the morphometry re-run in the new frame; the CTs landed; the autoPET person match | the truth table and the PDM's points exist; the three frame gaps are numbers |
| 2 features, no network | on the engine's rows: the exact rule with the seven chords, with the 32-measure pool, with the pool and the ratios, with a per-level Gaussian over b (the two PDMs, K on a curve), and with b beside the seven, under the re-estimated table and the printed one; a discriminative classifier over the same feature sets; leave-persons-out, five folds; naming by field length and rib class; the within-column correlation for the power of section 8; E3 nameability; the literature bounds of section 7 on the training persons' values and on each fitted prior's draw | grid, CPU; the rows stay on the grid under SchwingNet's morphometry rule and only the report's aggregates leave (decision 3) | 1 | stage 1; for the bounds alone, PR 38's bounds.py and its records/bounds reaching the pinned copy | whether named measurements name as well as a latent at the feature level; how many named measures the latent is worth; K; the naming bar's power; whether arm B is worth training at all |
| 3 smoke of the heads | the six arms on the existing autoanatomist phantoms, a few hundred steps each, the code path from the oracle to the named bodies for every head, and the CPU step time of each head; the latent arms on a PDM fit on the phantoms' oracle ends (the minimal 14-end set, kept with its digest) | grid, CPU, batch class, on the launched autoanatomist flow; a batch-class job measures no GPU time | 0 if the head block and its keys (section 10) land on PR 40, the search copy under SchwingNet's grid/autoanatomist/ is vendored again, and grid/searches/phantom_smoke.json names them in its space before docs/research/autoanatomist-search/PREREG.md is frozen, since its Covers line holds that plan by its bytes and neither file changes after; else 1, a plan of this evaluation's own flow kind under its own PREREG (section 10), a third part in its Covers line | the head block built; the phantom PDM; probe_smoke first, as the owner asked | the arms run end to end; nothing is read as a result |
| 4 screen | greg's rule: every arm in parallel on a short run. One plan: the six arms, and F where the auto-anatomist thread's objective=mask is ready, one seed each and arm A at three seeds (eight or nine trials), each trial a Slurm array task starting a launcher run of its own on a card of its own (the DRR study's form, section 2), 50 epochs, an epoch ceil(training windows / batch) steps in expectation, since the session draws its batch with replacement (section 10), over a fifth of the first run's training persons (normal spines alone) by the same hash, three-body windows at the smoke's batch of 2 (6 crops a step), calibrate=quantile at coverage 0.68, naming on, every other block at the smoke run's, w_prior 1; each trial calibrates on the validation persons and evaluates there in its own step, as the search's trial step does, writing section 7's quantities to its ledger entry; a merge run afterany the array gathers them; no test read | grid, GPU, the launched flow of this evaluation's kind under its frozen PREREG (section 10) | 2 (the array, then the merge); 1 where the trials share one card in series inside one job, the wall time then their sum | stages 1 to 3; flows/<kind>.py with its screen mode, the volume row kind with a person key, the windowing and this evaluation's PREREG, none of them landed | which arms train, calibrate and name on real spines at all, by the numbered rule of section 8, and their order on validation; the keep list for the full run, as a dated record |
| 5 full run | the arms the screen keeps, three seeds each, every trial on the first run's whole training part and the anomaly train part (greg's choice of 10:03 UTC) for 50 epochs (five and a half times the screen's steps; fewer if the screen's curves settled earlier, the count written in the plan), calibration on validation in the trial step, the merge reading the test persons once for every finished trial, the normal part and the anomaly families apart | grid, GPU, the same flow and PREREG, a second plan | 2 (the array, then the merge with the test read); the minimal form, A against C with two seeds, is 2 as well, the array smaller | stage 4's keep record | the primary endpoints per arm with intervals; the calibration gate; the explainability indices |
| 6 report | the figures of section 7 and the CLAIM report, from the run folders; the paired differences and the bootstrap | the flow's end step, or a container from the records | 0 | stages 4 and 5 | greg's decision on the head and the features, against the bars |

The search flow as PR 483 designs it retires half the trials at each rung on the validation reward and reads the test
part for the best trial only, so it gives one arm's test numbers and no paired comparison; its reward is also a
function of landmark distance, which arm E has none of. The screen and the full run are therefore the plan's own
flow kind (section 10), whose trials run one per array task on a card each, as greg's "as many in parallel as
possible" asks and as the DRR study already runs; a foreach inside one gpu-class job would run them on that job's one
card, in series or sharing it. The search's halving and controller are for a later sweep of w_prior and K, with the
anomaly families in its objective, since a weight chosen on a validation part of normal spines alone would pick the
value that hurts the families.

The cost, with its basis. No record holds a GPU step time: the smoke's 2 s a step was 6 crops on 4 CPUs, 0.35 s a
crop, and stage 3's batch-class job measures CPU time only, so the hours of stages 4 and 5 are a formula with one
unknown, measured by a short gpu-class smoke that is a count of its own or by each trial's first hundred steps, and
written into the record after, never claimed before:

| stage | unit of work | count | basis record |
| --- | --- | --- | --- |
| 1 | the engine over 1,738 masks | the whole set is the 32-CPU, 24-hour job SchwingNet's grid/morphometry.sbatch already is; the 229 thin studies took one morning in a container | PR 44 README; the morphometry memory |
| 2 | the rule and the classifier over the rows, five folds | minutes once the rows exist | item P's data axis timings |
| 3 | six arms, a few hundred steps each, on 4 CPUs | the smoke's 150 steps on 6 crops a step took 313 s | smoke.json |
| 4 | a step is a batch of three-body windows, 3 crops each; an epoch ceil(windows / batch) steps in expectation | a fifth of the first run's training persons (795 normal columns at 0.2) is about 160 columns and about 3,200 three-body windows; at the smoke's batch of 2, about 1,600 steps an epoch and 80,000 steps in 50 epochs, about 480,000 crops a trial; at the smoke's CPU time that is 47 hours, so the GPU time a crop decides whether a trial is hours or a day; the eight or nine trials run side by side, so the screen's wall time is one trial's | smoke.json (spines_per_batch 2, count 3, 0.35 s a crop on CPU); the subset share and the window length are the plan's |
| 5 | the same, over the first run's whole training part and the anomaly train part | 882 columns at 0.2 (795 normal and 87 anomalous), about 19,400 vertebrae and 17,500 windows; 50 epochs about 440,000 steps a trial, five and a half times the screen's, and at most twenty-one trials where F is kept, side by side | the screen's measured time a crop; the epoch count is the plan's |

The total ask, in the owner's units: 2 CPU jobs (stages 1 and 2), 2 GPU jobs for the screen (an array and its
merge) and 2 for the full run, with stage 3 folded into a plan another thread is already writing, and one short
gpu-class smoke where the step time is to be measured before the screen. That smoke is the auto-anatomist thread's
gold3_latent_smoke (SchwingNet PR 483: its flow, its plan and its own PREREG; objective=mask on four ENHANCE.PET CTs,
two trials of 300 steps in series on one card), counted once for both threads: it times the shared trunk and decoder,
and each trial's first hundred steps here then time that trial's own head. greg gave that word and count on 2026-10-30
at 03:20 UTC: "2 CPU 2 GPU 2 Full run plus 1 short GPU smoke is fine". The count is for these jobs as this note
describes them; nothing is submitted until the pieces of section 10 exist and the PREREG is frozen, and a job that
grows beyond its line here needs a new count. The size rule applies to nothing here, since no fetch is made.

Beside these jobs runs the auto-anatomist thread's annealer screen: plan gold3_latent_screen of its flow kind
autoanatomist (SchwingNet PR 483, under docs/research/autoanatomist-screen/PREREG.md), four anneal schedules with two
seeds each at objective=mask, which is arm F, on 96 training and 24 validation ENHANCE.PET CTs, as a GPU array of
eight tasks and a CPU join afterany it. Those 2 jobs are outside greg's count above; he gave his word for both on 2026-10-30 at 08:56 UTC ("Yes to both"), and they wait only for that thread's frozen PREREG. Its question
is the schedule with the head held at F; this plan's is the head with the schedule held. The two runs keep one person
split: the persons this plan lists as test are read by the annealer run from the same list and never trained on
there, since arm F may start from its checkpoint (agreed with that thread on 2026-10-30; the list is
latent-prior-test-reserve.json, section 8, and the interface is in section 10).

## 10. How it fits the swappable-block design and the launched flow

- The contract, greg's rule of 02:49 UTC: every part is a block, every shape follows from the configuration, and no
  block value makes a second network. The network is already a block (blocks.py's `architecture`, model.ARCHITECTURES
  at 7d5fecb, whose table has architecture, w_naming and naming among its thirty keys). The `objective` block
  (landmarks or mask), its `w_name` and the refusals in blocks.problems are the auto-anatomist thread's work in flight
  (its notes of 02:28 and 02:50 UTC), not in PR 40 at 7d5fecb; the blocks below assume they land as that note says and
  sit under objective=landmarks, and the seven key names below are free in the table (that thread, 02:53 UTC).
- `measures`: the named measure set the readout computes and the rule reads, seven (specs.SEVEN, as now), pool (the 32
  Panjabi measures) or pool-ratios (the 32 with the size-free ratios). specs.py already derives everything from the
  keys chosen (specs.select, specs.landmarks giving the union of the points the measures need, specs.index_of,
  specs.values), so the decoder's landmark channels, the PDM's points, arm E's output width and the rule's table all
  follow from this one block and the same network serves the seven and the 32; the flow's own plan key for the
  measure set is dropped in its favour (that thread, 02:53 UTC). What is missing is the specs for the measures beyond
  the nine defined today, each a smooth rule over named points as the nine are, ported from the engine's definitions
  (morphoview.lines); that port is part of the head block's landing.
- `head`: heatmap (as now), latent (arm B), hybrid (C), latent-noprior (C0), heatmap-pdm (D) and values (E), with
  `pdm` naming the fitted model's file by its digest, which needs one new kind in blocks.py's table (a digest string,
  spelled as given; its kinds today are choice, switch, int, float, pair and triple), `pdm_k` the coefficients kept and
  `w_prior` the prior term's weight (1 in version 1, 0 for C0), beside the table's w_naming (the chain term) and the
  auto-anatomist thread's w_name (its name head), three weights with three meanings. The latent head is a dense layer
  from the fused features' pooled eighth scale to K + 7 numbers (b and the pose); the hybrid differs from it only in
  the loss and the emission; arm E's head gives 2 x |measures| numbers. Each head returns landmarks, values and a
  spread in the same shapes, so the loss terms, the calibration, the naming layer, the session and the flow run over
  any of them unchanged, as the probe does today. No block named is still the smoke run to the bit.
- `emission` and `prior`: `emission` chooses what the naming layer reads, measures or latent (the auto-anatomist
  thread's name head is a classifier on the pooled bottleneck, scored as named right; emission=latent feeds the chain
  from that latent instead, which lifts the refusal in blocks.problems that objective=mask forces naming off).
  `prior` chooses the model behind the naming layer: exact, the enumeration of naming.py over schwingcheck's rule, as
  now and the default; or pymc:<dotted path>, a callable that builds a PyMC model over whatever measures (or latent)
  the blocks provide, so that a model written for schwingcheck (chain_pymc.py's sampled and enumerated models are the
  first two values) drops in as it is. For the training loss the PyMC model's log-density is compiled to a JAX
  function through pymc.sampling.jax.get_jaxified_logp (in PyMC 6.3.2's source, read on 2026-10-30; it gives the
  negative log-density of the model's free variables unless told otherwise; PyMC 6.3.2 and PyTensor 3.3.4 are the
  schwingcheck requirements, JAX 0.12 the auto-anatomist's in a container; the grid's GPU environment is Python 3.11,
  where that thread's driver installs jax 0.10.2, flax 0.12.8 and optax 0.2.8 in a venv and bordercall's 86
  auto-anatomist tests pass, so the compile path must hold on jax 0.10.2 too), which jax.grad differentiates; at evaluation the model
  is sampled and its posterior read beside the exact one; a model whose log-density will not jaxify is used at
  evaluation only and the loss falls back to exact, which the run's record says. That compile path is to be shown
  working at stage 3 on chain_pymc.py's enumerated model before the screen names it.
- The PDM is an asset built by one command from the exported ends (a module `autoanatomist/pdm.py`: fit, project,
  reconstruct, the negative log-likelihood, with tests holding the round trip to 1e-6 and the gradient of the
  reconstruction to a finite difference), kept with its digest so a run names the model it used; it is never fit
  inside training. Stage 3's PDM is the same command over the phantoms' oracle ends.
- The naming layer takes a second emission: a per-level Gaussian over the size-free b whose means and covariances the
  same asset holds, under the rule's shared size (section 6), so `posteriors` and `body_loss` run on either feature
  space; the exact enumeration is unchanged.
- The data: PR 40's rows.py already reads a CT and its label NIfTI as a volume row through the oracle interface and
  caches it by its digest, so no new loader is needed; what stages 4 and 5 need is the engine's export (the line ends
  of stage 1) standing behind that interface in place of the stand-in ChordOracle, the volume kind admitted by the
  search module's row check (it takes phantom rows only today) with a person field copied verbatim from the export
  (enhance_pet:0001, colon and padding included; a gold 3 row without one is refused, and the id stands in for
  phantoms alone), a split that takes listed parts (the parts file draw_test_reserve.py writes at the frozen share names
  every study's part, unit, family and whether the first run reads it, and wins over the hash for every row it names, a fourth split input beside the salt and
  the two shares, which the module lacks today), and the windowing of a volume row into fixed-length fields (section
  8), each window a row with its column's person, so that the naming term's equal-count rule holds and the windows of
  one unit land in one part.
- The one person split with the annealer screen (SchwingNet PR 483): its plan writer and its flow's start step read
  latent-prior-test-reserve.json beside test-persons.json and leave every listed person out of train and validation
  alike, comparing the export's person field by exact string, and keep each unit of latent-prior-repeat-groups.json in
  one part (leaving out a member whose frozen part differs from its unit's); before training the run checks its
  validation part against the export's hash, that every reserved normal ENHANCE.PET person was matched (424 at
  3abc2fa, 354 of them confirmed by the masks, leaving 801 in its pool of 1,155 confirmed normal ENHANCE.PET
  persons) and that none is in its manifest, and records both files' sha256 and the matched
  count beside RUN.json. Its screen takes ENHANCE.PET rows of class normal confirmed by the masks, the first run's
  normal spines here, so greg's rule of 2026-10-30 09:43 UTC holds on both sides; the anomaly-aware rule left both
  files byte for byte as they were and moved no normal person. Arm F starts from that
  run's checkpoint only where the recorded sha256 is this file's and no test person of this evaluation is in that
  manifest; otherwise arm F trains from scratch.
- The screen mode of the flow. None of it is in PR 483 at d8cadc3: flows/autoanatomist.py does not exist,
  flows/registry.txt names no autoanatomist kind, and autoanatomist_search.py takes phantom rows under the plan keys
  search, class, rows, split, space, fixed, seeds, rungs, keep, trials, controller, objective, latency_crops and
  wandb_project, every one required and no other allowed. What follows is the auto-anatomist thread's stated design
  (its notes of 02:50 and 02:53 UTC): flows/autoanatomist.py, one plan JSON, every trial trained for a fixed epoch
  count with no halving and no controller, an epoch ceil(training rows / batch) steps where the session draws each
  batch with replacement (so a pass in expectation only), the anneal over the run, the keys epochs, train_share, test
  (on or off, off in the screen's plan) added to the HANDOFF's, trial words going straight to blocks.parse, and the
  join's report marking the pre-registered decision numbers apart from the rest; an ENHANCE.PET row is kind, id, ct,
  labels, scheme enhance, seed, frame. Most of the screen the HANDOFF's layout could already say (space {head: the six
  values}, seeds the configurations, trials equal to the seeds, rungs one entry of N steps, keep near 1, rows the
  fifth's volume rows), so what the module truly lacks is small: a score for a trial whose evaluation gives no landmark
  distance (arm E, scored on its values and its naming), a test read of every finished trial rather than the best, the
  volume row kind with its person key, and the windowing. Each trial calibrates and evaluates on the validation
  persons in its own step, as the search's trial step does; the gathering is the merge run's.
- The flow kind. One registry kind is held to one PREREG, and the auto-anatomist kind's PREREG asks which blocks give
  the lowest validation landmark error on phantoms, with no bars; once frozen it may never change, so this evaluation's
  question, endpoints, gate, strata and bars cannot enter it. Stages 4 and 5 (and stage 3 in its one-job form) are
  therefore a flow kind of this evaluation's own, with every piece a kind needs: flows/<kind>.py with its FlowSpec
  class, a thin subclass of the auto-anatomist flow's that reuses its steps, so there is one flow's code and two
  kinds; grid/<kind>-driver.sbatch in the shape of grid/v1-driver.sbatch, starting flows/launch.py <kind> in the
  background; the <KIND>_RC word; a KINDS entry with its LEFT_OUT reasons in tools/run_code.py; the gate word in
  grid/gate.sh with its refusals and its gpu class (the gate refuses a gpu-class job whose script the registry's fourth
  column does not name); the registry line; and the PREREG under SchwingNet's docs/research/latent-shape-prior-evaluation/
  with its .sha256 and a Covers line holding the screen's plan by its bytes, written and frozen before the first job.
  The screen's merge writes the keep list as a dated record beside the PREREG; only then does the full run's plan
  enter the Covers line, hashed again before the full run's first job, so the test read follows the choice of arms
  and never steers it. A departure is a dated line in its DEVIATIONS.md. The trials run as the DRR study's do: a Slurm array, each task its
  own launcher run of the kind with a --trial word on a card of its own, and a merge run afterany the array.
- The plan files for stages 4 and 5 are two JSONs under SchwingNet's grid/searches/, the folder the HANDOFF plans, in
  the layout of its section 4 with the keys above, the six heads as the block space, w_prior fixed, the split's salt
  and shares, and the data source the gold 3 volume rows; the auto-anatomist thread's own PREREG
  (docs/research/autoanatomist-search/PREREG.md, not yet there; the folder holds that thread's prior art) covers
  phantom_smoke alone.
- Order of landing: the export flag on the engine's branch (PR 44's thread) and the re-vendor of bordercall under
  SchwingNet's grid/bordercall/; the measures port, the head block, pdm.py, the prior block and the windowing on the
  auto-anatomist's branch after PR 40 merges (or on a branch of this thread's own from it, once that thread's work is
  in); the volume row kind with its person field, the listed parts, the score for a trial with no landmarks and the test switch in
  SchwingNet's search module, and flows/autoanatomist.py, after PR 483 merges; then this evaluation's kind, its plan
  files, its registry line and its PREREG in SchwingNet. Stage 2 asks nothing of PR 40 or PR 483 as they stand; stage 3
  asks PR 483's plan for the head block in its no-job form; stage 1 asks the export flag of PR 44's thread; stages 4
  and 5 ask the pieces above of whoever lands them.

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

## 12. Risks, and the decisions taken in greg's place

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
- Leakage by person: every ENHANCE.PET study is its own person in the store, and Leipzig and Careggi have no person
  id; probable repeat scans are joined into units by their vertebral volumes, spacings and ribs before any part is drawn,
  the split reads each study's part and unit from the frozen parts file, and a repeat every link misses is the leak
  left, named in the PREREG (section 8).
- MOOSE's masks checked by people are the annotation; nothing here raises a tier, and the maskedge offset (+0.14 to
  +0.20 mm on the phantom) is what a network trained on masks learns.
- The latent arms may win on landmark distance and lose on the named values or the naming, as Daridon's and Choi's
  ablations did: the endpoints are the values and the naming, not the landmarks.
- The calibration cannot fail its own coverage gate on validation, so the gate is read on test and carries a sharpness
  bound (section 7), and the screen's calibration failure is read as sharpness (section 8).
- The screen can void a contrast: A goes to the full run whatever it shows, C unless it fails the numbered rule, and
  the keep list is a dated record before the full run's plan is frozen (section 8).

What greg was asked, once, so the PREREG can be frozen, and what he answered at 02:46 UTC: "i have no idea", with the
rule quoted at the top, and at 03:20 UTC the counts of item 1. So the plan decides the rest, and each decision below
stands until he says otherwise. The interactive page pipeline.html beside this note, published as a private
artifact for greg on 2026-10-30 (https://claude.ai/artifact/8mfLZEEQupfs1wnGFKrASc), draws the stages as a
Metaflow-style flowchart with what each step does, the network inside a trial switched per arm, and these decisions.
At the coordinator's ask it also draws the auto-anatomist thread's annealer screen as a run of its own, with that
thread's decisions marked as its own, and it carries a glossary of the words it uses.

1. Counts and classes (section 9), the one decision greg took himself, at 03:20 UTC: two CPU jobs (stages 1 and 2),
   two GPU jobs for the screen (the array and its merge), two for the full run, and one short gpu-class smoke where
   the step time is to be measured before the screen, served by the auto-anatomist thread's gold3_latent_smoke and
   counted once; stage 3 folded into phantom_smoke. A job that grows beyond its line in section 9 needs a new count.
2. The bars, two decisions apart: for the features (B against A) and for the head (C against A, with C0 and D telling
   why), at least 0.3 mm of value MAE over the seven chords and a naming gain on three-body fields whose points stage 2
   sets from the within-column correlation (3 points is underpowered at a test fifth under the lower-bound rule,
   section 8), each with the lower bound of its interval above the bar and the seed spread below it; the calibration
   gate of section 7 met; and, for the features decision alone, every kept mode nameable by at most three measures at a
   partial R^2 of 0.8. Short of any one, the named features and the heatmaps stand. The screen sets no bar of its own:
   it drops only on the three numbered failures of section 8 and ranks the rest.
3. Stage 2 runs on the grid; nothing leaves it but the aggregates of the report.
4. The reference named feature set is the 32-measure pool with the ratios, the seven chords reported beside it, since
   the seven are what the specs draw today and the pool is what the rule can score; one network serves both
   (section 10).
5. All six arms are in the screen, arm A at three seeds, and F (the learnt latent, the auto-anatomist thread's
   objective=mask) joins it where that thread has it ready; the full run takes what the screen keeps, A always and C
   unless it fails the numbered rule.
6. Stages 4 and 5 run as a flow kind of this evaluation's own, a thin subclass of the auto-anatomist flow with every
   piece section 10 lists, its registry line and its PREREG under SchwingNet's docs/research/latent-shape-prior-evaluation/,
   this note staying here.
7. The test share is 0.2, and 0.3 (495 units) is the alternative if the naming bar stage 2 gives is wider than three
   points; the test set is a listed one from the start (draw_test_reserve.py, section 8): anomaly strata drawn by rank,
   plain units by the hash, one patient's probable repeat scans one unit, studies in doubt in no part, the holdout tested;
   the reserve covers both shares and the hash's own draw as the fallback, and the screen never reads the test persons.
   greg set the anomaly rule himself on 2026-10-30 09:43 UTC (normal spines alone in the first run; four lumbar, six
   lumbar and T13 split across test and train); the families are read ribs first, so a column with thirteen
   rib-bearing bodies is a T13 though its names end at L6, and an eleven-rib column is a thoracic rib anomaly though its
   names end at L4, and the first run's normal spines are the ones the masks confirm, as the annealer screen's are.

## 13. What this plan does not do

No training, no job, no data read, no change to PR 40, PR 44 or PR 483. The 2-D transfer (FluXray synthetics, the
view=2d block) is designed in SchwingNet's handoff and is not evaluated here; once the 3-D answer is in, the same
arms project through project.py and the same figures are drawn on the detector. The morphometry phantoms stay
deferred; the CTSpinoPelvic1K cross-check stays dropped. A column-wide model (Meng 2020), a learnt latent with a KL
beyond arm F and the search's sweep of w_prior and K are later runs, not these.

## 14. Where this leads: 2-D landmarks that identify the vertebra bearing them

greg, 2026-10-30 02:33, 02:39 and 02:41 UTC: "i think eventually something id like to try would be placing landmarks
on a 2d xray which can be operated on in 2d space with functions to estimate 3d properties, which should reach into a
higher dimensional space and let you classify the seemingly flattened flat xrays according to higher dimensional
properties"; "essentially i want you to find landmarks which exist in 2d which when operated on with other nearby
landmarks uniquely identify the vertebra bearing them"; "you can use those landmarks in 3d projected onto 2d
synthetics to figure this out, like a forward backward mapping, landmarks projected from 3d to 2d and 2d landmarks
projected from 2d to the original label, not back into 3d".

So the question is identifiability, asked as a forward and a backward map. Forward: the engine's 3-D landmarks on
each gold tier 3 vertebra, with their names and the vertebra's label, projected onto the 2-D synthetic view by
project.py under a stated camera, so every 2-D landmark arrives named and labelled. Backward: from the 2-D landmarks
alone, functions of a landmark with its nearby landmarks (on the same vertebra and the adjacent ones) that map to the
original label, the level and the column's type, and nothing is reconstructed into 3-D. The 3-D truth is used once, to
make the labelled 2-D set; the classifier never sees it. It is the feature-level question of stage 2 carried to the
view, and the gold tier 3 set answers it with no new data and no radiograph. The pieces this plan lays down for it:

- The forward map: stage 1's export keeps every end in world coordinates with its vertebra's frame, its name and its
  label, so any camera can project it; project.py's camera model (SchwingNet's handoff) gives the 2-D positions, and
  a projected end that the view would not show (hidden behind bone, out of the field) is marked so, since a landmark
  a radiograph cannot show is no candidate.
- The landmarks: the projected ends of the engine's lines (a plate's rim, the pedicle's isthmus, the spinous tip, the
  canal's walls where the view shows them), each with its name, so a landmark found to identify is one a person can
  point to on the film.
- The functions: for each landmark, every function of it with its nearby landmarks that lives in the 2-D plane: the
  distances and the size-free ratios of section 5 as the view keeps them, the angles between chords, the relation to
  the neighbours above and below (the disc's height, the plates' convergence, the pedicle-to-pedicle step, the
  foreshortening of a width against its neighbour's). Each function carries the names of its inputs, so the set stays
  human-understandable in greg's sense, and none of them estimates a 3-D quantity.
- The backward map and the search: a forward selection over the functions, scored by the share of vertebrae named
  right under the exact rule (the re-estimated table over the chosen functions) and under the discriminative
  classifier of stage 2, with the label as the class and leave-persons-out; the gain of each function read as named
  right with it against without it, and the per-landmark identifiability as the best gain any function of that
  landmark gives. The output is a ranked list of 2-D landmarks and functions, not a network and not a 3-D model.
- The latent beside it: the PDM's coefficients b, fit in 3-D and projected with the landmarks, enter the same search
  as one more candidate feature set, which is this plan's own question asked of the view; the "higher dimensional
  properties" a flat view classifies by are then whatever functions of the 2-D landmarks the search keeps, read
  against the label alone.
- The anomaly classes: the rib-class truth of section 8 labels the L6, L4-on-sacrum and T13 columns in the 2-D set too,
  so identifiability is reported per class, and a landmark that names typical levels and fails on the strata is said
  so.

What it needs that this plan does not provide: project.py's camera model and the view=2d block landed (SchwingNet's
handoff), FluXray's realism for the synthetic to real step (docs/research/flux-realism), and a 2-D truth of its own on
real radiographs (C-ArmLSpine's, the film corpora) to say whether the landmarks and functions the synthetics pick out
hold on a real radiograph with a real detector and a real pose. It is written here so the stage 1 export keeps what
the forward map will need: every end in world coordinates with its vertebra's frame, its name and its label.
