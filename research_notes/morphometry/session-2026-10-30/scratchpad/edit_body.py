"""PR 47's body after round three: the counts of keys with no line, the reading again's share and
the phantoms the export's tests use."""
import sys
path = sys.argv[1]
src = open(path).read()
pairs = [
("The other keys, @UNLINED@ of the @LUMBAR_KEYS@ a lumbar vertebra's rows hold, have no line.",
 "The other keys, 56 of the 81 a lumbar vertebra's rows hold, have no line."),
("since reading `pedicle.one_side` again took 8 of a study's 11 s of drawing on the phantom;",
 "since reading `pedicle.one_side` again took five sixths of a study's drawing on the phantoms (3.5 of 4.2 s of CPU on L2 to L4 at 0.8 by 0.8 by 1 mm);"),
("@N_EXPORT@ tests on phantoms written as label files (L2 to L4 at 0.8 by 0.8 by 1 mm; the same cut through L4's body by the volume's edge; the same on 2.5 mm slices; and a chain whose joints open 8 degrees, tilt 4, turn 5 and slip 4 mm):",
 "@N_EXPORT@ tests on phantoms of L2 to L4 (straight at 0.8 by 0.8 by 1 mm; the same cut through L4's body by the volume's edge; the same on 2.5 mm slices; and a chain whose joints open 8 degrees, tilt 4, turn 5 and slip 4 mm):"),
]
for old, new in pairs:
    assert src.count(old) == 1, (old[:70], src.count(old))
    src = src.replace(old, new)
open(path, "w").write(src)
print("ok")
