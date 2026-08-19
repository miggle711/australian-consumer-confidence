#!/usr/bin/env python3
"""Export Tableau-ready CSVs from the cleaned data and the derived tables
already built in plot.py.

Tableau wants one row per date with each series as its own column (wide
format), and can compute simple things (deltas, dual-axis, reference
lines/bands from a joined secondary table) natively via calculated
fields/table calcs. It can't derive a rolling correlation, an event-window
before/after comparison, or a year x month reshape without a lot of
fighting the tool, so those three are exported pre-computed here, same as
the brief allows ("use existing data", the derivation happens once outside
Tableau rather than being fabricated).

Usage: python3 load_data.py && python3 export_tableau.py
Writes every file into tableau_export/.
"""

from pathlib import Path

import pandas as pd

from plot import (
    CLEANED_DIR,
    build_event_window_deltas,
    build_rolling_correlation_confidence_vs_cashrate,
    load_events,
)

REPO_ROOT = Path(__file__).resolve().parent
EXPORT_DIR = REPO_ROOT / "tableau_export"


def main():
    in_path = CLEANED_DIR / "consumer_confidence_data.csv"
    if not in_path.exists():
        raise SystemExit(f"{in_path} not found, run `python3 load_data.py` first.")

    EXPORT_DIR.mkdir(exist_ok=True)
    combined = pd.read_csv(in_path, parse_dates=["date"])

    # 1. Main wide monthly table: date + one column per series, forward-filled
    #    for the daily/quarterly series (cash rate, CPI) so every month has a
    #    value. Confidence and labour force are left as-is (already monthly).
    monthly = combined.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    wide = (
        monthly.sort_values("date")
        .groupby(["month", "series"])["value"]
        .last()
        .unstack("series")
        .sort_index()
    )
    ffill_cols = ["rba_cash_rate_target", "abs_cpi_index_australia", "abs_cpi_pct_change_australia"]
    wide[ffill_cols] = wide[ffill_cols].ffill()
    wide = wide.reset_index().rename(columns={"month": "date"})
    wide.to_csv(EXPORT_DIR / "confidence_monthly_wide.csv", index=False)

    # 2. Rolling correlation (confidence vs cash rate, + inflation regime band)
    rolling_corr = build_rolling_correlation_confidence_vs_cashrate(combined)
    rolling_corr.to_csv(EXPORT_DIR / "rolling_correlation.csv", index=False)

    # 3. Event-window deltas (elections, budgets), one flat table with an
    #    event_type column so Tableau can filter/colour by type in one sheet.
    elections = load_events("events_elections.csv")
    budgets = load_events("events_budgets.csv")
    election_deltas = build_event_window_deltas(combined, elections).assign(event_type="Election")
    budget_deltas = build_event_window_deltas(combined, budgets).assign(event_type="Budget")
    event_deltas = pd.concat([election_deltas, budget_deltas], ignore_index=True)
    event_deltas.to_csv(EXPORT_DIR / "event_window_deltas.csv", index=False)

    # 4. Calendar heatmap, long format (year, month, delta) rather than the
    #    pivoted grid used for the matplotlib version: Tableau builds the
    #    grid itself from long data via row/column shelves.
    confidence = combined[combined["series"] == "anz_roy_morgan_consumer_confidence"][
        ["date", "value"]
    ].sort_values("date").copy()
    confidence["delta"] = confidence["value"].diff()
    confidence["year"] = confidence["date"].dt.year
    confidence["month"] = confidence["date"].dt.month
    confidence["month_name"] = confidence["date"].dt.strftime("%b")
    heatmap_long = confidence[confidence["year"] >= 1990][
        ["date", "year", "month", "month_name", "value", "delta"]
    ]
    heatmap_long.to_csv(EXPORT_DIR / "calendar_heatmap.csv", index=False)

    # 5. Shock annotations: hand-curated markers for the climax chart, kept
    #    as its own tiny reference table (same pattern as elections/budgets).
    shocks = pd.DataFrame(
        [
            {"date": "1990-11-01", "label": "1990-91 recession (deepest reading in the series)"},
            {"date": "2020-04-01", "label": "COVID crash (116 -> 79.8 in two months)"},
            {"date": "2022-09-01", "label": "2022-23 hiking cycle + inflation shock"},
            {"date": "2024-09-01", "label": "Sustained low without a declared recession"},
        ]
    )
    shocks.to_csv(EXPORT_DIR / "shocks.csv", index=False)

    # 6. Events (elections/budgets) as reference-line tables, straight passthrough.
    elections.to_csv(EXPORT_DIR / "events_elections.csv", index=False)
    budgets.to_csv(EXPORT_DIR / "events_budgets.csv", index=False)

    print(f"wrote 7 Tableau-ready CSVs to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
