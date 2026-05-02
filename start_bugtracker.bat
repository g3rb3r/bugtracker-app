@echo off
cd /d "%~dp0"

REM pythonw — bez okna konsoli (jak typowa aplikacja okienkowa)
py -3w main.py 2>nul
if %errorlevel% equ 0 goto :eof

pythonw main.py 2>nul
if %errorlevel% equ 0 goto :eof

REM Fallback: z konsolą, żeby bylo widac ewentualny blad
echo Nie udalo sie uruchomic przez pythonw. Proba z python.exe...
py -3 main.py 2>nul
if %errorlevel% equ 0 goto :eof

python main.py
if %errorlevel% neq 0 (
  echo.
  echo Nie znaleziono Pythona lub brakuje modulow (np. Pillow).
  echo Zainstaluj Python z python.org i: pip install Pillow
  pause
)
