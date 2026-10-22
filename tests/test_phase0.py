import pytest

from vibe import llm
from vibe.audio import segment_bounds
from vibe.feeds import pick_shows


def test_segment_bounds_overlap():
    b = segment_bounds(900, 20, 10)
    assert b[0] == (0.0, 20.0) and b[1] == (10.0, 30.0)
    assert b[-1] == (880.0, 900.0)
    assert len(b) == 89


def test_segment_bounds_drops_short_tail_and_tiny_input():
    assert segment_bounds(35, 20, 10) == [(0.0, 20.0), (10.0, 30.0)]
    assert segment_bounds(15, 20, 10) == []


def test_cost_usd():
    usage = {"prompt_tokens": 1000, "completion_tokens": 100, "prompt_tokens_details": {"cached_tokens": 400}}
    prices = {"input": 0.25, "cached_input": 0.025, "output": 2.0}
    assert llm.cost_usd(usage, prices) == pytest.approx((600 * 0.25 + 400 * 0.025 + 100 * 2.0) / 1e6)


def test_spend_guard_blocks_over_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "_spend_file", lambda: tmp_path / "spend.json")
    monkeypatch.setattr(llm.cache, "get", lambda *a: None)
    llm.record_spend(0.81)
    with pytest.raises(llm.BudgetExceeded):
        llm.chat([{"role": "user", "content": "hi"}])


def _feed(show_id, vibe, spare=False, n_files=3):
    return {"show_id": show_id, "vibe": vibe, "spare": spare,
            "episodes": [{"file": f"{show_id}{i}.mp3"} for i in range(n_files)]}


def test_spares_fill_only_missing_slots():
    feeds = [_feed("a", "x"), _feed("b", "x"), _feed("c", "x"), _feed("d", "x", n_files=1),
             _feed("s1", "x", spare=True), _feed("s2", "x", spare=True),
             _feed("e", "y"), _feed("s3", "y", spare=True)]
    picked = [f["show_id"] for f in pick_shows(feeds)]
    assert picked == ["a", "b", "c", "s1", "e", "s3"]
