"""Premium Charts component for SAF SHIKAN Lead Dashboard.

This module provides modern, clean, and interactive Plotly visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Global styling configuration
FONT_FAMILY = "Outfit, Segoe UI, sans-serif"
COLOR_PALETTE = ["#1B5E20", "#388E3C", "#4CAF50", "#81C784", "#A5D6A7", "#C8E6C9"]


def plot_lead_category_distribution(df: pd.DataFrame) -> go.Figure:
    """Generate a premium donut chart of lead category distribution.
    
    Args:
        df: DataFrame containing Lead_Category column.
        
    Returns:
        Plotly Figure.
    """
    counts = df["Lead_Category"].value_counts().reset_index()
    counts.columns = ["Lead Category", "Count"]
    
    # Custom premium colors
    color_map = {
        "HOT": "#C62828",          # Premium ruby red
        "WARM": "#EF6C00",         # Warm pumpkin orange
        "COLD": "#1565C0",         # Deep royal blue
        "LOW PRIORITY": "#9E9E9E"  # Neutral slate gray
    }
    
    fig = px.pie(
        counts, names="Lead Category", values="Count",
        color="Lead Category", color_discrete_map=color_map,
        hole=0.55,
        title="Sales Pipeline Distribution"
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Proportion: %{percent}<extra></extra>",
        marker=dict(line=dict(color='#FFFFFF', width=3))
    )
    
    fig.update_layout(
        title_font=dict(size=18, family=FONT_FAMILY, color="#1B5E20", weight="bold"),
        showlegend=False,
        margin=dict(t=50, b=10, l=10, r=10),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def plot_customers_by_region(df: pd.DataFrame) -> go.Figure:
    """Generate a clean, styled bar chart of customers by region.
    
    Args:
        df: DataFrame containing Region column.
        
    Returns:
        Plotly Figure.
    """
    counts = df["Region"].value_counts().reset_index()
    counts.columns = ["Region", "Count"]
    
    fig = px.bar(
        counts, x="Region", y="Count",
        color="Region",
        color_discrete_map={
            "Punjab": "#2E7D32",  # Strong dark green
            "Sindh": "#4CAF50",   # Active grass green
            "KPK": "#81C784"      # Soft sage green
        },
        text="Count",
        title="Territory Sales Opportunities"
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(family=FONT_FAMILY, size=12, color="#1A1A1A", weight="bold"),
        hovertemplate="<b>Region: %{x}</b><br>Farmers: %{y}<extra></extra>",
        marker=dict(line=dict(color='rgba(0,0,0,0)', width=0), cornerradius=6)
    )
    
    fig.update_layout(
        title_font=dict(size=18, family=FONT_FAMILY, color="#1B5E20", weight="bold"),
        showlegend=False,
        xaxis_title="",
        yaxis_title="Farmer Registrations",
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY)
    )
    fig.update_yaxes(showgrid=True, gridcolor='#ECEFF1', zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


def plot_cluster_scatter_2d(df: pd.DataFrame) -> go.Figure:
    """Generate a high-performance interactive 2D PCA cluster projection.
    
    Args:
        df: Clustered DataFrame containing PCA dimensions and labels.
        
    Returns:
        Plotly Figure.
    """
    fig = px.scatter(
        df, x="Drone_Service_Potential_scaled", y="Area_Score_scaled",
        color="Cluster_Name",
        symbol="Cluster_Name",
        hover_data={
            "Name": True,
            "Phone": True,
            "Crop_Type": True,
            "Crop_Area": True,
            "Location": True,
            "Drone_Service_Potential_scaled": False,
            "Area_Score_scaled": False
        },
        title="Segment Mapping Matrix",
        labels={
            "Drone_Service_Potential_scaled": "Drone Service Potential (Scaled Score)",
            "Area_Score_scaled": "Farm Scale Score (Scaled Score)",
            "Cluster_Name": "Customer Segment"
        },
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    fig.update_traces(
        marker=dict(
            size=11, 
            opacity=0.9, 
            line=dict(width=1.5, color='#FFFFFF')
        ),
        hovertemplate="<b>%{customdata[0]}</b><br>Phone: %{customdata[1]}<br>Crop: %{customdata[2]} (%{customdata[3]} Acres)<br>Location: %{customdata[4]}<extra></extra>"
    )
    
    fig.update_layout(
        title_font=dict(size=18, family=FONT_FAMILY, color="#1B5E20", weight="bold"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.3,
            xanchor="center", x=0.5,
            title_text=""
        ),
        margin=dict(t=50, b=80, l=20, r=20),
        height=520,
        plot_bgcolor='#F8F9FA',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#ECEFF1', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#ECEFF1', zeroline=False)
    return fig


def plot_crops_per_cluster(df: pd.DataFrame) -> go.Figure:
    """Generate a clean grouped bar chart of crops per segment.
    
    Args:
        df: DataFrame containing Cluster_Name and Crop_Type.
        
    Returns:
        Plotly Figure.
    """
    counts = df.groupby(["Cluster_Name", "Crop_Type"]).size().reset_index(name="Count")
    counts["Crop_Type"] = counts["Crop_Type"].str.title()
    
    fig = px.bar(
        counts, x="Cluster_Name", y="Count", color="Crop_Type",
        title="Crop Portfolio Mix by Segment",
        labels={"Cluster_Name": "", "Count": "Farmers Registered", "Crop_Type": "Crop type"},
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig.update_traces(
        marker=dict(line=dict(color='rgba(0,0,0,0)', width=0), cornerradius=4)
    )
    
    fig.update_layout(
        title_font=dict(size=18, family=FONT_FAMILY, color="#1B5E20", weight="bold"),
        xaxis_tickangle=-12,
        margin=dict(t=50, b=50, l=20, r=20),
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY),
        legend=dict(title_text="Crops")
    )
    fig.update_yaxes(showgrid=True, gridcolor='#ECEFF1', zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


def plot_grouped_analytics(df: pd.DataFrame, group_col: str, metric_col: str, agg_func: str) -> go.Figure:
    """Generate a dynamic grouped bar/line chart for custom grouping analytics.
    
    Args:
        df: Customer DataFrame.
        group_col: Column to group by.
        metric_col: Numerical column to aggregate.
        agg_func: Aggregation function ('mean', 'sum', 'count').
        
    Returns:
        Plotly Figure.
    """
    # Clean group titles
    group_title = group_col.replace("_", " ").title()
    metric_title = metric_col.replace("_", " ").title()
    
    # Calculate aggregation
    grouped = df.groupby(group_col)[metric_col].agg(agg_func).reset_index()
    grouped.columns = [group_title, metric_title]
    grouped = grouped.sort_values(by=metric_title, ascending=False)
    
    # Handle string crop type capitalization if applicable
    if group_title == "Crop Type":
        grouped[group_title] = grouped[group_title].str.title()
        
    fig = px.bar(
        grouped, x=group_title, y=metric_title,
        color=metric_title,
        color_continuous_scale="Viridis",
        text=metric_title,
        title=f"{agg_func.upper()} of {metric_title} grouped by {group_title}"
    )
    
    text_format = "%.2f" if agg_func == "mean" else "%d"
    fig.update_traces(
        texttemplate=f"%{{y:{text_format}}}",
        textposition='outside',
        marker=dict(cornerradius=6)
    )
    
    fig.update_layout(
        title_font=dict(size=18, family=FONT_FAMILY, color="#1B5E20", weight="bold"),
        xaxis_title=group_title,
        yaxis_title=f"{metric_title} ({agg_func.title()})",
        margin=dict(t=50, b=20, l=20, r=20),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY),
        coloraxis_showscale=False
    )
    fig.update_yaxes(showgrid=True, gridcolor='#ECEFF1', zeroline=False)
    return fig
