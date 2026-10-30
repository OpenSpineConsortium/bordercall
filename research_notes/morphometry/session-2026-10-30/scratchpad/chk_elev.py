import math, numpy as np
from morphometry.pedicle import axis_from
rows = [{"y": y} for y in (0.0, -2.0, -4.0, -6.0)]
for t, s in ((12.0, 6.0), (30.0, 10.0), (30.0, 15.0), (35.0, 15.0)):
    side = 1
    # the walls' line: x grows by tan t per mm forward (converging toward the front); climb b = dz/dy along +y
    walls = {i: side * (math.tan(math.radians(t)) * r["y"]) for i, r in enumerate(rows)}
    rise = -math.tan(math.radians(s))      # posterior end higher: z falls going forward
    d, note, reads = axis_from(rows, [0, 1, 2, 3], walls, rise, side)
    pitch = math.hypot(d[0], d[1])
    trans = math.degrees(math.atan2(side * d[0], -d[1]))
    sag_code = math.degrees(math.atan2(d[2], pitch))
    sag_proj = math.degrees(math.atan2(d[2], -d[1]))
    print("t %4.1f s %4.1f reads %s | transverse %6.2f | sagittal line 566: %6.2f | projection: %6.2f | atan(tan s cos t): %6.2f"
          % (t, s, reads, trans, sag_code, sag_proj, math.degrees(math.atan(math.tan(math.radians(s)) * math.cos(math.radians(t))))))
