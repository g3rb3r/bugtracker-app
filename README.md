# 🎮 Bug Tracker - QA Panel

A desktop QA tool for tracking game bugs, attaching media evidence, and exporting shareable game reports.

## ✨ Features

### 📋 Bug Management
- **Add new bugs** using a complete form
- **Browse bugs** in three categories: All, In Progress, Completed
- **Edit existing bugs** with support for updating all fields
- **Delete bugs** with confirmation

### 📎 Media Attachments
- **Attach images and video** to reports (optional)
- **Automatically save files** in the `screenshots/` folder
- **Thumbnail previews** for images in bug details
- **Open/play attachments** directly from bug details
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WEBP, MP4, WEBM, MOV, MKV, AVI, WMV, M4V, MPEG, MPG

### 🧾 Report Export
- **Generate HTML + ZIP report** for the currently selected game
- Report includes bug details and copied media files
- Developers can open `index.html` in a browser (no app install required)

### 🎨 Responsive Interface
- **Flexible windows** that adapt to screen size
- **Intuitive design** with colorful buttons and icons
- **Scrolling support** in long forms

## 🚀 Installation & Run

### Requirements
- Python 3.9+
- Pillow

### Install dependencies
```bash
pip install Pillow
```

### Run the app
```bash
python main.py
```

## 📁 Project Structure

```
bugtracker_app/
├── main.py              # Main application file
├── bugs.json            # Bug database (can contain sample records)
├── screenshots/         # Local folder for generated attachments (gitignored)
├── reports/             # Local folder for generated reports (gitignored)
├── assets/              # App assets
└── README.md            # This file
```

## 📦 Demo Data and Git Ignore

- `bugs.json` may include **sample records** so users can quickly see how bugs look.
- Generated folders `screenshots/` and `reports/` are listed in `.gitignore`.
- Files inside those folders are **local only** and will not be pushed to GitHub (unless they were tracked before).

## 💡 How to Use

### Add a New Bug
1. Click **"➕ Add new bug"**
2. Fill in all required fields:
   - Bug title
   - Environment details (game version, platform, device, connection)
   - Reproduction steps
   - Expected and actual result
   - Bug severity
   - Notes
3. **Optional**: Add attachments by clicking **"📎 Add media"**
4. Click **"💾 Save bug"**

### Browse and Edit Bugs
1. Click a bug title from the list
2. In the details window, you can:
   - **View** all report information
   - **See image thumbnails** and media items
   - **Preview images** / **play videos**
   - **Click "✏️ Edit report"** to enable edit mode
   - **Change status** in edit mode
   - **Save changes** or **cancel editing**

### Manage Attachments
- **Add**: Choose image or video in the form
- **Remove**: Click ❌ next to the file name
- **Preview/Open**: Use controls in the details window
- **Auto naming**: Files are saved with safe names and original extensions

### Generate a Game Report
1. Select a specific game in **Filter by game**
2. Click **"🧾 Generate game report"**
3. Choose output folder
4. Share generated ZIP with your developer

## 🔧 Configuration

### Stored Data
- Bugs are stored in `bugs.json`
- Generated media is stored in `screenshots/`
- Generated exports are stored in `reports/`

### Git Ignore Notes
- `screenshots/` and `reports/` are gitignored by default
- Keep only sample records in `bugs.json` for public demos

## 🐛 Troubleshooting

### Error: "Cannot display image"
- Check that the image file is valid
- Make sure the file format is supported

### Media are missing in report
- Check if source files still exist in `screenshots/`
- Regenerate report if files were moved

### Save error
- Check write permissions in the application folder
- Make sure `bugs.json` is not being used by another application

## 📝 Data Format

Bugs are stored in `bugs.json` using JSON format:

```json
{
  "title": "Bug title",
  "game_title": "Game title",
  "environment": "Environment information",
  "steps": "Reproduction steps",
  "expected": "Expected result",
  "actual": "Actual result",
  "severity": "Severity",
  "notes": "Notes",
  "status": "Status",
  "screenshots": ["file1.png", "file2.mp4"]
}
```

## 🎯 Planned Features

- [ ] Export reports to PDF
- [ ] Filter by severity
- [ ] Search within bug content
- [ ] Statistics and charts
- [ ] Integration with bug tracking systems

---

**Author**: Maja Gebler  
**Version**: 1.1  
**Date**: 2026

