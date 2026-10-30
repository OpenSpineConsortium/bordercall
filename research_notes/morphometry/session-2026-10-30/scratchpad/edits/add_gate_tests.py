"""Insert the F2, F3 and F9 gate tests before the covariates rerun test."""
from pathlib import Path

PATH = Path("/home/user/SchwingNet/tests/test_gate.py")
ANCHOR = "    def test_morphometry_covariates_waits_while_a_set_rerun_is_pending(self):\n"
NEW = '''    def test_a_morphometry_job_whose_answer_was_lost_is_waited_for_while_slurm_holds_it(self):
        # The gate's list never names a job whose answer was lost, so Slurm's name for it, and once it runs
        # the part it writes, find it: every morphometry word waits for it, a run that holds the checkout
        # waits for it, and the owner's word for the lost one is spent only once it has ended.
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        lossy = self.fake / "lossy"
        lossy.write_text("morphometry_enhance", encoding="utf-8")
        self.assertEqual(self.gate("morphometry", "enhance", HPCW_LOSSY=str(lossy)).returncode, 1)
        self.assertEqual(len(self.line_of("morphometry.sbatch")), 1)
        self.assertNotIn("morphometry_enhance", self.recorded())
        self.allow_morphometry_rerun("enhance:lost")
        # queued under hpcworker's name for it, before it has written anything
        (self.fake / "queue").write_text("101 schwingnet-morphometry_enhance\\n", encoding="utf-8")
        for which in ("enhance", "verse", "covariates"):
            busy = self.gate("morphometry", which)
            self.assertEqual(busy.returncode, 75, busy.stdout)
            self.assertIn("(job 101 )", busy.stdout)
        (self.repo / "tools" / "gold3_complete_grid.py").write_text("", encoding="utf-8")
        matcher = self.repo / "grid" / "bordercall" / "holdings" / "fullspine_complete.py"
        matcher.parent.mkdir(parents=True, exist_ok=True)
        matcher.touch()
        holds = self.gate("bordercall", "complete")
        self.assertEqual(holds.returncode, 0, holds.stdout + holds.stderr)
        self.assertIn("the checkout: after the live runs that hold it (afterany:101)", holds.stdout)
        # running, under whatever name Slurm shows it by, the part it writes names it
        (self.fake / "queue").write_text("101\\n", encoding="utf-8")
        part = logs / "MORPHOMETRY-enhance.md.part"
        part.write_text("# morphometry enhance: job 101 on node, commit 0000000, 2026-10-30 16:00:00 UTC\\n", encoding="utf-8")
        for which in ("enhance", "verse", "covariates"):
            busy = self.gate("morphometry", which)
            self.assertEqual(busy.returncode, 75, busy.stdout)
            self.assertIn("(job 101 )", busy.stdout)
        self.assertFalse((logs / "MORPHOMETRY-enhance.lost").exists())
        self.assertEqual(len(self.line_of("morphometry.sbatch")), 1)
        # once it has ended the owner's word for it queues one more, its part kept under its job
        (self.fake / "queue").write_text("", encoding="utf-8")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("follows a submission whose answer was lost", done.stdout)
        self.assertFalse(part.exists())
        self.assertTrue((logs / "MORPHOMETRY-enhance-101.part").exists())
        self.assertEqual(len(self.line_of("morphometry.sbatch")), 2)

    def test_a_morphometry_word_asks_the_jobs_shape_once_before_it_marks_the_submission(self):
        # Asked before the mark, the shape is not asked again by job submit (HPCW_CHECKED): a refusal of its
        # own --check after the mark would queue nothing and still read as a lost answer.
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        checks = self.fake / "checks.log"
        done = self.gate("morphometry", "enhance", HPCW_CHECK_LOG=str(checks))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        asked = checks.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(asked), 1, asked)
        self.assertIn("--class batch --name morphometry_enhance ", asked[0])
        self.assertEqual(len(self.submitted()), 1)
        checks.unlink()
        env = self.covariates_inputs()
        done = self.gate("morphometry", "covariates", HPCW_CHECK_LOG=str(checks), **env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        asked = checks.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(asked), 1, asked)
        self.assertIn("--class batch --name morphometry_covariates ", asked[0])
        self.assertEqual(len(self.submitted()), 2)

    def test_a_morphometry_set_marks_its_submission_before_it_moves_anything_and_until_the_list_names_the_job(self):
        # The mark is written before anything is set aside, so a gate that cannot write it refuses with
        # nothing moved; a move that fails takes the mark back to what it was; and a job the gate's list
        # cannot name leaves it, so the next send reads a lost answer and waits for the owner's word.
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        report = self.morphometry_report("enhance", 4242)
        out = self.morphometry_outputs("enhance", 4242)
        self.allow_morphometry_rerun("enhance:4242")
        sent = logs / "MORPHOMETRY-enhance.sent"

        def untouched():
            self.assertTrue(report.exists())
            self.assertFalse((logs / "MORPHOMETRY-enhance-4242.md").exists())
            self.assertEqual((out / "rows.csv").read_text(encoding="utf-8"), "job 4242\\n")
            self.assertEqual(self.submitted(), [])

        sent.mkdir()
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn("the gate cannot write logs/MORPHOMETRY-enhance.sent", refused.stdout)
        self.assertIn("nothing was moved or queued", refused.stdout)
        self.assertNotIn("queueing", refused.stdout)
        untouched()
        self.assertFalse((out / "kept").exists())
        sent.rmdir()
        # a move that fails queues nothing and takes the mark off again
        (out / "kept").write_text("", encoding="utf-8")
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn("could not be moved under kept/4242", refused.stdout)
        untouched()
        self.assertFalse(sent.exists())
        (out / "kept").unlink()
        # a job queued while the gate's list cannot take its line leaves the mark
        state = logs / "GATE_JOBS.txt"
        if state.exists():
            state.unlink()
        state.mkdir()
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("does not name the job it queued", done.stdout)
        self.assertEqual(len(self.submitted()), 1)
        self.assertTrue(sent.is_file())
        self.assertTrue((logs / "MORPHOMETRY-enhance-4242.md").exists())
        state.rmdir()
        for _ in range(2):
            refused = self.gate("morphometry", "enhance")
            self.assertEqual(refused.returncode, 64, refused.stdout)
            self.assertIn("committed as MORPHOMETRY_RERUNS=enhance:lost in grid/gate.sh", refused.stdout)
        self.assertEqual(len(self.submitted()), 1)
        # the lost word's record not written, nothing is queued and the mark goes back as it stood
        sent.write_text("2026-10-30 15:00:00 UTC at commit 1111111\\n", encoding="utf-8")
        self.allow_morphometry_rerun("enhance:4242 enhance:lost")
        spent = logs / "MORPHOMETRY-enhance.lost"
        spent.mkdir()
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertEqual(sent.read_text(encoding="utf-8"), "2026-10-30 15:00:00 UTC at commit 1111111\\n")
        self.assertEqual(len(self.submitted()), 1)
        spent.rmdir()
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.submitted()), 2)
        self.assertFalse(sent.exists())
        # the word recorded as spent on the submission the earlier mark names, not on this one
        self.assertRegex(spent.read_text(encoding="utf-8"),
                         r"\\Aenhance:lost spent at \\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d UTC on the submission of "
                         r"2026-10-30 15:00:00 UTC at commit 1111111\\n\\Z")

'''
text = PATH.read_text(encoding="utf-8")
assert text.count(ANCHOR) == 1
assert NEW not in text
PATH.write_text(text.replace(ANCHOR, NEW + ANCHOR), encoding="utf-8")
print("done")
