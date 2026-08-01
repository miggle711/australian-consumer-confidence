# Insights

Observations from the plots in [plots/](plots/), generated from
[cleaned/consumer_confidence_data.csv](cleaned/consumer_confidence_data.csv).
Each entry links the chart it came from. These are visual/exploratory
readings, not statistically tested claims: treat them as hypotheses to dig
into further, not conclusions.

## Recessions line up with confidence troughs

[plots/confidence_with_recessions.png](plots/confidence_with_recessions.png)

Each of Australia's four major downturns since 1973 (1974-75 oil shock,
1982-83, 1990-91, 2020 COVID) lines up with a visible confidence trough in
the ANZ-Roy Morgan series. The 1990-91 recession ("the recession we had to
have") produced the single deepest reading in the entire 50-year series
(~71).

The current 2023-2026 downturn in confidence, the lowest sustained
readings since the early 1990s, has **no corresponding shaded recession
period**, since no official recession has been declared this cycle. Confidence
is behaving like a recession-era trough without an actual recession, which
points to inflation/cost-of-living and rate pressure as the driver rather
than a GDP contraction.

## Cash rate hikes (2022-23) line up with the current confidence collapse

[plots/confidence_and_cashrate_dual_axis.png](plots/confidence_and_cashrate_dual_axis.png)

The RBA's 2022-2023 hiking cycle (0.1% -> 4.35%) lines up closely with
confidence falling from its post-COVID recovery peak (~113) down to some of
the lowest sustained levels in the series (~65-80 through 2023-2026). This is
the clearest visual correlation between rate policy and confidence found so
far.

By contrast, the slow 2011-2020 easing cycle (4.75% -> ~0%) shows **no clear
confidence response**: confidence just meandered in its normal range
throughout. This suggests confidence reacts more to the *pace/direction* of
rate change (especially rapid hikes) than to the absolute rate level.

During the 2020 near-zero-rate period, confidence collapsed first (the
initial COVID shock) then recovered sharply *while rates stayed at
rock-bottom*: the shock itself, not the rate cut, was driving sentiment.

## No clean linear relationship between confidence and rate level or CPI

[plots/scatter_confidence_vs_cashrate.png](plots/scatter_confidence_vs_cashrate.png),
[plots/scatter_confidence_vs_cpi.png](plots/scatter_confidence_vs_cpi.png)

Plotting confidence against cash rate *level* (rather than the timeline
above) shows no simple linear trend: readings cluster into two bands
(~100-125 and ~65-90) across nearly every rate level from 0-5%. This
reinforces that the *level* of rates isn't predictive on its own; timing and
direction of change (see above) seem to matter more.

Confidence vs. CPI quarterly inflation shows a similar lack of a clean
trend, though there's a mild skew toward lower confidence at higher
inflation (>3%), most visible in the extreme-inflation quarters of the
1970s-80s oil shocks.

## Unemployment level alone doesn't predict confidence either

[plots/scatter_confidence_vs_unemployment.png](plots/scatter_confidence_vs_unemployment.png)

Like cash rate and CPI, unemployment rate *level* shows no clean trend
against confidence: readings span nearly the full confidence range (65-130)
at almost every unemployment level from 4% to 11%. Notably, the
highest-unemployment readings (10-11%, the early-1990s recession peak) include
some of the *highest* confidence scores in the dataset (~125-128) alongside
some of the lowest, likely capturing recovery periods where confidence has
already rebounded while unemployment is still working through its lag (a
well-known lagging indicator).

This is consistent with the pattern seen across all three economic
indicators so far: none of cash rate, CPI, or unemployment *level* predicts
confidence on its own. Confidence looks driven more by rate of change,
timing relative to shocks/recoveries, and possibly expectations about the
future, not the current-period level of any single indicator.

## Open questions / next steps

- Test rate-of-change (delta) rather than rate level against confidence:
  the dual-axis chart suggests this may correlate better than level did.
- A rolling correlation chart (24-month window) would show whether the
  confidence/rate relationship strengthens specifically during hiking
  cycles, as the dual-axis chart hints.
- Check lagged relationships: does confidence respond same-month, or with
  a 1-3 month delay after a rate decision or CPI print?
