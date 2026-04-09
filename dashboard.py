# ============================================
# TESLA EV MARKET — STREAMLIT DASHBOARD (PRO)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet

st.set_page_config(page_title="Tesla EV Market Sizing", page_icon="🚗", layout="wide")

# ============================================
# STYLING
# ============================================
st.markdown("""
<style>
.big-title { font-size: 2.2rem; font-weight: 800; color: #E31937; }
.finding-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: white;
    padding: 1.2rem;
    border-radius: 12px;
    border-left: 5px solid #E31937;
    margin-bottom: 0.8rem;
}
.finding-card h4 { color: #f5a623; margin: 0 0 0.4rem 0; }
.finding-card p  { margin: 0; font-size: 0.9rem; line-height: 1.5; color: #ccc; }
.prob-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    border: 2px solid #dee2e6;
}
.prob-number { font-size: 2rem; font-weight: 800; }
.green  { color: #28a745; }
.orange { color: #fd7e14; }
.red    { color: #dc3545; }
.limit-card {
    background: #fff8e1;
    border-left: 5px solid #f5a623;
    padding: 1rem 1.2rem;
    border-radius: 8px;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown('<p class="big-title">🚗 Tesla EV Market Sizing — 2024 to 2030</p>', unsafe_allow_html=True)
st.markdown("**ML Forecast · Bear / Base / Bull Scenarios · Monte Carlo Simulation · TAM / SAM / SOM**")
st.caption("Sources: IEA Global EV Outlook 2025 · Tesla 10-K · OICA 2024")
st.divider()

# ============================================
# LOAD & TRAIN PROPHET
# ============================================
@st.cache_data
def load_and_forecast():
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

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.3,
        interval_width=0.80,
    )
    model.fit(df_clean)

    future = model.make_future_dataframe(periods=7, freq='YE')
    forecast = model.predict(future)

    forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    forecast_df["Year"] = forecast_df["ds"].dt.year
    forecast_df = forecast_df[forecast_df["Year"] >= 2024]
    forecast_df = forecast_df.drop_duplicates(subset="Year")
    forecast_df.columns = ["ds", "ML_Forecast", "ML_Lower", "ML_Upper", "Year"]

    return forecast_df[["Year", "ML_Forecast", "ML_Lower", "ML_Upper"]]

ml_df = load_and_forecast()

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("⚙️ Adjust Assumptions")
st.sidebar.markdown("Sliders update all charts live")

bear_growth = st.sidebar.slider("Bear Market Growth %",  5,  25, 15) / 100
base_growth = st.sidebar.slider("Base Market Growth %", 10,  30, 20) / 100
bull_growth = st.sidebar.slider("Bull Market Growth %", 15,  40, 28) / 100

st.sidebar.divider()

bear_share = st.sidebar.slider("Bear Tesla Share Change %", -5,  0, -5) / 100
base_share = st.sidebar.slider("Base Tesla Share Change %", -2,  2,  0) / 100
bull_share = st.sidebar.slider("Bull Tesla Share Change %",  0,  5,  2) / 100

st.sidebar.divider()

bear_price = st.sidebar.slider("Bear Price Change %", -5,  0, -2) / 100
base_price = st.sidebar.slider("Base Price Change %", -1,  3,  1) / 100
bull_price = st.sidebar.slider("Bull Price Change %",  0,  6,  3) / 100

# ============================================
# PROJECTIONS
# ============================================
years = list(range(2024, 2031))

def project_units(market_g, share_g):
    vals = [9_900_000]
    for _ in range(6):
        vals.append(round(vals[-1] * (1 + market_g + share_g)))
    return vals

def project_revenue(market_g, share_g, price_g):
    vals = [75_147_492_000]
    for _ in range(6):
        vals.append(vals[-1] * (1 + market_g + share_g) * (1 + price_g))
    return vals

bear_units = project_units(bear_growth, bear_share)
base_units = project_units(base_growth, base_share)
bull_units = project_units(bull_growth, bull_share)

bear_rev = project_revenue(bear_growth, bear_share, bear_price)
base_rev = project_revenue(base_growth, base_share, base_price)
bull_rev = project_revenue(bull_growth, bull_share, bull_price)

manual_df = pd.DataFrame({
    "Year":       years,
    "Bear_Units": bear_units,
    "Base_Units": base_units,
    "Bull_Units": bull_units,
    "Bear_Rev":   [r/1e9 for r in bear_rev],
    "Base_Rev":   [r/1e9 for r in base_rev],
    "Bull_Rev":   [r/1e9 for r in bull_rev],
})

comparison = pd.merge(manual_df, ml_df, on="Year")

# ============================================
# KPI STRIP
# ============================================
st.subheader("📊 Key Metrics at a Glance")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("TAM (Total Cars)",      "$2.65T",  "73.5M units")
k2.metric("SAM (Global BEV 2024)", "9.9M",    "units sold")
k3.metric("Tesla Deliveries 2024", "1.79M",   "18.1% share")
k4.metric("Tesla Revenue 2024",    "$75.1B",  "base year")
k5.metric("ML Forecast 2030",      f"{int(comparison['ML_Forecast'].iloc[-1]/1e6):.0f}M", "units (Prophet)")

st.divider()

# ============================================
# SECTION 1 — TAM / SAM / SOM
# ============================================
st.subheader("🌍 Section 1 — TAM / SAM / SOM Analysis")

col_t, col_s = st.columns(2)

with col_t:
    st.markdown("##### 🚘 TAM — Global Total Car Market")
    tam_values = [73.5, 74.2, 75.0, 75.8, 76.5, 77.3, 78.0]
    fig_tam = go.Figure()
    fig_tam.add_trace(go.Bar(
        x=years, y=tam_values,
        marker_color="steelblue",
        hovertemplate="TAM: %{y}M units<extra></extra>"
    ))
    fig_tam.update_layout(
        xaxis_title="Year", yaxis_title="Million Units",
        height=350, margin=dict(t=20)
    )
    st.plotly_chart(fig_tam, use_container_width=True)

with col_s:
    st.markdown("##### 🥧 Competitor Market Share — 2024 Snapshot")
    fig_pie = go.Figure(data=[go.Pie(
        labels=["Tesla", "BYD", "Rest of World"],
        values=[18.1, 17.0, 64.9],
        hole=0.45,
        textinfo="label+percent",
        marker=dict(colors=["#E31937", "#1a1a2e", "#adb5bd"])
    )])
    fig_pie.update_layout(height=350, margin=dict(t=20), showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("##### 🔋 SAM — Global BEV Market (Historical + ML Forecast)")

fig_sam = go.Figure()
fig_sam.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["ML_Forecast"]/1e6,
    name="ML Forecast (Prophet)", mode="lines+markers",
    line=dict(color="orange", width=3), marker=dict(size=8),
    hovertemplate="ML Forecast: %{y:.2f}M<extra></extra>"
))
fig_sam.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Base_Units"]/1e6,
    name="Base Case", mode="lines+markers",
    line=dict(color="royalblue", width=2), marker=dict(size=7),
    hovertemplate="Base: %{y:.2f}M<extra></extra>"
))
fig_sam.update_layout(
    xaxis_title="Year", yaxis_title="BEV Sales (Million Units)",
    hovermode="x unified", height=380, legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig_sam, use_container_width=True)

st.markdown("##### 🚀 SOM — Tesla Share of BEV Market (2024–2030)")

tesla_start_share = 0.181

def project_share(change):
    shares = [tesla_start_share]
    for _ in range(6):
        shares.append(shares[-1] * (1 + change))
    return [round(s * 100, 2) for s in shares]

bear_som = project_share(bear_share)
base_som = project_share(base_share)
bull_som = project_share(bull_share)

fig_som = go.Figure()
fig_som.add_trace(go.Scatter(x=years, y=bear_som, name="Bear Case",
    mode="lines+markers", line=dict(color="red", dash="dash"), marker=dict(size=7),
    hovertemplate="Bear Share: %{y:.1f}%<extra></extra>"))
fig_som.add_trace(go.Scatter(x=years, y=base_som, name="Base Case",
    mode="lines+markers", line=dict(color="royalblue", width=2), marker=dict(size=7),
    hovertemplate="Base Share: %{y:.1f}%<extra></extra>"))
fig_som.add_trace(go.Scatter(x=years, y=bull_som, name="Bull Case",
    mode="lines+markers", line=dict(color="green", dash="dash"), marker=dict(size=7),
    hovertemplate="Bull Share: %{y:.1f}%<extra></extra>"))
fig_som.update_layout(
    xaxis_title="Year", yaxis_title="Tesla Market Share (%)",
    hovermode="x unified", height=380, legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig_som, use_container_width=True)

st.divider()

# ============================================
# SECTION 2 — SCENARIO vs ML COMPARISON
# ============================================
st.subheader("📈 Section 2 — Bear / Base / Bull vs ML Forecast (Units)")
st.caption("How do policy-driven scenarios compare to what pure historical data predicts?")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=list(comparison["Year"]) + list(comparison["Year"])[::-1],
    y=list(comparison["ML_Upper"]/1e6) + list(comparison["ML_Lower"]/1e6)[::-1],
    fill='toself', fillcolor='rgba(255,165,0,0.12)',
    line=dict(color='rgba(255,255,255,0)'),
    name="ML 80% Confidence Band", hoverinfo="skip"
))
fig1.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["ML_Forecast"]/1e6,
    name="ML Forecast (Prophet)", mode="lines+markers",
    line=dict(color="orange", width=3), marker=dict(size=9),
    hovertemplate="ML: %{y:.2f}M units<extra></extra>"
))
fig1.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Base_Units"]/1e6,
    name="Base Case", mode="lines+markers",
    line=dict(color="royalblue", width=2), marker=dict(size=7),
    hovertemplate="Base: %{y:.2f}M units<extra></extra>"
))
fig1.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bear_Units"]/1e6,
    name="Bear Case", mode="lines+markers",
    line=dict(color="red", width=2, dash="dash"), marker=dict(size=7),
    hovertemplate="Bear: %{y:.2f}M units<extra></extra>"
))
fig1.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bull_Units"]/1e6,
    name="Bull Case", mode="lines+markers",
    line=dict(color="green", width=2, dash="dash"), marker=dict(size=7),
    hovertemplate="Bull: %{y:.2f}M units<extra></extra>"
))

fig1.update_layout(
    xaxis_title="Year", yaxis_title="Global BEV Car Sales (Millions)",
    legend=dict(orientation="h", y=1.12),
    hovermode="x unified", height=480
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("##### 📋 Gap Table — How far ahead/behind are scenarios vs ML each year?")
gap_df = pd.DataFrame({"Year": comparison["Year"]})
gap_df["ML Forecast"] = (comparison["ML_Forecast"]/1e6).round(2).astype(str) + "M"
gap_df["Bear vs ML"]  = ((comparison["Bear_Units"] - comparison["ML_Forecast"])/1e6).round(2).astype(str) + "M"
gap_df["Base vs ML"]  = ((comparison["Base_Units"] - comparison["ML_Forecast"])/1e6).round(2).astype(str) + "M"
gap_df["Bull vs ML"]  = ((comparison["Bull_Units"] - comparison["ML_Forecast"])/1e6).round(2).astype(str) + "M"
st.dataframe(gap_df, use_container_width=True, hide_index=True)
st.caption("Positive = scenario more optimistic than ML. Negative = ML more optimistic than scenario.")

st.divider()

# ============================================
# SECTION 3 — REVENUE PROJECTION
# ============================================
st.subheader("💰 Section 3 — Tesla Revenue Projection ($ Billions)")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Base_Rev"],
    name="Base Case", mode="lines+markers",
    line=dict(color="royalblue", width=3), marker=dict(size=8),
    hovertemplate="Base: $%{y:.1f}B<extra></extra>"
))
fig2.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bear_Rev"],
    name="Bear Case", mode="lines+markers",
    line=dict(color="red", width=2, dash="dash"), marker=dict(size=7),
    hovertemplate="Bear: $%{y:.1f}B<extra></extra>"
))
fig2.add_trace(go.Scatter(
    x=comparison["Year"], y=comparison["Bull_Rev"],
    name="Bull Case", mode="lines+markers",
    line=dict(color="green", width=2, dash="dash"), marker=dict(size=7),
    hovertemplate="Bull: $%{y:.1f}B<extra></extra>"
))
fig2.update_layout(
    xaxis_title="Year", yaxis_title="Tesla Revenue (USD Billions)",
    legend=dict(orientation="h", y=1.12),
    hovermode="x unified", height=420
)
fig2.update_yaxes(tickprefix="$", ticksuffix="B")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================================
# SECTION 4 — MONTE CARLO
# ============================================
st.subheader("🎲 Section 4 — Monte Carlo Simulation (10,000 Scenarios)")
st.markdown("""
> **What is Monte Carlo?** Instead of picking just 3 scenarios (Bear/Base/Bull),
> we run **10,000 random combinations** of growth rate, market share, and pricing —
> and ask: *what does the distribution of outcomes look like?*
> This tells us not just what might happen, but **how likely** each outcome is.
""")

np.random.seed(42)
N = 10_000

mg = np.random.uniform(bear_growth, bull_growth, N)
sc = np.random.uniform(bear_share,  bull_share,  N)
pc = np.random.uniform(bear_price,  bull_price,  N)

revenue_2030 = 75_147_492_000 * ((1 + mg + sc) ** 6) * ((1 + pc) ** 6)
rev_B = revenue_2030 / 1e9

p10  = np.percentile(rev_B, 10)
p25  = np.percentile(rev_B, 25)
p50  = np.percentile(rev_B, 50)
p75  = np.percentile(rev_B, 75)
p90  = np.percentile(rev_B, 90)
mean = np.mean(rev_B)

bear_2030_rev = bear_rev[-1] / 1e9
base_2030_rev = base_rev[-1] / 1e9
bull_2030_rev = bull_rev[-1] / 1e9

prob_bear = np.mean(rev_B > bear_2030_rev) * 100
prob_base = np.mean(rev_B > base_2030_rev) * 100
prob_bull = np.mean(rev_B > bull_2030_rev) * 100
prob_100  = np.mean(rev_B > 100) * 100

fig3 = go.Figure()
fig3.add_trace(go.Histogram(
    x=rev_B, nbinsx=80,
    marker_color="royalblue", opacity=0.75,
    name="10,000 Simulations"
))
fig3.add_vline(x=p50,           line_color="orange", line_dash="dash", line_width=2,
               annotation_text=f"Median ${p50:.0f}B", annotation_position="top right")
fig3.add_vline(x=bear_2030_rev, line_color="red",    line_dash="dot",  line_width=2,
               annotation_text=f"Bear ${bear_2030_rev:.0f}B", annotation_position="top left")
fig3.add_vline(x=base_2030_rev, line_color="green",  line_dash="dot",  line_width=2,
               annotation_text=f"Base ${base_2030_rev:.0f}B", annotation_position="top right")
fig3.update_layout(
    xaxis_title="Tesla 2030 Revenue ($ Billions)",
    yaxis_title="Number of Simulations (out of 10,000)",
    height=430, showlegend=False
)
fig3.update_xaxes(tickprefix="$", ticksuffix="B")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("##### 🗣️ What does this mean in plain English?")

mc1, mc2, mc3, mc4 = st.columns(4)

with mc1:
    color = "green" if prob_100 > 80 else "orange"
    st.markdown(f"""
    <div class="prob-card">
        <div class="prob-number {color}">{prob_100:.0f}%</div>
        <div><b>chance Tesla exceeds $100B</b></div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">Almost guaranteed floor</div>
    </div>""", unsafe_allow_html=True)

with mc2:
    color = "green" if prob_bear > 70 else "orange"
    st.markdown(f"""
    <div class="prob-card">
        <div class="prob-number {color}">{prob_bear:.0f}%</div>
        <div><b>chance Tesla beats Bear (${bear_2030_rev:.0f}B)</b></div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">Bear case nearly certain</div>
    </div>""", unsafe_allow_html=True)

with mc3:
    color = "orange" if 30 < prob_base < 70 else ("green" if prob_base >= 70 else "red")
    st.markdown(f"""
    <div class="prob-card">
        <div class="prob-number {color}">{prob_base:.0f}%</div>
        <div><b>chance Tesla beats Base (${base_2030_rev:.0f}B)</b></div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">Base case = coin flip</div>
    </div>""", unsafe_allow_html=True)

with mc4:
    color = "red" if prob_bull < 10 else "orange"
    st.markdown(f"""
    <div class="prob-card">
        <div class="prob-number {color}">{prob_bull:.0f}%</div>
        <div><b>chance Tesla beats Bull (${bull_2030_rev:.0f}B)</b></div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">Bull needs a catalyst</div>
    </div>""", unsafe_allow_html=True)

st.markdown("##### 📊 Full Distribution — Revenue at each probability level")
perc_df = pd.DataFrame({
    "Percentile":    ["10th (Very Bad)", "25th (Bad)", "50th (Median)", "75th (Good)", "90th (Very Good)", "Mean"],
    "Tesla Revenue": [f"${p10:.1f}B", f"${p25:.1f}B", f"${p50:.1f}B", f"${p75:.1f}B", f"${p90:.1f}B", f"${mean:.1f}B"],
    "Plain English": [
        "Only 10% of scenarios end up worse than this",
        "A bad but plausible outcome",
        "The most likely single outcome",
        "A good outcome — requires solid execution",
        "Only happens in top 10% of scenarios",
        "Simple average across all 10,000 runs"
    ]
})
st.dataframe(perc_df, use_container_width=True, hide_index=True)

st.divider()

# ============================================
# SECTION 5 — KEY FINDINGS
# ============================================
st.subheader("💡 Section 5 — Key Findings")

prophet_2030 = int(comparison["ML_Forecast"].iloc[-1])
policy_gap   = int(base_units[-1] - prophet_2030)

st.markdown(f"""
<div class="finding-card">
    <h4>🔍 Finding 1 — The ML model is more pessimistic than even the Bear case</h4>
    <p>Prophet, trained purely on IEA historical data with zero knowledge of government policies,
    forecasts <b>{prophet_2030/1e6:.1f}M BEV units</b> by 2030 —
    below even our Bear case of <b>{bear_units[-1]/1e6:.1f}M units</b>.
    Reason: Prophet detects EV growth <b>decelerating</b> from 86% in 2021–22
    down to ~16% in 2023–24 and assumes that trend continues.</p>
</div>

<div class="finding-card">
    <h4>📜 Finding 2 — {policy_gap/1e6:.1f}M units = the measurable value of global EV policy</h4>
    <p>The gap between Prophet's no-policy forecast (<b>{prophet_2030/1e6:.1f}M</b>) and
    our Base case (<b>{base_units[-1]/1e6:.1f}M</b>) is <b>{policy_gap/1e6:.1f}M units</b>.
    Our Base case uses IEA's APS scenario which assumes all government EV pledges are fulfilled.
    That difference is literally what policy adds to Tesla's addressable market.</p>
</div>

<div class="finding-card">
    <h4>🎲 Finding 3 — Bear case is almost certain. Base case is a coin flip.</h4>
    <p>Across 10,000 Monte Carlo simulations, Tesla has a <b>{prob_bear:.0f}% probability</b>
    of exceeding Bear case revenue of <b>${bear_2030_rev:.0f}B</b> by 2030.
    But only a <b>{prob_base:.0f}% probability</b> of exceeding the Base case of
    <b>${base_2030_rev:.0f}B</b> — a genuine coin flip depending on whether Tesla
    can defend 18% market share against BYD and legacy OEMs.</p>
</div>

<div class="finding-card">
    <h4>🚀 Finding 4 — Bull case requires a genuine catalyst</h4>
    <p>Only <b>{prob_bull:.1f}%</b> of Monte Carlo simulations reach Bull case territory
    (${bull_2030_rev:.0f}B). The Bull case requires simultaneous wins:
    a sub-$30K mass market model, major emerging market penetration (India / SE Asia),
    and Tesla maintaining or growing its global market share against intensifying competition.</p>
</div>

<div class="finding-card">
    <h4>📉 Finding 5 — BEV market share battle is the biggest risk</h4>
    <p>In 2024, Tesla held <b>18.1%</b> of the global BEV car market while BYD held <b>17.0%</b> —
    a gap of just 1.1 percentage points. The Bear case assumes Tesla loses share every year.
    Even a 5% annual share decline compounds to a dramatically smaller revenue outcome by 2030,
    independent of overall market growth.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================
# SECTION 6 — MODEL LIMITATIONS
# ============================================
st.subheader("⚠️ Section 6 — Model Limitations")

st.markdown("""
<div class="limit-card">
    <b>Prophet has no policy awareness</b> — trained purely on historical IEA data.
    It cannot account for new government EV mandates, subsidy changes, or sudden policy reversals.
</div>
<div class="limit-card">
    <b>ASP assumptions are held constant per scenario</b> — real-world price changes are non-linear.
    A sudden price war acceleration (as seen 2022–2024) could compress Bear case revenue faster than modelled.
</div>
<div class="limit-card">
    <b>Limited ML training data</b> — only 7 annual data points (2018–2024).
    Prophet confidence intervals should be treated as directional, not statistically precise.
</div>
<div class="limit-card">
    <b>Monte Carlo assumes uniform distributions</b> — in reality, growth rates and price changes
    are correlated. A market downturn typically compresses both volume and price simultaneously,
    which this model treats as independent variables.
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Built with IEA Global EV Outlook 2025 · Tesla 10-K · Prophet ML · Monte Carlo Simulation · Streamlit")
