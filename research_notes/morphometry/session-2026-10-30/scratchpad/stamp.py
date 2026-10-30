import hashlib, os, sys
def stamp(here):
    h = hashlib.sha256()
    for pkg in ("morphometry", "scanimport"):
        folder = os.path.join(here, pkg)
        for name in sorted(os.listdir(folder)):
            if name.endswith(".py"):
                h.update(name.encode() + b"\0" + open(os.path.join(folder, name), "rb").read())
    return h.hexdigest()[:16]
for p in sys.argv[1:]:
    print(p, stamp(p))
