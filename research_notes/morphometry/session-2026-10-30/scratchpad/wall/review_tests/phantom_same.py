"""Whether the new phantom.py draws the suite's old phantoms voxel for voxel as the base commit's
did, and gives the same truths: each old test class's phantom drawn by both modules.

    phantom_same.py BASE_PHANTOM_FILE"""
import importlib.util
import sys

import numpy as np

from morphometry.tests import phantom as NEW


def load(path):
    spec = importlib.util.spec_from_file_location("base_phantom", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["base_phantom"] = mod
    spec.loader.exec_module(mod)
    return mod


def cases(P):
    L = ["L2", "L3", "L4"]
    yield "straight", P.straight(L, P.Vert()), {}
    yield "shapes", P.straight(L, P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0,
                                             sp_angle=32.0)), {}
    yield "thick", P.straight(L, P.Vert(), tilt=((1.0, 0.0, 0.0), 20.0)), {"spacing": (0.86, 0.86, 2.5),
                                                                           "grid_turn": ((0.0, 0.0, 1.0), 0.0)}


def main():
    OLD = load(sys.argv[1])
    for (name, new_placed, kw), (_, old_placed, _) in zip(cases(NEW), cases(OLD)):
        a, aff_a = NEW.draw(new_placed, **kw)
        b, aff_b = OLD.draw(old_placed, **kw)
        same = a.shape == b.shape and np.array_equal(a, b) and np.allclose(aff_a, aff_b, atol=0)
        print("%s: labels %s, %d labelled voxels" % (name, "identical" if same else "DIFFER", int((a > 0).sum())))
    for vert in (NEW.Vert(), NEW.lumbar(Ha=30.0, concavity=2.0, waist=0.92)):
        t_new = NEW.truth(vert)
        kw = {k: getattr(vert, k) for k in ("Ha", "concavity", "waist")}
        t_old = OLD.truth(OLD.lumbar(**kw))
        diff = [k for k in t_old if not np.allclose(t_old[k], t_new.get(k), equal_nan=True)]
        print("truth keys differing: %s" % (diff or "none"))


if __name__ == "__main__":
    main()
