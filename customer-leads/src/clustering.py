"""Clustering and Customer Segmentation Module for SAF SHIKAN.

This module segments customers using K-Means clustering based on engineered feature scores.
It automatically finds the optimal K, profiles the clusters, and saves visualizations.
"""

import os
import pickle
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from typing import Tuple, Dict, List

# Add parent directory to path so config can be imported when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    CLEAN_DATA_PATH, CLUSTERED_DATA_PATH, MODEL_PATH, FIGURES_DIR, RANDOM_STATE
)
from utils import load_dataset, save_dataset, logger, ensure_dirs


def evaluate_kmeans(scaled_features: pd.DataFrame, max_k: int = 10) -> Tuple[List[float], List[float]]:
    """Evaluate K-Means for K=2 to max_k.
    
    Computes WCSS and silhouette scores.
    
    Args:
        scaled_features: Scaled feature DataFrame for clustering.
        max_k: Maximum K value to test.
        
    Returns:
        A tuple of (wcss_list, silhouette_scores_list).
    """
    wcss = []
    silhouette_scores = []
    
    k_range = range(2, max_k + 1)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        kmeans.fit(scaled_features)
        wcss.append(kmeans.inertia_)
        
        score = silhouette_score(scaled_features, kmeans.labels_)
        silhouette_scores.append(score)
        logger.info(f"K={k}: WCSS={kmeans.inertia_:.2f}, Silhouette Score={score:.4f}")
        
    return wcss, silhouette_scores


def plot_metrics(wcss: List[float], silhouette_scores: List[float], max_k: int = 10) -> None:
    """Plot Elbow Curve and Silhouette Scores and save to reports/figures/.
    
    Args:
        wcss: List of WCSS values.
        silhouette_scores: List of silhouette scores.
        max_k: Maximum K tested.
    """
    k_range = list(range(2, max_k + 1))
    
    # 1. Plot Elbow Curve
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, wcss, marker='o', linestyle='-', color='#2E7D32', linewidth=2)
    plt.title('K-Means Elbow Curve', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Clusters (K)', fontsize=12)
    plt.ylabel('WCSS (Inertia)', fontsize=12)
    plt.xticks(k_range)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    elbow_path = os.path.join(FIGURES_DIR, "elbow_curve.png")
    plt.savefig(elbow_path, dpi=300)
    plt.close()
    logger.info(f"Saved Elbow curve to: {elbow_path}")
    
    # 2. Plot Silhouette Scores
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, silhouette_scores, marker='s', linestyle='-', color='#1565C0', linewidth=2)
    plt.title('K-Means Silhouette Scores', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Clusters (K)', fontsize=12)
    plt.ylabel('Silhouette Score', fontsize=12)
    plt.xticks(k_range)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    sil_path = os.path.join(FIGURES_DIR, "silhouette_scores.png")
    plt.savefig(sil_path, dpi=300)
    plt.close()
    logger.info(f"Saved Silhouette scores to: {sil_path}")


def find_optimal_k(scaled_features: pd.DataFrame, wcss: List[float], silhouette_scores: List[float], min_cluster_size: int = 50) -> int:
    """Select the optimal K value programmatically.
    
    Filters K options that have any cluster size below the specified minimum,
    and returns the K with the highest silhouette score. Fallback to 3 or 4.
    
    Args:
        scaled_features: Scaled feature DataFrame.
        wcss: List of WCSS values.
        silhouette_scores: List of silhouette scores.
        min_cluster_size: Minimum required size for any cluster.
        
    Returns:
        Optimal number of clusters K.
    """
    logger.info("Selecting optimal K dynamically...")
    k_range = list(range(2, len(silhouette_scores) + 2))
    valid_ks = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        kmeans.fit(scaled_features)
        labels = kmeans.labels_
        sizes = pd.Series(labels).value_counts().values
        
        # Check if all clusters are larger than minimum size
        if min(sizes) >= min_cluster_size:
            score = silhouette_scores[k - 2]
            valid_ks.append((k, score))
            logger.info(f"K={k} is valid (sizes: {sizes}, silhouette: {score:.4f})")
        else:
            logger.info(f"K={k} is invalid (sizes: {sizes} contains cluster < {min_cluster_size})")
            
    if valid_ks:
        # Sort by silhouette score descending
        valid_ks.sort(key=lambda x: x[1], reverse=True)
        optimal_k = valid_ks[0][0]
        logger.info(f"Dynamic selection chose K={optimal_k} with Silhouette Score={valid_ks[0][1]:.4f}")
    else:
        # Fallback to K=3 if no K satisfies the size constraint
        optimal_k = 3
        logger.warning(f"No K satisfied the cluster size constraint of {min_cluster_size}. Fallback to K={optimal_k}")
        
    return optimal_k


def profile_clusters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, str]]:
    """Profile clusters, generate dynamic descriptions, and name them.
    
    Args:
        df: Customer DataFrame containing cluster labels.
        
    Returns:
        A tuple of (profile_df, cluster_names_map).
    """
    logger.info("Profiling and naming clusters...")
    
    # Identify feature score columns
    scores_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    
    profiles = []
    cluster_names_map = {}
    
    for cluster_id in sorted(df["Cluster"].unique()):
        cluster_df = df[df["Cluster"] == cluster_id]
        size = len(cluster_df)
        
        # Mean stats
        mean_area = cluster_df["Crop_Area"].mean()
        mean_income = cluster_df["Estimated_Income"].mean()
        mean_scores = cluster_df[scores_cols].mean()
        
        # Dominant values
        dominant_crop = cluster_df["Crop_Type"].mode()[0]
        dominant_region = cluster_df["Region"].mode()[0]
        dominant_season = cluster_df["Season"].mode()[0]
        
        # Determine Scale Label
        if mean_area < 10:
            scale_label = "Small-scale"
        elif mean_area <= 35:
            scale_label = "Medium-scale"
        else:
            scale_label = "Large-scale"
            
        # Determine Drone Need Label based on crop suitability & season
        drone_need = "High" if mean_scores["Drone_Service_Potential"] >= 8 else "Moderate"
        
        # Name formulation
        cluster_name = f"{scale_label} {dominant_crop.title()} Growers ({dominant_region} - {dominant_season})"
        cluster_names_map[cluster_id] = cluster_name
        
        profile = {
            "Cluster": cluster_id,
            "Name": cluster_name,
            "Size": size,
            "Mean_Crop_Area": round(mean_area, 2),
            "Mean_Income_PKR": round(mean_income, 2),
            "Dominant_Crop": dominant_crop,
            "Dominant_Region": dominant_region,
            "Dominant_Season": dominant_season,
            "Avg_Drone_Potential": round(mean_scores["Drone_Service_Potential"], 2),
            "Avg_Area_Score": round(mean_scores["Area_Score"], 2),
            "Avg_Season_Score": round(mean_scores["Season_Score"], 2),
            "Avg_Region_Score": round(mean_scores["Region_Score"], 2),
            "Drone_Need": drone_need
        }
        profiles.append(profile)
        
    profile_df = pd.DataFrame(profiles)
    return profile_df, cluster_names_map


def plot_clusters_pca(df: pd.DataFrame, scaled_features: pd.DataFrame) -> None:
    """Reduce features to 2D using PCA, plot the clusters, and save.
    
    Args:
        df: Customer DataFrame with Cluster labels.
        scaled_features: Scaled feature DataFrame.
    """
    logger.info("Performing PCA for cluster visualization...")
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    pca_data = pca.fit_transform(scaled_features)
    
    df_pca = pd.DataFrame(pca_data, columns=["PCA1", "PCA2"])
    df_pca["Cluster"] = df["Cluster"].astype(str)
    df_pca["Cluster_Name"] = df["Cluster_Name"]
    
    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        x="PCA1", y="PCA2", hue="Cluster_Name", data=df_pca,
        palette="viridis", style="Cluster_Name", s=80, alpha=0.85
    )
    plt.title('SAF SHIKAN Customer Segments (2D PCA Projection)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)', fontsize=12)
    plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Segments")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    
    pca_plot_path = os.path.join(FIGURES_DIR, "cluster_scatter_2d.png")
    plt.savefig(pca_plot_path, dpi=300)
    plt.close()
    logger.info(f"Saved PCA scatter plot to: {pca_plot_path}")


def main() -> None:
    """Main execution function to load data, cluster, profile, visualize, and save."""
    logger.info("Initializing Phase 3: Clustering & Segmentation...")
    ensure_dirs()
    
    df = load_dataset(CLEAN_DATA_PATH)
    
    # Extract features for clustering
    feature_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    scaled_feature_cols = [f"{col}_scaled" for col in feature_cols]
    scaled_features = df[scaled_feature_cols]
    
    # Step 1: Find K and Plot metrics
    wcss, silhouette_scores = evaluate_kmeans(scaled_features, max_k=10)
    plot_metrics(wcss, silhouette_scores)
    
    # Find optimal K
    optimal_k = find_optimal_k(scaled_features, wcss, silhouette_scores)
    
    # Step 2: Train final K-Means model
    kmeans = KMeans(n_clusters=optimal_k, random_state=RANDOM_STATE, n_init=10)
    df["Cluster"] = kmeans.fit_predict(scaled_features)
    
    # Save the model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(kmeans, f)
    logger.info(f"Saved trained K-Means model to: {MODEL_PATH}")
    
    # Step 3 & 4: Profile and name clusters
    profile_df, cluster_names_map = profile_clusters(df)
    df["Cluster_Name"] = df["Cluster"].map(cluster_names_map)
    
    # Visualize using PCA
    plot_clusters_pca(df, scaled_features)
    
    # Save clustered data
    save_dataset(df, CLUSTERED_DATA_PATH)
    
    # Print confirmations for verification gate
    print("=" * 60)
    print("PHASE 3 VERIFICATION GATE - CLUSTERING & SEGMENTATION SUMMARY")
    print("=" * 60)
    print(f"Optimal K Selected: {optimal_k}")
    print("\nCluster Sizes:")
    print(df["Cluster_Name"].value_counts())
    print("\nCluster Characteristics Table:")
    print(profile_df.to_string(index=False))
    print("=" * 60)
    logger.info("Phase 3 Clustering completed successfully.")


if __name__ == "__main__":
    main()
