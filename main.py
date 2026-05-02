import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

# ====== MOTYW ======
# Kolory główne
COLORS = {
    # Tło główne
    'bg_primary': '#1e1e1e',      # Ciemne tło główne
    'bg_secondary': '#252526',    # Tło sekcji
    'bg_tertiary': '#2d2d30',     # Tło elementów
    
    # Akcenty
    'accent_blue': '#007acc',     # Niebieski akcent (VS Code)
    'accent_green': '#4ec9b0',    # Zielony akcent
    'accent_orange': '#ce9178',   # Pomarańczowy akcent
    'accent_red': '#f44747',      # Czerwony akcent
    
    # Tekst
    'text_primary': '#cccccc',    # Główny tekst
    'text_secondary': '#969696',  # Drugorzędny tekst
    'text_muted': '#6a6a6a',      # Stłumiony tekst
    
    # Ramki i obramowania
    'border': '#3e3e42',          # Ramki
    'border_hover': '#4e4e52',    # Ramki przy hover
    
    # Status
    'success': '#4ec9b0',         # Sukces
    'warning': '#ce9178',         # Ostrzeżenie
    'error': '#f44747',           # Błąd
    'info': '#007acc',            # Informacja
}

# Style dla różnych elementów
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
STATUS_MAP = {
    "W trakcie": "In Progress",
    "Zakończone": "Completed",
    "In Progress": "In Progress",
    "Completed": "Completed"
}

def normalize_status(status):
    """Converts legacy Polish statuses to English equivalents."""
    return STATUS_MAP.get(status, status or "In Progress")

# Funkcje pomocnicze do obsługi załączników (obrazy + wideo)
def is_video_file(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def open_attachment_external(abs_path):
    """Otwiera plik w domyślnej aplikacji systemu (np. odtwarzacz wideo)."""
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
    """Nazwa pliku w folderze screenshots — zachowuje rozszerzenie źródła (wideo/obraz)."""
    safe_title = "".join(c for c in bug_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_') or "attachment"
    ext = os.path.splitext(source_path)[1].lower()
    if not ext:
        ext = ".png"
    return f"{safe_title}_{index}{ext}"


def copy_screenshot_to_folder(source_path, bug_title, index):
    """Kopiuje załącznik do folderu screenshots z unikalną nazwą."""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    filename = get_attachment_filename(bug_title, index, source_path)
    destination = os.path.join(SCREENSHOTS_DIR, filename)
    
    try:
        shutil.copy2(source_path, destination)
        return filename
    except Exception as e:
        print(f"❌ Error while copying screenshot: {e}")
        return None

def get_screenshot_path(filename):
    """Zwraca pełną ścieżkę do screenshotu"""
    return os.path.join(SCREENSHOTS_DIR, filename)

def create_thumbnail(image_path, size=(100, 100)):
    """Tworzy miniaturę obrazu"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"❌ Error while creating thumbnail: {e}")
        return None

def show_image_preview(image_path):
    """Pokazuje podgląd obrazu w nowym oknie"""
    try:
        with Image.open(image_path) as img:
            # Dostosuj rozmiar obrazu do ekranu
            screen_width = root.winfo_screenwidth() - 100
            screen_height = root.winfo_screenheight() - 100
            
            # Oblicz proporcje
            img_width, img_height = img.size
            ratio = min(screen_width / img_width, screen_height / img_height)
            
            if ratio < 1:
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            # Utwórz okno podglądu
            preview_window = tk.Toplevel()
            preview_window.title(f"Screenshot preview")
            preview_window.geometry(f"{img.size[0] + 20}x{img.size[1] + 40}")
            
            # Wyśrodkuj okno
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (preview_window.winfo_width() // 2)
            y = (preview_window.winfo_screenheight() // 2) - (preview_window.winfo_height() // 2)
            preview_window.geometry(f"+{x}+{y}")
            
            # Dodaj obraz
            label = tk.Label(preview_window, image=photo)
            label.pack(padx=10, pady=10)
            
            # Przycisk zamknięcia
            close_button = tk.Button(preview_window, text="Close", command=preview_window.destroy,
                     bg="#f44336", fg="white", padx=10, pady=5)
            close_button.pack(pady=10)
            
            # Zachowaj referencję do obrazu w przycisku
            close_button.photo = photo
            
    except Exception as e:
        print(f"❌ Error while showing preview: {e}")
        messagebox.showerror("Error", f"Unable to display image: {e}")

def create_modern_button(parent, text, command, button_type='primary'):
    """Tworzy przycisk z nowoczesnym wyglądem"""
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

# Konfiguracja głównego okna
root = tk.Tk()
root.title("Bug Tracker - Panel QA")
root.geometry("1000x700")
root.configure(bg=COLORS['bg_primary'])

# Ustaw minimalny rozmiar okna
root.minsize(800, 600)

# ====== Nagłówek ======
header_frame = tk.Frame(root, bg=COLORS['bg_primary'])
header_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

header = tk.Label(header_frame, text="🐛 Bug Tracker", font=STYLES['font_heading'], 
                 bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
header.pack(side='left')

subtitle = tk.Label(header_frame, text="QA Panel - Bug Management", font=STYLES['font_body'], 
                   bg=COLORS['bg_primary'], fg=COLORS['text_secondary'])
subtitle.pack(side='left', padx=(STYLES['padding_medium'], 0), pady=(5, 0))

# ====== Filtr po tytule gry ======
game_filter_var = tk.StringVar(value=GAME_FILTER_ALL)
filter_bar = tk.Frame(root, bg=COLORS['bg_primary'])
filter_bar.pack(fill='x', padx=STYLES['padding_large'], pady=(0, STYLES['padding_small']))

tk.Label(filter_bar, text="Filter by game:", font=STYLES['font_body'],
         bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, STYLES['padding_small']))

game_filter_combo = ttk.Combobox(filter_bar, textvariable=game_filter_var, state='readonly', width=48)
game_filter_combo.pack(side='left', fill='x', expand=True)

# ====== Zakładki (filtry statusów) ======
notebook_frame = tk.Frame(root, bg=COLORS['bg_primary'])
notebook_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_small'])

# Konfiguracja stylu zakładek
style = ttk.Style()
style.theme_use('clam')  # Motyw clam dla lepszej kontroli

# Styl dla zakładek
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

# Tworzenie trzech zakładek
tab_all = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_in_progress = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_done = tk.Frame(notebook, bg=COLORS['bg_secondary'])

notebook.add(tab_all, text="📋 All")
notebook.add(tab_in_progress, text="🛠️ In Progress")
notebook.add(tab_done, text="✅ Completed")

# ====== Placeholder: lista bugów ======
def show_bug_details(bug):
    detail_window = tk.Toplevel(root)
    detail_window.title(f"📋 Details - {bug['title']}")
    detail_window.geometry("700x800")
    detail_window.configure(bg=COLORS['bg_primary'])

    # Tworzenie canvasu z przewijaniem
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

    # Konfiguracja canvas aby rozszerzał się na całą szerokość
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind('<Configure>', configure_canvas)

    # === Informacje tylko do odczytu ===
    read_only_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    read_only_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

    tk.Label(read_only_frame, text="Bug title:", font=STYLES['font_subheading'],
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
    title_entry = tk.Entry(read_only_frame, bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                           insertbackground=COLORS['text_primary'], relief='flat',
                           font=STYLES['font_body'])
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

    # === Pola edytowalne (domyślnie tylko do odczytu) ===
    editable_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    editable_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

    # Kroki do odtworzenia
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

    # Oczekiwany rezultat
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

    # Faktyczny rezultat
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

    # Notatki
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

    # === Zrzuty ekranu ===
    if 'screenshots' in bug and bug['screenshots']:
        screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
        screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
        
        tk.Label(screenshots_frame, text="Screenshots & video:", font=STYLES['font_subheading'],
                bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
        
        # Kontener na miniatury
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
                # Jeśli plik nie istnieje, pokaż informację
                tk.Label(thumbnails_frame, text=f"❌ Missing file: {screenshot_filename}", 
                        fg=COLORS['error'], bg=COLORS['bg_primary'], 
                        font=STYLES['font_body']).pack(side='left', padx=5, pady=5)

    # === Sekcja edycji zrzutów ekranu (tylko w trybie edycji) ===
    edit_screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    edit_screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    # Nagłówek sekcji edycji zrzutów ekranu
    edit_screenshots_header = tk.Label(edit_screenshots_frame, text="Add screenshots or video:",
                                      font=STYLES['font_subheading'], anchor='w',
                                      bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
    edit_screenshots_header.pack(anchor='w', fill='x')
    
    # Lista wybranych nowych zrzutów ekranu
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
        # Wyczyść listę
        for widget in edit_screenshots_list_frame.winfo_children():
            widget.destroy()
        
        # Pokaż wybrane nowe zrzuty ekranu
        for i, screenshot_path in enumerate(new_screenshots):
            screenshot_frame = tk.Frame(edit_screenshots_list_frame, relief="solid", bd=1,
                                      bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
            screenshot_frame.pack(fill='x', pady=2)
            
            # Nazwa pliku
            filename = os.path.basename(screenshot_path)
            icon = "🎬" if is_video_file(screenshot_path) else "📷"
            tk.Label(screenshot_frame, text=f"{icon} {filename}", anchor='w',
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Przycisk usuwania
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_new_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
        
        # Aktualizuj label z liczbą zrzutów
        if new_screenshots:
            new_screenshots_label.config(text=f"New: {len(new_screenshots)} file(s)")
        else:
            new_screenshots_label.config(text="")
    
    # Przyciski do zarządzania nowymi zrzutami ekranu
    edit_screenshots_buttons_frame = tk.Frame(edit_screenshots_frame, bg=COLORS['bg_primary'])
    edit_screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    edit_add_screenshot_btn = create_modern_button(
        edit_screenshots_buttons_frame, "📎 Add media", add_new_screenshot, 'warning')
    edit_add_screenshot_btn.pack(side='left', padx=(0, STYLES['padding_medium']))
    
    # Label do wyświetlania liczby nowych zrzutów
    new_screenshots_label = tk.Label(edit_screenshots_buttons_frame, text="", fg=COLORS['accent_blue'],
                                   bg=COLORS['bg_primary'], font=STYLES['font_body'])
    new_screenshots_label.pack(side='left', padx=(STYLES['padding_medium'], 0))

    # Początkowo ukryj sekcję edycji zrzutów ekranu
    edit_screenshots_header.pack_forget()
    edit_screenshots_buttons_frame.pack_forget()
    edit_screenshots_list_frame.pack_forget()

    # === Zmiana statusu ===
    status_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    status_frame.pack(pady=STYLES['padding_medium'], fill='x', padx=STYLES['padding_large'])

    tk.Label(status_frame, text="Status:", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(side='left', padx=(0, STYLES['padding_medium']))
    status_var = tk.StringVar(value=normalize_status(bug['status']))
    status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["In Progress", "Completed"], state="disabled")
    status_dropdown.pack(side='left')

    # === Przyciski ===
    buttons_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    buttons_frame.pack(pady=STYLES['padding_medium'], fill='x', padx=STYLES['padding_large'])
    
    # Kontener do wyśrodkowania przycisków
    buttons_center_frame = tk.Frame(buttons_frame, bg=COLORS['bg_primary'])
    buttons_center_frame.pack(expand=True)

    edit_mode = False

    def toggle_edit_mode():
        nonlocal edit_mode
        if not edit_mode:
            # Włącz tryb edycji
            title_entry.config(state='normal')
            steps_text.config(state='normal')
            expected_text.config(state='normal')
            actual_text.config(state='normal')
            notes_text.config(state='normal')
            status_dropdown.config(state="readonly")
            edit_button.config(text="❌ Cancel edit")
            edit_button.configure(bg=COLORS['error'], fg=COLORS['text_primary'])
            edit_mode = True
            # Pokaż sekcję edycji zrzutów ekranu
            edit_screenshots_header.pack(fill='x')
            edit_screenshots_buttons_frame.pack(fill='x')
            edit_screenshots_list_frame.pack(fill='x')
            # Pokaż przycisk zapisu
            save_button.pack(side='left', padx=STYLES['padding_small'])
        else:
            # Wyłącz tryb edycji
            title_entry.config(state='normal')
            title_entry.delete(0, tk.END)
            title_entry.insert(0, bug['title'])
            title_entry.config(state='readonly')
            steps_text.config(state='disabled')
            expected_text.config(state='disabled')
            actual_text.config(state='disabled')
            notes_text.config(state='disabled')
            status_dropdown.config(state="disabled")
            edit_button.config(text="✏️ Edit report")
            edit_button.configure(bg=COLORS['accent_blue'], fg=COLORS['text_primary'])
            edit_mode = False
            # Ukryj sekcję edycji zrzutów ekranu
            edit_screenshots_header.pack_forget()
            edit_screenshots_buttons_frame.pack_forget()
            edit_screenshots_list_frame.pack_forget()
            # Wyczyść nowe zrzuty ekranu
            new_screenshots.clear()
            update_edit_screenshots_display()
            # Ukryj przycisk zapisu
            save_button.pack_forget()
            # Przywróć oryginalne wartości
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
            # Przywróć oryginalny status
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

            # Wczytaj wszystkie bugi
            with open(BUGS_FILE, "r", encoding="utf-8") as f:
                bugs = json.load(f)
                for b in bugs:
                    b['status'] = normalize_status(b.get('status'))
            # Znajdź i zaktualizuj
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

            # Zapisz ponownie
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

            detail_window.title(f"📋 Details - {bug['title']}")
            print(f"✅ Zapisano zmiany: {bug['title']}")
            if new_screenshots:
                print(f"📎 Added {len(new_screenshots)} new attachment(s)")
            # Po zapisaniu wróć do trybu podglądu, nie zamykaj okna
            toggle_edit_mode()
            load_bugs()  # odśwież listę bugów w głównym oknie
        except Exception as e:
            print("❌ Error while saving changes:", e)

    # Przycisk zapisu (początkowo ukryty)
    save_button = create_modern_button(buttons_center_frame, "💾 Save changes", save_changes, 'success')

    # Przycisk edycji
    edit_button = create_modern_button(buttons_center_frame, "✏️ Edit report", toggle_edit_mode, 'primary')
    edit_button.pack(side='left', padx=STYLES['padding_small'])

    # === Przycisk zamknięcia ===
    close_btn = create_modern_button(buttons_center_frame, "❌ Close view", detail_window.destroy, 'secondary')
    close_btn.pack(side='left', padx=STYLES['padding_small'])

    # === Przycisk usuwania ===
    def delete_bug():
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this bug?"):
            try:
                with open(BUGS_FILE, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
                    for b in bugs:
                        b['status'] = normalize_status(b.get('status'))

                # Usuń buga na podstawie tytułu i środowiska
                bugs = [b for b in bugs if not (
                    b['title'] == bug['title'] and b['environment'] == bug['environment']
                    and b.get('game_title', '') == bug.get('game_title', '')
                )]

                with open(BUGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(bugs, f, indent=2, ensure_ascii=False)

                print(f"🗑️ Deleted bug: {bug['title']}")
                detail_window.destroy()
                load_bugs()

            except Exception as e:
                print("❌ Error while deleting bug:", e)

    delete_btn = create_modern_button(buttons_center_frame, "🗑️ Delete bug", delete_bug, 'error')
    delete_btn.pack(side='left', padx=STYLES['padding_small'])

def load_bugs():
    # Wyczyść wszystkie zakładki
    for tab in (tab_all, tab_in_progress, tab_done):
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

        title = tk.Label(frame, text=f"🐞 {bug['title']}", font=STYLES['font_subheading'],
                         anchor='w', cursor="hand2", wraplength=600, justify='left',
                         bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'])
        title.pack(fill='x', padx=STYLES['padding_medium'], pady=(STYLES['padding_small'], 0))
        title.bind("<Button-1>", lambda e, b=bug: show_bug_details(b))

        _gt = (bug.get('game_title') or '').strip()
        if _gt:
            game_line = tk.Label(frame, text=f"🎮 {_gt}", font=STYLES['font_small'],
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
        for tab in (tab_all, tab_in_progress, tab_done):
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
        for tab in (tab_all, tab_in_progress, tab_done):
            error_label = tk.Label(tab, text=f"Error while loading bugs: {e}",
                                   fg=COLORS['error'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            error_label.pack(pady=STYLES['padding_large'])
        return

    filtered = apply_game_filter(bugs)

    if not bugs:
        for tab in (tab_all, tab_in_progress, tab_done):
            empty_label = tk.Label(tab, text="No reported bugs",
                                   fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            empty_label.pack(pady=STYLES['padding_large'])
        return

    if not filtered:
        for tab in (tab_all, tab_in_progress, tab_done):
            empty_label = tk.Label(tab, text="No bugs match this game filter",
                                   fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            empty_label.pack(pady=STYLES['padding_large'])
        return

    for bug in filtered:
        create_bug_card(tab_all, bug)
        if bug['status'] == "In Progress":
            create_bug_card(tab_in_progress, bug)
        elif bug['status'] == "Completed":
            create_bug_card(tab_done, bug)


# ====== Przycisk dodawania nowego buga ======
def open_bug_form():
    top = tk.Toplevel(root)
    top.title("Add new bug")
    top.geometry("700x800")
    top.configure(bg=COLORS['bg_primary'])

    # Tworzenie canvasu z przewijaniem
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

    # Konfiguracja canvas aby rozszerzał się na całą szerokość
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind('<Configure>', configure_canvas)

    # Informacja o wymaganych polach
    info_label = tk.Label(scrollable_frame, 
                         text="* - Required fields | Fields without asterisk are optional", 
                         font=STYLES['font_small'], 
                         fg=COLORS['text_muted'], 
                         bg=COLORS['bg_primary'])
    info_label.pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0))
    
    # Informacja o minimalnych długościach
    length_info_label = tk.Label(scrollable_frame, 
                                text="📏 Minimum lengths: Bug title (5), Game title (2), Environment fields (2), Steps (20), Expected/Actual (15), Notes (10)", 
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

    # Pola formularza
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

    # === Sekcja zrzutów ekranu ===
    screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    tk.Label(screenshots_frame, text="9. Screenshots & video (optional):", font=STYLES['font_subheading'],
            anchor='w', bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(anchor='w', fill='x')
    
    # Lista wybranych screenshotsów
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
        # Wyczyść listę
        for widget in screenshots_list_frame.winfo_children():
            widget.destroy()
        
        # Pokaż wybrane screenshotsy
        for i, screenshot_path in enumerate(selected_screenshots):
            screenshot_frame = tk.Frame(screenshots_list_frame, relief="solid", bd=1, 
                                      bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
            screenshot_frame.pack(fill='x', pady=2)
            
            # Nazwa pliku
            filename = os.path.basename(screenshot_path)
            icon = "🎬" if is_video_file(screenshot_path) else "📷"
            tk.Label(screenshot_frame, text=f"{icon} {filename}", anchor='w',
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Przycisk usuwania
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
    
    # Przyciski do zarządzania screenshotsami
    screenshots_buttons_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
    screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    add_screenshot_btn = create_modern_button(screenshots_buttons_frame, "📎 Add media", add_screenshot, 'warning')
    add_screenshot_btn.pack(side='left', padx=(0, STYLES['padding_medium']))
    
    if selected_screenshots:
        tk.Label(screenshots_buttons_frame, text=f"Selected: {len(selected_screenshots)} file(s)",
                fg=COLORS['text_secondary'], bg=COLORS['bg_primary'],
                font=STYLES['font_body']).pack(side='left')

    def save_bug():
        # Walidacja wymaganych pól
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
        
        # Sprawdź czy wszystkie wymagane pola są wypełnione
        missing_fields = []
        for field_key, field_name in required_fields.items():
            if field_key in ['steps', 'expected', 'actual', 'notes']:
                # Dla pól tekstowych (Text widget)
                value = fields[field_key].get("1.0", tk.END).strip()
            else:
                # Dla pól jednoliniowych (Entry widget)
                value = fields[field_key].get().strip()
            
            if not value:
                missing_fields.append(field_name)
        
        # Jeśli są puste pola, pokaż błąd i przerwij
        if missing_fields:
            error_message = "❌ Please fill in all required fields:\n\n"
            error_message += "\n".join(f"• {field}" for field in missing_fields)
            messagebox.showerror("Validation error", error_message)
            return
        
        # Walidacja długości pól tekstowych
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
            'notes': 10  # Minimum dla notatek (jeśli są wypełnione)
        }
        
        # Sprawdź czy pola środowiska nie są zbyt krótkie
        environment_fields = ['game_version', 'platform', 'device', 'internet']
        for field_key in environment_fields:
            value = fields[field_key].get().strip()
            if len(value) < 2:
                messagebox.showerror("Validation error", f"❌ Field '{required_fields[field_key]}' must have at least 2 characters")
                return
        
        # Sprawdź czy wybrano ważność
        if not fields['severity'].get():
            messagebox.showerror("Validation error", "❌ Please select bug severity")
            return
        
        short_fields = []
        for field_key, min_length in min_lengths.items():
            if field_key in ['steps', 'expected', 'actual', 'notes']:
                value = fields[field_key].get("1.0", tk.END).strip()
            else:
                value = fields[field_key].get().strip()
            
            # Dla notatek sprawdź długość tylko jeśli są wypełnione
            if field_key == 'notes' and not value:
                continue
                
            if len(value) < min_length:
                short_fields.append(f"{required_fields.get(field_key, field_key)} (minimum {min_length} characters)")
        
        if short_fields:
            error_message = "❌ Some fields are too short:\n\n"
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

            # Zapisz screenshotsy
            bug_title = fields['title'].get()
            for i, screenshot_path in enumerate(selected_screenshots):
                filename = copy_screenshot_to_folder(screenshot_path, bug_title, i + 1)
                if filename:
                    bug_data["screenshots"].append(filename)

            # Wczytaj istniejące bugi (jeśli plik istnieje)
            if os.path.exists(BUGS_FILE):
                with open(BUGS_FILE, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
            else:
                bugs = []

            # Dodaj nowy bug
            bugs.append(bug_data)

            # Zapisz do pliku
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            # Informacja o sukcesie
            print("✅ New bug saved:", bug_data)
            if bug_data["screenshots"]:
                print(f"📎 Saved {len(bug_data['screenshots'])} attachment(s)")

            # Zamknij formularz
            load_bugs()
            top.destroy()

        except Exception as e:
            print("❌ Error while saving bug:", e)

    # Kontener do wyśrodkowania przycisku
    button_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    button_frame.pack(pady=STYLES['padding_large'], fill='x')
    
    button_center_frame = tk.Frame(button_frame, bg=COLORS['bg_primary'])
    button_center_frame.pack(expand=True)

    save_btn = create_modern_button(button_center_frame, "💾 Save bug", save_bug, 'success')
    save_btn.pack()

add_bug_btn = tk.Button(root, text="➕ Add new bug", command=open_bug_form, 
                       bg=COLORS['accent_blue'], fg=COLORS['text_primary'], 
                       font=STYLES['font_body'], padx=STYLES['padding_medium'], 
                       pady=STYLES['padding_small'], relief='flat', 
                       activebackground=COLORS['accent_green'],
                       activeforeground=COLORS['text_primary'])
add_bug_btn.pack(pady=STYLES['padding_medium'])

game_filter_combo.bind('<<ComboboxSelected>>', lambda _e: load_bugs())

# ====== Uruchomienie ======
load_bugs()
root.mainloop()
