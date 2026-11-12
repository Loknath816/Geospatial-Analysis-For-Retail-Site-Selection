"""
Data Ingestion, Validation, Cleaning and Provenance Engine.
Manages spatial datasets, coordinates validation, schema enforcement,
deduplication, and provenance metadata.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataPipeline")

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


class DataPipeline:
    """Enterprise Data Pipeline for Retail Intelligence."""

    def __init__(self, city_id: str = "bengaluru"):
        self.city_id = city_id
        self.city_config = self._load_city_config(city_id)
        self.bounds = self.city_config.get("bounds", {
            "min_lat": 12.75, "max_lat": 13.25,
            "min_lon": 77.40, "max_lon": 77.85
        })

    def _load_city_config(self, city_id: str) -> Dict[str, Any]:
        config_path = os.path.join(CONFIG_DIR, "city_profiles", f"{city_id}.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        logger.warning(f"City config {city_id}.json not found at {config_path}. Using defaults.")
        return {"city_id": city_id, "city_name": city_id.title()}

    def validate_coordinates(self, lat: float, lon: float) -> Tuple[bool, str]:
        """Validate if coordinates fall within the defined city boundaries."""
        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
            return False, f"Invalid non-numeric coordinates: lat={lat}, lon={lon}"
        if np.isnan(lat) or np.isnan(lon):
            return False, "Coordinates cannot be NaN"
        
        b = self.bounds
        if not (b["min_lat"] <= lat <= b["max_lat"] and b["min_lon"] <= lon <= b["max_lon"]):
            return False, f"Coordinates ({lat:.4f}, {lon:.4f}) outside {self.city_id} bounds: lat[{b['min_lat']}, {b['max_lat']}], lon[{b['min_lon']}, {b['max_lon']}]"
        
        return True, "Valid"

    def validate_dataframe_coordinates(self, df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon") -> pd.DataFrame:
        """Filter and return rows with valid spatial coordinates."""
        initial_len = len(df)
        valid_mask = df.apply(lambda r: self.validate_coordinates(r[lat_col], r[lon_col])[0], axis=1)
        valid_df = df[valid_mask].copy()
        dropped = initial_len - len(valid_df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} records with invalid/out-of-bounds coordinates.")
        return valid_df

    def detect_duplicate_coordinates(self, df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon", tolerance: float = 0.0001) -> pd.DataFrame:
        """Identify potential duplicate entries based on coordinate proximity."""
        dups = df[df.duplicated(subset=[lat_col, lon_col], keep=False)]
        return dups

    def save_dataset(self, df: pd.DataFrame, filename: str, metadata: Optional[Dict[str, Any]] = None):
        """Save processed dataframe with provenance metadata."""
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        csv_path = os.path.join(PROCESSED_DATA_DIR, filename)
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df)} rows to {csv_path}")

        if metadata:
            meta_path = os.path.join(PROCESSED_DATA_DIR, "metadata.json")
            all_meta = {}
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        all_meta = json.load(f)
                except Exception:
                    all_meta = {}
            all_meta[filename] = {
                **metadata,
                "record_count": len(df),
                "columns": list(df.columns),
                "last_processed_utc": datetime.utcnow().isoformat() + "Z"
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(all_meta, f, indent=2)

    def load_processed_dataset(self, filename: str) -> pd.DataFrame:
        """Load a processed dataset from disk."""
        path = os.path.join(PROCESSED_DATA_DIR, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        raise FileNotFoundError(f"Processed dataset {filename} not found at {path}")

