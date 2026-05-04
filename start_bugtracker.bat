```bat
@echo off
cd /d "%~dp0"

REM pythonw — no console window (like a typical windowed application)
py -3w main.py 2>nul
if %errorlevel% equ 0 goto :eof

pythonw main.py 2>nul
if %errorlevel% equ 0 goto :eof

REM Fallback: with console, so any error is visible
echo Failed to launch via pythonw. Trying python.exe...
py -3 main.py 2>nul
if %errorlevel% equ 0 goto :eof

python main.py
if %errorlevel% neq 0 (
  echo.
  echo Python not found or missing modules (e.g. Pillow).
  echo Install Python from python.org and run: pip install Pillow
  pause
)
```