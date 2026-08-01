# Raw data sources

Provenance for each file in this directory. See [../README.md](../README.md)
for how these feed into the pipeline, and [../INSIGHTS.md](../INSIGHTS.md)
for what the resulting charts show.

## westpac_mi_consumer_sentiment.csv

- **Series**: Westpac-Melbourne Institute Consumer Sentiment Index (AUCCI)
- **Source**: [TradingView Economic Calendar API](https://www.tradingview.com/symbols/ECONOMICS-AUCCI/)
  (`economic-calendar.tradingview.com/events_by_history_symbol`)
- **Coverage**: March 2013 – July 2026, monthly
- **Retrieved**: 2026-08-01
- **Note**: TradingView's economic-calendar API caps out at March 2013 for
  this symbol regardless of an earlier `from` date requested. The full
  series (published since 1975) exists on TradingView's interactive chart
  (`timeframe=ALL`) but is served over a protected WebSocket feed, not a
  public REST endpoint — not fetched here. Longer free/paid alternatives
  investigated: Melbourne Institute (subscription required), Trading
  Economics and MacroMicro (both gate full history behind paid plans).

## roy_morgan_consumer_confidence.csv

- **Series**: ANZ-Roy Morgan Australian Consumer Confidence, monthly ratings
- **Source**: [Roy Morgan](https://www.roymorgan.com/morgan-poll/consumer-confidence-anz-roy-morgan-australian-cc-monthly-ratings)
- **Coverage**: March 1973 – July 2026, monthly (sparse in early years —
  only quarterly surveys were run before the series became fully monthly)
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export is wide format (one row per year, one column
  per month) with occasional footnote markers on values (e.g. `74.2**`).
  Reshaped to long format and stripped of markers by
  [../src/roy_morgan.rs](../src/roy_morgan.rs).

## rba_cash_rate_target.csv

- **Series**: RBA Cash Rate Target (Table F1: Interest Rates and Yields –
  Money Market)
- **Source**: [RBA Statistical Tables](https://www.rba.gov.au/statistics/tables/)
- **Coverage**: January 2011 – July 2026, daily
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export includes a metadata header block (series
  descriptions, units, series IDs) and dozens of related columns (interbank
  rates, BABs/NCDs, OIS, Treasury Notes). Only the Cash Rate Target column
  is extracted, by [../src/rba_cash_rate.rs](../src/rba_cash_rate.rs).

## abs_cpi_quarterly.csv

- **Series**: CPI Quarterly, All Groups, Index numbers and Percentage
  change (ABS Table 17, from catalogue 6401.0 Consumer Price Index,
  Australia)
- **Source**: [ABS Consumer Price Index, Australia](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release)
- **Coverage**: September 1948 – June 2026, quarterly
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export includes per-capital-city columns (Sydney,
  Melbourne, Brisbane, etc.); only the national "Australia" index level and
  percentage-change-from-previous-period columns are extracted, by
  [../src/abs_cpi.rs](../src/abs_cpi.rs).

## RBA CPI- All Groups, Index numbers and Percentage change.xlsx

- **Series**: CPI, All Groups, Index numbers and Percentage change (ABS
  Table 1, monthly release)
- **Source**: [ABS Consumer Price Index, Australia](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release)
- **Coverage**: April 2024 – June 2026, monthly
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: ABS only began publishing a full monthly CPI series from April
  2024 onward (prior to that, CPI was quarterly-only — see
  `abs_cpi_quarterly.csv` above for the long-running quarterly series).
  Not currently wired into the pipeline (xlsx, not CSV) — kept here for a
  possible future monthly-CPI loader.
