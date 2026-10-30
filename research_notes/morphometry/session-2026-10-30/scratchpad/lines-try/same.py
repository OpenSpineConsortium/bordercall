import sys, time
import numpy as np
from morphometry import measure as M
from morphoview import lines as LN
kept = {}
M.measure_file(sys.argv[1], "verse", "0001", keep=kept)
worst, n = 0.0, 0
for lv, v in kept["verts"].items():
    t0 = time.time(); a = LN.checked(LN.vertebra_lines(v, kept["peds"][lv]), kept["values"][lv]); t1 = time.time()
    b = LN.checked(LN.vertebra_lines(v, kept["peds"][lv], kept["values"][lv]), kept["values"][lv]); t2 = time.time()
    assert [x.key for x in a] == [x.key for x in b], (lv, [x.key for x in a], [x.key for x in b])
    for x, y in zip(a, b):
        assert x.status == y.status == "drawn", (lv, x.key, x.status, y.status)
        d = max(abs(x.value - y.value), float(np.abs(x.a - y.a).max()), float(np.abs(x.b - y.b).max()))
        worst = max(worst, d); n += 1
    print(lv, "%.2f s again, %.2f s reused" % (t1 - t0, t2 - t1))
print("lines compared", n, "largest difference", worst)
