"""The reviewer's C5 read with its pedicles as drawn and with their roots' lip clipped where it
stands outside the body within 7 mm of the midline, each at the band's caps of 6 and 3 mm, so the
pedicles' share of the error is told from the rest. Arguments: spacing name, ped_z values, leans,
tilt names, each comma-separated."""
import math
import sys
import time

from common import CERVICAL, SPACINGS, TILTS, build, read_at, root_edges
from morphometry.tests import phantom as P


def cell(err, info):
    if not math.isfinite(err):
        return "NAN (%s)" % info.get("why", "")
    return "%+.2f f%.2f%s" % (err, info["free_deg"], "p" if info["parted"] else "")


def main():
    sname = sys.argv[1]
    ped_zs = [float(x) for x in sys.argv[2].split(",")]
    leans = [float(x) for x in sys.argv[3].split(",")]
    tilts = sys.argv[4].split(",")
    for ped_z in ped_zs:
        for tname in tilts:
            for lean in leans:
                for clip in (False, True):
                    t0 = time.perf_counter()
                    vert = P.lumbar(lean=lean, **dict(CERVICAL, ped_z=ped_z))
                    v, placed = build(["C4", "C5", "C6"], "C5", vert, SPACINGS[sname], TILTS[tname], clip=clip)
                    tag = "%s ped_z%+.0f %-7s lean%+.0f %s" % (sname, ped_z, tname, lean, "clip" if clip else "orig")
                    if "all" in v.flags:
                        print("%-36s NOT BUILT: %s" % (tag, v.flags["all"]), flush=True)
                        continue
                    e6, i6 = read_at(v, placed, lean, 6.0)
                    e3, i3 = read_at(v, placed, lean, 3.0)
                    r = root_edges(v)
                    diag = ("edges %d, beyond 5 mm up %d (r %+.2f) down %d (r %+.2f), inner r %+.2f"
                            % (r["n"], r["n_up"], r["r_up"], r["n_down"], r["r_down"], r["r_inner"])) if r else "-"
                    print("%-36s cap6 %-16s cap3 %-16s half %.2f | %s | %.0fs" % (
                        tag, cell(e6, i6), cell(e3, i3), i6.get("half_band_mm", float("nan")), diag,
                        time.perf_counter() - t0), flush=True)


if __name__ == "__main__":
    main()
