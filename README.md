# Location Intelligence & Review Analytics Platform
## Geo-Enabled Business Discovery & Customer Review Insights

## Project Overview
The **Location Intelligence & Review Analytics Platform** is a data-driven system designed to discover businesses within a user-defined geographic radius, collect customer reviews, and generate actionable business insights.

The platform enables users to search by city or address, specify a radius in miles, and analyze customer sentiment, ratings, and review trends across multiple locations.  
It provides a scalable and flexible alternative to manual review analysis and fragmented location-based research.

This solution is built for **business intelligence, market analysis, and customer experience insights**, producing BI-ready datasets and interactive visualizations.

---

## Who This Project Is For
This project is intended for:
- Business intelligence and analytics teams
- Product and strategy teams
- Retail and restaurant operations leaders
- Data engineers and analytics engineers
- Consultants analyzing brand performance across regions
- Engineers exploring geospatial and API-driven analytics systems

---

## Key Differentiator
### Location-Aware, Multi-Strategy Business Discovery
The platform supports **two complementary search strategies** to balance speed, coverage, and geographic accuracy:

#### Brand Search (Text Search)
- Fast, ranked discovery of brand locations
- Ideal for brand-level analysis
- Lower API usage and quicker insights

#### Geo Coverage (Tiled Nearby Search)
- Geographic tiling for broader spatial coverage
- Strict distance-based filtering
- Suitable for location density and regional analysis

Both strategies apply **deduplication and radius enforcement** to ensure accurate results.

---

## Why This Is a Smarter Approach
### Traditional Review Analysis Typically Involves
- Manual searching on maps or review platforms
- Limited visibility across multiple locations
- No structured sentiment or trend analysis
- Difficulty exporting data for BI tools

### This Platform Replaces That With
- Automated location discovery using geospatial logic
- Programmatic review collection
- Sentiment and rating analysis at scale
- BI-ready exports and in-app visual insights

### Result
A unified, scalable system for turning location-based customer feedback into **actionable business intelligence**.

---

## Updated User Flow
1. User enters a city or street address
2. User specifies a search radius (in miles)
3. User selects a search strategy (Brand Search or Geo Coverage)
4. Platform discovers businesses within the defined geography
5. Customer reviews are collected and enriched with store details
6. Sentiment, ratings, and trends are analyzed
7. Visual insights are displayed and datasets are made available for download

---

## Use Cases
This platform is especially effective for:
- Brand perception analysis across regions
- Identifying locations with high negative sentiment
- Comparing customer experience across stores
- Supporting location-based business decisions
- Feeding dashboards in BI tools such as Tableau

---

## Technologies Used
- Python for data processing and orchestration
- Google Places API (Geocoding, Text Search, Nearby Search, Place Details)
- Streamlit for interactive web application
- Pandas and NumPy for data analysis
- Matplotlib for responsive visualizations
- Render for cloud deployment
- Tableau (via CSV exports) for advanced BI dashboards

---

## System Implementation Steps
### 1. Requirement Analysis
Identified challenges in manual, inconsistent review analysis and limited geographic visibility.

### 2. Architecture Design
Designed a modular system with:
- Address resolution and normalization
- Multi-strategy search layer
- Review collection and enrichment
- Analytics and visualization layer

### 3. Location Resolution
- Autocomplete and geocoding for user-entered addresses
- Automatic extraction of city, state, and ZIP
- Central coordinate selection for distance calculations

### 4. Business Discovery
- Implemented Brand Search for ranked discovery
- Implemented Geo Coverage using tiled Nearby Search
- Enforced strict radius filtering using geospatial calculations

### 5. Review Collection
- Retrieved recent reviews per location
- Extracted ratings, timestamps, authors, and review text
- Enriched data with store-level address details

### 6. Insight Generation
- Sentiment classification (Positive, Neutral, Negative)
- Rating distribution analysis
- Identification of locations with high negative feedback
- Time-based review trend analysis

### 7. Visualization Layer
- KPI metrics for high-level overview
- Bar charts, pie charts, and trend lines
- Responsive layout for desktop and mobile users

### 8. BI Export
- Clean CSV outputs for Tableau and other BI tools
- Structured datasets suitable for dashboards and reporting

---

## Live Demo
### Website
https://google-places-review-insights.onrender.com

The live application demonstrates real-time business discovery, review analysis, and interactive visual insights.

---

## Step-by-Step Demo Guide
### Step 1: Enter Location
Enter a city name or street address in the input field.

### Step 2: Configure Search
- Select a search radius in miles
- Choose a search strategy (Brand Search or Geo Coverage)

### Step 3: Run Analysis
Click **Run Analysis** to discover businesses and collect reviews.

### Step 4: Explore Insights
- Review KPIs and charts
- Identify sentiment trends and rating distributions
- Inspect stores with high negative feedback

### Step 5: Export Data
Download BI-ready CSV files for further analysis or Tableau dashboards.

---

## Important Notes
- Google Places API returns ranked subsets, not guaranteed full coverage
- Large radii may require more API calls and increased runtime
- Review availability varies by business and location
- The platform respects Google API usage constraints

---

## Why This Is Different
Unlike basic review scraping or manual analysis:
- Uses geospatial logic for accurate radius filtering
- Supports multiple discovery strategies
- Produces structured, BI-ready datasets
- Combines engineering, analytics, and business insights in one platform

---

## Disclaimer
This project is a portfolio and demonstration system intended for educational and analytical purposes only.  
All data is retrieved using official Google APIs in accordance with their terms of service.
