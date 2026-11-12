
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import json, urllib.request

st.set_page_config(
    page_title="Geospatial Analysis for Retail Site Selection — Bengaluru",
    page_icon="🗺️",
    layout="wide"
)
DATA = "data"

# ───────────────────────────── DATA LOADING ──────────────────────────────
@st.cache_data
def load_data():
    features = pd.read_csv(f"{DATA}/feature_matrix.csv")
    competitors = pd.read_csv(f"{DATA}/competitors.csv")
    transit = pd.read_csv(f"{DATA}/transit_stops.csv")
    pois = pd.read_csv(f"{DATA}/pois.csv")
    sensitivity = pd.read_csv(f"{DATA}/sensitivity.csv")
    zone_pop = pd.read_csv(f"{DATA}/zone_population.csv")
    census = pd.read_csv(f"{DATA}/karnataka_districts_census.csv")
    recent = pd.read_excel(f"{DATA}/recent_bengaluru_data.xlsx", sheet_name="Recent_Indicators")
    sources = pd.read_excel(f"{DATA}/recent_bengaluru_data.xlsx", sheet_name="Source_Catalog")
    assumptions = pd.read_excel(f"{DATA}/recent_bengaluru_data.xlsx", sheet_name="Business_Assumptions")
    return features, competitors, transit, pois, sensitivity, zone_pop, census, recent, sources, assumptions

features, competitors, transit, pois, sensitivity, zone_pop, census, recent, sources, assumptions = load_data()

# ───────────────────────── MCDA MODEL (WSM) ──────────────────────────────
# Criteria direction: "higher" = benefit criterion, "lower" = cost criterion
CRITERIA = {
    "poi_footfall":      {"direction": "higher", "label": "Footfall Index",       "default_weight": 28},
    "pop_density":       {"direction": "higher", "label": "Population Density",   "default_weight": 18},
    "nearest_comp_m":    {"direction": "higher", "label": "Competitor Distance",  "default_weight": 12},
    "comp_count_1km":    {"direction": "lower",  "label": "Competitor Count",     "default_weight": 10},
    "transit_count_500m":{"direction": "higher", "label": "Transit Stops (500m)", "default_weight": 10},
    "nearest_metro_m":   {"direction": "lower",  "label": "Metro Distance",       "default_weight": 8},
    "literacy_rate":     {"direction": "higher", "label": "Literacy Rate",        "default_weight": 7},
    "road_access_score": {"direction": "higher", "label": "Road Access Score",    "default_weight": 7},
}

DIRECTION = {k: v["direction"] for k, v in CRITERIA.items()}

def normalize(series, direction):
    """Min-Max normalization. Benefit criteria: higher is better. Cost criteria: lower is better."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    if direction == "higher":
        return (series - mn) / (mx - mn)
    else:
        return (mx - series) / (mx - mn)

def score_sites(df, weights):
    """Apply Weighted Sum Model: S(i) = Sigma wj * nj(i)"""
    normalized = {feat: normalize(df[feat], DIRECTION[feat]) for feat in DIRECTION}
    result = df.copy()
    result["suitability_score"] = sum(weights[f] * normalized[f] for f in DIRECTION)
    result["rank"] = result.suitability_score.rank(ascending=False, method="min").astype(int)
    result = result.sort_values("suitability_score", ascending=False)
    result["classification"] = pd.cut(
        result.suitability_score,
        bins=[-1, 0.30, 0.45, 0.60, 0.75, 2],
        labels=["Poor", "Below Average", "Moderate", "Good", "Excellent"]
    )
    return result

def ask_ollama(prompt, model):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.loads(response.read().decode())["message"]["content"]

# ───────────────────────── HEADER ─────────────────────────────────────
st.title("🗺️ Geospatial Analysis for Retail Site Selection")
st.caption("GIS-Based Multi-Criteria Decision Analysis (MCDA) using Weighted Sum Model | Bengaluru, Karnataka")

# ───────────────────────── SIDEBAR ────────────────────────────────────
with st.sidebar:
    st.header("⚖️ MCDA Criteria Weights")
    st.caption("Adjust the relative importance of each geospatial criterion. Weights are auto-normalized to sum to 1.0.")
    
    raw = {}
    for key, meta in CRITERIA.items():
        raw[key] = st.slider(meta["label"], 0, 100, meta["default_weight"])
    
    total = sum(raw.values()) or 1
    weights = {k: v / total for k, v in raw.items()}
    st.caption(f"Raw total: {total} → Normalized to 1.0")

    st.divider()
    st.header("➕ Custom Site Evaluation")
    with st.expander("Enter a new site to evaluate"):
        custom_name = st.text_input("Site Name", "My Custom Site")
        col_lat, col_lon = st.columns(2)
        custom_lat = col_lat.number_input("Latitude", 12.0, 14.0, 12.9716, format="%.4f")
        custom_lon = col_lon.number_input("Longitude", 77.0, 78.0, 77.5946, format="%.4f")
        custom_footfall = st.slider("Footfall Score", 0.0, 15.0, 5.0)
        col_cd, col_cc = st.columns(2)
        custom_comp_dist = col_cd.number_input("Nearest Competitor (m)", 0, 5000, 500)
        custom_comp_count = col_cc.number_input("Competitors in 1km", 0, 20, 2)
        custom_pop_density = st.number_input("Population Density", 1000, 50000, 15000)
        custom_literacy = st.slider("Literacy Rate", 0.50, 1.00, 0.85)
        col_ts, col_md = st.columns(2)
        custom_transit = col_ts.number_input("Transit Stops (500m)", 0, 10, 2)
        custom_metro_dist = col_md.number_input("Nearest Metro (m)", 0, 20000, 1000)
        custom_road_access = st.slider("Road Access Score", 0.0, 1.0, 0.80)

        if st.button("Add Site to Analysis", type="primary"):
            new_site = pd.DataFrame([{
                "site_id": "CUSTOM", "name": custom_name, "zone": "Custom",
                "lat": custom_lat, "lon": custom_lon, "area_sqft": 1000,
                "nearest_comp_m": custom_comp_dist, "comp_count_1km": custom_comp_count,
                "poi_footfall": custom_footfall, "transit_count_500m": custom_transit,
                "nearest_transit_m": 100, "nearest_metro_m": custom_metro_dist,
                "pop_density": custom_pop_density, "literacy_rate": custom_literacy,
                "working_pct": 0.5, "households_zone": 100000,
                "road_access_score": custom_road_access
            }])
            st.session_state["custom_site"] = new_site
            st.success(f"'{custom_name}' added!")

        if "custom_site" in st.session_state:
            st.info(f"Active custom site: **{st.session_state['custom_site'].iloc[0]['name']}**")
            if st.button("Remove Custom Site"):
                del st.session_state["custom_site"]
                st.rerun()

# ───────────────────── SCORING ────────────────────────────────────────
current_features = features.copy()
if "custom_site" in st.session_state:
    current_features = pd.concat([current_features, st.session_state["custom_site"]], ignore_index=True)

scored = score_sites(current_features, weights)
vehicles = float(recent.loc[recent.metric == "Total vehicles registered in Bengaluru", "value"].iloc[0])
new_vehicles = float(recent.loc[recent.metric == "New vehicles added during FY2025-26", "value"].iloc[0])
metro_peak = float(recent.loc[recent.metric == "Namma Metro peak daily ridership record", "value"].iloc[0])

# ───────────────────── TABS ───────────────────────────────────────────
tabs = st.tabs([
    "🗺️ Suitability Map",
    "📋 Site Rankings",
    "⚖️ Compare Sites",
    "📉 Sensitivity Analysis",
    "💼 Business Planner",
    "🤖 AI Advisor",
    "📊 Census & Indicators",
    "📖 Methodology"
])

# ═══════════════════════ TAB 0: MAP ═══════════════════════════════════
with tabs[0]:
    st.subheader("Interactive Geospatial Suitability Map")
    st.caption("Candidate sites are color-coded by suitability classification. Toggle geospatial layers below.")

    col_toggle1, col_toggle2, col_toggle3 = st.columns(3)
    show_competitors = col_toggle1.checkbox("🏪 Show Competitors", value=True)
    show_transit = col_toggle2.checkbox("🚇 Show Transit Stops", value=True)
    show_pois = col_toggle3.checkbox("📍 Show Points of Interest", value=False)

    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="OpenStreetMap")

    # Candidate sites (primary layer)
    for _, r in scored.iterrows():
        color = (
            "#1a9641" if r.suitability_score >= 0.75 else
            "#74c476" if r.suitability_score >= 0.60 else
            "#f6d44a" if r.suitability_score >= 0.45 else
            "#f47d00" if r.suitability_score >= 0.30 else
            "#d73027"
        )
        folium.CircleMarker(
            [r.lat, r.lon],
            radius=12 + r.suitability_score * 22,
            color=color, fill=True, fill_color=color, fill_opacity=0.75,
            tooltip=f"#{int(r['rank'])} {r['name']} | Score: {r['suitability_score']:.3f} | {r['classification']}",
            popup=folium.Popup(
                f"<b>{r['name']}</b><br>"
                f"Rank: #{int(r['rank'])}<br>"
                f"Score: {r['suitability_score']:.3f}<br>"
                f"Class: {r['classification']}<br>"
                f"Metro: {int(r.nearest_metro_m)}m<br>"
                f"Pop Density: {int(r.pop_density):,}<br>"
                f"Footfall: {r.poi_footfall:.2f}",
                max_width=250
            )
        ).add_to(m)

    # Competitor layer
    if show_competitors:
        for _, c in competitors.iterrows():
            folium.CircleMarker(
                [c.lat, c.lon], radius=5, color="#e31a1c", fill=True,
                fill_color="#e31a1c", fill_opacity=0.6,
                tooltip=f"🏪 {c['name']} ({c['chain']}) — {c['type']}"
            ).add_to(m)

    # Transit layer
    if show_transit:
        for _, t in transit.iterrows():
            icon_color = "purple" if t.type == "Metro" else "blue"
            folium.CircleMarker(
                [t.lat, t.lon], radius=4, color=icon_color, fill=True,
                fill_color=icon_color, fill_opacity=0.5,
                tooltip=f"🚇 {t['name']} ({t['type']}{' — ' + str(t['line']) if pd.notna(t.get('line')) else ''})"
            ).add_to(m)

    # POI layer
    if show_pois:
        for _, p in pois.iterrows():
            folium.CircleMarker(
                [p.lat, p.lon], radius=3, color="#ff7f00", fill=True,
                fill_color="#ff7f00", fill_opacity=0.4,
                tooltip=f"📍 {p['name']} ({p['category']}) — Footfall Wt: {p['footfall_weight']}"
            ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; background:white; padding:12px 16px;
         border-radius:8px; border:1px solid #ccc; z-index:1000; font-size:13px; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
    <b>Suitability Classification</b><br>
    <span style="color:#1a9641;">&#9679;</span> Excellent (&#8805;0.75)&nbsp;
    <span style="color:#74c476;">&#9679;</span> Good (0.60–0.74)&nbsp;
    <span style="color:#f6d44a;">&#9679;</span> Moderate (0.45–0.59)<br>
    <span style="color:#f47d00;">&#9679;</span> Below Average (0.30–0.44)&nbsp;
    <span style="color:#d73027;">&#9679;</span> Poor (&lt;0.30)
    """
    if show_competitors:
        legend_html += '<br><span style="color:#e31a1c;">&#9679;</span> Competitor'
    if show_transit:
        legend_html += '&nbsp;<span style="color:purple;">&#9679;</span> Metro&nbsp;<span style="color:blue;">&#9679;</span> Bus'
    if show_pois:
        legend_html += '&nbsp;<span style="color:#ff7f00;">&#9679;</span> POI'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, use_container_width=True, height=600)

# ═══════════════════════ TAB 1: RANKINGS ══════════════════════════════
with tabs[1]:
    st.subheader("📋 Suitability Rankings")
    st.caption("Sites ranked by composite WSM score. Classification thresholds: Excellent >= 0.75, Good >= 0.60, Moderate >= 0.45, Below Average >= 0.30, Poor < 0.30.")

    display_cols = ["rank", "name", "zone", "suitability_score", "classification",
                    "pop_density", "nearest_comp_m", "comp_count_1km", "transit_count_500m", "nearest_metro_m", "road_access_score"]
    st.dataframe(
        scored[display_cols],
        use_container_width=True, hide_index=True,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", format="%d"),
            "suitability_score": st.column_config.ProgressColumn("Suitability Score", min_value=0, max_value=1, format="%.3f"),
            "pop_density": st.column_config.NumberColumn("Pop. Density", format="%d"),
            "nearest_comp_m": st.column_config.NumberColumn("Competitor Dist. (m)", format="%d m"),
            "nearest_metro_m": st.column_config.NumberColumn("Metro Dist. (m)", format="%d m"),
        }
    )

    st.download_button("⬇️ Download Rankings as CSV", scored.to_csv(index=False), "site_rankings.csv", "text/csv")

    fig_bar = px.bar(
        scored, x="suitability_score", y="name", orientation="h",
        color="classification",
        color_discrete_map={"Excellent": "#1a9641", "Good": "#74c476", "Moderate": "#f6d44a",
                            "Below Average": "#f47d00", "Poor": "#d73027"},
        title="All Sites Ranked by Suitability Score",
        labels={"suitability_score": "Suitability Score (WSM)", "name": "Candidate Site"}
    )
    fig_bar.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_bar, use_container_width=True)

# ═══════════════════════ TAB 2: COMPARE ═══════════════════════════════
with tabs[2]:
    st.subheader("⚖️ Side-by-Side Site Comparison")
    st.caption("Compare normalized criterion values across selected sites using a radar chart.")

    compare_sites = st.multiselect(
        "Select sites to compare (2-5 recommended):",
        scored.name.tolist(),
        default=scored.name.tolist()[:3]
    )

    if len(compare_sites) >= 2:
        compare_df = scored[scored.name.isin(compare_sites)]
        criteria_labels = [CRITERIA[k]["label"] for k in CRITERIA]
        criteria_keys = list(CRITERIA.keys())

        fig_radar = go.Figure()
        for _, row in compare_df.iterrows():
            norm_vals = []
            for feat in criteria_keys:
                n = normalize(scored[feat], DIRECTION[feat])
                idx = scored.index[scored.name == row["name"]][0]
                norm_vals.append(n.loc[idx])
            norm_vals.append(norm_vals[0])  # close the polygon
            fig_radar.add_trace(go.Scatterpolar(
                r=norm_vals,
                theta=criteria_labels + [criteria_labels[0]],
                fill='toself', name=f"{row['name']} (#{int(row['rank'])})",
                opacity=0.6
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Normalized Criterion Values (Radar Chart)",
            showlegend=True, height=550
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Side-by-side metrics
        st.markdown("**Key Metrics Comparison:**")
        comp_display = compare_df[["name", "rank", "suitability_score", "classification",
                                   "pop_density", "nearest_metro_m", "poi_footfall"]].copy()
        comp_display.columns = ["Site", "Rank", "Score", "Class", "Pop. Density", "Metro (m)", "Footfall"]
        st.dataframe(comp_display, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least 2 sites to compare.")

# ═══════════════════════ TAB 3: SENSITIVITY ═══════════════════════════
with tabs[3]:
    st.subheader("📉 Sensitivity Analysis")
    st.caption("How stable are the rankings when individual criterion weights are perturbed by +/-0.20? "
               "Spearman rho = 1.0 means rankings are perfectly preserved; lower rho indicates more sensitivity.")

    sens = sensitivity.copy()
    sens["label"] = sens.apply(
        lambda r: f"{CRITERIA.get(r.feature, {}).get('label', r.feature)} ({r.direction} {r.delta:+.1f})", axis=1
    )

    fig_tornado = px.bar(
        sens.sort_values("spearman_rho"),
        x="spearman_rho", y="label", orientation="h",
        color="spearman_rho",
        color_continuous_scale=["#d73027", "#f6d44a", "#1a9641"],
        range_color=[0.4, 1.0],
        title="Sensitivity Tornado Chart — Spearman rho under Weight Perturbation (+/-0.20)",
        labels={"spearman_rho": "Spearman rho (Rank Stability)", "label": "Criterion Perturbation"}
    )
    fig_tornado.add_vline(x=0.90, line_dash="dash", line_color="gray",
                          annotation_text="rho = 0.90 (high stability)", annotation_position="top left")
    fig_tornado.update_layout(height=500)
    st.plotly_chart(fig_tornado, use_container_width=True)

    # Interpretation
    most_sensitive = sens.loc[sens.spearman_rho.idxmin()]
    most_stable = sens.loc[sens.spearman_rho.idxmax()]
    st.markdown(f"""
    **Interpretation:**
    - **Most sensitive criterion:** {most_sensitive.label} (rho = {most_sensitive.spearman_rho:.4f}) — changing this weight most disrupts rankings.
    - **Most stable criterion:** {most_stable.label} (rho = {most_stable.spearman_rho:.4f}) — rankings are robust to changes in this weight.
    - All perturbations with rho > 0.90 indicate that the ranking is **statistically stable**.
    """)

    st.dataframe(sens[["feature", "direction", "delta", "spearman_rho"]],
                 use_container_width=True, hide_index=True)

# ═══════════════════════ TAB 4: BUSINESS PLANNER ══════════════════════
with tabs[4]:
    st.subheader("💼 Business Opportunity Planner")
    st.caption("Combines MCDA suitability with mobility, business-fit, and rent-affordability scoring.")

    business = st.selectbox("What business are you planning?", assumptions.business.tolist())
    budget = st.number_input("Maximum startup budget (₹)", 50000, 10000000,
                             int(assumptions.loc[assumptions.business == business, "illustrative_startup_budget"].iloc[0]), 50000)
    customer = st.selectbox("Primary customer segment",
                            ["Students", "Young professionals", "Families", "Office workers", "Tourists/visitors", "Mass market"])

    x = scored.copy()
    x["recent_mobility"] = np.clip(0.55 + 0.25 * x.road_access_score + 0.20 * x.transit_count_500m.rank(pct=True), 0, 1)
    x["business_fit"] = np.clip(0.45 + 0.25 * x.poi_footfall.rank(pct=True) + 0.15 * x.pop_density.rank(pct=True) + 0.15 * x.road_access_score, 0, 1)
    x["business_fit_score"] = 0.50 * x.suitability_score + 0.25 * x.recent_mobility + 0.25 * x.business_fit
    x = x.sort_values("business_fit_score", ascending=False)

    st.success(f"**Recommended site for {business}:** {x.iloc[0]['name']} (business-fit score: {x.iloc[0].business_fit_score:.3f})")
    st.dataframe(
        x[["name", "zone", "business_fit_score", "suitability_score",
           "nearest_metro_m", "poi_footfall", "pop_density"]].head(8),
        use_container_width=True, hide_index=True,
        column_config={
            "business_fit_score": st.column_config.ProgressColumn("Business Fit", min_value=0, max_value=1, format="%.3f"),
            "suitability_score": st.column_config.ProgressColumn("MCDA Score", min_value=0, max_value=1, format="%.3f"),
        }
    )

# ═══════════════════════ TAB 5: AI ADVISOR ════════════════════════════
with tabs[5]:
    st.subheader("🤖 AI-Assisted Site Advisory")
    st.caption("Uses a local Ollama LLM to generate strategic recommendations. This is supplementary to the core MCDA model.")
    st.info("This module requires a running Ollama server on localhost:11434. The core geospatial analysis does NOT depend on AI.")

    ai_business = st.selectbox("Business", assumptions.business.tolist(), key="ai_business")
    ai_budget = st.number_input("Budget (₹)", 50000, 10000000, 500000, 50000, key="ai_budget")
    goal = st.text_area("What do you want the AI to solve?",
                        "Find suitable locations, explain demand and competition, and give a validation plan.")
    model = st.selectbox("Ollama model", ["qwen3:8b", "llama3.2:latest"])

    if st.button("🧠 Generate AI Strategy", type="primary"):
        candidates = scored.head(8)[["name", "zone", "suitability_score", 
                                     "nearest_metro_m", "poi_footfall", "pop_density", "nearest_comp_m"]].to_dict("records")
        prompt = (
            f"Act as a retail site-selection analyst for Bengaluru. Do not invent facts. "
            f"Business={ai_business}; budget=₹{ai_budget:,}; goal={goal}. "
            f"Recent context: approximately {vehicles:,.0f} vehicles registered by 31-Mar-2026; "
            f"approximately {new_vehicles:,.0f} added in FY2025-26; "
            f"Namma Metro peak reported ridership about {metro_peak:,.0f} on 11-Aug-2025. "
            f"Candidate records are from the project's spatial dataset (GIS-MCDA ranked). "
            f"Recommend three candidates only from the supplied records, explain demand/competition/accessibility, "
            f"list risks, and give a 14-day validation plan. Candidates={json.dumps(candidates)}"
        )
        try:
            st.markdown(ask_ollama(prompt, model))
        except Exception as e:
            st.error("Ollama is not reachable. Start it and check the model with: ollama list")
            st.code("ollama serve")

# ═══════════════════════ TAB 6: CENSUS & INDICATORS ═══════════════════
with tabs[6]:
    st.subheader("📊 Census Data & Recent Indicators")

    # Recent Bengaluru indicators
    st.markdown("#### Recent Bengaluru Indicators (2025-26)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Vehicles Registered", "12.0M")
    c2.metric("Vehicles Added FY25-26", "0.79M")
    c3.metric("Metro Peak Ridership", "1.048M")
    st.dataframe(recent, use_container_width=True, hide_index=True)

    st.divider()

    # Zone-level demographics
    st.markdown("#### BBMP Zone Demographics (Census 2011)")
    fig_zone = px.bar(
        zone_pop, x="name", y="pop_density",
        color="literacy_rate", color_continuous_scale="Viridis",
        title="Population Density by BBMP Zone (colored by Literacy Rate)",
        labels={"pop_density": "Population Density (per km²)", "name": "Zone", "literacy_rate": "Literacy Rate"}
    )
    st.plotly_chart(fig_zone, use_container_width=True)
    st.dataframe(zone_pop, use_container_width=True, hide_index=True)

    st.divider()

    # Karnataka district census
    st.markdown("#### Karnataka District Census (2011)")
    fig_census = px.bar(
        census.sort_values("total_pop", ascending=False).head(15),
        x="district_name", y="total_pop",
        color="literacy_rate", color_continuous_scale="RdYlGn",
        title="Top 15 Karnataka Districts by Population",
        labels={"total_pop": "Total Population", "district_name": "District", "literacy_rate": "Literacy Rate"}
    )
    st.plotly_chart(fig_census, use_container_width=True)

    st.divider()

    st.markdown("#### Data Sources")
    st.dataframe(sources, use_container_width=True, hide_index=True)

# ═══════════════════════ TAB 7: METHODOLOGY ═══════════════════════════
with tabs[7]:
    st.subheader("📖 Methodology: GIS-Based Multi-Criteria Decision Analysis")

    st.markdown("""
    ### 1. Problem Statement
    Selecting optimal retail store locations in a metropolitan city like Bengaluru requires evaluating multiple
    spatial, demographic, and economic criteria simultaneously. This project applies **Geospatial Analysis**
    combined with **Multi-Criteria Decision Analysis (MCDA)** to systematically rank candidate sites.

    ### 2. Theoretical Foundation
    The project uses the **Weighted Sum Model (WSM)**, one of the most widely used MCDA methods in GIS-based
    site selection (Malczewski, 2004; Eastman, 1999).

    **Mathematical Formulation:**
    """)

    st.latex(r"S(i) = \sum_{j=1}^{n} w_j \cdot \hat{x}_{ij}")

    st.markdown("""
    Where:
    - **S(i)** = composite suitability score for candidate site *i*
    - **w_j** = weight assigned to criterion *j* (user-adjustable, sum of w_j = 1)
    - **x_ij** = min-max normalized value of criterion *j* for site *i*
    - **n** = 8 (number of geospatial criteria)

    ### 3. Normalization

    **Benefit criteria** (higher is better): Footfall, Population Density, Competitor Distance, Transit Stops, Literacy Rate, Road Access
    """)
    st.latex(r"\hat{x}_{ij} = \frac{x_{ij} - x_j^{min}}{x_j^{max} - x_j^{min}}")
    st.markdown("""
    **Cost criteria** (lower is better): Competitor Count, Metro Distance
    """)
    st.latex(r"\hat{x}_{ij} = \frac{x_j^{max} - x_{ij}}{x_j^{max} - x_j^{min}}")

    st.markdown("""
    ### 4. Geospatial Operations

    | Operation | Description | Parameters |
    |-----------|-------------|------------|
    | **Buffer Analysis** | Count features within a radius of each candidate site | 500m (transit), 1km (competitors) |
    | **Nearest-Neighbour Distance** | Compute distance to closest feature | Competitors, Metro stations |
    | **Inverse-Distance Weighted Footfall** | Proximity-weighted POI influence score | 40 POIs with footfall weights |
    | **Spatial Join** | Overlay zone demographics onto point locations | 7 BBMP zones |
    | **Choropleth Mapping** | Visualize scores as color-coded markers | 5-class diverging scheme |

    ### 5. Criteria & Data Sources

    | Criterion | Source | Spatial Operation |
    |-----------|--------|-------------------|
    | Footfall Index | POIs (OSM, Google Maps) — 40 locations | IDW proximity scoring |
    | Population Density | India Census 2011 — 7 BBMP zones | Spatial join |
    | Competitor Distance | Competitor stores (OSM) — 21 locations | Nearest-neighbour |
    | Competitor Count | Competitor stores — 21 locations | 1km buffer count |
    | Transit Accessibility | Metro + BMTC (BMRCL, BMTC) — 32 stops | 500m buffer count |
    | Metro Distance | Namma Metro — 19 stations | Nearest-neighbour |
    | Literacy Rate | India Census 2011 | Spatial join |
    | Road Access Score | Road network analysis | Normalized connectivity |

    ### 6. Classification Scheme

    | Score Range | Classification | Interpretation |
    |-------------|---------------|----------------|
    | 0.75 - 1.00 | **Excellent** | Highly suitable — strong demand drivers, accessible, limited competition |
    | 0.60 - 0.74 | **Good** | Suitable — solid fundamentals with minor trade-offs |
    | 0.45 - 0.59 | **Moderate** | Viable — requires deeper due diligence |
    | 0.30 - 0.44 | **Below Average** | Weak — significant gaps in one or more criteria |
    | < 0.30 | **Poor** | Not recommended under current criteria weights |

    ### 7. Sensitivity Analysis
    Weights are perturbed by +/-0.20 and **Spearman's rank correlation (rho)** is computed against the
    baseline ranking. This measures how robust the rankings are to changes in subjective weight assignments.

    ### 8. Limitations
    - Population density uses **Census 2011** ward-level data (latest available official spatial layer).
    - Footfall index is a proxy based on POI proximity, not actual footfall counter data.
    - Competitor data represents major organized retail chains; unorganized retail (kirana stores) is not included.
    - Road access scores are derived from network connectivity, not real-time traffic data.

    ### 9. References
    - Malczewski, J. (2004). GIS-based land-use suitability analysis: a critical overview. *Progress in Planning*, 62(1), 3-65.
    - Eastman, J.R. (1999). Multi-criteria evaluation and GIS. *Geographical Information Systems*, 1, 493-502.
    - Saaty, T.L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
    - Census of India 2011 — Registrar General and Census Commissioner.
    - BMRCL (2025). Namma Metro station data.
    - BMTC — Bengaluru Metropolitan Transport Corporation route data.
    """)
