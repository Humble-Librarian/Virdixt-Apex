"""
Tests for Native Standalone Audio DSP Engine (apex/audio/prosody.py)
"""

import io
import numpy as np
import pytest
from scipy.io import wavfile
from fastapi.testclient import TestClient

from apex.audio.prosody import NativeAcousticStressExtractor
from apex.server import app


@pytest.fixture
def synthetic_calm_audio() -> bytes:
    """Generates 1.0s of clean, stable 130 Hz voice sine wave (low jitter)."""
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    f0 = 130.0
    audio = 0.5 * np.sin(2 * np.pi * f0 * t)
    # Convert to 16-bit PCM wav bytes
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sr, pcm)
    return buf.getvalue()


@pytest.fixture
def synthetic_stressed_audio() -> bytes:
    """Generates 1.0s of erratic voice with heavy frequency modulation (high jitter)."""
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    f0 = 150.0
    # Add heavy 15 Hz jitter modulation + amplitude modulation
    phase_jitter = 0.25 * np.sin(2 * np.pi * 15 * t)
    amp_modulation = 0.4 + 0.3 * np.sin(2 * np.pi * 8 * t)
    audio = amp_modulation * np.sin(2 * np.pi * f0 * t + phase_jitter)
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sr, pcm)
    return buf.getvalue()


def test_native_dsp_calm_speech(synthetic_calm_audio):
    extractor = NativeAcousticStressExtractor()
    metrics = extractor.extract(synthetic_calm_audio)

    assert 120.0 <= metrics.f0_mean <= 140.0
    assert metrics.stress_level in ("CALM", "ELEVATED")
    assert metrics.cmdi_score < 7.0


def test_native_dsp_stressed_speech(synthetic_stressed_audio):
    extractor = NativeAcousticStressExtractor()
    metrics = extractor.extract(synthetic_stressed_audio)

    # Modulated audio triggers elevated jitter and higher CMDI
    assert metrics.z_jitter > 0.0
    assert metrics.stress_score > 20.0


def test_upload_audio_endpoint(synthetic_stressed_audio):
    client = TestClient(app)
    response = client.post(
        "/api/upload-audio",
        files={"file": ("earnings_call_qa.wav", synthetic_stressed_audio, "audio/wav")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "vector" in data
    assert data["metrics"]["f0_mean_hz"] > 0
    assert "cmdi_score" in data["metrics"]
