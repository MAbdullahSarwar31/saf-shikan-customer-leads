"""Filters component for SAF SHIKAN Lead Dashboard.

This module provides interactive sidebar controls to slice and dice customer lead data.
"""

import streamlit as st
import pandas as pd


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render interactive sidebar filters and apply them to the DataFrame.
    
    Args:
        df: Input DataFrame containing lead data.
        
    Returns:
        Filtered DataFrame.
    """
    st.sidebar.header("🔍 Filters")
    st.sidebar.write("Refine the customer lists below:")
    
    # 1. Lead Category Filter
    all_categories = sorted(df["Lead_Category"].unique())
    selected_categories = st.sidebar.multiselect(
        "Lead Priority Category",
        options=all_categories,
        default=all_categories,
        help="Select lead priority status to target."
    )
    
    # 2. Region Filter
    all_regions = sorted(df["Region"].unique())
    selected_regions = st.sidebar.multiselect(
        "Administrative Region",
        options=all_regions,
        default=all_regions,
        help="Filter leads by province/region."
    )
    
    # 3. Crop Type Filter
    # Standardize to title case for cleaner filter presentation
    df_display = df.copy()
    df_display["Crop_Type_Display"] = df_display["Crop_Type"].str.title()
    all_crops = sorted(df_display["Crop_Type_Display"].unique())
    
    selected_crops = st.sidebar.multiselect(
        "Crop Type",
        options=all_crops,
        default=all_crops,
        help="Filter by crops grown by the farmers."
    )
    
    # 4. Farm Scale Filter
    all_scales = sorted(df_display["Farm_Scale"].unique())
    selected_scales = st.sidebar.multiselect(
        "Farm Scale",
        options=all_scales,
        default=all_scales,
        help="Filter by total crop acreage category."
    )
    
    # 5. Lead Score Slider
    min_score = float(df_display["Lead_Score"].min())
    max_score = float(df_display["Lead_Score"].max())
    
    score_range = st.sidebar.slider(
        "Lead Score Range",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score),
        step=1.0,
        help="Select the minimum and maximum lead score boundaries."
    )
    
    # Apply filters sequentially
    filtered_df = df_display[
        (df_display["Lead_Category"].isin(selected_categories)) &
        (df_display["Region"].isin(selected_regions)) &
        (df_display["Crop_Type_Display"].isin(selected_crops)) &
        (df_display["Farm_Scale"].isin(selected_scales)) &
        (df_display["Lead_Score"] >= score_range[0]) &
        (df_display["Lead_Score"] <= score_range[1])
    ]
    
    # Drop temp display column before returning
    filtered_df = filtered_df.drop(columns=["Crop_Type_Display"])
    
    return filtered_df
