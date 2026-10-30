#!/bin/bash
# Run the RunWithLines tests on the base copy and on each mutant, four at a time, one log each.
S=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-correctness-1-1
PY=$S/../venv/bin/python
one() {
    local m=$1
    cd "$S/$m" || return
    PYTHONPATH="$S/$m" "$PY" -m unittest -v morphometry.tests.test_lines_export.RunWithLines > "$S/log_$m.txt" 2>&1
    echo "$m exit $?" >> "$S/done.txt"
}
: > "$S/done.txt"
for batch in "base m1 m2 m3" "m4 m5 m6 m7" "m8"; do
    for m in $batch; do one "$m" & done
    wait
done
echo all done >> "$S/done.txt"
