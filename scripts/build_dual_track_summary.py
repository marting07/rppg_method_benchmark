#!/usr/bin/env python3
"""Join Track A and Track B aggregate metrics for paper-level synthesis."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--track-a-method-means",
        default=Path("outputs/data/aggregate/ubfc_full_active_method_means.csv"),
        type=Path,
    )
    p.add_argument(
        "--track-b-liveness-metrics",
        default=Path("../rppg_live_backend_service/outputs/data/aggregate/live_liveness_metrics.csv"),
        type=Path,
    )
    p.add_argument(
        "--out",
        default=Path("outputs/data/aggregate/dual_track_synthesis.csv"),
        type=Path,
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    with args.track_a_method_means.open("r", encoding="utf-8", newline="") as f:
        track_a_rows = list(csv.DictReader(f))

    with args.track_b_liveness_metrics.open("r", encoding="utf-8", newline="") as f:
        track_b_rows = list(csv.DictReader(f))

    if not track_b_rows:
        raise RuntimeError(f"No Track B rows in {args.track_b_liveness_metrics}")

    tb = track_b_rows[0]
    out_rows: list[dict[str, str]] = []
    for row in track_a_rows:
        out_rows.append(
            {
                "track_a_method": row.get("method", ""),
                "track_a_mean_mae": row.get("mean_mae", ""),
                "track_a_mean_rmse": row.get("mean_rmse", ""),
                "track_a_mean_corr": row.get("mean_pearson_correlation", ""),
                "track_b_samples": tb.get("samples", ""),
                "track_b_accuracy": tb.get("accuracy", ""),
                "track_b_precision_live": tb.get("precision_live", ""),
                "track_b_recall_live": tb.get("recall_live", ""),
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "track_a_method",
                "track_a_mean_mae",
                "track_a_mean_rmse",
                "track_a_mean_corr",
                "track_b_samples",
                "track_b_accuracy",
                "track_b_precision_live",
                "track_b_recall_live",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote dual-track synthesis: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
