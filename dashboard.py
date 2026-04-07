# ============================================
# TESLA EV MARKET — STREAMLIT DASHBOARD (PRO)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet

st.set_page_config(page_title="Tesla EV Market", layout="wide")

st.title("🚗 Tesla EV Market — ML + Scenario + Monte Carlo")
st.markdown("Machine Learning + Business Model + Probability Simulation")

# --------------------------------------------
# LOAD DATA
# --------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("EV Data Explorer 2025.xlsx", engine="openpyxl")

    df = df[df["region_country"] == "World"]
    df = df[df["powertrain"].astype(str).str.contains("EV", na=False)]

    if "parameter" in df.columns:
        df = df[df["parameter"].astype(str).str.contains("sales", case=False, na=False)]

    df = df[["year", "value"]].dropna()

    df = df.rename(columns={"year": "ds", "value": "y"})
    df["ds"] = pd.to_datetime(df["ds"], format="%Y")

    return df.sort_values("ds")

df = load_data()

# --------------------------------------------
# SIDEBAR
# --------------------------------------------
st.sidebar.header("⚙️ Model Controls")

bear_growth = st.sidebar.slider("Bear Growth (%)", 10, 25, 15) / 100
base_growth = st.sidebar.slider("Base Growth (%)", 15, 30, 20) / 100
bull_growth = st.sidebar.slider("Bull Growth (%)", 20, 40, 28) / 100

# --------------------------------------------
# ML MODEL
# --------------------------------------------
model = Prophet(
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=False
)

model.fit(df)

future = model.make_future_dataframe(periods=6, freq='YE')
forecast = model.predict(future)

ml_df = forecast[["ds", "yhat"]].copy()
ml_df["Year"] = ml_df["ds"].dt.year
ml_df = ml_df[["Year", "yhat"]]
ml_df.columns = ["Year", "ML_Forecast"]

# --------------------------------------------
# MANUAL MODEL
# --------------------------------------------
years = list(range(2024, 2031))

base_2024 = ml_df[ml_df["Year"] == 2024]["ML_Forecast"].values[0]

bear = [base_2024]
base = [base_2024]
bull = [base_2024]

for _ in range(6):
    bear.append(bear[-1] * (1 + bear_growth))
    base.append(base[-1] * (1 + base_growth))
    bull.append(bull[-1] * (1 + bull_growth))

manual_df = pd.DataFrame({
    "Year": years,
    "Bear": bear,
    "Base": base,
    "Bull": bull
})

comparison = pd.merge(manual_df, ml_df, on="Year")

# --------------------------------------------
# KPI
# --------------------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("2024 EV Market", f"{base_2024:,.0f}")
col2.metric("2030 ML Forecast", f"{comparison['ML_Forecast'].iloc[-1]:,.0f}")
col3.metric("2030 Base Model", f"{comparison['Base'].iloc[-1]:,.0f}")

# --------------------------------------------
# INTERACTIVE GRAPH
# --------------------------------------------
st.subheader("📈 Forecast Comparison")

fig = go.Figure()

fig.add_trace(go.Scatter(x=comparison["Year"], y=comparison["ML_Forecast"], mode="lines+markers", name="ML"))
fig.add_trace(go.Scatter(x=comparison["Year"], y=comparison["Base"], mode="lines+markers", name="Base"))
fig.add_trace(go.Scatter(x=comparison["Year"], y=comparison["Bear"], mode="lines+markers", name="Bear"))
fig.add_trace(go.Scatter(x=comparison["Year"], y=comparison["Bull"], mode="lines+markers", name="Bull"))

fig.update_layout(hovermode="x unified", height=450)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# MONTE CARLO SIMULATION
# --------------------------------------------
st.subheader("🎲 Monte Carlo Simulation (2030 Outcome)")

N = 10000

np.random.seed(42)

market_growth = np.random.uniform(bear_growth, bull_growth, N)
share_change = np.random.uniform(-0.03, 0.03, N)
price_change = np.random.uniform(-0.03, 0.04, N)

revenue_2024 = 75_147_492_000

growth_rate = market_growth + share_change + price_change

revenue_2030 = revenue_2024 * ((1 + growth_rate) ** 6)
revenue_2030_B = revenue_2030 / 1e9

# --------------------------------------------
# HISTOGRAM
# --------------------------------------------
fig2 = go.Figure()

fig2.add_trace(go.Histogram(
    x=revenue_2030_B,
    nbinsx=60,
    name="Simulations"
))

fig2.update_layout(
    xaxis_title="2030 Revenue ($B)",
    yaxis_title="Frequency",
    height=400
)

st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------
# PROBABILITIES
# --------------------------------------------
st.subheader("📊 Probability Insights")

prob_100 = np.mean(revenue_2030_B > 100) * 100
prob_200 = np.mean(revenue_2030_B > 200) * 100
prob_300 = np.mean(revenue_2030_B > 300) * 100

c1, c2, c3 = st.columns(3)

c1.metric("P(> $100B)", f"{prob_100:.1f}%")
c2.metric("P(> $200B)", f"{prob_200:.1f}%")
c3.metric("P(> $300B)", f"{prob_300:.1f}%")

# --------------------------------------------
# TABLE
# --------------------------------------------
st.subheader("📋 Data Table")
st.dataframe(comparison)

# --------------------------------------------
# END
# --------------------------------------------
st.markdown("---")
st.caption("ML (Prophet) + Scenario + Monte Carlo = Advanced Market Model")