@echo off
cd /d "%~dp0"

REM Prefer built executable (no console, no Python required)
if exist "dist\BugTracker\BugTracker.exe" (
  start "" "dist\BugTracker\BugTracker.exe"
  goto :eof
)
if exist "BugTracker.exe" (
  start "" "BugTracker.exe"
  goto :eof
)

REM Development: run without console window (pythonw)
py -3w main.py 2>nul
if %errorlevel% equ 0 goto :eof

pythonw main.py 2>nul
if %errorlevel% equ 0 goto :eof

REM Fallback: show errors in console if pythonw is unavailable
echo pythonw not found, trying python.exe...
py -3 main.py 2>nul
if %errorlevel% equ 0 goto :eof

python main.py 2>nul
if %errorlevel% equ 0 goto :eof

echo.
echo Could not start Bug Tracker.
echo - Install Python 3.9+ and run: pip install -r requirements.txt
echo - Or build the app: build.bat  (then use dist\BugTracker\BugTracker.exe)
pause
