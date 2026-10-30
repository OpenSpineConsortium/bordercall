# Morphometry: the handoff of 2026-10-30, TIMEUTC UTC: the lines carried onto FleXray's X-rays

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5, on
the owner's words of 16:49 UTC: "make sure these lines can be projected from 3D to 2D natively,
surviving a conversion by flexray to a fluroscopic xray, further, there should be basic
functioanlity for non-linear arcs/curves/planes/volumes/ect". They were read as two asks: carry the
lines export's ends and frames onto the X-rays FleXray renders from the same CT, through FleXray's
own camera and held to what FleXray itself renders rather than to a camera of our own; and give
curves, planes and volumes that project the same way. This pass read no real mask or CT and queued
no grid job; the morphometry jobs stay as the owner held them at 14:45 UTC.

## What was built

- morphoview/projection.py: FleXray 1.0.2's camera as nanoDRR 0.1.5 builds it, in numpy alone:
  the pose, the intrinsics and one ray a pixel, under nanoDRR's three orientations (AP, PA and
  none), cone and parallel beams, and FleXray's 256-pixel canvas. A View is read from a row of
  SchwingNet's render manifest (tools/flexray_render.py) or from a file of its fields.
- `python -m morphoview project` carries lines.csv, and frames.csv where it is given, onto one
  render, as lines2d.csv, frames2d.csv, column2d.csv and VIEW.json; given the mask the lines were
  measured on, it also says how far each end and each midpoint lies from its level's shadow. The
  research note's section "Carrying the lines onto FleXray's X-rays" says what each file holds
  and gives both forms of the command.
- morphoview/shapes.py: arcs, circles, ellipses and centripetal splines as curves, open or closed;
  planes fitted to points, with the angle between two, where a line meets one, the angle a render
  sees one at, and their patches; flat polygons; and volumes from a label map, with the length
  each ray runs through them, by a fine sampling or by FleXray's own, and their silhouettes. Each
  is in the world's millimetres and projects through the same camera.
- tests/flexray_record.py records what FleXray does on the L2 to L4 phantom in three views into
  tests/fixtures/flexray.json (84 KB): its camera matrices, its rays, 95 beads' centroids on its
  renders, each level's support and mask, and its canvas in eight image sizes. The tests read the
  record and need neither torch nor FleXray; the class Live renders again where both are
  installed.

## What holds it

The note's section gives every figure. In short: the camera and its rays agree with FleXray's to
5e-13 mm under all three orientations; 95 beads rendered by FleXray land within 0.21 px of where
the camera projects them (medians 0.05 to 0.08 px), where a camera slipped half a pixel misses by
0.5; a fresh posterior to anterior render on 256 pixels, a view the record does not hold, puts all
95 within 0.16 px; each level's shadow equals FleXray's support of it pixel for pixel in all nine
views and levels; every drawn line's ends land within a pixel of its level's shadow, but for the
places Eisenstein's lateral construction puts at the midline, which are on the shadow in the
lateral view and 3 to 7 px off it in the other two, and the discs' midpoints, which lie in the
disc space; the canvas carries a place where FleXray's resize carries it, to 0.002 px. The shapes
are held to their geometry: each curve to its tolerance, a circle seen through parallel rays to
its ellipse's area to 1e-4, a ball's path lengths to its chords and their sum to its volume to
0.005, and FleXray's sampling to nanoDRR's, point for point.

## The mutants

48 deliberate faults, each applied alone to a copy of the code and both suites run on it, are all
caught. 19 are in the camera: the rotations taken in the wrong order, the translation left
unturned, each orientation's turn changed, the principal point put at a pixel's corner, the
pixel's height or the principal point's row read from its width, a parallel beam taken for a cone,
a beam run on past the detector, the pixels taken column by column, a parallel beam's source put
at the origin, a ray cast through a pixel's corner, the magnification inverted, the canvas's pads
swapped, halved or taken off, and a manifest read as a cone always or without its isocentre. 17
are in the shapes: the nearest voxel taken by floor, nanoDRR's window of samples cut too narrow,
its step taken over n points rather than n - 1, arcs drawn too coarse, splines left unrefined or
made uniform or chordal, a ring the source's plane cuts left unjoined or cut at its middle, a
plane's normal taken from the wrong singular vector, the angle a render sees a plane at taken by
its cosine, a patch's area doubled, the first piece kept in place of the largest, a footprint
shrunk, an image transposed, a circle left open and an arc turned the left-handed way. 12 are in
the command: a disc's shadow taken from one vertebra, a pixel's row and column swapped, the b end
taken from the a end, the ray's samples not the view's, a manifest's detector misread, a frame's
axes swapped, the column reversed, the canvas of an image whose height and width are swapped, the
main piece's shadow alone, the midpoint put at an end, the record's hash of another file and the
magnification inverted. The uniform spline was added on reading the spline's test, which built its
reference from the module's own span and so would have let it live; a test that holds the spline
to the same spans written independently in Hermite form now catches it. Two faults were left out
as ones no output can show: dropping the slab test's refusal of a ray that runs parallel to a face
outside the box, which only reads points that are not the volume's, and sampling each fine step at
its start rather than its middle, which moves a path length by less than the step the tests allow.

## Not done, with the reason

- The realism programme's manifest (tools/realism.py) names no camera, so its view file is written
  from the row and the recipe, as the note says; a reader for that manifest is a change to
  SchwingNet.
- How far the realism edit moves an edge it redraws is not measured. FleXray's segmentation of the
  edited image set against the render's shadow would measure it, on real renders on the grid, with
  a count of its own.
- The command has not run on a real render: the renders and masks are on the grid, and no job is
  counted for it.
- SchwingNet's copy of the engine, once re-pinned with morphoview/lines.py for `run --lines`,
  needs the rest of morphoview beside it (__main__.py, projection.py, render.py and shapes.py)
  and maskedge, which morphoview/__main__.py imports, if `project` is to run on the grid; none of
  it needs more than numpy and scipy beyond the engine.

## Tests and timing

- morphoview/tests/test_projection.py, 29 tests, and morphoview/tests/test_shapes.py, 17, with
  morphoview's own test_lines, 11: the 57 pass in 61 s on four CPUs in bordercall's environment,
  the two of Live skipped there since it has no FleXray. In an environment with FleXray 1.0.2,
  nanoDRR 0.1.5 and torch 2.15.0 on the CPU, Live renders the three views again and a fourth,
  posterior to anterior, and passes; test_lines' one figure test cannot run there, for want of
  matplotlib.
- The engine's measuring code is untouched: morphometry, scanimport and morphoview/lines.py, which
  a run's stamp covers, are as main has them, so a run's stamp and the export's tests are as they
  were.
- On the phantom `project` takes 2 to 4 s a view with the mask, most of it the shadows (0.3 to
  0.6 s a level).

