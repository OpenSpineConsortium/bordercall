import csv, sys
from collections import defaultdict
def keys(path):
    by = defaultdict(set)
    notes = {}
    vals = {}
    for r in csv.DictReader(open(path, newline="")):
        lvl = r["level"]
        kind = "study" if lvl == "study" else ("disc" if "-" in lvl else lvl if lvl in ("column", "pelvis") else "vertebra")
        by[kind].add(r["key"])
        vals[(r["study"], lvl, r["key"])] = (r["value"], r["note"])
    return by, vals
old, ov = keys(sys.argv[1]); new, nv = keys(sys.argv[2])
for kind in sorted(set(old) | set(new)):
    o, n = old.get(kind, set()), new.get(kind, set())
    print("==", kind, "old", len(o), "new", len(n))
    print("   only old:", sorted(o - n))
    print("   only new:", sorted(n - o))
VK = ("h_ant", "h_mid", "h_post", "h_post_inset", "body_w_mid", "body_d_mid", "endplate", "endplate_depth",
      "endplate_lower", "endplate_lower_depth", "endplate_area", "endplate_lower_area", "wedge", "canal_w",
      "canal_ap", "canal_area", "interpedicular", "pedicle_w", "pedicle_h", "pedicle_chord", "pedicle_area",
      "pedicle_angle_transverse", "pedicle_angle_sagittal", "spinous_length", "transverse_width",
      "lamina_thickness")
DK = ("disc_h_ant", "disc_h_mid", "disc_h_post", "disc_h_mean", "foramen_h")
print("join vertebra keys missing in new:", [k for k in VK if k not in new["vertebra"]])
print("join vertebra keys missing in old:", [k for k in VK if k not in old["vertebra"]])
print("join disc keys missing in new:", [k for k in DK if k not in new.get("disc", set())])
print("join disc keys missing in old:", [k for k in DK if k not in old.get("disc", set())])
print("report keys:", [(k, k in new["vertebra"]) for k in ("h_ant", "h_post_inset", "body_index_ant_post")])
print("study keys new:", sorted(new["study"]))
# values side by side for the join's keys at L3 of 0001
for k in VK + ("interpedicular_max",):
    a = ov.get(("0001", "L3", k)); b = nv.get(("0001", "L3", k))
    print("0001 L3 %-26s old %-12s new %-12s %s" % (k, a and a[0], b and b[0], (b and b[1])[:60] if b else ""))
for k in DK:
    a = ov.get(("0001", "L2-L3", k)); b = nv.get(("0001", "L2-L3", k))
    print("0001 L2-L3 %-23s old %-12s new %-12s" % (k, a and a[0], b and b[0]))
flags_new = sorted({(s, l, k) for (s, l, k) in nv if k.startswith("flag")})
flags_old = sorted({(s, l, k) for (s, l, k) in ov if k.startswith("flag")})
print("flags old:", flags_old)
print("flags new:", flags_new)
