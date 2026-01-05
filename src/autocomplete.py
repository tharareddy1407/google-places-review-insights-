# src/autocomplete.py
from typing import List, Dict
from .config import Settings
from .http_client import HttpClient

AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def get_address_suggestions(client: HttpClient, settings: Settings, user_input: str, limit: int = 5) -> List[Dict]:
    """Returns predictions with description + place_id."""
    params = {
        "input": user_input,
        "types": "geocode",   # addresses + cities
        "key": settings.api_key,
    }
    data = client.get_json(AUTOCOMPLETE_URL, params=params)
    preds = data.get("predictions", []) or []
    out = []
    for p in preds[:limit]:
        out.append({
            "description": p.get("description"),
            "place_id": p.get("place_id"),
        })
    return out

def get_place_formatted_address(client: HttpClient, settings: Settings, place_id: str) -> Dict:
    """Fetch formatted address + components + geometry for a selected suggestion."""
    params = {
        "place_id": place_id,
        "fields": "formatted_address,address_component,geometry",
        "key": settings.api_key,
    }
    data = client.get_json(PLACE_DETAILS_URL, params=params)
    result = data.get("result", {}) or {}
    return result
