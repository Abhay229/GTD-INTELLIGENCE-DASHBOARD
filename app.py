import os
import streamlit as st

from utils.theme import load_css, section_header, status_badge

st.set_page_config(
    page_title="AI Military Intelligence Dashboard",
    page_icon="🛡",
    layout="wide"
)
load_css()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🛡 AI-Based Military Intelligence Dashboard")

st.markdown("""
### Mission Briefing

This dashboard provides intelligence analysis and forecasting on the
**Global Terrorism Database (GTD)**, combining classic dashboards,
machine learning models, and an **LLM-powered agent** that can reason
over the data and call the analytical tools on your behalf.
""")

# ---------------------------------------------------------------------------
# System status row
# ---------------------------------------------------------------------------
# Read-only checks against the same files/config every other page already
# depends on. No backend logic is touched here — this only *displays*
# whether those dependencies are currently satisfied.

section_header("System Status", "◉")

status_cols = st.columns(3)

with status_cols[0]:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    try:
        from utils.data_loader import load_data
        _df = load_data()
        dataset_ok = _df is not None and len(_df) > 0
        row_count = f"{len(_df):,} rows" if dataset_ok else "no rows"
    except Exception:
        dataset_ok = False
        row_count = "not found"
    status_badge("DATASET LOADED" if dataset_ok else "DATASET OFFLINE", ok=dataset_ok)
    st.caption(f"GTD source data · {row_count}")
    st.markdown('</div>', unsafe_allow_html=True)

with status_cols[1]:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    model_files = [
        "models/attack_prediction_model.pkl",
        "models/feature_encoders.pkl",
        "models/target_encoder.pkl",
    ]
    model_ok = all(os.path.exists(p) for p in model_files)
    status_badge("MODEL TRAINED" if model_ok else "MODEL NOT TRAINED", ok=model_ok)
    st.caption("Attack-type classifier · run `train_attack_model.py`" if not model_ok else "Attack-type classifier ready")
    st.markdown('</div>', unsafe_allow_html=True)

with status_cols[2]:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    try:
        from agent.llm_client import is_configured, DEFAULT_MODEL
        agent_ok = is_configured()
        model_name = DEFAULT_MODEL if agent_ok else "no API key"
    except Exception:
        agent_ok = False
        model_name = "not configured"
    status_badge("AGENT ONLINE" if agent_ok else "AGENT OFFLINE", ok=agent_ok)
    st.caption(f"LLM: `{model_name}`")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Module grid — tactical tiles
# ---------------------------------------------------------------------------

section_header("Available Modules", "▣")

modules = [
    ("🏠", "Home", "KPIs + attacks-over-time overview"),
    ("🌍", "Global Threat Map", "Geo-plot of incidents, filterable by year"),
    ("🌎", "Country Analysis", "Deep dive on one country"),
    ("🤖", "Attack Prediction", "Random Forest classifier"),
    ("🚨", "Threat Level", "LOW / MEDIUM / HIGH classifier"),
    ("📈", "Forecasting", "Linear regression forecast"),
    ("🧠", "AI Intelligence Report", "LLM-generated executive summary"),
    ("📊", "Data Explorer", "Multi-filter EDA + CSV export"),
    ("⚙", "Settings", "Dashboard configuration"),
    ("🕵", "AI Analyst Agent", "Chat with a tool-calling agent"),
]

cols = st.columns(5)
for i, (icon, name, desc) in enumerate(modules):
    with cols[i % 5]:
        st.markdown(
            f"""
            <div class="content-card" style="min-height:138px;">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="font-size:1.5rem;">{icon}</div>
                    <div style="width:6px; height:6px; border-radius:50%; background:#3DD6C6;
                                box-shadow:0 0 6px #3DD6C6;"></div>
                </div>
                <div style="font-weight:700; margin-top:10px; color:#E8ECF1;">{name}</div>
                <div style="color:#7C8798; font-size:0.82rem; margin-top:4px; line-height:1.4;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the **left sidebar** to navigate between modules.")

with st.expander("ℹ️ About the AI Analyst Agent"):
    st.markdown("""
    The **AI Analyst Agent** page is powered by a free LLM via
    [OpenRouter](https://openrouter.ai). It doesn't just chat — it can
    call the same data-query, forecasting, and prediction functions used
    throughout this dashboard, decide which ones are relevant to your
    question, and synthesize a final answer.

    To use it, add your free OpenRouter API key to a `.env` file
    (see `.env.example`).
    """)
