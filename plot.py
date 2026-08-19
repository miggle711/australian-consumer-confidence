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
RAW_DIR = REPO_ROOT / "raw"
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

# Discrete shocks identified in INSIGHTS.md as the actual drivers behind
# confidence's biggest moves, in contrast to the scheduled/level-based
# suspects (rate level, CPI level, unemployment level, elections, budgets)
# tested and ruled out elsewhere in the pipeline.
SHOCKS = [
    ("1990-11-01", "1990-91 recession\n(deepest reading in the series)", -55),
    ("2020-04-01", "COVID crash\n(116 -> 79.8 in two months)", -30),
    ("2022-09-01", "2022-23 hiking cycle +\ninflation shock", 55),
    ("2024-09-01", "Sustained low without a\ndeclared recession", 20),
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


def build_scatter_confidence_delta_vs_cashrate_delta(combined: pd.DataFrame) -> pd.DataFrame:
    """Month-over-month change in confidence vs month-over-month change in
    cash rate, rather than levels: tests whether confidence reacts to the
    pace/direction of rate moves rather than the rate itself."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date")
    cash_rate = combined[combined["series"] == "rba_cash_rate_target"][["date", "value"]].sort_values(
        "date"
    )

    merged = pd.merge_asof(
        confidence, cash_rate, on="date", direction="backward", suffixes=("_confidence", "_cashrate")
    ).dropna()

    merged["confidence_delta"] = merged["value_confidence"].diff()
    merged["cash_rate_delta"] = merged["value_cashrate"].diff()
    merged = merged.dropna(subset=["confidence_delta", "cash_rate_delta"])

    return pd.DataFrame(
        {
            "confidence_delta": merged["confidence_delta"],
            "cash_rate_delta": merged["cash_rate_delta"],
        }
    )


def build_rolling_correlation_confidence_vs_cashrate(combined: pd.DataFrame, window_months: int = 24) -> pd.DataFrame:
    """Monthly confidence/cash-rate pairs (as-of join), then a rolling
    Pearson correlation over a trailing window: shows whether the
    relationship strengthens in specific periods (e.g. hiking cycles)
    rather than assuming it's constant across the whole series. Also
    computes the trailing net cash rate change and trailing average CPI
    inflation over the same window, to test whether hiking/easing cycles
    or the inflation environment explain when the correlation flips sign."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date")
    cash_rate = combined[combined["series"] == "rba_cash_rate_target"][["date", "value"]].sort_values(
        "date"
    )
    cpi_pct = combined[combined["series"] == "abs_cpi_pct_change_australia"][["date", "value"]].sort_values(
        "date"
    )

    merged = pd.merge_asof(
        confidence, cash_rate, on="date", direction="backward", suffixes=("_confidence", "_cashrate")
    ).dropna()
    merged = pd.merge_asof(merged, cpi_pct, on="date", direction="backward").rename(
        columns={"value": "cpi_pct_change"}
    )

    merged["rolling_corr"] = (
        merged["value_confidence"].rolling(window_months).corr(merged["value_cashrate"])
    )
    merged["rate_trend"] = merged["value_cashrate"].diff(window_months)
    # cpi_pct_change is quarter-over-quarter; annualize (x4) to compare
    # against the RBA's 2-3% annual inflation target.
    merged["cpi_trailing_avg"] = merged["cpi_pct_change"].rolling(window_months).mean() * 4

    return merged[["date", "rolling_corr", "rate_trend", "cpi_trailing_avg"]].dropna()


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


def build_confidence_calendar_heatmap(combined: pd.DataFrame, since_year: int = 1990) -> pd.DataFrame:
    """Month-over-month change in Roy Morgan confidence, reshaped into a
    year x month grid: shows the shock months (COVID, 1990-91, 2022) as a
    block of colour a viewer can spot at a glance, which a single-line
    timeline can't do as viscerally. Cropped to since_year so the panel
    stays compact on a scrollable page while still covering all four shock
    episodes (1990-91, COVID, 2022 hiking, current low)."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date").copy()
    confidence["delta"] = confidence["value"].diff()
    confidence["year"] = confidence["date"].dt.year
    confidence["month"] = confidence["date"].dt.month
    confidence = confidence[confidence["year"] >= since_year]

    grid = confidence.pivot_table(index="year", columns="month", values="delta")
    return grid.sort_index(ascending=False)


def build_survey_agreement(combined: pd.DataFrame) -> pd.DataFrame:
    """Matches Roy Morgan and Westpac-MI confidence readings for the same
    month, over their overlapping window (2013-present): tests whether the
    two independently-run confidence surveys actually agree with each
    other, rather than assuming they measure the same thing."""
    roy_morgan = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].copy()
    westpac = combined[combined["series"] == "westpac_mi_consumer_sentiment"][["date", "value"]].copy()

    roy_morgan["month"] = roy_morgan["date"].dt.to_period("M")
    westpac["month"] = westpac["date"].dt.to_period("M")

    merged = roy_morgan.merge(westpac, on="month", suffixes=("_rm", "_wp"))

    return pd.DataFrame(
        {
            "date": merged["month"].dt.to_timestamp(),
            "roy_morgan": merged["value_rm"],
            "westpac": merged["value_wp"],
            "spread": merged["value_rm"] - merged["value_wp"],
        }
    )


def build_event_window_deltas(combined: pd.DataFrame, events: pd.DataFrame, window_months: int = 2) -> pd.DataFrame:
    """For each event date, compares mean confidence in the window_months
    before it to the window_months after it. Returns one row per event with
    the before/after means and the delta, so an average effect can be
    computed across many events instead of eyeballing a single noisy
    timeline for a pattern too small to see."""
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date")

    rows = []
    for _, event in events.iterrows():
        event_date = event["date"]
        before_start = event_date - pd.DateOffset(months=window_months)
        after_end = event_date + pd.DateOffset(months=window_months)

        before = confidence[(confidence["date"] >= before_start) & (confidence["date"] < event_date)]
        after = confidence[(confidence["date"] >= event_date) & (confidence["date"] <= after_end)]

        if before.empty or after.empty:
            continue

        before_mean = before["value"].mean()
        after_mean = after["value"].mean()
        rows.append(
            {
                "date": event_date,
                "label": event["label"],
                "before_mean": before_mean,
                "after_mean": after_mean,
                "delta": after_mean - before_mean,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def load_events(filename: str) -> pd.DataFrame:
    """Loads a hand-curated event-date CSV (date, label columns) from
    raw/, used for vertical markers rather than a plotted series. See
    raw/README.md for provenance."""
    return pd.read_csv(RAW_DIR / filename, parse_dates=["date"])


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


def plot_scatter_confidence_delta_vs_cashrate_delta(scatter: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(scatter["cash_rate_delta"], scatter["confidence_delta"], color="#8338ec", s=16, alpha=0.7)
    ax.axhline(0, color="#888888", linewidth=0.8)
    ax.axvline(0, color="#888888", linewidth=0.8)
    ax.set_title("Month-over-Month Change: Confidence vs Cash Rate (2011-2026)", fontsize=14)
    ax.set_xlabel("Cash Rate Change (percentage points)")
    ax.set_ylabel("Confidence Change (index points)")
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_confidence_delta_vs_cashrate_delta")


def plot_scatter_confidence_vs_unemployment(scatter: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(scatter["unemployment_rate"], scatter["confidence"], color="#588157", s=12, alpha=0.7)
    ax.set_title("Consumer Confidence vs Unemployment Rate (1978-2026)", fontsize=14)
    ax.set_xlabel("Unemployment Rate (%, Seasonally Adjusted)")
    ax.set_ylabel("ANZ-Roy Morgan Consumer Confidence")
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_confidence_vs_unemployment")


def plot_confidence_calendar_heatmap(grid: pd.DataFrame):
    """Year (row) x month (column) heatmap of month-over-month confidence
    change, diverging red (falling) to blue (rising) around zero. An
    alternative to the shock-annotation line chart: lets a viewer spot the
    shock months as a block of colour rather than reading it off a
    timeline."""
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, ax = plt.subplots(figsize=(10, max(6, 0.22 * len(grid))))
    vmax = grid.abs().max().max()
    im = ax.imshow(grid.values, cmap="RdBu", vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(12))
    ax.set_xticklabels(month_labels, fontsize=8)
    ax.set_yticks(range(len(grid)))
    ax.set_yticklabels(grid.index, fontsize=6)
    ax.set_title("Month-over-Month Confidence Change by Year\n(red = falling, blue = rising)", fontsize=13)

    cbar = fig.colorbar(im, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label("Change in confidence index (points)", fontsize=9)

    save(fig, "confidence_calendar_heatmap")


def plot_survey_agreement_scatter(agreement: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 9))

    lo = min(agreement["roy_morgan"].min(), agreement["westpac"].min()) - 2
    hi = max(agreement["roy_morgan"].max(), agreement["westpac"].max()) + 2
    ax.plot([lo, hi], [lo, hi], color="#888888", linewidth=1, linestyle="--", label="Perfect agreement (y = x)")

    ax.scatter(agreement["westpac"], agreement["roy_morgan"], color="#3d5a80", s=16, alpha=0.7)

    corr = agreement["roy_morgan"].corr(agreement["westpac"])
    ax.set_title(f"Roy Morgan vs Westpac-MI Confidence, Same Month (2013-2026)\nPearson correlation: {corr:.2f}", fontsize=13)
    ax.set_xlabel("Westpac-MI Consumer Sentiment")
    ax.set_ylabel("ANZ-Roy Morgan Consumer Confidence")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)
    save(fig, "scatter_survey_agreement")


def plot_survey_agreement_spread(agreement: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(agreement["date"], agreement["spread"], color="#8338ec", linewidth=1.3)
    ax.axhline(0, color="#888888", linewidth=0.8)
    ax.fill_between(agreement["date"], agreement["spread"], 0, color="#8338ec", alpha=0.15)
    ax.set_title("Survey Spread: Roy Morgan minus Westpac-MI, Same Month (2013-2026)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Roy Morgan − Westpac-MI (index points)")
    ax.grid(True, alpha=0.3)
    save(fig, "survey_agreement_spread")


def plot_rolling_correlation_confidence_vs_cashrate(rolling_corr: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))

    hiking = rolling_corr["rate_trend"] > 0
    easing = rolling_corr["rate_trend"] < 0
    ax.fill_between(
        rolling_corr["date"], -1, 1, where=hiking, color="#d1495b", alpha=0.12,
        step=None, interpolate=True, label="Net hiking (trailing 24mo)",
    )
    ax.fill_between(
        rolling_corr["date"], -1, 1, where=easing, color="#3d5a80", alpha=0.12,
        step=None, interpolate=True, label="Net easing (trailing 24mo)",
    )

    ax.plot(rolling_corr["date"], rolling_corr["rolling_corr"], color="#8338ec", linewidth=1.5,
             label="Rolling correlation")
    ax.axhline(0, color="#888888", linewidth=0.8)
    ax.set_title("24-Month Rolling Correlation: Confidence vs Cash Rate, by Rate Cycle Direction (2011-2026)", fontsize=13)
    ax.set_xlabel("Year")
    ax.set_ylabel("Rolling Pearson correlation")
    ax.set_ylim(-1, 1)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    save(fig, "rolling_correlation_confidence_vs_cashrate")


def plot_rolling_correlation_confidence_vs_cashrate_by_inflation(rolling_corr: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))

    rba_target_midpoint = 2.5
    elevated = rolling_corr["cpi_trailing_avg"] > rba_target_midpoint
    low = rolling_corr["cpi_trailing_avg"] <= rba_target_midpoint
    ax.fill_between(
        rolling_corr["date"], -1, 1, where=elevated, color="#d1495b", alpha=0.12,
        step=None, interpolate=True, label="Elevated inflation (trailing 24mo avg > 2.5%)",
    )
    ax.fill_between(
        rolling_corr["date"], -1, 1, where=low, color="#3d5a80", alpha=0.12,
        step=None, interpolate=True, label="Low/normal inflation (trailing 24mo avg <= 2.5%)",
    )

    ax.plot(rolling_corr["date"], rolling_corr["rolling_corr"], color="#8338ec", linewidth=1.5,
             label="Rolling correlation")
    ax.axhline(0, color="#888888", linewidth=0.8)
    ax.set_title("24-Month Rolling Correlation: Confidence vs Cash Rate, by Inflation Environment (2011-2026)", fontsize=13)
    ax.set_xlabel("Year")
    ax.set_ylabel("Rolling Pearson correlation")
    ax.set_ylim(-1, 1)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    save(fig, "rolling_correlation_confidence_vs_cashrate_by_inflation")


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


def plot_confidence_with_shocks(combined: pd.DataFrame):
    """Same confidence timeline as plot_confidence_with_recessions, but
    annotated with the specific discrete shocks the rest of the analysis
    points to as the real driver of confidence's biggest moves, rather than
    generic recession shading. Gives the "it's shocks, not indicator
    levels" finding its own chart instead of leaving the reader to piece it
    together from the recession overlay and rolling-correlation charts."""
    fig, ax = plt.subplots(figsize=(13, 7))

    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series)
        ax.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series], zorder=3)

    roy_morgan = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"].sort_values("date")

    for date_str, text, y_offset in SHOCKS:
        shock_date = pd.Timestamp(date_str)
        ax.axvline(shock_date, color="#d1495b", linewidth=1.0, alpha=0.5, zorder=1)

        nearest = roy_morgan.iloc[(roy_morgan["date"] - shock_date).abs().argsort()[:1]]
        y = float(nearest["value"].iloc[0])
        va = "top" if y_offset < 0 else "bottom"
        ax.annotate(
            text, xy=(shock_date, y), xytext=(0, y_offset), textcoords="offset points",
            ha="center", va=va, fontsize=8, color="#333333",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#d1495b", alpha=0.9),
        )

    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("Australian Consumer Confidence: What Actually Moved It", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Confidence Index")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)
    save(fig, "confidence_with_shocks")


def plot_confidence_with_elections(combined: pd.DataFrame, elections: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 7))

    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series)
        ax.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series], zorder=3)

    for d in elections["date"]:
        ax.axvline(d, color="#d1495b", linewidth=1.0, alpha=0.5, zorder=1)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color="#d1495b", alpha=0.5, linewidth=1.5))
    labels.append("Federal election")
    ax.legend(handles, labels, loc="upper right", fontsize=9)

    ax.set_title("Australian Consumer Confidence with Federal Elections Marked (1972-2025)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Confidence Index")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)
    save(fig, "confidence_with_elections")


def plot_confidence_with_budgets(combined: pd.DataFrame, budgets: pd.DataFrame):
    cutoff = pd.Timestamp("2011-01-01")

    fig, ax = plt.subplots(figsize=(13, 7))

    for series in ("anz_roy_morgan_consumer_confidence", "westpac_mi_consumer_sentiment"):
        dates, vals = series_xy(combined, series, since=cutoff)
        ax.plot(dates, vals, color=COLORS[series], linewidth=1.3, label=SERIES_LABELS[series], zorder=3)

    for d in budgets["date"]:
        if d >= cutoff:
            ax.axvline(d, color="#2b7a78", linewidth=1.0, alpha=0.5, zorder=1)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color="#2b7a78", alpha=0.5, linewidth=1.5))
    labels.append("Budget night")
    ax.legend(handles, labels, loc="upper right", fontsize=9)

    ax.set_title("Australian Consumer Confidence with Budget Nights Marked (2011-2026)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Confidence Index")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)
    save(fig, "confidence_with_budgets")


def plot_event_window_deltas(deltas: pd.DataFrame, event_type: str, color: str, filename: str):
    deltas = deltas.sort_values("delta").reset_index(drop=True)
    avg_delta = deltas["delta"].mean()

    fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(deltas))))
    y = range(len(deltas))
    ax.hlines(y, 0, deltas["delta"], color=color, alpha=0.6, linewidth=2)
    ax.scatter(deltas["delta"], y, color=color, s=30, zorder=3)
    ax.axvline(0, color="#888888", linewidth=0.8)
    ax.axvline(avg_delta, color="#d1495b", linewidth=1.2, linestyle="--",
                label=f"Average: {avg_delta:+.2f} points")

    ax.set_yticks(list(y))
    ax.set_yticklabels(deltas["label"], fontsize=8)
    ax.set_xlabel("Confidence change: mean(2mo after) - mean(2mo before)")
    ax.set_title(f"Confidence Change Around Each {event_type} (±2-Month Window)", fontsize=13)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3, axis="x")
    save(fig, filename)


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
        raise SystemExit(f"{in_path} not found, run `python3 load_data.py` first.")

    PLOTS_DIR.mkdir(exist_ok=True)
    combined = pd.read_csv(in_path, parse_dates=["date"])

    scatter_cashrate = build_scatter_confidence_vs_cashrate(combined)
    scatter_cpi = build_scatter_confidence_vs_cpi(combined)
    scatter_unemployment = build_scatter_confidence_vs_unemployment(combined)
    scatter_cashrate_delta = build_scatter_confidence_delta_vs_cashrate_delta(combined)
    rolling_corr = build_rolling_correlation_confidence_vs_cashrate(combined)
    elections = load_events("events_elections.csv")
    budgets = load_events("events_budgets.csv")
    election_deltas = build_event_window_deltas(combined, elections)
    budget_deltas = build_event_window_deltas(combined, budgets)
    survey_agreement = build_survey_agreement(combined)
    calendar_heatmap = build_confidence_calendar_heatmap(combined)

    plot_confidence_indices(combined)
    plot_cpi_index(combined)
    plot_cpi_pct_change(combined)
    plot_cash_rate(combined)
    plot_scatter_confidence_vs_cashrate(scatter_cashrate)
    plot_scatter_confidence_vs_cpi(scatter_cpi)
    plot_scatter_confidence_vs_unemployment(scatter_unemployment)
    plot_scatter_confidence_delta_vs_cashrate_delta(scatter_cashrate_delta)
    plot_rolling_correlation_confidence_vs_cashrate(rolling_corr)
    plot_rolling_correlation_confidence_vs_cashrate_by_inflation(rolling_corr)
    plot_confidence_with_recessions(combined)
    plot_confidence_with_shocks(combined)
    plot_confidence_with_elections(combined, elections)
    plot_confidence_with_budgets(combined, budgets)
    plot_event_window_deltas(election_deltas, "Election", "#d1495b", "event_window_deltas_elections")
    plot_event_window_deltas(budget_deltas, "Budget", "#2b7a78", "event_window_deltas_budgets")
    plot_survey_agreement_scatter(survey_agreement)
    plot_survey_agreement_spread(survey_agreement)
    plot_confidence_and_cashrate_dual_axis(combined)
    plot_confidence_calendar_heatmap(calendar_heatmap)

    print(f"wrote 20 charts to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
