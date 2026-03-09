"""Compatibility exports backed by shared ``rppg_core.utils``."""

from __future__ import annotations

import sys
from pathlib import Path

PAPERS_ROOT = Path(__file__).resolve().parents[2]
if str(PAPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(PAPERS_ROOT))

from rppg_core.utils.bandpass_filter import bandpass_filter
from rppg_core.utils.roi import FaceDetector, extract_forehead_roi

__all__ = ["bandpass_filter", "FaceDetector", "extract_forehead_roi"]
