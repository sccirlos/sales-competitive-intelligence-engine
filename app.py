# app.py
from __future__ import annotations

import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Any, List, Tuple

# Use your existing competitor config (adjust import path as needed)
try:
    from compile_results import COMPETITORS 
except Exception:
    # fallback if you haven't moved it into compile_results.py yet
    COMPETITORS = {
        "SimplePractice": "https://www.simplepractice.com/",
        "Jane": "https://jane.app/",
        "TherapyNotes": "https://www.therapynotes.com/",
        "Theranest": "https://ensorahealth.com/product/theranest-mental-health/",
        "Valant": "https://www.valant.io/",
        "Healthie": "https://www.gethealthie.com/",
        "Blueprint": "https://www.blueprint.ai/",
        "Mentalyc": "https://www.mentalyc.com/",
        "YungSidekick": "https://yung-sidekick.com/",
        "Upheal": "https://www.upheal.io/",
        "Freed": "https://www.getfreed.ai/",
    }

# IMPORTANT: hook this up to your code
# Replace `run_competitor_research` with the function in your main.py (or a new runner module).
# Expected return:
#   features: List[Feature] or List[dict]
#   tiers:    List[PricingTier] or List[dict]
try:
    from main import run_competitor_research  # <-- CHANGE THIS to match your project
except Exception:
    run_competitor_research = None


def to_df(items: List[Any]) -> pd.DataFrame:
    """Convert list of dicts or Pydantic models to a DataFrame."""
    if not items:
        return pd.DataFrame()
    first = items[0]
    if hasattr(first, "model_dump"):  # Pydantic v2
        return pd.DataFrame([x.model_dump() for x in items])
    if isinstance(first, dict):
        return pd.DataFrame(items)
    return pd.DataFrame([vars(x) for x in items])


@st.cache_data(show_spinner=False)
def cached_run(competitor_name: str, competitor_url: str):
    """Cache results per competitor to avoid repeated LLM calls."""
    if run_competitor_research is None:
        raise RuntimeError(
            "Couldn't import run_competitor_research. "
            "Update the import in app.py to point to your scraper function."
        )
    features, tiers = run_competitor_research(competitor_name, competitor_url)
    return to_df(features), to_df(tiers)


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


st.set_page_config(page_title="AI Competitor Scraper", layout="wide")
st.title("AI Competitor Scraper")
st.caption("Internal tool: extract competitor features + pricing tiers into structured tables.")

with st.sidebar:
    st.header("Run")
    competitor_name = st.selectbox("Competitor", list(COMPETITORS.keys()))
    competitor_url = COMPETITORS[competitor_name]
    st.write("URL:", competitor_url)

    run_btn = st.button("Run analysis", type="primary")
    st.divider()
    st.caption("Tip: start with one competitor to validate output quality.")

if "features_df" not in st.session_state:
    st.session_state.features_df = pd.DataFrame()
if "tiers_df" not in st.session_state:
    st.session_state.tiers_df = pd.DataFrame()
if "last_run" not in st.session_state:
    st.session_state.last_run = None

if run_btn:
    with st.spinner(f"Running analysis for {competitor_name}..."):
        features_df, tiers_df = cached_run(competitor_name, competitor_url)
        st.session_state.features_df = features_df
        st.session_state.tiers_df = tiers_df
        st.session_state.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.session_state.last_run:
    st.success(f"Last run: {st.session_state.last_run}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Features")
    st.dataframe(st.session_state.features_df, use_container_width=True, height=450)

    if not st.session_state.features_df.empty:
        st.download_button(
            "Download Features CSV",
            data=csv_bytes(st.session_state.features_df),
            file_name=f"{competitor_name}_features.csv",
            mime="text/csv",
        )

with col2:
    st.subheader("Pricing tiers")
    st.dataframe(st.session_state.tiers_df, use_container_width=True, height=450)

    if not st.session_state.tiers_df.empty:
        st.download_button(
            "Download Pricing CSV",
            data=csv_bytes(st.session_state.tiers_df),
            file_name=f"{competitor_name}_pricing.csv",
            mime="text/csv",
        )

st.divider()

# Optional quick filters (nice for PMs)
df = st.session_state.features_df
if not df.empty:
    st.subheader("Filter (optional)")
    c1, c2, c3 = st.columns(3)

    with c1:
        if "category" in df.columns:
            categories = ["(All)"] + sorted([c for c in df["category"].dropna().unique()])
            selected_cat = st.selectbox("Category", categories)
        else:
            selected_cat = "(All)"

    with c2:
        if "is_gated" in df.columns:
            gated_only = st.checkbox("Show gated only", value=False)
        else:
            gated_only = False

    with c3:
        search = st.text_input("Search feature name", "")

    filtered = df.copy()
    if selected_cat != "(All)" and "category" in filtered.columns:
        filtered = filtered[filtered["category"] == selected_cat]
    if gated_only and "is_gated" in filtered.columns:
        filtered = filtered[filtered["is_gated"] == True]
    if search and "feature_name" in filtered.columns:
        filtered = filtered[filtered["feature_name"].str.contains(search, case=False, na=False)]

    st.dataframe(filtered, use_container_width=True, height=350)