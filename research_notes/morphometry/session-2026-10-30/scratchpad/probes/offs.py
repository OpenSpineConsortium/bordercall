"""Every line end and middle more than a pixel off its level's shadow, per recorded view."""
import os
import sys

sys.path.insert(0, sys.argv[1])
from morphoview.tests import test_projection as T  # noqa: E402


class L(T.Lines):
    pass


L.setUpClass()
for got in L.views:
    print("==", got["name"])
    for row, line in zip(L.rows, got["lines"]):
        offs = {k: float(line[k + "_off_px"]) for k in ("a", "b", "mid")}
        if row["key"] == "canal_ap_lateral_film" or max(offs.values()) > T.LAND_PX:
            print("  %-6s %-26s %-22s a %5.2f b %5.2f mid %5.2f" % (row["level"], row["key"], row["part"],
                                                                 offs["a"], offs["b"], offs["mid"]))
