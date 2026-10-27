# ============================================
# TESLA EV MARKET — STREAMLIT DASHBOARD (CORRECTED)
# ============================================
# What changed vs. the earlier version:
#   1. Market and Tesla units are now projected SEPARATELY.
#      Market grows at market growth only; Tesla units grow at
#      market growth + share change (same logic as projections.py).
#      (Before, the "market" chart used Tesla's growth rate in Bear/Bull.)
#   2. Tesla share is now units / market, so it matches projections.py.
#   3. Tesla deliveries start from 1,789,226 (actual), not from 9.9M.
#   4. Monte Carlo is cached, and slider ranges can't be reversed.
#   5. Card captions and finding headlines react to the sliders
#      (before they were hardcoded text, e.g. "coin flip").
#   6. Hardcoded inputs moved into named constants at the top.
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Tesla EV Market Sizing", page_icon="🚗", layout="wide")

# ============================================
# CONSTANTS (all base-year inputs in one place)
# ============================================
YEARS = list(range(2024, 2031))
N_YEARS = len(YEARS) - 1                 # 6 years of compounding

SAM_2024 = 9_900_000                     # BEV sales: N. America + Europe + China (IEA)
TESLA_UNITS_2024 = 1_789_226             # Tesla deliveries (10-K)
TESLA_REV_2024 = 75_147_492_000          # deliveries x $42K ASP (automotive only)
TESLA_SHARE_2024 = TESLA_UNITS_2024 / SAM_2024   # = 18.07%

TAM_2024_M = 73.5                        # global car sales, millions (OICA)
BYD_SHARE_2024 = 17.0                    # approximate, public 2024 sales data

N_SIMS = 10_000
SEED = 42

COLORS = {"Bear": "red", "Base": "royalblue", "Bull": "green"}
DASH = {"Bear": "dash", "Base": "solid", "Bull": "dash"}

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
    color: #333;
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
st.markdown("**Bear / Base / Bull Scenarios · Monte Carlo Simulation · TAM / SAM / SOM**")
st.caption("Sources: IEA Global EV Data Explorer 2025 (2024 actuals) · Tesla 10-K · OICA 2024")
st.divider()

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("⚙️ Adjust Assumptions")
st.sidebar.markdown("Sliders update all charts live")
st.sidebar.caption(
    "**Share change** = how much slower (−) or faster (+) Tesla grows than the "
    "market each year, in percentage points. It is not a drop in market share "
    "of that many points."
)

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

st.sidebar.caption("Tip: set Bear share change to −2% to see the milder Bear case.")

# ============================================
# PROJECTIONS
# ============================================
def project_market(market_g):
    """Serviceable BEV market (units): grows at market growth only."""
    vals = [SAM_2024]
    for _ in range(N_YEARS):
        vals.append(vals[-1] * (1 + market_g))
    return vals


def project_tesla_units(market_g, share_g):
    """Tesla deliveries: grow at market growth + share change."""
    vals = [TESLA_UNITS_2024]
    for _ in range(N_YEARS):
        vals.append(vals[-1] * (1 + market_g + share_g))
    return vals


def project_revenue(market_g, share_g, price_g):
    """Tesla revenue: unit growth x price change."""
    vals = [TESLA_REV_2024]
    for _ in range(N_YEARS):
        vals.append(vals[-1] * (1 + market_g + share_g) * (1 + price_g))
    return vals


scenarios = {
    "Bear": dict(g=bear_growth, s=bear_share, p=bear_price),
    "Base": dict(g=base_growth, s=base_share, p=base_price),
    "Bull": dict(g=bull_growth, s=bull_share, p=bull_price),
}

proj = {}
for name, a in scenarios.items():
    market = project_market(a["g"])
    units = project_tesla_units(a["g"], a["s"])
    rev = project_revenue(a["g"], a["s"], a["p"])
    proj[name] = pd.DataFrame({
        "Year":   YEARS,
        "Market": market,
        "Units":  units,
        "Rev":    rev,
        "Share":  [u / m for u, m in zip(units, market)],
    })


def scenario_chart(column, divisor, y_title, hover, height, prefix="", suffix=""):
    """One line chart with Bear / Base / Bull."""
    fig = go.Figure()
    for name in ["Base", "Bear", "Bull"]:
        df = proj[name]
        fig.add_trace(go.Scatter(
            x=df["Year"], y=df[column] / divisor,
            name=f"{name} Case", mode="lines+markers",
            line=dict(color=COLORS[name], dash=DASH[name], width=3 if name == "Base" else 2),
            marker=dict(size=8 if name == "Base" else 7),
            hovertemplate=f"{name}: {prefix}%{{y:{hover}}}{suffix}<extra></extra>",
        ))
    fig.update_layout(
        xaxis_title="Year", yaxis_title=y_title,
        hovermode="x unified", height=height,
        legend=dict(orientation="h", y=1.12),
    )
    return fig


# ============================================
# KPI STRIP
# ============================================
st.subheader("📊 Key Metrics at a Glance")

base_2030 = proj["Base"].iloc[-1]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("TAM (Total Cars)",      "$2.65T", f"{TAM_2024_M:.1f}M units")
k2.metric("SAM (BEV, Tesla regions)", f"{SAM_2024/1e6:.1f}M", "units sold, 2024")
k3.metric("Tesla Deliveries 2024", f"{TESLA_UNITS_2024/1e6:.2f}M", f"{TESLA_SHARE_2024:.1%} share")
k4.metric("Tesla Revenue 2024",    f"${TESLA_REV_2024/1e9:.1f}B", "base year, vehicles only")
k5.metric("Base Case 2030 Tesla Units", f"{base_2030['Units']/1e6:.1f}M",
          f"market {base_2030['Market']/1e6:.1f}M")

st.divider()

# ============================================
# SECTION 1 — TAM / SAM / SOM
# ============================================
st.subheader("🌍 Section 1 — TAM / SAM / SOM Analysis")

st.markdown("##### 🥧 Competitor Market Share — 2024 Snapshot")
tesla_pct = round(TESLA_SHARE_2024 * 100, 1)
fig_pie = go.Figure(data=[go.Pie(
    labels=["Tesla", "BYD", "Rest of World"],
    values=[tesla_pct, BYD_SHARE_2024, round(100 - tesla_pct - BYD_SHARE_2024, 1)],
    hole=0.45,
    textinfo="label+percent",
    marker=dict(colors=["#E31937", "#1a1a2e", "#adb5bd"]),
)])
fig_pie.update_layout(height=350, margin=dict(t=20), showlegend=True)
st.plotly_chart(fig_pie)
st.caption("BYD share is approximate (public 2024 sales data).")

st.markdown("##### 🔋 SAM — BEV Market in Tesla's Regions (Bear / Base / Bull)")
st.plotly_chart(scenario_chart("Market", 1e6, "BEV Sales (Million Units)", ".2f", 380, suffix="M"))

st.markdown("##### 🚀 SOM — Tesla Share of the BEV Market (2024–2030)")
fig_som = go.Figure()
for name in ["Bear", "Base", "Bull"]:
    df = proj[name]
    fig_som.add_trace(go.Scatter(
        x=df["Year"], y=(df["Share"] * 100).round(2),
        name=f"{name} Case", mode="lines+markers",
        line=dict(color=COLORS[name], dash=DASH[name]), marker=dict(size=7),
        hovertemplate=f"{name} Share: %{{y:.1f}}%<extra></extra>",
    ))
fig_som.update_layout(xaxis_title="Year", yaxis_title="Tesla Market Share (%)",
                      hovermode="x unified", height=380, legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_som)
st.caption("Share = Tesla units ÷ market units, so it is an outcome of the growth gap, not an input.")

st.divider()

# ============================================
# SECTION 2 — SCENARIO COMPARISON
# ============================================
st.subheader("📈 Section 2 — Tesla Deliveries by Scenario")
st.caption("Tesla grows at market growth plus share change, so it can grow faster or slower than the market.")

st.plotly_chart(scenario_chart("Units", 1e6, "Tesla Deliveries (Millions)", ".2f", 480, suffix="M"))

st.markdown("##### 📋 Spread Table — How far apart are the scenarios each year?")
gap_df = pd.DataFrame({"Year": YEARS})
for name in ["Bear", "Base", "Bull"]:
    gap_df[name] = (proj[name]["Units"] / 1e6).round(2).astype(str) + "M"
gap_df["Bull vs Bear"] = ((proj["Bull"]["Units"] - proj["Bear"]["Units"]) / 1e6).round(2).astype(str) + "M"
st.dataframe(gap_df, hide_index=True)
st.caption("Bull vs Bear shows how wide the range of outcomes becomes by each year.")

st.divider()

# ============================================
# SECTION 3 — REVENUE PROJECTION
# ============================================
st.subheader("💰 Section 3 — Tesla Revenue Projection ($ Billions)")

fig2 = scenario_chart("Rev", 1e9, "Tesla Revenue (USD Billions)", ".1f", 420, prefix="$", suffix="B")
fig2.update_yaxes(tickprefix="$", ticksuffix="B")
st.plotly_chart(fig2)
st.caption("Vehicle revenue only (deliveries × average price). Total Tesla revenue also includes energy and services.")

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


@st.cache_data
def run_monte_carlo(g_lo, g_hi, s_lo, s_hi, p_lo, p_hi, seed=SEED, n=N_SIMS):
    """Each run draws ONE value per lever and holds it for all 6 years."""
    rs = np.random.RandomState(seed)
    mg = rs.uniform(g_lo, g_hi, n)
    sc = rs.uniform(s_lo, s_hi, n)
    pc = rs.uniform(p_lo, p_hi, n)
    rev = TESLA_REV_2024 * ((1 + mg + sc) ** N_YEARS) * ((1 + pc) ** N_YEARS)
    return mg, sc, pc, rev / 1e9


mg, sc, pc, rev_B = run_monte_carlo(
    min(bear_growth, bull_growth), max(bear_growth, bull_growth),
    min(bear_share,  bull_share),  max(bear_share,  bull_share),
    min(bear_price,  bull_price),  max(bear_price,  bull_price),
)

p10, p25, p50, p75, p90 = np.percentile(rev_B, [10, 25, 50, 75, 90])
mean = float(np.mean(rev_B))

bear_2030_rev = proj["Bear"]["Rev"].iloc[-1] / 1e9
base_2030_rev = proj["Base"]["Rev"].iloc[-1] / 1e9
bull_2030_rev = proj["Bull"]["Rev"].iloc[-1] / 1e9

prob_bear = float(np.mean(rev_B > bear_2030_rev) * 100)
prob_base = float(np.mean(rev_B > base_2030_rev) * 100)
prob_bull = float(np.mean(rev_B > bull_2030_rev) * 100)
prob_100  = float(np.mean(rev_B > 100) * 100)

fig3 = go.Figure()
fig3.add_trace(go.Histogram(x=rev_B, nbinsx=80, marker_color="royalblue",
                            opacity=0.75, name="10,000 Simulations"))
fig3.add_vline(x=p50, line_color="orange", line_dash="dash", line_width=2,
               annotation_text=f"Median ${p50:.0f}B", annotation_position="top right")
fig3.add_vline(x=bear_2030_rev, line_color="red", line_dash="dot", line_width=2,
               annotation_text=f"Bear ${bear_2030_rev:.0f}B", annotation_position="top left")
fig3.add_vline(x=base_2030_rev, line_color="green", line_dash="dot", line_width=2,
               annotation_text=f"Base ${base_2030_rev:.0f}B", annotation_position="top right")
fig3.update_layout(xaxis_title="Tesla 2030 Revenue ($ Billions)",
                   yaxis_title="Number of Simulations (out of 10,000)",
                   height=430, showlegend=False)
fig3.update_xaxes(tickprefix="$", ticksuffix="B")
st.plotly_chart(fig3)

st.markdown("##### 🗣️ What does this mean in plain English?")


def prob_card(col, prob, title, note, color):
    with col:
        st.markdown(f"""
        <div class="prob-card">
            <div class="prob-number {color}">{prob}</div>
            <div><b>{title}</b></div>
            <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">{note}</div>
        </div>""", unsafe_allow_html=True)


mc1, mc2, mc3, mc4 = st.columns(4)

prob_card(mc1, f"{prob_100:.0f}%", "chance Tesla exceeds $100B",
          "Very likely floor" if prob_100 > 90 else "Not a guaranteed floor",
          "green" if prob_100 > 80 else "orange")

prob_card(mc2, f"{prob_bear:.0f}%", f"chance Tesla beats Bear (${bear_2030_rev:.0f}B)",
          "Bear very likely beaten" if prob_bear > 90
          else ("Bear likely beaten" if prob_bear > 70 else "Bear is a real risk"),
          "green" if prob_bear > 70 else "orange")

if prob_base >= 70:
    base_note, base_color = "Base likely beaten", "green"
elif prob_base > 30:
    base_note, base_color = "Close to a coin flip", "orange"
else:
    base_note, base_color = "Base unlikely to be beaten", "red"
prob_card(mc3, f"{prob_base:.0f}%", f"chance Tesla beats Base (${base_2030_rev:.0f}B)",
          base_note, base_color)

prob_card(mc4, f"{prob_bull:.1f}%", f"chance Tesla beats Bull (${bull_2030_rev:.0f}B)",
          "Bull needs a catalyst" if prob_bull < 10 else "Bull is within reach",
          "red" if prob_bull < 10 else "orange")

st.markdown("##### 📊 Full Distribution — Revenue at each probability level")
perc_df = pd.DataFrame({
    "Percentile":    ["10th (Very Bad)", "25th (Bad)", "50th (Median)", "75th (Good)", "90th (Very Good)", "Mean"],
    "Tesla Revenue": [f"${p10:.1f}B", f"${p25:.1f}B", f"${p50:.1f}B", f"${p75:.1f}B", f"${p90:.1f}B", f"${mean:.1f}B"],
    "Plain English": [
        "Only 10% of scenarios end up worse than this",
        "A bad but plausible outcome",
        "Middle outcome: half of runs above, half below",
        "A good outcome, requires solid execution",
        "Only the top 10% of scenarios reach this",
        "Simple average across all 10,000 runs",
    ],
})
st.dataframe(perc_df, hide_index=True)
st.caption(f"80% of simulated outcomes fall between ${p10:.0f}B and ${p90:.0f}B.")

st.divider()

# ============================================
# SECTION 5 — KEY FINDINGS
# ============================================
st.subheader("💡 Section 5 — Key Findings")

st.markdown(f"""
<div class="finding-card">
    <h4>🎲 Finding 1 — Bear is beaten in {prob_bear:.0f}% of runs; Base in {prob_base:.0f}%</h4>
    <p>Across 10,000 Monte Carlo simulations, Tesla has a <b>{prob_bear:.0f}% probability</b>
    of exceeding Bear case revenue of <b>${bear_2030_rev:.0f}B</b> by 2030, but only a
    <b>{prob_base:.0f}% probability</b> of exceeding the Base case of
    <b>${base_2030_rev:.0f}B</b>. Whether Base is reached depends on whether Tesla
    can hold about {TESLA_SHARE_2024:.0%} share against BYD and legacy OEMs.</p>
</div>

<div class="finding-card">
    <h4>🚀 Finding 2 — Bull case requires a genuine catalyst</h4>
    <p>Only <b>{prob_bull:.1f}%</b> of simulations reach the Bull case
    (${bull_2030_rev:.0f}B). Narratively, that would need several wins at once,
    for example a lower-priced mass-market model, new-market growth and Tesla
    holding or growing share. These are qualitative stories behind the Bull
    inputs, not separate variables in the model.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================
# SECTION 6 — MODEL LIMITATIONS
# ============================================
st.subheader("⚠️ Section 6 — Model Limitations")

st.markdown("""
<div class="limit-card">
    <b>ASP assumptions are held constant per scenario</b> — real-world price changes are non-linear.
    A sudden price war acceleration (as seen 2022–2024) could compress Bear case revenue faster than modelled.
</div>
<div class="limit-card">
    <b>Growth rates are fixed per year</b> — real BEV adoption moves in uneven steps tied to
    model launches, subsidy cycles and supply constraints. In the Monte Carlo, each run draws
    one rate and holds it for all six years, so year-to-year volatility is not captured.
</div>
<div class="limit-card">
    <b>Monte Carlo assumes uniform, independent distributions</b> — in reality growth and price are
    correlated. A market downturn typically compresses both volume and price at once.
</div>
<div class="limit-card">
    <b>Scope and inputs</b> — revenue is vehicles only (not energy or services), the SAM uses one
    average price for all regions, and the TAM growth and BYD share are approximate, illustrative inputs.
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Built with IEA Global EV Data Explorer 2025 · Tesla 10-K · Monte Carlo Simulation · Streamlit")
