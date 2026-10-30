@echo off
echo ============================================
echo   Retail Site Selector — Bangalore
echo   CSS7102 Mini Project
echo ============================================
echo.
echo [1/3] Checking Python...
python --version
echo.
echo [2/3] Installing requirements...
pip install -r requirements.txt
echo.
echo [3/3] Launching dashboard on http://localhost:8501
echo.
streamlit run app.py
pause
