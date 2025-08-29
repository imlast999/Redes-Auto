@echo off
echo 🚀 Instagram Video Dashboard
echo ========================
echo.
echo 🌐 Iniciando servidor...
python -m streamlit run app.py --server.port 8501 --server.address localhost --server.headless true --browser.gatherUsageStats false
pause