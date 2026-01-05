# src/insights.py
import re
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

STOPWORDS = {
    "the","a","an","and","or","but","to","of","in","on","for","with","is","it","this","that",
    "was","were","are","be","been","i","we","they","you","he","she","my","our","your","their",
    "at","as","so","if","from","by","just","very","really","too","not"
}

def sentiment_label(compound: float) -> str:
    if compound > 0.05:
        return "Positive"
    if compound < -0.05:
        return "Negative"
    return "Neutral"

def add_insights(reviews_df: pd.DataFrame) -> pd.DataFrame:
    df = reviews_df.copy()
    df["comment"] = df["comment"].fillna("").astype(str).str.strip()
    df = df[df["comment"] != ""].copy()

    analyzer = SentimentIntensityAnalyzer()
    df["compound"] = df["comment"].apply(lambda x: analyzer.polarity_scores(x)["compound"])
    df["sentiment"] = df["compound"].apply(sentiment_label)

    lower = df["comment"].str.lower()

    df["issue_food"] = lower.str.contains(r"\b(cold|stale|soggy|undercooked|overcooked)\b", regex=True)
    df["issue_service"] = lower.str.contains(r"\b(slow|rude|wrong order|bad service|unhelpful)\b", regex=True)
    df["issue_cleanliness"] = lower.str.contains(r"\b(dirty|unclean|filthy|messy)\b", regex=True)
    df["issue_price"] = lower.str.contains(r"\b(expensive|overpriced|not worth)\b", regex=True)

    # optional: hour-of-day for Tableau
    dt = pd.to_datetime(df["date_utc"], errors="coerce")
    df["hour_utc"] = dt.dt.hour

    return df
