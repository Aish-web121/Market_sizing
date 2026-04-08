# ============================================
# TESLA MARKET SIZING — PROJECTION MODEL
# Phase 2: Bear / Base / Bull scenarios 2024-2030
# ============================================

import pandas as pd
import numpy as np

# ---- STEP 1: Starting values (from Phase 1) ----

start_year        = 2024
end_year          = 2030
years             = list(range(start_year, end_year + 1))

bev_market_2024   = 9_900_000       # full SAM (units)
tesla_units_2024  = 1_789_226       # actual deliveries
tesla_rev_2024    = 75_147_492_000  # deliveries × ASP

# ---- STEP 2: Scenario growth rates ----
# Source: IEA STEPS / APS / NZE scenarios

scenarios = {
    'Bear': {
        'market_growth' : 0.15,   # IEA STEPS
        'share_change'  : -0.05,  # BYD pressure
        'price_change'  : -0.02,  # price war
    },
    'Base': {
        'market_growth' : 0.20,   # IEA APS
        'share_change'  :  0.00,  # holds position
        'price_change'  :  0.01,  # modest inflation
    },
    'Bull': {
        'market_growth' : 0.28,   # IEA NZE
        'share_change'  :  0.02,  # new models/markets
        'price_change'  :  0.03,  # premium mix shift
    },
}

# ---- STEP 3: Build projection tables ----

results = {}   # we'll store all 3 scenarios here

for scenario_name, rates in scenarios.items():

    bev_market   = []
    tesla_units  = []
    tesla_rev    = []

    # Starting point — same for all scenarios
    bev_market.append(bev_market_2024)
    tesla_units.append(tesla_units_2024)
    tesla_rev.append(tesla_rev_2024)

    # Project year by year
    for i in range(1, len(years)):
        # Market grows at market_growth rate
        new_market = bev_market[-1] * (1 + rates['market_growth'])

        # Tesla grows at market_growth + share_change
        new_units = tesla_units[-1] * (1 + rates['market_growth'] + rates['share_change'])

        # Revenue = units growth × price change
        new_rev = tesla_rev[-1] * (1 + rates['market_growth'] + rates['share_change']) * (1 + rates['price_change'])

        bev_market.append(round(new_market))
        tesla_units.append(round(new_units))
        tesla_rev.append(round(new_rev))

    # Store in a neat DataFrame
    results[scenario_name] = pd.DataFrame({
        'Year'            : years,
        'BEV Market'      : bev_market,
        'Tesla Units'     : tesla_units,
        'Tesla Revenue'   : tesla_rev,
        'Market Share'    : [u/m for u, m in zip(tesla_units, bev_market)],
    })

# ---- STEP 4: Print results ----

print("=" * 65)
print("   TESLA PROJECTION MODEL — 2024 to 2030")
print("=" * 65)

for scenario_name, df in results.items():
    print(f"\n📊 {scenario_name.upper()} CASE")
    print("-" * 65)
    print(f"{'Year':<8} {'BEV Market':>14} {'Tesla Units':>14} {'Revenue ($B)':>14} {'Share':>8}")
    print("-" * 65)
    for _, row in df.iterrows():
        print(
            f"{int(row['Year']):<8}"
            f"{int(row['BEV Market']):>14,}"
            f"{int(row['Tesla Units']):>14,}"
            f"${row['Tesla Revenue']/1e9:>13.1f}"
            f"{row['Market Share']:>8.1%}"
        )

# ---- STEP 5: 2030 Summary ----

print("\n" + "=" * 65)
print("   2030 FORECAST SUMMARY")
print("=" * 65)
print(f"{'Metric':<30} {'Bear':>10} {'Base':>10} {'Bull':>10}")
print("-" * 65)

metrics = [
    ('BEV Market (units)', 'BEV Market', '{:,.0f}'),
    ('Tesla Deliveries',   'Tesla Units', '{:,.0f}'),
    ('Tesla Revenue ($B)', 'Tesla Revenue', '${:.1f}B'),
    ('Market Share',       'Market Share', '{:.1%}'),
]

for label, col, fmt in metrics:
    bear_val = results['Bear'].iloc[-1][col]
    base_val = results['Base'].iloc[-1][col]
    bull_val = results['Bull'].iloc[-1][col]

    if '$' in fmt:
        bear_str = fmt.format(bear_val / 1e9)
        base_str = fmt.format(base_val / 1e9)
        bull_str = fmt.format(bull_val / 1e9)
    else:
        bear_str = fmt.format(bear_val)
        base_str = fmt.format(base_val)
        bull_str = fmt.format(bull_val)

    print(f"{label:<30} {bear_str:>10} {base_str:>10} {bull_str:>10}")

print("\n✅ Projection model complete")

# ---- STEP 6: Save to CSV (we'll use this in later phases) ----

for name, df in results.items():
    df.to_csv(f"projections_{name.lower()}.csv", index=False)

print("✅ CSVs saved — projections_bear.csv / base.csv / bull.csv")