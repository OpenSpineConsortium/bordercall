"""Run one study's measure and print the peak resident memory and the wall time."""
import resource, sys, time
sys.path.insert(0, sys.argv[1])
from morphometry import measure as M
t = time.time()
rows = M.measure_file(sys.argv[2], "enhance", "x")
print("%s maxrss %.0f MB wall %.1f s rows %d" % (sys.argv[3], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, time.time() - t, len(rows)))
