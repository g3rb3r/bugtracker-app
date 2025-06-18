import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
BUGS_FILE = "bugs.json"

# Konfiguracja głównego okna
root = tk.Tk()
root.title("Bug Tracker")
root.geometry("800x600")

# ====== Nagłówek ======
header = tk.Label(root, text="🎮 Bug Tracker - Panel QA", font=("Helvetica", 16, "bold"))
header.pack(pady=10)

# ====== Zakładki (filtry statusów) ======
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both', padx=10, pady=5)

# Tworzymy trzy zakładki
tab_all = tk.Frame(notebook)
tab_in_progress = tk.Frame(notebook)
tab_done = tk.Frame(notebook)

notebook.add(tab_all, text="🗂️ Wszystkie")
notebook.add(tab_in_progress, text="🛠️ W trakcie")
notebook.add(tab_done, text="✅ Zakończone")

# ====== Placeholder: lista bugów ======
def show_bug_details(bug):
    detail_window = tk.Toplevel(root)
    detail_window.title(f"📋 Szczegóły - {bug['title']}")
    detail_window.geometry("700x800")

    # Tworzymy canvas z przewijaniem
    canvas = tk.Canvas(detail_window)
    scrollbar = tk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

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
    read_only_frame = tk.Frame(scrollable_frame)
    read_only_frame.pack(fill='x', padx=10, pady=5)

    tk.Label(read_only_frame, text=f"Tytuł: {bug['title']}", font=('Helvetica', 12, 'bold')).pack(anchor='w', fill='x')
    tk.Label(read_only_frame, text=f"Ważność: {bug['severity']}", font=('Helvetica', 10)).pack(anchor='w', fill='x')
    
    env_label = tk.Label(read_only_frame, text=f"Środowisko:\n{bug['environment']}", font=('Helvetica', 10), justify='left', anchor='w')
    env_label.pack(anchor='w', fill='x', pady=(5, 0))

    # === Pola edytowalne (domyślnie tylko do odczytu) ===
    editable_frame = tk.Frame(scrollable_frame)
    editable_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Kroki do odtworzenia
    tk.Label(editable_frame, text="Kroki do odtworzenia:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5), fill='x')
    steps_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled')
    steps_text.pack(fill='x', pady=(0, 10))
    steps_text.config(state='normal')
    steps_text.insert(tk.END, bug['steps'])
    steps_text.config(state='disabled')

    # Oczekiwany rezultat
    tk.Label(editable_frame, text="Oczekiwany rezultat:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5), fill='x')
    expected_text = tk.Text(editable_frame, height=4, wrap='word', state='disabled')
    expected_text.pack(fill='x', pady=(0, 10))
    expected_text.config(state='normal')
    expected_text.insert(tk.END, bug['expected'])
    expected_text.config(state='disabled')

    # Faktyczny rezultat
    tk.Label(editable_frame, text="Faktyczny rezultat:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5), fill='x')
    actual_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled')
    actual_text.pack(fill='x', pady=(0, 10))
    actual_text.config(state='normal')
    actual_text.insert(tk.END, bug['actual'])
    actual_text.config(state='disabled')

    # Notatki
    tk.Label(editable_frame, text="Notatki / Dodatkowe informacje:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5), fill='x')
    notes_text = tk.Text(editable_frame, height=6, wrap='word', state='disabled')
    notes_text.pack(fill='x', pady=(0, 10))
    notes_text.config(state='normal')
    notes_text.insert(tk.END, bug['notes'])
    notes_text.config(state='disabled')

    # === Zmiana statusu ===
    status_frame = tk.Frame(scrollable_frame)
    status_frame.pack(pady=10, fill='x', padx=10)

    tk.Label(status_frame, text="Status:", font=('Helvetica', 10, 'bold')).pack(side='left', padx=(0, 10))
    status_var = tk.StringVar(value=bug['status'])
    status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["W trakcie", "Zakończone"], state="disabled")
    status_dropdown.pack(side='left')

    # === Przyciski ===
    buttons_frame = tk.Frame(scrollable_frame)
    buttons_frame.pack(pady=10, fill='x', padx=10)
    
    # Kontener do wyśrodkowania przycisków
    buttons_center_frame = tk.Frame(buttons_frame)
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
            edit_button.config(text="❌ Anuluj edycję", bg="#f44336")
            edit_mode = True
            
            # Pokaż przycisk zapisu
            save_button.pack(side='left', padx=5)
        else:
            # Wyłącz tryb edycji
            steps_text.config(state='disabled')
            expected_text.config(state='disabled')
            actual_text.config(state='disabled')
            notes_text.config(state='disabled')
            status_dropdown.config(state="disabled")
            edit_button.config(text="✏️ Edytuj raport", bg="#2196F3")
            edit_mode = False
            
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
                    break

            # Zapisz ponownie
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            print(f"✅ Zapisano zmiany: {bug['title']}")
            detail_window.destroy()
            load_bugs()

        except Exception as e:
            print("❌ Błąd przy zapisie zmian:", e)

    # Przycisk edycji
    edit_button = tk.Button(buttons_center_frame, text="✏️ Edytuj raport", command=toggle_edit_mode,
                           bg="#2196F3", fg="white", padx=10, pady=5)
    edit_button.pack(side='left', padx=5)

    # Przycisk zapisu (początkowo ukryty)
    save_button = tk.Button(buttons_center_frame, text="💾 Zapisz zmiany", command=save_changes,
                           bg="#4CAF50", fg="white", padx=10, pady=5)
    
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

    tk.Button(buttons_center_frame, text="🗑️ Usuń buga", command=delete_bug,
              bg="#f44336", fg="white", padx=10, pady=5).pack(side='left', padx=5)

    # === Przycisk zamknięcia ===
    tk.Button(buttons_center_frame, text="❌ Zamknij podgląd", command=detail_window.destroy,
              bg="#9E9E9E", fg="white", padx=10, pady=5).pack(side='left', padx=5)



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
                    tk.Label(tab, text="Brak zgłoszonych bugów", fg="gray").pack(pady=20)
                return

            # Funkcja pomocnicza do tworzenia karty buga
            def create_bug_card(parent, bug):
                frame = tk.Frame(parent, bd=1, relief="solid", padx=10, pady=5)
                frame.pack(fill='x', padx=10, pady=5)

                title = tk.Label(frame, text=f"🐞 {bug['title']}", font=('Helvetica', 10, 'bold'), anchor='w', cursor="hand2", wraplength=600, justify='left')
                title.pack(fill='x')
                title.bind("<Button-1>", lambda e, b=bug: show_bug_details(b))

                info = tk.Label(frame, text=f"Ważność: {bug['severity']} | Status: {bug['status']}", font=('Helvetica', 9), fg="gray", anchor='w')
                info.pack(fill='x')

            # Rozdziel bugi do odpowiednich zakładek
            for bug in bugs:
                create_bug_card(tab_all, bug)

                if bug['status'] == "W trakcie":
                    create_bug_card(tab_in_progress, bug)
                elif bug['status'] == "Zakończone":
                    create_bug_card(tab_done, bug)

        except Exception as e:
            for tab in (tab_all, tab_in_progress, tab_done):
                tk.Label(tab, text=f"Błąd przy wczytywaniu bugów: {e}", fg="red").pack(pady=20)
    else:
        for tab in (tab_all, tab_in_progress, tab_done):
            tk.Label(tab, text="Brak pliku z bugami", fg="gray").pack(pady=20)


# ====== Przycisk dodawania nowego buga ======
def open_bug_form():
    top = tk.Toplevel(root)
    top.title("Dodaj nowy bug")
    top.geometry("580x750")

    # Tworzymy canvas z przewijaniem
    canvas = tk.Canvas(top)
    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

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

    fields = {}

    def create_field(label_text, is_multiline=False):
        label = tk.Label(scrollable_frame, text=label_text)
        label.pack(anchor='w', padx=10, pady=(10, 0))
        if is_multiline:
            entry = tk.Text(scrollable_frame, height=5, width=60, wrap='word')
        else:
            entry = tk.Entry(scrollable_frame, width=60)
        entry.pack(padx=10)
        return entry

    # Pola formularza
    fields['title'] = create_field("1. Tytuł błędu:")

    tk.Label(scrollable_frame, text="2. Środowisko:", font=('Helvetica', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
    fields['game_version'] = create_field("Wersja gry:")
    fields['platform'] = create_field("Platforma:")
    fields['device'] = create_field("Urządzenie:")
    fields['internet'] = create_field("Połączenie internetowe:")

    fields['steps'] = create_field("3. Kroki do odtworzenia błędu:", is_multiline=True)
    fields['expected'] = create_field("4. Oczekiwany rezultat:", is_multiline=True)
    fields['actual'] = create_field("5. Faktyczny rezultat:", is_multiline=True)

    tk.Label(scrollable_frame, text="6. Ważność błędu:").pack(anchor='w', padx=10, pady=(10, 0))
    severity_var = tk.StringVar(value="Drobny")
    severity_dropdown = ttk.Combobox(scrollable_frame, textvariable=severity_var, values=[
        "Kosmetyczny", "Drobny", "Poważny", "Krytyczny"
    ], width=57)
    severity_dropdown.pack(padx=10)
    fields['severity'] = severity_var

    fields['notes'] = create_field("7. Notatki / Dodatkowe informacje:", is_multiline=True)

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
                "status": "W trakcie"
            }

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

            # Zamknij formularz
            load_bugs()
            top.destroy()

        except Exception as e:
            print("❌ Błąd przy zapisie buga:", e)



    tk.Button(scrollable_frame, text="💾 Zapisz bug", command=save_bug,
              bg="#2196F3", fg="white", padx=10, pady=5).pack(pady=20)

add_bug_btn = tk.Button(root, text="➕ Dodaj nowy bug", command=open_bug_form, bg="#4CAF50", fg="white", padx=10, pady=5)
add_bug_btn.pack(pady=10)

# ====== Uruchomienie ======
load_bugs()
root.mainloop()
