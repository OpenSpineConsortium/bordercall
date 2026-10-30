import sys; sys.path.insert(0, "/home/user/bordercall")
from morphometry.tests import phantom as P
v = P.lumbar(sap_x=19.0, sap_y=-10.0, facet=0.0, sap_thk=3.5, sap_len=14.0)
try:
    P.draw(P.straight(["L2", "L3", "L4"], v), spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), strict=True)
    print("strict draw: no collision")
except ValueError as e:
    print("strict draw raises:", e)
