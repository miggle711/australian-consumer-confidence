# Raw data sources

Provenance for each file in this directory. See [../README.md](../README.md)
for how these feed into the pipeline, and [../INSIGHTS.md](../INSIGHTS.md)
for what the resulting charts show.

## westpac_mi_consumer_sentiment.csv

- **Series**: Westpac-Melbourne Institute Consumer Sentiment Index (AUCCI)
- **Source**: [TradingView Economic Calendar API](https://www.tradingview.com/symbols/ECONOMICS-AUCCI/)
  (`economic-calendar.tradingview.com/events_by_history_symbol`)
- **Coverage**: March 2013 - July 2026, monthly
- **Retrieved**: 2026-08-01
- **Note**: TradingView's economic-calendar API caps out at March 2013 for
  this symbol regardless of an earlier `from` date requested. The full
  series (published since 1975) exists on TradingView's interactive chart
  (`timeframe=ALL`) but is served over a protected WebSocket feed, not a
  public REST endpoint, not fetched here. Longer free/paid alternatives
  investigated: Melbourne Institute (subscription required), Trading
  Economics and MacroMicro (both gate full history behind paid plans).

## roy_morgan_consumer_confidence.csv

- **Series**: ANZ-Roy Morgan Australian Consumer Confidence, monthly ratings
- **Source**: [Roy Morgan](https://www.roymorgan.com/morgan-poll/consumer-confidence-anz-roy-morgan-australian-cc-monthly-ratings)
- **Coverage**: March 1973 - July 2026, monthly (sparse in early years:
  only quarterly surveys were run before the series became fully monthly)
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export is wide format (one row per year, one column
  per month) with occasional footnote markers on values (e.g. `74.2**`).
  Reshaped to long format and stripped of markers by
  `load_roy_morgan_consumer_confidence` in [../load_data.py](../load_data.py).

## rba_cash_rate_target.csv

- **Series**: RBA Cash Rate Target (Table F1: Interest Rates and Yields -
  Money Market)
- **Source**: [RBA Statistical Tables](https://www.rba.gov.au/statistics/tables/)
- **Coverage**: January 2011 - July 2026, daily
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export includes a metadata header block (series
  descriptions, units, series IDs) and dozens of related columns (interbank
  rates, BABs/NCDs, OIS, Treasury Notes). Only the Cash Rate Target column
  is extracted, by `load_rba_cash_rate_target` in [../load_data.py](../load_data.py).

## abs_cpi_quarterly.csv

- **Series**: CPI Quarterly, All Groups, Index numbers and Percentage
  change (ABS Table 17, from catalogue 6401.0 Consumer Price Index,
  Australia)
- **Source**: [ABS Consumer Price Index, Australia](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release)
- **Coverage**: September 1948 - June 2026, quarterly
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: Original export includes per-capital-city columns (Sydney,
  Melbourne, Brisbane, etc.); only the national "Australia" index level and
  percentage-change-from-previous-period columns are extracted, by
  `load_abs_cpi_quarterly` in [../load_data.py](../load_data.py).

## abs_labour_force.csv

- **Series**: Labour force status by Sex, Australia: unemployment rate and
  participation rate, seasonally adjusted (ABS Table 001, from catalogue
  6202.0 Labour Force, Australia)
- **Source**: [ABS Labour Force, Australia](https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release)
- **Coverage**: February 1978 - June 2026, monthly
- **Retrieved**: manually downloaded by user (as xlsx), 2026-08-01
- **Note**: Original download is
  `raw/Table 001. Labour force status by Sex, Australia - Trend, Seasonally adjusted and Original.xlsx`,
  converted to CSV (ISO dates) for the loader. The workbook has 115 columns
  (Persons/Males/Females x Trend/Seasonally Adjusted/Original for a dozen
  labour force measures); only national "Persons, Seasonally Adjusted"
  unemployment rate and participation rate are extracted, by
  `load_abs_labour_force` in [../load_data.py](../load_data.py). Column
  labels repeat across the three series-type variants, so the loader
  matches on label text *and* the series-type header row together.

## events_elections.csv

- **Series**: Australian federal election polling dates, 1972-2025
- **Source**: [AEC: Election dates 1901-present](https://www.aec.gov.au/elections/federal_elections/election-dates.htm)
  for dates through 2016; individual Wikipedia election pages and the
  [AEC 2025 election timetable](https://www.aec.gov.au/Elections/federal_elections/2025/timetable.htm)
  for 2019, 2022, 2025 (the AEC's general dates page was last updated
  2022-07-20 and doesn't yet list 2025).
- **Coverage**: 1972-2025, one row per election (not manually downloaded;
  compiled from public record)
- **Compiled**: 2026-08-01
- **Note**: Hand-curated, not machine-parsed from a table export. Used to
  test whether confidence dips pre-election and recovers after, the same
  question the recession-overlay chart asks of recessions.

## events_budgets.csv

- **Series**: Australian Commonwealth Budget night dates, 1994-2026
- **Source**: Public record (Treasury/Parliament budget announcements);
  confirmed via web search against multiple sources including Wikipedia's
  per-year budget pages and [budget.gov.au](https://budget.gov.au/).
- **Coverage**: 1994-2026, one row per budget (two rows for 2022, which had
  both a pre-election March budget and a post-election October budget)
- **Compiled**: 2026-08-01
- **Note**: From 1994 onward the convention is the second Tuesday in May;
  most rows follow that rule, with known exceptions (2016: early to 3 May;
  2019: early to 2 April, ahead of the election; 2020: delayed to October
  due to COVID; 2022: two budgets; 2025: early to 25 March) hardcoded from
  confirmed sources rather than computed. Pre-1994 budgets (delivered in
  August under the old Spring-session convention) are not included since
  the exact date isn't confidently known for each year.

## RBA CPI- All Groups, Index numbers and Percentage change.xlsx

- **Series**: CPI, All Groups, Index numbers and Percentage change (ABS
  Table 1, monthly release)
- **Source**: [ABS Consumer Price Index, Australia](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release)
- **Coverage**: April 2024 - June 2026, monthly
- **Retrieved**: manually downloaded by user, 2026-08-01
- **Note**: ABS only began publishing a full monthly CPI series from April
  2024 onward (prior to that, CPI was quarterly-only; see
  `abs_cpi_quarterly.csv` above for the long-running quarterly series).
  Not currently wired into the pipeline (xlsx, not CSV), kept here for a
  possible future monthly-CPI loader.
