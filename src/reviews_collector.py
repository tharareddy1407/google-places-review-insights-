# src/reviews_collector.py
from datetime import datetime
from typing import Dict, List

from .config import Settings
from .http_client import HttpClient


def parse_components(address_components: list) -> dict:
    """
    Extracts city/state/zip/country from Google's address_components.
    """
    out = {"city": None, "state": None, "zip": None, "country": None}
    for c in address_components or []:
        types = c.get("types", [])
        if "locality" in types:
            out["city"] = c.get("long_name")
        if "administrative_area_level_1" in types:
            out["state"] = c.get("short_name")
        if "postal_code" in types:
            out["zip"] = c.get("long_name")
        if "country" in types:
            out["country"] = c.get("short_name")
    return out


def fetch_place_details(client: HttpClient, settings: Settings, place_id: str) -> Dict:
    """
    Place Details: fetch reviews + full store address.
    """
    params = {
        "place_id": place_id,
        "fields": "place_id,name,rating,user_ratings_total,reviews,formatted_address,address_component,geometry",
        "key": settings.api_key,
    }
    data = client.get_json(settings.details_url, params=params)

    status = data.get("status")
    if status != "OK":
        raise RuntimeError(
            f"Place Details error for {place_id}: status={status}, msg={data.get('error_message')}"
        )
    return data.get("result", {}) or {}


def collect_reviews(
    client: HttpClient,
    settings: Settings,
    places: List[Dict],
) -> Dict[str, List[Dict]]:
    """
    Returns:
      places_enriched: list of places with rating + user_ratings_total + full address fields
      reviews: list of normalized review rows (1 row per review) including store address fields
    """
    places_enriched: List[Dict] = []
    reviews_rows: List[Dict] = []

    for p in places:
        pid = p["place_id"]
        details = fetch_place_details(client, settings, pid)

        place_name = details.get("name") or p.get("name")
        avg_rating = details.get("rating")
        ratings_total = details.get("user_ratings_total")

        store_address = details.get("formatted_address")
        comp = parse_components(details.get("address_components", []))

        # Keep store lat/lon from details when available
        loc = (details.get("geometry") or {}).get("location") or {}
        store_lat = loc.get("lat", p.get("lat"))
        store_lon = loc.get("lng", p.get("lon"))

        places_enriched.append({
            **p,
            "name": place_name,
            "avg_rating": avg_rating,
            "user_ratings_total": ratings_total,
            "store_address": store_address,
            "store_city": comp["city"],
            "store_state": comp["state"],
            "store_zip": comp["zip"],
            "store_country": comp["country"],
            "lat": store_lat,
            "lon": store_lon,
        })

        reviews = details.get("reviews", []) or []
        for r in reviews:
            ts = r.get("time")
            reviews_rows.append({
                "place_id": pid,
                "restaurant_name": place_name,

                # Store/location fields for Tableau grouping
                "store_address": store_address,
                "store_city": comp["city"],
                "store_state": comp["state"],
                "store_zip": comp["zip"],

                # Review fields
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "comment": r.get("text"),
                "review_time_unix": ts,
                "date_utc": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None,
            })

    return {"places": places_enriched, "reviews": reviews_rows}
