@echo off
title Filtro de Productos por Clave
echo ========================================
echo   Iniciando Filtro de Productos...
echo ========================================
echo.

:: Abrir el navegador automaticamente (espera 2 segundos para dar tiempo a que streamlit inicie)
start cmd /c "timeout /t 3 >nul && start http://localhost:8501"

streamlit run app.py
pause
