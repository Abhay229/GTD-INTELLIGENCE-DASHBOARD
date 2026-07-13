import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import load_css, section_header, metric_card, style_fig, status_badge, CYAN, AMBER, RED, GREEN

st.set_page_config(
    page_title="Data Explorer",
    page_icon="📊",
    layout="wide"
)
load_css()

st.title("📊 Global Terrorism Data Explorer")

st.markdown("Explore, filter, visualize and download the GTD dataset.")

df = load_data()

# --------------------------------------------------------
# Sidebar Filters — console panel
# --------------------------------------------------------

st.sidebar.markdown(
    """
    <div style="font-family:'JetBrains Mono', monospace; font-size:0.7rem;
                color:#7C8798; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">
        Console · Query Builder
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    years = sorted(df["iyear"].dropna().unique())
    selected_year = st.multiselect("Year", years, default=[])

    countries = sorted(df["country_txt"].dropna().unique())
    selected_country = st.multiselect("Country", countries, default=[])

    regions = sorted(df["region_txt"].dropna().unique())
    selected_region = st.multiselect("Region", regions, default=[])

    attack_types = sorted(df["attacktype1_txt"].dropna().unique())
    selected_attack = st.multiselect("Attack Type", attack_types, default=[])

    weapons = sorted(df["weaptype1_txt"].dropna().unique())
    selected_weapon = st.multiselect("Weapon Type", weapons, default=[])

    groups = sorted(df["gname"].dropna().unique())
    selected_group = st.multiselect("Terrorist Group", groups, default=[])

    st.markdown('</div>', unsafe_allow_html=True)

    active_filters = sum(
        bool(x) for x in
        [selected_year, selected_country, selected_region, selected_attack, selected_weapon, selected_group]
    )
    st.markdown("<br>", unsafe_allow_html=True)
    status_badge(f"FILTERS ACTIVE: {active_filters}", ok=True)

# --------------------------------------------------------
# Apply Filters
# --------------------------------------------------------

filtered_df = df.copy()

if selected_year:
    filtered_df = filtered_df[filtered_df["iyear"].isin(selected_year)]
if selected_country:
    filtered_df = filtered_df[filtered_df["country_txt"].isin(selected_country)]
if selected_region:
    filtered_df = filtered_df[filtered_df["region_txt"].isin(selected_region)]
if selected_attack:
    filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attack)]
if selected_weapon:
    filtered_df = filtered_df[filtered_df["weaptype1_txt"].isin(selected_weapon)]
if selected_group:
    filtered_df = filtered_df[filtered_df["gname"].isin(selected_group)]

# --------------------------------------------------------
# Search Box
# --------------------------------------------------------

section_header("Search", "🔍")
search = st.text_input(
    "Search by City or Country",
    label_visibility="collapsed",
    placeholder="🔍 Search by City or Country",
)

if search:
    filtered_df = filtered_df[
        filtered_df["city"].fillna("").str.contains(search, case=False)
        | filtered_df["country_txt"].fillna("").str.contains(search, case=False)
    ]

# --------------------------------------------------------
# KPIs — recolored
# --------------------------------------------------------

section_header("Dataset Summary", "📊")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Incidents", len(filtered_df), icon="💥", color=CYAN)
with c2:
    metric_card("Countries", filtered_df["country_txt"].nunique(), icon="🌍", color=GREEN)
with c3:
    metric_card("Fatalities", int(filtered_df["nkill"].fillna(0).sum()), icon="☠️", color=RED)
with c4:
    metric_card("Injuries", int(filtered_df["nwound"].fillna(0).sum()), icon="🏥", color=AMBER)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------
# Dataset Preview — structured numeric columns
# --------------------------------------------------------

section_header("Filtered Dataset", "📋")

numeric_col_config = {}
for c in ["iyear", "nkill", "nwound"]:
    if c in filtered_df.columns:
        numeric_col_config[c] = st.column_config.NumberColumn(c, format="%d")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500,
    column_config=numeric_col_config,
)

# --------------------------------------------------------
# Download CSV
# --------------------------------------------------------

csv = filtered_df.to_csv(index=False)

st.download_button(
    "📥 Download Filtered Data",
    csv,
    file_name="Filtered_GTD_Data.csv",
    mime="text/csv"
)

# --------------------------------------------------------
# Charts — recolored tabs
# --------------------------------------------------------

section_header("Visual Analytics", "📈")

tab1, tab2, tab3 = st.tabs(["🌍 Country", "💥 Attack Type", "🔫 Weapon Type"])

with tab1:
    country_chart = filtered_df["country_txt"].value_counts().head(10).reset_index()
    country_chart.columns = ["Country", "Incidents"]
    fig = px.bar(
        country_chart, x="Country", y="Incidents", color="Incidents",
        title="Top 10 Countries",
        color_continuous_scale=[GREEN, AMBER, RED],
    )
    fig = style_fig(fig, height=420)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    attack_chart = filtered_df["attacktype1_txt"].value_counts().reset_index()
    attack_chart.columns = ["Attack Type", "Count"]
    fig = px.pie(
        attack_chart, names="Attack Type", values="Count",
        title="Attack Type Distribution", hole=0.45,
        color_discrete_sequence=[CYAN, AMBER, "#5B6B87", RED, GREEN, "#7A8FD6", "#D67AA8", "#4FA3D1"],
    )
    fig = style_fig(fig, height=420)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    weapon_chart = filtered_df["weaptype1_txt"].value_counts().reset_index()
    weapon_chart.columns = ["Weapon", "Count"]
    fig = px.bar(
        weapon_chart, x="Weapon", y="Count", color="Count",
        title="Weapon Type Distribution",
        color_continuous_scale=[GREEN, AMBER, RED],
    )
    fig = style_fig(fig, height=420)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------
# Missing Values
# --------------------------------------------------------

section_header("Missing Values", "🕳️")

missing = filtered_df.isnull().sum().sort_values(ascending=False).reset_index()
missing.columns = ["Column", "Missing Values"]
st.dataframe(
    missing,
    use_container_width=True,
    column_config={"Missing Values": st.column_config.NumberColumn("Missing Values", format="%d")},
)

# --------------------------------------------------------
# Dataset Information
# --------------------------------------------------------

section_header("Dataset Information", "ℹ️")

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.write("Rows :", filtered_df.shape[0])
st.write("Columns :", filtered_df.shape[1])
st.write("Memory Usage (MB):", round(filtered_df.memory_usage(deep=True).sum() / 1024**2, 2))
st.write("Column Names")
st.write(filtered_df.columns.tolist())
st.markdown('</div>', unsafe_allow_html=True)
