#!/bin/bash
R=/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/review-runtime
cd $R
# repeats 2 and 3 on the thread's environment (Python 3.13, numpy 2.5.4, scipy 1.18.1)
./time_engines.sh 3 old new 2>&1
# one pass each on Python 3.11 with numpy 2.2.6, the grid's recorded numpy, and two scipy versions
for v in 1.13.1 1.15.3; do
  PYX=$R/venv311-scipy$v/bin/python TAG=-py311-scipy$v ./time_engines.sh 1 old new
done
echo BATCH2 DONE
