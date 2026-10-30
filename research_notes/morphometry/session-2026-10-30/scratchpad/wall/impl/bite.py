"""Do the new tests bite? Run them with body.read_wall replaced by the reading it replaced (the
hindmost body point of each layer, copied in probe_tests.old_wall), and expect them to fail.

  PYTHONPATH=<bordercall>:<this folder> python bite.py
"""
import unittest
from unittest import mock

from morphometry import body as BODY
from morphometry.tests import test_morphometry as T
from probe_tests import old_wall

NAMES = ["LeanedWall.test_wall_on_the_staircase", "BasivertebralNotch.test_wall_past_the_notch",
         "BasivertebralNotch.test_end_plate_inclinations", "ThickSlices.test_end_plate_inclinations"]


def old_reading(v, B, xc):
    return old_wall(v, B, xc), {"free_deg": 0.0}      # the record every read wall carries; the old one had none


def main():
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n, T) for n in NAMES)
    with mock.patch.object(BODY, "read_wall", side_effect=old_reading):
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("failed %d of %d with the old reading" % (len(result.failures) + len(result.errors), result.testsRun))


if __name__ == "__main__":
    main()
