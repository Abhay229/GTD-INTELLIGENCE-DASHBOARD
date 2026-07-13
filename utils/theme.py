"""
utils/theme.py
----------------
Shared visual theme for the AI Military Intelligence Dashboard.
Styled as a SOC / intelligence command-console, not a generic SaaS app.

This module contains ONLY presentation code:
    - load_css()          -> inject global CSS (fonts, colors, cards, sidebar, tables, buttons)
    - metric_card()       -> styled replacement for st.metric
    - section_header()    -> consistent section titles with icon + divider
    - style_fig()         -> apply the shared Plotly color/template to any figure
    - threat_badge()      -> colored LOW/MEDIUM/HIGH/CRITICAL alert pill
    - status_badge()      -> small LIVE / OFFLINE style system-status pill
    - PALETTE             -> shared color sequence for charts
    - THREAT_SCALE        -> green->amber->red scale for probability/threat charts

No backend / data / ML logic lives here. Import and call `load_css()` once
at the top of every page, right after `st.set_page_config(...)`.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palette — SOC / intelligence console theme
# ---------------------------------------------------------------------------

BG = "#080A0E"            # near-black base
PANEL = "#10131A"         # card background
PANEL_BORDER = "rgba(255,255,255,0.08)"
INK = "#E8ECF1"           # primary text
MUTED = "#7C8798"         # secondary text

CYAN = "#3DD6C6"          # "system active" accent
AMBER = "#E8A33D"         # warning / attention accent
RED = "#E8465C"           # critical / high threat
GREEN = "#3DDC84"         # low threat / good
STEEL = "#5B6B87"         # neutral data color

PRIMARY = CYAN
ACCENT = AMBER

PALETTE = [CYAN, AMBER, STEEL, RED, GREEN, "#7A8FD6", "#D67AA8", "#4FA3D1", "#C9C15A", "#8F6FE0"]
THREAT_SCALE = [GREEN, AMBER, RED]


def load_css():
    """Inject global CSS. Call once per page, after set_page_config()."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        code, .mono, [data-testid="stMetricValue"] {{
            font-family: 'JetBrains Mono', monospace !important;
        }}

        /* ---------- App background: dark slate + faint scanline grid ---------- */
        .stApp {{
            background-color: {BG};
            background-image:
                linear-gradient(rgba(61,214,198,0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(61,214,198,0.035) 1px, transparent 1px);
            background-size: 42px 42px;
            color: {INK};
        }}

        /* ---------- Sidebar: mission console ---------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B0D12 0%, #06070A 100%);
            border-right: 1px solid {PANEL_BORDER};
        }}
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {{
            color: {CYAN};
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }}
        [data-testid="stSidebarNav"] li div a {{
            border-radius: 8px;
            margin: 2px 8px;
            transition: all 0.15s ease-in-out;
            border-left: 3px solid transparent;
        }}
        [data-testid="stSidebarNav"] li div a:hover {{
            background: rgba(61, 214, 198, 0.08);
            border-left: 3px solid {CYAN};
        }}
        [data-testid="stSidebarNav"] li div a[aria-current="page"] {{
            background: rgba(61, 214, 198, 0.12);
            border-left: 3px solid {CYAN};
        }}

        /* ---------- Titles ---------- */
        h1 {{
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: {INK} !important;
            -webkit-text-fill-color: unset;
        }}
        h1::after {{
            content: "";
            display: block;
            width: 64px;
            height: 3px;
            margin-top: 10px;
            background: linear-gradient(90deg, {CYAN}, transparent);
            border-radius: 2px;
        }}
        h2, h3 {{
            font-weight: 700 !important;
            color: {INK} !important;
        }}

        /* ---------- Section header component ---------- */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.95rem;
            font-weight: 700;
            color: {MUTED};
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin: 1.6rem 0 0.7rem 0;
            padding-bottom: 8px;
            border-bottom: 1px solid {PANEL_BORDER};
        }}
        .section-header .sh-icon {{ color: {CYAN}; font-size: 1rem; }}

        /* ---------- Custom metric cards ---------- */
        .metric-card {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 12px;
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
            transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(61, 214, 198, 0.45);
            box-shadow: 0 0 0 1px rgba(61,214,198,0.15), 0 12px 24px rgba(0,0,0,0.45);
        }}
        .metric-card .accent-bar {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 3px;
        }}
        .metric-card .metric-icon {{ font-size: 1.25rem; opacity: 0.85; }}
        .metric-card .metric-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.7rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 6px;
        }}
        .metric-card .metric-label {{
            font-size: 0.72rem;
            color: {MUTED};
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 2px;
        }}

        /* ---------- Generic content / panel card ---------- */
        .content-card {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 12px;
            padding: 20px 22px;
            margin-bottom: 1rem;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}
        .content-card:hover {{
            border-color: rgba(61, 214, 198, 0.25);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}

        /* ---------- Status / threat badges ---------- */
        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 5px 12px;
            border-radius: 20px;
            text-transform: uppercase;
        }}
        .status-dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px currentColor;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.35; }}
            100% {{ opacity: 1; }}
        }}
        .status-dot.live {{ animation: pulse 1.6s ease-in-out infinite; }}

        .threat-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 8px 18px;
            border-radius: 8px;
            display: inline-block;
            text-transform: uppercase;
            font-size: 1rem;
        }}

        /* ---------- Buttons ---------- */
        .stButton > button, .stFormSubmitButton > button {{
            background: {PANEL};
            color: {CYAN};
            border: 1px solid rgba(61, 214, 198, 0.4);
            border-radius: 8px;
            padding: 0.55rem 1.3rem;
            font-weight: 600;
            transition: all 0.15s ease;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            background: rgba(61, 214, 198, 0.12);
            border-color: {CYAN};
            box-shadow: 0 0 12px rgba(61, 214, 198, 0.25);
            color: #FFFFFF;
        }}

        /* ---------- Inputs / selects ---------- */
        div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {{
            background-color: #0D0F15 !important;
            border-radius: 8px !important;
            border: 1px solid {PANEL_BORDER} !important;
            color: {INK} !important;
        }}
        div[data-baseweb="select"] > div:focus-within, .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: {CYAN} !important;
        }}

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: {MUTED};
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(61, 214, 198, 0.1) !important;
            color: {CYAN} !important;
            border-color: rgba(61, 214, 198, 0.4) !important;
        }}

        /* ---------- DataFrames / tables ---------- */
        [data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {PANEL_BORDER};
        }}

        /* ---------- Progress bar ---------- */
        .stProgress > div > div > div > div {{
            background-image: linear-gradient(90deg, {CYAN}, {AMBER});
            border-radius: 6px;
        }}

        /* ---------- Alerts (info/success/warning/error) ---------- */
        div[data-testid="stAlert"] {{
            border-radius: 10px;
            border: 1px solid {PANEL_BORDER};
        }}

        /* ---------- Chat bubbles (Agent page) ---------- */
        [data-testid="stChatMessage"] {{
            background: {PANEL};
            border-radius: 10px;
            border: 1px solid {PANEL_BORDER};
        }}

        /* ---------- Dividers ---------- */
        hr {{ border-color: {PANEL_BORDER} !important; }}

        /* ---------- Expander (operation log) ---------- */
        details {{
            background: #0B0D12;
            border: 1px solid {PANEL_BORDER};
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = "▣"):
    """Consistent section title used instead of st.subheader()."""
    st.markdown(
        f"<div class='section-header'><span class='sh-icon'>{icon}</span>{title}</div>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value, icon: str = "▪", color: str = None):
    """
    Styled drop-in replacement for st.metric(). Call inside a column, e.g.:

        c1, c2 = st.columns(2)
        with c1:
            metric_card("Incidents", f"{len(df):,}", icon="💥")
    """
    color = color or CYAN
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="accent-bar" style="background:{color};"></div>
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, ok: bool = True):
    """Small system-status pill, e.g. status_badge('DATASET LOADED', True)."""
    color = CYAN if ok else RED
    pulse_class = "live" if ok else ""
    st.markdown(
        f"""
        <span class="status-pill" style="color:{color}; background:{color}18; border:1px solid {color}40;">
            <span class="status-dot {pulse_class}" style="background:{color}; color:{color};"></span>
            {label}
        </span>
        """,
        unsafe_allow_html=True,
    )


def threat_badge(level: str) -> str:
    """Return HTML for a colored LOW / MEDIUM / HIGH threat pill."""
    colors = {"LOW": GREEN, "MEDIUM": AMBER, "HIGH": RED, "CRITICAL": RED}
    emojis = {"LOW": "●", "MEDIUM": "▲", "HIGH": "■", "CRITICAL": "◆"}
    c = colors.get(level, CYAN)
    e = emojis.get(level, "●")
    return (
        f"<span class='threat-pill' style='background:{c}1F; color:{c}; "
        f"border:1px solid {c}55;'>{e} {level}</span>"
    )


def style_fig(fig, height: int = None):
    """
    Apply the shared visual template to any Plotly figure without touching
    the underlying data/traces. Call right before st.plotly_chart(fig, ...).
    """
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        colorway=PALETTE,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=PANEL_BORDER,
            borderwidth=1,
        ),
        hoverlabel=dict(bgcolor="#161A22", font_size=13, font_family="JetBrains Mono"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    if height:
        fig.update_layout(height=height)
    return fig
