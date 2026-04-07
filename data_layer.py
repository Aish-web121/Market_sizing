# ============================================
# TESLA MARKET SIZING — DATA LAYER
# Phase 1: Load and verify our assumptions
# ============================================

import pandas as pd

# ---- STEP 1: Define all our assumptions ----
# These are the exact same numbers from your Excel file

assumptions = {

    # Section 1 — Global Auto Market
    'total_cars_sold'        : 73_500_000,      # OICA 2024
    'avg_car_price'          : 36_000,           # Statista
    'total_car_market_value' : 2_646_000_000_000, # Calculated

    # Section 2 — EV Adoption
    'global_bev_sales'       : 11_000_000,       # IEA 2025
    'ev_market_share'        : 0.22,             # IEA 2025
    'avg_ev_price_global'    : 33_000,           # IEA 2025
    'avg_ev_price_premium'   : 43_000,           # EV-Volumes

    # Section 3 — Tesla Specifics
    'tesla_deliveries'       : 1_789_226,        # Tesla 10-K
    'tesla_avg_price'        : 42_000,           # Tesla 10-K
    'tesla_revenue'          : 97_690_000_000,   # Tesla 10-K

    # Section 4 — Geography
    'bev_north_america'      : 1_300_000,        # IEA 2025
    'bev_europe'             : 2_200_000,        # IEA 2025
    'bev_china'              : 6_400_000,        # IEA 2025

}

# ---- STEP 2: Calculate TAM / SAM / SOM ----

TAM_units = assumptions['total_cars_sold']
TAM_value = assumptions['total_cars_sold'] * assumptions['avg_car_price']

SAM_core_units = assumptions['bev_north_america'] + assumptions['bev_europe']
SAM_full_units = SAM_core_units + assumptions['bev_china']

SAM_core_value = SAM_core_units * assumptions['avg_ev_price_premium']
SAM_full_value = SAM_full_units * assumptions['avg_ev_price_premium']

SOM_units = assumptions['tesla_deliveries']
SOM_value = assumptions['tesla_deliveries'] * assumptions['tesla_avg_price']

tesla_share_core = SOM_units / SAM_core_units
tesla_share_full = SOM_units / SAM_full_units

# ---- STEP 3: Print results ----

print("=" * 50)
print("   TESLA MARKET SIZING — 2024 BASE YEAR")
print("=" * 50)

print(f"\n📊 TAM — Total Addressable Market")
print(f"   Units : {TAM_units:,} cars")
print(f"   Value : ${TAM_value:,.0f}")

print(f"\n📊 SAM — Serviceable Addressable Market")
print(f"   Core units (ex-China) : {SAM_core_units:,} BEVs")
print(f"   Core value            : ${SAM_core_value:,.0f}")
print(f"   Full units (w/ China) : {SAM_full_units:,} BEVs")
print(f"   Full value            : ${SAM_full_value:,.0f}")

print(f"\n📊 SOM — Serviceable Obtainable Market")
print(f"   Tesla deliveries : {SOM_units:,} cars")
print(f"   Tesla revenue    : ${SOM_value:,.0f}")

print(f"\n📊 Tesla Market Share")
print(f"   Share of core SAM : {tesla_share_core:.1%}")
print(f"   Share of full SAM : {tesla_share_full:.1%}")

print("\n" + "=" * 50)
print("✅ Data layer complete")
print("=" * 50)