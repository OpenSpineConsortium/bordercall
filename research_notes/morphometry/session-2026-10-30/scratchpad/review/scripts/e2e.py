"""End to end on phantoms: the old job, the gate's rerun word, the new job, then what the join reads.

Reuses tests/test_gate.py's harness (fake hpcworker, squeue) by loading it by path; writes only under
temporary folders and this scratch folder.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

SP = Path("/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad")
CLONE = Path("/home/user/SchwingNet")
PY = SP / "venv" / "bin" / "python"
OLD_GRID = SP / "review" / "old-main-grid" / "grid"
PHANTOMS = SP / "review" / "phantom" / "masks"
OUTDIR = SP / "review" / "e2e-out"

spec = importlib.util.spec_from_file_location("test_gate", CLONE / "tests" / "test_gate.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


def git_repo(path):
    quiet = ["-c", "gc.auto=0", "-c", "maintenance.auto=false", "-c", "user.name=t", "-c", "user.email=t@example.org"]
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), *quiet, "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), *quiet, "commit", "-q", "-m", "x"], check=True)


def screening_stub(out_set):
    """A venv stand-in so the job makes no venv and installs nothing: its python lacks icontract, so the
    screening steps fail as reported steps, which the measuring does not depend on."""
    env = out_set / "env"
    (env / "bin").mkdir(parents=True, exist_ok=True)
    (env / "READY").write_text("stub\n", encoding="utf-8")
    stub = env / "bin" / "python"
    stub.write_text(f"#!/bin/bash\nexec {PY} \"$@\"\n", encoding="utf-8")
    stub.chmod(0o755)


class E2E(T.GateTest):
    def run_job(self, repo, job, root, label):
        env = dict(os.environ, SCHWINGNET=str(repo), DATA_ROOT=str(self.data), LAB_VOLUME=str(self.tmp / "elsewhere"),
                   MORPHOMETRY_ROOT=str(root), SET="enhance", MORPHOMETRY_PYTHON=str(PY), SLURM_CPUS_PER_TASK="2",
                   SLURM_JOB_ID=str(job))
        done = subprocess.run(["bash", str(repo / "grid" / "morphometry.sbatch")], cwd=repo / "grid", env=env,
                              capture_output=True, text=True, timeout=1800)
        report = (repo / "grid" / "logs" / "MORPHOMETRY-enhance.md").read_text(encoding="utf-8")
        (OUTDIR / f"{label}-report.md").write_text(report, encoding="utf-8")
        (OUTDIR / f"{label}-stdout.txt").write_text(done.stdout + done.stderr, encoding="utf-8")
        return done, report

    def test_rerun_on_phantoms(self):
        OUTDIR.mkdir(parents=True, exist_ok=True)
        labels = self.data / "aws_enhance_pet_labels" / "raw" / "Vertebrae"
        labels.mkdir(parents=True)
        for mask in sorted(PHANTOMS.glob("*.nii.gz")):
            shutil.copy(mask, labels / mask.name)
        root = self.tmp / "go2432" / "morphometry"
        screening_stub(root / "enhance")
        # the old checkout: origin/main's grid/ (old job script, old engine 16f7b40)
        old = self.tmp / "old"
        shutil.copytree(OLD_GRID, old / "grid", ignore=shutil.ignore_patterns("logs"))
        git_repo(old)
        done, old_report = self.run_job(old, 40872077, root, "old")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr + old_report)
        # the same clone after the pull: the old report standing in the new checkout's logs
        logs = self.repo / "grid" / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        shutil.copy(old / "grid" / "logs" / "MORPHOMETRY-enhance.md", logs / "MORPHOMETRY-enhance.md")
        word = self.gate("morphometry", "enhance")
        (OUTDIR / "gate-word.txt").write_text(word.stdout + word.stderr, encoding="utf-8")
        self.assertEqual(word.returncode, 0, word.stdout + word.stderr)
        line = self.submitted()[-1]
        handed = re.search(r"MORPHOMETRY_ROOT=(\S+)", line).group(1)
        self.assertEqual(handed, str(root))
        self.covariates_commit()
        done, new_report = self.run_job(self.repo, 50000001, root, "new")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr + new_report)
        listing = subprocess.run(["find", str(root / "enhance"), "-maxdepth", "3", "-not", "-path", "*/env/*"],
                                 capture_output=True, text=True).stdout
        (OUTDIR / "tree.txt").write_text(listing.replace(str(root), "<root>"), encoding="utf-8")
        kept_report = (logs / "MORPHOMETRY-enhance-40872077.md").read_text(encoding="utf-8")
        (OUTDIR / "kept-report.md").write_text(kept_report, encoding="utf-8")
        # what the join would read from these rows: the code row and the stand-ins
        join = T.load_module(CLONE / "tools" / "gold3_covariates.py", "gold3_covariates_e2e")
        rows = join.read_rows(root / "enhance" / "rows.csv", join.enhance_id)
        report = join.Report()
        line = join.code_line({"ENHANCE.PET": rows.codes}, report)
        kept_rows = join.read_rows(root / "enhance" / "kept" / "40872077" / "rows.csv", join.enhance_id)
        kept_line = join.code_line({"ENHANCE.PET": kept_rows.codes}, join.Report())
        mixed = join.Report()
        both = join.code_line({"ENHANCE.PET": rows.codes, "VerSe": kept_rows.codes}, mixed)
        (OUTDIR / "join.txt").write_text(
            f"new rows: {line}; failures {report.failures}; stand-ins {sorted(rows.stand_ins)}\n"
            f"kept rows: {kept_line}\nnew beside kept: {both}; failures {mixed.failures}\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v", "E2E.test_rerun_on_phantoms"])
