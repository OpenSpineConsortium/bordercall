# Rule 6 of the full-spine completion, calibrated on SPINEPS's own masks

Source: the thread of the project symphony_4 that completes the gold tier 3 CTs' C2 and sacrum with
SPINEPS, 2026-10-29, on the owner's word of 03:32 UTC ("segment the c2 and sacrums which are on ct
volumes they just lack the masks and convert them all to gold tier 3 data") and his choice at 04:23 UTC
to run SPINEPS's CT models in the thread's cloud container. Confidential, like the rest of this
repository; no mask or CT is here, only numbers read from them.

## What rule 6 is for

holdings/fullspine_complete.py names a segmenter's level for a level the release does not draw only
where the segmenter's own subregion mask shows one whole body there. Rule 6 is that check. It reads the
disc between a body and each of its neighbours: exactly one run of disc between the two bodies'
centres, inside a cylinder about the line joining them, and the body read against that run in the
run's own frame. The run's plane is fitted to its voxels and cut into 4 mm cells; in each cell holding
three disc voxels or more, the disc's near and far surfaces are its voxels' least and greatest heights
along the plane's normal. A body more than 0.2% of whose voxels stand over 1 mm past the far surface in
their own cell has taken part of its neighbour; a body whose end, as the median over cells, runs more
than 1 mm into the disc or stops more than 3 mm short of it (or one voxel's reach along the normal and
1 mm, where that is more) is wrong at that end. A pair of height and step ratios over 1.25 and 1.12
together reads as two bodies merged with no disc drawn between them.

The cell reading replaced two earlier ones tried the same morning on the same masks: runs of disc read
along the line between the centres alone, and the body read against one flat plane fitted to the whole
disc. A flat plane misreads a wedge-shaped disc or a curved end plate, so a whole body seemed to stand
past it in one part and short of it in another; cut into cells, each part of the disc is read where it
stands.

## What was measured

calibrate_rule6.py reads the masks SPINEPS 2.1.2 wrote for twelve of the CTs the field test asks to
complete (seven VerSe adults, five TotalSegmentator children), calling the module's own column_of,
side_reading and sacrum_check, so the numbers are the shipped code's. Along each segmenter column, head
to foot and foot to head, every body is read against the level it is reached from and the level beyond
it, as it stands and altered by hand: with the 5, 10, 20 or 30% of its outer neighbour's height nearest
it taken in (a body that reaches across the disc), cut short at its outer end with 60, 70, 80 or 90% of
its height kept and the rest dropped, and joined to its outer neighbour with the disc between them
deleted. summarise.py turns readings.json.gz into summary.json.

    PYTHONPATH=. python research_notes/fullspine-rule6-calibration/calibrate_rule6.py readings.json <study folders>
    PYTHONPATH=. python research_notes/fullspine-rule6-calibration/summarise.py readings.json.gz > summary.json

## What it found

On the seven adult VerSe CTs (verse018, verse033, verse255, verse531, verse558, verse559, verse593):

| case | readings | refused |
| --- | --- | --- |
| a body as it stands, against either neighbour | 546 | 0 |
| a body taking 5% of its outer neighbour's height | 266 | 151 |
| taking 10% | 266 | 222 |
| taking 20% | 266 | 259 |
| taking 30% | 266 | 266 |
| a body cut short, 60% of its height kept | 266 | 256 |
| 70% kept | 266 | 226 |
| 80% kept | 266 | 140 |
| 90% kept | 266 | 4 |

As they stand, every reading found exactly one run of disc, no body had more than 0.017% of its
voxels past the far surface, and the median gaps ran from 0.16 to 2.94 mm, the largest on verse018's
1 x 1 x 3 mm grid. No single body of 266 passed both merge ratios (none with a height ratio over 1.25 had
a step ratio over 1.07, none with a step ratio over 1.12 a height ratio over 1.17), and all 252 joined
pairs passed both (none under 1.29 and 1.15). Each sacrum held one run of disc within 10 mm of its head
end; verse559's holds a second, 5,140 voxels against its L5/S1 disc's 26,129, 31 to 40 mm below its head
end, which is its S1/S2 disc and no reason to refuse it, so the sacrum is refused only for a run inside
it holding half the disc above it or more.

On the five TotalSegmentator children (s1411, s1532, s1593, s1606, s2065), whose spines SPINEPS was not
trained on, 84 of 358 readings as they stand are refused, and 14 of 174 single bodies pass both merge
ratios. These are not the readings the rule is set by: the two arms disagree there on where the bodies
lie, and the rules refuse every target before rule 6 is reached (below).

## What it does not see

- A body that took part of its neighbour outside the disc's own cells, or through the arch, is not
  read here; the body's pieces (its largest holding 98% of it) and rule 5's share under the release's
  levels catch some of it.
- A body short by a tenth of its height is not told from a whole one (4 of 266 refused); its gap_mm is
  in the record for a person.
- The cases altered by hand are made from real bodies, not from a segmenter's real failures; no real
  failure of these kinds was found in the seven adults' masks.

## The run over the twelve, end to end

end_to_end.json is the matcher's outcome on the twelve, with every refusal's reason, from the code as
it stands: the VerSe adults gain verse018's C7, verse033's and verse255's C6, verse559's C2 and six
sacra (all but verse018's, whose release stops at L4 with L5 not asked for). In six of the seven the
field test called the head end a border case, and SPINEPS's column stops below C2 (at C3 to C6), so C2
is refused there: in five, the head-most level SPINEPS draws has nothing beyond it to read its outer
side against; in verse593, SPINEPS's C3 is cut by the field's top and 0.59 times the height of its C4,
and is refused with that C4. The
children gain nothing: none of the release's levels is an anchor in s1532, s1593 and s1606, s2065's
anchors are never neighbours in the segmenter's column so rule 7 refuses it, and in s1411 the walk
toward T12 stops at the release's L1, which the segmenter does not match.
