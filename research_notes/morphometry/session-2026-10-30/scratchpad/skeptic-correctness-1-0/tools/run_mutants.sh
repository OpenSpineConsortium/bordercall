#!/bin/bash
# Run the RunWithLines tests on each mutant copy, three at a time, one log each.
cd /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-correctness-1-0
run_one() {
  ( cd /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-correctness-1-0/$1 && /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/venv/bin/python -W ignore -m unittest morphometry.tests.test_lines_export.RunWithLines -v > /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-correctness-1-0/mutant_$1.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-correctness-1-0/mutant_$1.log )
}
for m in "$@"; do run_one $m & done
wait
