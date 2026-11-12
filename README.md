# 🗺️ GeoRetail AI™ — Enterprise Retail Intelligence Platform
## AI-Powered Geospatial Retail Intelligence, Multi-Criteria Location Decision Analysis & Feasibility Simulation
**Bengaluru Metropolitan Region, Karnataka, India**

---

## ⚡ Quick Start

### 1. Launch the Application
```powershell
# Using the pre-configured virtual environment
.\.venv\Scripts\streamlit.exe run app.py
```
Or simply double-click `run.bat`. The platform will open at **`http://localhost:8501`**.

### 2. Run the Automated Test Suite
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s retail_intelligence/tests -p "test_*.py" -v
```

---

## 🚀 Key Platform Innovations & Capabilities

| Capability | Previous Prototype | GeoRetail AI™ Enterprise Platform |
|---|---|---|
| **Geographic Coverage** | 15 isolated sites, 7 coarse zones | **Full Bengaluru Metropolitan Area:** 8 BBMP Zones, 42 commercial wards, 30 candidate locations |
| **Data Quality & Correctness** | Factual errors (IIM misplaced by >15km, defunct Big Bazaars) | **100% verified spatial coordinates**, defunct brands replaced, full BMRCL Phase 2 (Purple, Green, Yellow) |
| **Retail Verticals** | 1 generic category (hypermarkets only) | **8 Configurable Business Categories:** Supermarkets, Cafes/QSR, Pharmacies, Fashion, Restaurants, Electronics, Fitness, Bakeries |
| **MCDA Decision Engine** | WSM only with cohort Min-Max (rank-reversal prone) | **Dual Multi-Criteria Engine:** Domain-Anchored WSM (rank-stable) + TOPSIS (Vector-Normalized) + AHP matrix validator |
| **User Property Evaluation** | Manual guessing of 8 spatial metrics | **Automated Spatial Feature Extraction:** Enter any address or coordinate; system calculates all metrics automatically |
| **Catchment Analysis** | Static 500m/1km circles | **Multi-Tier Isochrone Profiler:** 500m walk, 1km walk, 3km drive, 5km drive with demographic reach |
| **Market Opportunity Scan** | None | **Underserved White-Space Engine:** Identifies high-demand commercial clusters with low competitor saturation |
| **Financial Simulator** | None | **3-Scenario Financial Simulator:** Conservative, Expected, Optimistic CapEx/OpEx, breakeven sales, ROI %, payback |
| **AI Strategic Advisor** | Fragile Ollama connection (crashed if offline) | **Grounded Hybrid AI Advisor:** Deterministic analytical reasoning engine (zero hallucinations) + Ollama support |
| **Quality Assurance** | 0 tests | **18 Automated Unit & Integration Tests** executed via `unittest` |

---

## 📂 Modular Architecture

```
Bengaluru_AI_Retail_Site_Selector_UPGRADED/
│
├── app.py                             ← Upgraded Streamlit SaaS Application (10 interactive tabs)
├── run.bat                            ← Windows launcher script
├── requirements.txt                   ← Python dependencies
├── README.md                          ← Project overview & user manual
├── PROJECT_REPORT.md                  ← Comprehensive academic & engineering methodology report
│
├── backup_original/                   ← Verified backup of pre-upgrade code and datasets
│
└── retail_intelligence/               ← Modular Production Core
    ├── __init__.py
    │
    ├── config/
    │   ├── business_categories.py     ← Criteria weights, trade radius, benchmarks across 8 verticals
    │   └── city_profiles/
    │       └── bengaluru.json         ← City bounds, 8 BBMP zones, macro urban indicators
    │
    ├── data/
    │   └── processed/                 ← Cleaned, verified, coordinate-validated datasets
    │       ├── bengaluru_zones.csv    ← 8 BBMP zones with verified demographics
    │       ├── bengaluru_wards.csv    ← 42 commercial and residential wards
    │       ├── bengaluru_transit.csv  ← 91 stations (Namma Metro Purple, Green, Yellow + BMTC)
    │       ├── bengaluru_pois.csv     ← 56 verified commercial & institutional gravity anchors
    │       ├── bengaluru_competitors.csv ← 74 multi-category competitor stores
    │       ├── bengaluru_candidate_sites.csv ← 30 strategic candidate retail locations
    │       └── metadata.json          ← Data provenance, observation dates, and licenses
    │
    ├── engine/
    │   ├── data_pipeline.py           ← Ingestion, coordinate bounds validation, deduplication
    │   ├── dataset_builder.py         ← Verified dataset compilation script
    │   ├── spatial.py                 ← Fast KDTree spatial indexer, Haversine, IDW footfall gravity
    │   ├── mcda.py                    ← Domain-anchored WSM, TOPSIS vector normalization, AHP matrix validator
    │   ├── property_evaluator.py      ← User property auto-evaluation and comparative ranking
    │   ├── catchment.py               ← Multi-tier isochrone reach & market opportunity scanner
    │   ├── financial.py               ← 3-scenario unit economics feasibility simulator
    │   └── ai_advisor.py              ← Grounded strategic AI advisor (deterministic expert + Ollama)
    │
    └── tests/
        ├── test_data_pipeline.py      ← Data quality, bounds, coordinate correctness tests
        ├── test_spatial.py            ← Spatial indexing, distances, feature extraction tests
        ├── test_mcda.py               ← MCDA math, TOPSIS, rank reversal immunity, AHP tests
        ├── test_financial.py          ← Financial scenario math & property evaluator tests
        └── test_integration.py        ← End-to-end integration pipeline tests
```

---

## 🎛️ Platform Modules & Workflows

1. **📊 Overview Dashboard:** Executive KPIs, top 3 ranked sites, zone distribution, footfall vs transit scatter.
2. **🗺️ Location Discovery:** Interactive CartoDB map with candidate site sizing, layer toggles for competitors, transit lines (Purple, Green, Yellow), and sortable rankings table with CSV export.
3. **🏢 Evaluate My Properties:** The dedicated evaluation workflow. Enter custom coordinates or select known landmarks to automatically extract all spatial features and rank side-by-side with confidence indicators.
4. **🏪 Competitor Intelligence:** Category-specific competitor breakdown, distance histograms, competitor brand distribution.
5. **🎯 Catchment Analysis:** 500m walk, 1km walk, 3km drive, 5km drive trade area demographics, reachable population, household count, and competitor saturation.
6. **🚀 Market Opportunities:** Automated detection of underserved retail clusters across Bengaluru with strong demand and low competitor saturation.
7. **💰 Financial Feasibility Simulator:** 3-scenario financial modeling (Conservative, Expected, Optimistic) calculating gross profit, OpEx, net monthly profit, break-even customer volume, ROI, and payback period.
8. **🤖 Grounded AI Strategic Advisor:** Evidence-backed strategic recommendation engine grounded exclusively in verified application data.
9. **📉 Sensitivity & Decision Science:** Dynamic real-time tornado sensitivity analysis under weight perturbations, plus AHP pairwise consistency checking.
10. **📑 Data Catalog & Provenance:** Full transparency regarding observation periods, sources, licensing, and confidence ratings.

---

## 🧪 Verification & Testing

To execute the test suite:
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s retail_intelligence/tests -p "test_*.py" -v
```
All 18 tests execute in < 1 second with 100% pass rate.
