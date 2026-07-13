import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.theme import load_css, section_header, metric_card, style_fig, CYAN, AMBER, RED, GREEN, STEEL

st.set_page_config(
    page_title="Country Analysis",
    page_icon="🌎",
    layout="wide"
)
load_css()

st.title("🌎 Country Analysis")

df = load_data()

# -----------------------------
# Sidebar
# -----------------------------

countries = sorted(df["country_txt"].dropna().unique())

country = st.sidebar.selectbox(
    "Select Country",
    countries
)

country_df = df[df["country_txt"] == country]

st.caption(f"Deep-dive intelligence report for **{country}**.")
section_header(f"Intelligence Report: {country}", "▣")

# -----------------------------
# KPIs — recolored to SOC palette
# -----------------------------

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Incidents", f"{len(country_df):,}", icon="💥", color=CYAN)
with c2:
    metric_card("Fatalities", int(country_df["nkill"].sum()), icon="☠️", color=RED)
with c3:
    metric_card("Injured", int(country_df["nwound"].sum()), icon="🏥", color=AMBER)
with c4:
    metric_card("Groups", country_df["gname"].nunique(), icon="👥", color=GREEN)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# Attacks Over Time / Attack Types — recolored
# -----------------------------

section_header("Trends & Attack Composition", "▤")

left, right = st.columns(2)

with left:
    yearly = (
        country_df
        .groupby("iyear")
        .size()
        .reset_index(name="Attacks")
    )

    fig = px.line(
        yearly,
        x="iyear",
        y="Attacks",
        markers=True,
        title="Attacks Over Years"
    )
    fig.update_traces(
        line_color=CYAN,
        line_width=2.5,
        marker=dict(size=6, color=AMBER, line=dict(width=1, color=CYAN)),
    )
    fig = style_fig(fig, height=380)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    attack = (
        country_df
        .groupby("attacktype1_txt")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        attack,
        names="attacktype1_txt",
        values="Count",
        title="Attack Types",
        hole=0.5,
        color_discrete_sequence=[CYAN, AMBER, STEEL, RED, GREEN, "#7A8FD6", "#D67AA8", "#4FA3D1"],
    )
    fig = style_fig(fig, height=380)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Organizations & Weapons — recolored
# -----------------------------

section_header("Organizations & Weapons", "▲")

left, right = st.columns(2)

with left:
    groups = (
        country_df
        .groupby("gname")
        .size()
        .reset_index(name="Attacks")
        .sort_values("Attacks", ascending=False)
        .head(10)
    )

    fig = px.bar(
        groups,
        x="Attacks",
        y="gname",
        orientation="h",
        title="Top Terrorist Organizations",
        color_discrete_sequence=[RED],
    )
    fig = style_fig(fig, height=400)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    weapon = (
        country_df
        .groupby("weaptype1_txt")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    fig = px.bar(
        weapon,
        x="weaptype1_txt",
        y="Count",
        title="Weapon Types",
        color_discrete_sequence=[AMBER],
    )
    fig = style_fig(fig, height=400)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Incident Map — recolored
# -----------------------------

section_header("Incident Locations", "🗺️")

map_df = country_df.dropna(subset=["latitude", "longitude"])

fig = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    hover_name="city",
    hover_data={
        "country_txt": True,
        "iyear": True,
        "attacktype1_txt": True,
        "gname": True,
        "nkill": True,
        "latitude": False,
        "longitude": False
    },
    color="attacktype1_txt",
    projection="natural earth",
    title=f"Terrorist Incidents in {country}",
    height=600,
    color_discrete_sequence=[CYAN, AMBER, STEEL, RED, GREEN, "#7A8FD6", "#D67AA8", "#4FA3D1"],
)
fig.update_geos(
    bgcolor="rgba(0,0,0,0)",
    landcolor="#0C0F14",
    showocean=True, oceancolor="#050609",
    showcountries=True, countrycolor="rgba(61, 214, 198, 0.18)",
)
fig = style_fig(fig)
fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Incident Table — structured numeric columns
# -----------------------------

section_header("Incident Details", "▦")

cols = [
    "iyear", "city", "attacktype1_txt", "targtype1_txt",
    "weaptype1_txt", "gname", "nkill", "nwound"
]
cols = [c for c in cols if c in country_df.columns]

st.dataframe(
    country_df[cols],
    use_container_width=True,
    column_config={
        "iyear": st.column_config.NumberColumn("Year", format="%d"),
        "nkill": st.column_config.NumberColumn("Fatalities", format="%d"),
        "nwound": st.column_config.NumberColumn("Injured", format="%d"),
    },
)

# -----------------------------
# Download
# -----------------------------

csv = country_df.to_csv(index=False).encode()

st.download_button(
    "📥 Download Country Data",
    csv,
    file_name=f"{country}.csv",
    mime="text/csv"
)
