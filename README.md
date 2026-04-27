# 🎮 Bug Tracker - QA Panel

An application for managing game bug reports, created for QA teams.

## ✨ Features

### 📋 Bug Management
- **Add new bugs** using a complete form
- **Browse bugs** in three categories: All, In Progress, Completed
- **Edit existing bugs** with support for updating all fields
- **Delete bugs** with confirmation

### 📸 Screenshot Functionality
- **Attach screenshots** to reports (optional)
- **Automatically save files** in the `screenshots/` folder
- **Smart file naming**: `bug_title_1.png`, `bug_title_2.png`, etc.
- **Thumbnail previews** in the bug details window
- **Click-to-zoom screenshots** from thumbnails
- **Multiple supported formats**: PNG, JPG, JPEG, GIF, BMP

### 🎨 Responsive Interface
- **Flexible windows** that adapt to screen size
- **Intuitive design** with colorful buttons and icons
- **Scrolling support** in long forms

## 🚀 Installation and Run

### Requirements
- Python 3.6+
- PIL library (Pillow)

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
├── bugs.json            # Bug database
├── screenshots/         # Folder for screenshots
├── assets/              # App assets
└── README.md            # This file
```

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
3. **Optional**: Add screenshots by clicking **"📷 Add screenshot"**
4. Click **"💾 Save bug"**

### Browse and Edit Bugs
1. Click a bug title from the list
2. In the details window, you can:
   - **View** all report information
   - **See screenshots** as thumbnails
   - **Click a thumbnail** to enlarge a screenshot
   - **Click "✏️ Edit report"** to enable edit mode
   - **Change status** in edit mode
   - **Save changes** or **cancel editing**

### Manage Screenshots
- **Add**: Choose an image file in the form
- **Remove**: Click ❌ next to the file name
- **Preview**: Click a thumbnail in the details window
- **Auto naming**: Files are saved as `bug_title_1.png`, `bug_title_2.png`, etc.

## 🔧 Configuration

### Supported image formats
- PNG (recommended)
- JPG/JPEG
- GIF
- BMP

### Maximum thumbnail size
- Default: 80x80 pixels
- Preview: Automatically adjusted to screen size

## 🐛 Troubleshooting

### Error: "Cannot display image"
- Check whether the image file is not corrupted
- Make sure the format is supported

### Screenshots are not visible
- Check whether the `screenshots/` folder exists
- Make sure files were copied correctly

### Save error
- Check write permissions in the application folder
- Make sure `bugs.json` is not being used by another application

## 📝 Data Format

Bugs are stored in `bugs.json` using JSON format:

```json
{
  "title": "Bug title",
  "environment": "Environment information",
  "steps": "Reproduction steps",
  "expected": "Expected result",
  "actual": "Actual result",
  "severity": "Severity",
  "notes": "Notes",
  "status": "Status",
  "screenshots": ["file1.png", "file2.png"]
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
**Version**: 1.0  
**Date**: 2024

