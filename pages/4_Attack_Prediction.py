import streamlit as st
import joblib
import pandas as pd
import os

from utils.data_loader import load_data
from utils.theme import load_css, section_header, CYAN, AMBER

st.set_page_config(
    page_title="Attack Prediction",
    page_icon="🤖",
    layout="wide"
)
load_css()

st.title("🤖 Attack Type Prediction")

st.caption("Submit incident parameters below to generate a classified attack-type dossier.")

MODEL_PATH = "models/attack_prediction_model.pkl"
ENCODERS_PATH = "models/feature_encoders.pkl"
TARGET_ENCODER_PATH = "models/target_encoder.pkl"

if not (os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH) and os.path.exists(TARGET_ENCODER_PATH)):
    st.error(
        "Trained model not found. Run `python train_attack_model.py` first "
        "to generate the files inside `models/`."
    )
    st.stop()

model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODERS_PATH)
target_encoder = joblib.load(TARGET_ENCODER_PATH)

# -------------------------
# Load Dataset (cached, shared loader)
# -------------------------

df = load_data()

df = df.dropna(subset=[
    "country_txt",
    "region_txt",
    "weaptype1_txt",
    "targtype1_txt",
    "gname"
])

# -------------------------
# Structured Intel-Input Form — grouped fields
# -------------------------

section_header("Incident Input Form", "▣")

with st.form("prediction_form"):

    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.markdown(
        "<div class='section-header' style='margin-top:0;'>"
        "<span class='sh-icon'>📍</span>LOCATION & CONTEXT</div>",
        unsafe_allow_html=True,
    )
    loc1, loc2 = st.columns(2)
    with loc1:
        country = st.selectbox("Country", sorted(df["country_txt"].unique()))
    with loc2:
        region = st.selectbox("Region", sorted(df["region_txt"].unique()))

    st.markdown(
        "<div class='section-header'>"
        "<span class='sh-icon'>🎯</span>WEAPON & TARGET</div>",
        unsafe_allow_html=True,
    )
    wt1, wt2 = st.columns(2)
    with wt1:
        weapon = st.selectbox("Weapon Type", sorted(df["weaptype1_txt"].unique()))
    with wt2:
        target = st.selectbox("Target Type", sorted(df["targtype1_txt"].unique()))

    st.markdown(
        "<div class='section-header'>"
        "<span class='sh-icon'>👥</span>GROUP & OUTCOME</div>",
        unsafe_allow_html=True,
    )
    g1, g2 = st.columns(2)
    with g1:
        group = st.selectbox("Terrorist Group", sorted(df["gname"].unique()))
        success = st.selectbox(
            "Attack Successful?", [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
    with g2:
        suicide = st.selectbox(
            "Suicide Attack?", [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
    c1, c2 = st.columns(2)
    with c1:
        nkill = st.number_input("Number of Fatalities", min_value=0, value=0, step=1)
    with c2:
        nwound = st.number_input("Number of Injured", min_value=0, value=0, step=1)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 Predict Attack Type")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Prediction only runs when the form is actually submitted
# (this was previously outside the `submitted` check — fixed here)
# -------------------------

if submitted:
    try:
        country_enc = encoders["country_txt"].transform([country])[0]
        region_enc = encoders["region_txt"].transform([region])[0]
        weapon_enc = encoders["weaptype1_txt"].transform([weapon])[0]
        target_enc = encoders["targtype1_txt"].transform([target])[0]
        group_enc = encoders["gname"].transform([group])[0]

        input_df = pd.DataFrame({
            "country_txt": [country_enc],
            "region_txt": [region_enc],
            "weaptype1_txt": [weapon_enc],
            "targtype1_txt": [target_enc],
            "gname": [group_enc],
            "success": [success],
            "suicide": [suicide],
            "nkill": [nkill],
            "nwound": [nwound]
        })

        prediction = model.predict(input_df)
        attack_type = target_encoder.inverse_transform(prediction)[0]

        probabilities = model.predict_proba(input_df)
        confidence = probabilities.max() * 100

        # ---------------------------------------------------
        # Result — "Prediction Dossier" card
        # ---------------------------------------------------
        section_header("Prediction Dossier", "📄")

        st.markdown(
            f"""
            <div class="content-card">
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.72rem;
                            color:#7C8798; letter-spacing:1px; text-transform:uppercase;">
                    Classified Output · Attack Type Model
                </div>
                <div style="font-size:1.6rem; font-weight:800; color:#FFFFFF; margin-top:8px;">
                    {attack_type}
                </div>
                <div style="color:#7C8798; font-size:0.85rem; margin-top:4px;">
                    Predicted for {country} · {region} · {weapon} → {target}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown(
            f"<div style='display:flex; justify-content:space-between; align-items:baseline;'>"
            f"<span style='color:#7C8798; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.8px;'>Confidence Score</span>"
            f"<span style='font-family:JetBrains Mono, monospace; font-weight:700; color:{AMBER}; font-size:1.1rem;'>{confidence:.2f}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.progress(min(int(confidence), 100))
        st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(
            "One of the selected values wasn't seen during training "
            f"(likely a rare category). Details: {e}"
        )
