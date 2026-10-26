# Naming a vertebra from its neighbours, and how many dimensions that takes

**Status: specified, not implemented.** Everything here is synthetic — columns drawn from
Panjabi's published means and spreads. No CT, no labels, no corpus, no data access.

## The question

Can the identity of vertebra `i` be computed from the morphology of the vertebrae **adjacent**
to it — one or more neighbours, not `i` itself — and if so, how many dimensions does the
discriminating information occupy?

That second half has two readings. **Both are real and the study must answer both**, because
they decide different things.

### Reading 1 — statistical dimensionality: does a *formula* exist?

How many linear discriminant directions of the 7-measure space are needed to separate the 23
levels? If one direction carries most of the separation, there is a **scalar vertebral level
index** — an actual formula, a weighted combination of measurements that increases monotonically
down the spine. If three or more are needed, no scalar formula exists and the honest deliverable
is a classifier, not an equation.

This is answered by the discriminant eigenvalue spectrum and, more usefully, by accuracy as a
function of the number of retained discriminant dimensions. Report the curve, not a threshold.

### Reading 2 — projective dimensionality: can one X-ray see it?

This is the one that decides the clinical plan, and it is a question about **which measurements
survive a projection**. Each of the seven SPINEPS-measurable quantities has an anatomical axis,
and a radiograph in one plane preserves only the measurements that lie in that plane:

| measure | Panjabi | axis | lateral view | AP view |
|---|---|---|---|---|
| `h_post` | VBHp | craniocaudal | **yes** | yes |
| `endplate_depth` | EPDu | antero-posterior | **yes** | no |
| `endplate_lower_depth` | EPDl | antero-posterior | **yes** | no |
| `canal_ap` | SCD | antero-posterior | **yes** | no |
| `endplate` | EPWu | transverse | no | **yes** |
| `endplate_lower` | EPWl | transverse | no | **yes** |
| `canal_w` | SCW | transverse | no | **yes** |

So three measurement regimes, and they are the experiment:

- **`lateral`** — `h_post`, `endplate_depth`, `endplate_lower_depth`, `canal_ap` (4 measures)
- **`ap`** — `h_post`, `endplate`, `endplate_lower`, `canal_w` (4 measures)
- **`both`** — all 7, which is what only a volume or a registered pair gives you

**The decision rule.** If `lateral` (or `ap`) reaches `both` within noise, a **single
fluoroscopic shot is enough** and the problem is 2-D. If `both` beats either single plane by
more than the margin, the discriminating information is genuinely 3-D, a single projection
cannot name the vertebra, and the recovery route is registration — see below.

**One honesty constraint on this arm, which must appear in any write-up.** Treating a projection
as a clean selection of in-plane measures is an **idealisation, and an optimistic one**. A real
radiograph adds magnification, obliquity, cone-beam distortion and superimposition of the
contralateral side, none of which is modelled here. So the 2-D arms are an **upper bound** on
what a real fluoroscopic image yields. If `lateral` fails even in this idealised form, that is a
strong negative; if it succeeds, it has not yet been shown to succeed on an image.

## The design

**Predict the identity of `i` from its neighbours only.** The target vertebra's own measurements
are withheld. Vary the neighbourhood:

| arm | visible | why it matters clinically |
|---|---|---|
| `below1` | `i+1` | the target is at the cranial edge of the field |
| `above1` | `i-1` | the target is at the caudal edge |
| `flank` | `i-1`, `i+1` | the target is obscured — hardware, overlap, a cement plug |
| `flank2` | `i-2 … i+2` minus `i` | a five-body field with the middle unreadable |
| `with_target` | the window including `i` | the existing baseline, for reference only |

The clinical case this serves: a vertebra that cannot itself be measured — instrumented,
overlapped by the ilium, clipped by the collimator — can still be named if its neighbours carry
the information. That is a different and harder claim than the one this package already makes.

**Three traps, each of which would produce a plausible wrong answer.**

1. **No absolute position may reach the model.** If a feature encodes where the window sits in
   the column, the model is counting, and counting is the thing this whole programme exists to
   avoid. Build the neighbour features from the measurements alone and assert in a test that
   shuffling the window's position leaves the prediction unchanged.
2. **The per-case normalisation is estimated from what is visible.** This package divides each
   measure by that case's median across its measured levels. In a limited field of view that
   median comes from two or three vertebrae, so it is noisy and biased, and the bias is a
   function of *which* levels are visible — which is itself informative about level. **That is a
   leak.** Report accuracy against the number of vertebrae used for normalisation, and include an
   arm normalised by a fixed external constant rather than the visible median, to bound how much
   of the performance is the normalisation smuggling in position.
3. **Chance is not 1/23.** Levels are not equally likely in any real field of view, and a
   neighbour-only design has structurally correlated errors — naming `i` as `i+1` is one
   vertebra wrong, not a coin flip. Report exact accuracy, within-one accuracy, and the full
   confusion structure, and state the marginal distribution the chance rate is computed against.

## The anomalous arm, which is the point of the whole programme

Run every regime and every neighbourhood across all six phenotypes the generator carries:
`typical`, `four_lumbar`, `six_lumbar`, `t13`, `lumbar_rib`, `no_rib_t12`.

A neighbour-based formula is **more** exposed to transitional anatomy than a target-based one,
because the neighbour relation is exactly what a transitional vertebra breaks. In a six-lumbar
spine the vertebra below L5 is L6; in a four-lumbar spine it is the sacrum. A formula fitted on
typical columns will name the neighbour correctly and the target wrongly, and it will do so
*confidently*. So:

- Report per-phenotype accuracy, never pooled alone. A pooled number hides the failure.
- Report the **signed** offset distribution per phenotype, not just the error rate. A systematic
  one-level shift in `six_lumbar` is a different finding from scatter, and it is the finding that
  would matter.
- The existing `sweep` command's criterion — rank by the **worst** phenotype, not the mean — is
  the right criterion here too.

## If it is 3-D: registration, and what it is *not* for

Should `both` beat each single plane, the plan is to register an intraoperative fluoroscopic
image to a preoperative CT so the missing out-of-plane dimension can be read from the CT.

**The crucial point, and the reason this is not circular.** The registration is needed *only to
recover one missing dimension of local morphology*. It is **not** used to count levels, and it
does not need to be globally correct — a registration that is locally accurate over the few
visible bodies suffices, because the classifier only ever reads local shape. That is a far
weaker requirement than registration-based level localisation, which needs a globally correct
correspondence and whose published naming accuracy peaks around 73 %. Keep the two claims
strictly separate in any write-up: this uses registration as a *measurement device*, not as a
*localiser*.

Sequence to specify before any image work: CT segmented by SPINEPS → the 7 measures per visible
level → a projection model producing the 2-D measures → registration recovering the third axis →
the classifier on the full 7. Each stage synthetic first.

## Latency, measured

Measured on a Windows workstation, 2026-10-26, single core. `HANDOFF.md` carries the same table.

| operation | time | rate |
|---|---|---|
| **place one window (inference only)** | **0.40 ms** | **2,500 /s** |
| synthesize one column | 1.15 ms | 868 /s |
| `load_reference`, 7 measures | 3.9 ms | — |
| train, 120 columns | 0.35 s | — |
| train, 600 columns | 2.35 s | — |
| train, 2000 columns | 7.69 s | — |
| evaluate one phenotype, 400 windows | 0.71 s | 561 /s |
| **one full `A(S, r)` evaluation** | **7.24 s** | — |

**Inference is 0.40 ms and is not the latency problem.** Whatever the clinical budget turns out
to be, it is spent on segmentation and — if the answer is 3-D — on registration, not on naming.
That is worth establishing now, because it means a 3-D answer is a *pipeline* cost, not a
real-time one, and the registration step is where any latency work belongs.

## What would make this publishable, and what would sink it

The strong result is: **a scalar formula, in one plane, that names a vertebra from its neighbours
and holds across transitional anatomy.** Each of those four clauses is a separate test and any
one of them can fail.

The result that would sink it, and which must be looked for rather than hoped against: the
formula works on typical columns and shifts by exactly one level in `six_lumbar` and `t13`. That
is not a small degradation — it is the failure mode that makes a level-naming device dangerous,
because it is confident and systematic. Look for it first.
