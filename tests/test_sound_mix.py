"""Unit tests for helpers/sound_mix.py (attack measurement and filter graph)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import sound_mix as sm  # noqa: E402


def test_attack_is_time_to_half_peak():
    # 100 samples of silence, then a ramp to 1000 over 100 samples, at 1000 Hz
    samples = [0] * 100 + [i * 10 for i in range(101)]

    attack = sm.attack_seconds(samples, 1000)

    assert abs(attack - 0.150) < 1e-9  # half peak (500) reached at index 150


def test_attack_of_silence_is_zero():
    assert sm.attack_seconds([0, 0, 0], 48000) == 0.0


def test_filter_graph_places_effect_after_attack_offset_and_ducks_music():
    music = {"path": "/m.mp3", "gain_db": -12, "fade_in_s": 1, "fade_out_s": 2}
    effects = [{"path": "/pop.wav", "start_s": 4.98, "gain_db": -6}]

    inputs, graph = sm.build_filter(30.0, music, effects)

    assert inputs[:4] == ["-stream_loop", "-1", "-i", "/m.mp3"] and inputs[-2:] == ["-i", "/pop.wav"]
    assert "adelay=4980|4980" in graph
    assert "sidechaincompress" in graph and "volume=-12.0dB" in graph
    assert "amix=inputs=3" in graph and "normalize=0" in graph


def test_filter_graph_without_music_still_mixes_effects():
    inputs, graph = sm.build_filter(10.0, None, [{"path": "/a.wav", "start_s": 0.0}])

    assert "sidechaincompress" not in graph
    assert "amix=inputs=2" in graph
    assert inputs == ["-i", "/a.wav"]


def test_filter_graph_voice_commentary_is_delayed_and_ducks_the_clip():
    inputs, graph = sm.build_filter(20.0, None, [], {"path": "/v/take1.mp3", "offset_s": 2.5, "gain_db": 1})

    assert inputs == ["-i", "/v/take1.mp3"]
    assert "volume=1.0dB,adelay=2500|2500,asplit=2[vo][vkey]" in graph
    assert "[sp0][vkey]sidechaincompress=" in graph and graph.endswith("[sp][vo]amix=inputs=2:duration=first:normalize=0[mix]")


def test_speech_filter_chain_orders_highpass_compress_gain_limit():
    f = sm.speech_filter({"highpass_hz": 70, "gain_db": 20, "compress": True})

    assert f.startswith("highpass=f=70,acompressor") and ",volume=20.0dB,alimiter" in f
    assert sm.speech_filter({}) == "alimiter=limit=0.891:attack=5:release=50"
