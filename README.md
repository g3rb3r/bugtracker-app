# Bug Tracker - QA Panel

A desktop QA tool for tracking game bugs, attaching media evidence, and exporting shareable game reports.

## For end users (no Python required)

1. Download the **`dist/BugTracker`** folder (after someone builds it with `build.bat`), or build it yourself once (see below).
2. Double-click **`BugTracker.exe`** or **`start_bugtracker.bat`**.
3. Your bugs and attachments are stored in the **`data/`** folder next to the executable.
4. Edit **`config.json`** to change window size or the data folder location.

## Project layout

```
bugtracker-app/
├── app/                    # Application source code
│   ├── config.py           # Loads config.json and data paths
│   ├── constants.py        # Theme, severities, file types
│   ├── main.py             # Entry point
│   ├── screenshots/        # Media copy, thumbnails, preview
│   ├── utils/              # Bug file helpers, text parsing
│   └── ui/                 # Tkinter windows and forms
├── data/                   # Your bugs and attachments (not in git: screenshots/, reports/)
│   ├── bugs.json
│   ├── screenshots/
│   └── reports/
├── config.json             # User settings (paths, window size)
├── config.default.json     # Shipped defaults (copied on first run if config.json is missing)
├── main.py                 # Launcher: python main.py
├── start_bugtracker.bat    # Windows launcher
├── build.bat               # Build BugTracker.exe with PyInstaller
└── requirements.txt
```

## Developers: run from source

### Requirements
- Python 3.9+
- Pillow

```bash
pip install -r requirements.txt
python main.py
```

## Build a standalone .exe (Windows)

```bat
build.bat
```

Output: `dist\BugTracker\BugTracker.exe` — distribute the **entire `dist\BugTracker` folder** (exe + `config.json` + `data/`).

## Configuration (`config.json`)

| Key | Description |
|-----|-------------|
| `data_directory` | Folder for bugs and media (default: `data`) |
| `bugs_filename` | JSON database file name inside data folder |
| `screenshots_subdirectory` | Attachments folder inside data |
| `reports_subdirectory` | Default export folder inside data |
| `window` | Title, size, and minimum size |

Paths are relative to the folder containing `config.json` (project root when developing, exe folder when distributed).

## Features

- Add, edit, and delete bugs with media attachments
- Filter by game; status tabs: All, In Progress, Completed
- HTML + ZIP game reports for developers
- Severity levels: Cosmetic, Low, Minor, Medium, Major, High, Critical

---

**Author**: Maja Gebler  
**Version**: 2.0  
**Date**: 2026
