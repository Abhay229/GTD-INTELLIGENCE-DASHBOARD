import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.theme import load_css, section_header, metric_card, style_fig, CYAN, AMBER, RED, GREEN

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
load_css()

st.title("🏠 Command Center")
st.caption("Real-time overview of global terrorism incidents from the GTD dataset.")

df = load_data()

# -----------------------------
# KPI row (same underlying values as before, restyled to SOC palette)
# -----------------------------
section_header("Dashboard Summary", "◈")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Incidents", f"{len(df):,}", icon="💥", color=CYAN)
with c2:
    metric_card("Fatalities", f"{int(df['nkill'].sum()):,}", icon="☠️", color=RED)
with c3:
    metric_card("Injured", f"{int(df['nwound'].sum()):,}", icon="🏥", color=AMBER)
with c4:
    metric_card("Countries", df["country_txt"].nunique(), icon="🌍", color=GREEN)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# Attacks over years — tactical dark grid, amber/cyan line
# -----------------------------
section_header("Attacks Over Years", "📈")

yearly = (
    df.groupby("iyear")
      .size()
      .reset_index(name="Attacks")
)

fig = px.line(
    yearly,
    x="iyear",
    y="Attacks",
    markers=True,
)
fig.update_traces(
    line_color=CYAN,
    line_width=2.5,
    marker=dict(size=6, color=AMBER, line=dict(width=1, color=CYAN)),
)
fig.add_hline(
    y=yearly["Attacks"].mean(),
    line_dash="dot",
    line_color=AMBER,
    opacity=0.4,
    annotation_text="avg",
    annotation_font_color=AMBER,
)
fig = style_fig(fig, height=420)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.success("👉 Click **Global Threat Map** from the left sidebar to explore incidents geographically.")
