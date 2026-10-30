"""The wall on a thoracic-sized phantom (about a T8): a body 30 mm wide and 26 deep, 20 tall, under
a canal 16 mm wide, so the band is a quarter of the canal's width (4 mm); thin slices."""
import sys

from common import draw_and_build, show
from morphometry.tests import phantom as P

THORACIC = dict(W=30.0, D=26.0, Hp=20.0, Ha=20.0, canal_w=16.0, ped_w=6.0, ped_h=12.0, ped_z=3.0, ped_back=4.0,
                ped_t=5.0, pil_x=13.0, pil_y=-11.0, lam_t=5.0, lam_ap_top=15.0, lam_slope=15.0, lam_top=7.0,
                lam_bot=-10.0, sap_x=14.0, sap_y=-12.0, sap_len=10.0, sap_thk=4.0, sap_top=18.0, iap_x=12.0,
                iap_y=-16.0, iap_len=10.0, iap_thk=4.0, iap_bot=-18.0, facet=70.0, TP=60.0, tp_y=-12.0, tp_h=9.0,
                LS=30.0, sp_angle=40.0)
spacing = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}[sys.argv[1] if len(sys.argv) > 1 else "thin"]
for tname, tilt in (("x2", ((1.0, 0.0, 0.0), 2.0)), ("suite18", ((1.0, 0.3, 0.0), 18.0))):
    for lean in (0.0, 5.0, -5.0):
        v, placed, _, _ = draw_and_build(["T7", "T8", "T9"], "T8", P.lumbar(lean=lean, **THORACIC), spacing=spacing,
                                         tilt=tilt)
        show("T8 %s lean%+.0f" % (tname, lean), v, placed, lean)
