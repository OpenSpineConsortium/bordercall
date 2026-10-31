#!/bin/bash
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
# The second part's run on the grid, in three steps, each one hpcworker job submit (SchwingNet's
# grid/hpcw.sh; no partition, QoS or output line here, as the lab's one tested way of queueing
# asks): STEP=setup makes the venv from requirements-schwingcheck.txt; STEP=point, one task of an
# array of 480, writes grid point SLURM_ARRAY_TASK_ID under OUT/points/; STEP=merge, afterany the
# array, reads the points and writes every other record, then run.py's, then checks the tables.
# The merge's records are the serial run's to the bit (run_all.py: read_points), so nothing on
# the page depends on where it ran. grid/README.md gives the three submit lines.
set -uo pipefail
STEP=${STEP:?setup, point or merge}
NOTE=${BORDERCALL:-$HOME/bordercall}/research_notes/synthetic-validation
OUT=${SYNTHVAL_OUT:-$NOTE/records/all}
VENV=${SYNTHVAL_VENV:-$HOME/.venvs/schwingcheck}
cd "$NOTE" || exit 2
case "$STEP" in
  setup)
    python3 -m venv "$VENV" && "$VENV/bin/pip" install -q -r "$NOTE/../../requirements-schwingcheck.txt" || exit 1
    "$VENV/bin/python" -I -c "import pymc, numpy; print('pymc', pymc.__version__)" ;;
  point)
    "$VENV/bin/python" -I run_all.py --out "$OUT" --point "${SLURM_ARRAY_TASK_ID:?one task of the array}" ;;
  merge)
    "$VENV/bin/python" -I run_all.py --out "$OUT" || exit 1
    "$VENV/bin/python" -I run.py --out "$NOTE/records" || exit 1
    "$VENV/bin/python" -I tables.py --records "$NOTE/records" --check README.md --check MEASURES.md ;;
  *) echo "sweep: STEP is setup, point or merge"; exit 64 ;;
esac
