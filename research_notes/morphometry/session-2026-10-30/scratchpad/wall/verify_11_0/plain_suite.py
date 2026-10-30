"""Run BasivertebralNotch as the suite has it with the wall's robust fit replaced by one plain
least-squares fit (trimmed_start a plain fit, biweight the identity), to see whether it fails."""
import unittest

import numpy as np

from morphometry import body as BODY

BODY.trimmed_start = lambda X, y, z: np.linalg.lstsq(X, y, rcond=None)[0]
BODY.biweight = lambda X, y, coef, scale: coef

from morphometry.tests import test_morphometry as T  # noqa: E402

suite = unittest.TestLoader().loadTestsFromTestCase(T.BasivertebralNotch)
unittest.TextTestRunner(verbosity=2).run(suite)
