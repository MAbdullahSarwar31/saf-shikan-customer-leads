"""Configuration settings for SAF SHIKAN Lead Scoring & Segmentation project.

This file centralizes all configuration parameters, ranges, weights, and directory paths.
"""

import os

# Project Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Random state for reproducibility
RANDOM_STATE = 42

# Directory Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

# Data File Paths
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, "customers.csv")
CLEAN_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "customers_clean.csv")
CLUSTERED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "customers_clustered.csv")
FINAL_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "customers_final.csv")
EXCEL_OUTPUT_PATH = os.path.join(REPORTS_DIR, "Customer_Leads_SAF_SHIKAN.xlsx")
MODEL_PATH = os.path.join(MODELS_DIR, "kmeans_model.pkl")

# Pakistani Districts by Region
DISTRICTS = {
    "Punjab": [
        "Lahore", "Faisalabad", "Multan", "Sahiwal", "Okara",
        "Pakpattan", "Vehari", "Bahawalpur", "Rahim Yar Khan", "Gujranwala"
    ],
    "Sindh": [
        "Sukkur", "Larkana", "Hyderabad", "Nawabshah", "Mirpur Khas", "Khairpur"
    ],
    "KPK": [
        "Peshawar", "Mardan", "Swabi", "Charsadda"
    ]
}

# Crop Types and Prevalence Weights (for synthetic generation)
CROP_PREVALENCE = {
    "wheat": 0.35,      # Major staple Rabi crop
    "rice": 0.20,       # Major Kharif export crop
    "cotton": 0.15,     # Pesticide intensive Kharif cash crop
    "sugarcane": 0.12,  # Major water/fertilizer intensive Kharif crop
    "maize": 0.08,      # Standard Kharif/Rabi feed crop
    "sunflower": 0.04,  # Oilseed crop
    "canola": 0.04,     # Oilseed crop
    "tobacco": 0.02     # Cash crop in KPK
}

# Crop Area Ranges (in acres)
CROP_AREA_BOUNDS = {
    "wheat": (5, 50),
    "rice": (3, 30),
    "cotton": (10, 100),
    "sugarcane": (5, 40),
    "maize": (2, 20),
    "sunflower": (2, 15),
    "canola": (3, 20),
    "tobacco": (1, 10)
}

# Standard Seasons for crops
CROP_SEASONS = {
    "wheat": "Rabi",
    "canola": "Rabi",
    "rice": "Kharif",
    "cotton": "Kharif",
    "sugarcane": "Kharif",
    "maize": "Kharif",
    "sunflower": "Rabi",
    "tobacco": "Rabi"
}

# Estimated Crop Price per Acre in PKR (for Estimated_Income calculation)
CROP_PRICES_PER_ACRE = {
    "wheat": 95000,
    "rice": 120000,
    "cotton": 150000,
    "sugarcane": 180000,
    "maize": 100000,
    "sunflower": 80000,
    "canola": 85000,
    "tobacco": 200000
}

# Preprocessing: Drone Service Suitability Potential (1-10 scale)
DRONE_POTENTIAL_SCORES = {
    "cotton": 10,       # Pesticide heavy, tall canopy
    "rice": 9,          # Flooded fields make land-spraying difficult
    "sugarcane": 8,     # Extremely tall, dense crops, drone spray is optimal
    "wheat": 7,         # Large scale, needs uniform fungicide/pesticide spray
    "maize": 6,         # Medium height, standard pesticide needs
    "sunflower": 5,     # Average potential
    "canola": 5,        # Average potential
    "tobacco": 5        # Average potential
}

# Preprocessing: Season scores (more pest pressure/drone service need in Kharif)
SEASON_SCORES = {
    "Both": 10,
    "Kharif": 7,
    "Rabi": 5
}

# Preprocessing: Region operational scores (based on SAF SHIKAN's coverage)
REGION_SCORES = {
    "Punjab": 10,
    "Sindh": 8,
    "KPK": 6
}

# Lead Scoring Weights
LEAD_SCORING_WEIGHTS = {
    "drone_potential": 0.35,
    "area": 0.30,
    "season": 0.20,
    "region": 0.15
}
