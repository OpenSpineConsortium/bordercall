"""Two runs of probe.py cerv side by side: the error, the band and the freedom.

  cmp_cerv.py <base logs, comma separated> <new logs, comma separated>
"""
import re
import sys


def parse(paths):
    out = {}
    for p in paths.split(","):
        for line in open(p):
            m = re.match(r"(C5 \S+ \S+ lean \S+ ped_z \S+) half (\S+)\s+err\s+(\S+) .*parted (\S+)\s+across (\S+) free\s+(\S+)", line)
            if m:
                out[m.group(1)] = (float(m.group(2)), float(m.group(3)), m.group(4), float(m.group(6)))
    return out


a, b = parse(sys.argv[1]), parse(sys.argv[2])
for sp in ("thin", "thick"):
    ea = [abs(a[k][1]) for k in a if " %s " % sp in k]
    eb = [abs(b[k][1]) for k in b if " %s " % sp in k and k in a]
    for k in sorted(a):
        if " %s " % sp in k and k in b:
            print("%-34s half %.2f err %+6.2f free %5.2f | half %.2f err %+6.2f free %5.2f %s" % (
                k, a[k][0], a[k][1], a[k][3], b[k][0], b[k][1], b[k][3], b[k][2]))
    print("== %s: max |err| %.2f -> %.2f, mean %.2f -> %.2f over %d" % (
        sp, max(ea), max(eb), sum(ea) / len(ea), sum(eb) / len(eb), len(eb)))
