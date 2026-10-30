import json
from pathlib import Path

M = []


def add(name, file, old, new, tests):
    M.append({"name": name, "file": file, "old": old, "new": new, "tests": tests})


G = "grid/gate.sh"
S = "grid/morphometry.sbatch"
C = "grid/morphometry-covariates.sbatch"
P = "tools/gold3_covariates.py"

# gate.sh
add("G1_standing_part_not_previous", G,
    'for file in "$LOGS/MORPHOMETRY-covariates.md" "$LOGS/MORPHOMETRY-covariates.md.part" \\\n',
    'for file in "$LOGS/MORPHOMETRY-covariates.md" \\\n', ["gate"])
add("G2_keep_drops_facts_part", G,
    "facts.jsonl facts.jsonl.part verdicts.csv", "facts.jsonl verdicts.csv", ["gate"])
add("G3_keep_drops_whole_log", G,
    "steps.log facts.log whole.log facts.jsonl", "steps.log facts.log facts.jsonl", ["gate"])
add("G4_no_rerun_pending", G,
    '    elif morphometry_rerun_pending "$set"; then\n',
    '    elif false; then\n', ["gate"])
add("G5_no_stamp_compare", G,
    '[ "$enhance_stamp" != "$verse_stamp" ]; then', 'false; then', ["gate"])
add("G9_set_no_gate_list_check", G,
    """  awk -v job="$queued" -v what="morphometry_$id" '$1 == job && $3 == what { found = 1 } END { exit !found }' "$STATE" 2>/dev/null || {""",
    "  true || {", ["gate"])
add("G10_set_marker_unwritable_ignored", G,
    """> "$sent" 2>/dev/null || {
    echo "refusing: the gate cannot write logs/$(basename "$sent"), the marker that keeps a lost answer from queueing a second job; nothing was queued"
    return 1
  }
  queued=$(submit "morphometry_$id\"""",
    """> "$sent" 2>/dev/null || true
  queued=$(submit "morphometry_$id\"""", ["gate"])
add("G11_rerun_word_no_spaces", G,
    '''case " $MORPHOMETRY_RERUNS " in *" $1:$2 "*) return 0 ;; esac''',
    '''case " $MORPHOMETRY_RERUNS " in *"$1:$2"*) return 0 ;; esac''', ["gate"])
add("G12_set_no_rm_sent", G,
    '''  rm -f "$sent"
  echo "submitted the morphometry job for $id.''',
    '''  echo "submitted the morphometry job for $id.''', ["gate"])
add("G13_previous_unreadable_not_checked", G,
    '''      [ -f "$root/covariates/$job/joined.csv" ] && [ -r "$root/covariates/$job/joined.csv" ] \\
        || lacks''',
    '''      true \\
        || lacks''', ["gate"])
add("G14_previous_any_digits", G,
    '[[ $job =~ ^[0-9]{1,12}$ ]] || return 1', '[[ $job =~ ^[0-9]+$ ]] || return 1', ["gate"])
add("G15_previous_no_member_filter", G,
    "    grep -Eq '^- member [a-z]+: persons [0-9]+' \"$file\" || continue\n", "", ["gate"])
add("G16_keep_check_skipped", G,
    '  [ -z "$keep" ] || morphometry_keep "$keep" check || return\n', '', ["gate"])
add("G17_keep_even_failed", G,
    '      ! morphometry_ended_0 "$report" || keep=$job\n', '      keep=$job\n', ["gate"])
add("G18_lost_word_numbering", G,
    '''if [ "$spent" -eq 0 ]; then echo lost; else echo "lost$(( spent + 1 ))"; fi
}
morphometry_ended_0''',
    '''if [ "$spent" -eq 0 ]; then echo lost; else echo "lost$spent"; fi
}
morphometry_ended_0''', ["gate"])
add("G19_set_no_root_passed", G,
    '''queued=$(submit "morphometry_$id" batch SET="$id" DATA_ROOT="$DATA_ROOT" MORPHOMETRY_ROOT="$(morphometry_root)" ''',
    '''queued=$(submit "morphometry_$id" batch SET="$id" DATA_ROOT="$DATA_ROOT" ''', ["gate"])
add("G20_stamp_regex_loose", G,
    r"""stamp=$(sed -n 's/^- code stamp: \([0-9a-f]\{16\}\)$/\1/p' "$1" 2>/dev/null | head -n 1)""",
    r"""stamp=$(sed -n 's/^- code stamp: \(.*\)$/\1/p' "$1" 2>/dev/null | head -n 1)""", ["gate"])
add("G21_part_move_dropped", G,
    '''    mv "$report.part" "$LOGS/MORPHOMETRY-$id-${part_job:-${job:-unknown}}.part" || return 1''',
    '''    :''', ["gate"])

# morphometry.sbatch
add("S1_median_strictly_more_than_5", S,
    'return form % median(xs) if len(xs) >= LEAST else "-"', 'return form % median(xs) if len(xs) > LEAST else "-"',
    ["gate"])
add("S2_least_6", S, "LEAST = 5\n", "LEAST = 6\n", ["gate"])
add("S3_no_worker_died", S,
    'if re.search(r"^a worker died", log, re.M):', 'if False:', ["gate"])
add("S4_no_count_check", S,
    'if count and len(codes) != int(count.group(1)):', 'if False:', ["gate"])
add("S5_no_foreign", S, "if foreign:\n", "if False:\n", ["gate"])
add("S6_no_stamp_vs_count", S, "elif count.group(2) != stamp:", "elif False:", ["gate"])
add("S7_no_default_whole", S,
    '[ -n "$whole" ] || whole="not whole: the check of the rows gave no answer"\n', '', ["gate"])
add("S8_versions_no_scipy", S, 'for name in ("numpy", "scipy", "nibabel"):', 'for name in ("numpy", "nibabel"):', ["gate"])
add("S9_stamp_not_checked", S,
    '[[ $STAMP =~ ^[0-9a-f]{16}$ ]] || {', '[[ $STAMP =~ . ]] || {', ["gate"])
add("S10_not_whole_still_tabled", S,
    '''      report "$name rows FAILED: not a whole run (${whole#not whole: }), so they are not used"
      return 1 ;;''',
    '''      report "$name rows FAILED: not a whole run (${whole#not whole: }), so they are not used"
      rc=1 ;;''', ["gate"])

# morphometry-covariates.sbatch
add("C1_previous_any_name", C,
    "[[ $job =~ ^[0-9]{1,12}$ ]] ||", "[[ $job =~ . ]] ||", ["join"])
add("C2_previous_not_passed", C,
    ' \\\n     ${previous[@]+"${previous[@]}"} > "$OUT/join.out"', ' > "$OUT/join.out"', ["join"])

# gold3_covariates.py
add("P1_mean_then_strict", P,
    'if own["shown"] and len(then["mean"]) >= MIN_CELL and (', 'if own["shown"] and len(then["mean"]) > MIN_CELL and (',
    ["join"])
add("P2_r_then_strict", P,
    'len(then["r"]) >= MIN_PAIR and', 'len(then["r"]) > MIN_PAIR and', ["join"])
add("P3_slope_then_strict", P,
    'len(then["slope"]) >= MIN_SLOPE and', 'len(then["slope"]) > MIN_SLOPE and', ["join"])
add("P4_no_partial_check", P,
    ' or few(now["partial"], then["partial"], MIN_CELL)', '', ["join"])
add("P5_keyerror_not_caught", P,
    "except (OSError, KeyError, ValueError, csv.Error) as error:\n            report.fail(\"previous_unreadable\", error)",
    "except (OSError, ValueError, csv.Error) as error:\n            report.fail(\"previous_unreadable\", error)", ["join"])
add("P6_texts_two_places", P,
    '{place: f"{value:.4f}" for place, value in p.values.items()}', '{place: f"{value:.1f}" for place, value in p.values.items()}',
    ["join"])
add("P7_g_not_recomputed", P,
    '''    for numbers in cells.values():
        numbers["g"] = g_of(numbers)
    return [(key, level, numbers)''',
    '''    return [(key, level, numbers)''', ["join"])
add("P8_few_inclusive", P, "return 0 < differing(ours, theirs) < least", "return 0 < differing(ours, theirs) <= least", ["join"])
add("P9_mixed_ge1", P, "if len(every) > 1:\n        report.fail(\"rows_code_mixed\")",
    "if len(every) > 2:\n        report.fail(\"rows_code_mixed\")", ["join"])
add("P10_stand_in_kept", P,
    "if values.get(study, {}).pop((level, STAND_IN_KEY), None) is not None:",
    "if values.get(study, {}).get((level, STAND_IN_KEY), None) is not None:", ["join"])
add("P11_no_blind", P, "            if unread:\n                blind(numbers)\n", "", ["join"])
add("P12_slope_ages_ignored", P,
    "out[\"slope\"][p.key] = (blank(p.age), reading)", "out[\"slope\"][p.key] = reading", ["join"])
add("P13_r_reading_one_side", P,
    "out[\"r\"][p.key] = (text[(above, key)], text[(level, key)])", "out[\"r\"][p.key] = text[(level, key)]", ["join"])

Path(__file__).with_name("mutants.json").write_text(json.dumps(M, indent=1), encoding="utf-8")
print(len(M))
