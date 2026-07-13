import streamlit as st
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

from utils.data_loader import load_data
from utils.theme import load_css, section_header, style_fig, threat_badge, GREEN, AMBER, RED

st.set_page_config(
    page_title="Threat Level Prediction",
    page_icon="🚨",
    layout="wide"
)
load_css()

st.title("🚨 AI Threat Level Prediction System")

CAT_COLS = [
    "country_txt",
    "region_txt",
    "attacktype1_txt",
    "weaptype1_txt",
    "targtype1_txt",
]

THREAT_COLOR = {"LOW": GREEN, "MEDIUM": AMBER, "HIGH": RED}


def classify_threat(x):
    if x <= 2:
        return "LOW"
    elif x <= 10:
        return "MEDIUM"
    else:
        return "HIGH"


@st.cache_resource(show_spinner="Training threat level model (one-time)...")
def train_model():
    """
    Trains once and is cached for the life of the app session/process
    (previously this retrained a fresh Random Forest on every single
    rerun of the page, which was very slow).
    """
    df = load_data()

    df = df[CAT_COLS + ["nkill", "nwound"]].dropna()

    df["impact"] = df["nkill"] + df["nwound"]
    df["threat_level"] = df["impact"].apply(classify_threat)

    encoders = {}
    df_encoded = df.copy()

    for col in CAT_COLS:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df_encoded["threat_level"] = target_encoder.fit_transform(df_encoded["threat_level"])

    X = df_encoded.drop(columns=["threat_level", "impact"])
    y = df_encoded["threat_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Keep the *original* (human-readable) unique values for building the
    # sidebar dropdowns. Previously the UI selectboxes read from the same
    # dataframe columns AFTER they'd been overwritten with integer-encoded
    # values, so users saw numbers instead of country/region/etc. names.
    readable_options = {col: sorted(df[col].unique()) for col in CAT_COLS}

    return model, encoders, target_encoder, readable_options


model, encoders, target_encoder, readable_options = train_model()

# -------------------------------
# Sidebar Inputs (always show original text labels)
# -------------------------------
st.sidebar.markdown("### 🎛️ Input Parameters")

country = st.sidebar.selectbox("Country", readable_options["country_txt"])
region = st.sidebar.selectbox("Region", readable_options["region_txt"])
attack = st.sidebar.selectbox("Attack Type", readable_options["attacktype1_txt"])
weapon = st.sidebar.selectbox("Weapon Type", readable_options["weaptype1_txt"])
target = st.sidebar.selectbox("Target Type", readable_options["targtype1_txt"])

nkill = st.sidebar.number_input("Number Killed", 0, 1000, 0)
nwound = st.sidebar.number_input("Number Wounded", 0, 1000, 0)

# -------------------------------
# Prediction Button
# -------------------------------
if st.button("🚨 Predict Threat Level"):

    try:
        input_data = np.array([[
            encoders["country_txt"].transform([country])[0],
            encoders["region_txt"].transform([region])[0],
            encoders["attacktype1_txt"].transform([attack])[0],
            encoders["weaptype1_txt"].transform([weapon])[0],
            encoders["targtype1_txt"].transform([target])[0],
            nkill,
            nwound
        ]])

        prediction = model.predict(input_data)
        probability = model.predict_proba(input_data)

        result = target_encoder.inverse_transform(prediction)[0]
        confidence = np.max(probability) * 100

        # ---------------------------------------------------
        # Result — large alert card, LOW/MEDIUM/HIGH coloring
        # ---------------------------------------------------
        section_header("Prediction Result", "🔍")

        alert_color = THREAT_COLOR.get(result, AMBER)

        st.markdown(
            f"""
            <div class="content-card" style="border-color:{alert_color}55;
                        box-shadow:0 0 24px {alert_color}22; text-align:center; padding:32px 20px;">
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem;
                            color:#7C8798; letter-spacing:1.5px; text-transform:uppercase;">
                    Threat Classification
                </div>
                <div style="margin-top:14px;">
                    {threat_badge(result)}
                </div>
                <div style="margin-top:18px; font-family:'JetBrains Mono', monospace;
                            font-size:1rem; color:{alert_color};">
                    CONFIDENCE {confidence:.2f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(min(int(confidence), 100))

        # ---------------------------------------------------
        # Probability distribution — threat gradient (green -> amber -> red)
        # ---------------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Probability Distribution", "📊")

        import plotly.graph_objects as go
        classes = target_encoder.inverse_transform(np.arange(len(probability[0])))
        bar_colors = [THREAT_COLOR.get(c, AMBER) for c in classes]

        fig = go.Figure(go.Bar(
            x=classes,
            y=probability[0],
            marker_color=bar_colors,
            text=[f"{p*100:.1f}%" for p in probability[0]],
            textposition="outside",
        ))
        fig.update_layout(yaxis_title="Probability", xaxis_title="Threat Level")
        fig = style_fig(fig, height=380)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"Could not encode one of the inputs: {e}")
