"""Compatibility exports backed by the shared ``rppg_core`` package."""

from __future__ import annotations

import sys
from pathlib import Path

PAPERS_ROOT = Path(__file__).resolve().parents[2]
if str(PAPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(PAPERS_ROOT))

from rppg_core import ChromMethod, GreenMethod, ICAMethod, LGIMethod, PBVMethod, POSMethod, SSRMethod
from rppg_core.methods.base import RPPGMethod

__all__ = ["RPPGMethod", "GreenMethod", "ChromMethod", "POSMethod", "SSRMethod", "ICAMethod", "PBVMethod", "LGIMethod"]
