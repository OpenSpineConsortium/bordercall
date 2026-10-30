import pathlib, sys
root = pathlib.Path(sys.argv[1])
edits = pathlib.Path(sys.argv[2])
gate = root / "grid" / "gate.sh"
text = gate.read_text(encoding="utf-8")

def once(old, new):
    global text
    assert text.count(old) == 1, (text.count(old), old[:80])
    text = text.replace(old, new)

# the two words
once('''# check across reports yet refuses, so a word here waits for that check unless the rows are the same.
COVARIATES_RERUNS=""
''', '''# check across reports yet refuses, so a word here waits for that check unless the rows are the same.
# covariates:40878978 is the third job of the owner's count of 2026-10-30 14:33 UTC (MORPHOMETRY_RERUNS,
# below): the join once more over both sets' rows measured on the merged engine, refused while either
# set's report standing is still one MORPHOMETRY_RERUNS names (covariates_inputs_missing).
COVARIATES_RERUNS="covariates:40878978"
# The owner's word for one more measuring of a morphometry set, <set>:<job of the report or the record
# it replaces>, or <set>:lost for a submission whose answer was lost, then <set>:lost2 and on, each spent
# once (logs/MORPHOMETRY-<set>.lost records them); one word, one more job (word_morphometry). The report
# it replaces is kept as logs/MORPHOMETRY-<set>-<job>.md and, where it ended 0, its rows and step logs
# under <morphometry root>/<set>/kept/<job>/ (morphometry_keep). enhance:40872077 and verse:40877151 are
# the owner's choice of 2026-10-30 14:33 UTC on the decision card "How many grid jobs for the morphometry
# rerun on the new engine?", "Three: enhance, verse, covariates": each set measured once more on the
# merged engine, bordercall ee495d5 (code stamp a56adf14a9e98b15, where both reports name the
# 81e732f142d3aa16 of bordercall 16f7b40), then the join once more (COVARIATES_RERUNS).
MORPHOMETRY_RERUNS="enhance:40872077 verse:40877151"
''')

# the set's word, whole
start = text.index("word_morphometry() {")
end = text.index("word_morphometry_covariates() {")
text = text[:start] + (edits / "word.sh").read_text(encoding="utf-8") + "\n" + text[end:]

# one root for the sets' jobs and the join
text = text.replace("covariates_morphometry_root", "morphometry_root")
once('''morphometry_root() {  # where grid/morphometry.sbatch writes both sets' rows
''', '''morphometry_root() {  # where grid/morphometry.sbatch writes both sets' rows, handed to each set's job so its folder and kept/ are the gate's
''')

# the join waits for a set's counted rerun
once('''    elif ! tail -n 1 "$LOGS/MORPHOMETRY-$set.md" | grep -q '^- exit 0 at '; then
      lacks "a morphometry $set report that ended 0 (the one standing ended in failure)"
    fi''', '''    elif ! morphometry_ended_0 "$LOGS/MORPHOMETRY-$set.md"; then
      lacks "a morphometry $set report that ended 0 (the one standing ended in failure)"
    elif morphometry_rerun_pending "$set"; then
      lacks "the morphometry $set rerun the owner counted (the report standing is job $(bench_job_of "$LOGS/MORPHOMETRY-$set.md")'s, which MORPHOMETRY_RERUNS names; send morphometry $set first)"
    fi''')
gate.write_text(text, encoding="utf-8")
print("applied")
