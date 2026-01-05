# src/exporters.py
import os
import pandas as pd

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def export_places_csv(places: list, out_path: str) -> None:
    df = pd.DataFrame(places)
    df.to_csv(out_path, index=False)

def export_reviews_csv(reviews: list, out_path: str) -> None:
    df = pd.DataFrame(reviews)
    df.to_csv(out_path, index=False)

def export_tableau_reviews_csv(tableau_df: pd.DataFrame, out_path: str) -> None:
    # Tableau-friendly: flat, clean columns
    tableau_df.to_csv(out_path, index=False)
