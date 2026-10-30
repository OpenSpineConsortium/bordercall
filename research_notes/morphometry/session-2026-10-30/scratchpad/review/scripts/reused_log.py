"""Run the committed stacking test, then look at what a stack kept from an earlier job leaves behind:
its verdict, and whether the per-subject log the report names exists. Writes nothing in the clone."""
import importlib.util
import sys
import unittest
from pathlib import Path

CLONE = Path("/home/user/SchwingNet")
spec = importlib.util.spec_from_file_location("test_gate", CLONE / "tests" / "test_gate.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


class Probe(T.GateTest):
    def test_reused_stack_log(self):
        self.test_the_morphometry_job_stacks_the_totalsegmentator_subjects_in_parallel_and_counts_each_verdict_once()
        out = self.tmp / "go2432" / "morphometry" / "verse" / "totalseg"
        logs = sorted(p.name for p in (out / "int16").iterdir())
        verdict = (out / "stacked" / "s0005.verdict").read_text(encoding="utf-8").strip()
        report = (self.repo / "grid" / "logs" / "MORPHOMETRY-verse.md").read_text(encoding="utf-8")
        line = [l for l in report.splitlines() if l.startswith("- TotalSegmentator:")]
        print("int16 logs:", logs)
        print("s0005 verdict:", verdict, "| s0005 log exists:", (out / "int16" / "s0005.log").exists())
        print("int16.log exists:", (out / "int16.log").exists())
        print("report line:", line[0].replace(str(out), "<TS>") if line else None)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v", "Probe.test_reused_stack_log"])
