"""Fill PR 47's handoff and body placeholders with the measured counts."""
import sys
handoff, body, when = sys.argv[1], sys.argv[2], sys.argv[3]


def fill(path, pairs):
    src = open(path).read()
    for old, new in pairs:
        assert src.count(old) == 1, (path, old, src.count(old))
        src = src.replace(old, new)
    assert "@" not in "".join(w for w in src.split() if w.startswith("@") and w.endswith("@")), path
    open(path, "w").write(src)


MUTANTS = ("Each test the fixes added fails with its fix taken out, or with a slip a later change could "
           "make: 28 mutants of the export and its tests, all caught. The first round's 14 caught 13; "
           "the one that lived, the canal's depth read on the wrong section, led to the test that holds "
           "each median's line to the cell or section nearest it. The 13 were run again on the final "
           "tree, and the second round's 15 were caught too, the two that move an end's name run again "
           "once the end-name test read every pair either way round, so a wrong name fails on the "
           "geometry and not on a missing key.")

fill(handoff, [
    ("@WHEN@", when),
    ("@MUTANTS@", MUTANTS),
    ("@N_EXPORT@", "25"),
    ("The engine's suite,\n  @N_SUITE@ tests, passes (@SECS@ s on four shared CPUs).",
     "The engine's suite,\n  75 tests, passes: test_morphometry's 39 in 769 s and the export's and "
     "morphoview's 36 in 229 s,\n  on four CPUs shared with the mutant runs."),
])

fill(body, [
    ("@N_EXPORT@", "25"),
    ("@MUTANTS_SHORT@", "28 mutants, all caught. The first round's one survivor, the canal's depth read "
     "on the wrong section, led to the test that holds each median's line to its cell or section; the "
     "first round's 13 were run again on the final tree, and the two of the second round that move an "
     "end's name were run again once the end-name test read every pair either way round."),
    ("gives @N_SUITE@ tests, all passing (@SECS@ s on four shared CPUs).",
     "gives 75 tests, all passing (test_morphometry's 39 in 769 s, the export's and morphoview's 36 in "
     "229 s, on four CPUs shared with the mutant runs)."),
    ("- @TESTS_AND_WORDS@",
     "- **Fixed, from the review of the tests and the words: no test held a value against its measured,** "
     "a line off its row keeping both values, the stamp following the drawing's code, or a further "
     "segment's own ends. Each has a test now. The timing and the phantoms' wording are corrected (five "
     "sixths, 3.5 of 4.2 s; SameLines measures in memory), and the end-name test reads every pair "
     "either way round."),
])
print("filled")
