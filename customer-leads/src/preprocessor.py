"""Data Preprocessing and Cleaning Module for SAF SHIKAN.

This module cleans the raw synthetic dataset, validates fields, and engineers/scales
features required for clustering.
"""

import os
import re
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, List

# Add parent directory to path so config can be imported when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RAW_DATA_PATH, CLEAN_DATA_PATH, DRONE_POTENTIAL_SCORES,
    SEASON_SCORES, REGION_SCORES, CROP_AREA_BOUNDS
)
from utils import load_dataset, save_dataset, logger


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw customer dataset.
    
    Performs duplicate phone removal, name and crop type standardization,
    phone number format checks, and outlier flagging for crop area.
    
    Args:
        df: Input DataFrame to clean.
        
    Returns:
        Cleaned DataFrame.
    """
    initial_rows = len(df)
    logger.info(f"Starting data cleaning on {initial_rows} rows...")
    
    # 1. Handle missing values
    null_counts = df.isnull().sum().sum()
    if null_counts > 0:
        logger.warning(f"Found {null_counts} null values. Dropping rows with nulls.")
        df = df.dropna()
    else:
        logger.info("No missing values found.")
        
    # 2. Remove duplicate phone numbers
    duplicate_count = df.duplicated(subset=["Phone"]).sum()
    if duplicate_count > 0:
        logger.info(f"Removing {duplicate_count} duplicate phone numbers...")
        df = df.drop_duplicates(subset=["Phone"], keep="first")
    else:
        logger.info("No duplicate phone numbers found.")
        
    # 3. Standardize text columns (Title Case names, lowercase crops)
    df["Name"] = df["Name"].astype(str).str.strip().str.title()
    df["Crop_Type"] = df["Crop_Type"].astype(str).str.strip().str.lower()
    df["Location"] = df["Location"].astype(str).str.strip().str.title()
    df["Region"] = df["Region"].astype(str).str.strip().str.title()
    logger.info("Text columns standardized successfully.")
    
    # 4. Validate phone number format
    phone_pattern = re.compile(r"^03\d{2}-\d{7}$")
    invalid_phones = df[~df["Phone"].apply(lambda x: bool(phone_pattern.match(str(x))))]
    if len(invalid_phones) > 0:
        logger.warning(f"Found {len(invalid_phones)} invalid phone numbers. Dropping them.")
        df = df[df["Phone"].apply(lambda x: bool(phone_pattern.match(str(x))))]
    else:
        logger.info("All phone numbers conform to 03XX-XXXXXXX format.")
        
    # 5. Validate crop area ranges (flag outliers)
    outliers = []
    for idx, row in df.iterrows():
        crop = row["Crop_Type"]
        area = row["Crop_Area"]
        if crop in CROP_AREA_BOUNDS:
            min_val, max_val = CROP_AREA_BOUNDS[crop]
            if area < min_val or area > max_val:
                outliers.append((row["Name"], crop, area, f"Range: {min_val}-{max_val}"))
                
    if outliers:
        logger.warning(f"Flagged {len(outliers)} crop area outliers:")
        for name, crop, area, limit in outliers[:5]:
            logger.warning(f"  - {name}: {crop} area is {area} acres ({limit})")
        if len(outliers) > 5:
            logger.warning(f"  - ... and {len(outliers) - 5} more.")
    else:
        logger.info("All crop areas are within crop-specific limits.")
        
    logger.info(f"Data cleaning finished. Rows remaining: {len(df)} (Dropped {initial_rows - len(df)} rows).")
    return df


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Engineer scores and scale features for clustering.
    
    Args:
        df: Cleaned customer DataFrame.
        
    Returns:
        A tuple of (full_engineered_df, scaled_features_df).
    """
    logger.info("Engineering features for clustering...")
    df = df.copy()
    
    # Feature 1: Drone_Service_Potential (based on crop type)
    df["Drone_Service_Potential"] = df["Crop_Type"].map(DRONE_POTENTIAL_SCORES).fillna(5)
    
    # Feature 2: Area_Score (1-10 normalized crop area)
    min_area = df["Crop_Area"].min()
    max_area = df["Crop_Area"].max()
    if max_area > min_area:
        df["Area_Score"] = 1.0 + 9.0 * (df["Crop_Area"] - min_area) / (max_area - min_area)
    else:
        df["Area_Score"] = 5.0  # Fallback
        
    # Round Area_Score to 2 decimal places
    df["Area_Score"] = df["Area_Score"].round(2)
    
    # Feature 3: Season_Score (Both=10, Kharif=7, Rabi=5)
    df["Season_Score"] = df["Season"].map(SEASON_SCORES).fillna(5)
    
    # Feature 4: Region_Score (Punjab=10, Sindh=8, KPK=6)
    df["Region_Score"] = df["Region"].map(REGION_SCORES).fillna(5)
    
    # Features for clustering
    feature_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    
    # Fit StandardScaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[feature_cols])
    
    # Create scaled columns
    for i, col in enumerate(feature_cols):
        df[f"{col}_scaled"] = scaled_data[:, i]
        
    scaled_df = pd.DataFrame(scaled_data, columns=feature_cols)
    
    logger.info("Feature engineering and scaling completed successfully.")
    return df, scaled_df


def main() -> None:
    """Main execution function to load raw data, preprocess, and save cleaned data."""
    logger.info("Initializing Phase 2: Data Preprocessing & Cleaning...")
    
    # Load raw dataset
    df = load_dataset(RAW_DATA_PATH)
    
    # Clean data
    df_clean = clean_data(df)
    
    # Engineer features
    df_engineered, df_scaled = engineer_features(df_clean)
    
    # Save cleaned and engineered dataset
    save_dataset(df_engineered, CLEAN_DATA_PATH)
    
    # Print confirmations for verification gate
    print("=" * 60)
    print("PHASE 2 VERIFICATION GATE - DATA PREPROCESSING SUMMARY")
    print("=" * 60)
    print(f"Cleaned dataset shape: {df_engineered.shape}")
    print(f"Missing values count in clean dataset:\n{df_engineered.isnull().sum()}")
    
    # Show descriptive statistics for raw feature scores to check if they are in 1-10 range
    feature_cols = ["Drone_Service_Potential", "Area_Score", "Season_Score", "Region_Score"]
    print("\nFeature Scores Summary (Expected Range: 1.0 to 10.0):")
    print(df_engineered[feature_cols].describe().loc[["min", "max", "mean", "std"]])
    
    # Show scaled features statistics to verify scaling (mean ~0, std ~1)
    scaled_cols = [f"{col}_scaled" for col in feature_cols]
    print("\nScaled Feature Scores Summary (Expected Mean ~0, Std ~1):")
    print(df_engineered[scaled_cols].describe().loc[["mean", "std"]].round(4))
    
    # Feature correlation matrix
    print("\nCorrelation Matrix of Feature Scores:")
    print(df_engineered[feature_cols].corr().round(4))
    print("=" * 60)
    logger.info("Phase 2 Data Preprocessing completed successfully.")


if __name__ == "__main__":
    main()
