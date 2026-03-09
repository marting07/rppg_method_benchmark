"""Compatibility wrapper for PBV method from ``rppg_core``."""

from __future__ import annotations

import sys
from pathlib import Path

PAPERS_ROOT = Path(__file__).resolve().parents[2]
if str(PAPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(PAPERS_ROOT))

from rppg_core.methods.pbv import PBVMethod

__all__ = ["PBVMethod"]
