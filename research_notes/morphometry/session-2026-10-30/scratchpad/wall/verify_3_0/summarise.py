"""Summarise speck_all.log: per thickness, how many specks broke the parting of a parted label,
and the largest error then against the largest clean error."""
import re
import sys

rows = {"thin": [], "thick": []}
clean = {"thin": [], "thick": []}
sp = None
for line in open(sys.argv[1]):
    m = re.match(r"(\S+) clean ([-+.\d]+) fit ([-+.\d]+) parted (\w+)", line)
    if m:
        sp = "thin" if m.group(1).endswith("thin") else "thick"
        was = m.group(4) == "True"
        clean[sp].append(abs(float(m.group(2))))
        continue
    m = re.search(r"kept (\w+)\s+parted (\w+)\s+err\s+([-+.\dnan]+)", line)
    if m and was:
        rows[sp].append((m.group(1) == "True", m.group(2) == "True", float(m.group(3))))
for s in rows:
    r = rows[s]
    broke = [x for x in r if not x[1]]
    big = [x for x in broke if abs(x[2]) > 0.5]
    errs = [abs(x[2]) for x in r if x[2] == x[2]]
    print("%s: %d specks on parted labels, %d broke the parting, %d of those past 0.5; largest |err| with a speck %.2f, clean %.2f; refused %d"
          % (s, len(r), len(broke), len(big), max(errs), max(clean[s]), sum(1 for x in r if x[2] != x[2])))
