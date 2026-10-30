"""timed.py CMD...: run CMD, then print its wall time, the peak memory of it and its waited
descendants, and its exit code to stderr."""
import resource
import subprocess
import sys
import time

t0 = time.time()
rc = subprocess.call(sys.argv[1:])
peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
print("%.1f s wall %d KB maxrss rc %d" % (time.time() - t0, peak, rc), file=sys.stderr)
