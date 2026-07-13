"""Utility helper functions for SAF SHIKAN Lead Scoring & Segmentation project.

This module provides common utilities such as path validation, folder initialization,
and standard logging configurations.
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_dirs(base_dir: str = None) -> None:
    """Ensure that all necessary project subdirectories exist.
    
    Args:
        base_dir: Optional base directory. If None, absolute path of config.py parent will be used.
    """
    # Import config relative to avoid circular import issues if loaded early
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, FIGURES_DIR
    
    dirs = [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, FIGURES_DIR]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            logger.info(f"Created directory: {d}")


def save_dataset(df: pd.DataFrame, filepath: str) -> None:
    """Save a Pandas DataFrame to a CSV file and log the action.
    
    Args:
        df: DataFrame to save.
        filepath: Absolute or relative target file path.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.info(f"Saved dataset to: {filepath} (Shape: {df.shape})")


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load a CSV dataset into a Pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file to load.
        
    Returns:
        Loaded DataFrame.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")
    df = pd.read_csv(filepath)
    logger.info(f"Loaded dataset from: {filepath} (Shape: {df.shape})")
    return df
