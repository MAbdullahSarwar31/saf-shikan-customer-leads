"""Synthetic Dataset Generator for SAF SHIKAN Lead Scoring & Segmentation.

This module generates a realistic customer dataset reflecting Pakistani farming conditions.
"""

import os
import random
import sys
import numpy as np
import pandas as pd
from typing import Tuple, Dict, List

# Add parent directory to path so config can be imported when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RANDOM_STATE, RAW_DATA_PATH, DISTRICTS, CROP_PREVALENCE,
    CROP_AREA_BOUNDS, CROP_SEASONS, CROP_PRICES_PER_ACRE
)
from utils import ensure_dirs, save_dataset, logger

# Lists of common Pakistani names for synthetic generator
PAK_FIRST_MALE = [
    "Muhammad", "Ahmad", "Ali", "Tariq", "Imran", "Sajid", "Usman", "Bilal",
    "Kamran", "Zafar", "Asif", "Rizwan", "Fawad", "Naveed", "Faisal", "Majid",
    "Yasir", "Shehzad", "Babar", "Haroon", "Arsalan", "Junaid", "Hamza", "Waseem",
    "Irfan", "Adeel", "Sohail", "Zahid", "Amjad", "Noman", "Farhan", "Kashif",
    "Shahid", "Jamil", "Rashid", "Nadeem", "Akram", "Iqbal", "Saeed", "Arshad"
]

PAK_FIRST_FEMALE = [
    "Fatima", "Aisha", "Zainab", "Amina", "Sadia", "Maryam", "Sana", "Hina",
    "Noreen", "Bushra", "Nida", "Kiran", "Shazia", "Saima", "Iqra", "Sidra",
    "Uzma", "Farah", "Anum", "Sobia", "Ayesha", "Nazia", "Mehwish", "Humaira"
]

PAK_LAST = [
    "Khan", "Ahmed", "Malik", "Bhatti", "Choudhary", "Jatoi", "Shah", "Nawaz",
    "Butt", "Gujjar", "Dogar", "Sheikh", "Khokhar", "Gill", "Mughal", "Qureshi",
    "Bajwa", "Rehman", "Lodhi", "Wattoo", "Cheema", "Warraich", "Gondal", "Lashari",
    "Tarar", "Mahar", "Junejo", "Talpur", "Laghari", "Abbasi", "Yousafzai", "Khattak"
]

PAK_MOBILE_PREFIXES = [
    "0300", "0301", "0302", "0303", "0304", "0305", "0306", "0307", "0308", "0309",  # Jazz
    "0310", "0311", "0312", "0313", "0314", "0315", "0316", "0317", "0318",         # Zong
    "0320", "0321", "0322", "0323", "0324", "0325",                                 # Warid
    "0330", "0331", "0332", "0333", "0334", "0335", "0336", "0337",                 # Ufone
    "0340", "0341", "0342", "0343", "0344", "0345", "0346", "0347", "0348", "0349"  # Telenor
]


def generate_pakistani_name() -> str:
    """Generate a realistic Pakistani name with an 85% male and 15% female split.
    
    Returns:
        A full name string.
    """
    if random.random() < 0.85:
        first = random.choice(PAK_FIRST_MALE)
    else:
        first = random.choice(PAK_FIRST_FEMALE)
    last = random.choice(PAK_LAST)
    return f"{first} {last}"


def generate_unique_phone(existing_phones: set) -> str:
    """Generate a unique Pakistani mobile number in the format 03XX-XXXXXXX.
    
    Args:
        existing_phones: Set of already generated phone numbers.
        
    Returns:
        A unique phone number string.
    """
    while True:
        prefix = random.choice(PAK_MOBILE_PREFIXES)
        digits = "".join([str(random.randint(0, 9)) for _ in range(7)])
        phone = f"{prefix}-{digits}"
        if phone not in existing_phones:
            existing_phones.add(phone)
            return phone


def get_farm_scale(area: float) -> str:
    """Determine the farm scale category based on crop area.
    
    Args:
        area: Crop area in acres.
        
    Returns:
        Category: Small, Medium, or Large.
    """
    if area < 10:
        return "Small"
    elif area <= 50:
        return "Medium"
    else:
        return "Large"


def generate_customer_dataset(num_records: int = 500) -> pd.DataFrame:
    """Generate a realistic synthetic dataset of Pakistani farm customers.
    
    Args:
        num_records: Number of customer records to generate.
        
    Returns:
        Pandas DataFrame containing generated records.
    """
    # Set random seed for reproducibility
    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)
    
    existing_phones = set()
    records = []
    
    # Pre-unpack crop choices and weights for weighted choice
    crops = list(CROP_PREVALENCE.keys())
    crop_weights = list(CROP_PREVALENCE.values())
    
    # Regional probabilities for Pakistani farmers dataset (Punjab is largest agricultural hub)
    regions = ["Punjab", "Sindh", "KPK"]
    region_weights = [0.60, 0.25, 0.15]
    
    for _ in range(num_records):
        name = generate_pakistani_name()
        phone = generate_unique_phone(existing_phones)
        
        # Sample Crop Type
        crop_type = random.choices(crops, weights=crop_weights, k=1)[0]
        
        # Sample Crop Area based on crop-specific bounds
        min_area, max_area = CROP_AREA_BOUNDS[crop_type]
        crop_area = random.randint(min_area, max_area)
        
        # Sample Region and District
        region = random.choices(regions, weights=region_weights, k=1)[0]
        location = random.choice(DISTRICTS[region])
        
        # Determine base season
        base_season = CROP_SEASONS[crop_type]
        
        # Determine actual season (multi-crop vs single crop)
        # Larger farms are more likely to double-crop ("Both")
        farm_scale = get_farm_scale(crop_area)
        both_probability = 0.15 if farm_scale == "Small" else (0.35 if farm_scale == "Medium" else 0.60)
        
        if random.random() < both_probability:
            season = "Both"
        else:
            season = base_season
            
        # Calculate Estimated Income in PKR
        price_per_acre = CROP_PRICES_PER_ACRE[crop_type]
        # Multi-crop farmers have higher estimated income due to double harvest
        income_multiplier = 1.6 if season == "Both" else 1.0
        estimated_income = int(crop_area * price_per_acre * income_multiplier)
        
        records.append({
            "Name": name,
            "Phone": phone,
            "Crop_Type": crop_type,
            "Crop_Area": crop_area,
            "Season": season,
            "Location": location,
            "Estimated_Income": estimated_income,
            "Farm_Scale": farm_scale,
            "Region": region
        })
        
    df = pd.DataFrame(records)
    return df


def main() -> None:
    """Main execution function to generate and save Phase 1 dataset."""
    logger.info("Initializing Phase 1: Synthetic Dataset Generation...")
    ensure_dirs()
    
    df = generate_customer_dataset(500)
    
    # Save raw customers
    save_dataset(df, RAW_DATA_PATH)
    
    # Print confirmations as requested in verification gate
    print("=" * 60)
    print("PHASE 1 VERIFICATION GATE - DATA GENERATION SUMMARY")
    print("=" * 60)
    print(f"Dataset shape: {df.shape} (Expected: (500, 9))")
    print(f"Missing values count:\n{df.isnull().sum()}")
    print("\nFirst 5 rows of generated dataset:")
    print(df.head().to_string())
    print("\nColumn Data Types:")
    print(df.dtypes)
    print("\nValue Counts for Crop_Type:")
    print(df["Crop_Type"].value_counts())
    print("\nValue Counts for Season:")
    print(df["Season"].value_counts())
    print("\nValue Counts for Region:")
    print(df["Region"].value_counts())
    print("=" * 60)
    logger.info("Phase 1 Synthetic Dataset generated successfully.")


if __name__ == "__main__":
    main()
