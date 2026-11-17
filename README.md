# RR SupeRR Selector — IPL 2027 Auction Intelligence

A data-driven cricket analytics project developed for **Unstop SupeRR Selector Season 2**. The project identifies reliable batters and bowlers under high-pressure situations to support Rajasthan Royals' IPL 2027 auction strategy.

## Project Objective

Evaluate player performance under pressure using ball-by-ball cricket data and rank the top 10 batters and top 10 bowlers.

## Dataset and Scope

- Analysis period: 2022–2026
- Formats: IPL and T20 Internationals (T20Is)
- Match situations: Second-innings run chases
- Analysis level: Ball-by-ball performance

Raw source datasets are not included in this repository.

## Pressure Identification

A delivery is classified as high pressure when either condition is satisfied:

1. Required run rate (RRR) is at least 12.
2. At least 6 wickets have already fallen and RRR is at least 9.

Required run rate is calculated before the current delivery:

`RRR = Runs Needed × 6 / Legal Balls Remaining`

Revised targets and revised legal-ball limits are used where available. Invalid or incomplete chase situations are excluded according to the project methodology.

## Player Eligibility

**Batters**
- At least 30 high-pressure balls across 5 matches.
- At least 30 normal-pressure balls across 5 matches.

**Bowlers**
- At least 60 high-pressure legal balls across 5 matches.
- At least 60 normal-pressure legal balls across 5 matches.
- At least one high-pressure wicket.

## Ranking Methodology

Eligible player metrics from IPL and T20I are aggregated by player. Rates are recalculated from the aggregated totals, and percentile-based scores are calculated across the combined eligible player pool.

### Batter score weights

| Metric | Weight |
|---|---:|
| High-pressure strike rate | 25% |
| High-pressure batting average | 15% |
| Strike-rate difference | 20% |
|
