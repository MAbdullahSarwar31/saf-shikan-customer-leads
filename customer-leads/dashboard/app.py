"""SAF SHIKAN Farmer Data Portal — AGRON Admin Integration Module.

Open-source farmer data directory with filtering, grouping analytics, and export.
Data source: customers.csv (raw, no preprocessing pipeline).
Core columns: Name, Phone, Crop_Type, Crop_Area, Season, Region.
No AI scoring, no lead categories, no ML pipeline required.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAF SHIKAN | Farmer Data Portal",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Path Resolution ──────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "customers.csv")

# ─── AGRON Portal Design System CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F8FAF9 !important;
    color: #0F172A;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 100% !important;
}

/* ── Page Header ─────────────────────────────────────── */
.page-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: #0F172A;
    margin: 0 0 4px 0;
    letter-spacing: -0.4px;
}
.page-subtitle {
    font-size: 0.92rem;
    color: #64748B;
    margin: 0 0 24px 0;
    font-weight: 400;
}

/* ── Stat Cards ──────────────────────────────────────── */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1;
    min-width: 180px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: box-shadow 0.2s ease;
}
.stat-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.stat-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    color: #64748B;
    margin-bottom: 6px;
}
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 6px;
}
.stat-footer {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.78rem;
    color: #64748B;
}
.dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; display:inline-block; }
.dot-green  { background:#10B981; }
.dot-amber  { background:#F59E0B; }
.dot-blue   { background:#3B82F6; }
.dot-purple { background:#8B5CF6; }
.dot-teal   { background:#14B8A6; }
.dot-rose   { background:#F43F5E; }

/* ── AGRON Pill Tabs ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 7px 10px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.stTabs [data-baseweb="tab"] {
    height: 36px;
    border-radius: 8px;
    padding: 0 18px;
    font-size: 0.87rem;
    font-weight: 600;
    color: #64748B;
    transition: all 0.18s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0F172A;
    background-color: #F1F5F9;
}
.stTabs [aria-selected="true"] {
    background-color: #0C3823 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(12,56,35,0.25);
}

/* Hide default red highlight lines under active tab in Streamlit */
div[data-baseweb="tab-highlight"], 
div[data-baseweb="tab-border"], 
.stTabs [data-baseweb="tab-highlight"], 
.stTabs [data-baseweb="tab-border"] {
    background-color: transparent !important;
    display: none !important;
    height: 0px !important;
}

/* Custom styled inputs and dropdowns to replace default theme colors (e.g. red outlines) */
div[data-baseweb="select"] > div {
    border: 1px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #CBD5E1 !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #0C3823 !important;
    box-shadow: 0 0 0 1px #0C3823 !important;
}

/* Remove validation or primary theme red focus states from selectboxes and text inputs */
div[role="combobox"] {
    outline: none !important;
}
div[data-testid="stTextInput"] input {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #0C3823 !important;
    box-shadow: 0 0 0 1px #0C3823 !important;
}
input:focus, textarea:focus, select:focus {
    outline: none !important;
    border-color: #0C3823 !important;
    box-shadow: 0 0 0 1px #0C3823 !important;
}
div[data-baseweb="base-input"] {
    border-color: transparent !important;
}
button:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* ── Section Card ────────────────────────────────────── */
.section-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 4px 0;
}
.section-sub {
    font-size: 0.84rem;
    color: #64748B;
    margin: 0 0 14px 0;
}

/* ── Group Summary Row Cards ─────────────────────────── */
.group-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    background: #FFFFFF;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.group-row:hover { border-color: #10B981; }
.group-row-label { font-weight: 600; color: #0F172A; font-size: 0.95rem; }
.group-row-badge {
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
}
.badge-green { background:#D1FAE5; color:#065F46; }
.badge-blue  { background:#DBEAFE; color:#1E3A8A; }
.badge-amber { background:#FEF3C7; color:#92400E; }

/* ── Mobile ──────────────────────────────────────────── */
@media screen and (max-width: 768px) {
    .block-container { padding: 1rem 0.8rem !important; }
    .stats-row { flex-direction: column; gap: 12px; }
    .stat-card { min-width: 100%; }
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; }
}
</style>
""", unsafe_allow_html=True)


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load raw farmer data directly from customers.csv.
    
    Returns:
        DataFrame with 6 core columns: Name, Phone, Crop_Type, Crop_Area, Season, Region.
    """
    if not os.path.exists(RAW_DATA_PATH):
        st.error(f"Data file not found: {RAW_DATA_PATH}")
        st.stop()
    df = pd.read_csv(RAW_DATA_PATH)
    # Standardise casing
    df["Crop_Type"] = df["Crop_Type"].str.title()
    df["Season"]    = df["Season"].str.strip()
    df["Region"]    = df["Region"].str.strip()
    df["Location"]  = df["Location"].str.strip()
    df["Farm_Scale"]= df["Farm_Scale"].str.strip()
    return df


def generate_excel(df: pd.DataFrame) -> bytes:
    """Export filtered DataFrame to a styled Excel file.
    
    Args:
        df: Filtered farmers DataFrame.
        
    Returns:
        Excel bytes.
    """
    cols = ["Name", "Phone", "Crop_Type", "Crop_Area", "Season", "Region"]
    available = [c for c in cols if c in df.columns]
    export = df[available].copy()
    export.columns = [c.replace("_", " ") for c in available]

    wb = Workbook()
    ws = wb.active
    ws.title = "SAF SHIKAN Farmers"

    hdr_fill = PatternFill("solid", fgColor="0C3823")
    hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin = Border(
        left=Side("thin", color="E0E0E0"), right=Side("thin", color="E0E0E0"),
        top=Side("thin", color="E0E0E0"), bottom=Side("thin", color="E0E0E0")
    )
    center = Alignment(horizontal="center", vertical="center")
    left   = Alignment(horizontal="left",   vertical="center")

    ws.append(list(export.columns))
    for idx, cell in enumerate(ws[1], 1):
        cell.fill, cell.font, cell.alignment, cell.border = hdr_fill, hdr_font, center, thin

    for _, row in export.iterrows():
        ws.append(list(row))
        r = ws.max_row
        for c_idx, cell in enumerate(ws[r], 1):
            cell.border = thin
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = center if available[c_idx - 1] in ["Crop_Area", "Season", "Region", "Farm_Scale"] else left

    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        max_len = max((len(str(cell.value or "")) for cell in col), default=8)
        ws.column_dimensions[letter].width = min(max_len + 4, 40)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ─── Load & Pre-compute ───────────────────────────────────────────────────────
df = load_data()
CORE_COLS = ["Name", "Phone", "Crop_Type", "Crop_Area", "Season", "Region"]

total_farmers   = len(df)
unique_crops    = df["Crop_Type"].nunique()
unique_regions  = df["Region"].nunique()
avg_area_acres  = df["Crop_Area"].mean()
total_area      = df["Crop_Area"].sum()
unique_seasons  = df["Season"].nunique()

# ─── Page Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='page-title'>Farmer Data Directory</div>
<p class='page-subtitle'>Browse, filter, group and export SAF SHIKAN registered farmer profiles — 6 core data categories</p>
""", unsafe_allow_html=True)

# ─── Summary Stats Row ────────────────────────────────────────────────────────
st.markdown(f"""
<div class='stats-row'>
    <div class='stat-card'>
        <div class='stat-label'>Total Farmers</div>
        <div class='stat-value'>{total_farmers:,}</div>
        <div class='stat-footer'><span class='dot dot-green'></span>Registered profiles</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Crop Types</div>
        <div class='stat-value'>{unique_crops}</div>
        <div class='stat-footer'><span class='dot dot-amber'></span>Unique crop categories</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Regions Covered</div>
        <div class='stat-value'>{unique_regions}</div>
        <div class='stat-footer'><span class='dot dot-blue'></span>Punjab · Sindh · KPK</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Avg Farm Size</div>
        <div class='stat-value'>{avg_area_acres:.0f}</div>
        <div class='stat-footer'><span class='dot dot-purple'></span>Acres per farmer</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Total Crop Area</div>
        <div class='stat-value'>{total_area:,.0f}</div>
        <div class='stat-footer'><span class='dot dot-teal'></span>Acres across all profiles</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Tab Navigation ───────────────────────────────────────────────────────────
tab_dir, tab_group, tab_charts = st.tabs([
    "Farmer Directory",
    "Data Grouping & Aggregation",
    "Visual Analytics"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FARMER DIRECTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab_dir:
    # ── Inline Filter Bar ─────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns([2.8, 1.4, 1.4, 1.4])

    with f1:
        search = st.text_input(
            "Search",
            placeholder="Search by Name, Phone or Location...",
            label_visibility="collapsed"
        )
    with f2:
        region_opts = ["All Regions"] + sorted(df["Region"].unique())
        sel_region = st.selectbox("Region", region_opts, label_visibility="collapsed")
    with f3:
        crop_opts = ["All Crops"] + sorted(df["Crop_Type"].unique())
        sel_crop = st.selectbox("Crop", crop_opts, label_visibility="collapsed")
    with f4:
        season_opts = ["All Seasons"] + sorted(df["Season"].unique())
        sel_season = st.selectbox("Season", season_opts, label_visibility="collapsed")

    # ── Apply Filters ─────────────────────────────────────────────────────────
    filtered = df.copy()
    if search.strip():
        q = search.strip().lower()
        filtered = filtered[
            filtered["Name"].str.lower().str.contains(q, na=False) |
            filtered["Phone"].str.lower().str.contains(q, na=False) |
            filtered["Location"].str.lower().str.contains(q, na=False)
        ]
    if sel_region != "All Regions":
        filtered = filtered[filtered["Region"] == sel_region]
    if sel_crop != "All Crops":
        filtered = filtered[filtered["Crop_Type"] == sel_crop]
    if sel_season != "All Seasons":
        filtered = filtered[filtered["Season"] == sel_season]

    st.write(f"Showing **{len(filtered):,}** of **{total_farmers:,}** farmer records")

    # ── Farmer Directory Table (6 core columns) ───────────────────────────────
    display_df = filtered[CORE_COLS].copy()

    st.dataframe(
        display_df,
        column_config={
            "Name": st.column_config.TextColumn("Farmer Name", width="medium"),
            "Phone": st.column_config.TextColumn("Phone Number", width="medium"),
            "Crop_Type": st.column_config.TextColumn("Crop Type", width="small"),
            "Crop_Area": st.column_config.NumberColumn(
                "Farm Area (Acres)",
                format="%d acres",
                width="small"
            ),
            "Season": st.column_config.TextColumn("Season", width="small"),
            "Region": st.column_config.TextColumn("Region", width="small"),
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )

    # ── Export Actions ────────────────────────────────────────────────────────
    st.write("")
    dl1, dl2, _ = st.columns([1.6, 1.8, 4.6])
    with dl1:
        st.download_button(
            "Export as CSV",
            data=filtered[CORE_COLS].to_csv(index=False).encode("utf-8"),
            file_name="saf_shikan_farmers.csv",
            mime="text/csv",
            use_container_width=True
        )
    with dl2:
        st.download_button(
            "Export as Styled Excel",
            data=generate_excel(filtered),
            file_name="saf_shikan_farmers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA GROUPING & AGGREGATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_group:
    st.markdown("""
    <div class='section-card'>
        <div class='section-title'>Data Grouping & Aggregation</div>
        <div class='section-sub'>Group farmer records across the 6 core categories and compute farm area statistics</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Grouping Controls ─────────────────────────────────────────────────────
    g1, g2, g3 = st.columns(3)
    group_by = g1.selectbox(
        "Group By Category",
        ["Region", "Crop_Type", "Season", "Farm_Scale"],
        format_func=lambda x: x.replace("_", " "),
        help="Select one of the 6 data categories to group farmers by."
    )
    agg_metric = g2.selectbox(
        "Aggregate Field",
        ["Crop_Area", "Estimated_Income"],
        format_func=lambda x: x.replace("_", " "),
        help="Numerical field to aggregate."
    )
    agg_func = g3.selectbox(
        "Aggregation Function",
        ["count", "mean", "sum"],
        help="How to summarize the metric across each group."
    )

    st.write("---")

    # ── Compute Aggregation ───────────────────────────────────────────────────
    if agg_func == "count":
        grp = df.groupby(group_by).agg(
            Count=("Name", "count"),
            Avg_Area=("Crop_Area", "mean"),
            Total_Area=("Crop_Area", "sum")
        ).reset_index()
        grp.columns = [group_by.replace("_", " "), "Farmer Count", "Avg Area (Acres)", "Total Area (Acres)"]
        sort_col = "Farmer Count"
    elif agg_func == "mean":
        grp = df.groupby(group_by).agg(
            Count=("Name", "count"),
            Avg_Value=(agg_metric, "mean")
        ).reset_index()
        label = agg_metric.replace("_", " ")
        grp.columns = [group_by.replace("_", " "), "Farmer Count", f"Avg {label}"]
        sort_col = f"Avg {label}"
    else:  # sum
        grp = df.groupby(group_by).agg(
            Count=("Name", "count"),
            Total_Value=(agg_metric, "sum")
        ).reset_index()
        label = agg_metric.replace("_", " ")
        grp.columns = [group_by.replace("_", " "), "Farmer Count", f"Total {label}"]
        sort_col = f"Total {label}"

    grp = grp.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

    # ── Styled Aggregation Table ──────────────────────────────────────────────
    # Apply background gradient on the aggregated column
    styled = grp.style.background_gradient(
        subset=[sort_col], cmap="YlGn"
    ).format({
        col: "{:,.0f}" for col in grp.select_dtypes("number").columns
    })
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Export Grouped Summary ────────────────────────────────────────────────
    st.download_button(
        "Export Group Summary (CSV)",
        data=grp.to_csv(index=False).encode("utf-8"),
        file_name=f"saf_shikan_grouped_by_{group_by.lower()}.csv",
        mime="text/csv"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISUAL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_charts:
    FONT  = "Inter, Segoe UI, sans-serif"
    COLOR_GREEN = ["#0C3823", "#1B5E20", "#2E7D32", "#388E3C", "#43A047",
                   "#66BB6A", "#A5D6A7", "#C8E6C9"]
    LAYOUT = dict(
        font=dict(family=FONT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=30, l=10, r=10),
        title_font=dict(size=17, family=FONT, color="#0F172A")
    )

    r1c1, r1c2 = st.columns(2)

    # Chart 1 — Farmers by Region (bar)
    with r1c1:
        region_cnt = df["Region"].value_counts().reset_index()
        region_cnt.columns = ["Region", "Farmers"]
        fig1 = px.bar(
            region_cnt, x="Region", y="Farmers",
            color="Region", text="Farmers",
            color_discrete_sequence=["#0C3823", "#2E7D32", "#81C784"],
            title="Farmers by Region"
        )
        fig1.update_traces(
            textposition="outside",
            marker_cornerradius=6,
            hovertemplate="<b>%{x}</b><br>Farmers: %{y}<extra></extra>"
        )
        fig1.update_layout(**LAYOUT, showlegend=False, height=320)
        fig1.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
        fig1.update_xaxes(showgrid=False)
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2 — Crop Type Distribution (donut)
    with r1c2:
        crop_cnt = df["Crop_Type"].value_counts().reset_index()
        crop_cnt.columns = ["Crop", "Farmers"]
        fig2 = px.pie(
            crop_cnt, names="Crop", values="Farmers",
            hole=0.55,
            title="Crop Type Distribution",
            color_discrete_sequence=COLOR_GREEN
        )
        fig2.update_traces(
            textposition="inside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Farmers: %{value}<br>Share: %{percent}<extra></extra>",
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        fig2.update_layout(**LAYOUT, showlegend=False, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    # Chart 3 — Farmers by Season (bar)
    with r2c1:
        season_cnt = df["Season"].value_counts().reset_index()
        season_cnt.columns = ["Season", "Farmers"]
        fig3 = px.bar(
            season_cnt, x="Season", y="Farmers",
            color="Season", text="Farmers",
            color_discrete_sequence=["#0C3823", "#388E3C", "#81C784"],
            title="Farmers by Growing Season"
        )
        fig3.update_traces(
            textposition="outside",
            marker_cornerradius=6,
            hovertemplate="<b>%{x}</b><br>Farmers: %{y}<extra></extra>"
        )
        fig3.update_layout(**LAYOUT, showlegend=False, height=300)
        fig3.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
        fig3.update_xaxes(showgrid=False)
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 4 — Avg Farm Area by Crop (horizontal bar)
    with r2c2:
        avg_area = df.groupby("Crop_Type")["Crop_Area"].mean().sort_values().reset_index()
        avg_area.columns = ["Crop", "Avg Area (Acres)"]
        fig4 = px.bar(
            avg_area, x="Avg Area (Acres)", y="Crop",
            orientation="h",
            color="Avg Area (Acres)",
            color_continuous_scale=["#C8E6C9", "#0C3823"],
            text="Avg Area (Acres)",
            title="Avg Farm Area by Crop Type"
        )
        fig4.update_traces(
            texttemplate="%{x:.0f} ac",
            textposition="outside",
            marker_cornerradius=4,
            hovertemplate="<b>%{y}</b><br>Avg Area: %{x:.1f} acres<extra></extra>"
        )
        fig4.update_layout(**LAYOUT, coloraxis_showscale=False, height=300)
        fig4.update_xaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
        fig4.update_yaxes(showgrid=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Chart 5 — Crop breakdown by Region (stacked bar, full width)
    crop_region = df.groupby(["Region", "Crop_Type"]).size().reset_index(name="Farmers")
    fig5 = px.bar(
        crop_region, x="Region", y="Farmers", color="Crop_Type",
        barmode="stack",
        color_discrete_sequence=COLOR_GREEN,
        title="Crop Portfolio Breakdown by Region",
        labels={"Crop_Type": "Crop", "Farmers": "Registered Farmers"}
    )
    fig5.update_traces(
        marker_cornerradius=4,
        hovertemplate="<b>%{fullData.name}</b><br>Farmers: %{y}<extra></extra>"
    )
    fig5.update_layout(**LAYOUT, height=380, legend_title_text="Crop Type")
    fig5.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    fig5.update_xaxes(showgrid=False)
    st.plotly_chart(fig5, use_container_width=True)
