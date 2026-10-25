"""Run with:  python tests/test_assistant.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import assistant  # noqa: E402


def day(rain=0, wind=10, tmax=30):
    return {"date": "2026-01-01", "rain_mm": rain, "wind_kmh": wind, "temp_max_c": tmax, "temp_min_c": 20}


def test_structural_crack_is_stop_and_first():
    out = assistant.advisory_rules(crack={"structural_concern": True, "severity": "High"},
                                   forecast=[day(rain=12)])
    assert out[0]["priority"] == "STOP"


def test_weather_rules():
    out = assistant.advisory_rules(forecast=[day(rain=15, wind=50, tmax=40)])
    msgs = " ".join(a["message"] for a in out)
    assert "concrete pouring" in msgs and "crane" in msgs and "hot" in msgs


def test_empty_gives_info():
    out = assistant.advisory_rules()
    assert len(out) == 1 and out[0]["priority"] == "INFO"


def test_low_contingency_flagged():
    out = assistant.advisory_rules(budget={"contingency_pct": 3})
    assert any("Contingency" in a["message"] for a in out)


if __name__ == "__main__":
    test_structural_crack_is_stop_and_first()
    test_weather_rules()
    test_empty_gives_info()
    test_low_contingency_flagged()
    print("All assistant tests passed")
