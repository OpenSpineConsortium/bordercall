# Morphometry: the handoff of 2026-10-30, 20:30 UTC: the lines carried onto FleXray's X-rays, and curved shapes

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's words of 16:49 UTC ("make sure these lines can be projected from 3D to 2D natively,
surviving a conversion by flexray to a fluroscopic xray, further, there should be basic
functioanlity for non-linear arcs/curves/planes/volumes/ect") and of 20:06 UTC ("Please write a
handoff and checkpoint so another account can continue this work at this point do not more
checking just push and write everything"). So this entry was written and pushed with no review
and no mutant run, on that word. This pass read no real mask or CT and queued no grid job; the
owner's hold of 14:45 UTC on the jobs stands (no grid sends, no report reading, no plots until
the owner says the resynthesis is done). SchwingNet's side of the same stop is its checkpoint
docs/checkpoints/2026-10-30-morphometry-lines/README.md, on its branch
claude/project-thread-gv744i.

## What was built

The research note's section "Carrying the lines onto FleXray's X-rays" says what each part does
and what holds it; in brief:

- morphoview/projection.py copies FleXray 1.0.2's camera on nanoDRR 0.1.5 (the pose, the
  intrinsics, one ray a pixel to its centre, row by row), the crop SchwingNet renders, and
  FleXray's canvas from its model's preprocessing.json (256, padded to a square); CHECKED names
  the two releases, and a render of another FleXray is projected with a warning.
- `python -m morphoview project` (morphoview/__main__.py) carries lines.csv and frames.csv onto a
  render in three forms: SchwingNet's render manifest, a render of its realism programme
  (`--realism RENDER --sample ID --ct CT`, whose records name no camera, read from manifest.jsonl
  and recipe.json), or a view file. With `--edits` and `--filter` it lists each fluoroscopic
  edit of a realism render: whether it holds the render's pixels, how far it moved the render's
  picture (edit_shift, the phase correlation's peak by magnitude, refined by Foroosh's ratio, to
  0.01 px on known shifts) on the render and on FleXray's canvas, and whether FluXray's filter
  kept it.
- FleXray's labels at both thresholds a request names are recorded and told apart: 0.0, the
  training profile's, the support, which our shadows equal pixel for pixel in all nine views and
  levels; and 0.5, a bare request's, at which SchwingNet's realism programme renders its truth
  masks, which drops bone thinner than about 8.7 mm along the ray. Landings are measured on the
  shadow, never the mask.
- morphoview/shapes.py: curves (open or closed, cut at the source's plane), arcs, circles,
  ellipses and centripetal splines sampled to 0.05 mm, planes fitted by least squares with
  patches and angles, flat polygons, volumes with their path lengths and silhouettes, and
  surfaces: triangles through a grid, a height over a plane refined to 0.05 mm, Delaunay
  through scattered points, and the least-squares quadric through points, with each surface's
  area, rims and sag (a concave end-plate's dip below its rim). A surface's shadow is the pixel
  centres inside its projected triangles; one reaching behind the source is refused.
- tests/flexray_record.py recorded tests/fixtures/flexray.json from FleXray 1.0.2 itself on the
  straight L2 to L4 phantom (now with its placed frames, flexray_record.placed);
  tests/test_projection.py holds the copy to it, and its class Shapes draws an ellipse, an arc,
  a closed spline, a patch's outline, a dome and a cap inside the phantom's bodies and finds
  every one on FleXray's support of its body; tests/test_shapes.py holds every shape to its
  geometry on the render, under a cone beam and parallel rays.

## What is verified, and what is not

- Verified: the three modules' 94 tests pass in the plain environment, 3 skipped where FleXray
  and torch are absent, in 82 s (`python -m unittest morphoview.tests.test_projection
  morphoview.tests.test_shapes morphoview.tests.test_lines`), run once on this commit's code
  before it was copied here.
- Not run on this commit: Live, test_projection's class that renders the record's views again
  with FleXray 1.0.2 and torch (both thresholds, the crop and two fresh views of beads); it last
  passed before the shapes, the surfaces and the edits' shift were added.
- Not run at all: mutants over projection.py, shapes.py and the project command's new paths
  (the earlier harness lived in the container and is gone); an adversarial review of this diff.
- morphometry's own suite was not run again; nothing under morphometry/ changed but its
  phantom's frames being read by flexray_record.placed.

## What is left, in order

1. In a container with FleXray 1.0.2 and torch (the environment the record was made in), run
   test_projection with Live and the three modules again; fix what fails.
2. Mutants: a one-token change at a time to projection.py, shapes.py (above all mark_inside's
   slack and sides, refined_grid's stopping rule, Surface.rims, Surface.fit's rank test) and
   __main__.py's edit_shift, realism_view and edits_of; each must fail a test, and a survivor
   gets a test.
3. An adversarial review of this pull request's diff, by correctness, by fitness for PR 45's
   stage 1, and by the tests and the words, written into the pull request's body as its
   "Adversarial review" section; fix what holds up.
4. Merge this pull request once 1 to 3 are done. Then SchwingNet's task (its checkpoint above):
   re-vendor bordercall at the merged commit with morphoview (projection.py, shapes.py and the
   lines), pass --lines in grid/morphometry.sbatch, and the rest that the 17:10 UTC entry below
   lists under "What SchwingNet needs before the counted jobs".
5. Only on the owner's word after the resynthesis: the counted jobs, enhance, verse and the
   covariates join, one at a time, with plots of the old engine against the new.

