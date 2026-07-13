import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.theme import load_css, section_header, style_fig, status_badge

st.set_page_config(page_title="Global Threat Map", page_icon="🌍", layout="wide")
load_css()

st.title("🌍 Global Threat Map")
st.caption("Geospatial distribution of recorded incidents, filterable by year.")

df = load_data()

# ---------------------------------------------------------------------------
# Sidebar — console filter panel
# ---------------------------------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding:10px 4px 4px 4px;">
        <div style="font-family:'JetBrains Mono', monospace; font-size:0.7rem;
                    color:#7C8798; letter-spacing:1px; text-transform:uppercase;">
            Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("### 🎛️ Filters")

with st.sidebar:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    year = st.selectbox(
        "Year",
        ["All"] + sorted(df["iyear"].unique().tolist())
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    status_badge(f"SCOPE: {year if year != 'All' else 'ALL YEARS'}", ok=True)

if year != "All":
    df = df[df["iyear"] == year]

df = df.dropna(subset=["latitude", "longitude"])

# ---------------------------------------------------------------------------
# Map — intensified dark theme
# ---------------------------------------------------------------------------

section_header(f"Incidents Map · {year if year != 'All' else 'All Years'}", "🗺️")

fig = px.scatter_geo(
    df,
    lat="latitude",
    lon="longitude",
    color="attacktype1_txt",
    hover_name="country_txt",
    hover_data=["city", "gname", "nkill"],
    projection="natural earth",
)

fig.update_traces(marker=dict(size=5, opacity=0.85, line=dict(width=0)))

fig.update_geos(
    bgcolor="rgba(0,0,0,0)",
    landcolor="#0C0F14",
    showland=True,
    showocean=True, oceancolor="#050609",
    showcountries=True, countrycolor="rgba(61, 214, 198, 0.18)",
    showcoastlines=True, coastlinecolor="rgba(61, 214, 198, 0.25)",
    showframe=False,
    lataxis_showgrid=True, lataxis_gridcolor="rgba(255,255,255,0.04)",
    lonaxis_showgrid=True, lonaxis_gridcolor="rgba(255,255,255,0.04)",
)

fig.update_layout(
    legend=dict(
        title=dict(text="Attack Type", font=dict(size=12, color="#7C8798")),
        font=dict(size=11),
        orientation="h",
        yanchor="bottom", y=-0.15,
        xanchor="center", x=0.5,
        bgcolor="rgba(16,19,26,0.85)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
    )
)

fig = style_fig(fig, height=640)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.info("👈 Change filters from the sidebar.")
