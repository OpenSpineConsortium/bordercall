#!/bin/bash
# wait_answer.sh JOB REQUEST: poll the branch grid until logs/job-JOB.json names REQUEST, then print it
cd /home/claude/symphony-template
for i in $(seq 1 60); do
  git fetch -q origin +refs/heads/grid:refs/remotes/origin/grid 2>/dev/null
  if git show "origin/grid:logs/job-$1.json" 2>/dev/null | grep -q "$2"; then
    git show "origin/grid:logs/job-$1.json"; exit 0
  fi
  sleep 20
done
echo "no answer for $2 after 20 minutes"; exit 1
