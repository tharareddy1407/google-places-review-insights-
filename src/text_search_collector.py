# src/text_search_collector.py
import time
import math
from typing import Dict, List, Set, Tuple

from .config import Settings
from .http_client import HttpClient

EARTH_RADIUS_M = 6371000.0

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    """Distance in meters."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))

def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    """Distance in miles."""
    return haversine_m(lat1, lon1, lat2, lon2) / 1609.344


def text_search_pages(client: HttpClient, settings: Settings, query: str) -> List[Dict]:
    params = {"query": query, "key": settings.api_key}
    all_results: List[Dict] = []
    page = 0

    while True:
        data = client.get_json(settings.textsearch_url, params=params)
        status = data.get("status")

        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Text Search error: status={status}, msg={data.get('error_message')}")

        results = data.get("results", []) or []
        all_results.extend(results)

        token = data.get("next_page_token")
        page += 1
        if not token or page >= settings.max_pages_textsearch:
            break

        time.sleep(settings.next_page_token_wait_sec)
        params["pagetoken"] = token

    return all_results


def collect_places_textsearch(
    client: HttpClient,
    settings: Settings,
    query: str,
    filter_center: Tuple[float, float],
    filter_radius_m: float,
) -> List[Dict]:
    c_lat, c_lon = filter_center
    raw = text_search_pages(client, settings, query=query)

    seen: Set[str] = set()
    places: List[Dict] = []

    for p in raw:
        pid = p.get("place_id")
        if not pid or pid in seen:
            continue

        geo = p.get("geometry", {}).get("location", {}) or {}
        p_lat = geo.get("lat")
        p_lon = geo.get("lng")
        if p_lat is None or p_lon is None:
            continue

        dist_m = haversine_m(c_lat, c_lon, p_lat, p_lon)
        if dist_m > filter_radius_m:
            continue

        seen.add(pid)
        places.append({
            "place_id": pid,
            "name": p.get("name"),
            "vicinity": p.get("formatted_address") or p.get("vicinity"),
            "lat": p_lat,
            "lon": p_lon,
            "types": ",".join(p.get("types", []) or []),
            "distance_m": dist_m,
            "distance_miles": dist_m / 1609.344,
        })

    places.sort(key=lambda x: x["distance_m"])
    return places
