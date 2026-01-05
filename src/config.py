# src/config.py
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    api_key: str
    timeout_sec: int = 20

    # Google Places endpoints
    geocode_url: str = "https://maps.googleapis.com/maps/api/geocode/json"
    nearby_url: str = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    details_url: str = "https://maps.googleapis.com/maps/api/place/details/json"

    # Nearby Search constraints
    max_nearby_radius_m: int = 50_000  # 50km cap
    tile_radius_m: int = 40_000        # safe working radius for tiling
    max_pages_per_tile: int = 3        # Nearby Search pages: up to 3 (20 results each)

    # Rate limiting / token readiness
    next_page_token_wait_sec: float = 2.2
    sleep_between_requests_sec: float = 0.15

    # Export paths
    data_raw_dir: str = "data/raw"
    data_processed_dir: str = "data/processed"

def load_settings() -> Settings:
    key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "Missing GOOGLE_MAPS_API_KEY. Create a .env or export it in your terminal.\n"
            "Example: export GOOGLE_MAPS_API_KEY='YOUR_KEY'"
        )
    return Settings(api_key=key)
