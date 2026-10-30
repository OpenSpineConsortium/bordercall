"""Rewrites the comments on body.py's wall constants; run once by path."""
import sys

path = sys.argv[1]
text = open(path).read()
old = text[text.index("WALL_HEIGHT_SHARE = 0.6"):text.index("WALL_TRIM_STEPS = 30")]
new = '''WALL_HEIGHT_SHARE = 0.6       # the middle share of the height the body's points in the band span, clear of the rims
                              # and their lips
WALL_BAND_SHARE = 0.25        # the band reaches this share of the canal's width either side of the midline, half the
                              # canal's width in all, so the canal stands behind it
WALL_BAND_MAX_MM = 6.0        # and no more than this either side, so a wide lumbar canal's band stops short of the
                              # pedicles; on the cervical phantom (body 17 mm wide, canal 24) it is the whole 6 mm
WALL_GATE_SHARE = 0.25        # an edge lies within this share of the canal's depth of the canal's line: past that
                              # line's error on a clean wall (up to 3.7 degrees on 1 mm slices, 7.7 on 2.5 mm), short of
                              # the lamina; a notch leans the line (18.7 degrees through the suite's at mid-height) and
                              # the gate with it, and WALL_DROPPED_SHARE refuses what that leaves off the fit
WALL_RUN_MM = 3.0             # an edge stands at the back of this much solid bone, so a speck in the canal is no edge
WALL_TRIM_KEEP = 0.75         # the trimmed fit keeps this share: a notch or a lip holding more of the edges is not told
                              # from the wall
WALL_DROPPED_SHARE = 0.4      # not read where more of the band's edges than this lie more than a step off the fit: an
                              # 8 by 6 by 5 mm notch left 66 and 69 per cent and read 29 degrees off, and no reading
                              # of the cache, clean or altered, left more than 26 (1 mm slices) or 36 (2.5 mm)
WALL_BIWEIGHT_STEPS = 2.0     # the biweight's scale in lattice steps along y; a clean digitisation's edges lie within
                              # half a step
WALL_PART_MM = 1e-6           # a surface parts two centres only by more than this, so a centre on it parts nothing
WALL_ACROSS_MAX = 3           # the clamp sets aside at most this many edges the fit leaves furthest across, as specks
                              # behind the wall are, and no more
WALL_FREEDOM_DEG = 9.0        # not read where the lattice leaves the slope freer than this: pedicle.FREEDOM_DEG, kept
                              # here since pedicle imports this module
WALL_FREE_FLAG_DEG = 3.0      # flagged where freer than this, twice the suite's 1.5 degrees on the angles taken
                              # against it, since a reading may lie anywhere in its range
'''
assert text.count(old) == 1
open(path, "w").write(text.replace(old, new))
