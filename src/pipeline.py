# src/pipeline.py
import os
import json
import pandas as pd

from .config import load_settings
from .http_client import HttpClient
from .geo import miles_to_meters, generate_tile_centers
from .places_collector import collect_places
from .reviews_collector import collect_reviews
from .insights import add_insights
from .exporters import ensure_dir, export_places_csv, export_reviews_csv, export_tableau_reviews_csv

def geocode_address(client: HttpClient, settings, address: str):
    params = {"address": address, "key": settings.api_key}
    data = client.get_json(settings.geocode_url, params=params)
    status = data.get("status")
    if status != "OK":
        raise RuntimeError(f"Geocode error: status={status}, msg={data.get('error_message')}")
    loc = data["results"][0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])

def run():
    settings = load_settings()
    client = HttpClient(timeout_sec=settings.timeout_sec, sleep_sec=settings.sleep_between_requests_sec)

    print("\n=== Google Places Review Insights (Tableau-ready) ===\n")
    address = input("Enter a city/address (example: 'Lewisville, TX'): ").strip()
    keyword = input("Enter business keyword (example: 'restaurant' or 'mcdonalds'): ").strip()

    radius_miles = float(input("Enter radius in miles (example: 100): ").strip())
    radius_m = miles_to_meters(radius_miles)

    lat, lon = geocode_address(client, settings, address)
    print(f"\nGeocoded: {address} -> lat={lat:.5f}, lon={lon:.5f}")

    # Tiling (handles big radii like 100 miles)
    tile_radius_m = min(settings.tile_radius_m, settings.max_nearby_radius_m)
    tile_centers = generate_tile_centers(lat, lon, radius_m=radius_m, tile_radius_m=tile_radius_m)
    print(f"Using tiling: {len(tile_centers)} search centers, tile_radius ≈ {tile_radius_m/1609.344:.1f} miles\n")

    # Collect places
    places = collect_places(client, settings, tile_centers, tile_radius_m, keyword)
    print(f"Collected {len(places)} unique places.\n")

    # Collect reviews + enrich place data
    results = collect_reviews(client, settings, places)
    places_enriched = results["places"]
    reviews = results["reviews"]
    print(f"Collected {len(reviews)} total review rows.\n")

    # Build insights for Tableau
    reviews_df = pd.DataFrame(reviews)
    tableau_df = add_insights(reviews_df)

    # Output
    ensure_dir(settings.data_raw_dir)
    ensure_dir(settings.data_processed_dir)

    places_csv = os.path.join(settings.data_processed_dir, "places.csv")
    reviews_csv = os.path.join(settings.data_processed_dir, "reviews.csv")
    tableau_csv = os.path.join(settings.data_processed_dir, "tableau_reviews.csv")

    export_places_csv(places_enriched, places_csv)
    export_reviews_csv(reviews, reviews_csv)
    export_tableau_reviews_csv(tableau_df, tableau_csv)

    print("✅ Exports complete:")
    print(f" - {places_csv}")
    print(f" - {reviews_csv}")
    print(f" - {tableau_csv}")

if __name__ == "__main__":
    run()
