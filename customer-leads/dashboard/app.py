"""Premium Main Streamlit Dashboard App for SAF SHIKAN Lead Portal.

Provides a corporate-grade, executive dashboard for lead scoring, K-means segments,
and dynamic grouped aggregations with realistic executive UI styling.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Configure page layout and visual metadata
st.set_page_config(
    page_title="SAF SHIKAN | Sales Intelligence Portal",
    page_icon="SAF",
    layout="wide",
    initial_sidebar_state="auto"
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
    from components.filters import render_sidebar_filters
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
    from dashboard.components.filters import render_sidebar_filters
    from dashboard.components.tables import (
        display_leads_table, 
        generate_excel_bytes,
        display_grouped_table
    )

# Inject custom brand styling (SAF SHIKAN green theme)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium Title Banner */
    .banner-container {
        background: linear-gradient(135deg, #1B5E20 0%, #33691E 100%);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: #FFFFFF;
        border-left: 6px solid #81C784;
    }
    .banner-title {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }
    .banner-subtitle {
        margin: 6px 0 0 0;
        font-size: 1.05rem;
        font-family: 'Inter', sans-serif;
        color: #DCEDC8;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Metrics Grid */
    .metric-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
        flex-wrap: wrap;
        width: 100%;
    }
    .metric-card {
        flex: 1;
        min-width: 220px;
        background: #FFFFFF;
        border-radius: 12px;
        padding: 22px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        display: flex;
        align-items: center;
        gap: 18px;
        border: 1px solid #ECEFF1;
        border-left: 6px solid #2E7D32;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    .metric-card.total {
        border-left-color: #2E7D32;
        background: linear-gradient(135deg, #F1F8E9 0%, #FFFFFF 100%);
    }
    .metric-card.hot {
        border-left-color: #D32F2F;
        background: linear-gradient(135deg, #FFEBEE 0%, #FFFFFF 100%);
    }
    .metric-card.warm {
        border-left-color: #E65100;
        background: linear-gradient(135deg, #FFF3E0 0%, #FFFFFF 100%);
    }
    .metric-card.avg {
        border-left-color: #0288D1;
        background: linear-gradient(135deg, #E1F5FE 0%, #FFFFFF 100%);
    }
    .metric-card .icon-box {
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-card .label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #546E7A;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-family: 'Inter', sans-serif;
    }
    .metric-card .value {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
        color: #263238;
        margin-top: 2px;
    }
    .metric-card .desc {
        font-size: 0.75rem;
        color: #78909C;
        margin-top: 3px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Segment Cards */
    .segment-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #ECEFF1;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
        transition: all 0.25s ease;
    }
    .segment-card:hover {
        border-color: #C8E6C9;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }
    .segment-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .segment-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
    }
    .segment-badge.high-need {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .segment-badge.mod-need {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    .segment-stats {
        display: flex;
        gap: 20px;
        font-size: 0.82rem;
        color: #455A64;
        border-top: 1px solid #F1F4F5;
        padding-top: 12px;
        margin-top: 15px;
        font-family: 'Inter', sans-serif;
    }
    .stat-tag {
        background: #F8F9FA;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #E9ECEF;
    }
    
    /* Mobile & Tablet Responsive Rules for Executive UI */
    @media screen and (max-width: 768px) {
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-bottom: 2rem !important;
        }
        .banner-container {
            padding: 18px 14px;
            margin-bottom: 15px;
            border-left-width: 4px;
        }
        .banner-title {
            font-size: 1.35rem;
            line-height: 1.25;
        }
        .banner-subtitle {
            font-size: 0.82rem;
            margin-top: 6px;
        }
        .metric-container {
            flex-direction: column;
            gap: 12px;
            margin-bottom: 20px;
        }
        .metric-card {
            min-width: 100%;
            width: 100%;
            padding: 16px 14px;
            gap: 14px;
        }
        .metric-card .icon-box {
            width: 44px;
            height: 44px;
            min-width: 44px;
        }
        .metric-card .value {
            font-size: 1.6rem;
        }
        .segment-card {
            padding: 16px;
            margin-bottom: 14px;
        }
        .segment-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }
        .segment-stats {
            flex-direction: column;
            gap: 8px;
            align-items: stretch;
        }
        .stat-tag {
            width: 100%;
            display: block;
            text-align: left;
            box-sizing: border-box;
        }
        /* Ensure tables scroll smoothly on mobile screens */
        [data-testid="stDataFrame"] {
            width: 100%;
            overflow-x: auto;
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

# Sidebar Navigation and Branding
st.sidebar.image(
    "https://images.unsplash.com/photo-1527525447980-6e61a7409a3c?auto=format&fit=crop&q=80&w=400",
    caption="SAF SHIKAN Agro-Drone Services",
    use_container_width=True
)

st.sidebar.title("SAF SHIKAN")
st.sidebar.caption("Lead Scoring & Segmentation System")

page = st.sidebar.radio(
    "Select Interface Page",
    ["Overview Dashboard", "Customer Segments", "Interactive Lead List", "Priority Sales Pipeline"]
)

# Render Styled Header Banner
st.markdown(
    """
    <div class='banner-container'>
        <h1 class='banner-title'>SAF SHIKAN AGRO-DRONE INTELLIGENCE</h1>
        <p class='banner-subtitle'>Precision Spray Services & Customer Analytics Hub — Islamabad Pakistan</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- PAGE 1: OVERVIEW -----------------
if page == "Overview Dashboard":
    st.subheader("Enterprise Operations Overview")
    
    # Calculate metrics
    total_cust = len(df)
    hot_count = len(df[df["Lead_Category"] == "HOT"])
    warm_count = len(df[df["Lead_Category"] == "WARM"])
    avg_score = df["Lead_Score"].mean()
    
    # SVG Vector Icons for Executive Styling
    svg_users = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>"""
    svg_hot = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#D32F2F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>"""
    svg_warm = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#E65100" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""
    svg_score = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0288D1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""
    
    # Render customized HTML metrics grid
    st.markdown(
        f"""
        <div class='metric-container'>
            <div class='metric-card total'>
                <div class='icon-box'>{svg_users}</div>
                <div class='content'>
                    <div class='label'>Farmer Leads</div>
                    <div class='value'>{total_cust}</div>
                    <div class='desc'>Registered customer profiles</div>
                </div>
            </div>
            <div class='metric-card hot'>
                <div class='icon-box'>{svg_hot}</div>
                <div class='content'>
                    <div class='label'>Hot Pipeline</div>
                    <div class='value'>{hot_count}</div>
                    <div class='desc'>High priority targets</div>
                </div>
            </div>
            <div class='metric-card warm'>
                <div class='icon-box'>{svg_warm}</div>
                <div class='content'>
                    <div class='label'>Warm Opportunities</div>
                    <div class='value'>{warm_count}</div>
                    <div class='desc'>Near-term conversion potential</div>
                </div>
            </div>
            <div class='metric-card avg'>
                <div class='icon-box'>{svg_score}</div>
                <div class='content'>
                    <div class='label'>Avg Lead Score</div>
                    <div class='value'>{avg_score:.1f}</div>
                    <div class='desc'>Normalized score out of 100</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Chart visual layouts
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        st.plotly_chart(plot_lead_category_distribution(df), use_container_width=True)
        
    with c_col2:
        st.plotly_chart(plot_customers_by_region(df), use_container_width=True)


# ----------------- PAGE 2: CUSTOMER SEGMENTS -----------------
elif page == "Customer Segments":
    st.subheader("Dynamic Customer Clustering Segments")
    st.write("Target segments generated from K-Means Clustering on operational scores.")
    
    # Split scatter plot and crop distributions
    st.plotly_chart(plot_cluster_scatter_2d(df), use_container_width=True)
    st.plotly_chart(plot_crops_per_cluster(df), use_container_width=True)
    
    st.write("### Segment Profiles & Characteristics")
    
    # Pre-calculate profiling metrics from dataset
    profile_rows = []
    scores_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    
    for cluster_name in sorted(df["Cluster_Name"].unique()):
        c_df = df[df["Cluster_Name"] == cluster_name]
        mean_area = c_df["Crop_Area"].mean()
        mean_income = c_df["Estimated_Income"].mean()
        
        # Segment description templates
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
        
    # Render segment profiles in modern styled cards (2 columns grid)
    card_cols = st.columns(2)
    for idx, card in enumerate(profile_rows):
        col = card_cols[idx % 2]
        badge_class = "high-need" if card["need"] == "High" else "mod-need"
        
        with col:
            st.markdown(
                f"""
                <div class='segment-card'>
                    <div class='segment-header'>
                        <h3 style='margin:0; font-size:1.15rem; color:#1B5E20; font-weight:700;'>{card["name"]}</h3>
                        <span class='segment-badge {badge_class}'>{card["need"]} Drone Need</span>
                    </div>
                    <p style='font-size:0.88rem; color:#546E7A; margin: 10px 0;'>
                        Target farmer grouping focused on <strong>{card["crop"].title()}</strong> cultivations in <strong>{card["region"]}</strong> region during <strong>{card["season"]}</strong> season.
                    </p>
                    <div class='segment-stats'>
                        <span class='stat-tag'><strong>Segment Size:</strong> {card["size"]} profiles</span>
                        <span class='stat-tag'><strong>Avg Scale:</strong> {card["area"]} Acres</span>
                        <span class='stat-tag'><strong>Avg Revenue:</strong> PKR {int(card["income"]):,}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ----------------- PAGE 3: LEAD LIST -----------------
elif page == "Interactive Lead List":
    st.subheader("Dynamic Sales Pipeline Finder")
    st.write("Configure filters in the left sidebar to slice, group, or export sales targets.")
    
    # Filter dataset using the sidebar component
    filtered_df = render_sidebar_filters(df)
    
    # Tabbed layouts: 1 for data list, 1 for data aggregations (Groupings)
    tab_list, tab_group = st.tabs(["Filtered Lead Records", "Interactive Data Groupings"])
    
    with tab_list:
        st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** matching records:")
        
        # Display the formatted data table
        display_leads_table(filtered_df)
        
        st.write("")
        # Download actions
        col_dl1, col_dl2, _ = st.columns([1.8, 1.8, 5])
        
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        with col_dl1:
            st.download_button(
                label="Export Pipeline as CSV",
                data=csv_data,
                file_name="saf_shikan_leads_export.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        excel_bytes = generate_excel_bytes(filtered_df)
        with col_dl2:
            st.download_button(
                label="Export Pipeline as Styled Excel",
                data=excel_bytes,
                file_name="saf_shikan_leads_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    with tab_group:
        st.write("### Group & Aggregate Analytics")
        st.write("Select a category to group lead counts and aggregate scores or sizes dynamically.")
        
        g_col1, g_col2, g_col3 = st.columns(3)
        group_by = g_col1.selectbox(
            "Group Columns By", 
            ["Region", "Crop_Type", "Season", "Farm_Scale", "Lead_Category"],
            help="Categorical column to aggregate records on."
        )
        metric = g_col2.selectbox(
            "Aggregate Field Value", 
            ["Lead_Score", "Crop_Area", "Estimated_Income"],
            help="Numerical column to summarize."
        )
        operation = g_col3.selectbox(
            "Mathematical Operation", 
            ["mean", "sum", "count"],
            help="Summarization function to calculate."
        )
        
        st.write("---")
        
        # Display grouped statistics table (styled)
        display_grouped_table(filtered_df, group_by)
        
        st.write("")
        
        # Display dynamic grouped visualization
        st.plotly_chart(plot_grouped_analytics(filtered_df, group_by, metric, operation), use_container_width=True)


# ----------------- PAGE 4: PRIORITY SALES PIPELINE -----------------
elif page == "Priority Sales Pipeline":
    st.subheader("Top 20 Priority Sales Call List")
    st.write("Highest priority targets representing active crop areas requiring urgent spray scheduling.")
    
    # Filter HOT leads only
    hot_df = df[df["Lead_Category"] == "HOT"].copy()
    top_20_hot = hot_df.head(20)
    
    # Display table (phone numbers visible)
    display_leads_table(top_20_hot)
    
    st.write("")
    
    # Export call list
    excel_bytes = generate_excel_bytes(top_20_hot)
    st.download_button(
        label="Export Calling List to Styled Excel",
        data=excel_bytes,
        file_name="saf_shikan_hot_call_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
