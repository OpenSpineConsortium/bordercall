## Summary

The owner asked, at 16:49 UTC on 2026-10-30, that the lines the morphometry export draws be projectable from 3D to 2D natively, surviving FleXray's conversion to a fluoroscopic X-ray, with basic arcs, curves, planes and volumes beside them. This carries the export's ends and frames onto FleXray's renders through FleXray's own camera, held to what FleXray itself renders, and adds shapes that project the same way.

- `morphoview/projection.py`: FleXray 1.0.2's camera as nanoDRR 0.1.5 builds it, in numpy alone: the pose, the intrinsics and one ray a pixel, under nanoDRR's three orientations, cone and parallel beams, and FleXray's 256-pixel canvas. A View is read from a row of SchwingNet's render manifest or from a file of its fields.
- `python -m morphoview project`: lines.csv, and frames.csv where given, onto one render as lines2d.csv, frames2d.csv, column2d.csv and VIEW.json; with the mask the lines were measured on, how far each end and midpoint lies from its level's shadow.
- `morphoview/shapes.py`: arcs, circles, ellipses and centripetal splines, open or closed; planes fitted to points, their angles, meets and patches; flat polygons; volumes from a label map, with each ray's path length through them and their silhouettes.
- `morphoview/tests/flexray_record.py` records FleXray on the L2 to L4 phantom into `tests/fixtures/flexray.json` (84 KB), so the tests need neither torch nor FleXray; the class Live renders again where both are installed.
- The research note's section "Carrying the lines onto FleXray's X-rays" says what each output holds, how a realism render's view is written, and every figure below; the handoff has the entry of this pass.

No real mask or CT was read and no grid job was queued; the morphometry jobs stay held as the owner held them at 14:45 UTC.

## What holds it

- The camera and its rays agree with FleXray's to 5e-13 mm under all three orientations, in FleXray's order of pixels.
- 95 beads rendered by FleXray land within 0.21 px of their projected centres (medians 0.05 to 0.08 px); a camera slipped half a pixel misses by 0.5. A fresh posterior to anterior render on 256 pixels, a view the record does not hold, puts all 95 within 0.16 px.
- Each level's shadow equals FleXray's support of it pixel for pixel in all nine views and levels.
- Every drawn line's ends land within a pixel of its level's shadow, but for Eisenstein's midline places off the lateral view (3 to 7 px) and the discs' midpoints, which lie in the disc space.
- The canvas carries a place where FleXray's resize carries it, to 0.002 px, in eight image sizes.
- The shapes are held to their geometry: curves to their tolerance, a circle through parallel rays to its ellipse's area to 1e-4, a ball's path lengths to its chords and their sum to its volume to 0.005, and FleXray's sampling to nanoDRR's point for point.

MUTANTS_SECTION

## Not done

- The realism programme's manifest names no camera; its view file is written from the row and the recipe, as the note says.
- How far the realism edit moves an edge it redraws is not measured; it would be measured on real renders on the grid, with a count of its own.
- The command has not run on a real render: those are on the grid, and no job is counted for it.
- SchwingNet's copy needs the rest of morphoview and maskedge beside lines.py if `project` is to run on the grid.

## Adversarial review

REVIEW_SECTION

## Test plan

TESTPLAN_SECTION

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Pn5qEJbGG6tvpFq8R3s7FA
