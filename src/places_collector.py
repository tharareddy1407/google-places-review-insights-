# src/places_collector.py
import time
from typing import Dict, List, Set, Tuple

from .config import Settings
from .http_client import HttpClient

def nearby_search_tile(
    client: HttpClient,
    settings: Settings,
    lat: float,
    lon: float,
    radius_m: int,
    keyword: str,
) -> List[Dict]:
    params = {
        "location": f"{lat},{lon}",
        "radius": radius_m,
        "keyword": keyword,
        "key": settings.api_key,
    }

    all_results: List[Dict] = []
    page = 0

    while True:
        data = client.get_json(settings.nearby_url, params=params)
        status = data.get("status")

        if status not in ("OK", "ZERO_RESULTS"):
            # Common: OVER_QUERY_LIMIT, REQUEST_DENIED, INVALID_REQUEST
            raise RuntimeError(f"Nearby Search error: status={status}, msg={data.get('error_message')}")

        results = data.get("results", []) or []
        all_results.extend(results)

        token = data.get("next_page_token")
        page += 1
        if not token or page >= settings.max_pages_per_tile:
            break

        # token needs a short wait before it becomes valid
        time.sleep(settings.next_page_token_wait_sec)
        params["pagetoken"] = token

    return all_results

def collect_places(
    client: HttpClient,
    settings: Settings,
    tile_centers: List[Tuple[float, float]],
    tile_radius_m: int,
    keyword: str,
) -> List[Dict]:
    """
    Returns unique place rows:
      { place_id, name, vicinity, lat, lon, types }
    """
    seen: Set[str] = set()
    places: List[Dict] = []

    for i, (lat, lon) in enumerate(tile_centers, start=1):
        results = nearby_search_tile(client, settings, lat, lon, tile_radius_m, keyword)

        for p in results:
            pid = p.get("place_id")
            if not pid or pid in seen:
                continue
            seen.add(pid)

            geo = p.get("geometry", {}).get("location", {}) or {}
            places.append({
                "place_id": pid,
                "name": p.get("name"),
                "vicinity": p.get("vicinity"),
                "lat": geo.get("lat"),
                "lon": geo.get("lng"),
                "types": ",".join(p.get("types", []) or []),
            })

        # light pacing between tiles
        time.sleep(settings.sleep_between_requests_sec)

    return places
