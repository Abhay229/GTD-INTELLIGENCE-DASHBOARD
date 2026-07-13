"""
Tool functions exposed to the LLM agent.

Each function here wraps logic that already exists elsewhere in this
project (Country_Analysis, Forecasting, Threat_Level pages) as a plain,
well-documented Python function with a JSON tool schema. The agent
(agent/agent_core.py) decides which of these to call and in what order,
based on the user's natural-language question.
"""

import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

from utils.data_loader import load_data


# ---------------------------------------------------------------------
# Tool 1: query_country_stats
# ---------------------------------------------------------------------

def query_country_stats(country: str) -> dict:
    """Get summary statistics for a specific country from the GTD dataset."""
    df = load_data()
    country_df = df[df["country_txt"].str.lower() == country.lower()]

    if country_df.empty:
        return {"error": f"No data found for country '{country}'."}

    top_group = (
        country_df["gname"].value_counts().idxmax()
        if country_df["gname"].notna().any() else "Unknown"
    )
    top_attack = (
        country_df["attacktype1_txt"].value_counts().idxmax()
        if country_df["attacktype1_txt"].notna().any() else "Unknown"
    )
    top_weapon = (
        country_df["weaptype1_txt"].value_counts().idxmax()
        if country_df["weaptype1_txt"].notna().any() else "Unknown"
    )

    return {
        "country": country,
        "total_incidents": int(len(country_df)),
        "total_fatalities": int(country_df["nkill"].sum()),
        "total_injuries": int(country_df["nwound"].sum()),
        "unique_groups": int(country_df["gname"].nunique()),
        "most_active_group": top_group,
        "most_common_attack_type": top_attack,
        "most_common_weapon_type": top_weapon,
        "years_covered": f"{int(country_df['iyear'].min())}-{int(country_df['iyear'].max())}",
    }


# ---------------------------------------------------------------------
# Tool 2: forecast_attacks
# ---------------------------------------------------------------------

def forecast_attacks(country: str, years: int = 5) -> dict:
    """Forecast future yearly attack counts for a country using linear regression."""
    df = load_data()
    country_df = df[df["country_txt"].str.lower() == country.lower()]

    yearly = (
        country_df.groupby("iyear").size().reset_index(name="Attacks").sort_values("iyear")
    )

    if len(yearly) < 5:
        return {"error": f"Not enough historical data to forecast for '{country}'."}

    X = yearly[["iyear"]]
    y = yearly["Attacks"]

    model = LinearRegression()
    model.fit(X, y)

    last_year = int(yearly["iyear"].max())
    future_years = np.arange(last_year + 1, last_year + years + 1)
    preds = np.maximum(model.predict(pd.DataFrame({"iyear": future_years})), 0)

    historical_last = int(yearly.iloc[-1]["Attacks"])
    forecast_last = int(preds[-1])
    growth_pct = ((forecast_last - historical_last) / max(historical_last, 1)) * 100

    if growth_pct < 0:
        trend = "decreasing"
    elif growth_pct < 15:
        trend = "stable"
    else:
        trend = "increasing"

    return {
        "country": country,
        "last_historical_year": last_year,
        "last_historical_attacks": historical_last,
        "forecast": {
            int(yr): int(p) for yr, p in zip(future_years, preds)
        },
        "growth_percent": round(growth_pct, 2),
        "trend": trend,
    }


# ---------------------------------------------------------------------
# Tool 3: predict_threat_level
# ---------------------------------------------------------------------

_THREAT_CAT_COLS = [
    "country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt"
]

_threat_model_cache = {}


def _get_threat_model():
    """Train (once, cached in-process) the same Random Forest threat-level model
    used on the Threat Level page."""
    if _threat_model_cache:
        return _threat_model_cache

    df = load_data()
    df = df[_THREAT_CAT_COLS + ["nkill", "nwound"]].dropna()
    df["impact"] = df["nkill"] + df["nwound"]

    def classify(x):
        if x <= 2:
            return "LOW"
        elif x <= 10:
            return "MEDIUM"
        return "HIGH"

    df["threat_level"] = df["impact"].apply(classify)

    encoders = {}
    df_enc = df.copy()
    for col in _THREAT_CAT_COLS:
        le = LabelEncoder()
        df_enc[col] = le.fit_transform(df_enc[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df_enc["threat_level"] = target_encoder.fit_transform(df_enc["threat_level"])

    X = df_enc.drop(columns=["threat_level", "impact"])
    y = df_enc["threat_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    _threat_model_cache.update({
        "model": model, "encoders": encoders, "target_encoder": target_encoder
    })
    return _threat_model_cache


def predict_threat_level(
    country: str,
    region: str,
    attack_type: str,
    weapon_type: str,
    target_type: str,
    nkill: int = 0,
    nwound: int = 0,
) -> dict:
    """Predict LOW/MEDIUM/HIGH threat level for a hypothetical incident profile."""
    cache = _get_threat_model()
    model, encoders, target_encoder = cache["model"], cache["encoders"], cache["target_encoder"]

    try:
        row = np.array([[
            encoders["country_txt"].transform([country])[0],
            encoders["region_txt"].transform([region])[0],
            encoders["attacktype1_txt"].transform([attack_type])[0],
            encoders["weaptype1_txt"].transform([weapon_type])[0],
            encoders["targtype1_txt"].transform([target_type])[0],
            nkill,
            nwound,
        ]])
    except ValueError as e:
        return {"error": f"Unrecognized category value: {e}"}

    pred = model.predict(row)
    proba = model.predict_proba(row)

    return {
        "threat_level": target_encoder.inverse_transform(pred)[0],
        "confidence_percent": round(float(np.max(proba)) * 100, 2),
    }


# ---------------------------------------------------------------------
# Tool 4: query_data  (flexible filtered lookup, used by the chat agent)
# ---------------------------------------------------------------------

def query_data(
    country: str = None,
    region: str = None,
    year_from: int = None,
    year_to: int = None,
    attack_type: str = None,
    limit: int = 10,
) -> dict:
    """Filter the GTD dataset by common fields and return summary counts."""
    df = load_data()

    if country:
        df = df[df["country_txt"].str.lower() == country.lower()]
    if region:
        df = df[df["region_txt"].str.lower() == region.lower()]
    if year_from:
        df = df[df["iyear"] >= year_from]
    if year_to:
        df = df[df["iyear"] <= year_to]
    if attack_type:
        df = df[df["attacktype1_txt"].str.lower() == attack_type.lower()]

    if df.empty:
        return {"matching_incidents": 0}

    return {
        "matching_incidents": int(len(df)),
        "total_fatalities": int(df["nkill"].sum()),
        "total_injuries": int(df["nwound"].sum()),
        "top_countries": df["country_txt"].value_counts().head(limit).to_dict(),
        "top_attack_types": df["attacktype1_txt"].value_counts().head(limit).to_dict(),
    }


# ---------------------------------------------------------------------
# Tool schemas (OpenAI/OpenRouter function-calling format)
# ---------------------------------------------------------------------

TOOL_REGISTRY = {
    "query_country_stats": query_country_stats,
    "forecast_attacks": forecast_attacks,
    "predict_threat_level": predict_threat_level,
    "query_data": query_data,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "query_country_stats",
            "description": "Get summary statistics (incidents, fatalities, top group/attack/weapon) for one country from the GTD dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string", "description": "Country name, e.g. 'Nigeria'"}
                },
                "required": ["country"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "forecast_attacks",
            "description": "Forecast the number of future terrorist attacks per year for a country using linear regression on historical trends.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "years": {"type": "integer", "description": "Number of years to forecast, default 5"},
                },
                "required": ["country"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predict_threat_level",
            "description": "Predict LOW/MEDIUM/HIGH threat level for a hypothetical incident profile using a trained Random Forest classifier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "region": {"type": "string"},
                    "attack_type": {"type": "string"},
                    "weapon_type": {"type": "string"},
                    "target_type": {"type": "string"},
                    "nkill": {"type": "integer"},
                    "nwound": {"type": "integer"},
                },
                "required": ["country", "region", "attack_type", "weapon_type", "target_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_data",
            "description": "Filter the GTD dataset by country, region, year range, and/or attack type and return aggregate counts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "region": {"type": "string"},
                    "year_from": {"type": "integer"},
                    "year_to": {"type": "integer"},
                    "attack_type": {"type": "string"},
                    "limit": {"type": "integer", "description": "Max items in top-N breakdowns, default 10"},
                },
                "required": [],
            },
        },
    },
]
