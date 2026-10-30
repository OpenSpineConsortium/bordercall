import sys
sys.path.insert(0, sys.argv[1])
from morphometry.tests import phantom as P
for name, v in (("lumbar", P.Vert()), ("cervical", P.cervical())):
    t = P.truth(v)
    print(name, {k: round(x, 2) for k, x in t.items() if k.startswith(("pedicle", "interped", "h_", "body_index", "canal_w"))})
