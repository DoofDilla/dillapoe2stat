@echo off
REM Quick Start Script for KISS Overlay
REM This script launches the overlay in a separate window

echo ========================================
echo   KISS Overlay - Quick Start
echo ========================================
echo.
echo Make sure the tracker is already running!
echo (python poe_stats_refactored_v2.py)
echo.
echo Starting overlay in 3 seconds...
timeout /t 3 /nobreak >nul

REM Launch overlay
python kiss_overlay_standalone.py

echo.
echo Overlay closed.
pause
