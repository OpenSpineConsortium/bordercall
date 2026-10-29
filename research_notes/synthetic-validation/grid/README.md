# The second part on the grid

The owner's word of 2026-10-29 23:03 UTC: the final rerun of run_all.py and run.py runs on the
grid, not in a container. The grid search is 480 independent points on three tables, so it is a
Slurm array; the merge reads the points and writes the same records a serial run writes, to the
bit (run_all.py, read_points; checked on the quick grid). Three jobs, queued through SchwingNet's
grid/hpcw.sh from a bordercall clone on the grid, each waiting afterany on the one before; the
count is the owner's.

```
source ~/SchwingNet/grid/hpcw.sh; REPO=~/SchwingNet
S=$NOTE/grid/sweep.sbatch           # NOTE is this folder's path in the clone
setup=$(hpcw_submit synthval_setup batch STEP=setup BORDERCALL=~/bordercall -- "$S")
hpcw_after "afterany:$setup"
points=$(hpcw_submit synthval_point batch STEP=point BORDERCALL=~/bordercall "${HPCW_AFTER[@]}" --array 0-479 --cpus 2 --mem 8G --time 02:00:00 -- "$S")
hpcw_after "afterany:$points"
merge=$(hpcw_submit synthval_merge batch STEP=merge BORDERCALL=~/bordercall "${HPCW_AFTER[@]}" --cpus 4 --mem 16G --time 04:00:00 -- "$S")
```

Afterwards the records under records/ and records/all/ are committed from the clone to the claim's
branch (every record is byte-identical to a container's but RECORD.json's and RECORD_ALL.json's
seconds and host), and figures.py is run again so FIGURES.md names the committed records. Not yet
run on the grid as of 2026-10-29; the records committed with pull request 38 are a container's.
