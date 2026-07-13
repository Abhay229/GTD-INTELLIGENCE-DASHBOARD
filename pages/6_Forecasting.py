import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression

from utils.data_loader import load_data
from utils.theme import load_css, section_header, metric_card, style_fig, STEEL, AMBER, RED, GREEN

st.set_page_config(
    page_title="Forecasting",
    page_icon="📈",
    layout="wide"
)
load_css()

st.title("📈 Terrorism Attack Forecasting")

st.markdown("""
Forecast the future number of terrorist attacks using historical GTD data.
""")

df = load_data()

# ----------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------
st.sidebar.markdown("### 🎛️ Forecast Settings")

countries = sorted(df["country_txt"].dropna().unique())

country = st.sidebar.selectbox("Select Country", countries)

forecast_years = st.sidebar.slider("Forecast Years", 1, 10, 5)

# ----------------------------------------------------
# Prepare Data
# ----------------------------------------------------
country_df = df[df["country_txt"] == country]

yearly = (
    country_df
    .groupby("iyear")
    .size()
    .reset_index(name="Attacks")
)

yearly = yearly.sort_values("iyear")

if len(yearly) < 5:
    st.warning("Not enough historical data for forecasting.")
    st.stop()

# ----------------------------------------------------
# Train Linear Regression Model
# ----------------------------------------------------
X = yearly[["iyear"]]
y = yearly["Attacks"]

model = LinearRegression()
model.fit(X, y)

last_year = yearly["iyear"].max()

future_years = np.arange(last_year + 1, last_year + forecast_years + 1)

future_df = pd.DataFrame({"iyear": future_years})

predictions = model.predict(future_df)
predictions = np.maximum(predictions, 0)

forecast = pd.DataFrame({
    "Year": future_years,
    "Forecasted Attacks": predictions.astype(int)
})

# ----------------------------------------------------
# Historical + Forecast Plot — steel vs. amber dashed
# ----------------------------------------------------
section_header(f"Attack Forecast for {country}", "📈")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=yearly["iyear"], y=yearly["Attacks"],
    mode="lines+markers", name="Historical",
    line=dict(color=STEEL, width=2.5),
    marker=dict(size=6, color=STEEL),
))

fig.add_trace(go.Scatter(
    x=forecast["Year"], y=forecast["Forecasted Attacks"],
    mode="lines+markers", name="Forecast",
    line=dict(color=AMBER, width=2.5, dash="dash"),
    marker=dict(size=6, color=AMBER, symbol="diamond"),
))

# connector between last historical point and first forecast point
fig.add_trace(go.Scatter(
    x=[yearly["iyear"].iloc[-1], forecast["Year"].iloc[0]],
    y=[yearly["Attacks"].iloc[-1], forecast["Forecasted Attacks"].iloc[0]],
    mode="lines",
    line=dict(color=AMBER, width=2, dash="dot"),
    showlegend=False,
))

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Attacks",
)
fig = style_fig(fig, height=560)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

section_header("Forecast Results", "📋")
st.dataframe(
    forecast,
    use_container_width=True,
    column_config={
        "Year": st.column_config.NumberColumn("Year", format="%d"),
        "Forecasted Attacks": st.column_config.NumberColumn("Forecasted Attacks", format="%d"),
    },
)

# ----------------------------------------------------
# Growth Analysis — KPIs colored by risk direction
# ----------------------------------------------------
historical_last = yearly.iloc[-1]["Attacks"]
forecast_last = forecast.iloc[-1]["Forecasted Attacks"]

growth = ((forecast_last - historical_last) / max(historical_last, 1)) * 100

if growth < 0:
    risk_color = GREEN
elif growth < 15:
    risk_color = AMBER
else:
    risk_color = RED

section_header("Growth Analysis", "📊")

col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Current Attacks", int(historical_last), icon="📌", color=STEEL)
with col2:
    metric_card(f"Forecast ({forecast_years} Yrs)", int(forecast_last), icon="🔮", color=AMBER)
with col3:
    metric_card("Growth %", f"{growth:.2f}%", icon="📈", color=risk_color)

st.markdown("<br>", unsafe_allow_html=True)
section_header("Risk Assessment", "🧭")

if growth < 0:
    st.success("🟢 Threat Trend: Decreasing")
elif growth < 15:
    st.warning("🟡 Threat Trend: Stable")
else:
    st.error("🔴 Threat Trend: Increasing")

csv = forecast.to_csv(index=False)

st.download_button(
    label="📥 Download Forecast CSV",
    data=csv,
    file_name=f"{country}_forecast.csv",
    mime="text/csv"
)
