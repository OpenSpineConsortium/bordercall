import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''        # a cap of a sphere of 20 mm cut to a disc of 6, facing along the body's diagonal so every
        # view sees it at a slant
        tilted = SH.Plane(centre + 2.0 * up, across + forward + up)''', '''        # a cap of a sphere of 20 mm cut to a disc of 6, facing half way between the body's side
        # and its front, so each view sees it at 44 degrees or more
        tilted = SH.Plane(centre + 2.0 * up, across - forward)''')
swap('''                for kind, surface in surfaces.items():
                    shade = surface.silhouette(cam)
                    self.assertGreater(int(shade.sum()), 10, (name, pl.level, kind))''', '''                for kind, surface in surfaces.items():
                    shade = surface.silhouette(cam)
                    self.assertGreater(int(shade.sum()), 20, (name, pl.level, kind))''')
open(path, "w", encoding="ascii").write(src)
print("ok")
