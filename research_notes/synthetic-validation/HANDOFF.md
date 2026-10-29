# Handoff: the synthetic validation note, second part written up, two steps left

Written 2026-10-29 at 23:15 UTC on the owner's checkpoint word of 23:13 UTC ("CHECKPOINT ALL THREADS
NOW AND PUSH WHATEVER THEY HAVE AND WRITE HANDOFFS"), by the thread "Finalize and benchmark the
Bayesian generator" of the claude.ai project symphony_2 (item 2 of the owner's auto-anatomist list).
The pull request that finishes the steps below deletes this file.

## Where things stand

- Pull request 38 (branch claude/project-thread-o3ng22-all-measures, commit 3be6e77 and this
  handoff) holds the finished second part: every measure of the reread, the full run's records
  under records/all (a container's run), nine tables, five figures, the README's second part and
  MEASURES.md, 25 tests, the grid array (run_all.py --point, grid/sweep.sbatch, grid/README.md) and
  the adversarial review in its body. It is a draft. Pull request 29, the first part, merged
  (2db2e27).
- The page: https://claude.ai/artifact/NQSUQ6c1Edzra7bW6CWJx2, built by report/build.py from the
  README, published from the symphony_2 account; the first part's older link belongs to another
  account and stays as it was. Both parts are on it, as prose with tables and figures.
- The owner's rules of 23:03 and 22:58 UTC: the final rerun runs on the grid, and the page is to
  be plots with short reading notes, not a wall of text.

## Next steps, in order

1. The grid rerun, on the owner's count (three jobs: setup, a 480-task array, a merge; the three
   submit lines are grid/README.md). The merge writes records/all and records/ to the bit of a
   serial run, with RECORD_ALL.json and RECORD.json carrying the committed code's digests (as
   committed they predate the array change; the README's Run it says so). Commit the records from
   the clone, run figures.py again so FIGURES.md names them, `tables.py --check` both files.
2. report/build.py as figures with reading notes: for each of the 16 figures its caption, two to
   four sentences on how to read it (axes, markers, what good looks like) and two or three on what
   it shows, the numbers from the README's answer; tables stay in the README; keep the four tiles.
   build.py is not hashed by the records, so this needs no rerun. Republish to the link above with
   the Artifact tool from a symphony_2 session (another account publishes a new link).
3. When bordercall pull request 39 (the reread's n-fault fixes, 3,760 rows at 1119506) merges:
   `papers_table.write_snapshot_all` to recut data/series_all.csv, then step 1 again; every number
   of the second part moves.
4. Delete this file, mark 38 ready, merge on the owner's standing permission.
