#!/bin/bash
# refresh.sh TAG: send the status word once, wait for its answer, cut the study's progress and its
# jobs' sacct lines out of it, and rebuild the monitor page from them (publishing stays a separate step)
set -u
S=/tmp/claude-0/-home-claude/1251a0cd-a700-5bbb-8f9e-89e952a5a266/scratchpad
M=$S/monitor
TAG=${1:?tag}
REQ="drr-gap-status-$TAG-9dubtu"
cd /home/claude/symphony-template || exit 1
gh api -X POST repos/OpenSpineConsortium/symphony-template/actions/workflows/grid-accounts.yml/dispatches \
  -f ref=main -f 'inputs[action]=job' -f 'inputs[job]=schwingnet-status' -f "inputs[request]=$REQ" || exit 1
"$S/wait_answer.sh" schwingnet-status "$REQ" > "$S/status-$TAG.json" || { echo "no answer"; exit 1; }
python3 - "$S/status-$TAG.json" "$S/progress-$TAG.txt" "$S/jobs-$TAG.txt" <<'EOF'
import json, re, sys
d = json.load(open(sys.argv[1]))
lines = d["lines"]
progress, inside = [], False
for line in lines:
    if line.startswith("## bench flexray_drr_gap, progress"):
        inside = True; print(line); continue
    if inside and line.startswith("## "):
        inside = False
    if inside:
        progress.append(line)
open(sys.argv[2], "w").write("\n".join(progress) + ("\n" if progress else ""))
jobs = [l for l in lines if "drr_gap" in l or "bench_flexray" in l]
open(sys.argv[3], "w").write("\n".join(jobs) + "\n")
print("at", d["at"], "rc", d["rc"], "said", d["said"])
print("\n".join(jobs))
print("progress lines:", len(progress))
print("\n".join(progress[:60]))
EOF
