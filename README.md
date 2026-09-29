# NYC 311: Does Neighborhood Income Affect Complaint Resolution Time?

## The Question

I wanted to know if NYC 311 complaints resolve at different speeds depending on the income level of the neighborhood — and if so, whether that pattern is consistent across complaint types or varies.

## Why This Matters

311 response time is a real measure of how city services actually reach residents. If certain neighborhoods systematically wait longer for the same complaint type, that's a resource allocation question worth surfacing — not just an academic one.

## Data Sources

- **NYC 311 Service Requests** — pulled via NYC Open Data's Socrata API (dataset `erm2-nwe9`), filtered to complaints created from 2022 onward
- **US Census ACS 5-Year Estimates** — median household income by ZIP Code Tabulation Area (ZCTA), pulled via the Census API

## Tools

Python, DuckDB, SQL (window functions, CTEs), pandas, scipy, Streamlit, Plotly

## Method

1. Loaded 311 complaint data into DuckDB and explored resolution times (time between `created_date` and `closed_date`) by complaint type
2. Found that **average** resolution time was heavily distorted by outliers in several categories, so I switched to **median** as the primary metric throughout
3. Verified the most extreme outliers manually (checked raw dates) to confirm they were genuine long-running cases, not data errors
4. Filtered out complaint types with fewer than 30 recorded cases, since smaller samples aren't reliable enough to compare
5. Pulled Census income data by ZCTA and joined it to the 311 data using ZIP code — 187 of 205 NYC ZIP codes matched (91%)
6. Split matched ZIP codes into four income quartiles (Q1 = lowest income, Q4 = highest income) using `NTILE(4)`
7. Compared median resolution time across quartiles, for the same complaint type
8. Validated the differences using the **Mann-Whitney U test** (chosen over a t-test because resolution times are heavily skewed, not normally distributed)

## Data Quality Issues I Found — and How I Handled Them

- **Outlier resolution times**: A handful of complaints (e.g., certain Unsanitary Condition cases) took hundreds of hours to resolve. I pulled the raw records and confirmed the dates were real, not data entry errors, so I kept them but reported median instead of mean to avoid distortion.
- **Unmatched ZIP codes (18 of 205)**: These turned out to be non-residential — single-building commercial ZIP codes (e.g., the Empire State Building, Rockefeller Center), airports (LaGuardia, JFK), and one clear placeholder value (`10000`). None represented a real residential population, so excluding them didn't bias the analysis.
- **Suppressed Census income data**: About 9% of ZCTAs nationwide have income values suppressed due to small sample sizes (Census placeholder `-666666666`). Filtered these out before joining.
- **Small-sample complaint types**: Filtered out anything with fewer than 30 total cases, and fewer than 10-30 cases per income quartile, to avoid drawing conclusions from noise.

## Findings

The relationship between income and resolution time is **not uniform** — it varies by complaint category, and in some cases reverses direction entirely.

**Routine sanitation and quality-of-life complaints resolve significantly slower in low-income neighborhoods:**
- Missed Collection: lowest-income quartile took roughly 5x longer than the highest-income quartile (p < 0.0001)
- Illegal Dumping: similarly large and statistically significant gap (p < 0.0001)
- Graffiti: a smaller but still significant gap (p = 0.016)

**Serious housing code violations show the opposite pattern — faster in low-income areas:**
- Water Leak complaints resolved significantly faster in the lowest-income quartile (p < 0.0001)
- Paint/Plaster violations followed the same pattern (p = 0.005)

My read: habitability violations like water leaks likely trigger mandatory inspection timelines (HPD code enforcement) regardless of neighborhood, and may occur more frequently in lower-income housing stock, keeping response crews more routinely deployed there. Quality-of-life complaints, on the other hand, may depend more on discretionary dispatch — and possibly on how much 311 call volume/political pressure a neighborhood generates per issue.

## What Didn't Hold Up

General Construction/Plumbing complaints showed a large raw difference between income quartiles (roughly -59%) — but when I ran the significance test, the p-value came back at 0.545, meaning this difference is statistically indistinguishable from random chance given the sample size. This was a useful check: without the significance test, I would have reported this as a real finding when it isn't.

## Limitations

- This is correlational, not causal — I haven't controlled for confounders like population density, borough, or seasonal effects (e.g., heat complaints cluster in winter)
- Single time period (2022 onward), single city — not a multi-year trend
- Income is measured at the ZIP/ZCTA level, which is a coarse proxy for actual household income within a neighborhood

## What I'd Do With More Time

- Control for population density and borough-level effects
- Look at trends over multiple years instead of a single snapshot
- Break resolution time down by season, since some complaint types (heat, plumbing) are likely seasonal

## Live Dashboard

[https://nyc311.streamlit.app/]

## Repository Structure

```
├── 01_load_data.py           # Pulls 311 data from NYC Open Data API
├── 02_load_income_data.py    # Pulls income data from Census API
├── 03_join_income.ipynb      # Joins datasets, builds income quartiles
├── 04_explore.ipynb          # Data exploration and quality checks
├── 05_sql_analysis.sql       # Core SQL queries
├── 06_statistical_tests.ipynb
├── dashboard/app.py          # Streamlit dashboard
├── nyc311.db                 # DuckDB database (pre-built, ready to query)
└── requirements.txt
```

