"""Throwaway checks of the owner's count of three (enhance once more, verse once more, the join once more)
against grid/gate.sh as changed in /home/user/SchwingNet, driven through tests/test_gate.py's own harness.
Nothing here touches the clone: the harness copies grid/ into a temporary folder for each test."""

import importlib.util
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("test_gate", "/home/user/SchwingNet/tests/test_gate.py")
TG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TG)
STAMP, OLD_STAMP = TG.STAMP, TG.OLD_STAMP


class VerifyCount(TG.GateTest):
    def real_state(self):
        """The grid as it stands at 14:33 UTC on 2026-10-30: the three counted jobs in the gate's list, their
        reports standing (the sets' on the older engine), the first join's table kept, every input there."""
        env = self.covariates_inputs()
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        for which, job in (("enhance", 40872077), ("verse", 40877151)):
            self.morphometry_report(which, job, stamp=OLD_STAMP)
            self.morphometry_outputs(which, job)
            self.state_line(job, f"morphometry:{which}", f"morphometry_{which}")
        self.covariates_report(40878978)
        self.joined_table(40878978)
        self.state_line(40878978, "morphometry:covariates", "morphometry_covariates")
        return env

    def head(self):
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()

    def merge_elsewhere(self):
        """Another pull request merged and the gate pulled: a commit that touches nothing of morphometry."""
        return self.covariates_commit()

    def rows_written(self, which, job):
        """What a set's job leaves for the join: its rows files."""
        out = self.tmp / "go2432" / "morphometry" / which
        for rows in ("rows.csv", "totalseg/rows.csv") if which == "verse" else ("rows.csv",):
            (out / rows).parent.mkdir(parents=True, exist_ok=True)
            (out / rows).write_text(f"job {job}\n", encoding="utf-8")

    def jobs(self, what):
        return [line for line in self.submitted() if f"--name {what} " in line]

    def test_vc_happy_path_is_three_and_resends_on_moving_main_queue_nothing(self):
        env = self.real_state()
        # covariates first: refused, nothing moved
        waits = self.gate("morphometry", "covariates", **env)
        self.assertEqual(waits.returncode, 2, waits.stdout)
        for which in ("enhance", "verse"):
            done = self.gate("morphometry", which)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            job = self.recorded()[f"morphometry_{which}"]
            # sent twice in a row while live
            self.live(job)
            for word in ("enhance", "verse", "covariates"):
                busy = self.gate("morphometry", word, **(env if word == "covariates" else {}))
                self.assertEqual(busy.returncode, 75, busy.stdout)
            (self.fake / "queue").write_text("", encoding="utf-8")
            head = self.head()
            self.morphometry_report(which, job, commit=head[:7])
            self.rows_written(which, job)
            # covariates between the two reruns, main moving between every send
            if which == "enhance":
                self.merge_elsewhere()
                waits = self.gate("morphometry", "covariates", **env)
                self.assertEqual(waits.returncode, 2, waits.stdout)
            for _ in range(3):
                self.merge_elsewhere()
                again = self.gate("morphometry", which)
                self.assertEqual(again.returncode, 0, again.stdout)
                self.assertNotIn("queueing", again.stdout)
        self.merge_elsewhere()
        done = self.gate("morphometry", "covariates", **env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        joined = self.recorded()["morphometry_covariates"]
        self.covariates_report(joined)
        for _ in range(3):
            self.merge_elsewhere()
            for word in ("enhance", "verse", "covariates"):
                again = self.gate("morphometry", word, **(env if word == "covariates" else {}))
                self.assertEqual(again.returncode, 0, again.stdout)
        self.assertEqual(len(self.submitted()), 3, self.submitted())

    def test_vc_failed_rerun_then_any_merge_queues_a_fourth_job_on_the_send_that_reads_it(self):
        env = self.real_state()
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        first = self.recorded()["morphometry_enhance"]
        head = self.head()
        # the rerun ran on the gate's commit and its rows were not the run's whole (a worker died)
        self.morphometry_report("enhance", first, rc=1, commit=head[:7], stamp=STAMP)
        same = self.gate("morphometry", "enhance")
        self.assertEqual(same.returncode, 0, same.stdout)
        self.assertEqual(len(self.submitted()), 1)
        # any other pull request merges and the gate pulls it: the next send, the one that reads the report,
        # queues the set again with no word for it
        self.merge_elsewhere()
        read = self.gate("morphometry", "enhance")
        print("\n--- the send after a merge elsewhere:\n" + read.stdout)
        self.assertEqual(read.returncode, 0, read.stdout + read.stderr)
        self.assertIn("ended in failure on older code: queueing the set again", read.stdout)
        self.assertEqual(len(self.jobs("morphometry_enhance")), 2)
        # and again, without bound: the second fails on its own commit, main moves, a third
        second = self.recorded()["morphometry_enhance"]
        self.morphometry_report("enhance", second, rc=1, commit=self.head()[:7], stamp=STAMP)
        self.merge_elsewhere()
        third = self.gate("morphometry", "enhance")
        self.assertIn("queueing the set again", third.stdout)
        self.assertEqual(len(self.jobs("morphometry_enhance")), 3)
        # then the rest of the count: verse once more and the join once more
        self.morphometry_report("enhance", self.recorded()["morphometry_enhance"], commit=self.head()[:7])
        self.rows_written("enhance", self.recorded()["morphometry_enhance"])
        self.assertEqual(self.gate("morphometry", "verse").returncode, 0)
        self.morphometry_report("verse", self.recorded()["morphometry_verse"], commit=self.head()[:7])
        self.rows_written("verse", self.recorded()["morphometry_verse"])
        done = self.gate("morphometry", "covariates", **env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        print("--- jobs queued against the owner's count of three:", len(self.submitted()))
        self.assertEqual(len(self.submitted()), 5)

    def test_vc_the_real_job_fails_a_worker_death_and_the_next_send_after_a_merge_requeues_it(self):
        """The new rows check turns a run whose worker died, which ended 0 before, into exit 1; with any merge
        between the job's start and the send that reads it, that send queues the set again."""
        env = self.real_state()
        fake_py = self.tmp / "fakepy"
        fake_py.write_text(self.FAKE_ENHANCE_PYTHON, encoding="utf-8")
        fake_py.chmod(0o755)
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        job = self.recorded()["morphometry_enhance"]
        line = self.submitted()[0]
        root = re.search(r"MORPHOMETRY_ROOT=(\S+)", line).group(1)
        run = dict(os.environ, SCHWINGNET=str(self.repo), DATA_ROOT=str(self.data), LAB_VOLUME=str(self.tmp), SET="enhance",
                   MORPHOMETRY_ROOT=root, MORPHOMETRY_PYTHON=str(fake_py), SLURM_CPUS_PER_TASK="2", FAKE_RUN="died",
                   SLURM_JOB_ID=job)
        ran = subprocess.run(["bash", str(self.repo / "grid" / "morphometry.sbatch")], cwd=self.repo / "grid", env=run,
                             capture_output=True, text=True, timeout=120)
        report = (self.repo / "grid" / "logs" / "MORPHOMETRY-enhance.md").read_text(encoding="utf-8")
        print("\n--- the rerun's report:\n" + report)
        self.assertEqual(ran.returncode, 1, ran.stdout + ran.stderr + report)
        self.assertIn("rows FAILED: not a whole run (a worker died", report)
        same = self.gate("morphometry", "enhance")
        self.assertNotIn("queueing", same.stdout)
        self.merge_elsewhere()
        read = self.gate("morphometry", "enhance")
        self.assertIn("ended in failure on older code: queueing the set again", read.stdout)
        self.assertEqual(len(self.jobs("morphometry_enhance")), 2)

    def test_vc_a_checkout_moved_during_the_rerun_requeues_on_the_very_next_send(self):
        env = self.real_state()
        fake_py = self.tmp / "fakepy"
        # the whole run, with the checkout moved while it measures (a hand pull, or the hold lost)
        fake_py.write_text(self.FAKE_ENHANCE_PYTHON.replace(
            "    exit 0 ;;\n  '-m screening facts'",
            "    git -C \"$SCHWINGNET\" -c user.name=t -c user.email=t@t -c gc.auto=0 -c maintenance.auto=false "
            "commit -q --allow-empty -m moved\n    exit 0 ;;\n  '-m screening facts'", 1), encoding="utf-8")
        fake_py.chmod(0o755)
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        job = self.recorded()["morphometry_enhance"]
        root = re.search(r"MORPHOMETRY_ROOT=(\S+)", self.submitted()[0]).group(1)
        run = dict(os.environ, SCHWINGNET=str(self.repo), DATA_ROOT=str(self.data), LAB_VOLUME=str(self.tmp), SET="enhance",
                   MORPHOMETRY_ROOT=root, MORPHOMETRY_PYTHON=str(fake_py), SLURM_CPUS_PER_TASK="2", FAKE_RUN="whole",
                   SLURM_JOB_ID=job, GIT_CEILING_DIRECTORIES=str(self.tmp))
        ran = subprocess.run(["bash", str(self.repo / "grid" / "morphometry.sbatch")], cwd=self.repo / "grid", env=run,
                             capture_output=True, text=True, timeout=120)
        report = (self.repo / "grid" / "logs" / "MORPHOMETRY-enhance.md").read_text(encoding="utf-8")
        self.assertEqual(ran.returncode, 3, ran.stdout + ran.stderr + report)
        read = self.gate("morphometry", "enhance")
        self.assertIn("queueing the set again", read.stdout)
        self.assertEqual(len(self.jobs("morphometry_enhance")), 2)

    def test_vc_a_lost_rerun_answer_hides_the_running_job_from_the_busy_check(self):
        """A submission whose answer was lost is in no list the busy check reads: the other set is queued
        beside it, waiting on nothing, and the join is refused only because the lost set's report moved."""
        env = self.real_state()
        lossy = self.fake / "lossy"
        lossy.write_text("morphometry_enhance", encoding="utf-8")
        lost = self.gate("morphometry", "enhance", HPCW_LOSSY=str(lossy))
        self.assertEqual(lost.returncode, 1, lost.stdout)
        # the lost job is queued under Slurm and running: Slurm lists an id the gate never recorded
        (self.fake / "queue").write_text("101\n", encoding="utf-8")
        done = self.gate("morphometry", "verse")
        print("\n--- verse sent while the lost enhance job runs:\n" + done.stdout)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        verse_line = self.jobs("morphometry_verse")[0]
        self.assertNotIn("--dependency", verse_line)
        refused = self.gate("morphometry", "covariates", **env)
        print("--- covariates sent then:\n" + refused.stdout)
        self.assertEqual(refused.returncode, 2, refused.stdout)
        self.assertIn("the morphometry enhance report (send morphometry enhance first)", refused.stdout)

    def test_vc_a_lost_word_queues_a_second_job_beside_the_lost_one_that_slurm_still_runs(self):
        """The lost submission did reach Slurm and runs: its part names its job, which squeue lists. The word
        for the lost one (the owner reading "may be queued") queues a second enhance job beside it, and the
        gate moves the running job's part away."""
        env = self.real_state()
        lossy = self.fake / "lossy"
        lossy.write_text("morphometry_enhance", encoding="utf-8")
        lost = self.gate("morphometry", "enhance", HPCW_LOSSY=str(lossy))
        self.assertEqual(lost.returncode, 1, lost.stdout)
        logs = self.repo / "grid" / "logs"
        part = logs / "MORPHOMETRY-enhance.md.part"
        part.write_text("# morphometry enhance: job 555 on node, commit 0000000, 2026-10-30 16:00:00 UTC\n"
                        "- ENHANCE.PET: 1597 masks linked\n", encoding="utf-8")
        self.live(555)
        refused = self.gate("morphometry", "enhance")
        print("\n--- while the lost job 555 runs:\n" + refused.stdout)
        self.assertEqual(refused.returncode, 64, refused.stdout)
        self.allow_morphometry_rerun("enhance:40872077 verse:40877151 enhance:lost")
        done = self.gate("morphometry", "enhance")
        print("--- the lost word, job 555 still live:\n" + done.stdout)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.jobs("morphometry_enhance")), 2)
        self.assertFalse(part.exists())
        self.assertTrue((logs / "MORPHOMETRY-enhance-555.part").exists())

    def test_vc_a_refused_second_check_spends_the_word_with_no_job(self):
        """hpcw_submit asks --check again before it queues; a refusal there queues nothing, but the gate has
        already moved the report and written the marker, so the next send asks for a lost word."""
        env = self.real_state()
        flaky = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/verify-count/flaky-hpcworker"
        done = self.gate("morphometry", "enhance", HPCWORKER=flaky)
        print("\n--- the send whose second check is refused:\n" + done.stdout + done.stderr)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.submitted(), [])
        logs = self.repo / "grid" / "logs"
        self.assertTrue((logs / "MORPHOMETRY-enhance.sent").exists())
        self.assertFalse((logs / "MORPHOMETRY-enhance.md").exists())
        again = self.gate("morphometry", "enhance")
        print("--- the next send:\n" + again.stdout)
        self.assertEqual(again.returncode, 64, again.stdout)
        self.assertIn("MORPHOMETRY_RERUNS=enhance:lost", again.stdout)
        self.assertEqual(self.submitted(), [])


if __name__ == "__main__":
    unittest.main()
