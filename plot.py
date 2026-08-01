#!/usr/bin/env python3
"""Australian Consumer Confidence: render all charts.

Reads cleaned/consumer_confidence_data.csv (written by load_data.py),
builds the derived scatter joins, and renders every chart into plots/.

Usage: python3 load_data.py && python3 plot.py
Requires: pip install -r requirements.txt
"""

from datetime import date
from pathlib import Path
from typing import Optional

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parent
CLEANED_DIR = REPO_ROOT / "cleaned"
PLOTS_DIR = REPO_ROOT / "plots"

COLORS = {
    "anz_roy_morgan_consumer_confidence": "#3d5a80",
    "westpac_mi_consumer_sentiment": "#e07a5f",
    "rba_cash_rate_target": "#2b7a78",
    "abs_cpi_index_australia": "#3d5a80",
    "abs_cpi_pct_change_australia": "#d1495b",
}

SERIES_LABELS = {
    "anz_roy_morgan_consumer_confidence": "ANZ-Roy Morgan Consumer Confidence",
    "westpac_mi_consumer_sentiment": "Westpac-MI Consumer Sentiment",
    "rba_cash_rate_target": "RBA Cash Rate Target",
}

RECESSIONS = [
    ("1974-09-01", "1975-06-01"),
    ("1982-06-01", "1983-06-01"),
    ("1990-09-01", "1991-09-01"),
    ("2020-03-01", "2020-09-01"),
]


# ---------------------------------------------------------------------------
# Derived data for plotting: date-matched scatter joins. Kept in one place
# so every chart that needs them uses the same join logic.
# ---------------------------------------------------------------------------


def build_scatter_confidence_vs_cashrate(combined: pd.DataFrame) -> pd.DataFrame:
    """As-of join: each confidence reading matched to the most recent cash
    rate observation on or before that date (cash rate is daily, confidence
    is monthly)."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date")
    cash_rate = combined[combined["series"] == "rba_cash_rate_target"][["date", "value"]].sort_values(
        "date"
    )

    merged = pd.merge_asof(
        confidence, cash_rate, on="date", direction="backward", suffixes=("_confidence", "_cashrate")
    ).dropna()

    return pd.DataFrame(
        {"confidence": merged["value_confidence"], "cash_rate": merged["value_cashrate"]}
    )


def build_scatter_confidence_vs_cpi(combined: pd.DataFrame) -> pd.DataFrame:
    """Matches each confidence reading to the CPI quarterly % change for
    the same quarter."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].copy()
    cpi_pct = combined[combined["series"] == "abs_cpi_pct_change_australia"][["date", "value"]].copy()

    confidence["quarter"] = confidence["date"].dt.to_period("Q")
    cpi_pct["quarter"] = cpi_pct["date"].dt.to_period("Q")

    merged = confidence.merge(cpi_pct, on="quarter", suffixes=("_confidence", "_cpi"))

    return pd.DataFrame(
        {"confidence": merged["value_confidence"], "cpi_pct_change": merged["value_cpi"]}
    )


def build_scatter_confidence_vs_unemployment(combined: pd.DataFrame) -> pd.DataFrame:
    """Matches each confidence reading to the unemployment rate for the
    same month (both series are monthly)."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].copy()
    unemployment = combined[combined["series"] == "abs_unemployment_rate_australia"][
        ["date", "value"]
    ].copy()

    confidence["month"] = confidence["date"].dt.to_period("M")
    unemployment["month"] = unemployment["date"].dt.to_period("M")

    merged = confidence.merge(unemployment, on="month", suffixes=("_confidence", "_unemployment"))

    return pd.DataFrame(
        {
            "confidence": merged["value_confidence"],
            "unemployment_rate": merged["value_unemployment"],
        }
    )


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def series_xy(combined: pd.DataFrame, series: str, since: Optional[pd.Timestamp] = None):
    sub = combined[combined["series"] == series].sort_values("date")
    if since is not None:
        sub = sub[sub["date"] >= since]
    return sub["date"], sub["value"]


def save(fig, name: str):
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=150)
    fig.savefig(PLOTS_DIR / f"{name}.svg")
    plt.close(fig)


def plot_confidence_indices(combined: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))
    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series)
        ax.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series])
    ax.set_title("Australian Consumer Confidence Indices", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Index")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    save(fig, "confidence_indices")


def plot_cpi_index(combined: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    dates, vals = series_xy(combined, "abs_cpi_index_australia")
    ax.plot(dates, vals, color=COLORS["abs_cpi_index_australia"], linewidth=1.3)
    ax.set_title("ABS CPI Index (All Groups, Australia)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Index")
    ax.grid(True, alpha=0.3)
    save(fig, "cpi_index")


def plot_cpi_pct_change(combined: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    dates, vals = series_xy(combined, "abs_cpi_pct_change_australia")
    ax.plot(dates, vals, color=COLORS["abs_cpi_pct_change_australia"], linewidth=1.3)
    ax.set_title("ABS CPI Quarterly % Change (Inflation Rate)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("% change")
    ax.grid(True, alpha=0.3)
    save(fig, "cpi_pct_change")


def plot_cash_rate(combined: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    dates, vals = series_xy(combined, "rba_cash_rate_target")
    ax.plot(dates, vals, color=COLORS["rba_cash_rate_target"], linewidth=1.8, drawstyle="steps-post")
    ax.set_title("RBA Cash Rate Target", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cash rate (%)")
    ax.grid(True, alpha=0.3)
    save(fig, "rba_cash_rate")


def plot_scatter_confidence_vs_cashrate(scatter: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(scatter["cash_rate"], scatter["confidence"], color="#3d5a80", s=16, alpha=0.8)
    ax.set_title("Consumer Confidence vs RBA Cash Rate (2011-2026)", fontsize=14)
    ax.set_xlabel("Cash Rate Target (%)")
    ax.set_ylabel("ANZ-Roy Morgan Consumer Confidence")
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_confidence_vs_cashrate")


def plot_scatter_confidence_vs_cpi(scatter: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(scatter["cpi_pct_change"], scatter["confidence"], color="#d1495b", s=12, alpha=0.7)
    ax.set_title("Consumer Confidence vs Quarterly CPI Inflation (1973-2026)", fontsize=14)
    ax.set_xlabel("CPI % Change (Quarter)")
    ax.set_ylabel("ANZ-Roy Morgan Consumer Confidence")
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_confidence_vs_cpi")


def plot_scatter_confidence_vs_unemployment(scatter: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(scatter["unemployment_rate"], scatter["confidence"], color="#588157", s=12, alpha=0.7)
    ax.set_title("Consumer Confidence vs Unemployment Rate (1978-2026)", fontsize=14)
    ax.set_xlabel("Unemployment Rate (%, Seasonally Adjusted)")
    ax.set_ylabel("ANZ-Roy Morgan Consumer Confidence")
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_confidence_vs_unemployment")


def plot_confidence_with_recessions(combined: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))

    for start, end in RECESSIONS:
        ax.axvspan(date.fromisoformat(start), date.fromisoformat(end), color="#888888", alpha=0.25, zorder=0)

    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series)
        ax.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series])

    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(color="#888888", alpha=0.25))
    labels.append("Recession periods")
    ax.legend(handles, labels, loc="upper right", fontsize=9)

    ax.set_title("Australian Consumer Confidence with Recession Periods Shaded", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Confidence Index")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)
    save(fig, "confidence_with_recessions")


def plot_confidence_and_cashrate_dual_axis(combined: pd.DataFrame):
    cutoff = pd.Timestamp("2011-01-01")

    fig, ax1 = plt.subplots(figsize=(13, 7))

    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series, since=cutoff)
        ax1.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series])
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Confidence Index")
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    cr_dates, cr_vals = series_xy(combined, "rba_cash_rate_target", since=cutoff)
    ax2.plot(
        cr_dates, cr_vals, color=COLORS["rba_cash_rate_target"], linewidth=1.8,
        label=SERIES_LABELS["rba_cash_rate_target"], drawstyle="steps-post",
    )
    ax2.set_ylabel("Cash Rate Target (%)", color=COLORS["rba_cash_rate_target"])
    ax2.tick_params(axis="y", labelcolor=COLORS["rba_cash_rate_target"])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    ax1.set_title("Consumer Confidence vs RBA Cash Rate (2011-2026)", fontsize=14)
    save(fig, "confidence_and_cashrate_dual_axis")


def main():
    in_path = CLEANED_DIR / "consumer_confidence_data.csv"
    if not in_path.exists():
        raise SystemExit(f"{in_path} not found — run `python3 load_data.py` first.")

    PLOTS_DIR.mkdir(exist_ok=True)
    combined = pd.read_csv(in_path, parse_dates=["date"])

    scatter_cashrate = build_scatter_confidence_vs_cashrate(combined)
    scatter_cpi = build_scatter_confidence_vs_cpi(combined)
    scatter_unemployment = build_scatter_confidence_vs_unemployment(combined)

    plot_confidence_indices(combined)
    plot_cpi_index(combined)
    plot_cpi_pct_change(combined)
    plot_cash_rate(combined)
    plot_scatter_confidence_vs_cashrate(scatter_cashrate)
    plot_scatter_confidence_vs_cpi(scatter_cpi)
    plot_scatter_confidence_vs_unemployment(scatter_unemployment)
    plot_confidence_with_recessions(combined)
    plot_confidence_and_cashrate_dual_axis(combined)

    print(f"wrote 9 charts to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
