"""Which of the wall reader's paths a logged run reached: how many readings parted the label,
how far the clamp moved the slope, the largest freedom against the flag's and the refusal's
bounds, and every refusal's reason.

    paths.py LOG.json"""
import json
import sys
from collections import Counter


def main():
    with open(sys.argv[1]) as f:
        log = json.load(f)
    rows = log["readings"]
    read = [r for r in rows if r.get("slope_deg") is not None]
    print("mutant %s: %d readings, %d read, %d refused; failures %s errors %s" % (
        log["mutant"], len(rows), len(read), len(rows) - len(read), log["failures"], log["errors"]))
    print("parted: %s" % dict(Counter(bool(r.get("parted")) for r in read)))
    moved = [abs(r.get("clamp_moved_deg", 0.0)) for r in read]
    print("clamp moved the slope in %d of %d, by at most %.4f degrees" % (
        sum(m > 1e-9 for m in moved), len(read), max(moved or [0.0])))
    free = [float(r["free_deg"]) for r in read if "free_deg" in r]
    print("freedom: largest %.3f degrees; over 3: %d; over 9: %d" % (
        max(free or [0.0]), sum(x > 3.0 for x in free), sum(x > 9.0 for x in free)))
    print("dropped edges: largest %d" % max([int(r.get("dropped", 0)) for r in read] or [0]))
    for r in rows:
        if r.get("slope_deg") is None:
            print("refused at %s: %s" % (r["level"], r.get("why")))
    print("readings per level: %s" % dict(Counter(r["level"] for r in rows)))


if __name__ == "__main__":
    main()
