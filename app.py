import os
import pandas as pd
import streamlit as st

from src.config import load_settings
from src.http_client import HttpClient
from src.geo import miles_to_meters, generate_tile_centers
from src.places_collector import collect_places
from src.reviews_collector import collect_reviews
from src.insights import add_insights

st.set_page_config(page_title="Google Places Review Insights", layout="wide")

st.title("Google Places Review Insights (Tableau-ready)")

api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
if not api_key:
    st.error("Missing GOOGLE_MAPS_API_KEY. Add it in Render → Environment.")
    st.stop()

settings = load_settings()
client = HttpClient(timeout_sec=settings.timeout_sec, sleep_sec=settings.sleep_between_requests_sec)

address = st.text_input("City/Address", "Lewisville, TX")
keyword = st.text_input("Keyword (restaurant, mcdonalds, pizza...)", "restaurant")
radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=200, value=25, step=1)

run_btn = st.button("Run Analysis")

def geocode_address(address: str):
    params = {"address": address, "key": settings.api_key}
    data = client.get_json(settings.geocode_url, params=params)
    status = data.get("status")
    if status != "OK":
        raise RuntimeError(f"Geocode error: status={status}, msg={data.get('error_message')}")
    loc = data["results"][0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])

if run_btn:
    with st.spinner("Geocoding address..."):
        lat, lon = geocode_address(address)

    radius_m = miles_to_meters(radius_miles)

    tile_radius_m = min(settings.tile_radius_m, settings.max_nearby_radius_m)
    tile_centers = generate_tile_centers(lat, lon, radius_m=radius_m, tile_radius_m=tile_radius_m)

    st.info(f"Geocoded to: {lat:.5f}, {lon:.5f} | Tiles: {len(tile_centers)} | Tile radius ≈ {tile_radius_m/1609.344:.1f} miles")

    with st.spinner("Collecting places..."):
        places = collect_places(client, settings, tile_centers, tile_radius_m, keyword)

    st.success(f"Places collected: {len(places)}")

    with st.spinner("Collecting reviews (Place Details)..."):
        results = collect_reviews(client, settings, places)

    places_df = pd.DataFrame(results["places"])
    reviews_df = pd.DataFrame(results["reviews"])
    tableau_df = add_insights(reviews_df)

    st.subheader("Preview: Tableau-ready data")
    st.dataframe(tableau_df.head(50), use_container_width=True)

    # Download buttons
    st.download_button("Download places.csv", places_df.to_csv(index=False).encode("utf-8"), "places.csv", "text/csv")
    st.download_button("Download reviews.csv", reviews_df.to_csv(index=False).encode("utf-8"), "reviews.csv", "text/csv")
    st.download_button("Download tableau_reviews.csv", tableau_df.to_csv(index=False).encode("utf-8"), "tableau_reviews.csv", "text/csv")
