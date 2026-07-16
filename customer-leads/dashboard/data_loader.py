"""Data Ingestion & Loading Module for SAF SHIKAN Farmer Portal.

Provides isolated, cached data fetching functions to avoid layout-rendering side effects during auth.
"""

import pandas as pd
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets.get("supabase_url", "")
SUPABASE_KEY = st.secrets.get("supabase_key", "")
SUPABASE_TABLE = st.secrets.get("supabase_table", "farmer")

@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client | None:
    """Return an authenticated Supabase client using Streamlit secrets."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load farmer data live from Supabase database (cached for 10 min)."""
    supabase = get_supabase_client()
    req_cols = ["Name", "Phone", "Crop_Type", "Crop_Area", "Season", "Location", "Farm_Scale", "Region"]

    if supabase:
        candidate_tables = [SUPABASE_TABLE]
        for t in ["farmer", "farmers"]:
            if t not in candidate_tables:
                candidate_tables.append(t)

        last_error = None
        for tbl in candidate_tables:
            try:
                response = supabase.table(tbl).select(
                    "Name, Phone, Crop_Type, Crop_Area, Season, Location, Farm_Scale, Region"
                ).execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    for col in req_cols:
                        if col not in df.columns:
                            df[col] = ""
                    df = df[req_cols]
                    df["Crop_Type"]  = df["Crop_Type"].astype(str).str.title()
                    df["Season"]     = df["Season"].astype(str).str.strip()
                    df["Region"]     = df["Region"].astype(str).str.strip()
                    df["Location"]   = df["Location"].astype(str).str.strip()
                    df["Farm_Scale"] = df["Farm_Scale"].astype(str).str.strip()
                    df["Crop_Area"]  = pd.to_numeric(df["Crop_Area"], errors="coerce").fillna(0.0)
                    return df
                else:
                    last_error = f"Table '{tbl}' returned 0 rows. Enable select policy for role 'anon'."
            except Exception as e:
                last_error = str(e)
                continue

        if last_error:
            st.warning(f"⚠️ Supabase database issue: {last_error}")

    return pd.DataFrame(columns=req_cols)
