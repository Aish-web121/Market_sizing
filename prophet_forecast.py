# ============================================
# TESLA EV MARKET — ML vs MANUAL COMPARISON
# ============================================

import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

# ============================================
# STEP 1 — LOAD DATASET (IEA FILE)
# ============================================

file_path = "EV Data Explorer 2025.xlsx"

df = pd.read_excel(file_path, engine="openpyxl")

print("\nColumns in dataset:")
print(df.columns)

# ============================================
# STEP 2 — CLEAN DATA
# ============================================

# Keep global EV data only
df = df[df["region_country"] == "World"]

# Keep EV only (BEV / EV)
df = df[df["powertrain"].astype(str).str.contains("EV", na=False)]

# OPTIONAL: filter only EV sales (if available)
if "parameter" in df.columns:
    df = df[df["parameter"].astype(str).str.contains("sales", case=False, na=False)]

# Select required columns
df = df[["year", "value"]]

# Remove missing values
df = df.dropna()

# Rename for Prophet
df = df.rename(columns={"year": "ds", "value": "y"})

# Convert year to datetime
df["ds"] = pd.to_datetime(df["ds"], format="%Y")

# Sort data
df = df.sort_values("ds")

print("\nCleaned Data:")
print(df.head())

# ============================================
# STEP 3 — TRAIN ML MODEL
# ============================================

model = Prophet(
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=False
)

model.fit(df)

print("\nModel training complete")

# ============================================
# STEP 4 — FORECAST (2025–2030)
# ============================================

future = model.make_future_dataframe(periods=6, freq='Y')

forecast = model.predict(future)

forecast_df = forecast[["ds", "yhat"]].copy()
forecast_df["Year"] = forecast_df["ds"].dt.year
forecast_df = forecast_df[["Year", "yhat"]]

forecast_df = forecast_df.rename(columns={"yhat": "ML_Forecast"})

print("\nML Forecast:")
print(forecast_df.tail())

# ============================================
# STEP 5 — MANUAL PROJECTIONS (YOUR EXCEL)
# ============================================

manual_df = pd.DataFrame({
    "Year": [2024,2025,2026,2027,2028,2029,2030],
    "Bear": [9900000,11385000,13092750,15056662,17315161,19912436,22899301],
    "Base": [9900000,11880000,14256000,17107200,20528640,24634368,29561241],
    "Bull": [9900000,12672000,16220160,20761804,26575110,34016140,43540660]
})

# ============================================
# STEP 6 — ALIGN BASE YEAR (IMPORTANT FIX)
# ============================================

ml_2024 = forecast_df[forecast_df["Year"] == 2024]["ML_Forecast"].values[0]
manual_2024 = manual_df[manual_df["Year"] == 2024]["Base"].values[0]

scale_factor = ml_2024 / manual_2024

manual_df["Bear"] *= scale_factor
manual_df["Base"] *= scale_factor
manual_df["Bull"] *= scale_factor

print("\nManual projections adjusted")

# ============================================
# STEP 7 — MERGE DATA
# ============================================

comparison = pd.merge(manual_df, forecast_df, on="Year")

# Calculate gaps
comparison["Gap_Base"] = comparison["ML_Forecast"] - comparison["Base"]
comparison["Gap_Bear"] = comparison["ML_Forecast"] - comparison["Bear"]
comparison["Gap_Bull"] = comparison["ML_Forecast"] - comparison["Bull"]

print("\nComparison Table:")
print(comparison)

# ============================================
# STEP 8 — SAVE RESULTS
# ============================================

comparison.to_csv("ml_vs_manual_comparison.csv", index=False)

print("\nSaved: ml_vs_manual_comparison.csv")

# ============================================
# STEP 9 — PLOT GRAPH
# ============================================

plt.figure()

plt.plot(comparison["Year"], comparison["ML_Forecast"], label="ML Forecast")
plt.plot(comparison["Year"], comparison["Base"], label="Manual Base")
plt.plot(comparison["Year"], comparison["Bear"], label="Manual Bear")
plt.plot(comparison["Year"], comparison["Bull"], label="Manual Bull")

plt.xlabel("Year")
plt.ylabel("EV Market Units")
plt.title("ML vs Manual Forecast Comparison")

plt.legend()

plt.show()

# ============================================
# DONE
# ============================================

print("\nProject Complete — ML vs Manual comparison ready")