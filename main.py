import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from html import escape
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

# ====== THEME ======
# Main colors
COLORS = {
    # Main background
    'bg_primary': '#1e1e1e',      # Dark primary background
    'bg_secondary': '#252526',    # Section background
    'bg_tertiary': '#2d2d30',     # Element background
    
    # Accents
    'accent_blue': '#007acc',     # Blue accent (VS Code)
    'accent_green': '#4ec9b0',    # Green accent
    'accent_orange': '#ce9178',   # Orange accent
    'accent_red': '#f44747',      # Red accent
    
    # Text
    'text_primary': '#cccccc',    # Primary text
    'text_secondary': '#969696',  # Secondary text
    'text_muted': '#6a6a6a',      # Muted text
    
    # Borders
    'border': '#3e3e42',          # Border
    'border_hover': '#4e4e52',    # Border on hover
    
    # Status colors
    'success': '#4ec9b0',         # Success
    'warning': '#ce9178',         # Warning
    'error': '#f44747',           # Error
    'info': '#007acc',            # Info
}

# Styles for UI elements
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

BUGS_FILE = "bugs.json"
SCREENSHOTS_DIR = "screenshots"
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
REPORTS_DIR = "reports"
STATUS_MAP = {
    "W trakcie": "In Progress",
    "Zakończone": "Completed",
    "In Progress": "In Progress",
    "Completed": "Completed"
}

def normalize_status(status):
    """Converts legacy Polish statuses to English equivalents."""
    return STATUS_MAP.get(status, status or "In Progress")

# Helper functions for attachments (images + video)
def is_video_file(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def open_attachment_external(abs_path):
    """Opens file in the system default app (e.g., video player)."""
    abs_path = os.path.normpath(os.path.abspath(abs_path))
    if not os.path.isfile(abs_path):
        messagebox.showerror("Error", "File not found.")
        return
    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", abs_path], check=False)
        else:
            subprocess.run(["xdg-open", abs_path], check=False)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {e}")


def get_attachment_filename(bug_title, index, source_path):
    """Filename inside screenshots folder; keeps source extension (video/image)."""
    safe_title = "".join(c for c in bug_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_') or "attachment"
    ext = os.path.splitext(source_path)[1].lower()
    if not ext:
        ext = ".png"
    return f"{safe_title}_{index}{ext}"


def copy_screenshot_to_folder(source_path, bug_title, index):
    """Copies attachment to screenshots folder with a unique filename."""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    filename = get_attachment_filename(bug_title, index, source_path)
    destination = os.path.join(SCREENSHOTS_DIR, filename)
    
    try:
        shutil.copy2(source_path, destination)
        return filename
    except Exception as e:
        print(f"Error while copying screenshot: {e}")
        return None

def get_screenshot_path(filename):
    """Returns full path to screenshot/attachment."""
    return os.path.join(SCREENSHOTS_DIR, filename)


def safe_filename(value):
    allowed = {' ', '-', '_'}
    sanitized = "".join(c for c in value if c.isalnum() or c in allowed).strip()
    return sanitized.replace(" ", "_") or "report"

def create_thumbnail(image_path, size=(100, 100)):
    """Creates image thumbnail."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error while creating thumbnail: {e}")
        return None

def show_image_preview(image_path):
    """Shows image preview in a new window."""
    try:
        with Image.open(image_path) as img:
            # Fit image to the screen
            screen_width = root.winfo_screenwidth() - 100
            screen_height = root.winfo_screenheight() - 100
            
            # Calculate scaling ratio
            img_width, img_height = img.size
            ratio = min(screen_width / img_width, screen_height / img_height)
            
            if ratio < 1:
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            # Create preview window
            preview_window = tk.Toplevel()
            preview_window.title(f"Screenshot preview")
            preview_window.geometry(f"{img.size[0] + 20}x{img.size[1] + 40}")
            
            # Center window
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (preview_window.winfo_width() // 2)
            y = (preview_window.winfo_screenheight() // 2) - (preview_window.winfo_height() // 2)
            preview_window.geometry(f"+{x}+{y}")
            
            # Add image
            label = tk.Label(preview_window, image=photo)
            label.pack(padx=10, pady=10)
            
            # Close button
            close_button = tk.Button(preview_window, text="Close", command=preview_window.destroy,
                     bg="#f44336", fg="white", padx=10, pady=5)
            close_button.pack(pady=10)
            
            # Keep image reference
            close_button.photo = photo
            
    except Exception as e:
        print(f"Error while showing preview: {e}")
        messagebox.showerror("Error", f"Unable to display image: {e}")

def create_modern_button(parent, text, command, button_type='primary'):
    """Creates a button with modern styling."""
    colors = {
        'primary': {'bg': COLORS['accent_blue'], 'active_bg': COLORS['accent_green']},
        'success': {'bg': COLORS['success'], 'active_bg': COLORS['accent_green']},
        'danger': {'bg': COLORS['error'], 'active_bg': COLORS['accent_red']},
        'warning': {'bg': COLORS['warning'], 'active_bg': COLORS['accent_orange']},
        'secondary': {'bg': COLORS['bg_tertiary'], 'active_bg': COLORS['border_hover']}
    }
    
    btn_colors = colors.get(button_type, colors['primary'])
    
    return tk.Button(parent, text=text, command=command,
                    bg=btn_colors['bg'], fg=COLORS['text_primary'],
                    font=STYLES['font_body'], padx=STYLES['padding_medium'],
                    pady=STYLES['padding_small'], relief='flat',
                    activebackground=btn_colors['active_bg'],
                    activeforeground=COLORS['text_primary'],
                    cursor='hand2')


def is_text_input_widget(widget):
    if widget is None:
        return False
    return widget.winfo_class() in {"Entry", "TEntry", "Text", "TCombobox", "Spinbox"}

# Main window setup
root = tk.Tk()
root.title("Bug Tracker - Panel QA")
root.geometry("1000x700")
root.configure(bg=COLORS['bg_primary'])

scroll_state = {"active_canvas": None}


def register_scrollable_canvas(canvas):
    def set_active(_event=None):
        scroll_state["active_canvas"] = canvas

    canvas.bind("<Enter>", set_active, add="+")
    canvas.bind("<Button-1>", set_active, add="+")
    return set_active


def _scroll_units(delta):
    active = scroll_state.get("active_canvas")
    if active is None or not active.winfo_exists():
        return
    active.yview_scroll(delta, "units")


def _on_global_mousewheel(event):
    if event.delta:
        units = -1 if event.delta > 0 else 1
        _scroll_units(units)


def _on_global_arrow_scroll(event):
    if is_text_input_widget(event.widget):
        return
    key_to_units = {
        "Up": -1,
        "Down": 1,
        "Prior": -8,
        "Next": 8,
    }
    units = key_to_units.get(event.keysym)
    if units:
        _scroll_units(units)
        return "break"


def _select_all_in_widget(event):
    widget = event.widget
    if widget.winfo_class() in {"Entry", "TEntry"}:
        widget.select_range(0, tk.END)
        widget.icursor(tk.END)
    elif widget.winfo_class() == "Text":
        widget.tag_add("sel", "1.0", "end-1c")
        widget.mark_set("insert", "end-1c")
    return "break"


def _move_entry_by_word(event, direction, select=False):
    widget = event.widget
    text = widget.get()
    cursor = widget.index(tk.INSERT)

    if direction < 0:
        new_pos = cursor
        while new_pos > 0 and text[new_pos - 1].isspace():
            new_pos -= 1
        while new_pos > 0 and not text[new_pos - 1].isspace():
            new_pos -= 1
    else:
        new_pos = cursor
        text_len = len(text)
        while new_pos < text_len and text[new_pos].isspace():
            new_pos += 1
        while new_pos < text_len and not text[new_pos].isspace():
            new_pos += 1

    if select:
        anchor = widget.index("anchor") if widget.selection_present() else cursor
        widget.selection_range(min(anchor, new_pos), max(anchor, new_pos))
    else:
        widget.selection_clear()
    widget.icursor(new_pos)
    return "break"


def _move_text_by_word(event, direction, select=False):
    widget = event.widget
    if direction < 0:
        target = widget.index("insert -1c wordstart")
    else:
        target = widget.index("insert wordend +1c")

    if select:
        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        widget.tag_remove("sel", "1.0", tk.END)
        widget.tag_add("sel", "anchor", target)
    else:
        widget.tag_remove("sel", "1.0", tk.END)
    widget.mark_set("insert", target)
    widget.see("insert")
    return "break"


root.bind_all("<MouseWheel>", _on_global_mousewheel, add="+")
root.bind_all("<Button-4>", lambda _e: _scroll_units(-1), add="+")
root.bind_all("<Button-5>", lambda _e: _scroll_units(1), add="+")
for _key in ("<Up>", "<Down>", "<Prior>", "<Next>"):
    root.bind_all(_key, _on_global_arrow_scroll, add="+")
for _class_name in ("Entry", "TEntry", "Text"):
    root.bind_class(_class_name, "<Control-a>", _select_all_in_widget, add="+")
    root.bind_class(_class_name, "<Control-A>", _select_all_in_widget, add="+")
for _class_name in ("Entry", "TEntry"):
    root.bind_class(_class_name, "<Control-Left>", lambda e: _move_entry_by_word(e, -1), add="+")
    root.bind_class(_class_name, "<Control-Right>", lambda e: _move_entry_by_word(e, 1), add="+")
    root.bind_class(_class_name, "<Control-Shift-Left>", lambda e: _move_entry_by_word(e, -1, select=True), add="+")
    root.bind_class(_class_name, "<Control-Shift-Right>", lambda e: _move_entry_by_word(e, 1, select=True), add="+")
root.bind_class("Text", "<Control-Left>", lambda e: _move_text_by_word(e, -1), add="+")
root.bind_class("Text", "<Control-Right>", lambda e: _move_text_by_word(e, 1), add="+")
root.bind_class("Text", "<Control-Shift-Left>", lambda e: _move_text_by_word(e, -1, select=True), add="+")
root.bind_class("Text", "<Control-Shift-Right>", lambda e: _move_text_by_word(e, 1, select=True), add="+")

# Set minimum window size
root.minsize(800, 600)

# ====== Header ======
header_frame = tk.Frame(root, bg=COLORS['bg_primary'])
header_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

header = tk.Label(header_frame, text="🐛 Bug Tracker", font=STYLES['font_heading'], 
                 bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
header.pack(side='left')

subtitle = tk.Label(header_frame, text="QA Panel - Bug Management", font=STYLES['font_body'], 
                   bg=COLORS['bg_primary'], fg=COLORS['text_secondary'])
subtitle.pack(side='left', padx=(STYLES['padding_medium'], 0), pady=(5, 0))

# ====== Game title filter ======
game_filter_var = tk.StringVar(value=GAME_FILTER_ALL)
filter_bar = tk.Frame(root, bg=COLORS['bg_primary'])
filter_bar.pack(fill='x', padx=STYLES['padding_large'], pady=(0, STYLES['padding_small']))

tk.Label(filter_bar, text="Filter by game:", font=STYLES['font_body'],
         bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, STYLES['padding_small']))

game_filter_combo = ttk.Combobox(filter_bar, textvariable=game_filter_var, state='readonly', width=48)
game_filter_combo.pack(side='left', fill='x', expand=True)

# ====== Tabs (status filters) ======
notebook_frame = tk.Frame(root, bg=COLORS['bg_primary'])
notebook_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_small'])

# Tab style setup
style = ttk.Style()
style.theme_use('clam')  # Clam theme for better styling control

# Tab style
style.configure('Custom.TNotebook', background=COLORS['bg_primary'], borderwidth=0)
style.configure('Custom.TNotebook.Tab', 
                background=COLORS['bg_secondary'],
                foreground=COLORS['text_secondary'],
                padding=[STYLES['padding_medium'], STYLES['padding_small']],
                borderwidth=0)
style.map('Custom.TNotebook.Tab',
          background=[('selected', COLORS['accent_blue']), ('active', COLORS['bg_tertiary'])],
          foreground=[('selected', COLORS['text_primary']), ('active', COLORS['text_primary'])])

style.configure('GameFilter.TCombobox',
                fieldbackground=COLORS['bg_tertiary'],
                background=COLORS['bg_secondary'],
                foreground=COLORS['text_primary'],
                arrowcolor=COLORS['text_primary'])
style.map('GameFilter.TCombobox',
          fieldbackground=[('readonly', COLORS['bg_tertiary'])],
          selectbackground=[('readonly', COLORS['accent_blue'])],
          selectforeground=[('readonly', COLORS['text_primary'])])

game_filter_combo.configure(style='GameFilter.TCombobox')

notebook = ttk.Notebook(notebook_frame, style='Custom.TNotebook')
notebook.pack(expand=1, fill='both')

# Create three tabs
tab_all = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_in_progress = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_done = tk.Frame(notebook, bg=COLORS['bg_secondary'])

notebook.add(tab_all, text="📋 All")
notebook.add(tab_in_progress, text="🛠️ In Progress")
notebook.add(tab_done, text="✅ Completed")


def create_scrollable_tab(parent_tab):
    """Creates a vertically scrollable content area inside a notebook tab."""
    canvas = tk.Canvas(parent_tab, bg=COLORS['bg_secondary'], highlightthickness=0)
    scrollbar = tk.Scrollbar(parent_tab, orient="vertical", command=canvas.yview)
    content_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'])

    def on_content_configure(_event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    content_frame.bind("<Configure>", on_content_configure)
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", on_canvas_configure)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    set_active = register_scrollable_canvas(canvas)
    content_frame.bind("<Enter>", set_active, add="+")
    return content_frame


tab_all_content = create_scrollable_tab(tab_all)
tab_in_progress_content = create_scrollable_tab(tab_in_progress)
tab_done_content = create_scrollable_tab(tab_done)

# ====== Bug list view ======
def show_bug_details(bug):
    detail_window = tk.Toplevel(root)
    detail_window.title(f"Details - {bug['title']}")
    detail_window.geometry("700x800")
    detail_window.configure(bg=COLORS['bg_primary'])

    # Create scrollable canvas
    canvas = tk.Canvas(detail_window, bg=COLORS['bg_primary'], highlightthickness=0)
    scrollbar = tk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_primary'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    set_active = register_scrollable_canvas(canvas)
    scrollable_frame.bind("<Enter>", set_active, add="+")

    # Keep canvas content stretched to full width
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind('<Configure>', configure_canvas)

    # === Read-only information ===
    read_only_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    read_only_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

    tk.Label(read_only_frame, text="Bug title:", font=STYLES['font_subheading'],
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
    title_entry = tk.Entry(
        read_only_frame,
        bg=COLORS['bg_tertiary'],
        fg=COLORS['text_primary'],
        readonlybackground=COLORS['bg_tertiary'],
        disabledbackground=COLORS['bg_tertiary'],
        disabledforeground=COLORS['text_primary'],
        insertbackground=COLORS['text_primary'],
        relief='flat',
        highlightthickness=1,
        highlightbackground=COLORS['border'],
        highlightcolor=COLORS['accent_blue'],
        font=STYLES['font_body'],
    )
    title_entry.insert(0, bug['title'])
    title_entry.config(state='readonly')
    title_entry.pack(fill='x', pady=(STYLES['padding_small'], STYLES['padding_medium']))
    _game_title = (bug.get('game_title') or '').strip()
    tk.Label(read_only_frame, text=f"Game title: {_game_title or '—'}", font=STYLES['font_body'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(anchor='w', fill='x')
    tk.Label(read_only_frame, text=f"Severity: {bug['severity']}", font=STYLES['font_body'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(anchor='w', fill='x')
    
    env_label = tk.Label(read_only_frame, text=f"Environment:\n{bug['environment']}", 
                        font=STYLES['font_body'], justify='left', anchor='w',
                        bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
    env_label.pack(anchor='w', fill='x', pady=(STYLES['padding_small'], 0))

    # === Editable fields (disabled by default) ===
    editable_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    editable_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

    # Steps to reproduce
    tk.Label(editable_frame, text="Steps to reproduce:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', pady=(STYLES['padding_medium'], STYLES['padding_small']), fill='x')
    steps_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled',
                        bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'], 
                        insertbackground=COLORS['text_primary'], relief='flat',
                        font=STYLES['font_body'])
    steps_text.pack(fill='x', pady=(0, STYLES['padding_medium']))
    steps_text.config(state='normal')
    steps_text.insert(tk.END, bug['steps'])
    steps_text.config(state='disabled')

    # Expected result
    tk.Label(editable_frame, text="Expected result:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', pady=(STYLES['padding_medium'], STYLES['padding_small']), fill='x')
    expected_text = tk.Text(editable_frame, height=4, wrap='word', state='disabled',
                           bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'], 
                           insertbackground=COLORS['text_primary'], relief='flat',
                           font=STYLES['font_body'])
    expected_text.pack(fill='x', pady=(0, STYLES['padding_medium']))
    expected_text.config(state='normal')
    expected_text.insert(tk.END, bug['expected'])
    expected_text.config(state='disabled')

    # Actual result
    tk.Label(editable_frame, text="Actual result:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', pady=(STYLES['padding_medium'], STYLES['padding_small']), fill='x')
    actual_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled',
                         bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'], 
                         insertbackground=COLORS['text_primary'], relief='flat',
                         font=STYLES['font_body'])
    actual_text.pack(fill='x', pady=(0, STYLES['padding_medium']))
    actual_text.config(state='normal')
    actual_text.insert(tk.END, bug['actual'])
    actual_text.config(state='disabled')

    # Notes
    tk.Label(editable_frame, text="Notes / Additional info:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', pady=(STYLES['padding_medium'], STYLES['padding_small']), fill='x')
    notes_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled',
                        bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'], 
                        insertbackground=COLORS['text_primary'], relief='flat',
                        font=STYLES['font_body'])
    notes_text.pack(fill='x', pady=(0, STYLES['padding_medium']))
    notes_text.config(state='normal')
    notes_text.insert(tk.END, bug['notes'])
    notes_text.config(state='disabled')

    # === Screenshots and video ===
    if 'screenshots' in bug and bug['screenshots']:
        screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
        screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
        
        tk.Label(screenshots_frame, text="Screenshots & video:", font=STYLES['font_subheading'],
                bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
        
        # Thumbnail/media container
        thumbnails_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
        thumbnails_frame.pack(fill='x', pady=STYLES['padding_small'])
        
        for i, screenshot_filename in enumerate(bug['screenshots']):
            screenshot_path = get_screenshot_path(screenshot_filename)
            if os.path.exists(screenshot_path):
                thumb_container = tk.Frame(thumbnails_frame, relief="solid", bd=1,
                                             bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
                thumb_container.pack(side='left', padx=5, pady=5)

                if is_video_file(screenshot_path):
                    tk.Label(thumb_container, text="🎬", font=('Segoe UI', 28),
                             bg=COLORS['bg_tertiary'], fg=COLORS['text_primary']).pack(padx=5, pady=(5, 0))
                    short_name = screenshot_filename
                    if len(short_name) > 18:
                        short_name = short_name[:15] + "…"
                    tk.Label(thumb_container, text=short_name, font=STYLES['font_small'],
                             fg=COLORS['text_muted'], bg=COLORS['bg_tertiary'], wraplength=90).pack()
                    play_btn = tk.Button(thumb_container, text="Play", cursor="hand2",
                                         bg=COLORS['accent_blue'], fg=COLORS['text_primary'],
                                         font=STYLES['font_small'], relief='flat',
                                         command=lambda p=screenshot_path: open_attachment_external(p))
                    play_btn.pack(padx=4, pady=4)
                    tk.Label(thumb_container, text=f"#{i+1}", font=STYLES['font_small'],
                             fg=COLORS['text_muted'], bg=COLORS['bg_tertiary']).pack()
                else:
                    thumbnail = create_thumbnail(screenshot_path, (80, 80))
                    if thumbnail:
                        thumb_label = tk.Label(thumb_container, image=thumbnail, cursor="hand2",
                                               bg=COLORS['bg_tertiary'])
                        thumb_label.image = thumbnail
                        thumb_label.pack(padx=5, pady=5)
                        thumb_label.bind("<Button-1>", lambda e, path=screenshot_path: show_image_preview(path))
                        tk.Label(thumb_container, text=f"#{i+1}", font=STYLES['font_small'],
                                 fg=COLORS['text_muted'], bg=COLORS['bg_tertiary']).pack()
                    else:
                        tk.Label(thumb_container, text="📎", font=('Segoe UI', 24),
                                 bg=COLORS['bg_tertiary'], fg=COLORS['text_secondary']).pack(padx=5, pady=5)
                        tk.Button(thumb_container, text="Open", cursor="hand2",
                                  bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                                  font=STYLES['font_small'], relief='flat',
                                  command=lambda p=screenshot_path: open_attachment_external(p)).pack(padx=4, pady=4)
                        tk.Label(thumb_container, text=f"#{i+1}", font=STYLES['font_small'],
                                 fg=COLORS['text_muted'], bg=COLORS['bg_tertiary']).pack()
            else:
                # If attachment is missing, show warning
                tk.Label(thumbnails_frame, text=f"Missing file: {screenshot_filename}", 
                        fg=COLORS['error'], bg=COLORS['bg_primary'], 
                        font=STYLES['font_body']).pack(side='left', padx=5, pady=5)

    # === Attachment edit section (edit mode only) ===
    edit_screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    edit_screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    # Attachment edit section header
    edit_screenshots_header = tk.Label(edit_screenshots_frame, text="Add screenshots or video:",
                                      font=STYLES['font_subheading'], anchor='w',
                                      bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
    edit_screenshots_header.pack(anchor='w', fill='x')
    
    # Selected new attachments
    new_screenshots = []
    edit_screenshots_list_frame = tk.Frame(edit_screenshots_frame, bg=COLORS['bg_primary'])
    edit_screenshots_list_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    def add_new_screenshot():
        file_path = filedialog.askopenfilename(
            title="Choose image or video",
            filetypes=MEDIA_FILE_TYPES,
        )
        if file_path:
            new_screenshots.append(file_path)
            update_edit_screenshots_display()
    
    def remove_new_screenshot(index):
        if 0 <= index < len(new_screenshots):
            new_screenshots.pop(index)
            update_edit_screenshots_display()
    
    def update_edit_screenshots_display():
        # Clear list
        for widget in edit_screenshots_list_frame.winfo_children():
            widget.destroy()
        
        # Show selected new attachments
        for i, screenshot_path in enumerate(new_screenshots):
            screenshot_frame = tk.Frame(edit_screenshots_list_frame, relief="solid", bd=1,
                                      bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
            screenshot_frame.pack(fill='x', pady=2)
            
            # File name
            filename = os.path.basename(screenshot_path)
            icon = "🎬" if is_video_file(screenshot_path) else "📷"
            tk.Label(screenshot_frame, text=f"{icon} {filename}", anchor='w',
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Remove button
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_new_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
        
        # Update counter label
        if new_screenshots:
            new_screenshots_label.config(text=f"New: {len(new_screenshots)} file(s)")
        else:
            new_screenshots_label.config(text="")
    
    # Buttons for managing new attachments
    edit_screenshots_buttons_frame = tk.Frame(edit_screenshots_frame, bg=COLORS['bg_primary'])
    edit_screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    edit_add_screenshot_btn = create_modern_button(
        edit_screenshots_buttons_frame, "📎 Add media", add_new_screenshot, 'warning')
    edit_add_screenshot_btn.pack(side='left', padx=(0, STYLES['padding_medium']))
    
    # Label showing number of new attachments
    new_screenshots_label = tk.Label(edit_screenshots_buttons_frame, text="", fg=COLORS['accent_blue'],
                                   bg=COLORS['bg_primary'], font=STYLES['font_body'])
    new_screenshots_label.pack(side='left', padx=(STYLES['padding_medium'], 0))

    # Hide attachment edit section initially
    edit_screenshots_header.pack_forget()
    edit_screenshots_buttons_frame.pack_forget()
    edit_screenshots_list_frame.pack_forget()

    # === Status change ===
    status_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    status_frame.pack(pady=STYLES['padding_medium'], fill='x', padx=STYLES['padding_large'])

    tk.Label(status_frame, text="Status:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(side='left', padx=(0, STYLES['padding_medium']))
    status_var = tk.StringVar(value=normalize_status(bug['status']))
    status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["In Progress", "Completed"], state="disabled")
    status_dropdown.pack(side='left')

    # === Action buttons ===
    buttons_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    buttons_frame.pack(pady=STYLES['padding_medium'], fill='x', padx=STYLES['padding_large'])
    
    # Centering container for buttons
    buttons_center_frame = tk.Frame(buttons_frame, bg=COLORS['bg_primary'])
    buttons_center_frame.pack(expand=True)

    edit_mode = False

    def toggle_edit_mode():
        nonlocal edit_mode
        if not edit_mode:
            # Enable edit mode
            title_entry.config(state='normal')
            steps_text.config(state='normal')
            expected_text.config(state='normal')
            actual_text.config(state='normal')
            notes_text.config(state='normal')
            status_dropdown.config(state="readonly")
            edit_button.config(text="Cancel edit")
            edit_button.configure(bg=COLORS['error'], fg=COLORS['text_primary'])
            edit_mode = True
            # Show attachment edit section
            edit_screenshots_header.pack(fill='x')
            edit_screenshots_buttons_frame.pack(fill='x')
            edit_screenshots_list_frame.pack(fill='x')
            # Show save button
            save_button.pack(side='left', padx=STYLES['padding_small'])
        else:
            # Disable edit mode
            title_entry.config(state='normal')
            title_entry.delete(0, tk.END)
            title_entry.insert(0, bug['title'])
            title_entry.config(state='readonly')
            steps_text.config(state='disabled')
            expected_text.config(state='disabled')
            actual_text.config(state='disabled')
            notes_text.config(state='disabled')
            status_dropdown.config(state="disabled")
            edit_button.config(text="Edit report")
            edit_button.configure(bg=COLORS['accent_blue'], fg=COLORS['text_primary'])
            edit_mode = False
            # Hide attachment edit section
            edit_screenshots_header.pack_forget()
            edit_screenshots_buttons_frame.pack_forget()
            edit_screenshots_list_frame.pack_forget()
            # Clear new attachments
            new_screenshots.clear()
            update_edit_screenshots_display()
            # Hide save button
            save_button.pack_forget()
            # Restore original values
            steps_text.config(state='normal')
            steps_text.delete("1.0", tk.END)
            steps_text.insert(tk.END, bug['steps'])
            steps_text.config(state='disabled')
            expected_text.config(state='normal')
            expected_text.delete("1.0", tk.END)
            expected_text.insert(tk.END, bug['expected'])
            expected_text.config(state='disabled')
            actual_text.config(state='normal')
            actual_text.delete("1.0", tk.END)
            actual_text.insert(tk.END, bug['actual'])
            actual_text.config(state='disabled')
            notes_text.config(state='normal')
            notes_text.delete("1.0", tk.END)
            notes_text.insert(tk.END, bug['notes'])
            notes_text.config(state='disabled')
            # Restore original status
            status_var.set(bug['status'])

    def save_changes():
        try:
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Validation error", "Bug title cannot be empty.")
                return
            if len(new_title) < 5:
                messagebox.showerror("Validation error", "Bug title must be at least 5 characters.")
                return

            # Load all bugs
            with open(BUGS_FILE, "r", encoding="utf-8") as f:
                bugs = json.load(f)
                for b in bugs:
                    b['status'] = normalize_status(b.get('status'))
            # Find and update selected bug
            matched_bug = None
            for b in bugs:
                if (b['title'] == bug['title'] and b['environment'] == bug['environment']
                        and b.get('game_title', '') == bug.get('game_title', '')):
                    matched_bug = b
                    b['title'] = new_title
                    b['status'] = status_var.get()
                    b['steps'] = steps_text.get("1.0", tk.END).strip()
                    b['expected'] = expected_text.get("1.0", tk.END).strip()
                    b['actual'] = actual_text.get("1.0", tk.END).strip()
                    b['notes'] = notes_text.get("1.0", tk.END).strip()
                    if new_screenshots:
                        existing_count = len(b.get('screenshots', []))
                        for i, screenshot_path in enumerate(new_screenshots):
                            filename = copy_screenshot_to_folder(
                                screenshot_path, new_title, existing_count + i + 1)
                            if filename:
                                if 'screenshots' not in b:
                                    b['screenshots'] = []
                                b['screenshots'].append(filename)
                    break

            if matched_bug is None:
                messagebox.showerror("Error", "Report not found in data file.")
                return

            # Save file again
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            bug['title'] = new_title
            bug['status'] = matched_bug['status']
            bug['steps'] = matched_bug['steps']
            bug['expected'] = matched_bug['expected']
            bug['actual'] = matched_bug['actual']
            bug['notes'] = matched_bug['notes']
            if new_screenshots:
                bug['screenshots'] = matched_bug['screenshots']

            detail_window.title(f"Details - {bug['title']}")
            print(f"Changes saved: {bug['title']}")
            if new_screenshots:
                print(f"Added {len(new_screenshots)} new attachment(s)")
            # Return to read mode without closing window
            toggle_edit_mode()
            load_bugs()  # refresh bug list in the main window
        except Exception as e:
            print("Error while saving changes:", e)

    # Save button (hidden initially)
    save_button = create_modern_button(buttons_center_frame, "Save changes", save_changes, 'success')

    # Edit button
    edit_button = create_modern_button(buttons_center_frame, "Edit report", toggle_edit_mode, 'primary')
    edit_button.pack(side='left', padx=STYLES['padding_small'])

    # === Close button ===
    close_btn = create_modern_button(buttons_center_frame, "Close view", detail_window.destroy, 'secondary')
    close_btn.pack(side='left', padx=STYLES['padding_small'])

    # === Delete button ===
    def delete_bug():
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this bug?"):
            try:
                with open(BUGS_FILE, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
                    for b in bugs:
                        b['status'] = normalize_status(b.get('status'))

                # Delete bug by title, environment, and game title
                bugs = [b for b in bugs if not (
                    b['title'] == bug['title'] and b['environment'] == bug['environment']
                    and b.get('game_title', '') == bug.get('game_title', '')
                )]

                with open(BUGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(bugs, f, indent=2, ensure_ascii=False)

                print(f"Deleted bug: {bug['title']}")
                detail_window.destroy()
                load_bugs()

            except Exception as e:
                print("Error while deleting bug:", e)

    delete_btn = create_modern_button(buttons_center_frame, "Delete bug", delete_bug, 'error')
    delete_btn.pack(side='left', padx=STYLES['padding_small'])

def load_bugs():
    update_report_button_state()
    # Clear all tabs
    for tab in (tab_all_content, tab_in_progress_content, tab_done_content):
        for widget in tab.winfo_children():
            widget.destroy()

    def reset_game_filter_choices():
        game_filter_combo['values'] = (GAME_FILTER_ALL,)
        game_filter_var.set(GAME_FILTER_ALL)

    def apply_game_filter(all_bugs):
        titles = set()
        has_empty_title = False
        for b in all_bugs:
            gt = (b.get('game_title') or '').strip()
            if gt:
                titles.add(gt)
            else:
                has_empty_title = True
        options = [GAME_FILTER_ALL] + sorted(titles)
        if has_empty_title:
            options.append(GAME_FILTER_NO_TITLE)
        game_filter_combo['values'] = options
        sel = game_filter_var.get()
        if sel not in options:
            game_filter_var.set(GAME_FILTER_ALL)
            sel = GAME_FILTER_ALL
        if sel == GAME_FILTER_ALL:
            return all_bugs
        if sel == GAME_FILTER_NO_TITLE:
            return [b for b in all_bugs if not (b.get('game_title') or '').strip()]
        return [b for b in all_bugs if (b.get('game_title') or '').strip() == sel]

    def create_bug_card(parent, bug):
        frame = tk.Frame(parent, bg=COLORS['bg_tertiary'], relief='flat',
                         bd=STYLES['border_width'], highlightbackground=COLORS['border'],
                         highlightthickness=STYLES['border_width'])
        frame.pack(fill='x', padx=STYLES['padding_medium'], pady=STYLES['padding_small'])

        title = tk.Label(frame, text=f"{bug['title']}", font=STYLES['font_subheading'],
                         anchor='w', cursor="hand2", wraplength=600, justify='left',
                         bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        title.pack(fill='x', padx=STYLES['padding_medium'], pady=(STYLES['padding_small'], 0))
        title.bind("<Button-1>", lambda e, b=bug: show_bug_details(b))

        _gt = (bug.get('game_title') or '').strip()
        if _gt:
            game_line = tk.Label(frame, text=f"{_gt}", font=STYLES['font_small'],
                                 anchor='w', cursor="hand2", wraplength=600, justify='left',
                                 fg=COLORS['accent_green'], bg=COLORS['bg_tertiary'])
            game_line.pack(fill='x', padx=STYLES['padding_medium'], pady=(0, 0))
            game_line.bind("<Button-1>", lambda e, b=bug: show_bug_details(b))

        info = tk.Label(frame, text=f"Severity: {bug['severity']} | Status: {bug['status']}",
                        font=STYLES['font_small'], fg=COLORS['text_secondary'], anchor='w',
                        bg=COLORS['bg_tertiary'])
        info.pack(fill='x', padx=STYLES['padding_medium'], pady=(0, STYLES['padding_small']))

    if not os.path.exists(BUGS_FILE):
        reset_game_filter_choices()
        for tab in (tab_all_content, tab_in_progress_content, tab_done_content):
            no_file_label = tk.Label(tab, text="No bug file found",
                                     fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                     font=STYLES['font_body'])
            no_file_label.pack(pady=STYLES['padding_large'])
        return

    try:
        with open(BUGS_FILE, "r", encoding="utf-8") as f:
            bugs = json.load(f)
        for b in bugs:
            b['status'] = normalize_status(b.get('status'))
    except Exception as e:
        reset_game_filter_choices()
        for tab in (tab_all_content, tab_in_progress_content, tab_done_content):
            error_label = tk.Label(tab, text=f"Error while loading bugs: {e}",
                                   fg=COLORS['error'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            error_label.pack(pady=STYLES['padding_large'])
        return

    filtered = apply_game_filter(bugs)

    if not bugs:
        for tab in (tab_all_content, tab_in_progress_content, tab_done_content):
            empty_label = tk.Label(tab, text="No reported bugs",
                                   fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            empty_label.pack(pady=STYLES['padding_large'])
        return

    if not filtered:
        for tab in (tab_all_content, tab_in_progress_content, tab_done_content):
            empty_label = tk.Label(tab, text="No bugs match this game filter",
                                   fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            empty_label.pack(pady=STYLES['padding_large'])
        return

    for bug in filtered:
        create_bug_card(tab_all_content, bug)
        if bug['status'] == "In Progress":
            create_bug_card(tab_in_progress_content, bug)
        elif bug['status'] == "Completed":
            create_bug_card(tab_done_content, bug)


# ====== Add new bug button ======
def open_bug_form():
    top = tk.Toplevel(root)
    top.title("Add new bug")
    top.geometry("700x800")
    top.configure(bg=COLORS['bg_primary'])

    # Create scrollable canvas
    canvas = tk.Canvas(top, bg=COLORS['bg_primary'], highlightthickness=0)
    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_primary'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    set_active = register_scrollable_canvas(canvas)
    scrollable_frame.bind("<Enter>", set_active, add="+")

    # Keep canvas content stretched to full width
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind('<Configure>', configure_canvas)

    # Required-fields info
    info_label = tk.Label(scrollable_frame, 
                         text="* - Required fields | Fields without asterisk are optional", 
                         font=STYLES['font_small'], 
                         fg=COLORS['text_muted'], 
                         bg=COLORS['bg_primary'])
    info_label.pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0))
    
    # Minimum length info
    length_info_label = tk.Label(scrollable_frame, 
                                text="Minimum lengths: Bug title (5), Game title (2), Environment fields (2), Steps (20), Expected/Actual (15), Notes (10)", 
                                font=STYLES['font_small'], 
                                fg=COLORS['text_muted'], 
                                bg=COLORS['bg_primary'])
    length_info_label.pack(anchor='w', padx=STYLES['padding_large'], pady=(0, STYLES['padding_medium']))

    fields = {}

    def create_field(label_text, is_multiline=False):
        label = tk.Label(scrollable_frame, text=label_text, anchor='w', 
                        bg=COLORS['bg_primary'], fg=COLORS['text_primary'], 
                        font=STYLES['font_body'])
        label.pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
        if is_multiline:
            entry = tk.Text(scrollable_frame, height=5, wrap='word',
                           bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                           insertbackground=COLORS['text_primary'], relief='flat',
                           font=STYLES['font_body'])
        else:
            entry = tk.Entry(scrollable_frame, bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                           insertbackground=COLORS['text_primary'], relief='flat',
                           font=STYLES['font_body'])
        entry.pack(padx=STYLES['padding_large'], fill='x')
        return entry

    # Form fields
    fields['title'] = create_field("1. Bug title: *")
    fields['game_title'] = create_field("2. Game title: *")

    tk.Label(scrollable_frame, text="3. Environment: *", font=STYLES['font_subheading'], 
            anchor='w', bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
    fields['game_version'] = create_field("Game version: *")
    fields['platform'] = create_field("Platform: *")
    fields['device'] = create_field("Device: *")
    fields['internet'] = create_field("Internet connection: *")

    fields['steps'] = create_field("4. Steps to reproduce: *", is_multiline=True)
    fields['expected'] = create_field("5. Expected result: *", is_multiline=True)
    fields['actual'] = create_field("6. Actual result: *", is_multiline=True)

    tk.Label(scrollable_frame, text="7. Bug severity: *", anchor='w', 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary'], 
            font=STYLES['font_body']).pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
    severity_var = tk.StringVar(value="Minor")
    severity_dropdown = ttk.Combobox(scrollable_frame, textvariable=severity_var, values=[
        "Cosmetic", "Minor", "Major", "Critical"
    ], state="readonly")
    severity_dropdown.pack(padx=STYLES['padding_large'], fill='x')
    fields['severity'] = severity_var

    fields['notes'] = create_field("8. Notes / Additional info (optional):", is_multiline=True)

    # === Attachments section ===
    screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    tk.Label(screenshots_frame, text="9. Screenshots & video (optional):", font=STYLES['font_subheading'],
            anchor='w', bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(anchor='w', fill='x')
    
    # Selected attachments list
    selected_screenshots = []
    screenshots_list_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
    screenshots_list_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    def add_screenshot():
        file_path = filedialog.askopenfilename(
            title="Choose image or video",
            filetypes=MEDIA_FILE_TYPES,
        )
        if file_path:
            selected_screenshots.append(file_path)
            update_screenshots_display()
    
    def remove_screenshot(index):
        if 0 <= index < len(selected_screenshots):
            selected_screenshots.pop(index)
            update_screenshots_display()
    
    def update_screenshots_display():
        # Clear list
        for widget in screenshots_list_frame.winfo_children():
            widget.destroy()
        
        # Show selected attachments
        for i, screenshot_path in enumerate(selected_screenshots):
            screenshot_frame = tk.Frame(screenshots_list_frame, relief="solid", bd=1, 
                                      bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
            screenshot_frame.pack(fill='x', pady=2)
            
            # File name
            filename = os.path.basename(screenshot_path)
            icon = "🎬" if is_video_file(screenshot_path) else "📷"
            tk.Label(screenshot_frame, text=f"{icon} {filename}", anchor='w',
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Remove button
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
    
    # Attachment management buttons
    screenshots_buttons_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
    screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    add_screenshot_btn = create_modern_button(screenshots_buttons_frame, "📎 Add media", add_screenshot, 'warning')
    add_screenshot_btn.pack(side='left', padx=(0, STYLES['padding_medium']))
    
    if selected_screenshots:
        tk.Label(screenshots_buttons_frame, text=f"Selected: {len(selected_screenshots)} file(s)",
                fg=COLORS['text_secondary'], bg=COLORS['bg_primary'],
                font=STYLES['font_body']).pack(side='left')

    def save_bug():
        # Validate required fields
        required_fields = {
            'title': 'Bug title',
            'game_title': 'Game title',
            'game_version': 'Game version',
            'platform': 'Platform',
            'device': 'Device',
            'internet': 'Internet connection',
            'steps': 'Steps to reproduce',
            'expected': 'Expected result',
            'actual': 'Actual result'
        }
        
        # Check if required fields are filled
        missing_fields = []
        for field_key, field_name in required_fields.items():
            if field_key in ['steps', 'expected', 'actual', 'notes']:
                # For multiline text fields (Text widget)
                value = fields[field_key].get("1.0", tk.END).strip()
            else:
                # For single-line fields (Entry widget)
                value = fields[field_key].get().strip()
            
            if not value:
                missing_fields.append(field_name)
        
        # If fields are missing, show error and stop
        if missing_fields:
            error_message = "Please fill in all required fields:\n\n"
            error_message += "\n".join(f"• {field}" for field in missing_fields)
            messagebox.showerror("Validation error", error_message)
            return
        
        # Validate minimum lengths
        min_lengths = {
            'title': 5,
            'game_title': 2,
            'game_version': 2,
            'platform': 2,
            'device': 2,
            'internet': 2,
            'steps': 20,
            'expected': 15,
            'actual': 15,
            'notes': 10  # Notes minimum only if provided
        }
        
        # Check environment field lengths
        environment_fields = ['game_version', 'platform', 'device', 'internet']
        for field_key in environment_fields:
            value = fields[field_key].get().strip()
            if len(value) < 2:
                messagebox.showerror("Validation error", f"Field '{required_fields[field_key]}' must have at least 2 characters")
                return
        
        # Check if severity is selected
        if not fields['severity'].get():
            messagebox.showerror("Validation error", "Please select bug severity")
            return
        
        short_fields = []
        for field_key, min_length in min_lengths.items():
            if field_key in ['steps', 'expected', 'actual', 'notes']:
                value = fields[field_key].get("1.0", tk.END).strip()
            else:
                value = fields[field_key].get().strip()
            
            # Validate notes length only when notes are provided
            if field_key == 'notes' and not value:
                continue
                
            if len(value) < min_length:
                short_fields.append(f"{required_fields.get(field_key, field_key)} (minimum {min_length} characters)")
        
        if short_fields:
            error_message = "Some fields are too short:\n\n"
            error_message += "\n".join(f"• {field}" for field in short_fields)
            messagebox.showerror("Validation error", error_message)
            return
        
        try:
            bug_data = {
                "title": fields['title'].get().strip(),
                "game_title": fields['game_title'].get().strip(),
                "environment": (
                    f"Game version: {fields['game_version'].get().strip()}\n"
                    f"Platform: {fields['platform'].get().strip()}\n"
                    f"Device: {fields['device'].get().strip()}\n"
                    f"Internet connection: {fields['internet'].get().strip()}"
                ),
                "steps": fields['steps'].get("1.0", tk.END).strip(),
                "expected": fields['expected'].get("1.0", tk.END).strip(),
                "actual": fields['actual'].get("1.0", tk.END).strip(),
                "severity": fields['severity'].get(),
                "notes": fields['notes'].get("1.0", tk.END).strip(),
                "status": "In Progress",
                "screenshots": []
            }

            # Save attachments
            bug_title = fields['title'].get()
            for i, screenshot_path in enumerate(selected_screenshots):
                filename = copy_screenshot_to_folder(screenshot_path, bug_title, i + 1)
                if filename:
                    bug_data["screenshots"].append(filename)

            # Load existing bugs (if file exists)
            if os.path.exists(BUGS_FILE):
                with open(BUGS_FILE, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
            else:
                bugs = []

            # Add new bug
            bugs.append(bug_data)

            # Save to file
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            # Success info
            print("New bug saved:", bug_data)
            if bug_data["screenshots"]:
                print(f"📎 Saved {len(bug_data['screenshots'])} attachment(s)")

            # Close form
            load_bugs()
            top.destroy()

        except Exception as e:
            print("Error while saving bug:", e)

    # Container to center the button
    button_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    button_frame.pack(pady=STYLES['padding_large'], fill='x')
    
    button_center_frame = tk.Frame(button_frame, bg=COLORS['bg_primary'])
    button_center_frame.pack(expand=True)

    save_btn = create_modern_button(button_center_frame, "Save bug", save_bug, 'success')
    save_btn.pack()

def update_report_button_state():
    selected_game = (game_filter_var.get() or "").strip()
    if selected_game and selected_game not in {GAME_FILTER_ALL, GAME_FILTER_NO_TITLE}:
        report_btn.config(state="normal", bg=COLORS['success'])
    else:
        report_btn.config(state="disabled", bg=COLORS['bg_tertiary'])


def generate_game_report():
    selected_game = (game_filter_var.get() or "").strip()
    if not selected_game or selected_game in {GAME_FILTER_ALL, GAME_FILTER_NO_TITLE}:
        messagebox.showinfo("Report", "Choose a specific game in the filter first.")
        return

    if not os.path.exists(BUGS_FILE):
        messagebox.showerror("Report", "No bugs file found.")
        return

    try:
        with open(BUGS_FILE, "r", encoding="utf-8") as f:
            bugs = json.load(f)
        for b in bugs:
            b["status"] = normalize_status(b.get("status"))
    except Exception as e:
        messagebox.showerror("Report", f"Could not read bugs file: {e}")
        return

    game_bugs = [b for b in bugs if (b.get("game_title") or "").strip() == selected_game]
    if not game_bugs:
        messagebox.showinfo("Report", f"No bugs found for game: {selected_game}")
        return

    default_reports_dir = os.path.join(os.getcwd(), REPORTS_DIR)
    os.makedirs(default_reports_dir, exist_ok=True)
    target_dir = filedialog.askdirectory(
        title="Choose folder for generated report",
        initialdir=default_reports_dir
    )
    if not target_dir:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"bug_report_{safe_filename(selected_game)}_{timestamp}"
    report_dir = os.path.join(target_dir, report_name)
    media_dir = os.path.join(report_dir, "media")
    os.makedirs(media_dir, exist_ok=True)

    def html_text(text):
        return escape(text or "").replace("\n", "<br>")

    bug_sections = []
    total_attachments = 0
    missing_attachments = []

    for idx, bug in enumerate(game_bugs, start=1):
        media_parts = []
        for media_idx, filename in enumerate(bug.get("screenshots", []), start=1):
            source_path = get_screenshot_path(filename)
            if not os.path.exists(source_path):
                missing_attachments.append(filename)
                media_parts.append(f"<li>Missing file: {escape(filename)}</li>")
                continue

            ext = os.path.splitext(filename)[1].lower()
            copied_name = f"bug{idx}_{media_idx}_{safe_filename(os.path.splitext(filename)[0])}{ext}"
            destination_path = os.path.join(media_dir, copied_name)
            shutil.copy2(source_path, destination_path)
            total_attachments += 1
            rel_path = f"media/{escape(copied_name)}"

            if is_video_file(filename):
                media_parts.append(
                    f"<div class='media-item'><p>Video: {escape(filename)}</p>"
                    f"<video controls preload='metadata' src='{rel_path}'></video></div>"
                )
            else:
                media_parts.append(
                    f"<div class='media-item'><p>Image: {escape(filename)}</p>"
                    f"<a href='{rel_path}' target='_blank'>"
                    f"<img src='{rel_path}' alt='{escape(filename)}'></a></div>"
                )

        attachments_html = "".join(media_parts) if media_parts else "<p>No attachments.</p>"
        bug_sections.append(
            "<section class='bug-card'>"
            f"<h2>{idx}. {escape(bug.get('title', 'Untitled bug'))}</h2>"
            f"<p><strong>Status:</strong> {escape(bug.get('status', 'In Progress'))} "
            f"| <strong>Severity:</strong> {escape(bug.get('severity', 'n/a'))}</p>"
            f"<p><strong>Environment:</strong><br>{html_text(bug.get('environment', ''))}</p>"
            f"<p><strong>Steps to reproduce:</strong><br>{html_text(bug.get('steps', ''))}</p>"
            f"<p><strong>Expected:</strong><br>{html_text(bug.get('expected', ''))}</p>"
            f"<p><strong>Actual:</strong><br>{html_text(bug.get('actual', ''))}</p>"
            f"<p><strong>Notes:</strong><br>{html_text(bug.get('notes', ''))}</p>"
            f"<div><strong>Attachments:</strong>{attachments_html}</div>"
            "</section>"
        )

    html_report = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Bug Report - {escape(selected_game)}</title>"
        "<style>"
        "body{font-family:Segoe UI,Arial,sans-serif;background:#f4f6f8;color:#222;margin:0;padding:24px;}"
        ".container{max-width:1100px;margin:0 auto;}"
        ".header{background:#fff;padding:16px 20px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.1);}"
        ".bug-card{background:#fff;padding:16px 20px;border-radius:10px;margin-top:16px;"
        "box-shadow:0 1px 3px rgba(0,0,0,.1);}"
        "img{max-width:100%;max-height:300px;border:1px solid #d0d7de;border-radius:6px;}"
        "video{max-width:100%;max-height:320px;border:1px solid #d0d7de;border-radius:6px;background:#000;}"
        ".media-item{margin:10px 0;}"
        "</style></head><body><div class='container'>"
        "<div class='header'>"
        f"<h1>Bug Report: {escape(selected_game)}</h1>"
        f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        f"<p><strong>Total bugs:</strong> {len(game_bugs)} | <strong>Attachments copied:</strong> {total_attachments}</p>"
        "</div>"
        f"{''.join(bug_sections)}"
        "</div></body></html>"
    )

    index_path = os.path.join(report_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    zip_path = shutil.make_archive(report_dir, "zip", report_dir)
    info_text = (
        f"Report generated.\n\nFolder:\n{report_dir}\n\nZIP:\n{zip_path}\n\n"
        f"Bugs: {len(game_bugs)}\nAttachments copied: {total_attachments}"
    )
    if missing_attachments:
        info_text += f"\nMissing attachments: {len(missing_attachments)}"
    messagebox.showinfo("Report ready", info_text)


actions_frame = tk.Frame(root, bg=COLORS['bg_primary'])
actions_frame.pack(pady=STYLES['padding_medium'])

add_bug_btn = tk.Button(actions_frame, text="Add new bug", command=open_bug_form,
                       bg=COLORS['accent_blue'], fg=COLORS['text_primary'],
                       font=STYLES['font_body'], padx=STYLES['padding_medium'],
                       pady=STYLES['padding_small'], relief='flat',
                       activebackground=COLORS['accent_green'],
                       activeforeground=COLORS['text_primary'])
add_bug_btn.pack(side='left', padx=(0, STYLES['padding_small']))

report_btn = tk.Button(actions_frame, text="Generate game report", command=generate_game_report,
                      bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                      font=STYLES['font_body'], padx=STYLES['padding_medium'],
                      pady=STYLES['padding_small'], relief='flat',
                      activebackground=COLORS['success'],
                      activeforeground=COLORS['text_primary'])
report_btn.pack(side='left', padx=(STYLES['padding_small'], 0))

game_filter_combo.bind('<<ComboboxSelected>>', lambda _e: (load_bugs(), update_report_button_state()))

# ====== Starting up ======
load_bugs()
update_report_button_state()
root.mainloop()
