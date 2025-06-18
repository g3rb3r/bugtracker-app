import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os
import shutil
from datetime import datetime

# ====== NOWOCZESNY MOTYW CIEMNY (VS Code/OpenAI/Cursor style) ======
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

# Funkcje pomocnicze do obsługi screenshotsów
def get_screenshot_filename(bug_title, index):
    """Generuje nazwę pliku dla screenshotu"""
    # Usuń znaki specjalne z tytułu
    safe_title = "".join(c for c in bug_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    return f"{safe_title}_{index}.png"

def copy_screenshot_to_folder(source_path, bug_title, index):
    """Kopiuje screenshot do folderu screenshots z odpowiednią nazwą"""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
    
    filename = get_screenshot_filename(bug_title, index)
    destination = os.path.join(SCREENSHOTS_DIR, filename)
    
    try:
        shutil.copy2(source_path, destination)
        return filename
    except Exception as e:
        print(f"❌ Błąd przy kopiowaniu screenshotu: {e}")
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
        print(f"❌ Błąd przy tworzeniu miniatury: {e}")
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
            preview_window.title(f"Podgląd screenshotu")
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
            close_button = tk.Button(preview_window, text="Zamknij", command=preview_window.destroy,
                     bg="#f44336", fg="white", padx=10, pady=5)
            close_button.pack(pady=10)
            
            # Zachowaj referencję do obrazu w przycisku
            close_button.photo = photo
            
    except Exception as e:
        print(f"❌ Błąd przy wyświetlaniu podglądu: {e}")
        messagebox.showerror("Błąd", f"Nie można wyświetlić obrazu: {e}")

def create_modern_button(parent, text, command, button_type='primary'):
    """Tworzy nowoczesny przycisk w stylu VS Code"""
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

subtitle = tk.Label(header_frame, text="Panel QA - Zarządzanie błędami", font=STYLES['font_body'], 
                   bg=COLORS['bg_primary'], fg=COLORS['text_secondary'])
subtitle.pack(side='left', padx=(STYLES['padding_medium'], 0), pady=(5, 0))

# ====== Zakładki (filtry statusów) ======
notebook_frame = tk.Frame(root, bg=COLORS['bg_primary'])
notebook_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_small'])

# Konfiguracja stylu zakładek
style = ttk.Style()
style.theme_use('clam')  # Użyj motywu clam dla lepszej kontroli

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

notebook = ttk.Notebook(notebook_frame, style='Custom.TNotebook')
notebook.pack(expand=1, fill='both')

# Tworzymy trzy zakładki
tab_all = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_in_progress = tk.Frame(notebook, bg=COLORS['bg_secondary'])
tab_done = tk.Frame(notebook, bg=COLORS['bg_secondary'])

notebook.add(tab_all, text="📋 Wszystkie")
notebook.add(tab_in_progress, text="🛠️ W trakcie")
notebook.add(tab_done, text="✅ Zakończone")

# ====== Placeholder: lista bugów ======
def show_bug_details(bug):
    detail_window = tk.Toplevel(root)
    detail_window.title(f"📋 Szczegóły - {bug['title']}")
    detail_window.geometry("700x800")
    detail_window.configure(bg=COLORS['bg_primary'])

    # Tworzymy canvas z przewijaniem
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

    tk.Label(read_only_frame, text=f"Tytuł: {bug['title']}", font=STYLES['font_subheading'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
    tk.Label(read_only_frame, text=f"Ważność: {bug['severity']}", font=STYLES['font_body'], 
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(anchor='w', fill='x')
    
    env_label = tk.Label(read_only_frame, text=f"Środowisko:\n{bug['environment']}", 
                        font=STYLES['font_body'], justify='left', anchor='w',
                        bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
    env_label.pack(anchor='w', fill='x', pady=(STYLES['padding_small'], 0))

    # === Pola edytowalne (domyślnie tylko do odczytu) ===
    editable_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    editable_frame.pack(fill='both', expand=True, padx=STYLES['padding_large'], pady=STYLES['padding_medium'])

    # Kroki do odtworzenia
    tk.Label(editable_frame, text="Kroki do odtworzenia:", font=STYLES['font_subheading'], 
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
    tk.Label(editable_frame, text="Oczekiwany rezultat:", font=STYLES['font_subheading'], 
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
    tk.Label(editable_frame, text="Faktyczny rezultat:", font=STYLES['font_subheading'], 
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
    tk.Label(editable_frame, text="Notatki / Dodatkowe informacje:", font=STYLES['font_subheading'], 
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
        
        tk.Label(screenshots_frame, text="Zrzuty ekranu:", font=STYLES['font_subheading'], 
                bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
        
        # Kontener na miniatury
        thumbnails_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
        thumbnails_frame.pack(fill='x', pady=STYLES['padding_small'])
        
        for i, screenshot_filename in enumerate(bug['screenshots']):
            screenshot_path = get_screenshot_path(screenshot_filename)
            if os.path.exists(screenshot_path):
                # Utwórz miniaturę
                thumbnail = create_thumbnail(screenshot_path, (80, 80))
                if thumbnail:
                    # Kontener na miniaturę
                    thumb_container = tk.Frame(thumbnails_frame, relief="solid", bd=1, 
                                             bg=COLORS['bg_tertiary'], highlightbackground=COLORS['border'])
                    thumb_container.pack(side='left', padx=5, pady=5)
                    
                    # Miniatura z możliwością kliknięcia
                    thumb_label = tk.Label(thumb_container, image=thumbnail, cursor="hand2",
                                         bg=COLORS['bg_tertiary'])
                    thumb_label.image = thumbnail  # Zachowaj referencję
                    thumb_label.pack(padx=5, pady=5)
                    thumb_label.bind("<Button-1>", lambda e, path=screenshot_path: show_image_preview(path))
                    
                    # Numer screenshotu
                    tk.Label(thumb_container, text=f"#{i+1}", font=STYLES['font_small'], 
                            fg=COLORS['text_muted'], bg=COLORS['bg_tertiary']).pack()
            else:
                # Jeśli plik nie istnieje, pokaż informację
                tk.Label(thumbnails_frame, text=f"❌ Brak pliku: {screenshot_filename}", 
                        fg=COLORS['error'], bg=COLORS['bg_primary'], 
                        font=STYLES['font_body']).pack(side='left', padx=5, pady=5)

    # === Sekcja edycji zrzutów ekranu (tylko w trybie edycji) ===
    edit_screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    edit_screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    # Nagłówek sekcji edycji zrzutów ekranu
    edit_screenshots_header = tk.Label(edit_screenshots_frame, text="Dodaj nowe zrzuty ekranu:", 
                                      font=STYLES['font_subheading'], anchor='w',
                                      bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
    edit_screenshots_header.pack(anchor='w', fill='x')
    
    # Lista wybranych nowych zrzutów ekranu
    new_screenshots = []
    edit_screenshots_list_frame = tk.Frame(edit_screenshots_frame, bg=COLORS['bg_primary'])
    edit_screenshots_list_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    def add_new_screenshot():
        file_path = filedialog.askopenfilename(
            title="Wybierz zrzut ekranu",
            filetypes=[
                ("Obrazy", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Wszystkie pliki", "*.*")
            ]
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
            tk.Label(screenshot_frame, text=f"📷 {filename}", anchor='w',
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Przycisk usuwania
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_new_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
        
        # Aktualizuj label z liczbą zrzutów
        if new_screenshots:
            new_screenshots_label.config(text=f"Nowe: {len(new_screenshots)} zrzutów")
        else:
            new_screenshots_label.config(text="")
    
    # Przyciski do zarządzania nowymi zrzutami ekranu
    edit_screenshots_buttons_frame = tk.Frame(edit_screenshots_frame, bg=COLORS['bg_primary'])
    edit_screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    edit_add_screenshot_btn = create_modern_button(edit_screenshots_buttons_frame, "📷 Dodaj zrzut ekranu", add_new_screenshot, 'warning')
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
    status_var = tk.StringVar(value=bug['status'])
    status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["W trakcie", "Zakończone"], state="disabled")
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
            steps_text.config(state='normal')
            expected_text.config(state='normal')
            actual_text.config(state='normal')
            notes_text.config(state='normal')
            status_dropdown.config(state="readonly")
            edit_button.config(text="❌ Anuluj edycję")
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
            steps_text.config(state='disabled')
            expected_text.config(state='disabled')
            actual_text.config(state='disabled')
            notes_text.config(state='disabled')
            status_dropdown.config(state="disabled")
            edit_button.config(text="✏️ Edytuj raport")
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
            # Wczytaj wszystkie bugi
            with open(BUGS_FILE, "r", encoding="utf-8") as f:
                bugs = json.load(f)
            # Znajdź i zaktualizuj
            for b in bugs:
                if b['title'] == bug['title'] and b['environment'] == bug['environment']:
                    b['status'] = status_var.get()
                    b['steps'] = steps_text.get("1.0", tk.END).strip()
                    b['expected'] = expected_text.get("1.0", tk.END).strip()
                    b['actual'] = actual_text.get("1.0", tk.END).strip()
                    b['notes'] = notes_text.get("1.0", tk.END).strip()
                    # Dodaj nowe zrzuty ekranu do istniejących
                    if new_screenshots:
                        bug_title = bug['title']
                        existing_count = len(b.get('screenshots', []))
                        for i, screenshot_path in enumerate(new_screenshots):
                            filename = copy_screenshot_to_folder(screenshot_path, bug_title, existing_count + i + 1)
                            if filename:
                                if 'screenshots' not in b:
                                    b['screenshots'] = []
                                b['screenshots'].append(filename)
                    break
            # Zapisz ponownie
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)
            print(f"✅ Zapisano zmiany: {bug['title']}")
            if new_screenshots:
                print(f"📷 Dodano {len(new_screenshots)} nowych zrzutów ekranu")
            # Po zapisaniu wróć do trybu podglądu, nie zamykaj okna
            toggle_edit_mode()
            load_bugs()  # odśwież listę bugów w głównym oknie
        except Exception as e:
            print("❌ Błąd przy zapisie zmian:", e)

    # Przycisk zapisu (początkowo ukryty)
    save_button = create_modern_button(buttons_center_frame, "💾 Zapisz zmiany", save_changes, 'success')

    # Przycisk edycji
    edit_button = create_modern_button(buttons_center_frame, "✏️ Edytuj raport", toggle_edit_mode, 'primary')
    edit_button.pack(side='left', padx=STYLES['padding_small'])

    # === Przycisk zamknięcia ===
    close_btn = create_modern_button(buttons_center_frame, "❌ Zamknij podgląd", detail_window.destroy, 'secondary')
    close_btn.pack(side='left', padx=STYLES['padding_small'])

    # === Przycisk usuwania ===
    def delete_bug():
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tego buga?"):
            try:
                with open(BUGS_FILE, "r", encoding="utf-8") as f:
                    bugs = json.load(f)

                # Usuń buga na podstawie tytułu i środowiska
                bugs = [b for b in bugs if not (b['title'] == bug['title'] and b['environment'] == bug['environment'])]

                with open(BUGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(bugs, f, indent=2, ensure_ascii=False)

                print(f"🗑️ Usunięto buga: {bug['title']}")
                detail_window.destroy()
                load_bugs()

            except Exception as e:
                print("❌ Błąd przy usuwaniu buga:", e)

    delete_btn = create_modern_button(buttons_center_frame, "🗑️ Usuń buga", delete_bug, 'error')
    delete_btn.pack(side='left', padx=STYLES['padding_small'])

def load_bugs():
    # Wyczyść wszystkie zakładki
    for tab in (tab_all, tab_in_progress, tab_done):
        for widget in tab.winfo_children():
            widget.destroy()

    if os.path.exists(BUGS_FILE):
        try:
            with open(BUGS_FILE, "r", encoding="utf-8") as f:
                bugs = json.load(f)

            if not bugs:
                for tab in (tab_all, tab_in_progress, tab_done):
                    empty_label = tk.Label(tab, text="Brak zgłoszonych bugów", 
                                         fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                         font=STYLES['font_body'])
                    empty_label.pack(pady=STYLES['padding_large'])
                return

            # Funkcja pomocnicza do tworzenia karty buga
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

                info = tk.Label(frame, text=f"Ważność: {bug['severity']} | Status: {bug['status']}", 
                              font=STYLES['font_small'], fg=COLORS['text_secondary'], anchor='w',
                              bg=COLORS['bg_tertiary'])
                info.pack(fill='x', padx=STYLES['padding_medium'], pady=(0, STYLES['padding_small']))

            # Rozdziel bugi do odpowiednich zakładek
            for bug in bugs:
                create_bug_card(tab_all, bug)

                if bug['status'] == "W trakcie":
                    create_bug_card(tab_in_progress, bug)
                elif bug['status'] == "Zakończone":
                    create_bug_card(tab_done, bug)

        except Exception as e:
            for tab in (tab_all, tab_in_progress, tab_done):
                error_label = tk.Label(tab, text=f"Błąd przy wczytywaniu bugów: {e}", 
                                     fg=COLORS['error'], bg=COLORS['bg_secondary'],
                                     font=STYLES['font_body'])
                error_label.pack(pady=STYLES['padding_large'])
    else:
        for tab in (tab_all, tab_in_progress, tab_done):
            no_file_label = tk.Label(tab, text="Brak pliku z bugami", 
                                   fg=COLORS['text_muted'], bg=COLORS['bg_secondary'],
                                   font=STYLES['font_body'])
            no_file_label.pack(pady=STYLES['padding_large'])


# ====== Przycisk dodawania nowego buga ======
def open_bug_form():
    top = tk.Toplevel(root)
    top.title("Dodaj nowy bug")
    top.geometry("700x800")
    top.configure(bg=COLORS['bg_primary'])

    # Tworzymy canvas z przewijaniem
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
    fields['title'] = create_field("1. Tytuł błędu:")

    tk.Label(scrollable_frame, text="2. Środowisko:", font=STYLES['font_subheading'], 
            anchor='w', bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
    fields['game_version'] = create_field("Wersja gry:")
    fields['platform'] = create_field("Platforma:")
    fields['device'] = create_field("Urządzenie:")
    fields['internet'] = create_field("Połączenie internetowe:")

    fields['steps'] = create_field("3. Kroki do odtworzenia błędu:", is_multiline=True)
    fields['expected'] = create_field("4. Oczekiwany rezultat:", is_multiline=True)
    fields['actual'] = create_field("5. Faktyczny rezultat:", is_multiline=True)

    tk.Label(scrollable_frame, text="6. Ważność błędu:", anchor='w', 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary'], 
            font=STYLES['font_body']).pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
    severity_var = tk.StringVar(value="Drobny")
    severity_dropdown = ttk.Combobox(scrollable_frame, textvariable=severity_var, values=[
        "Kosmetyczny", "Drobny", "Poważny", "Krytyczny"
    ], state="readonly")
    severity_dropdown.pack(padx=STYLES['padding_large'], fill='x')
    fields['severity'] = severity_var

    fields['notes'] = create_field("7. Notatki / Dodatkowe informacje:", is_multiline=True)

    # === Sekcja zrzutów ekranu ===
    screenshots_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    screenshots_frame.pack(fill='x', padx=STYLES['padding_large'], pady=STYLES['padding_medium'])
    
    tk.Label(screenshots_frame, text="8. Zrzuty ekranu (opcjonalne):", font=STYLES['font_subheading'], 
            anchor='w', bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(anchor='w', fill='x')
    
    # Lista wybranych screenshotsów
    selected_screenshots = []
    screenshots_list_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
    screenshots_list_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    def add_screenshot():
        file_path = filedialog.askopenfilename(
            title="Wybierz screenshot",
            filetypes=[
                ("Obrazy", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Wszystkie pliki", "*.*")
            ]
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
            tk.Label(screenshot_frame, text=f"📷 {filename}", anchor='w', 
                    bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
                    font=STYLES['font_body']).pack(side='left', padx=5, pady=2, fill='x', expand=True)
            
            # Przycisk usuwania
            tk.Button(screenshot_frame, text="❌", command=lambda idx=i: remove_screenshot(idx),
                     bg=COLORS['error'], fg=COLORS['text_primary'], width=3,
                     relief='flat', font=STYLES['font_small']).pack(side='right', padx=5, pady=2)
    
    # Przyciski do zarządzania screenshotsami
    screenshots_buttons_frame = tk.Frame(screenshots_frame, bg=COLORS['bg_primary'])
    screenshots_buttons_frame.pack(fill='x', pady=STYLES['padding_small'])
    
    add_screenshot_btn = create_modern_button(screenshots_buttons_frame, "📷 Dodaj screenshot", add_screenshot, 'warning')
    add_screenshot_btn.pack(side='left', padx=(0, STYLES['padding_medium']))
    
    if selected_screenshots:
        tk.Label(screenshots_buttons_frame, text=f"Wybrano: {len(selected_screenshots)} screenshotów", 
                fg=COLORS['text_secondary'], bg=COLORS['bg_primary'],
                font=STYLES['font_body']).pack(side='left')

    def save_bug():
        try:
            bug_data = {
                "title": fields['title'].get(),
                "environment": (
                    f"Wersja gry: {fields['game_version'].get()}\n"
                    f"Platforma: {fields['platform'].get()}\n"
                    f"Urządzenie: {fields['device'].get()}\n"
                    f"Połączenie internetowe: {fields['internet'].get()}"
                ),
                "steps": fields['steps'].get("1.0", tk.END).strip(),
                "expected": fields['expected'].get("1.0", tk.END).strip(),
                "actual": fields['actual'].get("1.0", tk.END).strip(),
                "severity": fields['severity'].get(),
                "notes": fields['notes'].get("1.0", tk.END).strip(),
                "status": "W trakcie",
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
            print("✅ Nowy bug zapisany:", bug_data)
            if bug_data["screenshots"]:
                print(f"📷 Zapisano {len(bug_data['screenshots'])} screenshotsów")

            # Zamknij formularz
            load_bugs()
            top.destroy()

        except Exception as e:
            print("❌ Błąd przy zapisie buga:", e)

    # Kontener do wyśrodkowania przycisku
    button_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_primary'])
    button_frame.pack(pady=STYLES['padding_large'], fill='x')
    
    button_center_frame = tk.Frame(button_frame, bg=COLORS['bg_primary'])
    button_center_frame.pack(expand=True)

    save_btn = create_modern_button(button_center_frame, "💾 Zapisz bug", save_bug, 'success')
    save_btn.pack()

add_bug_btn = tk.Button(root, text="➕ Dodaj nowy bug", command=open_bug_form, 
                       bg=COLORS['accent_blue'], fg=COLORS['text_primary'], 
                       font=STYLES['font_body'], padx=STYLES['padding_medium'], 
                       pady=STYLES['padding_small'], relief='flat', 
                       activebackground=COLORS['accent_green'],
                       activeforeground=COLORS['text_primary'])
add_bug_btn.pack(pady=STYLES['padding_medium'])

# ====== Uruchomienie ======
load_bugs()
root.mainloop()
