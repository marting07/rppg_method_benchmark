#!/usr/bin/env python3
"""Constrained nested tuning for rPPG method parameters on a manifest."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path


METHODS = ("green", "chrom", "pos", "ssr", "ica", "pbv", "lgi")


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"No rows in manifest: {path}")
    return rows


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["corpus_id", "subject_id", "scenario_id", "video_path", "ground_truth_path"],
        )
        writer.writeheader()
        writer.writerows(rows)


def by_subject(rows: list[dict[str, str]]) -> list[tuple[str, list[dict[str, str]]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        grouped.setdefault(r["subject_id"], []).append(r)
    return sorted(grouped.items(), key=lambda kv: kv[0])


def make_folds(subject_groups: list[tuple[str, list[dict[str, str]]]], n_folds: int) -> list[list[str]]:
    folds: list[list[str]] = [[] for _ in range(n_folds)]
    for idx, (sid, _rows) in enumerate(subject_groups):
        folds[idx % n_folds].append(sid)
    return folds


def rows_for_subjects(groups: list[tuple[str, list[dict[str, str]]]], subject_ids: set[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for sid, rows in groups:
        if sid in subject_ids:
            out.extend(rows)
    return out


def load_method_means(path: Path, method: str) -> dict[str, float]:
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("method") == method:
                return {
                    "mean_mae": float(row["mean_mae"]),
                    "mean_rmse": float(row["mean_rmse"]),
                    "mean_pearson_correlation": float(row["mean_pearson_correlation"]),
                    "mean_failure_rate_gt_10bpm": float(row["mean_failure_rate_gt_10bpm"]),
                }
    raise RuntimeError(f"Method row not found: {method} in {path}")


def score(metrics: dict[str, float]) -> float:
    return (
        metrics["mean_mae"]
        + 0.35 * metrics["mean_rmse"]
        + 8.0 * metrics["mean_failure_rate_gt_10bpm"]
        - 4.0 * metrics["mean_pearson_correlation"]
    )


def run_batch(
    manifest_path: Path,
    aggregate_out: Path,
    method: str,
    scenario: str,
    output_dir: Path,
    params: dict[str, float],
) -> tuple[bool, str]:
    cmd = [
        sys.executable,
        "scripts/run_manifest_batch.py",
        "--manifest",
        str(manifest_path),
        "--methods",
        method,
        "--scenario",
        scenario,
        "--output-dir",
        str(output_dir),
        "--aggregate-out",
        str(aggregate_out),
        "--ground-truth-mode",
        "bpm_row",
        "--max-lag-seconds",
        "2.0",
        "--roi-fusion-mode",
        "multi_snr",
        "--roi-snr-exponent",
        str(params["roi_snr_exponent"]),
        "--welch-window-seconds",
        str(params["welch_window_seconds"]),
        "--welch-overlap-ratio",
        str(params["welch_overlap_ratio"]),
        "--min-hr-confidence",
        str(params["min_hr_confidence"]),
        "--hr-smoothing-alpha",
        str(params["hr_smoothing_alpha"]),
        "--max-hr-jump-bpm-per-s",
        str(params["max_hr_jump_bpm_per_s"]),
        "--quality-min-skin-ratio",
        str(params["quality_min_skin_ratio"]),
        "--quality-max-saturation-ratio",
        str(params["quality_max_saturation_ratio"]),
        "--quality-max-motion-score",
        str(params["quality_max_motion_score"]),
        "--quality-min-roi-pixels",
        str(int(params["quality_min_roi_pixels"])),
        "--hold-max-seconds",
        str(params["hold_max_seconds"]),
        "--hold-decay-per-second",
        str(params["hold_decay_per_second"]),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).replace("\n", " ").strip()
    return True, ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--methods", default="all", help="comma list or 'all'")
    p.add_argument("--scenario", default="still")
    p.add_argument("--output-dir", default=Path("outputs/data"), type=Path)
    p.add_argument("--results-root", default=Path("outputs/data/aggregate/nested_tuning"), type=Path)
    p.add_argument("--folds", type=int, default=2)
    p.add_argument("--inner-train-max-subjects", type=int, default=10)
    p.add_argument("--max-inner-combos", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--welch-window-seconds", default="6.0,8.0")
    p.add_argument("--welch-overlap-ratio", default="0.50,0.65")
    p.add_argument("--min-hr-confidence", default="1.00,1.10")
    p.add_argument("--hr-smoothing-alpha", default="0.20,0.30")
    p.add_argument("--max-hr-jump-bpm-per-s", default="8.0,12.0")
    p.add_argument("--roi-snr-exponent", default="1.0")
    p.add_argument("--quality-min-skin-ratio", default="0.30")
    p.add_argument("--quality-max-saturation-ratio", default="0.10")
    p.add_argument("--quality-max-motion-score", default="0.08")
    p.add_argument("--quality-min-roi-pixels", default="260")
    p.add_argument("--hold-max-seconds", default="1.0")
    p.add_argument("--hold-decay-per-second", default="1.0")
    args = p.parse_args()

    methods = METHODS if args.methods == "all" else tuple(m.strip() for m in args.methods.split(",") if m.strip())
    for m in methods:
        if m not in METHODS:
            raise ValueError(f"Unsupported method: {m}")

    rows = load_manifest(args.manifest)
    groups = by_subject(rows)
    if args.folds < 2 or args.folds > len(groups):
        raise ValueError("folds must be >=2 and <= number of subjects")
    folds = make_folds(groups, args.folds)

    grid = list(
        itertools.product(
            parse_float_list(args.welch_window_seconds),
            parse_float_list(args.welch_overlap_ratio),
            parse_float_list(args.min_hr_confidence),
            parse_float_list(args.hr_smoothing_alpha),
            parse_float_list(args.max_hr_jump_bpm_per_s),
            parse_float_list(args.roi_snr_exponent),
            parse_float_list(args.quality_min_skin_ratio),
            parse_float_list(args.quality_max_saturation_ratio),
            parse_float_list(args.quality_max_motion_score),
            parse_float_list(args.quality_min_roi_pixels),
            parse_float_list(args.hold_max_seconds),
            parse_float_list(args.hold_decay_per_second),
        )
    )
    if not grid:
        raise RuntimeError("Empty parameter grid")

    rng = random.Random(args.seed)
    args.results_root.mkdir(parents=True, exist_ok=True)
    tmp_manifest_dir = args.results_root / "tmp_manifests"
    tmp_manifest_dir.mkdir(parents=True, exist_ok=True)

    fold_rows: list[dict[str, str]] = []
    test_rows_all: list[dict[str, str]] = []

    for method in methods:
        for fold_idx in range(args.folds):
            test_subjects = set(folds[fold_idx])
            train_subjects = set(s for i, f in enumerate(folds) if i != fold_idx for s in f)

            train_list = sorted(train_subjects)
            if args.inner_train_max_subjects > 0 and len(train_list) > args.inner_train_max_subjects:
                train_list = sorted(rng.sample(train_list, args.inner_train_max_subjects))
            train_rows = rows_for_subjects(groups, set(train_list))
            test_rows = rows_for_subjects(groups, test_subjects)

            train_manifest = tmp_manifest_dir / f"{method}_fold{fold_idx+1}_train.csv"
            test_manifest = tmp_manifest_dir / f"{method}_fold{fold_idx+1}_test.csv"
            write_manifest(train_manifest, train_rows)
            write_manifest(test_manifest, test_rows)

            combos = list(grid)
            if len(combos) > args.max_inner_combos:
                combos = rng.sample(combos, args.max_inner_combos)

            best_params: dict[str, float] | None = None
            best_score: float | None = None

            for combo_idx, combo in enumerate(combos, start=1):
                params = {
                    "welch_window_seconds": combo[0],
                    "welch_overlap_ratio": combo[1],
                    "min_hr_confidence": combo[2],
                    "hr_smoothing_alpha": combo[3],
                    "max_hr_jump_bpm_per_s": combo[4],
                    "roi_snr_exponent": combo[5],
                    "quality_min_skin_ratio": combo[6],
                    "quality_max_saturation_ratio": combo[7],
                    "quality_max_motion_score": combo[8],
                    "quality_min_roi_pixels": combo[9],
                    "hold_max_seconds": combo[10],
                    "hold_decay_per_second": combo[11],
                }
                agg_out = args.results_root / f"{method}_fold{fold_idx+1}_inner_{combo_idx:03d}.csv"
                ok, err = run_batch(train_manifest, agg_out, method, args.scenario, args.output_dir, params)
                if not ok:
                    fold_rows.append(
                        {
                            "method": method,
                            "fold": str(fold_idx + 1),
                            "phase": "inner",
                            "status": "failed",
                            "score": "",
                            "mean_mae": "",
                            "mean_rmse": "",
                            "mean_pearson_correlation": "",
                            "mean_failure_rate_gt_10bpm": "",
                            **{k: str(v) for k, v in params.items()},
                            "error": err,
                        }
                    )
                    continue

                means = load_method_means(agg_out.with_name(agg_out.stem + "_method_means.csv"), method)
                s = score(means)
                fold_rows.append(
                    {
                        "method": method,
                        "fold": str(fold_idx + 1),
                        "phase": "inner",
                        "status": "ok",
                        "score": f"{s:.6f}",
                        "mean_mae": f"{means['mean_mae']:.6f}",
                        "mean_rmse": f"{means['mean_rmse']:.6f}",
                        "mean_pearson_correlation": f"{means['mean_pearson_correlation']:.6f}",
                        "mean_failure_rate_gt_10bpm": f"{means['mean_failure_rate_gt_10bpm']:.6f}",
                        **{k: str(v) for k, v in params.items()},
                        "error": "",
                    }
                )
                if best_score is None or s < best_score:
                    best_score = s
                    best_params = params

            if best_params is None:
                continue

            outer_agg = args.results_root / f"{method}_fold{fold_idx+1}_outer_test.csv"
            ok, err = run_batch(test_manifest, outer_agg, method, args.scenario, args.output_dir, best_params)
            if not ok:
                test_rows_all.append(
                    {
                        "method": method,
                        "fold": str(fold_idx + 1),
                        "status": "failed",
                        "score": "",
                        "mean_mae": "",
                        "mean_rmse": "",
                        "mean_pearson_correlation": "",
                        "mean_failure_rate_gt_10bpm": "",
                        **{k: str(v) for k, v in best_params.items()},
                        "error": err,
                    }
                )
                continue
            means = load_method_means(outer_agg.with_name(outer_agg.stem + "_method_means.csv"), method)
            s = score(means)
            test_rows_all.append(
                {
                    "method": method,
                    "fold": str(fold_idx + 1),
                    "status": "ok",
                    "score": f"{s:.6f}",
                    "mean_mae": f"{means['mean_mae']:.6f}",
                    "mean_rmse": f"{means['mean_rmse']:.6f}",
                    "mean_pearson_correlation": f"{means['mean_pearson_correlation']:.6f}",
                    "mean_failure_rate_gt_10bpm": f"{means['mean_failure_rate_gt_10bpm']:.6f}",
                    **{k: str(v) for k, v in best_params.items()},
                    "error": "",
                }
            )

    fieldnames = [
        "method",
        "fold",
        "phase",
        "status",
        "score",
        "mean_mae",
        "mean_rmse",
        "mean_pearson_correlation",
        "mean_failure_rate_gt_10bpm",
        "welch_window_seconds",
        "welch_overlap_ratio",
        "min_hr_confidence",
        "hr_smoothing_alpha",
        "max_hr_jump_bpm_per_s",
        "roi_snr_exponent",
        "quality_min_skin_ratio",
        "quality_max_saturation_ratio",
        "quality_max_motion_score",
        "quality_min_roi_pixels",
        "hold_max_seconds",
        "hold_decay_per_second",
        "error",
    ]
    inner_csv = args.results_root / "nested_inner_results.csv"
    with inner_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in fold_rows:
            out = {k: "" for k in fieldnames}
            out.update(r)
            w.writerow(out)

    outer_fields = [k for k in fieldnames if k != "phase"]
    outer_csv = args.results_root / "nested_outer_results.csv"
    with outer_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=outer_fields)
        w.writeheader()
        for r in test_rows_all:
            out = {k: "" for k in outer_fields}
            out.update(r)
            w.writerow(out)

    # Summarize outer-fold means per method and choose a global config by vote among winning folds.
    summary: list[dict[str, str]] = []
    best_global: dict[str, dict[str, float]] = {}
    for method in methods:
        ok_rows = [r for r in test_rows_all if r["method"] == method and r["status"] == "ok"]
        if not ok_rows:
            continue
        mae = sum(float(r["mean_mae"]) for r in ok_rows) / len(ok_rows)
        rmse = sum(float(r["mean_rmse"]) for r in ok_rows) / len(ok_rows)
        corr = sum(float(r["mean_pearson_correlation"]) for r in ok_rows) / len(ok_rows)
        fail = sum(float(r["mean_failure_rate_gt_10bpm"]) for r in ok_rows) / len(ok_rows)
        summary.append(
            {
                "method": method,
                "folds_ok": str(len(ok_rows)),
                "outer_mean_mae": f"{mae:.6f}",
                "outer_mean_rmse": f"{rmse:.6f}",
                "outer_mean_pearson_correlation": f"{corr:.6f}",
                "outer_mean_failure_rate_gt_10bpm": f"{fail:.6f}",
            }
        )

        # Vote best config from outer rows by lowest score.
        best_row = min(ok_rows, key=lambda r: float(r["score"]))
        keys = [
            "welch_window_seconds",
            "welch_overlap_ratio",
            "min_hr_confidence",
            "hr_smoothing_alpha",
            "max_hr_jump_bpm_per_s",
            "roi_snr_exponent",
            "quality_min_skin_ratio",
            "quality_max_saturation_ratio",
            "quality_max_motion_score",
            "quality_min_roi_pixels",
            "hold_max_seconds",
            "hold_decay_per_second",
        ]
        best_global[method] = {k: float(best_row[k]) for k in keys}

    summary_csv = args.results_root / "nested_outer_summary_method_means.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "method",
                "folds_ok",
                "outer_mean_mae",
                "outer_mean_rmse",
                "outer_mean_pearson_correlation",
                "outer_mean_failure_rate_gt_10bpm",
            ],
        )
        w.writeheader()
        w.writerows(summary)

    best_json = args.results_root / "nested_best_params.json"
    best_json.write_text(json.dumps(best_global, indent=2), encoding="utf-8")

    print(f"Wrote: {inner_csv}")
    print(f"Wrote: {outer_csv}")
    print(f"Wrote: {summary_csv}")
    print(f"Wrote: {best_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
