"""Probe: the SEVEN chords without a line against the nearest keys that have one, on L3 of the
straight phantom."""
from morphometry import measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G
LEVELS = ["L2", "L3", "L4"]
lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
kept = {}
M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "near", pelvis=False, keep=kept)
vals = kept["values"]["L3"]
for a, b in (("h_post", "h_post_inset"), ("canal_w", "interpedicular"), ("canal_ap", "canal_ap_min")):
    print("%-8s %.3f   %-14s %.3f" % (a, vals[a], b, vals[b]))
