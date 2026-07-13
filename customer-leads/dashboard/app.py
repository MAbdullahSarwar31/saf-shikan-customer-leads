"""Main Streamlit Dashboard App for SAF SHIKAN Lead Scoring & Segmentation.

Provides an interactive portal for the sales team to filter, visualize, and export leads.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Configure page layout and style
st.set_page_config(
    page_title="SAF SHIKAN | Sales Lead Portal",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
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
        plot_crops_per_cluster
    )
    from components.filters import render_sidebar_filters
    from components.tables import display_leads_table, generate_excel_bytes
except ImportError:
    # Fallback if imported directly from python command
    from dashboard.components.charts import (
        plot_lead_category_distribution,
        plot_customers_by_region,
        plot_cluster_scatter_2d,
        plot_crops_per_cluster
    )
    from dashboard.components.filters import render_sidebar_filters
    from dashboard.components.tables import display_leads_table, generate_excel_bytes

# Inject custom brand styling (SAF SHIKAN green `#1B5E20`)
st.markdown(
    """
    <style>
    .main-title {
        color: #1B5E20;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #558B2F;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-top: -10px;
        margin-bottom: 25px;
        font-size: 1.15rem;
    }
    .metric-card {
        background-color: #F1F8E9;
        border-left: 5px solid #2E7D32;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #558B2F;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        color: #1B5E20;
        font-weight: 800;
    }
    .segment-card {
        background-color: #FAFAFA;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        padding: 15px;
        margin-bottom: 10px;
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

st.sidebar.title("🛸 SAF SHIKAN")
st.sidebar.caption("Lead Scoring & Segmentation System")

page = st.sidebar.radio(
    "Go to Page",
    ["📊 Overview Dashboard", "🎯 Customer Segments", "📋 Interactive Lead List", "🔥 Top Hot Leads"]
)

# Header Section
st.markdown("<h1 class='main-title'>SAF SHIKAN 🛸</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Agro-Drone Spray Services — Islamabad Pakistan</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- PAGE 1: OVERVIEW -----------------
if page == "📊 Overview Dashboard":
    st.subheader("Business Metrics Overview")
    
    # Calculate high-level metrics
    total_cust = len(df)
    hot_count = len(df[df["Lead_Category"] == "HOT"])
    warm_count = len(df[df["Lead_Category"] == "WARM"])
    avg_score = df["Lead_Score"].mean()
    
    # Metrics columns
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>TOTAL FARM CUSTOMERS</div>
                <div class='metric-value'>{total_cust}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with m_col2:
        st.markdown(
            f"""
            <div class='metric-card' style='border-left-color: #B71C1C; background-color: #FFEBEE;'>
                <div class='metric-title' style='color: #C62828;'>HOT LEADS 🔥</div>
                <div class='metric-value' style='color: #B71C1C;'>{hot_count}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with m_col3:
        st.markdown(
            f"""
            <div class='metric-card' style='border-left-color: #E65100; background-color: #FFF3E0;'>
                <div class='metric-title' style='color: #EF6C00;'>WARM LEADS ✅</div>
                <div class='metric-value' style='color: #E65100;'>{warm_count}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with m_col4:
        st.markdown(
            f"""
            <div class='metric-card' style='border-left-color: #0D47A1; background-color: #E3F2FD;'>
                <div class='metric-title' style='color: #1565C0;'>AVG LEAD SCORE</div>
                <div class='metric-value' style='color: #0D47A1;'>{avg_score:.2f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    st.write("")
    st.write("")
    
    # Chart Row
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        st.plotly_chart(plot_lead_category_distribution(df), use_container_width=True)
        
    with c_col2:
        st.plotly_chart(plot_customers_by_region(df), use_container_width=True)


# ----------------- PAGE 2: CUSTOMER SEGMENTS -----------------
elif page == "🎯 Customer Segments":
    st.subheader("Customer Clustering Profiles")
    st.write("Segments generated from unsupervised Machine Learning (K-Means Clustering).")
    
    # PCA Plot
    st.plotly_chart(plot_cluster_scatter_2d(df), use_container_width=True)
    
    # Crop Distribution
    st.plotly_chart(plot_crops_per_cluster(df), use_container_width=True)
    
    # Segment Characteristics and Summaries
    st.write("### Segment Profiling Table")
    
    # Build profiling table dynamically from dataset
    scores_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    
    profiles = []
    for cluster_name in sorted(df["Cluster_Name"].unique()):
        c_df = df[df["Cluster_Name"] == cluster_name]
        profiles.append({
            "Customer Segment": cluster_name,
            "Size": len(c_df),
            "Avg Area (Acres)": round(c_df["Crop_Area"].mean(), 1),
            "Avg Income (PKR)": f"{int(c_df['Estimated_Income'].mean()):,}",
            "Dominant Crop": c_df["Crop_Type"].mode()[0].title(),
            "Dominant Region": c_df["Region"].mode()[0],
            "Dominant Season": c_df["Season"].mode()[0],
            "Drone Need Level": "High" if c_df["Drone_Service_Potential"].mean() >= 8.0 else "Moderate"
        })
        
    st.table(pd.DataFrame(profiles))


# ----------------- PAGE 3: LEAD LIST -----------------
elif page == "📋 Interactive Lead List":
    st.subheader("Sales Pipeline & Lead Search")
    st.write("Configure filters in the left sidebar to target specific crop sectors, farm sizes, or regions.")
    
    # Render filters and get filtered df
    filtered_df = render_sidebar_filters(df)
    
    st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** matching customers:")
    
    # Render table
    display_leads_table(filtered_df)
    
    st.write("")
    
    # Download actions
    col_dl1, col_dl2, _ = st.columns([1.5, 1.5, 5])
    
    # CSV Download
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    with col_dl1:
        st.download_button(
            label="📥 Download CSV Pipeline",
            data=csv_data,
            file_name="saf_shikan_filtered_leads.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # Excel Download
    excel_bytes = generate_excel_bytes(filtered_df)
    with col_dl2:
        st.download_button(
            label="📥 Download Styled Excel Workbook",
            data=excel_bytes,
            file_name="saf_shikan_filtered_leads.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ----------------- PAGE 4: TOP LEADS -----------------
elif page == "🔥 Top Hot Leads":
    st.subheader("Top 20 Hot Leads Calling List")
    st.write("These farmers are the highest potential leads for drone spraying based on their massive crop scales, pesticide intensive crops (e.g. Cotton, Rice), and double-cropping seasons.")
    
    # Filter HOT leads only
    hot_df = df[df["Lead_Category"] == "HOT"].copy()
    
    # Take top 20
    top_20_hot = hot_df.head(20)
    
    # Render table
    display_leads_table(top_20_hot)
    
    st.write("")
    
    # Excel Download button
    excel_bytes = generate_excel_bytes(top_20_hot)
    st.download_button(
        label="📥 Export Call List to Styled Excel",
        data=excel_bytes,
        file_name="saf_shikan_top_20_hot_leads.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
