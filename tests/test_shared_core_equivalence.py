from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAPERS_ROOT = PROJECT_ROOT.parent
if str(PAPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(PAPERS_ROOT))

from rppg_core import GreenMethod as CoreGreenMethod
from rppg_methods import GreenMethod as WrapperGreenMethod


class SharedCoreEquivalenceTests(unittest.TestCase):
    def test_wrapper_and_core_green_match(self) -> None:
        fs = 30.0
        core = CoreGreenMethod(fs=fs, buffer_size=300)
        wrapper = WrapperGreenMethod(fs=fs, buffer_size=300)

        for i in range(360):
            t = i / fs
            g = 128.0 + 18.0 * np.sin(2.0 * np.pi * 1.2 * t)
            roi = np.zeros((16, 16, 3), dtype=np.uint8)
            roi[:, :, 1] = np.clip(int(round(g)), 0, 255)
            roi[:, :, 0] = 90
            roi[:, :, 2] = 110
            core.update(roi)
            wrapper.update(roi)

        c_hr = core.get_hr()
        w_hr = wrapper.get_hr()
        self.assertIsNotNone(c_hr)
        self.assertIsNotNone(w_hr)
        assert c_hr is not None and w_hr is not None
        self.assertAlmostEqual(c_hr, w_hr, places=6)


if __name__ == "__main__":
    unittest.main()
