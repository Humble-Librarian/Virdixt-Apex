"""
Native Standalone Acoustic Prosody & Vocal Stress DSP Engine
Pure Python + NumPy + SciPy implementation of vocal biomarker extraction.
Extracts fundamental frequency (F0), cycle-to-cycle vocal jitter, amplitude shimmer,
harmonics-to-noise ratio (HNR), and Composite Multimodal Deception Index (CMDI).
"""

import io
import math
from pathlib import Path
from typing import Union, Tuple, Optional
import numpy as np
from scipy import signal
from scipy.io import wavfile

from apex.config import CONFIG
from apex.core.types import AcousticBiomarkerVector


class AcousticMetrics:
    def __init__(
        self,
        f0_mean: float,
        f0_std: float,
        jitter_local: float,
        z_jitter: float,
        shimmer_local_db: float,
        z_shimmer: float,
        hnr_db: float,
        stress_score: float,
        stress_level: str,
    ):
        self.f0_mean = f0_mean
        self.f0_std = f0_std
        self.jitter_local = jitter_local  # Proportion (e.g. 0.02 = 2.0%)
        self.z_jitter = z_jitter
        self.shimmer_local_db = shimmer_local_db
        self.z_shimmer = z_shimmer
        self.hnr_db = hnr_db
        self.stress_score = stress_score  # 0 to 100
        self.cmdi_score = round(stress_score / 10.0, 2)  # 0 to 10
        self.stress_level = stress_level


class NativeAcousticStressExtractor:
    """
    Air-gapped DSP audio analyzer for unscripted executive earnings call Q&A speech.
    Uses Normalized Cross-Correlation (NCCF) pitch tracking and perturbation analysis.
    """

    def __init__(
        self,
        f0_min: float = 75.0,
        f0_max: float = 400.0,
        frame_length_ms: float = 30.0,
        hop_length_ms: float = 10.0,
    ):
        self.f0_min = f0_min
        self.f0_max = f0_max
        self.frame_length_ms = frame_length_ms
        self.hop_length_ms = hop_length_ms

        # Baseline clinical norms for adult speech (Pravitha et al., Titze 1994)
        self.norm_jitter_mean = 0.008  # 0.8%
        self.norm_jitter_std = 0.004   # 0.4%
        self.norm_shimmer_mean = 0.35  # 0.35 dB
        self.norm_shimmer_std = 0.20   # 0.20 dB

    def load_audio(
        self,
        audio_input: Union[str, Path, bytes, np.ndarray],
        target_sr: int = 16000,
    ) -> Tuple[np.ndarray, int]:
        """Loads and normalizes audio into a mono float32 array."""
        if isinstance(audio_input, (str, Path)):
            p = Path(audio_input)
            if not p.exists():
                raise FileNotFoundError(f"Audio file not found: {p}")
            sr, data = wavfile.read(str(p))
        elif isinstance(audio_input, bytes):
            sr, data = wavfile.read(io.BytesIO(audio_input))
        elif isinstance(audio_input, np.ndarray):
            sr = target_sr
            data = audio_input
        else:
            raise ValueError(f"Unsupported audio input type: {type(audio_input)}")

        # Convert to float32 mono
        if data.ndim > 1:
            data = data.mean(axis=1)

        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0
        elif data.dtype != np.float32:
            data = data.astype(np.float32)

        # Remove DC offset
        data = data - np.mean(data)

        # Peak normalize
        max_val = np.max(np.abs(data))
        if max_val > 1e-6:
            data = data / max_val

        # Resample if needed
        if sr != target_sr and len(data) > 0:
            num_samples = int(len(data) * target_sr / sr)
            data = signal.resample(data, num_samples).astype(np.float32)
            sr = target_sr

        return data, sr

    def extract(
        self,
        audio_input: Union[str, Path, bytes, np.ndarray],
        sr: int = 16000,
    ) -> AcousticMetrics:
        """
        Runs complete DSP feature extraction:
        1. NCCF Pitch Tracking -> F0 sequence and periods
        2. Cycle-to-cycle period perturbation -> Jitter %
        3. Peak amplitude perturbation -> Shimmer dB
        4. Harmonics-to-Noise Ratio -> HNR dB
        5. Composite Multimodal Deception Index (CMDI)
        """
        data, sample_rate = self.load_audio(audio_input, target_sr=sr)

        if len(data) < int(sample_rate * 0.1):  # Less than 100ms
            return self._default_metrics()

        frame_len = int(sample_rate * (self.frame_length_ms / 1000.0))
        hop_len = int(sample_rate * (self.hop_length_ms / 1000.0))

        lag_min = max(2, int(sample_rate / self.f0_max))
        lag_max = min(frame_len - 1, int(sample_rate / self.f0_min))

        f0_list = []
        amp_list = []
        hnr_list = []

        num_frames = max(1, (len(data) - frame_len) // hop_len)

        for i in range(num_frames):
            start = i * hop_len
            frame = data[start : start + frame_len]

            # RMS energy gate (ignore silent pauses)
            rms = np.sqrt(np.mean(frame**2))
            if rms < 0.02:
                continue

            # Normalized Autocorrelation
            corr = np.correlate(frame, frame, mode="full")
            corr = corr[len(frame) - 1 :]
            norm_factor = corr[0] if corr[0] > 1e-7 else 1.0
            norm_corr = corr / norm_factor

            # Search in valid pitch lag window
            search_window = norm_corr[lag_min : lag_max + 1]
            if len(search_window) == 0:
                continue

            peak_idx = int(np.argmax(search_window))
            peak_lag = lag_min + peak_idx
            peak_val = float(search_window[peak_idx])

            # Voiced frame threshold
            if peak_val > 0.35:
                pitch_hz = sample_rate / peak_lag
                f0_list.append(pitch_hz)
                amp_list.append(float(np.max(np.abs(frame))))

                # Local HNR
                clamped_r = min(0.999, max(0.01, peak_val))
                hnr_val = 10.0 * math.log10(clamped_r / (1.0 - clamped_r))
                hnr_list.append(hnr_val)

        if len(f0_list) < 3:
            return self._default_metrics()

        f0_arr = np.array(f0_list, dtype=np.float32)
        amp_arr = np.array(amp_list, dtype=np.float32)

        f0_mean = float(np.mean(f0_arr))
        f0_std = float(np.std(f0_arr))

        # 1. Vocal Jitter (Period Perturbation)
        periods = 1.0 / f0_arr
        period_diffs = np.abs(np.diff(periods))
        mean_period = np.mean(periods)
        local_jitter = float(np.mean(period_diffs) / mean_period) if mean_period > 0 else 0.005

        z_jitter = float((local_jitter - self.norm_jitter_mean) / self.norm_jitter_std)

        # 2. Vocal Shimmer (Amplitude Perturbation)
        amp_diffs = np.abs(np.diff(amp_arr))
        # Shimmer in dB: 20 * log10(A_i+1 / A_i)
        ratio = amp_arr[1:] / np.maximum(amp_arr[:-1], 1e-6)
        ratio_clamped = np.clip(ratio, 1e-4, 1e4)
        shimmer_db = float(np.mean(np.abs(20.0 * np.log10(ratio_clamped))))
        z_shimmer = float((shimmer_db - self.norm_shimmer_mean) / self.norm_shimmer_std)

        # 3. Harmonics to Noise Ratio
        avg_hnr = float(np.mean(hnr_list)) if hnr_list else 15.0

        # 4. Composite Multimodal Deception Index (CMDI: 0.0 to 10.0)
        # Combines z_jitter, z_shimmer, and pitch instability
        jitter_component = max(0.0, z_jitter) * 1.5
        shimmer_component = max(0.0, z_shimmer) * 1.2
        pitch_instability = min(3.0, (f0_std / max(20.0, f0_mean)) * 10.0)

        raw_cmdi = (jitter_component + shimmer_component + pitch_instability) / 1.5
        cmdi_score = round(min(10.0, max(0.0, raw_cmdi)), 2)
        stress_score = round(cmdi_score * 10.0, 1)

        if cmdi_score >= 6.5:
            stress_level = "PANIC_ANOMALY"
        elif cmdi_score >= 4.0:
            stress_level = "ELEVATED"
        else:
            stress_level = "CALM"

        return AcousticMetrics(
            f0_mean=round(f0_mean, 1),
            f0_std=round(f0_std, 2),
            jitter_local=round(local_jitter, 5),
            z_jitter=round(z_jitter, 2),
            shimmer_local_db=round(shimmer_db, 2),
            z_shimmer=round(z_shimmer, 2),
            hnr_db=round(avg_hnr, 1),
            stress_score=stress_score,
            stress_level=stress_level,
        )

    def extract_vector(
        self,
        audio_input: Union[str, Path, bytes, np.ndarray],
        sr: int = 16000,
    ) -> AcousticBiomarkerVector:
        """Convenience method returning a typed AcousticBiomarkerVector."""
        m = self.extract(audio_input, sr=sr)
        acute = (
            m.z_jitter > CONFIG.thresholds.jitter_sigma_stress_threshold
            or m.stress_score > 70.0
        )
        return AcousticBiomarkerVector(
            f0_mean_hz=m.f0_mean,
            f0_std_hz=m.f0_std,
            jitter_local_percent=round(m.jitter_local * 100.0, 3),
            jitter_z_score=m.z_jitter,
            shimmer_local_db=m.shimmer_local_db,
            shimmer_z_score=m.z_shimmer,
            hnr_db=m.hnr_db,
            cmdi_score=round(m.stress_score / 10.0, 2),
            vocal_stress_rating=m.stress_level,
            acute_stress_flag=acute,
        )

    @staticmethod
    def _default_metrics() -> AcousticMetrics:
        return AcousticMetrics(
            f0_mean=140.0,
            f0_std=12.0,
            jitter_local=0.008,
            z_jitter=0.0,
            shimmer_local_db=0.35,
            z_shimmer=0.0,
            hnr_db=18.0,
            stress_score=15.0,
            stress_level="CALM",
        )
