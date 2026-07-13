import streamlit as st

from utils.data_loader import load_data
from agent.llm_client import is_configured, DEFAULT_MODEL
from utils.theme import load_css, section_header, metric_card, status_badge, CYAN, AMBER, GREEN

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)
load_css()

st.title("⚙️ Dashboard Settings")

st.caption("System configuration for your AI-Based Military Intelligence Dashboard.")

# ==========================================================
# SYSTEM HEALTH — status rows (API key, dataset, agent model)
# ==========================================================

section_header("System Health", "◉")

st.markdown('<div class="content-card">', unsafe_allow_html=True)

agent_configured = is_configured()

health_col1, health_col2 = st.columns([1, 2])
with health_col1:
    status_badge("AGENT CONFIGURED" if agent_configured else "AGENT NOT CONFIGURED", ok=agent_configured)
with health_col2:
    if agent_configured:
        st.markdown(
            f"<span style='font-family:JetBrains Mono, monospace; color:#7C8798; font-size:0.85rem;'>"
            f"Active model: <span style='color:{CYAN};'>{DEFAULT_MODEL}</span></span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='color:#7C8798; font-size:0.85rem;'>"
            "No <code>OPENROUTER_API_KEY</code> found — AI Intelligence Report and "
            "AI Analyst Agent will fall back to non-LLM behavior. Add it to a "
            "<code>.env</code> file (copy <code>.env.example</code>).</span>",
            unsafe_allow_html=True,
        )

st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)

dataset_col1, dataset_col2 = st.columns([1, 2])
try:
    _df = load_data()
    dataset_ok = _df is not None and len(_df) > 0
    dataset_msg = f"{len(_df):,} rows · {_df.shape[1]} columns" if dataset_ok else "no data returned"
except Exception:
    dataset_ok = False
    dataset_msg = "dataset not found"
with dataset_col1:
    status_badge("DATASET LOADED" if dataset_ok else "DATASET OFFLINE", ok=dataset_ok)
with dataset_col2:
    st.markdown(
        f"<span style='color:#7C8798; font-size:0.85rem;'>{dataset_msg}</span>",
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# APPEARANCE
# ==========================================================

section_header("Appearance", "🎨")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
a1, a2, a3 = st.columns(3)
with a1:
    theme = st.selectbox("Dashboard Theme", ["Light", "Dark"], index=1)
with a2:
    layout = st.selectbox("Dashboard Layout", ["Wide", "Centered"])
with a3:
    chart_style = st.selectbox("Chart Style", ["Plotly", "Bar", "Line", "Pie"])
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# DEFAULT DASHBOARD
# ==========================================================

section_header("Default Dashboard", "🌍")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    country = st.text_input("Default Country", "India")
with d2:
    forecast_years = st.slider("Default Forecast Years", 1, 10, 5)
with d3:
    confidence = st.slider("Minimum Prediction Confidence (%)", 50, 100, 80)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# GLOBAL THREAT MAP
# ==========================================================

section_header("Global Threat Map", "🗺️")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
with m1:
    map_style = st.selectbox("Map Style", ["OpenStreetMap", "Carto Positron", "Carto Dark"])
with m2:
    show_cluster = st.checkbox("Enable Marker Clustering", value=True)
with m3:
    show_heatmap = st.checkbox("Enable Heatmap", value=False)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# FORECASTING
# ==========================================================

section_header("Forecasting", "📈")
st.markdown('<div class="content-card">', unsafe_allow_html=True)
forecast_model = st.selectbox("Forecasting Algorithm", ["Linear Regression", "ARIMA", "Prophet"])
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# MACHINE LEARNING
# ==========================================================

section_header("Machine Learning", "🤖")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
ml1, ml2, ml3 = st.columns(3)
with ml1:
    ml_model = st.selectbox("Prediction Model", ["Random Forest", "Decision Tree", "Gradient Boosting"])
with ml2:
    probability = st.checkbox("Show Prediction Probability", value=True)
with ml3:
    feature_importance = st.checkbox("Show Feature Importance", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# AI INTELLIGENCE REPORT
# ==========================================================

section_header("AI Intelligence Report", "📄")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
with r1:
    report_type = st.selectbox("Default Report Format", ["PDF", "Word", "Text"])
with r2:
    include_charts = st.checkbox("Include Charts in Report", value=True)
with r3:
    include_tables = st.checkbox("Include Data Tables", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# NOTIFICATIONS
# ==========================================================

section_header("Notifications", "🔔")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
with n1:
    attack_alert = st.checkbox("Enable Attack Alerts", value=True)
with n2:
    forecast_alert = st.checkbox("Enable Forecast Alerts", value=True)
with n3:
    report_alert = st.checkbox("Enable Report Notifications", value=False)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# DATASET INFORMATION
# ==========================================================

section_header("Dataset Information", "📊")

if dataset_ok:
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Rows", _df.shape[0], icon="🧾", color=CYAN)
    with col2:
        metric_card("Columns", _df.shape[1], icon="📐", color=GREEN)
    with col3:
        metric_card("Countries", _df["country_txt"].nunique(), icon="🌍", color=AMBER)
else:
    st.error("Dataset not found.")

# ==========================================================
# SAVE / RESET
# (note: not persisted - UI only, same as original project)
# ==========================================================

st.markdown("<br>", unsafe_allow_html=True)

b1, b2 = st.columns(2)
with b1:
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")
        st.balloons()
with b2:
    if st.button("🔄 Reset Settings", use_container_width=True):
        st.warning("Settings reset to default values.")
