# src/reviews_collector.py
from datetime import datetime
from typing import Dict, List

from .config import Settings
from .http_client import HttpClient

def fetch_place_details(client: HttpClient, settings: Settings, place_id: str) -> Dict:
    params = {
        "place_id": place_id,
        "fields": "place_id,name,rating,user_ratings_total,reviews",
        "key": settings.api_key,
    }
    data = client.get_json(settings.details_url, params=params)

    status = data.get("status")
    if status != "OK":
        raise RuntimeError(f"Place Details error for {place_id}: status={status}, msg={data.get('error_message')}")
    return data.get("result", {}) or {}

def collect_reviews(
    client: HttpClient,
    settings: Settings,
    places: List[Dict],
) -> Dict[str, List[Dict]]:
    """
    Returns:
      places_enriched: list of places with rating + user_ratings_total
      reviews: list of normalized review rows (1 row per review)
    """
    places_enriched: List[Dict] = []
    reviews_rows: List[Dict] = []

    for idx, p in enumerate(places, start=1):
        pid = p["place_id"]
        details = fetch_place_details(client, settings, pid)

        place_name = details.get("name") or p.get("name")
        avg_rating = details.get("rating")
        ratings_total = details.get("user_ratings_total")

        places_enriched.append({
            **p,
            "avg_rating": avg_rating,
            "user_ratings_total": ratings_total,
        })

        reviews = details.get("reviews", []) or []
        for r in reviews:
            ts = r.get("time")
            reviews_rows.append({
                "place_id": pid,
                "restaurant_name": place_name,
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "comment": r.get("text"),
                "review_time_unix": ts,
                "date_utc": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None,
            })

    return {"places": places_enriched, "reviews": reviews_rows}
