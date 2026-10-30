"""The words left after round three: the reading again's share, the phantoms the export's tests
use, the hold on the counted jobs, and the README's counts of keys with no line."""
import sys
root = sys.argv[1]


def edit(rel, pairs):
    path = root + "/" + rel
    src = open(path).read()
    for old, new in pairs:
        assert src.count(old) == 1, (rel, old[:70], src.count(old))
        src = src.replace(old, new)
    open(path, "w").write(src)


edit("research_notes/morphometry/handoff.md", [
("""  reading pedicle.one_side again took 8 of a study's 11 s of drawing on the phantom; on a vertebra
  the volume's edge cuts, whose values the measure blanks, it reads the side again.
""", """  reading pedicle.one_side again took five sixths of a study's drawing on the phantoms (3.5 of
  4.2 s of CPU on L2 to L4 at 0.8 by 0.8 by 1 mm); on a vertebra the volume's edge cuts, whose
  values the measure blanks, it reads the side again.
"""),
("""- then the owner's count of three, enhance, verse and the covariates join, one at a time.
""", """- then the owner's count of three, enhance, verse and the covariates join, one at a time, which
  the owner held at 14:45 UTC until a resynthesis.
"""),
("""- morphometry/tests/test_lines_export.py, @N_EXPORT@ tests on phantoms written as label files: L2
  to L4 straight, the same cut through L4's body by the volume's edge, a thick-sliced pair and the
  chain whose joints open, tilt, turn and slip. The engine's suite, @N_SUITE@ tests, passes
  (@SECS@ s on four shared CPUs).
""", """- morphometry/tests/test_lines_export.py, @N_EXPORT@ tests on phantoms of L2 to L4: straight at 0.8
  by 0.8 by 1 mm, the same cut through L4's body by the volume's edge, the same on 2.5 mm slices,
  and a chain whose joints open 8 degrees, tilt 4, turn 5 and slip 4 mm. The engine's suite,
  @N_SUITE@ tests, passes (@SECS@ s on four shared CPUs).
"""),
])

edit("research_notes/morphometry/README.md", [
("the other keys, @UNLINED@ of the @LUMBAR_KEYS@ a lumbar vertebra's rows hold,",
 "the other keys, 56 of the 81 a lumbar vertebra's rows hold,"),
])
print("ok")
