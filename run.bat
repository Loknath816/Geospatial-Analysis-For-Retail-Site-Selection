@echo off
echo ========================================================
echo   GeoRetail AI Enterprise Platform -- Bengaluru
echo   Retail Intelligence and Location Decision System
echo ========================================================
echo.
if exist ".\.venv\Scripts\streamlit.exe" (
    echo [1/2] Using project virtual environment .venv...
    echo [2/2] Launching GeoRetail AI dashboard on http://localhost:8501 ...
    echo.
    .\.venv\Scripts\streamlit.exe run app.py
) else (
    echo [1/2] Virtual environment not found, attempting global streamlit...
    echo [2/2] Launching dashboard on http://localhost:8501 ...
    echo.
    streamlit run app.py
)
pause
