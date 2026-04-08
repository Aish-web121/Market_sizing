# ============================================
# TESLA MARKET SIZING — ML FORECAST
# Phase 3: Prophet — IEA Cars BEV data
# ============================================

import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go

# ---- STEP 1: Load IEA data — Cars only ----

df = pd.read_excel("EV Data Explorer 2025.xlsx", engine="openpyxl")

df_clean = df[
    (df["region_country"] == "World") &
    (df["powertrain"] == "BEV") &
    (df["parameter"] == "EV sales") &
    (df["category"] == "Historical") &
    (df["mode"] == "Cars")
][["year", "value"]].copy()

df_clean = df_clean.sort_values("year")
df_clean = df_clean[df_clean["year"] >= 2018]

df_clean = df_clean.rename(columns={"year": "ds", "value": "y"})
df_clean["ds"] = pd.to_datetime(df_clean["ds"], format="%Y")

print("=" * 55)
print("   IEA DATA — World BEV Car Sales (Historical)")
print("=" * 55)
print(df_clean.to_string(index=False))

# ---- STEP 2: Train Prophet ----

print("\n⏳ Training Prophet model...")

model = Prophet(
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=False,
    changepoint_prior_scale=0.3,
    interval_width=0.80,
)

model.fit(df_clean)
print("✅ Model trained!")

# ---- STEP 3: Forecast 2024–2030 ----

future = model.make_future_dataframe(periods=7, freq='YE')
forecast = model.predict(future)

forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
forecast_df["Year"] = forecast_df["ds"].dt.year
forecast_df = forecast_df[forecast_df["Year"] >= 2024][["Year", "yhat", "yhat_lower", "yhat_upper"]]
forecast_df = forecast_df.drop_duplicates(subset="Year")
forecast_df.columns = ["Year", "ML_Forecast", "Lower", "Upper"]

print("\n📊 Prophet Forecast (2024–2030):")
print("-" * 55)
print(f"{'Year':<8} {'Forecast':>12} {'Lower':>12} {'Upper':>12}")
print("-" * 55)
for _, row in forecast_df.iterrows():
    print(
        f"{int(row['Year']):<8}"
        f"{int(row['ML_Forecast']):>12,}"
        f"{int(row['Lower']):>12,}"
        f"{int(row['Upper']):>12,}"
    )

# ---- STEP 4: Compare vs your scenarios ----

manual_df = pd.DataFrame({
    "Year": [2024, 2025, 2026, 2027, 2028, 2029, 2030],
    "Bear": [9900000, 11385000, 13092750, 15056662, 17315161, 19912436, 22899301],
    "Base": [9900000, 11880000, 14256000, 17107200, 20528640, 24634368, 29561241],
    "Bull": [9900000, 12672000, 16220160, 20761804, 26575110, 34016140, 43540660],
})

comparison = pd.merge(manual_df, forecast_df[["Year", "ML_Forecast"]], on="Year")

prophet_2030 = int(comparison[comparison["Year"] == 2030]["ML_Forecast"].values[0])
bear_2030    = 22_899_301
base_2030    = 29_561_241
bull_2030    = 43_540_660

print("\n" + "=" * 55)
print("   MODEL VALIDATION — 2030 BEV Market (Units)")
print("=" * 55)
print(f"  Prophet ML forecast  : {prophet_2030:>12,}")
print(f"  Your Bear case       : {bear_2030:>12,}")
print(f"  Your Base case       : {base_2030:>12,}")
print(f"  Your Bull case       : {bull_2030:>12,}")

policy_impact = base_2030 - prophet_2030
print(f"\n  Policy Impact Analysis:")
print(f"  Prophet (no policy)  : {prophet_2030:>12,} units")
print(f"  Base case (IEA APS)  : {base_2030:>12,} units")
print(f"  Gap = value of policy: {policy_impact:>12,} units (~{policy_impact/1e6:.1f}M)")

if prophet_2030 < bear_2030:
    verdict = "⚠️  Prophet MORE pessimistic than Bear — policy drives all upside"
elif prophet_2030 < base_2030:
    verdict = "✅  Prophet lands between Bear and Base — model validated"
else:
    verdict = "✅  Prophet is optimistic — consistent with Base/Bull range"

print(f"\n  Verdict: {verdict}")

# ---- STEP 5: Save CSV ----

comparison.to_csv("ml_vs_manual_comparison.csv", index=False)
print("\n✅ Saved: ml_vs_manual_comparison.csv")

# ---- STEP 6: Interactive Plotly Chart ----

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["ML_Forecast"],
    name="ML Forecast (Prophet)", mode="lines+markers",
    line=dict(color="orange", width=3),
    marker=dict(size=8)
))
fig.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Base"],
    name="Base Case", mode="lines+markers",
    line=dict(color="royalblue", width=2),
    marker=dict(size=7)
))
fig.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bear"],
    name="Bear Case", mode="lines+markers",
    line=dict(color="red", width=2, dash="dash"),
    marker=dict(size=7)
))
fig.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bull"],
    name="Bull Case", mode="lines+markers",
    line=dict(color="green", width=2, dash="dash"),
    marker=dict(size=7)
))

fig.update_layout(
    title="Prophet ML Forecast vs Manual Scenarios — 2024–2030",
    xaxis_title="Year",
    yaxis_title="Global BEV Car Sales (Units)",
    legend=dict(orientation="h", y=1.1),
    hovermode="x unified",
    height=500
)
fig.update_yaxes(tickformat=",")

fig.write_html("ml_vs_manual_chart.html")
fig.show()
print("✅ Chart saved: ml_vs_manual_chart.html")