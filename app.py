# app.py
import os
import pandas as pd
import streamlit as st

from src.config import load_settings
from src.http_client import HttpClient
from src.geo import miles_to_meters, generate_tile_centers
from src.places_collector import collect_places
from src.reviews_collector import collect_reviews

# NOTE: your file is named insights.py in /src (based on your screenshot)
from src.insights import add_insights

# --- Optional: load .env locally (safe on Render too) ---
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


st.set_page_config(page_title="Google Places Review Insights", layout="wide")
st.title("Google Places Review Insights (Tableau-ready)")

# Validate API key early
api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
if not api_key:
    st.error("Missing GOOGLE_MAPS_API_KEY. Add it in Render → Environment Variables.")
    st.stop()

settings = load_settings()
client = HttpClient(timeout_sec=settings.timeout_sec, sleep_sec=settings.sleep_between_requests_sec)

# -------------------------
# Helpers: Autocomplete + Resolve
# -------------------------
AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GEOCODE_URL = settings.geocode_url  # from config


def get_address_suggestions(user_input: str, limit: int = 6):
    params = {
        "input": user_input,
        "types": "geocode",  # cities + addresses
        "key": settings.api_key,
    }
    data = client.get_json(AUTOCOMPLETE_URL, params=params)
    preds = data.get("predictions", []) or []
    return [{"description": p.get("description"), "place_id": p.get("place_id")} for p in preds[:limit]]


def resolve_place(place_id: str):
    params = {
        "place_id": place_id,
        "fields": "formatted_address,address_component,geometry",
        "key": settings.api_key,
    }
    data = client.get_json(DETAILS_URL, params=params)
    status = data.get("status")
    if status != "OK":
        raise RuntimeError(f"Place Details (resolve) error: status={status}, msg={data.get('error_message')}")
    return data.get("result", {}) or {}


def geocode_address(address: str):
    params = {"address": address, "key": settings.api_key}
    data = client.get_json(GEOCODE_URL, params=params)
    status = data.get("status")
    if status != "OK":
        raise RuntimeError(f"Geocode error: status={status}, msg={data.get('error_message')}")
    loc = data["results"][0]["geometry"]["location"]
    formatted = data["results"][0].get("formatted_address")
    return float(loc["lat"]), float(loc["lng"]), formatted


def parse_components(address_components: list) -> dict:
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


# -------------------------
# UI
# -------------------------
user_input = st.text_input("City/Address", "Plano, TX")
keyword = st.text_input("Keyword (restaurant, mcdonalds, pizza...)", "mcdonalds")
radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=200, value=10, step=1)

st.caption("Tip: Type at least 3 characters to see address suggestions. Select one for a full normalized address.")

suggestions = []
selected = None
resolved = None

if user_input and len(user_input.strip()) >= 3:
    try:
        suggestions = get_address_suggestions(user_input.strip(), limit=6)
    except Exception as e:
        st.warning(f"Autocomplete unavailable (will fallback to geocode on run): {e}")

if suggestions:
    selected = st.selectbox(
        "Select the best match (auto-fills full city/state/ZIP when available)",
        options=suggestions,
        format_func=lambda x: x["description"],
    )
    if selected and selected.get("place_id"):
        try:
            resolved = resolve_place(selected["place_id"])
        except Exception as e:
            st.warning(f"Could not resolve selection. Will fallback to geocode on run. Details: {e}")

run_btn = st.button("Run Analysis")

# -------------------------
# Run
# -------------------------
if run_btn:
    # Determine lat/lng + normalized address
    try:
        if resolved:
            loc = (resolved.get("geometry") or {}).get("location") or {}
            lat, lon = float(loc.get("lat")), float(loc.get("lng"))
            formatted_address = resolved.get("formatted_address")
            comp = parse_components(resolved.get("address_components", []))
        else:
            lat, lon, formatted_address = geocode_address(user_input.strip())
            comp = {"city": None, "state": None, "zip": None, "country": None}

        st.success(
            f"Resolved Address: {formatted_address or user_input} | "
            f"Lat/Lon: {lat:.5f}, {lon:.5f} | "
            f"City: {comp.get('city')} | State: {comp.get('state')} | ZIP: {comp.get('zip')}"
        )
    except Exception as e:
        st.error(f"Failed to resolve address. Error: {e}")
        st.stop()

    # Tiling logic (handles large radii like 100 miles)
    radius_m = miles_to_meters(radius_miles)
    tile_radius_m = min(settings.tile_radius_m, settings.max_nearby_radius_m)
    tile_centers = generate_tile_centers(lat, lon, radius_m=radius_m, tile_radius_m=tile_radius_m)

    st.info(
        f"Geocoded to: {lat:.5f}, {lon:.5f} | "
        f"Tiles: {len(tile_centers)} | "
        f"Tile radius ≈ {tile_radius_m / 1609.344:.1f} miles"
    )

    # Collect places
    with st.spinner("Collecting places (Nearby Search)..."):
        try:
            places = collect_places(client, settings, tile_centers, tile_radius_m, keyword)
        except Exception as e:
            st.error(f"Failed collecting places: {e}")
            st.stop()

    st.success(f"Places collected: {len(places)}")

    if not places:
        st.warning("No places found. Try increasing radius or changing keyword.")
        st.stop()

    # Collect reviews + store addresses
    with st.spinner("Collecting reviews + store addresses (Place Details)..."):
        try:
            results = collect_reviews(client, settings, places)
        except Exception as e:
            st.error(f"Failed collecting reviews: {e}")
            st.stop()

    places_df = pd.DataFrame(results["places"])
    reviews_df = pd.DataFrame(results["reviews"])

    if reviews_df.empty:
        st.warning("No reviews returned for the found places. (Google often provides only a small set of reviews.)")
    else:
        tableau_df = add_insights(reviews_df)

        st.subheader("Preview: Tableau-ready data (includes store address + ZIP)")
        st.dataframe(tableau_df.head(50), use_container_width=True)

        st.download_button(
            "Download places.csv",
            places_df.to_csv(index=False).encode("utf-8"),
            "places.csv",
            "text/csv",
        )
        st.download_button(
            "Download reviews.csv",
            reviews_df.to_csv(index=False).encode("utf-8"),
            "reviews.csv",
            "text/csv",
        )
        st.download_button(
            "Download tableau_reviews.csv",
            tableau_df.to_csv(index=False).encode("utf-8"),
            "tableau_reviews.csv",
            "text/csv",
        )

        st.caption("Use tableau_reviews.csv in Tableau Public to build dashboards.")
