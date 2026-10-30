import sys
path, tpath = sys.argv[1], sys.argv[2]
src = open(path).read()
def swap(s, old, new):
    assert s.count(old) == 1, old[:60]
    return s.replace(old, new)
src = swap(src, '''    "h_ant": "anterior height", "h_mid": "middle height", "h_post_inset": "posterior height", "wedge": "wedge",''',
'''    "h_ant": "anterior height", "h_mid": "middle height", "h_post_inset": "posterior height",
    "h_post": "posterior height at the wall", "wedge": "wedge",''')
src = swap(src, '''    "endplate_lower_depth": "lower end-plate depth", "canal_ap_min": "least canal depth",''',
'''    "endplate_lower_depth": "lower end-plate depth", "canal_ap_min": "least canal depth",
    "canal_w": "canal width", "canal_ap": "canal depth",''')
# the canal's width lies in the body's middle half, not at the pedicles the axial panel is cut through
src = swap(src, '''            and not ln.key.startswith(("canal_ap_lateral_film", "tp_span", "interpedicular"))]''',
'''            and not ln.key.startswith(("canal_ap_lateral_film", "tp_span", "interpedicular", "canal_w"))]''')
open(path, "w").write(src)
t = open(tpath).read()
t = swap(t, '''BONE_WITHIN = ("h_ant", "h_mid", "h_post_inset", "body_d_mid", "body_w_mid", "endplate", "endplate_lower", "tp_span",
               "pedicle_chord_right", "pedicle_chord_left")
CANAL_WITHIN = ("canal_ap_min", "interpedicular")''', '''BONE_WITHIN = ("h_ant", "h_mid", "h_post_inset", "h_post", "body_d_mid", "body_w_mid", "endplate", "endplate_lower",
               "tp_span", "pedicle_chord_right", "pedicle_chord_left")
CANAL_WITHIN = ("canal_ap_min", "interpedicular", "canal_w", "canal_ap")''')
open(tpath, "w").write(t)
print("ok")
