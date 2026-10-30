    def allow_morphometry_rerun(self, word):
        """The owner's word for one more measuring of a set, as a pull request commits it in grid/gate.sh."""
        gate = self.repo / "grid" / "gate.sh"
        text, count = re.subn(r'(?m)^MORPHOMETRY_RERUNS="[^"]*"$', f'MORPHOMETRY_RERUNS="{word}"', gate.read_text(encoding="utf-8"))
        self.assertEqual(count, 1)
        gate.write_text(text, encoding="utf-8")

    def morphometry_report(self, which, job, rc=0):
        """A set's report as its job leaves it: the first line naming the job and a commit, the last its exit."""
        report = self.repo / "grid" / "logs" / f"MORPHOMETRY-{which}.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(f"# morphometry {which}: job {job} on node, commit 0000000, 2026-10-29 16:00:00 UTC\n"
                          f"- rows of job {job}\n- exit {rc} at 2026-10-29 20:00:00 UTC\n", encoding="utf-8")
        return report

    MORPHOMETRY_RUN = ("rows/0001.csv", "rows.csv", "run.log", "steps.log", "facts.log", "whole.log", "facts.jsonl",
                       "verdicts.csv", "inputs.txt")
    MORPHOMETRY_REUSED = ("masks/0001.nii.gz", "env/READY", "env.log")
    TOTALSEG_RUN = ("rows/s0001.csv", "rows.csv", "run.log", "steps.log", "facts.log", "whole.log", "facts.jsonl",
                    "verdicts.csv", "ids.txt")
    TOTALSEG_REUSED = ("masks/s0001.nii.gz", "manifests/s0001.json", "stacked/s0001.verdict", "int16/s0001.log")

    def morphometry_outputs(self, which, job):
        """The set's folder under the morphometry root as a whole run of JOB leaves it, each file naming JOB."""
        out = self.tmp / "go2432" / "morphometry" / which
        names = list(self.MORPHOMETRY_RUN + self.MORPHOMETRY_REUSED)
        if which == "verse":
            names += [f"totalseg/{name}" for name in self.TOTALSEG_RUN + self.TOTALSEG_REUSED]
        for name in names:
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"job {job}\n", encoding="utf-8")
        return out

    def test_the_committed_morphometry_reruns_are_the_owners_count_of_three(self):
        # the owner's choice of 2026-10-30 14:33 UTC, "Three: enhance, verse, covariates", as committed
        text = (GRID / "gate.sh").read_text(encoding="utf-8")
        self.assertRegex(text, r'(?m)^MORPHOMETRY_RERUNS="enhance:40872077 verse:40877151"$')
        self.assertRegex(text, r'(?m)^COVARIATES_RERUNS="covariates:40878978"$')
        # walked with the real job numbers: each set's first report is kept and the set queued once more,
        # and the report of the job that follows only prints
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        for which, job in (("enhance", 40872077), ("verse", 40877151)):
            self.morphometry_report(which, job)
            out = self.morphometry_outputs(which, job)
            done = self.gate("morphometry", which)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn(f"is job {job}'s, which MORPHOMETRY_RERUNS lets the owner's count measure once more", done.stdout)
            self.assertIn(f"rows of job {job}", (logs / f"MORPHOMETRY-{which}-{job}.md").read_text(encoding="utf-8"))
            self.assertEqual((out / "kept" / str(job) / "rows.csv").read_text(encoding="utf-8"), f"job {job}\n")
            queued = self.recorded()[f"morphometry_{which}"]
            self.morphometry_report(which, queued)
            for _ in range(2):
                again = self.gate("morphometry", which)
                self.assertEqual(again.returncode, 0, again.stdout)
                self.assertIn(f"rows of job {queued}", again.stdout)
                self.assertNotIn("queueing", again.stdout)
        self.assertEqual(len(self.submitted()), 2)

    def test_morphometry_reruns_a_set_once_for_the_job_the_word_names_and_keeps_its_report_and_rows(self):
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        report = self.morphometry_report("enhance", 4242)
        out = self.morphometry_outputs("enhance", 4242)
        # a word for another job, for the other set or for a lost answer that is not there queues nothing
        for word in ("enhance:4243", "verse:4242", "enhance:lost", ""):
            self.allow_morphometry_rerun(word)
            done = self.gate("morphometry", "enhance")
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertIn("rows of job 4242", done.stdout)
            self.assertNotIn("queueing", done.stdout)
        self.assertEqual(self.submitted(), [])
        self.assertFalse((out / "kept").exists())
        # the word for the report's job queues the set once, its report and its rows kept under that job
        self.allow_morphometry_rerun("enhance:4242")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("the report above is job 4242's, which MORPHOMETRY_RERUNS lets the owner's count measure once more: "
                      "queueing the set again", done.stdout)
        lines = self.submitted()
        self.assertEqual(len(lines), 1, lines)
        for said in ("--class batch --name morphometry_enhance", "SET=enhance", f"MORPHOMETRY_ROOT={self.tmp}/go2432/morphometry",
                     "--no-requeue", "--time 24:00:00", "morphometry.sbatch"):
            self.assertIn(said, lines[0])
        self.assertFalse(report.exists())
        self.assertIn("rows of job 4242", (logs / "MORPHOMETRY-enhance-4242.md").read_text(encoding="utf-8"))
        for name in self.MORPHOMETRY_RUN:
            self.assertEqual((out / "kept" / "4242" / name).read_text(encoding="utf-8"), "job 4242\n", name)
            self.assertFalse((out / name).exists(), name)
        # what the next job reuses stays where it reads it
        for name in self.MORPHOMETRY_REUSED:
            self.assertEqual((out / name).read_text(encoding="utf-8"), "job 4242\n", name)
        self.assertFalse((logs / "MORPHOMETRY-enhance.sent").exists())
        # while it is live every morphometry word waits, the join's among them
        job = self.recorded()["morphometry_enhance"]
        self.live(job)
        for which in ("enhance", "verse", "covariates"):
            refused = self.gate("morphometry", which)
            self.assertEqual(refused.returncode, 75, refused.stdout)
            self.assertIn(f"job {job}", refused.stdout)
        (self.fake / "queue").write_text("", encoding="utf-8")
        # its report queues nothing more, though the word still stands
        self.morphometry_report("enhance", job)
        for _ in range(2):
            done = self.gate("morphometry", "enhance")
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertIn(f"rows of job {job}", done.stdout)
        self.assertEqual(len(self.submitted()), 1)

    def test_a_morphometry_rerun_of_a_set_that_failed_keeps_its_report_and_leaves_its_rows_to_resume(self):
        # a run that ended in failure on this commit is no whole run: the word queues it once more, and its
        # rows, measured by the code stamp they carry, stay for the next job to resume from
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        self.morphometry_report("enhance", 4242, rc=1)
        out = self.morphometry_outputs("enhance", 4242)
        self.allow_morphometry_rerun("enhance:4242")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue((logs / "MORPHOMETRY-enhance-4242.md").exists())
        self.assertEqual((out / "rows.csv").read_text(encoding="utf-8"), "job 4242\n")
        self.assertFalse((out / "kept").exists())
        self.assertEqual(len(self.submitted()), 1)

    def test_a_verse_rerun_keeps_totalsegmentators_rows_and_leaves_its_stacks_for_the_job(self):
        self.morphometry_inputs("engine")
        masks = self.data / "verse_masks_2026_10_29" / "raw"
        masks.mkdir(parents=True)
        (masks / "verse004.nii.gz").write_text("", encoding="utf-8")
        release = self.data / "totalsegmentator_v300" / "raw" / "Totalsegmentator_dataset_v300"
        (release / "s0001" / "segmentations").mkdir(parents=True)
        admission = self.repo / "data" / "gold3-ct" / "admission.json"
        admission.parent.mkdir(parents=True, exist_ok=True)
        admission.write_text(json.dumps({"studies": [{"id": "s0001", "member": "totalsegmentator", "verdict": "admitted"}]}),
                             encoding="utf-8")
        self.morphometry_report("verse", 4343)
        out = self.morphometry_outputs("verse", 4343)
        ts = out / "totalseg"
        self.allow_morphometry_rerun("verse:4343")
        done = self.gate("morphometry", "verse")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for name in self.MORPHOMETRY_RUN:
            self.assertEqual((out / "kept" / "4343" / name).read_text(encoding="utf-8"), "job 4343\n", name)
        for name in self.TOTALSEG_RUN:
            self.assertEqual((out / "kept" / "4343" / "totalseg" / name).read_text(encoding="utf-8"), "job 4343\n", name)
            self.assertFalse((ts / name).exists(), name)
        for name in self.TOTALSEG_REUSED:
            self.assertEqual((ts / name).read_text(encoding="utf-8"), "job 4343\n", name)
        # the job the word queued, run as the gate handed it its root: the stack is not made again, and
        # nothing it writes lands under kept/
        line = self.submitted()[0]
        root = re.search(r"MORPHOMETRY_ROOT=(\S+)", line).group(1)
        fake_py = self.tmp / "fakepy"
        fake_py.write_text(
            "#!/bin/bash\n"
            "case \"$1 $2 $3\" in\n"
            "  '-c import numpy, scipy, nibabel'*|'-c import icontract, beartype'*) exit 0 ;;\n"
            "  '-m morphometry run') while [ $# -gt 0 ]; do [ \"$1\" = --out ] && out=$2; [ \"$1\" = --masks ] && masks=$2; shift; done;\n"
            "      mkdir -p \"$out\"; n=$(ls \"$masks\" | wc -l); printf 'study,level,key,value,note\\n' > \"$out/rows.csv\";\n"
            "      echo \"$n studies chosen, $n to measure, code fake\"; exit 0 ;;\n"
            "  '-m screening int16') while [ $# -gt 0 ]; do [ \"$1\" = --out ] && out=$2; [ \"$1\" = --manifest ] && man=$2; shift; done;\n"
            "      echo stacked again > \"$out\"; echo '{}' > \"$man\"; exit 0 ;;\n"
            "  '-m screening facts') while [ $# -gt 0 ]; do [ \"$1\" = --out ] && out=$2; shift; done; : > \"$out\"; exit 0 ;;\n"
            "  '-m screening whole') while [ $# -gt 0 ]; do [ \"$1\" = --out ] && out=$2; shift; done; printf 'study,verdict\\n' > \"$out\"; exit 0 ;;\n"
            "  '-c from morphometry.__main__'*) echo fakestamp; exit 0 ;;\n"
            "esac\n"
            "exec python3 \"$@\"\n", encoding="utf-8")
        fake_py.chmod(0o755)
        self.covariates_commit()
        env = dict(os.environ, SCHWINGNET=str(self.repo), DATA_ROOT=str(self.data), LAB_VOLUME=str(self.tmp / "elsewhere"),
                   MORPHOMETRY_ROOT=root, SET="verse", MORPHOMETRY_PYTHON=str(fake_py), SLURM_CPUS_PER_TASK="2")
        ran = subprocess.run(["bash", str(self.repo / "grid" / "morphometry.sbatch")], cwd=self.repo / "grid", env=env,
                             capture_output=True, text=True, timeout=120)
        report = (self.repo / "grid" / "logs" / "MORPHOMETRY-verse.md").read_text(encoding="utf-8")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr + report)
        self.assertIn("TotalSegmentator: 1 admitted subjects; 1 stacked", report)
        self.assertEqual((ts / "masks" / "s0001.nii.gz").read_text(encoding="utf-8"), "job 4343\n")
        self.assertEqual((ts / "stacked" / "s0001.verdict").read_text(encoding="utf-8").strip(), "stacked")
        self.assertEqual((ts / "rows.csv").read_text(encoding="utf-8"), "study,level,key,value,note\n")
        self.assertEqual((out / "rows.csv").read_text(encoding="utf-8"), "study,level,key,value,note\n")
        kept = sorted(str(p.relative_to(out / "kept" / "4343")) for p in (out / "kept" / "4343").rglob("*") if p.is_file())
        self.assertEqual(kept, sorted(list(self.MORPHOMETRY_RUN) + [f"totalseg/{name}" for name in self.TOTALSEG_RUN]))
        self.assertTrue(all((out / "kept" / "4343" / name).read_text(encoding="utf-8") == "job 4343\n" for name in kept))
        self.assertFalse((self.tmp / "elsewhere").exists())

    def test_a_morphometry_rerun_refused_on_its_way_spends_nothing_and_moves_nothing(self):
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        report = self.morphometry_report("enhance", 4242)
        out = self.morphometry_outputs("enhance", 4242)
        self.allow_morphometry_rerun("enhance:4242")

        def untouched():
            self.assertTrue(report.exists())
            self.assertFalse((logs / "MORPHOMETRY-enhance-4242.md").exists())
            self.assertFalse((logs / "MORPHOMETRY-enhance.sent").exists())
            self.assertEqual((out / "rows.csv").read_text(encoding="utf-8"), "job 4242\n")
            self.assertEqual(self.submitted(), [])

        # a shape the scheduler refuses
        (self.fake / "refuse").write_text("morphometry_enhance", encoding="utf-8")
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 1, refused.stdout)
        untouched()
        self.assertFalse((out / "kept").exists())
        (self.fake / "refuse").unlink()
        # an input gone
        shutil.rmtree(self.data / "aws_enhance_pet_labels")
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 2, refused.stdout)
        self.assertIn("fetch aws_enhance_pet_labels first", refused.stdout)
        untouched()
        self.assertFalse((out / "kept").exists())
        self.morphometry_inputs("truth")
        # a kept file already there is never written over, and nothing else moves
        (out / "kept" / "4242").mkdir(parents=True)
        (out / "kept" / "4242" / "verdicts.csv").write_text("someone's\n", encoding="utf-8")
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 2, refused.stdout)
        self.assertIn("is there already", refused.stdout)
        self.assertEqual((out / "kept" / "4242" / "verdicts.csv").read_text(encoding="utf-8"), "someone's\n")
        self.assertEqual(sorted(p.name for p in (out / "kept" / "4242").iterdir()), ["verdicts.csv"])
        untouched()
        shutil.rmtree(out / "kept")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.submitted()), 1)

    def test_morphometry_queues_nothing_after_a_lost_answer_until_the_owners_word(self):
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        lossy = self.fake / "lossy"
        lossy.write_text("morphometry_enhance", encoding="utf-8")
        lost = self.gate("morphometry", "enhance", HPCW_LOSSY=str(lossy))
        self.assertEqual(lost.returncode, 1, lost.stdout)
        self.assertEqual(len(self.submitted()), 1)  # queued under Slurm, its answer lost
        self.assertNotIn("morphometry_enhance", self.recorded())
        self.assertTrue((logs / "MORPHOMETRY-enhance.sent").exists())
        for _ in range(2):
            refused = self.gate("morphometry", "enhance")
            self.assertEqual(refused.returncode, 64, refused.stdout)
            self.assertIn("no job id came back", refused.stdout)
            self.assertIn("committed as MORPHOMETRY_RERUNS=enhance:lost in grid/gate.sh", refused.stdout)
        for word in ("verse:lost", "enhance:101", "enhance:lost2"):
            self.allow_morphometry_rerun(word)
            self.assertEqual(self.gate("morphometry", "enhance").returncode, 64)
        self.assertEqual(len(self.submitted()), 1)
        # the other set is a count of its own
        done = self.gate("morphometry", "verse")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.submitted()), 2)
        # the word for the lost one queues one more, recorded as spent
        self.allow_morphometry_rerun("enhance:lost")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("follows a submission whose answer was lost", done.stdout)
        self.assertEqual(len(self.submitted()), 3)
        self.assertFalse((logs / "MORPHOMETRY-enhance.sent").exists())
        self.assertIn("enhance:lost spent at", (logs / "MORPHOMETRY-enhance.lost").read_text(encoding="utf-8"))
        job = self.recorded()["morphometry_enhance"]
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 64, refused.stdout)
        self.assertIn(f"MORPHOMETRY_RERUNS=enhance:{job} in grid/gate.sh", refused.stdout)
        # a second lost answer needs a word of its own, whatever else still stands
        self.allow_morphometry_rerun(f"enhance:lost enhance:{job}")
        self.assertEqual(self.gate("morphometry", "enhance", HPCW_LOSSY=str(lossy)).returncode, 1)
        self.assertEqual(len(self.submitted()), 4)
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 64, refused.stdout)
        self.assertIn("MORPHOMETRY_RERUNS=enhance:lost2 in grid/gate.sh", refused.stdout)
        self.assertEqual(len(self.submitted()), 4)

    def test_a_morphometry_job_that_left_no_report_waits_for_the_owners_word_and_keeps_its_part(self):
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        logs = self.repo / "grid" / "logs"
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        job = self.recorded()["morphometry_enhance"]
        # cancelled before it wrote anything: no report and no part
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 64, refused.stdout)
        self.assertIn(f"was queued before (job {job}) and left no report", refused.stdout)
        self.assertIn(f"committed as MORPHOMETRY_RERUNS=enhance:{job} in grid/gate.sh", refused.stdout)
        # killed past its trap: what it wrote is printed, and still nothing is queued
        part = logs / "MORPHOMETRY-enhance.md.part"
        part.write_text(f"# morphometry enhance: job {job} on node, commit 0000000, 2026-10-30 16:00:00 UTC\n"
                        "- ENHANCE.PET: 1597 masks linked\n", encoding="utf-8")
        out = self.morphometry_outputs("enhance", job)
        for _ in range(2):
            refused = self.gate("morphometry", "enhance")
            self.assertEqual(refused.returncode, 64, refused.stdout)
            self.assertIn("MORPHOMETRY-enhance.md.part, unfinished", refused.stdout)
            self.assertIn("1597 masks linked", refused.stdout)
        self.assertEqual(len(self.submitted()), 1)
        # the owner's word for it queues one more, the part kept under its job and its rows left to resume
        self.allow_morphometry_rerun(f"enhance:{job}")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn(f"the set's job {job} left no report", done.stdout)
        self.assertEqual(len(self.submitted()), 2)
        self.assertFalse(part.exists())
        self.assertIn("1597 masks linked", (logs / f"MORPHOMETRY-enhance-{job}.part").read_text(encoding="utf-8"))
        self.assertEqual((out / "rows.csv").read_text(encoding="utf-8"), f"job {job}\n")
        self.assertFalse((out / "kept").exists())
        # and the word is spent: the job it queued is the newest, and it left no report either
        refused = self.gate("morphometry", "enhance")
        self.assertEqual(refused.returncode, 64, refused.stdout)
        self.assertIn(f"MORPHOMETRY_RERUNS=enhance:{self.recorded()['morphometry_enhance']} in grid/gate.sh", refused.stdout)
        self.assertEqual(len(self.submitted()), 2)

    def test_morphometry_covariates_waits_while_a_set_rerun_is_pending(self):
        env = self.covariates_inputs()
        logs = self.repo / "grid" / "logs"
        for which in ("enhance", "verse"):
            self.allow_morphometry_rerun(f"{which}:40")
            refused = self.gate("morphometry", "covariates", **env)
            self.assertEqual(refused.returncode, 2, refused.stdout)
            self.assertIn(f"the morphometry {which} rerun the owner counted (the report standing is job 40's", refused.stdout)
        self.assertEqual(self.submitted(), [])
        # the join's own rerun waits too, its report standing and its word unspent
        (logs / "MORPHOMETRY-covariates.md").write_text(
            "# morphometry covariates: job 77 on node, commit 0000000, 2026-10-30 13:00:00 UTC\n"
            "- exit 0 at 2026-10-30 13:10:00 UTC\n", encoding="utf-8")
        self.allow_covariates_rerun("covariates:77")
        refused = self.gate("morphometry", "covariates", **env)
        self.assertEqual(refused.returncode, 2, refused.stdout)
        self.assertTrue((logs / "MORPHOMETRY-covariates.md").exists())
        self.assertFalse((logs / "MORPHOMETRY-covariates.sent").exists())
        self.assertEqual(self.submitted(), [])
        # once neither set's report is one the word names, the join is queued once more
        self.allow_morphometry_rerun("enhance:39 verse:39")
        done = self.gate("morphometry", "covariates", **env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue((logs / "MORPHOMETRY-covariates-77.md").exists())
        self.assertEqual(len(self.submitted()), 1)

    def test_a_morphometry_set_queues_no_setup_job(self):
        # the set runs on the SPINEPS environment's interpreter, so environments not built queue nothing more
        self.morphometry_inputs("engine", "truth", "verse", "totalseg")
        done = self.gate("morphometry", "enhance")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = self.submitted()
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("--name morphometry_enhance", lines[0])
        self.assertNotIn("afterok", lines[0])
        self.assertNotIn("setup", self.recorded())

