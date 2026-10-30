# Bengaluru AI Retail Site Intelligence — Upgraded

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## New features
- Recent 2025-26 vehicle-registration indicators
- 2025 Namma Metro ridership context
- 2025 BBMP trade-license source catalog
- 2025 Bengaluru road-crash source catalog
- Business planner
- Business-fit site ranking
- Local Ollama AI advisor
- Recent-data Excel workbook: `data/recent_bengaluru_data.xlsx`

## AI
The AI advisor calls your local Ollama server at `http://localhost:11434/api/chat`.
Recommended models: `qwen3:8b` or `llama3.2:latest`.

## Important
The original spatial demographic layer remains Census-2011 based because a comparable official 2025/26 ward-level population surface was not verified.
