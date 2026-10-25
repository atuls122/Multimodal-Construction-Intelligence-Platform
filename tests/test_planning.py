"""Run with:  python -m pytest -q   (or just: python tests/test_planning.py)"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import planning_valuation as pv  # noqa: E402


def test_budget_scales_with_area_and_quality():
    rates = pv.load_rates(os.path.join(os.path.dirname(__file__), "..", "data", "material_rates.csv"))
    _, small = pv.estimate_budget(rates, 1000, 1, "Standard", 10)
    _, big = pv.estimate_budget(rates, 2000, 1, "Standard", 10)
    _, premium = pv.estimate_budget(rates, 1000, 1, "Premium", 10)
    assert big["grand_total"] > small["grand_total"]
    assert premium["grand_total"] > small["grand_total"]
    assert abs(small["grand_total"] - small["subtotal"] * 1.10) < 1


def test_timeline_is_continuous():
    t = pv.build_timeline(date(2026, 1, 1), 1000, 2)
    assert list(t["start"][1:]) == list(t["end"][:-1])


def test_asset_value_never_below_salvage():
    av = pv.asset_value(1_000_000, age_years=500, useful_life_years=60, salvage_pct=10)
    assert round(av["current_value"]) == 100_000


def test_inr_format():
    assert pv.inr(1234567) == "₹12,34,567"
    assert pv.inr(999) == "₹999"


if __name__ == "__main__":
    test_budget_scales_with_area_and_quality()
    test_timeline_is_continuous()
    test_asset_value_never_below_salvage()
    test_inr_format()
    print("All tests passed")
