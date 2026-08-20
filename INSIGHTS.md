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

## Month-over-month rate changes don't predict confidence swings either

[plots/scatter_confidence_delta_vs_cashrate_delta.png](plots/scatter_confidence_delta_vs_cashrate_delta.png)

Testing the hypothesis from the dual-axis chart directly: does the *size*
of a month's cash rate change predict the *size* of that month's confidence
change? No. Points cluster in vertical stripes at the RBA's standard move
sizes (0%, 0.25%, 0.5%), as expected, but there's no visible slope. At 0%
cash rate change (no meeting, or a hold), confidence swings range from -20
to +13, the widest range in the whole chart, while the largest hikes
(+0.5%) show confidence changes clustered tightly between -2 and +2.

This means the biggest confidence swings happen in months when the cash
rate *didn't move at all*, which points away from the RBA decision itself
being the proximate cause of large confidence moves and toward other
same-month events (COVID announcements, inflation prints, elections,
budget releases) as the actual drivers. The dual-axis chart's visual
impression that 2022-23 hikes "caused" the confidence collapse likely
reflects both trends moving together over a multi-year window rather than
a month-to-month causal link.

## The confidence/cash-rate relationship flips sign over multi-year cycles

(chart image removed, see note below; analysis kept for reference)

**Superseded for the Tableau submission by
[plots/confidence_and_cashrate_regimes.png](plots/confidence_and_cashrate_regimes.png)**:
the rolling correlation coefficient is a statistical concept the
assignment brief asks to avoid unless properly taught, so the same
finding below is shown instead as an annotated overlay of the raw
confidence and cash-rate lines, labelled "moving together" / "moving
apart" at each window rather than a derived -1 to +1 statistic. This
analysis (and its chart) is kept here as the reasoning behind that
annotated chart's window boundaries and labels.

The 24-month rolling correlation between confidence and cash rate swings
repeatedly between strongly negative (~-0.85) and strongly positive
(~+0.88), crossing zero many times across 2011-2026. This is the missing
piece explaining why the static level scatter and the month-to-month delta
scatter both looked like noise: they're averaging together periods where
the relationship is opposite-signed, which cancels out in a single snapshot.

Two clear regimes stand out: 2019-2021 shows strongly *positive*
correlation (confidence and rates fell together heading into COVID, then
both partly recovered), while 2022 shows strongly *negative* correlation
(rates rising fast while confidence fell during the hiking cycle,
consistent with the dual-axis chart's visual impression). The relationship
is real, but its direction depends on the surrounding economic regime, not
a fixed rule; a static "does A predict B" scatter can't capture this, only
a windowed view can.

## Moving together vs. moving apart, shown without a statistic

[plots/confidence_and_cashrate_regimes.png](plots/confidence_and_cashrate_regimes.png)

The Tableau-facing version of the finding above: same dual-axis
confidence/cash-rate overlay as the standard dual-axis chart, but with
three windows shaded and labelled directly on the lines rather than as a
derived correlation number, so a general reader can verify the claim by
eye instead of trusting a statistic. 2016-17 ("rates fell, confidence
rose: moving apart"), 2019-21 ("both collapsed together in COVID, then
partly recovered together: moving together"), and 2022-23 ("rates rose
fast, confidence fell: moving apart") are the three clearest, most
visually legible examples from the rolling-correlation analysis; the
2013-14 and 2023 negative-correlation stretches and the 2014-15/2025
positive ones are not shown, since they're less visually obvious on the
raw lines and a three-window story is enough to make the "it depends on
the period" point without overloading the chart.

## Rate-cycle direction (hiking vs. easing) does not explain the sign flips

(chart image removed along with the rolling-correlation chart above; analysis kept for reference)

Tested the most obvious explanation for the regime flips above: is
correlation negative specifically during hiking cycles and positive during
easing cycles? Shaded the rolling correlation chart by the trailing
24-month net rate change (hiking in red, easing in blue) to check.

The answer is no, not cleanly. Almost the entire 2011-2026 window is a net
easing period (rates fell from 4.75% to near zero, then partly recovered);
the single hiking episode is 2022-2024. Correlation is indeed negative
during that hiking stretch, consistent with the earlier read, but
correlation is *also* negative during multiple easing stretches (2013-14,
2016-17, 2023) and *positive* during other easing stretches (2014-15,
2019-21, 2025). With only one hiking episode in the whole series to compare
against, and the sign flipping repeatedly within the (much longer) easing
periods too, rate-cycle direction alone isn't a sufficient explanation for
what characterizes a regime. Whatever is driving the flips (inflation
environment, crisis vs. calm, expectations) is not simply "which way rates
are moving."

## Elevated inflation lines up with negative correlation, but isn't sufficient alone

(chart image removed along with the rolling-correlation chart above; analysis kept for reference)

Shaded the rolling correlation chart by trailing 24-month average CPI
inflation (annualized from the quarterly % change figures), split at the
RBA's 2.5% target midpoint. This lines up better than rate-cycle direction
did: the "elevated inflation" band from 2022 onward closely tracks the
sharp drop into strongly negative correlation (down to -0.85), and the
brief elevated-inflation blip in 2013 coincides with a local dip too.

But it's not sufficient on its own; the "low/normal inflation" band (most
of 2014-2021) contains *both* the strongly positive regime (2019-21, up to
+0.88) and a strongly negative one (2016-17, down to -0.83). So low
inflation doesn't reliably predict a particular sign, only elevated
inflation seems to reliably coincide with negative correlation. This is a
partial answer: inflation environment plus something else (likely whether
confidence is being driven by a shared external shock like COVID, versus
diverging due to a policy response) together shape the regime.

## 2019-21 vs. 2016-17: an external shock, not a policy response, explains the sign

Compared the two low-inflation regimes with opposite correlation signs
directly by looking at start/end values and the shape of the confidence
series within each window.

**2016-17** (correlation ~-0.8): cash rate fell modestly (2.0% -> 1.5%),
unemployment fell modestly (6.0% -> 5.6%), and confidence *rose* slightly
(114.0 -> 115.6). Rates eased a little while the economy quietly
improved; confidence drifted the "wrong way" relative to rates, producing
a mild negative correlation.

**2019-21** (correlation ~+0.85): cash rate fell more steeply (1.5% ->
0.1%), but the real story is the shape of confidence within the window,
not just its start/end values: confidence crashed from 116 to 79.8 in
March-April 2020 alone (the COVID shock), then partially recovered through
late 2020 and 2021. That collapse-and-recover shape happened to line up
almost exactly with the RBA's emergency rate cuts to near-zero, producing a
strong positive correlation, but the two aren't really causally connected;
a pandemic shock and a policy response coincided in time, and correlation
picked up the coincidence.

**Conclusion**: the sign of the rolling correlation isn't really measuring
a stable economic relationship at all. It's measuring how much of
confidence's movement in a given window happens to be explained by
whatever else was going on (an external shock, a slow economic drift) that
also correlates with what rates were doing at the time. This is consistent
with everything found so far: confidence isn't driven by rates (or CPI, or
unemployment) in any fixed way; it responds to discrete events and
conditions, and any correlation with a policy variable is often
coincidental co-movement rather than one driving the other.

## Elections and budgets don't show a consistent confidence pattern either

[plots/confidence_with_elections.png](plots/confidence_with_elections.png),
[plots/confidence_with_budgets.png](plots/confidence_with_budgets.png)

Marked all 21 federal elections (1972-2025) and 34 budget nights (1994-2026,
see [raw/README.md](raw/README.md) for exact dates and sourcing) directly on
the confidence timeline, extending the same technique that worked well for
recessions.

Neither shows a consistent visual pattern. Some elections roughly coincide
with local confidence peaks or troughs (1990, 1996, 2007), but just as many
land in the middle of an unrelated trend with no visible reaction at all;
there's no reliable "confidence dips before, recovers after" shape repeated
across elections. Budget nights, being roughly annual, are too frequent
relative to the series' month-to-month noise to visually isolate a
consistent effect at this zoom level, and no obvious spike or dip lines up
with the budget markers either.

This is consistent with the broader pattern from the correlation analysis:
individual scheduled political/fiscal events don't appear to be reliable
standalone drivers of confidence either, at least not at the resolution
this chart can show. A specific-event effect, if one exists, is likely
smaller than the month-to-month noise in the series and would need a
statistical test (e.g. average confidence change in the N months around
each event, across all elections) rather than eyeballing a single timeline
to detect.

## Confirmed statistically: elections and budgets have no consistent average effect

[plots/event_window_deltas_elections.png](plots/event_window_deltas_elections.png),
[plots/event_window_deltas_budgets.png](plots/event_window_deltas_budgets.png)

Ran the statistical test flagged above: for each of the 21 elections and
34 budgets, computed mean confidence in the 2 months before vs. the 2
months after, and plotted every event's delta sorted, with the average
across all events marked.

The averages are close to zero and not meaningful given the spread:
**elections average +0.84 points**, **budgets average -0.16 points**,
against individual event deltas ranging from about -9 to +11 points. If
elections or budgets had a real, consistent effect on confidence, the
average would sit clearly away from zero relative to that spread; it
doesn't. This confirms what the visual overlay suggested, now with an
actual number rather than an impression: scheduled political and fiscal
events do not move consumer confidence in a consistent direction, at
least not within a two-month window.

The largest individual swings (2022 election: -9; 2020 and 2009 budgets:
+10 to +12) are almost certainly capturing external events that happened
to fall near those dates (COVID recovery, GFC-era stimulus, the 2022
inflation shock) rather than a reaction to the election or budget itself,
consistent with the earlier finding that apparent correlations in this
data tend to reflect coincidental external shocks rather than the
scheduled event being tested.

## The two confidence surveys agree on direction but disagree on level, and their gap flipped at COVID

[plots/scatter_survey_agreement.png](plots/scatter_survey_agreement.png),
[plots/survey_agreement_spread.png](plots/survey_agreement_spread.png)

Checked whether Roy Morgan and Westpac-MI, two independently run monthly
confidence surveys, actually measure the same thing over their overlapping
window (March 2013-present). They're reasonably correlated (Pearson r =
0.81) and clearly track the same big moves (the COVID crash, the 2022-24
decline), so they're not measuring unrelated things. But the scatter sits
well off the "perfect agreement" (y=x) line: Roy Morgan runs
systematically higher than Westpac-MI for most of the series.

The spread-over-time chart shows why that offset isn't a simple constant
bias: **Roy Morgan ran 10-20 points above Westpac-MI every single month
from 2013 through February 2020, then the gap flipped almost overnight in
March 2020** (from +12.9 in February to -3.4 in March), and Roy Morgan has
run mostly *below* Westpac-MI ever since, with the gap widening again
recently (down to -20 in 2026). The flip happens in the exact month of the
COVID confidence crash. The likely explanation is methodological: Roy
Morgan surveys are conducted continuously/weekly and aggregated, while
Westpac-MI is a single mid-month snapshot, so Roy Morgan's series probably
captured the initial COVID shock's full severity in real time while
Westpac's single survey point that month may have partially missed it.
That one-off shock appears to have reset the baseline relationship between
the two surveys permanently rather than the gap reverting afterward.

**Practical implication for the rest of this project**: any chart or
finding that overlays both series (e.g. the recession/election/budget
overlays, the dual-axis chart) should be read as two related but
non-interchangeable measures, not duplicate views of the same number, and
the pre-2020 vs. post-2020 relationship between them isn't stable.

## What actually moved confidence, shown directly

[plots/confidence_with_shocks.png](plots/confidence_with_shocks.png)

Every finding above points the same direction: none of cash rate, CPI, or
unemployment *level* predicts confidence, month-to-month rate changes
don't either, and neither elections nor budgets show a consistent average
effect. What's left is discrete shocks and the surrounding regime,
demonstrated concretely so far only by cross-referencing the recession
overlay and the rolling-correlation regime comparison.

This chart makes that conclusion visible on its own: the same confidence
timeline as the recession overlay, but annotated with the four specific
episodes the rest of the analysis identified as real drivers, rather than
generic recession shading. The 1990-91 trough (deepest reading in the
50-year series) and the COVID crash (116 -> 79.8 in two months) are the
two sharpest, clearest shocks in the whole dataset. The 2022-23 hiking
cycle and the resulting sustained low (2023-2026, with no declared
recession) are marked as a single connected episode rather than a
standalone "rates caused it" story, consistent with the earlier finding
that the correlation there reflects co-movement over a multi-year window,
not a month-to-month causal link.

## The calendar heatmap shows single-month shocks, not the slow 2022 grind

[plots/confidence_calendar_heatmap.png](plots/confidence_calendar_heatmap.png)

Reshaped month-over-month confidence change into a year x month grid
(1990-2026) to see whether the shock episodes are visible as a block of
colour, without needing to read them off a timeline. March 2020 (COVID)
is unmistakable, the single most extreme cell in the whole grid at
-21.4 points, and January 1990 (-recession lead-in) is similarly stark
at the other end.

The 2022-23 hiking/inflation period does **not** show up as a standout
cell the way COVID does: it's a string of unremarkable, mildly negative
months rather than one dramatic swing. This is consistent with the
month-to-month delta scatter finding (large single-month confidence
swings aren't associated with the RBA's actual rate-change months); the
2022-23 decline was a grind, accumulated gradually, not a shock in the
same sense as COVID. A viewer scanning the heatmap for "what happened in
2022" could easily miss it, so this chart needs to be paired with the
shock-annotation timeline or explicit callout text, not shown alone, or
it risks implying nothing happened that year.

## Open questions / next steps

- Run the same rolling-correlation treatment against CPI and unemployment
  directly (confidence vs. CPI, confidence vs. unemployment) to see if
  they show similar regime-flipping behavior, or whether cash rate is
  unusual in this respect.
- The clearest single-event effect found anywhere in this analysis remains
  COVID's March-April 2020 confidence crash (visible in the recession
  overlay and the regime-comparison finding above); other discrete shocks
  of that scale (if any occurred in this window) may be worth identifying
  and testing individually, since they're likely to dominate any
  election/budget-level effect.
- Lag analysis (does confidence respond 1-3 months after a rate move) was
  considered but skipped for the same reason: a fixed lag/lead test would
  likely inherit the same "correlation reflects coincidence, not causation"
  pattern found here.
