"""Base classes and common utilities for remote photoplethysmography methods.

All methods follow the same four-stage processing model:

1) ``signal_extraction``: derive one scalar value from the ROI frame
2) ``normalization``: remove slow trends / scale effects
3) ``filtering``: isolate the heart-rate band
4) ``hr_estimation``: estimate BPM from the dominant spectral peak
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from utils.bandpass_filter import bandpass_filter


class RPPGMethod:
    """Abstract base class for rPPG methods.

    Parameters
    ----------
    fs : float
        Sampling frequency (frame rate) of the video in Hertz.
    buffer_size : int
        Number of samples to retain for heart rate estimation. The
        buffer should be long enough to capture several cardiac
        cycles; a typical buffer corresponds to 8–12 seconds of
        video.
    """

    def __init__(self, fs: float = 30.0, buffer_size: int = 300) -> None:
        self.fs = fs
        self.buffer_size = buffer_size
        self.signal_buffer: list[float] = []
        self.times: list[float] = []
        self.last_hr: Optional[float] = None
        self.last_peak_freq_hz: Optional[float] = None

    def reset(self) -> None:
        """Clear the internal signal buffer and reset heart rate."""
        self.signal_buffer.clear()
        self.times.clear()
        self.last_hr = None
        self.last_peak_freq_hz = None

    def update(self, roi_frame: np.ndarray) -> None:
        """Process a new ROI frame and update the internal buffer.

        Subclasses must override this method to extract the per‑frame
        photoplethysmographic value (e.g. mean green intensity or a
        chrominance combination) from the ROI.

        Parameters
        ----------
        roi_frame : np.ndarray
            The cropped BGR image corresponding to the subject's
            forehead.
        """
        raise NotImplementedError

    def update_from_value(self, value: float) -> None:
        """Run the common pipeline for one extracted method value."""
        self._append_value(value)
        self.last_hr = self.estimate_hr_bpm()

    def _append_value(self, value: float) -> None:
        """Append a raw value to the signal buffer and trim if necessary."""
        self.signal_buffer.append(value)
        # Maintain buffer length
        if len(self.signal_buffer) > self.buffer_size:
            # Remove oldest values
            excess = len(self.signal_buffer) - self.buffer_size
            self.signal_buffer = self.signal_buffer[excess:]

    def normalize_signal(self, signal: np.ndarray) -> np.ndarray:
        """Normalization stage: remove DC component."""
        if signal.size == 0:
            return signal
        return signal - np.mean(signal)

    def filter_signal(self, normalized_signal: np.ndarray) -> np.ndarray:
        """Filtering stage: apply standard rPPG heart-rate band-pass."""
        return bandpass_filter(normalized_signal, fs=self.fs, low=0.75, high=4.0)

    def get_filtered_signal(self) -> np.ndarray:
        """Return the current normalized and filtered signal."""
        signal = np.array(self.signal_buffer, dtype=np.float64)
        if signal.size == 0:
            return signal
        normalized = self.normalize_signal(signal)
        return self.filter_signal(normalized)

    def compute_psd(self) -> tuple[np.ndarray, np.ndarray]:
        """Return one-sided FFT magnitude spectrum for the filtered signal."""
        filtered = self.get_filtered_signal()
        if filtered.size == 0:
            return np.array([], dtype=np.float64), np.array([], dtype=np.float64)
        n = len(filtered)
        freqs = np.fft.rfftfreq(n, d=1.0 / self.fs)
        fft_mag = np.abs(np.fft.rfft(filtered))
        return freqs, fft_mag

    def estimate_hr_bpm(self) -> Optional[float]:
        """Heart-rate estimation stage from dominant in-band FFT peak."""
        signal = np.array(self.signal_buffer, dtype=np.float64)
        if signal.size < int(self.fs * 4):
            return None
        freqs, fft_mag = self.compute_psd()
        if freqs.size == 0:
            return None
        mask = (freqs >= 0.75) & (freqs <= 4.0)
        if not np.any(mask):
            return None
        peak_freq = freqs[mask][np.argmax(fft_mag[mask])]
        self.last_peak_freq_hz = float(peak_freq)
        return float(peak_freq * 60.0)

    def get_hr(self) -> Optional[float]:
        """Return the most recent heart rate estimation.

        This method should be called after ``update`` has been
        invoked on successive frames. The result is cached to avoid
        recomputing the FFT on every frame.
        """
        return self.last_hr

    def get_ppg_signal(self) -> np.ndarray:
        """Return the current filtered PPG signal for plotting."""
        return self.get_filtered_signal()
