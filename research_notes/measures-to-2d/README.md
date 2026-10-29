# Which of the 106 measures survive projection onto an X-ray: the 3-D construction, the 2-D fate, the magnification

Source: the thread "Build the auto-anatomist on raw CT", 29 October 2026, for the owner's asks of 14:59 UTC ("can you start looking for what techniques you are using for calculating morphometrics that the bayesian generator uses to predict in 3d that translates to 2d xray?"), 15:16 UTC (corners and landmarks come from the CT morphometry engine's constructions projected, never from XRSpinoPelvic1K's 2-D corner fit) and 15:18 UTC (all the distinct measures of the clinical reread, not Panjabi's 32). Confidential with the rest of this repository.

What a row rests on: the measure's definition in paper-tables/tools/vocabulary.csv and its recipes in clinical-reread/synthesis/measures.md (the (b) mask recipe and the (c) radiograph recipe, with section 2.5's magnification, 1.14 AP and 1.23 lateral at 110 cm after Eisenstein); the engine's construction as the morphometry thread's draft (bordercall PR 30, branch claude/project-thread-6o9umj, the modules anatomy, body, column, canal, pedicle, posterior, pelvis, measure and morphoview.lines) builds it, named by module and function; and the projection rules of autoanatomist/project.py (a length keeps its value across the beam and foreshortens along it, an angle is read in a plane the beam lies in within 15 degrees, an area in a plane square to the beam within the area factor 0.9, a detector length is the object length times the magnification sdd / depth). How it was made: four drafting passes, one per group below, each reading those three sources; the checking pass that was to refute each row did not run (the account's limit), so every row is one reading, unverified, and the groups not drafted are listed at the end with their keys. The checkpoint of 17:27 UTC kept the rows rather than lose them.

Rules that hold over every row: the magnification enters a length as a factor of M, an area as M squared and an angle not at all, so a ratio of two lengths in one plane cancels it, and a rule fed projected lengths either widens its size prior by the magnification's spread or carries a magnification latent; the geometric rules say which measurements a view can carry at all, and which it carries well is for the measured study (the paired CT and FluXray design in SchwingNet's handoff), never for a rule.

## End-plates

### endplate (length, mm, EPWu)

Definition (vocabulary.csv): upper end-plate width: the distance between the lateral ends of the superior end-plate
The 3-D construction (in the engine): morphoview.lines.panjabi_plates draws it as a line along x between the two lateral surfaces (scanimport.geometry.surface) of Panjabi's upper plate slab, lines.plate_slabs by scanimport.geometry.plate (the body's points within 1 to 3 mm of the plane scanimport.geometry.plate_plane rests on the highest central cells), at the slab's median y and z, and the value is anatomy.panjabi_body's by scanimport.geometry.body_chords, the slab's x extent in the vertebra's frame. The engine drops no uncinate process, so at C3 to C7 the upper width keeps the unci that recipe 3.1b step 4 removes and reads high as 3.1 warns.
AP view: A chord along x lies across the AP beam (y) and keeps its length, and the engine's two projected ends are the lateral corners of the plate line, read between them and divided by the AP magnification (1.14 at 110 cm tube to film, 3.1c); 3.6 adds that the pipeline must read the plate line and not the waist, which the AP silhouette shows most clearly. Visibility by 3.1c: the upper and lower plates superimpose unless the beam is parallel to the disc, which a cone beam gives only at the central ray (project.py's Camera.beam gives each point its own ray).
Lateral view: The chord runs along the lateral beam (x) and keeps nothing of itself, both ends falling on the body's one outline; recipe 3.1c says a lateral view cannot give the width.
Oblique view: At 45 degrees a chord along x keeps cos 45 = 0.71 of itself, under the projector's floor of 0.9, so the width is not readable and the recipes name no oblique form; in geometry only its ratio to another chord along x in the same view, such as TPW over EPWu, survives, both shortening alike.
Magnification-free form: TPW over EPWu on one AP view (9.2, 11.9: from Panjabi's tables 3.18 at C3, 1.20 at T12, 1.73 to 1.96 at L1 to L5); width over depth (3.1d) is size-free but needs both views, each divided by its own M first (3.1c).
Readability: AP
Sources: measures.md 2.2, 2.4 (O1), 2.5, 3.1 (a) to (d), 3.6, 9.2, 11.1, 11.9; anatomy.panjabi_body, scanimport.geometry.body_chords, plate, plate_plane, surface, extent, lines.plate_slabs, lines.panjabi_plates; project.py FORESHORTENING_FLOOR, Camera.beam.

### endplate_depth (length, mm, EPDu)

Definition (vocabulary.csv): upper end-plate depth: the anteroposterior extent of the superior end-plate
The 3-D construction (in the engine): morphoview.lines.panjabi_plates draws it as a line along y at the body's mid x, from the canal's anterior wall line (anatomy.body_in_front's wall_y0, the body's posterior wall squared to that line by anatomy.square_to_wall) to the anterior surface of the same upper plate slab at the slab's median z, and the value is anatomy.panjabi_body's by scanimport.geometry.body_chords, the slab's front surface less the wall. It is read over the whole slab and not the 3 mm midline band of recipe 3.2b, so a posterolateral lobe can set the front; the film's landmarks exist too: column.wall_corner gives the posterior corner where the wall meets the plate on the midline, and body.plate_rims with body.rim_plane (lines.plate_line) the plate rim to rim 2.5 mm inside each corner.
AP view: A chord along y runs along the AP beam and keeps nothing of itself, both ends on one point of the outline; recipe 3.2c gives the depth to the lateral view only.
Lateral view: A chord along y lies across the lateral beam (x) and keeps its length: the plate line from its anterior to its posterior corner (gilad1985's P1 and P2, 3.2a), the engine's posterior end at the wall line and column.wall_corner at the corner itself, divided by the lateral magnification (1.23 at 110 cm, 3.2c), which brought corrected living films within about 1 mm of Panjabi's lumbar depths. Visibility by 3.2c: the beam must be tangent to the plate, and a double contour means it is not.
Oblique view: At 45 degrees a chord along y keeps 0.71 of itself, under the 0.9 floor, so the depth is not readable and the recipes name no oblique form; in geometry only its ratio to another chord along y in the same view holds.
Magnification-free form: SPL over EPDu on one lateral view (9.1, 11.9: 1.97 at C3, 2.71 at T1, 1.43 at T11, about 2.0 from L1 to L5); width over depth (3.1d) needs both views corrected.
Readability: lateral
Sources: measures.md 2.2, 2.4 (O1), 2.5, 3.2 (a) to (d), 9.1, 11.1, 11.9; anatomy.panjabi_body, anatomy.body_in_front, anatomy.square_to_wall, scanimport.geometry.body_chords, surface, lines.plate_slabs, lines.panjabi_plates, lines.plate_line, column.wall_corner, body.plate_rims, body.rim_plane; project.py FORESHORTENING_FLOOR.

### endplate_lower (length, mm, EPWl)

Definition (vocabulary.csv): lower end-plate width: the distance between the lateral ends of the inferior end-plate
The 3-D construction (in the engine): As endplate on the lower plate: lines.panjabi_plates draws the line between the lateral surfaces of the slab scanimport.geometry.plate cuts above the plane resting on the lowest central cells, and the value is scanimport.geometry.body_chords' x extent of that slab in anatomy.panjabi_body. The engine's body is cut only at the canal's wall line (anatomy.body_in_front) and at the foramina in the neck (anatomy.clip_to_foramina), so at T1 a rib head the label joins to the body stays in the slab, which 11.1 warns reads wide.
AP view: A chord along x across the AP beam keeps its length, its projected ends the lateral corners of the lower plate line, divided by 1.14 (3.1c); the lower line lies under the upper's and the two superimpose unless the beam is parallel to the disc (3.1c), so a cone beam shows them apart only at the level on the central ray.
Lateral view: Along the lateral beam, so nothing of it survives and both ends fall on the outline; 3.1c says a lateral cannot give the width.
Oblique view: Not readable at 45 degrees (0.71 of itself, under the 0.9 floor); only a ratio to another chord along x in the same view holds in geometry, and the recipes name none for the lower plate.
Magnification-free form: lower width over lower depth (EPWl over EPDl), the most regular lumbar gradient (1.23 at L1 to 1.49 at L5, 0.07 to 0.08 per level to L4) and 1.19 to 1.39 from C6 to C7 (3.1d); it needs both views, each corrected for its own M (3.1c).
Readability: AP
Sources: measures.md 2.2, 2.4 (O1), 2.5, 3.1 (a) to (d), 11.1; anatomy.panjabi_body, anatomy.body_in_front, anatomy.clip_to_foramina, scanimport.geometry.body_chords, plate, surface, extent, lines.plate_slabs, lines.panjabi_plates; project.py FORESHORTENING_FLOOR.

### endplate_lower_depth (length, mm, EPDl)

Definition (vocabulary.csv): lower end-plate depth: the anteroposterior extent of the inferior end-plate
The 3-D construction (in the engine): As endplate_depth on the lower plate: lines.panjabi_plates draws it from the canal's wall line to the lower slab's anterior surface at mid x, the value scanimport.geometry.body_chords' front surface less the wall in anatomy.panjabi_body, over the whole slab rather than recipe 3.2b's midline band. column.wall_corner(v, False) gives the posterior-inferior corner, the one column.slip sets against the next plate as Meyerding did, and lines.plate_line the lower plate rim to rim.
AP view: Along the AP beam, so nothing of it survives; 3.2c names the lateral only.
Lateral view: Across the lateral beam it keeps its length: the lower plate line from its anterior to its posterior corner (gilad1985's chord a, P3 to P4, 3.2a), divided by 1.23 (3.2c), with the posterior-inferior corner from column.wall_corner. Visibility by 3.2c: a tangent beam, and a double contour means the plate is not tangent; 3.2d adds that the lower depth alone separates no lumbar level.
Oblique view: Not readable at 45 degrees (0.71 of itself, under the 0.9 floor); in geometry only a ratio to another chord along y in the same view holds.
Magnification-free form: lower width over lower depth (3.1d), across the two views; the recipes name no single-view ratio for the lower depth, SPL being set against the upper depth (9.1).
Readability: lateral
Sources: measures.md 2.2, 2.4 (O1), 2.5, 3.2 (a) to (d), 11.1; anatomy.panjabi_body, scanimport.geometry.body_chords, surface, lines.panjabi_plates, lines.plate_line, column.wall_corner, column.slip, body.plate_rims, body.rim_plane; project.py FORESHORTENING_FLOOR.

### endplate_area (area, mm2, EPAu)

Definition (vocabulary.csv): upper end-plate surface area
The 3-D construction (in the engine): morphometry.body.plate_area: the area of the body's section parallel to the upper plate from voxel counts, N voxels in a slab 2 mm thick (or one voxel's shadow on the plate's normal if more) starting half a millimetre deeper than body.concavity's depth, times a voxel's volume over the slab's thickness, the plate's plane being scanimport.geometry.plate_plane resting on the highest cells of body.plate_core; nothing in morphoview draws it. It is a section a few millimetres inside the rim, where a waisted body is already narrower, not the rim loop's vector area of recipe 3.4b (O2), and it drops no unci at C3 to C7.
AP view: The plate's normal is z, square to the AP beam (y), so the face shows edge on as the plate line and its area factor |n.r| is 0, under the projector's floor of 0.9. Recipe 3.4c says the area is not measurable on a film; the ellipse pi x EPW x EPD / 4 from an AP width and a lateral depth stands in, 1.7 to 19 per cent high against Panjabi and 12 to 16 per cent low against tan2004's lumbar plates, so 11.1 says never to substitute it.
Lateral view: The same, edge on to the lateral beam (x) with area factor 0; the view gives only the plate's depth for the stand-in ellipse (3.4c).
Oblique view: Edge on to every beam in the transverse plane, area factor 0 at any alpha; even FleXray's steepest tilt of the beam up the column (beta 30 degrees) shows sin 30 = 0.5 of the face, under the 0.9 floor, so no plain view shows an end-plate face on.
Magnification-free form: none: an area scales by M squared (2.5), 3.4c names no ratio, and the ellipse stand-in carries each view's own M.
Readability: CT only
Sources: measures.md 2.1 (the vector area), 2.4 (O1, O2), 2.5, 3.4 (a) to (c), 11.1; body.plate_area, body.plate_core, body.concavity, scanimport.geometry.plate_plane; project.py area_factor, AREA_FACTOR_FLOOR, FLEXRAY_BETA_DEG.

### endplate_lower_area (area, mm2, EPAl)

Definition (vocabulary.csv): lower end-plate surface area
The 3-D construction (in the engine): morphometry.body.plate_area with top False: the body's section parallel to the lower plate from voxel counts in a 2 mm slab that starts half a millimetre above the lower plate's concavity, its plane scanimport.geometry.plate_plane resting on the lowest cells of body.plate_core; no line draws it. Like the upper, it is a section inside the rim and not recipe 3.4b's vector area of the rim loop, with no unci dropped.
AP view: Normal along z, edge on to the AP beam, area factor 0: not measurable on a film (3.4c), the ellipse from EPWl and EPDl standing in with the biases 3.4c lists; 3.4d adds that Panjabi's lower area is not monotone, peaking at C6 and L3.
Lateral view: Edge on to the lateral beam, area factor 0; the lateral gives only EPDl for the stand-in (3.4c).
Oblique view: Area factor 0 at any alpha, and 0.5 at most under FleXray's largest beta, under the 0.9 floor; no plain view shows it face on.
Magnification-free form: none: the area scales by M squared (2.5) and 3.4c names no ratio.
Readability: CT only
Sources: measures.md 2.1, 2.4 (O1, O2), 2.5, 3.4 (a) to (d), 11.1; body.plate_area, body.plate_core, body.concavity, scanimport.geometry.plate_plane; project.py area_factor, AREA_FACTOR_FLOOR, FLEXRAY_BETA_DEG.

### endplate_incl (angle, deg, EPItu)

Definition (vocabulary.csv): upper end-plate inclination to the transverse plane
The 3-D construction (in the engine): morphometry.body.inclinations: the angle of the upper plate's rim-to-rim line (body.rim_plane's front-to-back slope, the line through the plate's surface in the bands 2.5 mm inside its anterior and posterior corners, body.plate_rims and body.band_surface) against the transverse plane square to the posterior wall (body.posterior_wall_slope, the wall's midline slope over the middle 60 per cent of its height), signed, positive where the plate descends anteriorly; morphoview.lines.plate_line gives that line's two world ends and lines.wedge draws it as the wedge's upper line. It is the sagittal part only, where Panjabi's EPItu is the unsigned angle between the plate's plane and the transverse plane, mixing sagittal and coronal tilt (3.5a, b); rim_plane's across slope holds the coronal part but inclinations does not report it.
AP view: A sagittal angle lies in a plane whose normal (x) is square to the AP beam, so the plane is seen edge on (plane tilt 90 degrees, past the projector's 15 degree limit) and the AP keeps none of it; what the AP plate line shows is the plate's coronal tilt, the other part of Panjabi's unsigned angle, which the recipes do not read (3.5c names the lateral only).
Lateral view: The sagittal plane faces the lateral beam (plane tilt 0), so the angle keeps its value: the angle between the projected plate line and the perpendicular to the posterior body line, the sagittal part only (3.5c), with no magnification correction. The engine's plate line and the posterior wall project as the two lines a reader draws; 3.5c has only the angle between the two plates checked on film (3.9 degrees against 3.8 on bone on ten lateral films) and no per-level statistic.
Oblique view: At 45 degrees the sagittal plane leans 45 degrees off the detector, past the 15 degree limit, so the angle is not readable; nothing of the inclination holds in an oblique and the recipes name none.
Magnification-free form: the angle itself, which magnification does not change (2.5, 3.5c); no ratio named.
Readability: lateral
Sources: measures.md 2.1, 2.2, 2.5, 3.5 (a) to (d), 11.1, 11.8, 12 (Panjabi's lumbar rows of this angle reprint his cervical rows, kept in the pool as printed by the owner's choice of 2026-10-29); body.inclinations, body.rim_plane, body.plate_rims, body.band_surface, body.posterior_wall_slope, lines.plate_line, lines.wedge; project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

### endplate_lower_incl (angle, deg, EPItl)

Definition (vocabulary.csv): lower end-plate inclination to the transverse plane
The 3-D construction (in the engine): morphometry.body.inclinations with top False: the lower plate's rim-to-rim line (body.rim_plane from body.plate_rims' bands 2.5 mm inside the posterior and anterior corners) against the plane square to the posterior wall (body.posterior_wall_slope), signed, positive where the plate descends anteriorly, its ends from lines.plate_line and drawn by lines.wedge as the extra line 'lower plate'. Sagittal part only, where Panjabi's EPItl is the unsigned angle between planes (3.5a, b); the coronal part is in rim_plane's across slope and is not reported.
AP view: The sagittal plane is edge on to the AP beam (plane tilt 90 degrees), so nothing of it survives; the AP line's tilt is the coronal part, which the recipes do not read (3.5c).
Lateral view: Faces the lateral beam (plane tilt 0): the angle between the lower plate line and the perpendicular to the posterior body line, sagittal part only, no magnification correction (3.5c). At L5 the same-definition series read 10.5 to 12 degrees against Panjabi's printed 1.8 (3.5d, 11.1), so a lateral reading there is not scored against his row.
Oblique view: Not readable: the plane leans 45 degrees, past the 15 degree limit, and the recipes name no oblique form.
Magnification-free form: the angle itself; no ratio named (2.5, 3.5c).
Readability: lateral
Sources: measures.md 2.1, 2.2, 2.5, 3.5 (a) to (d), 11.1, 11.8, 12 (the lumbar rows reprint the cervical rows); body.inclinations, body.rim_plane, body.plate_rims, body.band_surface, body.posterior_wall_slope, lines.plate_line, lines.wedge; project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

### endplate_wedge (angle, deg, EPIt)

Definition (vocabulary.csv): wedge angle: the sum of the upper and lower end-plate inclinations to the transverse plane, printed by the thoracic paper as a mean with no standard error
The 3-D construction (not in the engine yet): not in the engine: recipe 3.5b takes it as the sum of the two unsigned plane angles EPItu + EPItl, as Panjabi printed it for T1 to T12 with no spread, beside the frame-free angle between the two plates it calls the robust quantity. The engine's body.inclinations gives both inclinations signed and sagittal only, and its wedge key is their signed difference (lines.wedge draws it); the sum of their magnitudes follows from those two values but no function computes it, and it would carry the sagittal parts alone.
AP view: Its two parts are sagittal angles whose plane is edge on to the AP beam, so the AP keeps none of it; the AP plate lines show the coronal tilts instead, which the printed sum mixes in but the recipes do not read (3.5c).
Lateral view: Both plate lines lie in the sagittal plane facing the lateral beam, so each inclination keeps its value and so does their sum, the sagittal part only (3.5c), with no magnification correction. The printed thoracic value is a sum of magnitudes, so a lateral reading must add the two magnitudes and not take the signed angle between the plates that the lateral shows at once.
Oblique view: Not readable: both planes lean 45 degrees, past the 15 degree limit.
Magnification-free form: the angle itself; no ratio named (3.5c).
Readability: lateral
Sources: measures.md 3.5 (a) to (d), 11.1; body.inclinations, lines.wedge, lines.plate_line; project.py PLANE_TILT_MAX_DEG.

### wedge (angle, deg)

Definition (vocabulary.csv): body wedge angle: the angle between the upper and lower end-plates in the sagittal plane
The 3-D construction (in the engine): morphometry.body.inclinations (key wedge): the signed angle in the sagittal plane between the two plates' rim-to-rim lines (body.rim_plane on each plate, from body.plate_rims' bands 2.5 mm inside the corners), the upper line's slope less the lower's, positive where the body is taller in front; morphoview.lines.wedge draws it as the upper plate's line (lines.plate_line) with the lower plate's line as its extra line, rule 'angle'. It needs no wall: the angle between the two lines is frame free, which the reread calls the robust quantity (3.5b).
AP view: A sagittal angle, so the AP sees its plane edge on (plane tilt 90 degrees) and keeps none of it; the angle the AP shows between the two plate lines is the coronal wedge, a different quantity the recipes do not name for this key.
Lateral view: The sagittal plane faces the lateral beam (plane tilt 0), so the angle between the two projected plate lines is the wedge itself, free of magnification; 3.5c read it on ten lateral films at 3.9 degrees against 3.8 on bone, and 3.3d sets its lumbar course by the heights, about -3.5 degrees at L1 (taller behind) to +5.1 at L5 (taller in front). Visibility as for the plate lines: each needs a tangent beam, and a double contour spoils the line (3.2c).
Oblique view: Not readable: the plane leans 45 degrees, past the 15 degree limit; in geometry its sign survives only through the anterior over posterior height ratio, since heights along z keep their length in any oblique.
Magnification-free form: the angle itself; its sign is carried by the anterior over posterior height ratio of 3.3 and 11.9 (only L5 taller in front by 10 per cent or more), a ratio of two heights in one lateral view.
Readability: lateral
Sources: measures.md 3.3 (c), (d), 3.5 (b), (c), 11.9; body.inclinations, body.rim_plane, body.plate_rims, lines.wedge, lines.plate_line; project.py PLANE_TILT_MAX_DEG.

### endplate_concavity (length, mm)

Definition (vocabulary.csv): end-plate concavity depth (upper, lower or which, in the note)
The 3-D construction (in the engine): morphometry.body.concavity (keys endplate_concavity for the upper plate and endplate_lower_concavity for the lower): the plate's cells' extremes (body.plate_extremes, body.plate_cells) are ringed by their distance from the plate's centre as a share of its half-width and half-depth, a plane is fitted to the ring between 85 and 95 per cent (body.plane_robust), and the depth is the median of how far the centre cells (within 25 per cent) lie below that plane along z, a plane and a point rather than a line, which morphoview does not draw. It is the depth at the centre, where recipe 4b asks for the largest perpendicular depth on the midsagittal and frontal lines through the deepest point, its position from the posterior rim as a share of the depth, and chen2011's angle A-Cm-P; the engine gives the depth alone.
AP view: The depth is a chord along z, the plate's normal, across the AP beam, so it keeps its length: the dip of the plate line below the chord joining its lateral corners, the frontal profile of 4c (vanderhouwen2009's frontal points, chen2011's coronal angle R-Cs-L of 170.9 to 175.7 degrees, 4d). Visibility by 4c: double contours and tilt spoil it; the dip is 1 to 3 mm, which 4b asks 0.75 mm voxels for and which a stored FluXray pixel of 2.4 mm (0.6 mm on 1024 stored at 256, project.py) does not resolve.
Lateral view: The same chord along z keeps its length across the lateral beam: the dip of the plate line below the chord joining its anterior and posterior corners, the sagittal profile of 4c, largest in the middle or posteriorly with the inferior plate deeper than the superior across every lumbar disc (4d); a true lateral is needed since double contours and tilt spoil it (4c), and 4f warns that CT depths run about 1 to 1.7 mm deeper than X-ray and MRI depths at the caudal plates, so a film's dip is compared only with film values.
Oblique view: In geometry the chord along z keeps its length under any alpha, but the rim line it is read against is the plate's outline seen from 45 degrees, so the profile sampled lies between the sagittal and the frontal ones that 4c names and no series measured it; the share of the depth and the angle A-Cm-P keep their definition only in the view they were defined in.
Magnification-free form: the deepest point's position as a share of the plate's depth and the sagittal angle A-Cm-P (4b; chen2011 about 163 degrees from T10 to L3, 4d), and busscher2010's central over mean marginal height (4d), each a ratio or angle of one lateral view; the depth itself scales by M.
Readability: both
Sources: measures.md 2.4 (O1), 4 (a) to (f), 11.9; body.concavity, body.plate_cells, body.plate_extremes, body.plane_robust; project.py FORESHORTENING_FLOOR, FLUXRAY_PIXEL_MM, FLUXRAY_DETECTOR_PX, FLUXRAY_STORED_PX.

## The body and the discs

### h_post (length, mm, VBHp)

Definition (vocabulary.csv): posterior vertebral body height: the distance between the end-plates at the posterior wall
The 3-D construction (in the engine): anatomy.panjabi_body calls scanimport.geometry.body_chords, which keeps the body voxels within the posterior fifth of the body's depth behind the canal's wall line and the central half across, and scanimport.geometry.column_height takes the median over a grid of cells of each cell's height along z, surface to surface; body.py's docstring says this Panjabi value passes through unchanged. The line morphoview draws for the posterior height is the inset one (body.heights h_post_inset, lines.heights): from the lower plate's band surface to the upper plate's, each band 3 by 6 mm on the midline 2.5 mm inside that plate's own posterior corner (body.plate_rims, body.band_surface), corner to corner; column.wall_corner is the engine's posterior corner, where the wall meets the plate on the midline.
AP view: A chord along z lies across an AP beam and keeps its length, but the recipe's judgment is that the posterior wall is not seen apart from the rest of the body on an AP view, and that an AP height equals h_post only when the beam is parallel to both plates (3.3 c, 11.1); the plates also superimpose unless the beam is parallel to the disc (3.1 c). So the AP has no landmark for it.
Lateral view: Along z, across the beam: the posterior wall from end-plate to end-plate, its two corners the 2-D ends, divided by the lateral magnification (1.23 at 110 cm, 2.5, 3.3 c). At C3 to C7 the lateral reads 1.8 to 3.0 mm above the midsagittal height because the uncovertebral region projects above the midline (3.3 c), and projected lumbar heights ran 3 to 5 mm above Panjabi (3.3 a).
Oblique view: The beam stays in the axial plane at every alpha (project.py), so a z chord keeps its whole length, above the 0.9 floor. Whether the posterior corners can be seen over the pedicle and arch in a 45-degree view is not judged by any recipe, so geometry holds and visibility is open.
Magnification-free form: anterior over posterior height (VBHa/VBHp, 3.3 c and d, 11.9), and VBHm/VBHp (3.3 d): two z chords on one lateral, M cancelling.
Readability: lateral
Sources: measures.md 2.2, 2.5, 3.1 (c), 3.3 (a)(b)(c)(d), 11.1, 11.9; anatomy.panjabi_body, scanimport.geometry.body_chords, scanimport.geometry.column_height, body.heights, body.plate_rims, body.band_surface, column.wall_corner, lines.heights; project.py View, FORESHORTENING_FLOOR.

### h_ant (length, mm)

Definition (vocabulary.csv): anterior vertebral body height: between the end-plates at the anterior wall
The 3-D construction (in the engine): body.heights: the distance between the two plates' band surfaces at the bands set 2.5 mm inside each plate's own anterior corner on the midline (body.plate_rims gives the band's y, body.band_surface reads the plate there along the plate's slope), taken corner to corner as the hypotenuse of the z gap and the y offset; lines.heights draws it as a sagittal line between those two world points.
AP view: A z chord keeps its length across an AP beam, but the AP does not tell the anterior wall from the posterior: the recipe says an AP height equals a height at a wall only when the beam is parallel to both plates (3.3 c) and the plate lines superimpose otherwise (3.1 c). So the AP gives an undifferentiated body height, not h_ant.
Lateral view: Along z, across the beam: between the anterior corners of the two plate lines, the front ends of the lines 3.2 (c) draws, divided by 1.23 (2.5). The recipe's lateral part names no anterior-specific bias; on contact films the intra-observer error for body heights was 1.7 to 5.1 percent (3.3 c).
Oblique view: A z chord keeps its length at any alpha, so it passes the floor; the anterior corners stay at the front of the silhouette in a 45-degree view, but no recipe gives an oblique verdict.
Magnification-free form: anterior over posterior height (VBHa/VBHp; body.heights body_index_ant_post), the set's strongest single L5 marker (3.3 d, 11.9); also VBHm/VBHa (3.3 d).
Readability: lateral
Sources: measures.md 2.5, 3.1 (c), 3.2 (c), 3.3 (b) step 5, (c), (d), 11.9; body.heights, body.plate_rims, body.band_surface, lines.heights.

### h_mid (length, mm)

Definition (vocabulary.csv): middle (central) vertebral body height: between the end-plates at the body's centre
The 3-D construction (in the engine): body.heights: the same two band surfaces read at the band half-way between each plate's posterior and anterior rim bands on the midline (body.plate_rims, body.band_surface), corner-inset, so it is the plate-to-plate distance at the body's centre; lines.heights draws it. The dip it carries against the rim line is read separately by body.concavity.
AP view: A z chord across the beam keeps its length, and the body's centre lies inside the silhouette; what shows of each plate's centre is the frontal profile's dip below the rim line, which section 4 (c) admits for an AP as an inference and warns that tilt and double contours spoil. The heights recipe itself (3.3 c) names no AP.
Lateral view: Along z, across the beam: the two plates' sagittal profiles at the body's centre, each the dip below the line joining its anterior and posterior corners on a true lateral (4 c); busscher2010's central height was read on a lateral reformat (3.3 a, d). Divide by 1.23 (2.5); a beam not tangent to the plate gives a double contour.
Oblique view: A z chord keeps its length at any alpha. The reading needs a plate profile seen with a tangent beam, which a 45-degree view does not give, and no recipe judges it.
Magnification-free form: VBHm/VBHa and VBHm/VBHp (3.3 d; body.heights body_index_mid_post); the central over mean marginal height (4 d). Each is two z chords on one view.
Readability: both
Sources: measures.md 2.5, 3.3 (a)(b) step 5, (c), (d), 4 (b)(c)(d); body.heights, body.plate_rims, body.band_surface, body.concavity, lines.heights.

### h_lat (length, mm)

Definition (vocabulary.csv): lateral vertebral body height (right, left or their mean), between the end-plates at the side wall
The 3-D construction (not in the engine yet): not in the engine: body.heights reads its bands only on the midline (within 3 mm of the body's centre x) and scanimport.geometry.column_height only the central half across, so no function reads a height at the side wall; 3.3 (b) step 4 prescribes recording the heights at the left and right posterior corners as well, and by the same recipe a lateral height is the column extent along frame F's Y in a band at the body's lateral rim, one per side or their mean.
AP view: A z chord across the beam keeps its length, and the side walls are what an AP shows: the lateral corners of the upper and lower end-plate lines (3.1 c's landmarks) are its two ends, divided by 1.14 (2.5). The plates superimpose unless the beam is parallel to the disc (3.1 c), and an AP height is a wall's height only when the beam is parallel to both plates (3.3 c). The 2-D corner format carries the four AP corners (scanimport.radiograph), though its importer takes only widths from an AP.
Lateral view: Along z, but both side walls superimpose on each other and on the midline, so the lateral cannot tell a side-wall height from the posterior or anterior one; in the neck the uncovertebral region projects above the midline (3.3 c).
Oblique view: A z chord keeps its length; a 45-degree view separates the near from the far side wall, but no recipe judges what is seen there.
Magnification-free form: none
Readability: AP
Sources: measures.md 2.5, 3.1 (c), 3.3 (b) step 4, (c); body.heights, scanimport.geometry.column_height, scanimport.radiograph.corner_chords.

### body_w_mid (length, mm)

Definition (vocabulary.csv): vertebral body width at mid-height (the waist), transverse
The 3-D construction (in the engine): body.waist on body.mid_slab: the slab of body points within a voxel of the level half-way between the two plate planes at the body's middle, and the width the extent along x (scanimport.geometry.extent) of the slab's points in a band about its mid-depth; lines.waist draws it as a coronal line at the slab's median z. Its own docstring warns that the slab takes in the transverse processes where they spring from the body, 76 mm at one L5.
AP view: Along x, across an AP beam, so it keeps its length: the narrowest waist between the body's side walls, which was read on AP films at 100 cm uncorrected (3.6); divide by 1.14 (2.5). The recipe says a waist is what an AP shows most clearly, so a radiograph pipeline measures the plate lines or carries a separate waist reference, and never pools a waist with an end-plate width (3.6, 3.1 a, 11.1).
Lateral view: Along the lateral beam, foreshortened to nothing; a lateral view cannot give a width (3.1 c).
Oblique view: An x chord keeps cos 45, 0.71, under the 0.9 floor; nothing of it holds.
Magnification-free form: the Jones and Thomson canal index (measure.derived canal_index_jones: canal_ap_min times interpedicular_max over body_d_mid times body_w_mid), an AP pair over a lateral pair with each view's M cancelling in its pair; width over depth needs both views each corrected first (3.1 c).
Readability: AP
Sources: measures.md 2.5, 3.1 (a)(c), 3.6, 11.1; body.waist, body.mid_slab, lines.waist, measure.derived, scanimport.geometry.extent.

### body_d_mid (length, mm)

Definition (vocabulary.csv): vertebral body depth at mid-height (the waist), anteroposterior, midline
The 3-D construction (in the engine): body.waist: in the midline band of the mid slab (body.mid_slab), the surfaces of the points' y (scanimport.geometry.surface) from the posterior to the anterior surface; lines.waist draws it as a sagittal line at the slab's median z.
AP view: Along y, along the AP beam, so it is lost; an AP gives no depth.
Lateral view: Along y, across the beam: the body's anterior surface and its posterior cortex at mid-height, the cortex that is the anterior limit of the canal depth on a lateral (6.1 c); divide by 1.23 (2.5). A waist depth runs 1 to 5 mm below the end-plate depth and is never fed to EPD (3.2 a, 3.6).
Oblique view: A y chord keeps 0.71, under the floor; nothing holds.
Magnification-free form: canal over body, the Torg ratio (6.1 c; measure.derived canal_index_torg = canal_ap / body_d_mid), two y chords on one lateral; and the Jones index.
Readability: lateral
Sources: measures.md 2.5, 3.2 (a), 3.6, 6.1 (c); body.waist, body.mid_slab, lines.waist, measure.derived.

### body_w (length, mm)

Definition (vocabulary.csv): vertebral body width where the paper does not say upper, lower or mid-height
The 3-D construction (not in the engine yet): not in the engine as a key of its own: no function emits an unspecified width. The engine's widths are the end-plate widths, the extent along x of the top or bottom slab (anatomy.panjabi_body through scanimport.geometry.body_chords; lines.panjabi_plates draws them), and the waist (body.waist); 3.1 (b) prescribes the plate's rim extent along X in frame F, and 11.1 says never to pool a waist with a plate width, so the row's note decides which stands in.
AP view: Along x, across the beam, it keeps its length: either the end-plate line between its lateral corners, with the plates superimposing unless the beam is parallel to the disc (3.1 c), or the waist between the side walls (3.6); divide by 1.14 (2.5).
Lateral view: Along the beam; a lateral view cannot give it (3.1 c).
Oblique view: 0.71 of itself, under the floor.
Magnification-free form: width over depth, which spans both views and is magnification-free only once each view is corrected (3.1 c); TPW/EPWu on one AP (11.9); the transverse over sagittal rim-chord ratio (11.9).
Readability: AP
Sources: measures.md 2.2, 2.5, 3.1 (b)(c), 3.6, 11.1, 11.9; anatomy.panjabi_body, scanimport.geometry.body_chords, body.waist, lines.panjabi_plates.

### body_d (length, mm)

Definition (vocabulary.csv): vertebral body depth where the paper does not say upper, lower or mid-height
The 3-D construction (not in the engine yet): not in the engine as a key of its own: the engine's depths are the end-plate depths, the top or bottom slab's anterior surface less the wall line's y (scanimport.geometry.body_chords; lines.panjabi_plates draws each from the wall line to the front), and the waist depth (body.waist); 3.2 (b) prescribes the plate's rim-to-rim extent along Z in the midsagittal band, never the whole body's maximum, and the row's note says which stands in.
AP view: Along y, along the beam; an AP gives no depth.
Lateral view: Along y, across the beam: the plate line from its anterior to its posterior corner with the beam tangent to the plate, a double contour meaning it is not (3.2 c), or the waist's anterior to posterior surface (3.6); divide by 1.23, and corrected films matched Panjabi's lumbar depths within about 1 mm (3.2 c).
Oblique view: 0.71 of itself, under the floor.
Magnification-free form: canal over body on one lateral (6.1 c); SPL/EPDu (11.9); width over depth across views, each corrected (3.1 c).
Readability: lateral
Sources: measures.md 2.2, 2.5, 3.1 (c), 3.2 (b)(c), 3.6, 6.1 (c), 11.1, 11.9; scanimport.geometry.body_chords, body.waist, lines.panjabi_plates.

### body_area (area, mm2)

Definition (vocabulary.csv): vertebral body cross-sectional area where the paper does not say which end-plate or level of the body
The 3-D construction (not in the engine yet): not in the engine as a key of its own: body.plate_area gives only the end-plate areas, the voxel count of a 2 mm slab parallel to each plate starting half a millimetre beneath its concavity, divided by the slab's thickness; no mid-height section area is emitted, though body.mid_slab is the slab a waist section would be counted on. 3.4 (b) prescribes O1 and O2, the vector area of the plate's rim loop, and 3.6 lists the section at mid-pedicle as the waist form.
AP view: A plate or a transverse section is a planar area with normal z, seen edge on by a beam along y: the projector's area factor is the cosine of 90 degrees, nothing, and 3.4 (c) says the area is not measurable on a film; the ellipse on the AP width and the lateral depth stands in, 2 to 19 percent off Panjabi by level and the other sign against tan2004.
Lateral view: The same: normal z, beam along x, edge on; not measurable (3.4 c).
Oblique view: The beam stays in the axial plane at every alpha, so the normal z stays square to it and the face is still edge on.
Magnification-free form: none (an area scales by M squared, 2.5; the ellipse stand-in needs each view corrected).
Readability: CT only
Sources: measures.md 2.4 (O1, O2), 2.5, 3.4 (b)(c), 3.6; body.plate_area, body.mid_slab; project.py area_factor, AREA_FACTOR_FLOOR.

### body_index (ratio, ratio)

Definition (vocabulary.csv): a ratio of body dimensions (e.g. anterior to posterior height); the note says which
The 3-D construction (in the engine): body.heights: body_index_ant_post = h_ant / h_post_inset and body_index_mid_post = h_mid / h_post_inset, each height read alike in corner-inset bands on the midline (the inset posterior height, not Panjabi's pass-through h_post); morphoview draws the two heights (lines.heights), the ratio being their quotient.
AP view: Both heights are z chords and keep their length, but the AP tells no anterior from posterior wall (3.3 c), so the ratio has no AP landmarks.
Lateral view: Both heights between the body corners on one lateral, so M cancels and the ratio needs no magnification (3.3 c); every series has L5 alone 10 percent or more taller in front (3.3 d, 11.9), and gilad1985's b/d and abbas2021's beveling ratio were film readings (3.3 d, e).
Oblique view: Two z chords keep their length and their quotient keeps its value where both corners are seen; no recipe judges the oblique.
Magnification-free form: it is one: VBHa/VBHp, also VBHm/VBHa and VBHm/VBHp (3.3 d, 11.9).
Readability: lateral
Sources: measures.md 2.5, 3.3 (c)(d)(e), 11.9; body.heights, lines.heights.

### disc_h_ant (length, mm)

Definition (vocabulary.csv): intervertebral disc height at the anterior margin
The 3-D construction (in the engine): column.disc_heights, in the lower vertebra's frame with the upper body brought in through the world (column.in_frame): the gap along z from L's upper plate surface to U's lower plate surface, each read in a band 2.5 mm inside that plate's own anterior corner (body.plate_rims, body.band_surface) so a slipped U still holds points; lines.discs draws it between those two world points.
AP view: A z chord across the beam keeps its length, but the AP tells no anterior corner from a posterior one and the plate lines superimpose unless the beam is parallel to the disc (3.1 c, 3.3 c); the disc recipe names the lateral only (5 c).
Lateral view: Between the corresponding anterior body corners, divided by M (5 c); films read the anterior height about 9 percent short of sections (5 c).
Oblique view: A z chord keeps its length at any alpha; no recipe judges the oblique.
Magnification-free form: disc anterior over posterior height, the wedging index I3 = ADH/PDH, compared film with film only (5 c, 11.9); anterior over middle height (5 d).
Readability: lateral
Sources: measures.md 2.5, 3.1 (c), 3.3 (c), 5 (a)(b)(c)(d), 11.9; column.disc_heights, column.in_frame, body.plate_rims, body.band_surface, lines.discs.

### disc_h_mid (length, mm)

Definition (vocabulary.csv): intervertebral disc height at the middle (centre)
The 3-D construction (in the engine): column.disc_heights: the same z gap read in bands half-way between each plate's own posterior and anterior rim bands on the midline, the centre of the interspace; lines.discs draws it.
AP view: A z chord keeps its length, but the centre of the interspace lies inside the body outlines and the recipe's judgment is that the middle height cannot be read on film (5 c).
Lateral view: Geometry allows it, a z chord across the beam, but 5 (c) says the middle disc height cannot be read on film, so no lateral value is taken.
Oblique view: A z chord keeps its length; the recipe's film verdict still stands.
Magnification-free form: twomey1985's convexity index M/(A+P) and the anterior over middle height (5 a, d), both of which need the middle that film does not give.
Readability: neither
Sources: measures.md 5 (a)(b)(c)(d); column.disc_heights, body.plate_rims, body.band_surface, lines.discs.

### disc_h_post (length, mm)

Definition (vocabulary.csv): intervertebral disc height at the posterior margin
The 3-D construction (in the engine): column.disc_heights: the z gap read in the bands 2.5 mm inside each plate's own posterior corner; lines.discs draws it.
AP view: A z chord keeps its length, but the posterior corners are not seen apart from the rest of the body on an AP (3.3 c).
Lateral view: Between the posterior body corners, divided by M (5 c), but films read it about 37 percent short, so the recipe says to predict it from the film's anterior height with kunkel2011's ADH-to-PDH equation (13 to 17 percent low) rather than measure it, within the fitted range only (5 c).
Oblique view: A z chord keeps its length; the posterior corners lie over the pedicles in a 45-degree view, and no recipe judges it.
Magnification-free form: ADH/PDH, film against film only (5 c, 11.9).
Readability: lateral
Sources: measures.md 2.5, 3.3 (c), 5 (b)(c), 11.9; column.disc_heights, body.plate_rims, body.band_surface, lines.discs.

### disc_h_mean (length, mm)

Definition (vocabulary.csv): intervertebral disc height as a mean of several points or an area over a length
The 3-D construction (in the engine): column.disc_heights: the mean of the three band gaps, not a number unless all three are; no line of its own, lines.discs drawing the three. twomey1985's area over AP length is 5 (b)'s mean gap over the overlapping plate area, which the engine does not take.
AP view: No: none of the three corners' gaps is read on an AP (3.1 c, 3.3 c).
Lateral view: Only as the mean of the anterior and posterior corner heights, bach2019's Average (A+P)/2 (5 a), since the middle cannot be read on film (5 c); the engine's three-band mean and twomey's area over length are section measures a film does not give.
Oblique view: z chords keep their length; the same film caveat holds.
Magnification-free form: none named for the mean; the convexity index M/(A+P) uses the two-corner sum (5 a).
Readability: lateral
Sources: measures.md 5 (a)(b)(c); column.disc_heights, lines.discs.

### disc_index (ratio, ratio)

Definition (vocabulary.csv): a disc ratio (e.g. disc height over body depth, or disc to body height); the note says which
The 3-D construction (not in the engine yet): not in the engine: column.disc_heights gives the four heights and measure.derived only the two canal indexes, so no disc ratio is emitted. Section 5 names the wedging index I3 = ADH/PDH and the convexity index M/(A+P) (5 a, c) and 11.9 the disc anterior over posterior height; a disc height over the body's depth or height is a quotient of 5 (b)'s gaps with 3.2 (b)'s rim depth or 3.3 (b)'s height, the row's note saying which.
AP view: No: an AP gives none of the disc heights' corners (3.1 c, 3.3 c) and no depth.
Lateral view: ADH/PDH on one lateral cancels M but is compared film with film only, since the film PDH is short (5 c); a disc over body height (two z chords) or a disc height over the end-plate depth (a y chord at about the same depth) cancels M on one lateral (2.5), with the middle height unavailable on film (5 c).
Oblique view: A ratio of two z chords keeps its value where the corners are seen; one with a y chord in it does not, the depth keeping 0.71.
Magnification-free form: it is one: ADH/PDH, M/(A+P), disc over body height, disc height over EPD (5 a, c; 2.5).
Readability: lateral
Sources: measures.md 2.5, 3.2 (b), 3.3 (b), 5 (a)(b)(c)(d), 11.9; column.disc_heights, measure.derived.

### disc_w (length, mm)

Definition (vocabulary.csv): disc transverse width
The 3-D construction (not in the engine yet): not in the engine, and section 5 defines no disc width: 5 (b)'s two-instance recipe takes heights and the mean gap only. The nearest prescriptions are the facing plates' rim widths, the extent along X of each plate's rim in frame F (3.1 b), or the extent of the SPINEPS disc label 100 (2.3).
AP view: Along x, across the beam, it keeps its length; the disc itself is radiolucent, so its width is the facing end-plate lines between their lateral corners (3.1 c), divided by 1.14 (2.5), with the plates superimposing unless the beam is parallel to the disc.
Lateral view: Along the beam; a lateral gives no width (3.1 c).
Oblique view: 0.71 of itself, under the floor.
Magnification-free form: none
Readability: AP
Sources: measures.md 2.3, 2.5, 3.1 (b)(c), 5 (b); none in the engine (column.disc_heights takes heights only).

### disc_d (length, mm)

Definition (vocabulary.csv): disc anteroposterior depth
The 3-D construction (not in the engine yet): not in the engine, and section 5 defines no disc depth. The nearest prescriptions are the facing plates' rim-to-rim depths along Z in the midsagittal band (3.2 b), or the extent of the SPINEPS disc label 100 (2.3); twomey1985's AP length of the midsagittal disc section is the form the true average height divides by (5 a).
AP view: Along y, along the beam; lost.
Lateral view: Along y, across the beam: the facing plate lines from anterior to posterior corner with the beam tangent to the plates (3.2 c), divided by 1.23 (2.5); a double contour means the beam is not tangent.
Oblique view: 0.71 of itself, under the floor.
Magnification-free form: none
Readability: lateral
Sources: measures.md 2.3, 2.5, 3.2 (b)(c), 5 (a)(b); none in the engine (column.disc_heights takes heights only).

## Pedicles

### pedicle_w (length, mm, PDWr)

Definition (vocabulary.csv): pedicle width: the smallest transverse diameter of the pedicle
The 3-D construction (in the engine): pedicle.coronal_sweep takes slabs square to the frame's y from the body's posterior wall back to the canal's posterior wall and keeps on each side the island nearest the midline within the body's height (canal.body_span); pedicle.island_row reads each island's extent across x between its outer surfaces (scanimport.geometry.surface), and pedicle.isthmus takes the median over the slabs within ISTHMUS_SHARE of the fewest voxels and multiplies it by the cosine of the transverse angle from pedicle.axis_from, since a coronal slab cuts a converging pedicle on the slant. morphoview.lines.pedicles draws pedicle_w_<side> as a chord along x through the isthmus row's centre whose drawn length is the raw slab width while the value carries the cosine; pedicle.measures gives the side mean.
AP view: The chord lies along x, across an AP beam, so it keeps its length times M; it is the outer medial-to-lateral extent of the pedicle ring, the very coronal island the engine finds, but as the ring is an oblique section of a pedicle converging by a it stands 1/cos a above the engine's value, the cosine an AP film cannot supply. 7.1 (c): the AP view is the one view, divided by 1.14 at 110 cm; the densest ring lies 1 to 3 mm inside the outer cortex, so films of dry vertebrae read 0 to 0.6 mm low at L1 to L4 and 3.5 mm low at L5.
Lateral view: The chord runs along the beam and both pedicles superimpose: nothing of the width survives, and 7.1 (c) names the AP alone.
Oblique view: A chord along x keeps cos 45, 0.71, under the projector's 0.9 floor, so the drawn width fails. What holds is geometric only: one side's pedicle is crossed at 45 - a from its axis and its ring comes within the floor of the section square to the axis where a exceeds about 19 degrees (the neck, T1 to T2 and L5 by Panjabi's means), but the engine draws that chord nowhere and the other side's ring is crossed at 45 + a.
Magnification-free form: H/W of the same AP ring (7.1 c, 7.3 c, 11.9); duman2026's width over height, TPD/SPD, the same ratio inverted (7.3 d).
Readability: AP
Sources: measures.md 2.2, 2.4 (O3), 2.5, 7 (recipe P), 7.1 (a) to (c), 11.3; morphometry/pedicle.py coronal_sweep, island_row, walls, without_strays, axis_from, isthmus, measures; morphoview/lines.py pedicles; autoanatomist/project.py FORESHORTENING_FLOOR.

### pedicle_h (length, mm, PDHr)

Definition (vocabulary.csv): pedicle height: the smallest craniocaudal diameter of the pedicle
The 3-D construction (in the engine): The same sweep: pedicle.island_row reads each island's extent up z between its outer surfaces, and pedicle.isthmus takes the median over the isthmus slabs with no cosine, since the slab's vertical extent is the height and the sagittal tilt's 1/cos is small (7.2). morphoview.lines.pedicles draws pedicle_h_<side> as a chord along z through the centre of the row nearest the median; pedicle.measures gives the side mean.
AP view: The chord lies along z, across the beam, and keeps itself times M as the ring's vertical extent between the notches, the slab's own reading with no cosine to lose. 7.2 (c) allows it: the AP ring gives a height too, distorted by the convergence since the ring is an oblique section.
Lateral view: Along z, across the beam: it keeps itself, divided by 1.23 at 110 cm. 7.2 (c) makes this the view: the narrowest vertical dimension between the superior and inferior notches with both sides superimposed; films of dry vertebrae read 1.5 to 1.8 mm high at L1 to L3 and 2.4 mm low at L5, and mitra2002's lateral films agreed within 0.9 mm.
Oblique view: A chord along z keeps itself whole under every rotation about the column, so the height is the one pedicle chord that survives the 45-degree view; the recipes say nothing of its visibility there.
Magnification-free form: H/W of the same ring (7.3 c, 11.9).
Readability: both
Sources: measures.md 7 (recipe P), 7.2 (a) to (c), 11.3, 11.9; morphometry/pedicle.py coronal_sweep, island_row, isthmus, measures; morphoview/lines.py pedicles.

### pedicle_area (area, mm2, PDAr)

Definition (vocabulary.csv): pedicle cross-sectional area at its narrowest
The 3-D construction (in the engine): pedicle.island_row gives each slab's area as its voxel volume over the slab's thickness, and pedicle.isthmus takes the median over the isthmus slabs times the cosine of the axis's angle to y, so that the coronal face stands for the section square to the axis, recipe P's isthmus section; it is a planar area whose normal is the axis, near y. morphoview.lines.pedicles draws no area; pedicle.measures gives the side mean.
AP view: The face's normal lies near the beam, so the ring encloses the area times M squared with an area factor of about cos a, the very cosine pedicle.isthmus applies: above the 0.9 floor where the convergence is under 26 degrees (T3 to L4 by Panjabi's means, L5 at 0.91), under it at C3 to C7 and T1 to T2. The recipe's judgment overrides the geometry: 7.3 (c) says an area is not measurable on a film, the proxies W x H / 2 and the ellipse are level dependent, and the ring's dense line lies 1 to 3 mm inside the cortex (7.6).
Lateral view: The face stands edge on to a lateral beam: nothing of the area survives.
Oblique view: One side's face is crossed at 45 - a and keeps cos(45 - a), above 0.9 only where a exceeds about 19 degrees (the neck, T1 to T2, L5), the other at 45 + a; a fact about the ring's shape, not a reading the recipe allows.
Magnification-free form: None: the shape proxies carry M squared; H/W of the ring is the magnification-free shape measure 7.3 (c) offers in its place.
Readability: neither
Sources: measures.md 2.4 (O2), 7 (recipe P), 7.3 (a) to (c), 7.6, 11.3; morphometry/pedicle.py island_row, isthmus, measures; autoanatomist/project.py area_factor, AREA_FACTOR_FLOOR.

### pedicle_incl_sag (angle, deg, PDIsr)

Definition (vocabulary.csv): pedicle axis inclination to the sagittal plane
The 3-D construction (in the engine): pedicle.axis_from fits the axis over the run of slabs within RUN_SHARE of the fewest voxels, across from the slope of the island's medial wall (pedicle.walls) against y, and pedicle.isthmus turns it into pedicle_angle_transverse, atan2 of the medial component over the backward one, positive where the pedicles converge toward the front; pedicle.measures gives the side mean. That engine key measures this key's direction (the vocabulary's note) as the angle of the axis's projection in the transverse plane, where 7.4 (b) prescribes arcsin of the axis's x component, the angle to the sagittal plane; the two agree where the sagittal tilt is small, and no line is drawn for it, the chord line along the axis standing for it.
AP view: An axial angle, its plane normal along z, holds the beam and is seen edge on (a tilt of 90 degrees against the 15-degree limit). 7.4 (c): the convergence needs an axial image and cannot be read on an AP or a lateral film.
Lateral view: Edge on in the same way: nothing survives.
Oblique view: Every alpha turns about z, so the axial plane stays edge on at 45 degrees as at 0; the one geometric trace is that a 45-degree beam crosses one side's pedicle at 45 - a, so that ring is roundest where a is near 45 (C3 to C5), a shape and not a reading.
Magnification-free form: None; an angle carries no M.
Readability: CT only
Sources: measures.md 2.2, 7.4 (a) to (c), 11.3; morphometry/pedicle.py axis_from, walls, isthmus, one_side, measures; autoanatomist/project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

### pedicle_incl_trans (angle, deg, PDItr)

Definition (vocabulary.csv): pedicle axis inclination to the transverse plane
The 3-D construction (in the engine): pedicle.axis_from's climb, the slope of the run's centres' z against y, gives the axis's z component; pedicle.isthmus takes atan2 of it over the backward component, positive where the posterior end is higher, and pedicle.one_side subtracts the posterior wall's slope angle (pedicle.wall_slope, body.posterior_wall_slope) so the angle is against the plane square to the wall, Panjabi's and Zindrick's reference and not the end plate's. The engine's key is pedicle_angle_sagittal; it is withheld where the free run spans under SAGITTAL_SPAN_MM, 5.5 mm front to back, since so short a run's climb is the notch's and the process's (study 0004's thoracic pedicles), and 7.4 (b)'s arcsin of the cranial component agrees with it where the convergence is small.
AP view: A sagittal angle, its plane normal along x, is edge on to an AP beam: nothing survives.
Lateral view: The plane faces the detector, so the angle keeps its value as the tilt of the pedicle's axis from the perpendicular to the posterior body line. 7.4 (c): it can be approximated on a lateral where the pedicle outline shows, the neck's pedicle overlapping the lateral mass; end-plate-referenced readings differ from it by the plate's inclination (3.5), and lateral films read those 3.4 to 6.1 degrees low.
Oblique view: The plane's normal leans 45 degrees off the beam, three times the 15-degree limit: nothing holds.
Magnification-free form: None; an angle carries no M.
Readability: lateral
Sources: measures.md 2.2, 3.5, 7.4 (a) to (c), 11.3; morphometry/pedicle.py axis_from, isthmus, wall_slope, one_side, measures; morphometry/body.py posterior_wall_slope; autoanatomist/project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

### pedicle_w_outer (length, mm)

Definition (vocabulary.csv): pedicle outer (cortex to cortex) width where the paper separates outer from inner
The 3-D construction (in the engine): The engine's pedicle_w is an outer width by construction and this key is the same line: the mask's boundary is the periosteal cortex (recipe P's note) and pedicle.island_row reads the island's extent to the surface beyond its outermost voxel centres (scanimport.geometry.surface), the median and cosine taken by pedicle.isthmus and the chord drawn by morphoview.lines.pedicles. The engine does not tell outer from inner.
AP view: As pedicle_w, a chord along x that keeps its length times M as the ring's outer edges (7.1 c). The ring's densest line lies 1 to 3 mm inside the outer cortex (7.1 c, 7.6), so the film's edge under-reads the outer width that the mask gives.
Lateral view: Along the beam, both sides superimposed: nothing survives.
Oblique view: 0.71 of itself, under the 0.9 floor; nothing holds beyond what pedicle_w's row says of the near-coaxial side.
Magnification-free form: H/W of the same ring (7.3 c).
Readability: AP
Sources: measures.md 7 (recipe P, the outer-boundary note), 7.1 (a), (c), 7.6; morphometry/pedicle.py island_row, isthmus; morphoview/lines.py pedicles; scanimport/geometry.py surface.

### pedicle_w_inner (length, mm)

Definition (vocabulary.csv): pedicle inner (endosteal, cancellous) width
The 3-D construction (not in the engine yet): Not in the engine: a binary mask has no cortex, and 7.6 says a wall thickness needs the CT's intensities; the inner width is makino2012's, inner cortex to inner cortex square to the axis in the axial plane, and 7.1 (a) and 7.6 infer it reads about two cortices, 1.5 to 3 mm, below the outer width.
AP view: Geometrically the same chord along x as the outer width, but no recipe reads an endosteal width on a film: the ring's dense line lies between the two cortices, 1 to 3 mm inside the outer (7.6), and marks neither.
Lateral view: Along the beam: nothing survives.
Oblique view: 0.71, under the floor; nothing holds.
Magnification-free form: None.
Readability: CT only
Sources: measures.md 7 (recipe P), 7.1 (a) makino2012 row and biases, 7.6, 11.9; no engine function.

### pedicle_h_outer (length, mm)

Definition (vocabulary.csv): pedicle outer height
The 3-D construction (in the engine): The engine's pedicle_h, outer by the mask's boundary: the island's extent up z to its outer surfaces (pedicle.island_row), the median over the isthmus slabs (pedicle.isthmus), drawn along z by morphoview.lines.pedicles. The engine has no inner height to set it against.
AP view: Along z, across the beam: it keeps itself times M as the ring's vertical extent, which 7.2 (c) allows with the convergence's distortion.
Lateral view: Along z: it keeps itself, divided by 1.23, as the narrowest vertical dimension between the notches with both sides superimposed, the recipe's view (7.2 c).
Oblique view: Along z it keeps itself whole at every alpha.
Magnification-free form: H/W of the same ring (7.3 c).
Readability: both
Sources: measures.md 7 (recipe P), 7.2 (a) to (c); morphometry/pedicle.py island_row, isthmus; morphoview/lines.py pedicles.

### pedicle_h_inner (length, mm)

Definition (vocabulary.csv): pedicle inner (endosteal) height
The 3-D construction (not in the engine yet): Not in the engine: it needs the CT's intensities (7.6), and 7.2 (a) infers from otsuki2021's cranial and caudal walls of 2.5 to 4.0 mm that the endosteal height reads 5.7 to 6.9 mm below the outer one at L1 to L5.
AP view: A chord along z would keep itself, but no recipe reads an endosteal height on a film; the ring's top and bottom are the cranial and caudal walls' outer images, their dense line inside the cortex (7.6).
Lateral view: The same: the pedicle's upper and lower outlines are the outer walls, both sides superimposed, and no recipe reads the inner edge.
Oblique view: Along z it keeps itself whole, with nothing to read.
Magnification-free form: None.
Readability: CT only
Sources: measures.md 7.2 (a) makino2012 row and the wall inference, 7.6; no engine function.

### pedicle_chord (length, mm)

Definition (vocabulary.csv): pedicle axis or screw path length: from the posterior entry point through the pedicle to the anterior cortex of the body
The 3-D construction (in the engine): pedicle.chord marches along the axis line through the isthmus row's centre (pedicle.axis_from) in MARCH_MM steps and reads the run of the vertebra's voxels (anatomy.Vertebra.is_bone) from where the line enters the posterior elements to where it leaves the body's anterior cortex, Zindrick's screw path and the 0-degree chord of 7.5's mask recipe (O5 along recipe P's axis); morphoview.lines.march gives the entry and exit offsets and lines.pedicles draws pedicle_chord_<side> between them. It is NaN where the run gave no axis and for a vertebra the volume's edge cuts (pedicle.measures, measure.cut_by_the_edge).
AP view: The chord runs along the axis, near the beam, and keeps only the sine of its angle to y, about sin a, far under the floor; its entry point and the anterior cortex fall on one spot. 7.5's radiograph part names the lateral alone.
Lateral view: The chord keeps about cos a of itself, its medial component lying along the beam: above the 0.9 floor where the convergence is under 26 degrees (T3 to L5 by Panjabi's means, L5 at 0.91), under it in the neck. 7.5: on a lateral film the 0-degree chord is about 1.32 times the mid-body AP depth and the 15-degree chord about 1.60 times, with 3 to 4 mm of scatter and no magnification correction, a prediction from the body depth rather than a reading of the chord's lamina end.
Oblique view: One side's chord runs at 45 - a from the beam and keeps sin(45 - a), under half of itself; the other's at 45 + a, which passes the floor only where a exceeds about 19 degrees (the neck, T1 to T2, L5).
Magnification-free form: The chord over the mid-body AP depth on one lateral: about 1.32 for the 0-degree chord and 1.60 for the 15-degree one (7.5).
Readability: lateral
Sources: measures.md 2.4 (O5), 7 (recipe P), 7.5 (mask recipe, radiograph); morphometry/pedicle.py chord, axis_from, one_side, measures, MARCH_MM; morphometry/measure.py cut_by_the_edge; morphoview/lines.py march, pedicles; autoanatomist/project.py FORESHORTENING_FLOOR.

### pedicle_length (length, mm)

Definition (vocabulary.csv): pedicle length proper (from the lamina junction to the body)
The 3-D construction (not in the engine yet): Not in the engine: no function gives the length proper, and 7.5 lists the short anatomical lengths of masharawi2021 and arockiaraj2025 as not comparable with the chords, giving a mask recipe for the chord alone. Recipe P step 2 bounds the bridge from the body's dorsal surface to the most anterior voxel of the superior articular or transverse process, and its extent along the axis of step 3 (O3) would be this length; pedicle.axis_from measures the free run's front-to-back span only to decide whether the sagittal angle is read (SAGITTAL_SPAN_MM) and writes it in a flag, not as a value.
AP view: Along the axis, near the beam: it fails as the chord does, keeping about sin a.
Lateral view: A chord along the axis keeps about cos a, above the floor below 26 degrees of convergence, but the recipes give no film reading for the length proper (7.5 gives one for the chord only), and 7.4 (c) allows the lateral pedicle outline only where it shows, the neck's lying under the lateral mass.
Oblique view: One side at 45 - a from the beam, the other at 45 + a, as the chord; nothing the recipes read.
Magnification-free form: None.
Readability: neither
Sources: measures.md 2.4 (O3), 7 (recipe P steps 2 and 3), 7.4 (c), 7.5; morphometry/pedicle.py axis_from, SAGITTAL_SPAN_MM (the span, flagged and not measured).

### pedicle_cortex (length, mm)

Definition (vocabulary.csv): pedicle cortical wall thickness (which wall, in the note)
The 3-D construction (not in the engine yet): Not in the engine: 7.6 says a mask cannot give a wall thickness and the CT's intensities are needed; the values are otsuki2021's micro-CT walls at the lumbar isthmus (medial 0.8 to 1.3, lateral 0.6 to 1.7, cranial 3.1 to 4.0, caudal 2.5 to 3.2 mm at L1 to L5, porous shell included) and mitra2002's direct ones, the wall named in the note. The mask's boundary is the outer cortex (recipe P), which is why its widths stand about one wall on each side above endosteal ones.
AP view: The medial and lateral walls lie across the beam and the ring is their image, but the densest line lies 1 to 3 mm inside the outer cortex and at S1 the ring's medial line is trabecular bone, not cortex (7.6), so a film shows a cortical line and not its thickness; the cranial and caudal walls are the ring's top and bottom, the same.
Lateral view: The cranial and caudal walls are the pedicle's upper and lower outlines, both sides superimposed; no recipe reads a thickness there.
Oblique view: Nothing holds.
Magnification-free form: None.
Readability: CT only
Sources: measures.md 7 (recipe P, the outer-boundary note), 7.1 (a) makino2012 row, 7.6; no engine function.

### pedicle_angle_transverse (angle, deg)

Definition (vocabulary.csv): pedicle transverse (medial) angle in the axial plane, to the midsagittal plane (Panjabi's pedicle_incl_sag measures the same direction)
The 3-D construction (in the engine): The engine's own key: pedicle.axis_from takes the axis's across component as the slope of the island's medial wall (pedicle.walls) over the run of slabs within RUN_SHARE of the fewest voxels, the canal's side, since toward the back the island widens into the transverse process and its middle drifts out (a false 37 degrees of convergence at study 0004's L4); pedicle.isthmus gives atan2 of the medial component over the backward one, positive where the pedicles converge toward the front, pedicle.one_side sets it NaN where the run is too short for an axis, and pedicle.measures gives the side mean. No line is drawn for it; the chord line along the axis (morphoview.lines.pedicles) shows the axis.
AP view: An axial angle, its plane normal along z, is seen edge on by an AP beam. 7.4 (c): no clinical AP or lateral film gives it; axial radiographs of disarticulated vertebrae over-read it against direct measures, and an image midline adds the vertebra's rotation to one side and takes it from the other, which the side mean cancels.
Lateral view: Edge on in the same way: nothing survives.
Oblique view: A rotation about z keeps the axial plane edge on at every alpha; a 45-degree beam crosses one side's pedicle at 45 - a and makes that ring roundest where a is near 45 degrees (C3 to C5), a shape and not a reading of the angle.
Magnification-free form: None; an angle carries no M.
Readability: CT only
Sources: measures.md 7.4 (a) to (c), 11.3; morphometry/pedicle.py axis_from, walls, isthmus, one_side, measures, RUN_SHARE; autoanatomist/project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

### pedicle_angle_sagittal (angle, deg)

Definition (vocabulary.csv): pedicle sagittal (cranial-caudal) angle in the sagittal plane, to the end-plate or transverse plane (Panjabi's pedicle_incl_trans measures the same direction)
The 3-D construction (in the engine): The engine's own key: pedicle.axis_from's climb (the run's centres' z against y) gives the axis's z component, pedicle.isthmus takes atan2 of it over the backward component, positive where the posterior end is higher, and pedicle.one_side subtracts atan of the wall's slope (pedicle.wall_slope, body.posterior_wall_slope) so the angle is against the plane square to the posterior wall, as the end-plates' inclinations are taken, and not against a column line that leans where neighbours slip. It is NaN where the run spans under SAGITTAL_SPAN_MM, 5.5 mm front to back (study 0004's thoracic pedicles span 4.5 to 5.3 mm), since so short a run's climb is the notch's and the superior articular process's and not the pedicle's; pedicle.measures gives the side mean.
AP view: A sagittal angle, its plane normal along x, is edge on to an AP beam: nothing survives.
Lateral view: The plane faces the detector, so the angle keeps its value between the pedicle's axis and the perpendicular to the posterior body line where the pedicle outline shows (7.4 c), the neck's pedicle lying under the lateral mass; olsewski1990, mitra2002 and lien2007 take it against the end plate instead, differing by the plate's inclination (3.5), and lateral films read that angle 3.4 to 6.1 degrees low.
Oblique view: The plane leans 45 degrees off the beam, over the 15-degree limit: nothing holds.
Magnification-free form: None; an angle carries no M.
Readability: lateral
Sources: measures.md 3.5, 7.4 (a) to (c), 11.3; morphometry/pedicle.py axis_from, isthmus, wall_slope, one_side, measures, SAGITTAL_SPAN_MM; morphometry/body.py posterior_wall_slope; autoanatomist/project.py plane_tilt_deg, PLANE_TILT_MAX_DEG.

## The canal and the foramen

### canal_w (length, mm, SCW)

Definition (vocabulary.csv): spinal canal width: the transverse diameter of the canal at the level of the pedicles
The 3-D construction (in the engine): anatomy.read_in builds a CanalSlab for every slab across the column where the arch closes round the canal, its width read by scanimport.geometry.canal_walls as the distance between the bone surfaces on the two sides of the hole in a band through the hole's middle; v.panjabi['canal_w'] is scanimport.geometry.canal_chords' median of that width over the slabs in the middle half of the body's height, and canal.measures gives the reread's own form as interpedicular_max, the greatest smoothed width (canal.smoothed) over the full rings (anatomy.Vertebra.full_rings) within a quarter of the pedicle's height of the pedicle centre (canal.pedicle_slabs with pedicle.band). As a line, morphoview.lines.across_walls gives the two side walls through the hole's middle in a chosen ring, but lines.interpedicular draws it only for the least width, so no line yet draws canal_w or interpedicular_max; the reread's recipe (6.2 (b): the greatest extent between the medial pedicle surfaces over every closed section, the mid-pedicle value stored beside it) is the engine's interpedicular_max in kind and not its body-middle median.
AP view: A chord along x, across an AP beam, so it keeps its length; the 2-D landmarks are the medial cortices of the two pedicle rings seen end-on, and 6.2 (c) reads the gap between them divided by 1.14 at 110 cm, with a film lower limit of 20 mm against 18 mm on bone and rotation making the projected gap inaccurate. The film reads the shortest gap between the projected pedicles (the engine's interpedicular key), not the greatest section width that canal_w is, so an AP gives canal_w only up to the difference between the least and the greatest width over the pedicle's height.
Lateral view: The chord lies along the beam and the two medial pedicle walls fall on one another, so a lateral gives nothing of it; 6.2 (c) names the AP only.
Oblique view: A 45-degree oblique keeps 0.71 of the chord, under the 0.9 floor, and the pedicle rings open into tubes so their medial cortices are no longer seen end-on. Its ratio to the end-plate width, both along x at nearly one depth, would cancel the foreshortening and M in principle, but the reread states no oblique reading.
Magnification-free form: Canal width over end-plate width on one AP view (6.2 (c)); width over depth (6.2 (d)) needs the AP and the lateral, whose M differ (1.14 against 1.23, 2.5), so it is free of M only once each view is corrected; the Jones index takes the width as its AP factor (measure.derived).
Readability: AP
Sources: measures.md 2.2, 2.4, 2.5, 6 (recipe C), 6.2 (a) to (e), 11.2; anatomy.read_in, anatomy.Vertebra.full_rings, scanimport.geometry.canal_walls, scanimport.geometry.canal_chords, canal.measures, canal.pedicle_slabs, canal.smoothed, pedicle.band, morphoview.lines.across_walls, morphoview.lines.interpedicular, measure.derived.

### canal_ap (length, mm, SCD)

Definition (vocabulary.csv): spinal canal depth: the anteroposterior diameter of the canal in the midline
The 3-D construction (in the engine): v.panjabi['canal_ap'] is the midline depth scanimport.geometry.canal_walls reads in each slab, the anterior wall's surface less the posterior wall's in a band through the hole's middle, taken by scanimport.geometry.canal_chords as the median over the slabs in the middle half of the body; canal.least_depth gives canal_ap_min, Eisenstein's least depth, the minimum of the smoothed midline profile over the full rings with its height as a share of the body, and canal.lateral_film gives canal_ap_lateral_film at L1 to L4, the depth from the body's posterior wall line (anatomy.wall_slope) to the line joining the superior and inferior articular apexes (canal.apex, the two sides averaged) at three quarters of the body's height. morphoview.lines.least_depth draws the midline chord from the posterior to the anterior wall in the ring the minimum came from (lines.median_of_three) and lines.lateral_film draws the film construction with the apex-to-apex join as an extra line; the reread's recipe, a ray along the engine's -y from the body's back to the first arch voxel in the mid-pedicle section, the median over |x| <= 1 mm (6.1 (b)), is a third height convention the engine does not take.
AP view: The chord runs along the beam and the arch's inner surface at the base of the spinous process lies over the body, so an AP gives nothing; 6.1 (c) says lateral view only.
Lateral view: Along y, across the beam, it keeps its length; 6.1 (c) takes the posterior cortex of the body at the midline in front and, at L1 to L4, a point opposite the cranial half of the body on the line from the superior articular apex to the inverted inferior apex, at L5 a point just in front of the lucent lake of the spinous process, divided by 1.23 at 110 cm, with a film lower limit of 15 mm against 13 mm on bone. canal.lateral_film is that construction in true size, and it is a film convention rather than Panjabi's mid-canal chord, so the film value and canal_ap differ by more than M.
Oblique view: 0.71 of the chord, under the floor, and the apex line, averaged over two sides on a lateral, splits into two on an oblique; the depth over the body's depth would cancel the foreshortening in principle, but the reread states no oblique reading.
Magnification-free form: Canal depth over body depth, the Torg ratio, on one lateral view (6.1 (c), (d): 0.70 at L1 falling to 0.58 at L3 to L5 in alonge2021; yadav2020's SCD/UVD; italianmri's SCD/VBD); measure.derived's canal_index_torg is canal_ap over body_d_mid.
Readability: lateral
Sources: measures.md 2.2, 2.4 (O5), 2.5, 6 (recipe C), 6.1 (a) to (e), 11.2, 12; anatomy.read_in, anatomy.wall_slope, scanimport.geometry.canal_walls, scanimport.geometry.canal_chords, canal.least_depth, canal.smoothed, canal.apex, canal.lateral_film, morphoview.lines.least_depth, morphoview.lines.lateral_film, measure.derived.

### canal_area (area, mm2, SCA)

Definition (vocabulary.csv): spinal canal cross-sectional area
The 3-D construction (in the engine): canal.counted_area gives one slab's canal area from the scan's own voxels, those outside the bone whose centres fall in the slab and in the hole grown by one pixel, their count times a voxel's volume over the slab's thickness; canal.measures takes canal_area as the median over the full rings in the middle half of the body and canal_area_min as the least of the median-filtered profile, and every CanalSlab also carries its hole's raster area (anatomy.read_in from scanimport.geometry.sections). It is a planar patch with normal z, not a line, so morphoview draws none; the reread wants the mid-pedicle section's area with the minimum beside it (6.3 (b), recipe C), where the engine's median spans the body's middle half.
AP view: An axial area is edge-on to a beam along y (area factor 0), so nothing of it reaches the film; 6.3 (c) calls it not measurable, the ellipse pi x SCW x SCD / 4 reading 10 to 30 percent high and SCW x SCD / 2 reading 20 to 30 percent low, with SCA/(SCW x SCD) about 0.73 at C2, 0.57 to 0.60 at C5 to C7 and about 0.71 at L1 falling to 0.61 at L4 to L5.
Lateral view: Edge-on again (normal z, beam along x); nothing. The only film route is the two-diameter estimate from an AP width and a lateral depth, each carrying its own M, corrected by the factor of the series whose definition the mask copies (6.3 (c)).
Oblique view: Any beam in the xy plane sees the section edge-on, so a 45-degree oblique keeps none of it; nothing holds.
Magnification-free form: Canal area over body area (griffith2016's CSA ratio, 6.3 (d)) on CT; on film none, an area scaling by M squared and no view showing it.
Readability: CT only
Sources: measures.md 2.4 (O2), 2.5, 6 (recipe C), 6.3 (a) to (e), 11.2; anatomy.read_in, anatomy.CanalSlab, anatomy.Vertebra.full_rings, canal.counted_area, canal.measures, scanimport.geometry.sections.

### interpedicular (length, mm)

Definition (vocabulary.csv): interpedicular distance: the smallest distance between the medial walls of the pedicles (Panjabi's canal width is the closest)
The 3-D construction (in the engine): canal.measures gives interpedicular, the least distance between the pedicles' medial walls: the minimum of the smoothed slab width (canal.smoothed) over the full rings lying within nine tenths of the pedicle's half-height of the pedicle centre (canal.pedicle_slabs with pedicle.band, which averages the isthmus rows' centre and height from pedicle.one_side), each slab's width read by scanimport.geometry.canal_walls on the bone surfaces either side of the hole. morphoview.lines.interpedicular draws it as the line between the two side walls (lines.across_walls) in the ring the minimum came from, in the axial_canal panel; the reread's film-equivalent form, the pedicles projected along y onto the coronal plane and the smallest gap over the rows crossing both (6.2 (b) step 4), is not built, the in-section minimum standing in for it in true size.
AP view: A chord along x, across the beam, keeps its length, and this is the measure an AP film reads: the gap between the medial cortices of the end-on pedicle rings, divided by 1.14 at 110 cm (6.2 (c)); Hinck's values are uncorrected film values at 40 in, his AP spine films 0.57 mm wider than PA chest films, and rotation makes the projected gap inaccurate (ahn2001 in 6.2 (c)).
Lateral view: Along the beam, the two pedicles superimposed; nothing; 6.2 (c) names the AP only.
Oblique view: 0.71 of the chord, under the floor, and the medial pedicle cortices are no longer end-on; the reread states no oblique reading.
Magnification-free form: Interpedicular distance over end-plate width on one AP view (6.2 (c)); ratios between levels, which cancel M (6.2 (b), chaudhary2015); the Jones index (canal_ap_min x interpedicular_max over body_d_mid x body_w_mid, measure.derived), a lateral ratio times an AP ratio, each free of its own M.
Readability: AP
Sources: measures.md 2.2, 2.5, 6 (recipe C), 6.2 (a) to (e), 11.2, 11.9; anatomy.read_in, scanimport.geometry.canal_walls, canal.measures, canal.pedicle_slabs, canal.smoothed, pedicle.band, pedicle.one_side, morphoview.lines.interpedicular, morphoview.lines.across_walls, morphoview.lines.median_of_three, measure.derived.

### canal_index (ratio, ratio)

Definition (vocabulary.csv): a canal ratio (e.g. Torg-Pavlov canal to body ratio, or canal shape index); the note says which
The 3-D construction (in the engine): measure.derived gives two canal-to-body ratios from measures already taken: canal_index_torg, canal_ap over body_d_mid (the body's mid-height depth from body.waist on body.mid_slab, drawn by morphoview.lines.waist), and canal_index_jones, canal_ap_min times interpedicular_max over body_d_mid times body_w_mid; canal.measures gives a shape ratio, canal_index_trefoil, the median over the full rings of the lateral depth (canal.lateral_depth, at 0.75 of the half-width out from the midline) over the midline depth. A ratio has no line of its own, its chords being lines.least_depth, lines.interpedicular and lines.waist; the reread's forms are canal depth over body depth (6.1 (c), (d)), width over depth (6.2 (d)), width over end-plate width (6.2 (c)) and SCA over the ellipse on SCW and SCD (6.4).
AP view: The Torg ratio's two depths lie along the beam, so an AP gives none of it; the width forms survive: interpedicular over end-plate width, both along x, cancels M on one AP (6.2 (c)), and that is the AP factor of the Jones index (interpedicular_max over body_w_mid), the pedicle rings' medial cortices over the body's lateral cortices.
Lateral view: The Torg ratio is a lateral measure: canal depth from the body's posterior cortex to Eisenstein's posterior limit over the body's depth at about the same height, both along y and at one depth, so M cancels (6.1 (c); 6.1 (d): 0.70, 0.64, 0.58, 0.58, 0.58 at L1 to L5 in alonge2021, and a U with its floor at L4 on MRI). The Jones index's depth factor comes from the same view, so the whole index is one lateral ratio times one AP ratio; the trefoil index's two depths, midline and 0.75 of the half-width out, fall on one line on a lateral and cannot be told apart, so it is CT only.
Oblique view: Two chords along one axis at about one depth foreshorten alike and share M, so a ratio such as Torg's keeps its value in principle at 45 degrees, but its landmarks (the midline posterior wall, the apex line averaged over two sides) are not the oblique's and the reread states no oblique reading; the width-over-depth shape ratio mixes an x chord with a y chord and fails.
Magnification-free form: Itself: Torg's canal depth over body depth (lateral), interpedicular over end-plate width (AP), and the Jones product of the two; width over depth needs two views whose M differ (1.14 against 1.23, 2.5) and is free of M only after each is corrected.
Readability: lateral
Sources: measures.md 2.5, 6.1 (c), (d), 6.2 (c), (d), 6.3 (c), (d), 6.4 (canal shape), 11.9; measure.derived, measure.ratio, canal.measures, canal.lateral_depth, canal.least_depth, body.waist, body.mid_slab, morphoview.lines.waist, morphoview.lines.least_depth, morphoview.lines.interpedicular.

### lateral_recess (length, mm)

Definition (vocabulary.csv): lateral recess depth or width
The 3-D construction (in the engine): canal.lateral_depth reads, in one slab, the canal's front-to-back depth at 0.75 of its half-width out from the midline on each side (LATERAL_SHARE), between the bone surfaces in front of and behind the hole in a band across, the two sides averaged; canal.measures keeps the least of it over the full rings as canal_ap_lateral and its ratio to the midline depth as canal_index_trefoil. That is the lateral depth of the ring at pedicle height and not yadav2020's lateral recess diameter, which 6.4 takes from the posterior body surface to the anteromedial point of the facet joint in the transverse section at the cranial end-plate, as the perpendicular to the tangent on the anterior margins of both superior articular processes (labels 45 and 46) just medial to the process; the engine does not build that, and no morphoview line draws either.
AP view: A depth along y lies along the beam; nothing; 6.4 gives no radiograph for the lateral recess.
Lateral view: Along y, across the beam, the chord would keep its length, but its ends, the posterior body wall off the midline and the lamina or articular root behind it, fall on the midline canal and on the other side's recess; 6.4 states none, so no view gives it.
Oblique view: 0.71 of the chord, under the floor; a 45-degree oblique throws the near facet joint clear of the body but the reread states no oblique reading for the recess.
Magnification-free form: none in 6.4 for the recess; the engine's trefoil index, lateral over midline depth, is a size-free shape but CT only.
Readability: neither
Sources: measures.md 6 (recipe C), 6.4 (lateral recess diameter, canal shape), 11.9; canal.lateral_depth, canal.measures, anatomy.read_in, anatomy.Vertebra.full_rings.

### foramen_h (length, mm)

Definition (vocabulary.csv): intervertebral foramen height
The 3-D construction (in the engine): column.foramen gives it between two instances: on each side, from the lowest point of the upper vertebra's pedicle at its isthmus (pedicle.one_side's record of the isthmus row, its centre less half its height along the vertical unit eh, built by pedicle.coronal_sweep, pedicle.axis_from and pedicle.isthmus) to the highest point of the lower vertebra's pedicle isthmus, the difference taken along the lower vertebra's z, each side and the mean, called from column.disc for adjacent vertebrae whose bodies the volume's edge does not cut (measure.measure_volume). No morphoview line draws it (lines.discs draws the three disc heights, lines.pedicles each pedicle's height at the isthmus row nearest the median); the reread's recipe (6.4) reads the greatest craniocaudal gap between the caudal surface of the upper pedicle cut and the cranial surface of the lower one in the parasagittal plane through each pedicle's centroid (O3), where the engine takes it at the isthmus centre.
AP view: A height along z lies across an AP beam and keeps its length; the 2-D landmarks are the caudal cortex of the upper pedicle ring and the cranial cortex of the lower one, each side seen apart. 6.4 names the lateral only, though 7.2 (c) allows that the AP ring gives a pedicle height, distorted by the pedicle's convergence, so the AP reading is permitted by geometry and not stated by the reread for the foramen.
Lateral view: Along z, across the beam; 6.4 reads it on a lateral, pedicle to pedicle, with both sides superimposed and divided by M (1.23 at 110 cm, 2.5). mitra2002's lateral pedicle-to-pedicle spacing read 3.0 to 5.7 mm high, which 6.4 lays to the overlap of the two sides' pedicles, so the superimposition is the lateral's bias.
Oblique view: A chord along z keeps its whole length under any beam in the xy plane, so a 45-degree oblique keeps it (foreshortening 1); the pedicle borders stay the landmarks and the reread states no oblique reading.
Magnification-free form: none named for it in 6.4 (the notch over body depth and the disc's anterior over posterior height belong to other measures).
Readability: both
Sources: measures.md 2.4 (O3), 2.5, 6.4 (the intervertebral foramen; pedicle-to-pedicle spacing), 7.2 (c), 11.9; column.foramen, column.disc, pedicle.one_side, pedicle.coronal_sweep, pedicle.axis_from, pedicle.isthmus, pedicle.measures, measure.measure_volume, morphoview.lines.discs, morphoview.lines.pedicles.

### foramen_w (length, mm)

Definition (vocabulary.csv): intervertebral foramen width (anteroposterior)
The 3-D construction (not in the engine yet): not in the engine: the reread writes no mask recipe for a foraminal anteroposterior width; 6.4 cites shin2024's axial and sagittal foraminal widths (narrowest at L4/5, slightly wider at L5/S1) without one, and the nearest recipe it prescribes is amonookuofi1985's inferior vertebral notch, one instance: in the parasagittal plane through each pedicle, below the pedicle, the largest front-to-back gap (the engine's y) between the back of the body (label 49) and the front of the arch (label 41 or 47/48), each side and the mean, offered as an index of the foramen's size.
AP view: A chord along y lies along the beam; nothing; 6.4 gives no AP reading for the foramen's width or the notch.
Lateral view: Along y, across the beam, it keeps its length; 6.4 (Inference) reads the notch on a lateral as the width of the foramen's upper bay below the pedicle, divided by M, the foramen's lucency bounded in front by the posterior body or disc and behind by the articular process, both sides superimposed.
Oblique view: 0.71 of the chord, under the floor; the oblique opens the pars and the facet joint, not the foramen's width, and the reread states no oblique reading.
Magnification-free form: Notch over body depth on one lateral (6.4: about 0.30 at L1 falling to 0.20 to 0.23 at L5, ratios of group means with no SD).
Readability: lateral
Sources: measures.md 2.5, 6.4 (the intervertebral foramen; the inferior vertebral notch), 11.9, 12; no engine function (a grep of morphometry/canal.py, column.py, measure.py and morphoview/lines.py for foramen finds column.foramen's height only).

### foramen_area (area, mm2)

Definition (vocabulary.csv): intervertebral foramen area
The 3-D construction (not in the engine yet): not in the engine: the reread prescribes no mask recipe; 6.4 cites shin2024's foraminal area (largest at L3/4, smallest at L5/S1) with none, and 11.9 lists the foramen's height alone among the features the set supports. The geometry a recipe would take is the parasagittal plane through the pedicles' centroids (normal x), the patch bounded by the upper pedicle's caudal surface, the lower pedicle's cranial surface, the body and disc in front and the facet joint behind, two instances.
AP view: A parasagittal area (normal x) is edge-on to a beam along y, area factor 0; nothing, and 6.4 states no radiograph for it.
Lateral view: The normal runs along the beam, so the patch shows face on (area factor 1) scaled by M squared, about 1.51 at 110 cm, as the foramen's lucent outline with both sides superimposed; the reread states a film reading for the foramen's height and the notch and none for the area, and shin2024's area is a CT reading, so the lateral is permitted by geometry and not vouched for by the reread.
Oblique view: At 45 degrees the area keeps cos 45, 0.71, under the 0.9 floor; fails.
Magnification-free form: none; an area scales by M squared and 6.4 names no ratio for it.
Readability: lateral
Sources: measures.md 2.4 (O2), 2.5, 6.4 (the intervertebral foramen), 11.9, 12; no engine function (the same grep).

## Not drafted

55 of the 106 keys have no row yet (the drafting passes for the laminae and processes, the facets, the pelvis and alignment, and the measures that are not a vertebra's geometry did not run). Each is to be written as the rows above are, from the same three sources:

- spinous_length (length, mm, SPL): spinous process length: from the posterior wall of the canal to the tip of the process
- transverse_width (length, mm, TPW): transverse process width: from the tip of one transverse process to the tip of the other
- pars_area (area, mm2, PIAr): pars interarticularis cross-sectional area
- uncovertebral_area_upper (area, mm2, UJAru): uncovertebral joint surface area, upper joint
- uncovertebral_area_lower (area, mm2, UJArl): uncovertebral joint surface area, lower joint
- uncovertebral_incl_frontal_upper (angle, deg, UJIfu): uncovertebral joint inclination to the frontal plane, upper joint
- uncovertebral_incl_sag_upper (angle, deg, UJIsu): uncovertebral joint inclination to the sagittal plane, upper joint
- uncovertebral_incl_frontal_lower (angle, deg, UJIfl): uncovertebral joint inclination to the frontal plane, lower joint
- uncovertebral_incl_sag_lower (angle, deg, UJIsl): uncovertebral joint inclination to the sagittal plane, lower joint
- costovertebral_area_upper (area, mm2, CVAur): costovertebral articulation surface area, upper (superior) demifacet
- costovertebral_area_lower (area, mm2, CVAlr): costovertebral articulation surface area, lower (inferior) demifacet
- costovertebral_area (area, mm2, CVA): costovertebral articulation surface area, the total per rib
- costotransverse_area (area, mm2, CTAr): costotransverse articulation surface area
- rib_articulation_area (area, mm2, CVA + CTA): costovertebral and costotransverse articulation area, the total per rib
- facet_w_sup (length, mm, FCWsr): superior facet width: the transverse extent of the superior articular facet
- facet_w_inf (length, mm, FCWir): inferior facet width
- facet_h_sup (length, mm, FCHsr): superior facet height: the craniocaudal extent of the superior articular facet
- facet_h_inf (length, mm, FCHir): inferior facet height
- facet_area_sup (area, mm2, FCAsr): superior facet surface area
- facet_area_inf (area, mm2, FCAir): inferior facet surface area
- interfacet_w_sup (length, mm, IFWs): superior interfacet width: from the centre of the right superior facet to the centre of the left
- interfacet_w_inf (length, mm, IFWi): inferior interfacet width
- interfacet_h (length, mm, IFHr): interfacet height: from the centre of the superior facet to the centre of the inferior facet of the same side
- facet_trans_sup (angle, deg, Tsr): superior facet angle to the transverse plane
- facet_trans_inf (angle, deg, Tir): inferior facet angle to the transverse plane
- facet_sag_sup (angle, deg, Ssr): superior facet angle to the sagittal plane (the right side negative by the paper's convention)
- facet_sag_inf (angle, deg, Sir): inferior facet angle to the sagittal plane
- facet_card_x_sup (angle, deg, CAXsr): card angle of the superior facet normal about the X axis
- facet_card_x_inf (angle, deg, CAXir): card angle of the inferior facet normal about the X axis
- facet_card_y_sup (angle, deg, CAYsr): card angle of the superior facet normal about the Y axis
- facet_card_y_inf (angle, deg, CAYir): card angle of the inferior facet normal about the Y axis
- lamina_thickness (length, mm): lamina thickness
- lamina_h (length, mm): lamina height
- lamina_w (length, mm): lamina width or length
- lamina_angle (angle, deg): lamina angle
- pars_w (length, mm): pars interarticularis width or thickness
- spinous_h (length, mm): spinous process height
- spinous_angle (angle, deg): spinous process angle
- transverse_length (length, mm): one transverse process's length (right, left or mean)
- transverse_h (length, mm): transverse process height or thickness
- facet_angle_axial (angle, deg): facet joint orientation in the axial plane, to the midsagittal (or coronal) plane; the note says which reference and convention
- facet_angle_sagittal (angle, deg): facet joint orientation in the sagittal plane
- facet_tropism (angle, deg): facet tropism: the difference between left and right facet angles
- facet_gap (length, mm): facet joint space width
- rib (other, as printed): any rib or costal measure; the note says which
- sacrum (other, as printed): any sacral or pelvic measure; the note says which
- alignment (angle, deg): a curvature or alignment angle over several levels (lordosis, kyphosis, Cobb, sacral slope)
- subject_age (years, years): the age of the subjects
- subject_height (length, mm): the stature of the subjects (cm or m)
- subject_weight (other, as printed): the weight of the subjects (kg)
- subject_bmi (other, as printed): body mass index
- subject_count (count, count): a count of subjects, specimens, vertebrae or cases (the note says of what)
- prevalence (percent, %): a count or share of an anomaly, variant or finding (the note says which)
- reliability (other, as printed): an ICC, kappa, repeat difference or other reliability figure
- other (other, as printed): a value no key above fits: the note says what it is
