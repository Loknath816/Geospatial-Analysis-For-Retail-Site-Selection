# 🗺️ Geospatial Analysis for Retail Site Selection
**Bangalore, Karnataka | CSS7102 Mini Project | Presidency University**

---

## ⚡ Quick Start (3 Steps)

### Step 1 — Open the project in VS Code
```
File → Open Folder → select the `retail_site_selector` folder
```

### Step 2 — Open a Terminal in VS Code  
```
Terminal → New Terminal  (or Ctrl + `)
```

### Step 3 — Run the project
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```
The app opens automatically at **http://localhost:8501**

---

## 📂 Project Structure

```
retail_site_selector/
│
├── app.py                      ← Main Streamlit dashboard (run this)
├── requirements.txt            ← Python packages to install
├── run.bat                     ← Windows double-click launcher
├── README.md                   ← This file
│
└── data/
    ├── candidate_sites.csv     ← 15 Bangalore retail candidate locations
    ├── competitors.csv         ← 21 competitor store locations
    ├── transit_stops.csv       ← 31 metro & bus stops
    ├── pois.csv                ← 39 Points of Interest (malls, hospitals, IT parks)
    ├── zone_population.csv     ← Population data by Bangalore zone
    ├── feature_matrix.csv      ← Computed features per candidate site
    ├── ranked_sites.csv        ← Final suitability-scored rankings
    ├── sensitivity.csv         ← Sensitivity analysis results
    └── karnataka_districts_census.csv ← India 2011 Census data
```

---

## 📊 What the Dashboard Shows

| Tab | Content |
|-----|---------|
| 🗺️ Suitability Map | Interactive Folium map with colour-coded candidate sites |
| 📋 Rankings | Sortable table with suitability scores + CSV download |
| ⚖️ Compare Sites | Side-by-side comparison with radar chart |
| 📉 Sensitivity | Tornado chart showing which weights affect rankings most |
| 📊 Census Data | Karnataka districts from India 2011 Census |
| 📖 About Project | Full methodology explanation for viva |

---

## 🎛️ How to Use the Sidebar

- **Adjust sliders** to change the importance of each criterion
- Scores re-compute **instantly** on every slider change
- Layer toggles show/hide competitors, transit, and POIs on the map

---

## 💡 Project Explanation (For Your Viva)

**What does this project do?**
It scores and ranks 15 potential retail store locations in Bangalore using 8 spatial criteria derived from real census data and geographic analysis.

**How is the scoring done?**
Using a Weighted Sum Model (WSM):
1. For each location, compute 8 features (population density, competitor proximity, footfall index, transit access, etc.)
2. Normalize all features to [0–1] scale
3. Multiply each feature by its weight (adjustable by sliders)
4. Sum up = suitability score between 0 and 1

**What data was used?**
- India 2011 Census (district and sub-district level for Bangalore)
- OpenStreetMap data for competitors, transit, and POIs
- Bangalore Namma Metro + BMTC bus stop coordinates

**Why is this better than just using Google Maps / expert opinion?**
- Transparent: every score is traceable to individual criteria
- Reproducible: run the same analysis for any set of candidate locations
- Interactive: adjust weights based on business priorities
- Data-driven: backed by Census 2011 official data

---

## 🛠️ Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9+ |
| Streamlit | 1.35 |
| Folium | 0.16 |
| Plotly | 5.22 |
| Pandas | 2.2 |

---

## 📞 Troubleshooting

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Package install fails?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**streamlit_folium error?**
```bash
pip install streamlit-folium==0.21.0
```
