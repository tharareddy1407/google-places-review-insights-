# src/geo.py
import math
from typing import List, Tuple

EARTH_RADIUS_M = 6371000.0

def miles_to_meters(mi: float) -> float:
    return mi * 1609.344

def meters_to_lat_deg(m: float) -> float:
    return (m / EARTH_RADIUS_M) * (180.0 / math.pi)

def meters_to_lon_deg(m: float, at_lat_deg: float) -> float:
    lat_rad = math.radians(at_lat_deg)
    return (m / (EARTH_RADIUS_M * max(0.000001, math.cos(lat_rad)))) * (180.0 / math.pi)

def generate_tile_centers(lat: float, lon: float, radius_m: float, tile_radius_m: float) -> List[Tuple[float, float]]:
    """
    Cover a circle of radius_m with a grid of smaller circles tile_radius_m.
    Simple grid approach: good enough for portfolio + business insights.
    """
    if radius_m <= tile_radius_m:
        return [(lat, lon)]

    step_m = tile_radius_m * 1.5  # overlap a bit to reduce misses
    dlat = meters_to_lat_deg(step_m)
    dlon = meters_to_lon_deg(step_m, lat)

    lat_extent = meters_to_lat_deg(radius_m)
    lon_extent = meters_to_lon_deg(radius_m, lat)

    centers = []
    lat_min, lat_max = lat - lat_extent, lat + lat_extent
    lon_min, lon_max = lon - lon_extent, lon + lon_extent

    r2 = radius_m * radius_m

    cur_lat = lat_min
    while cur_lat <= lat_max:
        cur_lon = lon_min
        while cur_lon <= lon_max:
            # keep only grid points inside circle (approx)
            dy = (cur_lat - lat) * (math.pi/180) * EARTH_RADIUS_M
            dx = (cur_lon - lon) * (math.pi/180) * EARTH_RADIUS_M * math.cos(math.radians(lat))
            if (dx*dx + dy*dy) <= r2:
                centers.append((cur_lat, cur_lon))
            cur_lon += dlon
        cur_lat += dlat

    # Always include center
    centers.append((lat, lon))
    # Deduplicate (rounded)
    uniq = {}
    for a, b in centers:
        uniq[(round(a, 5), round(b, 5))] = (a, b)
    return list(uniq.values())
