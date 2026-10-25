"""Epic 3 - Construction planning and valuation: budget, timeline (Gantt), asset value.

NOTE: quantity norms and rates in data/material_rates.csv are rough, editable
rule-of-thumb figures for learning purposes. Replace them with local rates.
"""
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

QUALITY_MULTIPLIER = {"Economy": 0.85, "Standard": 1.00, "Premium": 1.30}

# (phase, share of total duration)
PHASES = [
    ("Site preparation & excavation", 0.08),
    ("Foundation", 0.14),
    ("Structure (columns, beams, slabs)", 0.30),
    ("Masonry & plastering", 0.18),
    ("Electrical & plumbing", 0.12),
    ("Flooring, painting & fixtures", 0.14),
    ("Final inspection & handover", 0.04),
]


def load_rates(path: str = "data/material_rates.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"item", "category", "unit", "qty_per_sqft", "rate_inr"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Rates file is missing columns: {sorted(missing)}")
    return df


def estimate_budget(rates: pd.DataFrame, built_up_area_sqft: float, floors: int = 1,
                    quality: str = "Standard", contingency_pct: float = 10.0):
    """Return (line_items_dataframe, summary_dict)."""
    if built_up_area_sqft <= 0 or floors <= 0:
        raise ValueError("Area and floors must be positive")
    total_area = built_up_area_sqft * floors
    mult = QUALITY_MULTIPLIER.get(quality, 1.0)

    df = rates.copy()
    df["quantity"] = (df["qty_per_sqft"] * total_area).round(1)
    df["adj_rate_inr"] = (df["rate_inr"] * mult).round(2)
    df["cost_inr"] = (df["quantity"] * df["adj_rate_inr"]).round(0)

    subtotal = float(df["cost_inr"].sum())
    contingency = subtotal * contingency_pct / 100
    summary = {
        "total_area_sqft": total_area,
        "subtotal": subtotal,
        "contingency": contingency,
        "grand_total": subtotal + contingency,
        "cost_per_sqft": (subtotal + contingency) / total_area,
        "by_category": df.groupby("category")["cost_inr"].sum().sort_values(ascending=False).to_dict(),
    }
    return df, summary


def estimate_duration_days(built_up_area_sqft: float, floors: int = 1) -> int:
    """Very rough duration: ~120 days base + 0.08 day per sqft, +25% per extra floor."""
    base = 120 + 0.08 * built_up_area_sqft
    return int(round(base * (1 + 0.25 * (floors - 1))))


def build_timeline(start: date, built_up_area_sqft: float, floors: int = 1) -> pd.DataFrame:
    total_days = estimate_duration_days(built_up_area_sqft, floors)
    rows, cursor = [], start
    for name, share in PHASES:
        days = max(1, round(total_days * share))
        end = cursor + timedelta(days=days)
        rows.append({"phase": name, "start": cursor, "end": end, "days": days})
        cursor = end
    return pd.DataFrame(rows)


def plot_gantt(timeline: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 4))
    for _, row in timeline.iterrows():
        ax.barh(row["phase"], (row["end"] - row["start"]).days, left=mdates.date2num(row["start"]))
    ax.xaxis_date()
    ax.invert_yaxis()
    ax.set_xlabel("Date")
    ax.set_title("Construction Timeline")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def asset_value(construction_cost: float, age_years: float, useful_life_years: float = 60,
                salvage_pct: float = 10.0) -> dict:
    """Straight-line depreciation of the building (land value excluded)."""
    if useful_life_years <= 0:
        raise ValueError("Useful life must be positive")
    salvage = construction_cost * salvage_pct / 100
    yearly_dep = (construction_cost - salvage) / useful_life_years
    depreciation = min(yearly_dep * age_years, construction_cost - salvage)
    return {
        "current_value": construction_cost - depreciation,
        "total_depreciation": depreciation,
        "yearly_depreciation": yearly_dep,
        "salvage_value": salvage,
    }


def inr(x: float) -> str:
    """Format a number as Indian Rupees with lakh/crore-style grouping (e.g. ₹12,34,567)."""
    s = f"{abs(round(x)):d}"
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if x < 0 else "") + "₹" + s
