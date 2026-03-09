# rPPG Improvement Tracker

Legend:

- `[ ]` pending
- `[~]` in progress
- `[x]` completed

## Active Method Set

Status: `[x]`

- [x] Green
- [x] CHROM
- [x] POS
- [x] SSR/2SR-style

## Core Implementation

Status: `[x]`

- [x] Shared processing pipeline in `rppg_methods/base.py`
- [x] Manual method implementations in `rppg_methods/green.py`, `rppg_methods/chrom.py`, `rppg_methods/pos.py`, `rppg_methods/ssr.py`
- [x] Method exports aligned in `rppg_methods/__init__.py`

## Evaluation and Scripts

Status: `[x]`

- [x] Evaluator factory aligned to active methods (`scripts/offline_evaluate.py`)
- [x] Sweep script choices aligned (`scripts/sweep_method_params.py`)
- [x] Paper illustration defaults aligned (`scripts/create_paper_illustrations.py`)
- [x] Experiment protocol methods aligned (`configs/experiment_protocol.json`)

## Tests

Status: `[x]`

- [x] Behavioral tests aligned to active methods (`tests/test_methods.py`)

## Documentation and Paper

Status: `[x]`

- [x] README updated to active method set
- [x] AGENTS guide updated to active method set
- [x] Methods docs updated:
  - `docs/methods.md`
  - `docs/method_math_to_code.md`
  - `docs/method_pseudocode.md`
  - `docs/experimental_protocol.md`
- [x] Paper draft updated to active method set (`../rppg_modular_live_proof_paper/paper_content_draft.tex`)
- [x] Bibliography aligned to active method citations (`../rppg_modular_live_proof_paper/references.bib`)
- [x] Paper asset bundle created for direct template integration:
  - `../rppg_modular_live_proof_paper/assets/method_equations.tex`
  - `../rppg_modular_live_proof_paper/assets/method_pseudocode.tex`
  - `../rppg_modular_live_proof_paper/assets/method_math_to_code_table.tex`
  - `../rppg_modular_live_proof_paper/assets/figure_assets_index.md`
- [x] Paper base scaffold created:
  - `../rppg_modular_live_proof_paper/paper_base.tex`
  - `../rppg_modular_live_proof_paper/ieee_submission.tex`
  - `../rppg_modular_live_proof_paper/README.md`
- [x] Draft appendices now input local paper assets instead of external docs.
- [x] Paper draft split into modular sections:
  - `../rppg_modular_live_proof_paper/sections/01_title_abstract.tex` ... `../rppg_modular_live_proof_paper/sections/12_references.tex`
  - assembled content entrypoint: `../rppg_modular_live_proof_paper/paper_content_structured.tex`
  - `../rppg_modular_live_proof_paper/paper_base.tex` updated to consume split sections.

## Current Table Artifacts

Status: `[x]`

- [x] `outputs/data/aggregate/ubfc_full_active_methods_method_means.csv`
- [x] `outputs/data/aggregate/ubfc_full_active_method_means.tex`
- [x] `outputs/data/aggregate/ubfc_full_active_method_means.pdf`
- [x] `outputs/data/aggregate/ubfc_full_active_method_means.png`

Current 42-subject UBFC means (active methods, BPM-row GT + multi-ROI SNR fusion + stricter quality gating/hold + redesigned SSR):

- [x] `chrom`: MAE `5.940`, RMSE `7.637`, corr `0.404`, failure `0.183`
- [x] `green`: MAE `13.242`, RMSE `14.635`, corr `0.426`, failure `0.437`
- [x] `pos`: MAE `6.890`, RMSE `8.927`, corr `0.336`, failure `0.223`
- [x] `ssr`: MAE `19.298`, RMSE `20.991`, corr `0.165`, failure `0.717`

## Current Figure Artifacts

Status: `[x]`

- [x] `outputs/paper/figures/paper_subject1_active_v2/`
- [x] `outputs/paper/figures/paper_subject1_active_v2_overview/`
- [x] `outputs/paper/figures/ubfc_rppg_v1_subject1_f87e84d150/`
- [x] `outputs/plots/ubfc_rppg_v1_subject1_f87e84d150/`

## Validation

Status: `[x]`

- [x] Local validation passed (`py_compile`, unit tests)
- [x] Full UBFC batch rerun with `--methods green,chrom,pos,ssr`

## Ground Truth Alignment Pass

Status: `[x]`

- [x] Added UBFC GT mode selection in evaluator (`auto`, `bpm_row`, `bvp_derived`) in `scripts/offline_evaluate.py`
- [x] Added BVP-derived GT BPM path for UBFC three-row files in `scripts/offline_evaluate.py`
- [x] Added per-method lag optimization (`--max-lag-seconds`) before metrics in `scripts/offline_evaluate.py`
- [x] Added lag/source metadata outputs (`summary.csv`, `metadata.json`)
- [x] Updated plot rendering to show GT only where estimates are valid:
  - `scripts/create_paper_illustrations.py`
  - `scripts/generate_figures.py`
- [x] Full UBFC manifest rerun completed with GT alignment (`42/42` successful):
  - `outputs/data/aggregate/ubfc_full_active_methods_gtfix.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_gtfix_method_means.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_gtfix_runs.csv`

## Multi-ROI Fusion Pass

Status: `[x]`

- [x] Added forehead+cheeks ROI extraction helpers in `utils/roi.py`
- [x] Added evaluator ROI fusion modes (`single`, `multi_snr`) and SNR-exponent weighting in `scripts/offline_evaluate.py`
- [x] Switched default comparison GT mode back to `bpm_row` in evaluator and batch runner
- [x] Added batch/Makefile flags for ROI fusion and GT mode:
  - `scripts/run_manifest_batch.py`
  - `Makefile`
- [x] Full UBFC manifest rerun completed with `bpm_row + multi_snr` (`42/42` successful):
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_method_means.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_runs.csv`

## Quality Gating / Hold Pass

Status: `[x]`

- [x] Added stricter, configurable quality gates (skin/saturation/motion/min-pixels) in `scripts/offline_evaluate.py`
- [x] Added bounded quality-hold policy with decay (skip/update-hold behavior) in `scripts/offline_evaluate.py`
- [x] Added quality/hold CLI propagation through:
  - `scripts/run_manifest_batch.py`
  - `Makefile`
- [x] Full UBFC manifest rerun completed with `bpm_row + multi_snr + qg4` (`42/42` successful):
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_qg4.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_qg4_method_means.csv`
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_qg4_runs.csv`

## Nested Retuning Pass

Status: `[x]`

- [x] Added constrained nested tuning workflow script:
  - `scripts/nested_tune_methods.py`
- [x] Produced nested inner/outer artifacts:
  - `outputs/data/aggregate/nested_tuning_qg4_fast/nested_inner_results.csv`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/nested_outer_results.csv`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/nested_outer_summary_method_means.csv`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/nested_best_params.json`
- [x] Applied nested-selected per-method params on full UBFC:
  - `outputs/data/aggregate/nested_tuning_qg4_fast/full_apply_method_means.csv`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/full_apply_method_means.tex`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/full_apply_method_means.pdf`
  - `outputs/data/aggregate/nested_tuning_qg4_fast/full_apply_method_means.png`
- [x] Outcome summary (vs qg4 baseline):
  - CHROM improved on MAE/RMSE/failure, POS improved on RMSE/correlation, SSR slight mixed gains, GREEN degraded noticeably.
  - Canonical paper table remains the qg4 baseline for balanced overall performance.

## SSR Redesign Pass

Status: `[x]`

- [x] Redesigned SSR implementation in `rppg_methods/ssr.py` with subspace-continuity alignment and stabilized rotation extraction.
- [x] Full UBFC SSR benchmark completed (`42/42` successful):
  - `outputs/data/aggregate/ubfc_ssr_redesign_qg4.csv`
  - `outputs/data/aggregate/ubfc_ssr_redesign_qg4_method_means.csv`
  - `outputs/data/aggregate/ubfc_ssr_redesign_qg4_runs.csv`
- [x] Promoted redesigned SSR into canonical paper table (other methods from qg4 baseline):
  - `outputs/data/aggregate/ubfc_full_active_methods_bpmrow_multi_qg4_ssr6_method_means.csv`
  - `outputs/data/aggregate/ubfc_full_active_method_means.tex`
  - `outputs/data/aggregate/ubfc_full_active_method_means.pdf`
  - `outputs/data/aggregate/ubfc_full_active_method_means.png`

## Scope Alignment

Status: `[x]`

- [x] Repository scope updated to UBFC-rPPG Dataset 2 only.
- [x] Removed references to unavailable corpora from paper/docs/configs.
- [x] Updated wording for publication-safe, reproducible-method framing.
