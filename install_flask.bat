@echo off
echo ============================================================
echo Installing Flask and Flask-CORS
echo ============================================================
echo.
echo This will install:
echo   - Flask (web framework)
echo   - Flask-CORS (cross-origin support)
echo.
echo Installation size: ~1.1 MB
echo Time: 15-40 seconds
echo.
pause

echo.
echo Installing Flask...
python -m pip install --upgrade flask

echo.
echo Installing Flask-CORS...
python -m pip install --upgrade flask-cors

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Run: python ultimate_server.py
echo   2. Open: http://localhost:5000
echo.
pause
