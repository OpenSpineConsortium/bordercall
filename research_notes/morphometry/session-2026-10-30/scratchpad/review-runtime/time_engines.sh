#!/bin/bash
# time_engines.sh REPEATS ENGINE...: run `python -m morphometry run` over masks/ with one worker,
# each engine REPEATS times into a fresh folder, and print each study's seconds row and the
# process's wall time and peak memory.
set -u
R=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/review-runtime
PY=${PYX:-/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/venv/bin/python}
TAG=${TAG:-}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPYCACHEPREFIX=$R/pycache PYTHONNOUSERSITE=1
reps=$1; shift
for k in $(seq 1 "$reps"); do
  for eng in "$@"; do
    out=$R/runs/$eng$TAG-$k
    rm -rf "$out"; mkdir -p "$out"
    start=$(date +%s.%N)
    PYTHONPATH=$R/$eng/grid/bordercall "$PY" -I $R/timed.py \
      "$PY" -m morphometry run --masks "${MASKS:-$R/masks}" --scheme enhance --out "$out" --workers 1 \
      > "$out.log" 2> "$out.time"
    echo "== $eng$TAG rep $k: $(tail -n 1 "$out.time")"
    grep -h ',seconds,' "$out"/rows/*.csv | awk -F, -v e="$eng" '{ printf "   %s %s %.1f s\n", e, $1, $4 }'
    grep -hc 'flag:error' "$out"/rows/*.csv | paste -sd' ' | sed 's/^/   error rows per study: /'
  done
done
