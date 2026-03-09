"""Compatibility wrappers for ROI helpers from ``rppg_core``."""

from __future__ import annotations

import sys
from pathlib import Path

PAPERS_ROOT = Path(__file__).resolve().parents[2]
if str(PAPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(PAPERS_ROOT))

from rppg_core.utils.roi import (
    FaceDetector,
    extract_forehead_roi,
    extract_left_cheek_roi,
    extract_named_face_rois,
    extract_right_cheek_roi,
)

__all__ = [
    "FaceDetector",
    "extract_forehead_roi",
    "extract_left_cheek_roi",
    "extract_right_cheek_roi",
    "extract_named_face_rois",
]
