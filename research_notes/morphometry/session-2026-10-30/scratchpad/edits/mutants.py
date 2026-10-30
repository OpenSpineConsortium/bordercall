"""Each fix taken out in turn in a scratch copy, the tests that guard it run, and the file put back byte for
byte; a mutant the tests still pass is reported as surviving. Run with the copy's root as its argument."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
ONLY = set(sys.argv[2:])
GATE = ["python3", "-m", "unittest", "tests.test_gate"]
JOIN = ["python3", "-m", "unittest", "tests.test_gold3_covariates"]
JOIN_NO_NUMPY = ["python3.12", "-m", "unittest", "tests.test_gold3_covariates"]

MARK = '''  [ ! -f "$sent" ] || before=$(cat "$sent")
  echo "$(date -u '+%F %T') UTC at commit $commit" > "$sent" 2>/dev/null || {
    echo "refusing: the gate cannot write logs/$(basename "$sent"), the marker that keeps a lost answer from queueing a second job; nothing was moved or queued"
    return 1
  }
'''
SET_SPEND = "  # Only now, with nothing left to refuse it, is the word spent: a whole run's rows set aside under its\n"
SET_AGAIN = '  [ -z "$again" ] || echo "  $again: queueing the set again at $commit"\n'

# name: (command, -k filters, [(file, old, new), ...])
MUTANTS = {
    "F1_failed_report_requeues_on_older_code": (GATE, ["queues_each_set_once_as_one_batch_job", "rerun_of_a_set_that_failed"], [
        ("grid/gate.sh", '    morphometry_rerun_allowed "$id" "$job" || return 0\n    again="the report above',
         '    morphometry_rerun_allowed "$id" "$job" || bench_failed_on_older_code "$report" || return 0\n    again="the report above')]),
    "F2_slurm_name_not_read": (GATE, ["answer_was_lost_is_waited"], [
        ("grid/gate.sh", """'$2 == "schwingnet-" what || $2 == what { sub(/_.*/, "", $1); print $1 }'""", "'0 { print $1 }'")]),
    "F2_part_not_read": (GATE, ["answer_was_lost_is_waited"], [
        ("grid/gate.sh", '  [ ! -f "$LOGS/MORPHOMETRY-$1.md.part" ] || job=$(bench_job_of "$LOGS/MORPHOMETRY-$1.md.part")\n', "")]),
    "F2_busy_ignores_lost": (GATE, ["answer_was_lost_is_waited"], [
        ("grid/gate.sh", "\n    morphometry_lost_live enhance; morphometry_lost_live verse; morphometry_lost_live covariates; } | tr '\\n' ' '",
         "; } | tr '\\n' ' '")]),
    "F2_holders_ignore_lost": (GATE, ["answer_was_lost_is_waited"], [
        ("grid/gate.sh", "\n                  morphometry_lost_live enhance; morphometry_lost_live verse; } | sort -u); do",
         "; } | sort -u); do")]),
    "F2_busy_ignores_the_joins_lost_job": (GATE, ["join_whose_answer_was_lost"], [
        ("grid/gate.sh", "morphometry_lost_live verse; morphometry_lost_live covariates; } | tr", "morphometry_lost_live verse; } | tr")]),
    "F2_busy_ignores_lost_for_the_join_test": (GATE, ["join_whose_answer_was_lost"], [
        ("grid/gate.sh", "\n    morphometry_lost_live enhance; morphometry_lost_live verse; morphometry_lost_live covariates; } | tr '\\n' ' '",
         "; } | tr '\\n' ' '")]),
    "F2_join_part_not_read": (GATE, ["join_whose_answer_was_lost"], [
        ("grid/gate.sh", '  [ ! -f "$LOGS/MORPHOMETRY-$1.md.part" ] || job=$(bench_job_of "$LOGS/MORPHOMETRY-$1.md.part")\n', "")]),
    "F2_join_slurm_name_not_read": (GATE, ["join_whose_answer_was_lost"], [
        ("grid/gate.sh", """'$2 == "schwingnet-" what || $2 == what { sub(/_.*/, "", $1); print $1 }'""", "'0 { print $1 }'")]),
    "F3_set_shape_asked_twice": (GATE, ["asks_the_jobs_shape_once"], [
        ("grid/gate.sh", 'queued=$(HPCW_CHECKED=1 submit "morphometry_$id"', 'queued=$(submit "morphometry_$id"')]),
    "F3_join_shape_asked_twice": (GATE, ["asks_the_jobs_shape_once"], [
        ("grid/gate.sh", "queued=$(HPCW_CHECKED=1 submit morphometry_covariates", "queued=$(submit morphometry_covariates")]),
    "F3_hpcw_ignores_checked": (GATE, ["asks_the_jobs_shape_once"], [
        ("grid/hpcw.sh", 'if ! hpcw_is_array "$@" && [ -z "${HPCW_CHECKED:-}" ]; then', 'if ! hpcw_is_array "$@"; then')]),
    "F9_mark_after_moves": (GATE, ["marks_its_submission_before"], [
        ("grid/gate.sh", MARK + SET_SPEND, SET_SPEND),
        ("grid/gate.sh", SET_AGAIN, MARK + SET_AGAIN)]),
    "F9_G10_mark_unwritable_ignored": (GATE, ["marks_its_submission_before"], [
        ("grid/gate.sh", MARK + SET_SPEND,
         MARK.replace(''' 2>/dev/null || {
    echo "refusing: the gate cannot write logs/$(basename "$sent"), the marker that keeps a lost answer from queueing a second job; nothing was moved or queued"
    return 1
  }
''', " 2>/dev/null || true\n") + SET_SPEND)]),
    "F9_G9_set_list_not_checked": (GATE, ["marks_its_submission_before"], [
        ("grid/gate.sh", """  awk -v job="$queued" -v what="morphometry_$id" '$1 == job && $3 == what { found = 1 } END { exit !found }' "$STATE" 2>/dev/null || {""",
         "  true || {")]),
    "F9_mark_not_put_back": (GATE, ["marks_its_submission_before"], [
        ("grid/gate.sh", '  if [ -n "$2" ]; then echo "$2" > "$1"; else rm -f "$1"; fi\n', "  :\n")]),
    "F9_lost_line_names_the_new_mark": (GATE, ["marks_its_submission_before"], [
        ("grid/gate.sh", 'on the submission of $before" >> "$LOGS/MORPHOMETRY-$id.lost"',
         'on the submission of $(cat "$sent")" >> "$LOGS/MORPHOMETRY-$id.lost"')]),
    "F9_join_mark_after_moves": (GATE, ["keeps_its_marker_until"], [
        ("grid/gate.sh", MARK + "  # Only now, with nothing left to refuse it, is the word spent: the report or the part it replaces set\n",
         "  # Only now, with nothing left to refuse it, is the word spent: the report or the part it replaces set\n"),
        ("grid/gate.sh", '  [ -z "$again" ] || echo "  the join $again"\n', MARK + '  [ -z "$again" ] || echo "  the join $again"\n')]),
    "F4_no_aside_note": (GATE, ["reruns_a_set_once_for_the_job", "rerun_of_a_set_that_failed", "verse_rerun_keeps"], [
        ("grid/gate.sh", "where the files it names are now, added to FILE and printed\n",
         "where the files it names are now, added to FILE and printed\n  return 0\n")]),
    "F5_reused_counted_as_stacked": (GATE, ["verse_rerun_keeps", "stacks_the_totalsegmentator_subjects_in_parallel"], [
        ("grid/morphometry.sbatch", 'echo reused > "$TS/stacked/$id.verdict"; return 0', 'echo stacked > "$TS/stacked/$id.verdict"; return 0')]),
    "F5_earlier_verdicts_kept": (GATE, ["stacks_the_totalsegmentator_subjects_in_parallel"], [
        ("grid/morphometry.sbatch", '      rm -f "$TS"/stacked/*.verdict\n', "")]),
    "F11_S1_median_over_more_than_five": (GATE, ["fails_a_set_whose_rows_are_not_the_runs_whole"], [
        ("grid/morphometry.sbatch", 'if len(xs) >= LEAST else "-"', 'if len(xs) > LEAST else "-"')]),
    "F11_S2_least_six": (GATE, ["fails_a_set_whose_rows_are_not_the_runs_whole"], [
        ("grid/morphometry.sbatch", "LEAST = 5\n", "LEAST = 6\n")]),
    "F12_G1_standing_part_not_previous": (GATE, ["checks_a_join_against_every_earlier_one"], [
        ("grid/gate.sh", '  for file in "$LOGS/MORPHOMETRY-covariates.md" "$LOGS/MORPHOMETRY-covariates.md.part" \\\n',
         '  for file in "$LOGS/MORPHOMETRY-covariates.md" \\\n')]),
    "F14_G2_keep_drops_facts_part": (GATE, ["reruns_a_set_once_for_the_job", "verse_rerun_keeps"], [
        ("grid/gate.sh", "facts.jsonl facts.jsonl.part verdicts.csv", "facts.jsonl verdicts.csv")]),
    "F7_P1_mean_then_strict": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", 'len(then["mean"]) >= MIN_CELL and (', 'len(then["mean"]) > MIN_CELL and (')]),
    "F7_P2_r_then_strict": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", 'len(then["r"]) >= MIN_PAIR and', 'len(then["r"]) > MIN_PAIR and')]),
    "F7_P5_keyerror_not_caught": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", "except (OSError, KeyError, ValueError, csv.Error) as error:",
         "except (OSError, ValueError, csv.Error) as error:")]),
    "F7_P14_valueerror_not_caught": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", "except (OSError, KeyError, ValueError, csv.Error) as error:",
         "except (OSError, KeyError, csv.Error) as error:")]),
    "F7_P14_csv_error_not_caught": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", "except (OSError, KeyError, ValueError, csv.Error) as error:",
         "except (OSError, KeyError, ValueError) as error:")]),
    "F7_P6_texts_two_places": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", 'f"{value:.4f}" for place, value in p.values.items()',
         'f"{value:.2f}" for place, value in p.values.items()')]),
    "F7_P12_slope_ages_ignored": (JOIN, ["AcrossReports"], [
        ("tools/gold3_covariates.py", 'out["slope"][p.key] = (blank(p.age), reading)', 'out["slope"][p.key] = reading')]),
    "F8_C1_previous_any_name": (JOIN_NO_NUMPY, ["JobHandoff"], [
        ("grid/morphometry-covariates.sbatch", "  [[ $job =~ ^[0-9]{1,12}$ ]] || { report \"FAILED: the gate named an earlier join",
         "  true || { report \"FAILED: the gate named an earlier join")]),
    "F8_C2_previous_not_passed": (JOIN_NO_NUMPY, ["JobHandoff"], [
        ("grid/morphometry-covariates.sbatch", '     ${previous[@]+"${previous[@]}"} > "$OUT/join.out" 2>&1 &',
         '     > "$OUT/join.out" 2>&1 &')]),
}


def run(command, filters):
    args = list(command)
    for one in filters:
        args += ["-k", one]
    done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=1800)
    tail = [line for line in done.stderr.splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    return done.returncode, " ".join(tail)


def apply(edits):
    saved = {}
    for name, old, new in edits:
        path = ROOT / name
        if name not in saved:
            saved[name] = path.read_bytes()
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            restore(saved)
            raise SystemExit(f"{name}: the text to change occurs {count} times")
        path.write_text(text.replace(old, new), encoding="utf-8")
    return saved


def restore(saved):
    for name, data in saved.items():
        (ROOT / name).write_bytes(data)
        assert hashlib.sha256((ROOT / name).read_bytes()).digest() == hashlib.sha256(data).digest(), name


def main():
    chosen = {k: v for k, v in MUTANTS.items() if not ONLY or k in ONLY}
    baselines = {}
    for name, (command, filters, edits) in chosen.items():
        key = (tuple(command), tuple(filters))
        if key not in baselines:
            baselines[key] = run(command, filters)
            print(f"baseline {' '.join(command[:1])} -k {' -k '.join(filters)}: rc={baselines[key][0]} {baselines[key][1]}", flush=True)
        saved = apply(edits)
        try:
            rc, said = run(command, filters)
        finally:
            restore(saved)
        verdict = "KILLED" if rc != 0 else "SURVIVED"
        print(f"{name} -> {verdict} | rc={rc} {said}", flush=True)


main()
