"""
Shared data loading utility for the GTD Intelligence Dashboard.

All pages should import load_data() from here instead of calling
pd.read_csv() independently. This guarantees:
  - a single cached copy of the dataset in memory (fast reruns)
  - consistent column selection / cleaning across every page
"""

import streamlit as st
import pandas as pd
import os

DATA_PATH = os.path.join("data", "globalterrorism.csv")


@st.cache_data(show_spinner="Loading Global Terrorism Database...")
def load_data() -> pd.DataFrame:
    """
    Load and lightly clean the Global Terrorism Database (GTD).

    Returns
    -------
    pd.DataFrame
    """
    if not os.path.exists(DATA_PATH):
        st.error(
            f"Dataset not found at `{DATA_PATH}`.\n\n"
            "Download the Global Terrorism Database CSV (globalterrorism.csv) "
            "and place it inside the `data/` folder. See data/README.md for "
            "instructions."
        )
        st.stop()

    df = pd.read_csv(DATA_PATH, encoding="latin1", low_memory=False)

    # Basic type safety on the columns most pages rely on
    for col in ["nkill", "nwound"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df
