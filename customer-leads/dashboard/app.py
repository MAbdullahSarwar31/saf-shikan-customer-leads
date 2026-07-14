"""AGRON - SAF SHIKAN Admin Portal Friendly Lead Scoring Dashboard.

Designed specifically for seamless integration into the AGRON Admin Dashboard as a single cohesive tab.
Mirrors the exact visual design system of the AGRON Portal (Screenshots 1, 2, & 3):
- Soft off-white portal background (#F8FAF9)
- AGRON page header & typography
- AGRON console metric cards with colored dot indicators
- AGRON pill-style tab bar navigation
- Embedded inline filters and search bar (no sidebar reliance)
"""

import os
import sys
import pandas as pd
import streamlit as st

# Configure page layout for seamless AGRON Admin Dashboard embedding
st.set_page_config(
    page_title="SAF SHIKAN | Customer Leads Intelligence",
    page_icon="SAF",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Resolve project root relative to app.py
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Add PROJECT_ROOT and components directory to sys.path
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(APP_DIR, "components"))

# Import custom components and helpers
try:
    from components.charts import (
        plot_lead_category_distribution,
        plot_customers_by_region,
        plot_cluster_scatter_2d,
        plot_crops_per_cluster,
        plot_grouped_analytics
    )
    from components.tables import (
        display_leads_table, 
        generate_excel_bytes,
        display_grouped_table
    )
except ImportError:
    from dashboard.components.charts import (
        plot_lead_category_distribution,
        plot_customers_by_region,
        plot_cluster_scatter_2d,
        plot_crops_per_cluster,
        plot_grouped_analytics
    )
    from dashboard.components.tables import (
        display_leads_table, 
        generate_excel_bytes,
        display_grouped_table
    )

# Inject AGRON Portal Design System CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Outfit', -apple-system, sans-serif;
        background-color: #F8FAF9 !important;
        color: #0F172A;
    }
    
    /* Hide extra default Streamlit top padding when embedded */
    .block-container {
        padding-top: 1.8rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 100% !important;
    }
    
    /* AGRON Page Header (Screenshot 1 & 2 style) */
    .agron-page-header {
        margin-bottom: 24px;
    }
    .agron-page-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.5px;
        font-family: 'Outfit', sans-serif;
    }
    .agron-page-subtitle {
        font-size: 0.92rem;
        color: #64748B;
        margin: 4px 0 0 0;
        font-weight: 400;
    }
    
    /* AGRON Metric Grid (Screenshot 2 / Console style) */
    .agron-metric-grid {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
        flex-wrap: wrap;
        width: 100%;
    }
    .agron-card {
        flex: 1;
        min-width: 220px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .agron-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .agron-card-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .agron-card-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        margin: 4px 0 6px 0;
        font-family: 'Outfit', sans-serif;
        line-height: 1.1;
    }
    .agron-card-footer {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        color: #64748B;
    }
    .agron-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .agron-dot.green { background-color: #10B981; }
    .agron-dot.red { background-color: #EF4444; }
    .agron-dot.amber { background-color: #F59E0B; }
    .agron-dot.blue { background-color: #3B82F6; }
    
    /* AGRON Pill Navigation Tabs (Matching Screenshot 1 active pill buttons) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 8px;
        padding: 0 20px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #64748B;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0F172A;
        background-color: #F1F5F9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0C3823 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(12, 56, 35, 0.2);
    }
    
    /* Container Cards */
    .agron-section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .agron-section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .agron-section-subtitle {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 16px;
    }
    
    /* Segment Card Styling */
    .segment-portal-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }
    .segment-portal-card:hover {
        border-color: #10B981;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
    }
    .segment-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .segment-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .segment-pill {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    .segment-pill.high {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .segment-pill.mod {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .segment-desc {
        font-size: 0.86rem;
        color: #475569;
        margin-bottom: 14px;
    }
    .segment-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .segment-tag {
        background: #F8FAF9;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 0.78rem;
        color: #334155;
    }
    
    /* Mobile Responsiveness */
    @media screen and (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem !important;
        }
        .agron-metric-grid {
            flex-direction: column;
            gap: 12px;
        }
        .agron-card {
            min-width: 100%;
            width: 100%;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_data():
    """Load final processed lead dataset.
    
    Returns:
        DataFrame.
    """
    data_path = os.path.join(PROJECT_ROOT, "data", "processed", "customers_final.csv")
    if not os.path.exists(data_path):
        st.error(f"Scored dataset not found at: {data_path}. Please run scorer.py first.")
        st.stop()
    return pd.read_csv(data_path)


# Load dataset
df = load_data()

# Optional Collapsed Sidebar for Brand Info
st.sidebar.caption("SAF SHIKAN AGRON INTEGRATION")
st.sidebar.write("Integrated Lead Intelligence Module v2.0")

# 1. AGRON Portal Header (matching Screenshot 1)
st.markdown(
    """
    <div class='agron-page-header'>
        <h1 class='agron-page-title'>Customer Leads Intelligence</h1>
        <p class='agron-page-subtitle'>Manage and track AI-scored farmer leads, segment clusters, and precision spray opportunities</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. AGRON Portal Executive Metrics Grid (matching Screenshot 2 & 3)
total_cust = len(df)
hot_count = len(df[df["Lead_Category"] == "HOT"])
warm_count = len(df[df["Lead_Category"] == "WARM"])
avg_score = df["Lead_Score"].mean()

st.markdown(
    f"""
    <div class='agron-metric-grid'>
        <div class='agron-card'>
            <div class='agron-card-label'>Total Farmer Leads</div>
            <div class='agron-card-value'>{total_cust:,}</div>
            <div class='agron-card-footer'>
                <span class='agron-dot green'></span>
                <span>Registered farmer profiles</span>
            </div>
        </div>
        <div class='agron-card'>
            <div class='agron-card-label'>Hot Pipeline (48h)</div>
            <div class='agron-card-value'>{hot_count:,}</div>
            <div class='agron-card-footer'>
                <span class='agron-dot red'></span>
                <span>Urgent spray opportunity</span>
            </div>
        </div>
        <div class='agron-card'>
            <div class='agron-card-label'>Warm Opportunities</div>
            <div class='agron-card-value'>{warm_count:,}</div>
            <div class='agron-card-footer'>
                <span class='agron-dot amber'></span>
                <span>Active engagement targets</span>
            </div>
        </div>
        <div class='agron-card'>
            <div class='agron-card-label'>Average Lead Score</div>
            <div class='agron-card-value'>{avg_score:.1f}</div>
            <div class='agron-card-footer'>
                <span class='agron-dot blue'></span>
                <span>Normalized score out of 100</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. AGRON Module Navigation Tabs (Single-Page Seamless Experience)
tab_leads, tab_segments, tab_analytics, tab_priority = st.tabs([
    "Leads Directory & Scoring",
    "Customer Segmentation (AI)",
    "Grouped Analytics",
    "Priority Call List"
])


# ================== TAB 1: LEADS DIRECTORY & SCORING ==================
with tab_leads:
    # Inline AGRON Filter Control Bar (Mirrors Screenshot 1 Orders Search & Pills)
    f_col1, f_col2, f_col3, f_col4 = st.columns([2.5, 1.5, 1.3, 1.3])
    
    with f_col1:
        search_query = st.text_input(
            "Search Leads",
            placeholder="Search by Farmer Name, Phone, or Location...",
            label_visibility="collapsed"
        )
    
    with f_col2:
        all_cats = ["All Categories"] + sorted(df["Lead_Category"].unique().tolist())
        selected_cat = st.selectbox("Priority Category", all_cats, label_visibility="collapsed")
        
    with f_col3:
        all_regions = ["All Regions"] + sorted(df["Region"].unique().tolist())
        selected_region = st.selectbox("Region", all_regions, label_visibility="collapsed")
        
    with f_col4:
        df_crop_display = df["Crop_Type"].str.title()
        all_crops = ["All Crops"] + sorted(df_crop_display.unique().tolist())
        selected_crop = st.selectbox("Crop Type", all_crops, label_visibility="collapsed")
        
    # Apply Inline Filters
    filtered_df = df.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["Name"].str.lower().str.contains(q, na=False) |
            filtered_df["Phone"].str.lower().str.contains(q, na=False) |
            filtered_df["Location"].str.lower().str.contains(q, na=False)
        ]
    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["Lead_Category"] == selected_cat]
    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]
    if selected_crop != "All Crops":
        filtered_df = filtered_df[filtered_df["Crop_Type"].str.title() == selected_crop]
        
    st.write(f"Showing **{len(filtered_df):,}** of **{len(df):,}** customer lead records:")
    
    # Display sortable datatable
    display_leads_table(filtered_df)
    
    st.write("")
    
    # Export Actions
    dl_col1, dl_col2, _ = st.columns([1.8, 1.8, 4.4])
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    with dl_col1:
        st.download_button(
            label="Export Filtered Leads (CSV)",
            data=csv_data,
            file_name="saf_shikan_leads_export.csv",
            mime="text/csv",
            use_container_width=True
        )
    excel_bytes = generate_excel_bytes(filtered_df)
    with dl_col2:
        st.download_button(
            label="Export Filtered Leads (Styled Excel)",
            data=excel_bytes,
            file_name="saf_shikan_leads_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ================== TAB 2: CUSTOMER SEGMENTATION (AI) ==================
with tab_segments:
    st.markdown(
        """
        <div class='agron-section-card' style='margin-bottom: 16px;'>
            <div class='agron-section-title'>AI K-Means Customer Clustering</div>
            <div class='agron-section-subtitle'>Target farmer segments dynamically identified from operational scores and crop scale matrices</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Visual Cluster Projections
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_cluster_scatter_2d(df), use_container_width=True)
    with c2:
        st.plotly_chart(plot_crops_per_cluster(df), use_container_width=True)
        
    st.write("### Target Segment Profiles")
    
    # Pre-calculate profiling metrics
    profile_rows = []
    for cluster_name in sorted(df["Cluster_Name"].unique()):
        c_df = df[df["Cluster_Name"] == cluster_name]
        mean_area = c_df["Crop_Area"].mean()
        mean_income = c_df["Estimated_Income"].mean()
        dominant_crop = c_df["Crop_Type"].mode()[0]
        dominant_region = c_df["Region"].mode()[0]
        dominant_season = c_df["Season"].mode()[0]
        drone_need = "High" if c_df["Drone_Service_Potential"].mean() >= 8.0 else "Moderate"
        
        profile_rows.append({
            "name": cluster_name,
            "size": len(c_df),
            "area": round(mean_area, 1),
            "income": mean_income,
            "crop": dominant_crop,
            "region": dominant_region,
            "season": dominant_season,
            "need": drone_need
        })
        
    card_cols = st.columns(2)
    for idx, card in enumerate(profile_rows):
        col = card_cols[idx % 2]
        pill_class = "high" if card["need"] == "High" else "mod"
        
        with col:
            st.markdown(
                f"""
                <div class='segment-portal-card'>
                    <div class='segment-header-row'>
                        <h4 class='segment-name'>{card["name"]}</h4>
                        <span class='segment-pill {pill_class}'>{card["need"]} Drone Need</span>
                    </div>
                    <p class='segment-desc'>
                        Focusing on <strong>{card["crop"].title()}</strong> cultivations in <strong>{card["region"]}</strong> region during <strong>{card["season"]}</strong> season.
                    </p>
                    <div class='segment-tags'>
                        <span class='segment-tag'><strong>Segment Size:</strong> {card["size"]} profiles</span>
                        <span class='segment-tag'><strong>Avg Scale:</strong> {card["area"]} Acres</span>
                        <span class='segment-tag'><strong>Avg Revenue:</strong> PKR {int(card["income"]):,}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ================== TAB 3: GROUPED ANALYTICS ==================
with tab_analytics:
    st.markdown(
        """
        <div class='agron-section-card'>
            <div class='agron-section-title'>Multi-Dimensional Grouping Analytics</div>
            <div class='agron-section-subtitle'>Aggregate farmer counts, average lead scores, and total crop areas across operational categories</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    g_col1, g_col2, g_col3 = st.columns(3)
    group_by = g_col1.selectbox(
        "Group Column By",
        ["Region", "Crop_Type", "Season", "Farm_Scale", "Lead_Category"],
        help="Categorical column to aggregate records on."
    )
    metric = g_col2.selectbox(
        "Aggregate Metric",
        ["Lead_Score", "Crop_Area", "Estimated_Income"],
        help="Numerical column to summarize."
    )
    operation = g_col3.selectbox(
        "Mathematical Operation",
        ["mean", "sum", "count"],
        help="Summarization function to calculate."
    )
    
    st.write("---")
    
    # Display grouped table and chart
    display_grouped_table(df, group_by)
    st.write("")
    st.plotly_chart(plot_grouped_analytics(df, group_by, metric, operation), use_container_width=True)


# ================== TAB 4: PRIORITY CALL LIST ==================
with tab_priority:
    st.markdown(
        """
        <div class='agron-section-card'>
            <div class='agron-section-title'>Top 20 Urgent Sales Call List</div>
            <div class='agron-section-subtitle'>Highest priority HOT leads requiring immediate outbound calling and drone spray scheduling within 48 hours</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    hot_df = df[df["Lead_Category"] == "HOT"].copy()
    top_20_hot = hot_df.head(20)
    
    display_leads_table(top_20_hot)
    st.write("")
    
    excel_hot = generate_excel_bytes(top_20_hot)
    st.download_button(
        label="Export Priority Calling List (Styled Excel)",
        data=excel_hot,
        file_name="saf_shikan_priority_call_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
