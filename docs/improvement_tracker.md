# rPPG Improvement Tracker

This file tracks implementation progress for the five agreed improvement areas.

Legend:

- `[ ]` pending
- `[~]` in progress
- `[x]` completed

## 1) Method fidelity and explainability

Status: `[x]`

Tasks:

- [x] Split method workflow into explicit stages (`signal_extraction`, `normalization`, `filtering`, `hr_estimation`) in code structure.
- [x] Add clear equations and algorithm flow notes in method docs.
- [x] Link each method implementation block to primary literature references.
- [x] Mark simplified JBSS behavior explicitly in code and docs.

## 2) Scientific comparison protocol

Status: `[x]`

Tasks:

- [x] Define fixed experimental scenarios (still, motion, lighting, distance).
- [x] Standardize comparison parameters (window, frequency band, BPM range).
- [x] Define required metrics (MAE, RMSE, Pearson correlation).
- [x] Add protocol configuration file for reproducible experiments.

## 3) Data and reproducibility pipeline

Status: `[x]`

Tasks:

- [x] Add offline evaluation runner for recorded videos.
- [x] Export per-frame and per-window signals to CSV.
- [x] Save structured run metadata (method, fs, config, timestamp).
- [x] Support deterministic outputs for repeated runs.

## 4) Figure generation for paper

Status: `[x]`

Tasks:

- [x] Generate per-method signal plots (raw, filtered, PSD, BPM vs time).
- [x] Generate comparison plots (error boxplot, Bland-Altman, failure rate).
- [x] Save plots in publication-friendly format and naming.
- [x] Document how to regenerate all figures from commands.

## 5) Code quality and publication readiness

Status: `[x]`

Tasks:

- [x] Add tests for short-buffer filtering behavior.
- [x] Add tests for no-face / empty ROI handling.
- [x] Add synthetic-signal tests for deterministic HR estimation.
- [x] Add publication docs (`docs/methods.md`, `docs/experimental_protocol.md`).

## Execution Task List

- [x] T1 Create tracking document and folder layout.
- [x] T2 Refactor method pipeline and add explanatory docs.
- [x] T3 Add protocol config and experiment definitions.
- [x] T4 Implement offline evaluator and structured outputs.
- [x] T5 Implement figure generation scripts.
- [x] T6 Add tests and publication docs.
- [x] T7 Update README and tracker to final state.

## Validation Notes

- `python3 -m py_compile` passed for updated source files.
- `python3 -m unittest discover -s tests -p "test_*.py"` is currently blocked in this shell due to missing installed dependencies (`scipy`, `cv2`).
- Run `make install` then `make test` in project `.venv` to execute the test suite end-to-end.
