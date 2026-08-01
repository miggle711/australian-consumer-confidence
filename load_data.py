#!/usr/bin/env python3
"""Australian Consumer Confidence: load raw data, clean, combine.

Reads manually downloaded files from raw/ (see raw/SOURCES.md for
provenance), reshapes each into tidy (date, series, value) rows, and
combines them into cleaned/consumer_confidence_data.csv.

Usage: python3 load_data.py
Requires: pip install -r requirements.txt
"""

import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
RAW_DIR = REPO_ROOT / "raw"
CLEANED_DIR = REPO_ROOT / "cleaned"


# ---------------------------------------------------------------------------
# Per-source loaders. Each returns a tidy DataFrame with columns
# date (datetime64), series (str), value (float).
# ---------------------------------------------------------------------------


def load_westpac_mi_consumer_sentiment() -> pd.DataFrame:
    """Westpac-MI Consumer Sentiment (AUCCI). Plain date,value CSV."""
    df = pd.read_csv(RAW_DIR / "westpac_mi_consumer_sentiment.csv")
    return pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"]),
            "series": "westpac_mi_consumer_sentiment",
            "value": df["value"].astype(float),
        }
    )


def load_roy_morgan_consumer_confidence() -> pd.DataFrame:
    """ANZ-Roy Morgan Consumer Confidence. Wide: one row per year, one
    column per month, with occasional footnote markers (e.g. "74.2**")."""
    df = pd.read_csv(RAW_DIR / "roy_morgan_consumer_confidence.csv")
    df.columns = [c.strip() for c in df.columns]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    rows = []
    for _, row in df.iterrows():
        year = row.get("YEAR")
        if pd.isna(year):
            continue
        year = int(year)
        for month_idx, month_name in enumerate(months, start=1):
            raw = row.get(month_name)
            if pd.isna(raw) or str(raw).strip() == "":
                continue
            cleaned = re.match(r"[-\d.]+", str(raw).strip())
            if not cleaned:
                continue
            rows.append((pd.Timestamp(year=year, month=month_idx, day=1), float(cleaned.group())))

    dates, values = zip(*rows)
    return pd.DataFrame(
        {"date": dates, "series": "anz_roy_morgan_consumer_confidence", "value": values}
    )


def load_rba_cash_rate_target() -> pd.DataFrame:
    """RBA Cash Rate Target. Metadata header block, then daily rows in
    'DD-Mon-YYYY' format; only the Cash Rate Target column is kept."""
    raw = pd.read_csv(RAW_DIR / "rba_cash_rate_target.csv", header=None, skip_blank_lines=False)
    header_row_idx = raw.index[raw[0] == "Series ID"][0]
    data = raw.iloc[header_row_idx + 1 :]

    dates = pd.to_datetime(data[0], format="%d-%b-%Y", errors="coerce")
    values = pd.to_numeric(data[1], errors="coerce")
    mask = dates.notna() & values.notna()

    return pd.DataFrame(
        {"date": dates[mask], "series": "rba_cash_rate_target", "value": values[mask]}
    )


def load_abs_cpi_quarterly() -> pd.DataFrame:
    """ABS CPI Quarterly, All Groups (Table 17). Header block with
    description/unit/series-type rows, then quarterly rows in 'Mon-YYYY'
    format. Only the national "Australia" index level and
    percentage-change-from-previous-period columns are kept."""
    raw = pd.read_csv(RAW_DIR / "abs_cpi_quarterly.csv", header=None, skip_blank_lines=False)
    labels = raw.iloc[0].str.strip()

    index_col = labels[labels == "Index Numbers ;  All groups CPI ;  Australia ;"].index[0]
    pct_col = labels[
        labels == "Percentage Change from Previous Period ;  All groups CPI ;  Australia ;"
    ].index[0]

    header_row_idx = raw.index[raw[0] == "Series ID"][0]
    data = raw.iloc[header_row_idx + 1 :]

    dates = pd.to_datetime(data[0], format="%b-%Y", errors="coerce")

    index_values = pd.to_numeric(data[index_col], errors="coerce")
    index_mask = dates.notna() & index_values.notna()
    index_df = pd.DataFrame(
        {
            "date": dates[index_mask],
            "series": "abs_cpi_index_australia",
            "value": index_values[index_mask],
        }
    )

    pct_values = pd.to_numeric(data[pct_col], errors="coerce")
    pct_mask = dates.notna() & pct_values.notna()
    pct_df = pd.DataFrame(
        {
            "date": dates[pct_mask],
            "series": "abs_cpi_pct_change_australia",
            "value": pct_values[pct_mask],
        }
    )

    return pd.concat([index_df, pct_df], ignore_index=True)


def load_abs_labour_force() -> pd.DataFrame:
    """ABS Labour Force (Table 001). Header block where row 0 has data-item
    labels and row 2 has series type (Trend/Seasonally Adjusted/Original);
    the same label repeats three times, so columns are matched on label AND
    series type together. Only national unemployment rate and
    participation rate, seasonally adjusted, are kept."""
    raw = pd.read_csv(RAW_DIR / "abs_labour_force.csv", header=None, skip_blank_lines=False)
    labels = raw.iloc[0].str.strip()
    series_types = raw.iloc[2].str.strip()

    def find_col(label: str) -> int:
        mask = (labels == label) & (series_types == "Seasonally Adjusted")
        return labels[mask].index[0]

    unemployment_col = find_col("Unemployment rate ;  Persons ;")
    participation_col = find_col("Participation rate ;  Persons ;")

    header_row_idx = raw.index[raw[0] == "Series ID"][0]
    data = raw.iloc[header_row_idx + 1 :]

    dates = pd.to_datetime(data[0], errors="coerce")

    unemployment_values = pd.to_numeric(data[unemployment_col], errors="coerce")
    unemployment_mask = dates.notna() & unemployment_values.notna()
    unemployment_df = pd.DataFrame(
        {
            "date": dates[unemployment_mask],
            "series": "abs_unemployment_rate_australia",
            "value": unemployment_values[unemployment_mask],
        }
    )

    participation_values = pd.to_numeric(data[participation_col], errors="coerce")
    participation_mask = dates.notna() & participation_values.notna()
    participation_df = pd.DataFrame(
        {
            "date": dates[participation_mask],
            "series": "abs_participation_rate_australia",
            "value": participation_values[participation_mask],
        }
    )

    return pd.concat([unemployment_df, participation_df], ignore_index=True)


LOADERS = {
    "Westpac-MI Consumer Sentiment (AUCCI)": (
        "westpac_mi_consumer_sentiment.csv",
        load_westpac_mi_consumer_sentiment,
    ),
    "ANZ-Roy Morgan Consumer Confidence": (
        "roy_morgan_consumer_confidence.csv",
        load_roy_morgan_consumer_confidence,
    ),
    "RBA Cash Rate Target": ("rba_cash_rate_target.csv", load_rba_cash_rate_target),
    "ABS CPI (All Groups, Australia)": ("abs_cpi_quarterly.csv", load_abs_cpi_quarterly),
    "ABS Labour Force (Unemployment & Participation Rate)": (
        "abs_labour_force.csv",
        load_abs_labour_force,
    ),
}


def load_all_sources() -> pd.DataFrame:
    frames = []
    for name, (filename, loader) in LOADERS.items():
        path = RAW_DIR / filename
        if not path.exists():
            print(f"skipping {name}, raw file not found at {path}")
            continue
        frame = loader()
        print(f"loaded {name}: {len(frame)} rows")
        frames.append(frame)

    if not frames:
        raise SystemExit("no datasets loaded, add CSVs under raw/ (see raw/SOURCES.md) and rerun")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["series", "date"]).reset_index(drop=True)
    return combined


def main():
    CLEANED_DIR.mkdir(exist_ok=True)

    combined = load_all_sources()

    out_path = CLEANED_DIR / "consumer_confidence_data.csv"
    combined.to_csv(out_path, index=False, date_format="%Y-%m-%d")
    print(f"wrote {len(combined)} rows to {out_path}")


if __name__ == "__main__":
    main()
