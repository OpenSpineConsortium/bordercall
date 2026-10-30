"""The wall on a cervical-sized phantom (about a C5, Panjabi 1991's sizes): a body 17 mm wide
and 16 deep under a canal 24 mm wide, so the band (min(6, a quarter of the canal's width)) is
not capped by the body's width, on the grids the lumbar cache uses."""
import sys

from common import draw_and_build, show
from morphometry.tests import phantom as P

CERVICAL = dict(W=17.0, D=16.0, Hp=14.0, Ha=14.0, canal_w=24.0, ped_w=5.5, ped_h=7.0, ped_z=2.0, ped_back=4.0,
                ped_t=45.0, mass_w=7.0, mass_h=10.0, foramen_d=5.5, pil_x=17.0, pil_y=-10.0, lam_t=4.0,
                lam_ap_top=14.0, lam_slope=10.0, lam_top=6.0, lam_bot=-8.0, sap_x=18.0, sap_y=-11.0, sap_len=8.0,
                sap_thk=4.0, sap_top=13.0, iap_x=17.0, iap_y=-13.0, iap_len=8.0, iap_thk=4.0, iap_bot=-13.0,
                facet=80.0, TP=50.0, tp_y=-6.0, tp_thk=5.0, tp_z=1.0, tp_h=6.0, LS=18.0, sp_angle=20.0, sp_hw=2.5,
                sp_hh=3.0)
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5), "fine": (0.4, 0.4, 0.6)}
TILTS = {"x0": ((1.0, 0.0, 0.0), 0.0), "x2": ((1.0, 0.0, 0.0), 2.0), "x5": ((1.0, 0.0, 0.0), 5.0),
         "suite18": ((1.0, 0.3, 0.0), 18.0)}


def main():
    names = sys.argv[1].split(",") if len(sys.argv) > 1 else ["C4", "C5", "C6"]
    which = sys.argv[2].split(",") if len(sys.argv) > 2 else list(SPACINGS)
    extra = dict(kv.split("=") for kv in sys.argv[3].split(",")) if len(sys.argv) > 3 else {}
    kw = dict(CERVICAL, **{k: float(x) for k, x in extra.items()})
    for sname in which:
        for tname, tilt in TILTS.items():
            for lean in (0.0, 5.0):
                v, placed, _, _ = draw_and_build(names, names[1], P.lumbar(lean=lean, **kw), spacing=SPACINGS[sname],
                                                 tilt=tilt)
                show("%s %s %s lean%+.0f" % (names[1], sname, tname, lean), v, placed, lean)
                if "all" not in v.flags:
                    rings = v.full_rings()
                    print("    rings %d width %.1f ap %.1f body pts %d flags %s" % (
                        len(rings), sum(s.width for s in rings) / len(rings), sum(s.ap for s in rings) / len(rings),
                        int(v.body.sum()), sorted(v.flags)), flush=True)


if __name__ == "__main__":
    main()
