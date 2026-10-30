import sys
path = sys.argv[1]
src = open(path).read()
old = '''    out = [(f.__name__, (lambda f=f: f(v))) for f in (heights, wedge, waist, panjabi_plates, panjabi_height,
                                                      least_depth, panjabi_canal, lateral_film, spinous, tp_span)]
    out += [("pedicles", lambda: pedicles(v, ped, vals)), ("interpedicular", lambda: interpedicular(v, ped))]
    return out
'''
new = '''    alone = (("heights", heights), ("wedge", wedge), ("waist", waist), ("panjabi_plates", panjabi_plates),
             ("panjabi_height", panjabi_height), ("least_depth", least_depth), ("panjabi_canal", panjabi_canal),
             ("lateral_film", lateral_film), ("spinous", spinous), ("tp_span", tp_span))
    out = [(name, (lambda f=f: f(v))) for name, f in alone]
    out += [("pedicles", lambda: pedicles(v, ped, vals)), ("interpedicular", lambda: interpedicular(v, ped))]
    return out
'''
assert src.count(old) == 1
open(path, "w").write(src.replace(old, new))
print("ok")
