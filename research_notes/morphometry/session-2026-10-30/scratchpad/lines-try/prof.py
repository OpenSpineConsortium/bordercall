import cProfile, pstats, sys, time
from morphometry import measure as M
from morphometry import __main__ as MM
from morphoview import lines as LN
kept = {}
t0 = time.time(); rows = M.measure_file(sys.argv[1], "verse", "0001", keep=kept); t1 = time.time()
pr = cProfile.Profile(); pr.enable()
lines, frames, flags = MM.study_lines("0001", kept)
pr.disable(); t2 = time.time()
print("measure %.1f s, lines %.1f s, %d line rows" % (t1 - t0, t2 - t1, len(lines)))
st = pstats.Stats(pr); st.sort_stats("cumulative").print_stats(18)
