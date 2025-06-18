import tkinter as tk
from tkinter import ttk
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
bug_list_label = tk.Label(tab_all, text="(Tutaj pojawi się lista zgłoszonych bugów)", fg="gray")
bug_list_label.pack(pady=20)

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
            top.destroy()

        except Exception as e:
            print("❌ Błąd przy zapisie buga:", e)



    tk.Button(scrollable_frame, text="💾 Zapisz bug", command=save_bug,
              bg="#2196F3", fg="white", padx=10, pady=5).pack(pady=20)

add_bug_btn = tk.Button(root, text="➕ Dodaj nowy bug", command=open_bug_form, bg="#4CAF50", fg="white", padx=10, pady=5)
add_bug_btn.pack(pady=10)

# ====== Uruchomienie ======
root.mainloop()
