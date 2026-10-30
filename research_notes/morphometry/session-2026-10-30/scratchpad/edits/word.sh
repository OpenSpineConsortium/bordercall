word_morphometry() {  # bordercall's morphometry engine over one gold tier 3 set (the owner's counts: 2026-10-29 15:19 UTC, one CPU job a set; 2026-10-30 14:33 UTC, one more a set, MORPHOMETRY_RERUNS): queued once a word, its report printed on every later send
  local report=$LOGS/MORPHOMETRY-$id.md sent=$LOGS/MORPHOMETRY-$id.sent busy job="" missing holds opts=() again="" lost="" keep="" part_job queued
  case "$id" in
    enhance|verse) ;;
    covariates) word_morphometry_covariates; return ;;
    *) echo "refusing: morphometry takes enhance or verse, or covariates once both have run"; return 64 ;;
  esac
  # One at a time: both sets hold the checkout and write under one root, and the count is one job a set;
  # the join reads both sets' rows, so neither set is measured again while it runs.
  busy=$( { live_of morphometry_enhance; live_of morphometry_verse; live_of morphometry_covariates; } | tr '\n' ' ')
  [ -z "${busy// /}" ] || { echo "refusing: a morphometry job is still queued or running (job $busy); send morphometry $id again once it ends"; return 75; }
  if [ -f "$report" ]; then
    # Kept, so the owner's count holds: a report that stands queues nothing, unless it ended in failure
    # on older code or the owner's word for one more job names its job in MORPHOMETRY_RERUNS.
    echo "## $(basename "$report") ($(date -r "$report" '+%F %T'))"
    head -n 200 "$report" | LC_ALL=C tr -cd '\11\12\40-\176' | masked | head -c 30000
    job=$(bench_job_of "$report")
    if bench_failed_on_older_code "$report"; then
      # A set that failed measured nothing it can be trusted on, so once a fix has moved the checkout it
      # is queued once more, its report kept under its job's number, as a benchmark's is; the same
      # commit queues nothing. Its rows stay, and the next job measures again only those of another code.
      again="the report above ended in failure on older code"
    elif morphometry_rerun_allowed "$id" "$job"; then
      again="the report above is job $job's, which MORPHOMETRY_RERUNS lets the owner's count measure once more"
      # A whole run's rows may have been joined, so they are kept beside its report under its job, where
      # no later job writes, and the next job measures every study again.
      ! morphometry_ended_0 "$report" || keep=$job
    else
      return 0
    fi
  elif [ -f "$report.part" ]; then
    # A job that ended past its trap (cancelled, its time limit, a node lost) leaves what it wrote here.
    echo "## $(basename "$report").part, unfinished ($(date -r "$report.part" '+%F %T')): what the job wrote before it ended"
    head -n 200 "$report.part" | LC_ALL=C tr -cd '\11\12\40-\176' | masked | head -c 30000
  fi
  if [ -z "$again" ]; then
    job=$(awk -v what="morphometry_$id" '$3 == what { job = $1 } END { print job }' "$STATE" 2>/dev/null)
    if [ -f "$sent" ]; then
      # A submission whose answer was lost leaves no record and no live job the gate knows; the word
      # that named it was spent on it, so another waits for the owner's word for the lost one (lost,
      # then lost2, lost3 and on), as the join's does.
      lost=$(morphometry_lost_word "$id")
      morphometry_rerun_allowed "$id" "$lost" || {
        echo "refusing: a morphometry $id job was submitted at $(cat "$sent") and no job id came back, so it may be queued or ended under Slurm's name schwingnet-morphometry_$id; another waits for the owner's word, committed as MORPHOMETRY_RERUNS=$id:$lost in grid/gate.sh"
        return 64
      }
      again="the set follows a submission whose answer was lost, which MORPHOMETRY_RERUNS lets the owner's count run once more"
    elif [ -n "$job" ]; then
      # A job killed past its trap writes no report, only the part above, and was one of the count's jobs.
      morphometry_rerun_allowed "$id" "$job" || {
        echo "refusing: a morphometry $id job was queued before (job $job) and left no report; the owner's count was one job a set, so another waits for his word, committed as MORPHOMETRY_RERUNS=$id:$job in grid/gate.sh"
        return 64
      }
      again="the set's job $job left no report, which MORPHOMETRY_RERUNS lets the owner's count measure once more"
    fi
  fi
  [ -f "$REPO/grid/bordercall/morphometry/__main__.py" ] || { echo "refusing: no vendored morphometry under grid/bordercall/ at this commit"; return 2; }
  missing=$(morphometry_inputs_missing)
  [ -z "$missing" ] || { echo "refusing: morphometry $id needs $missing"; return 2; }
  [ -z "$keep" ] || morphometry_keep "$keep" check || return
  # No setup job: the set runs on the SPINEPS environment's interpreter, and its screening venv is its own.
  holds=$(checkout_holders)
  [ -z "$holds" ] || echo "  the checkout: after the live runs that hold it ($holds)"
  depend_on "$holds" || return 1
  # The job's shape is asked before anything is spent, so a refused shape moves and marks nothing.
  hpcw_check "morphometry_$id" batch SET="$id" DATA_ROOT="$DATA_ROOT" MORPHOMETRY_ROOT="$(morphometry_root)" ${opts[@]+"${opts[@]}"} --no-requeue --time 24:00:00 -- morphometry.sbatch || return 1
  # Only now, with nothing left to refuse it, is the word spent: a whole run's rows set aside under its
  # job, the report or the part it replaces under its job, and a lost answer's word recorded.
  [ -z "$keep" ] || morphometry_keep "$keep" || return 1
  [ ! -f "$report" ] || mv "$report" "$LOGS/MORPHOMETRY-$id-$job.md" || return 1
  if [ -f "$report.part" ]; then
    part_job=$(bench_job_of "$report.part")
    mv "$report.part" "$LOGS/MORPHOMETRY-$id-${part_job:-${job:-unknown}}.part" || return 1
  fi
  if [ -n "$lost" ]; then
    echo "$id:$lost spent at $(date -u '+%F %T') UTC on the submission of $(cat "$sent")" >> "$LOGS/MORPHOMETRY-$id.lost" || return 1
  fi
  [ -z "$again" ] || echo "  $again: queueing the set again at $commit"
  # The marker stands from before the submission until the gate's list names the job it queued, so an
  # answer lost in between, or a list the gate could not write, leaves a marker and never a second job.
  echo "$(date -u '+%F %T') UTC at commit $commit" > "$sent" 2>/dev/null || {
    echo "refusing: the gate cannot write logs/$(basename "$sent"), the marker that keeps a lost answer from queueing a second job; nothing was queued"
    return 1
  }
  queued=$(submit "morphometry_$id" batch SET="$id" DATA_ROOT="$DATA_ROOT" MORPHOMETRY_ROOT="$(morphometry_root)" ${opts[@]+"${opts[@]}"} --no-requeue --time 24:00:00 -- morphometry.sbatch) || return 1
  awk -v job="$queued" -v what="morphometry_$id" '$1 == job && $3 == what { found = 1 } END { exit !found }' "$STATE" 2>/dev/null || {
    echo "  the gate's list (logs/GATE_JOBS.txt) does not name the job it queued (${queued:-no id}), so the marker logs/$(basename "$sent") stays and no second job follows without the owner's word"
    return 1
  }
  rm -f "$sent"
  echo "submitted the morphometry job for $id. Send morphometry $id again once it ends to read its report, logs/MORPHOMETRY-$id.md."
}
morphometry_rerun_allowed() {  # morphometry_rerun_allowed SET WORD: MORPHOMETRY_RERUNS names WORD (a job, or a lost word) beside SET
  [ -n "$2" ] || return 1
  case " $MORPHOMETRY_RERUNS " in *" $1:$2 "*) return 0 ;; esac
  return 1
}
morphometry_lost_word() {  # morphometry_lost_word SET: the word that lets one more job follow the lost answer now standing: lost, then lost2, lost3 and on
  local spent=0
  [ ! -f "$LOGS/MORPHOMETRY-$1.lost" ] || spent=$(wc -l < "$LOGS/MORPHOMETRY-$1.lost")
  if [ "$spent" -eq 0 ]; then echo lost; else echo "lost$(( spent + 1 ))"; fi
}
morphometry_ended_0() {  # morphometry_ended_0 REPORT: its last line is a zero exit, a run that measured what it chose
  tail -n 1 "$1" 2>/dev/null | grep -q '^- exit 0 at '
}
morphometry_rerun_pending() {  # morphometry_rerun_pending SET: the set's standing report is one MORPHOMETRY_RERUNS names, so it is measured once more before any join
  [ -f "$LOGS/MORPHOMETRY-$1.md" ] && morphometry_rerun_allowed "$1" "$(bench_job_of "$LOGS/MORPHOMETRY-$1.md")"
}
morphometry_keep() {  # morphometry_keep JOB [check]: a whole run's rows and step logs moved under the set's kept/JOB; with check, only whether they can be
  # Moved, never copied: kept/ is the set's own folder on one volume, so each move is a rename, and what
  # the next job reuses (the masks' links, the venv, TotalSegmentator's stacks) stays where it reads it.
  # A file already under kept/JOB is never written over: a person looks at both first.
  local out from to name sub
  out=$(morphometry_root)/$id
  for sub in "" totalseg; do
    [ -z "$sub" ] || [ "$id" = verse ] || continue
    for name in rows rows.csv run.log steps.log facts.log whole.log facts.jsonl facts.jsonl.part verdicts.csv inputs.txt ids.txt; do
      from=$out${sub:+/$sub}/$name to=$out/kept/$1${sub:+/$sub}/$name
      [ -e "$from" ] || [ -L "$from" ] || continue
      if [ -e "$to" ] || [ -L "$to" ]; then
        echo "refusing: $to is there already, so job $1's $name would land on it; a person looks at both first; nothing was queued"
        return 2
      fi
      [ "${2:-}" != check ] || continue
      mkdir -p "${to%/*}" && mv -T -- "$from" "$to" || { echo "refusing: $from could not be moved under kept/$1; nothing was queued, and the next send moves what is left"; return 1; }
    done
  done
}
