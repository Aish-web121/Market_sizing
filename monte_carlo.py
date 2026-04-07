# ============================================
# TESLA MARKET SIZING — MONTE CARLO SIMULATION
# Phase 4: 10,000 scenarios, probability distribution
# ============================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

np.random.seed(42)   # makes results reproducible
N = 10_000           # number of simulations

print("=" * 55)
print("   MONTE CARLO SIMULATION — Tesla Revenue 2030")
print("=" * 55)
print(f"\n⏳ Running {N:,} simulations...")

# ---- STEP 1: Define uncertainty ranges ----
# Instead of 3 fixed scenarios, we sample randomly
# from realistic ranges for each variable

# Market growth: anywhere between Bear and Bull
market_growth = np.random.uniform(0.12, 0.28, N)

# Share change: Tesla could lose or gain share
share_change = np.random.uniform(-0.03, 0.03, N)

# Price change: price war to premium push
price_change = np.random.uniform(-0.03, 0.04, N)

# ---- STEP 2: Run all 10,000 projections ----

revenue_2024 = 75_147_492_000
years = 6  # 2024 to 2030

# Compound growth over 6 years
unit_growth_rate    = market_growth + share_change
revenue_growth_rate = unit_growth_rate + price_change

revenue_2030 = revenue_2024 * ((1 + revenue_growth_rate) ** years)
revenue_2030_B = revenue_2030 / 1e9   # convert to billions

print("✅ Simulations complete!\n")

# ---- STEP 3: Statistics ----

p10  = np.percentile(revenue_2030_B, 10)
p25  = np.percentile(revenue_2030_B, 25)
p50  = np.percentile(revenue_2030_B, 50)   # median
p75  = np.percentile(revenue_2030_B, 75)
p90  = np.percentile(revenue_2030_B, 90)
mean = np.mean(revenue_2030_B)

print("=" * 55)
print("   RESULTS — Tesla 2030 Revenue Distribution")
print("=" * 55)
print(f"  10th percentile  (very bad)  : ${p10:>8.1f}B")
print(f"  25th percentile  (bad)       : ${p25:>8.1f}B")
print(f"  50th percentile  (median)    : ${p50:>8.1f}B")
print(f"  Mean                         : ${mean:>8.1f}B")
print(f"  75th percentile  (good)      : ${p75:>8.1f}B")
print(f"  90th percentile  (very good) : ${p90:>8.1f}B")

# ---- STEP 4: Probability questions ----

prob_above_238 = np.mean(revenue_2030_B > 238) * 100   # base case
prob_above_138 = np.mean(revenue_2030_B > 138) * 100   # bear case
prob_above_100 = np.mean(revenue_2030_B > 100) * 100
prob_above_400 = np.mean(revenue_2030_B > 400) * 100   # bull-ish

print(f"\n  Probability of exceeding $100B  : {prob_above_100:.1f}%")
print(f"  Probability of exceeding $138B  : {prob_above_138:.1f}%  ← Bear case")
print(f"  Probability of exceeding $238B  : {prob_above_238:.1f}%  ← Base case")
print(f"  Probability of exceeding $400B  : {prob_above_400:.1f}%  ← Near Bull")

# ---- STEP 5: Compare to your 3 scenarios ----

print(f"\n{'=' * 55}")
print("   VALIDATION — Monte Carlo vs Your Scenarios")
print(f"{'=' * 55}")
print(f"  Your Bear case  : $138.6B  →  MC says {prob_above_138:.0f}% chance of beating this")
print(f"  Your Base case  : $238.2B  →  MC says {prob_above_238:.0f}% chance of beating this")
print(f"  MC Median       : ${p50:.1f}B  →  most likely single outcome")
print(f"  Prophet forecast: ~$XX B   →  (add manually from Phase 3)")

# ---- STEP 6: Save results ----

mc_results = pd.DataFrame({'Revenue_2030_B': revenue_2030_B})
mc_results.to_csv("monte_carlo_results.csv", index=False)
print(f"\n✅ Saved: monte_carlo_results.csv")
print(f"✅ Monte Carlo complete — ready for Streamlit dashboard")