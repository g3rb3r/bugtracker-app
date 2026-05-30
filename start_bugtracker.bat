@echo off
cd /d "%~dp0"

REM Prefer built executable (no Python install required)
if exist "dist\BugTracker\BugTracker.exe" (
  start "" "dist\BugTracker\BugTracker.exe"
  goto :eof
)
if exist "BugTracker.exe" (
  start "" "BugTracker.exe"
  goto :eof
)

REM Development: run from source
py -3 main.py 2>nul
if %errorlevel% equ 0 goto :eof

python main.py 2>nul
if %errorlevel% equ 0 goto :eof

echo.
echo Could not start Bug Tracker.
echo - To run from source: install Python 3.9+ and run: pip install -r requirements.txt
echo - To build .exe: run build.bat
pause
