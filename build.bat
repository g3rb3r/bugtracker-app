@echo off
cd /d "%~dp0"
echo Building Bug Tracker executable...
echo.

py -3 -m pip install -r requirements.txt
if %errorlevel% neq 0 (
  python -m pip install -r requirements.txt
)

py -3 -m PyInstaller --noconfirm --windowed --name BugTracker ^
  --hidden-import=PIL._tkinter_finder ^
  --collect-submodules app ^
  --add-data "config.default.json;." ^
  --add-data "app\templates;app\templates" ^
  main.py

if %errorlevel% neq 0 (
  echo Build failed.
  pause
  exit /b 1
)

if not exist "dist\BugTracker\config.json" (
  copy /Y "config.default.json" "dist\BugTracker\config.json"
)
if not exist "dist\BugTracker\data" (
  mkdir "dist\BugTracker\data"
  mkdir "dist\BugTracker\data\screenshots"
  mkdir "dist\BugTracker\data\reports"
  if exist "data\bugs.json" copy /Y "data\bugs.json" "dist\BugTracker\data\bugs.json"
)

echo.
echo Done. Run: dist\BugTracker\BugTracker.exe
echo Copy the whole dist\BugTracker folder when sharing the app.
pause
