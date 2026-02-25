# rPPG Pulse Estimation Method Comparison

This project compares three remote photoplethysmography (rPPG) methods for pulse estimation from webcam video:

- Green channel method
- CHROM (chrominance-based method)
- JBSS-inspired ICA method

The implementation goal is educational and research-focused: keep the core methods manually implemented (no specialized rPPG library abstractions) so each step is explainable in a paper.

## Project Goal

Build a clear, reproducible comparison study that:

- explains how each method works mathematically and algorithmically,
- references the original researchers/papers,
- evaluates behavior under the same capture conditions,
- produces publication-ready figures and tables.

## References

- Verkruysse, W., Svaasand, L. O., & Nelson, J. S. (2008). *Remote plethysmographic imaging using ambient light*. Optics Express, 16(26), 21434-21445.
- de Haan, G., & Jeanne, V. (2013). *Robust pulse rate from chrominance-based rPPG*. IEEE Transactions on Biomedical Engineering, 60(10), 2878-2886.
- Bousefsaf, F., Maaoui, C., & Pruski, A. (2013). *Continuous wavelet filtering on webcam photoplethysmographic signals to remotely assess the instantaneous heart rate*. Biomedical Signal Processing and Control, 8(6), 568-574. (context for signal processing choices)

Note: The current JBSS file is a simplified ICA-based educational approximation and should be clearly labeled as such in the paper.

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
make venv
make install
```

2. Run the app:

```bash
make run
```

## Virtual Environment Management

- `make venv`: create `.venv` using Python venv
- `make install`: install dependencies from `requirements.txt`
- `make run`: start the app
- `make test`: run unit tests
- `make evaluate VIDEO=/abs/path/video.mp4 SCENARIO=still METHODS=all [GT=/abs/path/gt.csv] [RUN_ID=my_run]`: run offline evaluation
- `make plots RUN_DIR=outputs/data/<run_id>`: generate paper figures from one evaluation run
- `make freeze`: regenerate `requirements.txt` from current `.venv`
- `make clean-venv`: remove `.venv`

## Current Structure

```text
main.py
rppg_methods/
utils/
configs/
docs/
scripts/
tests/
```

## Reproducible Paper Workflow

1. Record videos for protocol scenarios defined in `configs/experiment_protocol.json`.
2. Optional: collect ground-truth BPM in CSV format with columns `time_s,bpm`.
3. Run evaluator:

```bash
make evaluate VIDEO=/absolute/path/scenario_still.mp4 SCENARIO=still METHODS=all GT=/absolute/path/still_gt.csv RUN_ID=still_run_01
```

4. Generate figures:

```bash
make plots RUN_DIR=outputs/data/still_run_01
```

5. Use generated artifacts in:
- `outputs/data/<run_id>/summary.csv`
- `outputs/plots/<run_id>/`

## Documentation Index

- Methods and equations: `docs/methods.md`
- Experimental protocol: `docs/experimental_protocol.md`
- Ongoing implementation tracker: `docs/improvement_tracker.md`
