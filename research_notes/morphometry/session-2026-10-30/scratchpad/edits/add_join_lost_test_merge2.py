"""Insert the join's lost-answer test after the set's."""
from pathlib import Path

PATH = Path("/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/merge2/SchwingNet/tests/test_gate.py")
ANCHOR = "    def test_a_morphometry_word_asks_the_jobs_shape_once_before_it_marks_the_submission(self):\n"
NEW = '''    def test_a_join_whose_answer_was_lost_is_waited_for_while_slurm_holds_it(self):
        # The join's lost job reads both sets' rows, so every morphometry word waits for it while Slurm holds
        # it, found by its name or by the part it writes; it holds no checkout, so no run waits for it.
        env = self.covariates_inputs()
        logs = self.repo / "grid" / "logs"
        lossy = self.fake / "lossy"
        lossy.write_text("morphometry_covariates", encoding="utf-8")
        self.assertNotEqual(self.gate("morphometry", "covariates", HPCW_LOSSY=str(lossy), **env).returncode, 0)
        self.assertEqual(len(self.line_of("morphometry-covariates.sbatch")), 1)
        self.assertTrue((logs / "MORPHOMETRY-covariates.sent").exists())
        self.allow_covariates_rerun("covariates:lost")
        (self.fake / "queue").write_text("101 schwingnet-morphometry_covariates\\n", encoding="utf-8")
        for which in ("covariates", "enhance", "verse"):
            busy = self.gate("morphometry", which, **env)
            self.assertEqual(busy.returncode, 75, busy.stdout)
            self.assertIn("(job 101 )", busy.stdout)
        (self.repo / "tools" / "gold3_complete_grid.py").write_text("", encoding="utf-8")
        matcher = self.repo / "grid" / "bordercall" / "holdings" / "fullspine_complete.py"
        matcher.parent.mkdir(parents=True, exist_ok=True)
        matcher.touch()
        holds = self.gate("bordercall", "complete")
        self.assertEqual(holds.returncode, 0, holds.stdout + holds.stderr)
        self.assertNotIn("afterany:101", holds.stdout)
        (self.fake / "queue").write_text("101\\n", encoding="utf-8")
        part = logs / "MORPHOMETRY-covariates.md.part"
        part.write_text("# morphometry covariates: job 101 on node, commit abc1234, 2026-10-30 16:00:00 UTC\\n", encoding="utf-8")
        for which in ("covariates", "enhance", "verse"):
            busy = self.gate("morphometry", which, **env)
            self.assertEqual(busy.returncode, 75, busy.stdout)
            self.assertIn("(job 101 )", busy.stdout)
        self.assertFalse((logs / "MORPHOMETRY-covariates.lost").exists())
        self.assertEqual(len(self.line_of("morphometry-covariates.sbatch")), 1)
        (self.fake / "queue").write_text("", encoding="utf-8")
        done = self.gate("morphometry", "covariates", **env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("follows a submission whose answer was lost", done.stdout)
        self.assertFalse(part.exists())
        self.assertTrue((logs / "MORPHOMETRY-covariates-101.part").exists())
        self.assertEqual(len(self.line_of("morphometry-covariates.sbatch")), 2)

'''
text = PATH.read_text(encoding="utf-8")
assert text.count(ANCHOR) == 1 and NEW not in text
PATH.write_text(text.replace(ANCHOR, NEW + ANCHOR), encoding="utf-8")
print("done")
