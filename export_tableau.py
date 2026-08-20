#!/usr/bin/env python3
"""Export Tableau-ready CSVs from the cleaned data and the derived tables
already built in plot.py.

Tableau wants one row per date with each series as its own column (wide
format), and can compute simple things (deltas, dual-axis, reference
lines/bands from a joined secondary table) natively via calculated
fields/table calcs. It can't derive an event-window before/after
comparison or a year x month reshape without a lot of fighting the tool,
so those are exported pre-computed here, same as the brief allows ("use
existing data", the derivation happens once outside Tableau rather than
being fabricated).

Usage: python3 load_data.py && python3 export_tableau.py
Writes every file into tableau_export/.
"""

from pathlib import Path

import pandas as pd

from plot import (
    CLEANED_DIR,
    RECESSIONS,
    REGIME_WINDOWS,
    build_event_window_deltas,
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

    # 2. Event-window deltas (elections, budgets), one flat table with an
    #    event_type column so Tableau can filter/colour by type in one sheet.
    elections = load_events("events_elections.csv")
    budgets = load_events("events_budgets.csv")
    election_deltas = build_event_window_deltas(combined, elections).assign(event_type="Election")
    budget_deltas = build_event_window_deltas(combined, budgets).assign(event_type="Budget")
    event_deltas = pd.concat([election_deltas, budget_deltas], ignore_index=True)
    event_deltas.to_csv(EXPORT_DIR / "event_window_deltas.csv", index=False)

    # 3. Calendar heatmap, long format (year, month, delta) rather than the
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

    # 4. Shock annotations: hand-curated markers for the climax chart, kept
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

    # 5. Regime windows: hand-curated start/end/label for the "moving
    #    together vs. moving apart" overlay chart, same start/end/colour
    #    used to shade plots/confidence_and_cashrate_regimes.png. Label
    #    newlines (used to wrap text in the matplotlib annotation box) are
    #    flattened to spaces for the flat CSV.
    regime_windows = pd.DataFrame(REGIME_WINDOWS, columns=["start_date", "end_date", "label", "color"])
    regime_windows["label"] = regime_windows["label"].str.replace("\n", " ", regex=False)
    regime_windows.to_csv(EXPORT_DIR / "regime_windows.csv", index=False)

    # 6. Events (elections/budgets) as reference-line tables, straight passthrough.
    elections.to_csv(EXPORT_DIR / "events_elections.csv", index=False)
    budgets.to_csv(EXPORT_DIR / "events_budgets.csv", index=False)

    # 6b. Combined elections + budgets, one table with an event_type column,
    #     for the single overlay chart with a show/hide toggle (rather than
    #     two separate near-identical timeline charts).
    events_combined = pd.concat(
        [elections.assign(event_type="Election"), budgets.assign(event_type="Budget")],
        ignore_index=True,
    )
    events_combined.to_csv(EXPORT_DIR / "events_combined.csv", index=False)

    # 7. Recession periods, one row per recession with start/end/label, for
    #    the reference-band blend on the confidence timeline. See
    #    raw/README.md for sourcing and the peak-to-trough vs. strict
    #    two-consecutive-quarters distinction.
    recession_labels = ["1974-75 recession", "1982-83 recession", "1990-91 recession", "2020 recession"]
    recessions = pd.DataFrame(
        [(start, end, label) for (start, end), label in zip(RECESSIONS, recession_labels)],
        columns=["start_date", "end_date", "label"],
    )
    recessions.to_csv(EXPORT_DIR / "recessions.csv", index=False)

    print(f"wrote 10 Tableau-ready CSVs to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
