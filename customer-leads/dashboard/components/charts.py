"""Charts component for SAF SHIKAN Lead Dashboard.

This module provides interactive Plotly visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_lead_category_distribution(df: pd.DataFrame) -> go.Figure:
    """Generate a pie chart of lead category distribution.
    
    Args:
        df: DataFrame containing Lead_Category column.
        
    Returns:
        Plotly Figure.
    """
    counts = df["Lead_Category"].value_counts().reset_index()
    counts.columns = ["Lead Category", "Count"]
    
    # Clean color mapping matching the Excel sheet
    color_map = {
        "HOT": "#B71C1C",          # Dark Red
        "WARM": "#E65100",         # Dark Orange
        "COLD": "#0D47A1",         # Dark Blue
        "LOW PRIORITY": "#757575"  # Gray
    }
    
    fig = px.pie(
        counts, names="Lead Category", values="Count",
        color="Lead Category", color_discrete_map=color_map,
        hole=0.4,
        title="Lead Priority Distribution"
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig.update_layout(
        title_font=dict(size=16, family="Calibri, Arial", color="#1B5E20"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(t=50, b=40, l=20, r=20),
        height=350
    )
    return fig


def plot_customers_by_region(df: pd.DataFrame) -> go.Figure:
    """Generate a bar chart of customers by region.
    
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
        color_discrete_sequence=["#1B5E20", "#388E3C", "#81C784"], # Dark Green gradient
        text="Count",
        title="Customers by Administrative Region"
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        title_font=dict(size=16, family="Calibri, Arial", color="#1B5E20"),
        showlegend=False,
        xaxis_title="Region",
        yaxis_title="Farmer Count",
        margin=dict(t=50, b=20, l=20, r=20),
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showgrid=True, gridcolor='#E0E0E0')
    return fig


def plot_cluster_scatter_2d(df: pd.DataFrame) -> go.Figure:
    """Generate an interactive Plotly 2D scatter plot of PCA cluster projections.
    
    Args:
        df: Clustered DataFrame containing PCA1, PCA2, and Cluster_Name.
        
    Returns:
        Plotly Figure.
    """
    fig = px.scatter(
        df, x="Drone_Service_Potential_scaled", y="Area_Score_scaled",  # Use scaled dimensions
        color="Cluster_Name",
        symbol="Cluster_Name",
        hover_data=["Name", "Phone", "Crop_Type", "Crop_Area", "Location"],
        title="Customer Segments (Drone Potential vs Farm Scale Space)",
        labels={
            "Drone_Service_Potential_scaled": "Drone Service Potential (Scaled)",
            "Area_Score_scaled": "Farm Area Score (Scaled)"
        },
        color_discrete_sequence=px.colors.qualitative.T10
    )
    
    fig.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(
        title_font=dict(size=16, family="Calibri, Arial", color="#1B5E20"),
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=1.02),
        margin=dict(t=50, b=40, l=20, r=20),
        height=500,
        plot_bgcolor='#F8F9FA',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=True, gridcolor='#E0E0E0')
    fig.update_yaxes(showgrid=True, gridcolor='#E0E0E0')
    return fig


def plot_crops_per_cluster(df: pd.DataFrame) -> go.Figure:
    """Generate a grouped bar chart showing Crop Type distribution across clusters.
    
    Args:
        df: DataFrame containing Cluster_Name and Crop_Type.
        
    Returns:
        Plotly Figure.
    """
    # Group crop counts by cluster
    counts = df.groupby(["Cluster_Name", "Crop_Type"]).size().reset_index(name="Count")
    
    # Capitalize crop type for display
    counts["Crop_Type"] = counts["Crop_Type"].str.title()
    
    fig = px.bar(
        counts, x="Cluster_Name", y="Count", color="Crop_Type",
        title="Crop Type Distribution by Segment",
        labels={"Cluster_Name": "Customer Segment", "Count": "Farmer Count", "Crop_Type": "Crop"},
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        title_font=dict(size=16, family="Calibri, Arial", color="#1B5E20"),
        xaxis_tickangle=-15,
        margin=dict(t=50, b=50, l=20, r=20),
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showgrid=True, gridcolor='#E0E0E0')
    return fig
