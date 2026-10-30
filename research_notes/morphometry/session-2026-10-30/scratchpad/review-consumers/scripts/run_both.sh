#!/bin/bash
# Measure the phantom masks with each engine, each scheme its own folder.
S=$1
PY=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
for eng in old new; do
  for scheme in enhance verse; do
    ( cd "$S" && PYTHONPATH=$S/$eng/grid/bordercall "$PY" -m morphometry run --masks "$S/masks/$scheme" --scheme $scheme --out "$S/out/$eng/$scheme" --workers 2 > "$S/out/$eng-$scheme.log" 2>&1; echo "$eng $scheme rc $?" >> "$S/out/done.txt" ) &
  done
done
wait
