@echo off
rem Crea dist\PhotoExplorer.exe (un unico file)
cd /d "%~dp0"
".venv\Scripts\python.exe" build.py
pause
