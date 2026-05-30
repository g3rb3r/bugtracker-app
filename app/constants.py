"""Application-wide constants (theme, enums, file types)."""

COLORS = {
    'bg_primary': '#1e1e1e',
    'bg_secondary': '#252526',
    'bg_tertiary': '#2d2d30',
    'accent_blue': '#007acc',
    'accent_green': '#4ec9b0',
    'accent_orange': '#ce9178',
    'accent_red': '#f44747',
    'text_primary': '#cccccc',
    'text_secondary': '#969696',
    'text_muted': '#6a6a6a',
    'border': '#3e3e42',
    'border_hover': '#4e4e52',
    'success': '#4ec9b0',
    'warning': '#ce9178',
    'error': '#f44747',
    'info': '#007acc',
}

STYLES = {
    'font_heading': ('Segoe UI', 16, 'bold'),
    'font_subheading': ('Segoe UI', 12, 'bold'),
    'font_body': ('Segoe UI', 10),
    'font_small': ('Segoe UI', 9),
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 15,
    'border_radius': 6,
    'border_width': 1,
}

VIDEO_EXTENSIONS = frozenset({
    ".mp4", ".webm", ".mov", ".mkv", ".avi", ".wmv", ".m4v", ".mpeg", ".mpg",
})

MEDIA_FILE_TYPES = [
    ("Images and video", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.mp4 *.webm *.mov *.mkv *.avi *.wmv *.m4v"),
    ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
    ("Video", "*.mp4 *.webm *.mov *.mkv *.avi *.wmv *.m4v *.mpeg *.mpg"),
    ("All files", "*.*"),
]

GAME_FILTER_ALL = "All games"
GAME_FILTER_NO_TITLE = "(No game title)"

STATUS_MAP = {
    "W trakcie": "In Progress",
    "Zakończone": "Completed",
    "In Progress": "In Progress",
    "Completed": "Completed",
}

SEVERITY_OPTIONS = [
    "Cosmetic", "Low", "Minor", "Medium", "Major", "High", "Critical",
]

ENV_FIELD_PREFIXES = {
    "game_version": "Game version:",
    "platform": "Platform:",
    "device": "Device:",
    "internet": "Internet connection:",
}
