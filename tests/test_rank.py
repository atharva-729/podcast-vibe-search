import numpy as np
import pandas as pd
import pytest

from vibe import query, rank
from vibe.features import FEATURES, percentile


def _df(pcts, shows=None, starts=None):
    n = len(pcts)
    df = pd.DataFrame({f + "_pct": [p.get(f + "_pct", 0.5) for p in pcts] for f in FEATURES})
    df["show_id"] = shows or [f"s{i}" for i in range(n)]
    df["episode_id"] = [s + "_ep" for s in df.show_id]
    df["start_s"] = starts or [0.0] * n
    return df


def test_minmax():
    assert rank.minmax(np.array([1.0, 3.0, 2.0])).tolist() == [0.0, 1.0, 0.5]
    assert rank.minmax(np.array([2.0, 2.0])).tolist() == [0.0, 0.0]


def test_feature_fit_targets_and_avoid():
    df = _df([{"energy_pct": 0.2}, {"energy_pct": 0.8}])
    assert rank.feature_fit(df, {"energy": "low"}).tolist() == pytest.approx([1.0, 0.4])
    # avoiding high energy rewards distance from 0.8
    assert rank.feature_fit(df, {}, ["energy:high"]).tolist() == pytest.approx([0.6, 0.0])
    assert rank.feature_fit(df, {}).tolist() == [0.0, 0.0]


def test_select_caps_per_show_and_merges_neighbours():
    df = _df([{}] * 5, shows=["a", "a", "a", "b", "a"], starts=[0.0, 20.0, 100.0, 0.0, 200.0])
    score = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
    picked = rank.select(df, score, k=5, max_per_show=2)
    # 1 is adjacent to 0 (merged away); show "a" capped at 2 (0 and 2); then "b"
    assert picked == [0, 2, 3]


def test_describe_matched_targets_in_words():
    row = _df([{"laughter_score_pct": 0.9, "energy_pct": 0.85, "pace_wpm_pct": 0.1}]).iloc[0]
    why = rank.describe(row, {"laughter_score": "high", "energy": "high", "pace_wpm": "high"})
    assert why == ["high energy", "lots of laughter"]  # closest fit first; pace (0.1 vs high) not claimed
    assert "topic: football" in rank.describe(row, {}, topic_n=0.9, topic="football")


def test_query_validate_drops_invented_fields():
    p = query.validate({"vibe_text": "rain", "targets": {"energy": "low", "voice": "none", "pace_wpm": "slow"},
                        "topic": "", "avoid": ["music_score:high", "voice:present"]})
    assert p == {"vibe_text": "rain", "targets": {"energy": "low"}, "topic": None, "avoid": ["music_score:high"]}
    with pytest.raises(ValueError):
        query.validate({"targets": {}})


def test_keyword_fallback():
    assert query.fallback("calm and slow")["targets"] == {"energy": "low", "pace_wpm": "low"}


def test_percentile_is_rank_based():
    assert percentile(pd.Series([10, 30, 20, np.nan])).tolist() == pytest.approx([1 / 3, 1.0, 2 / 3, 0.5])
