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
    detail_window.geometry("600x650")

    text_frame = tk.Frame(detail_window)
    text_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

    text = tk.Text(text_frame, wrap='word', font=("Helvetica", 10), height=30)
    text.pack(fill="both", expand=True)

    full_text = (
        f"Tytuł: {bug['title']}\n\n"
        f"Środowisko:\n{bug['environment']}\n\n"
        f"Kroki do odtworzenia:\n{bug['steps']}\n\n"
        f"Oczekiwany rezultat:\n{bug['expected']}\n\n"
        f"Faktyczny rezultat:\n{bug['actual']}\n\n"
        f"Ważność: {bug['severity']}\n\n"
        f"Dodatkowe notatki:\n{bug['notes']}\n\n"
    )
    text.insert(tk.END, full_text)
    text.config(state="disabled")

    # === Zmiana statusu ===
    status_frame = tk.Frame(detail_window)
    status_frame.pack(pady=10)

    tk.Label(status_frame, text="Status:", font=('Helvetica', 10, 'bold')).pack(side='left', padx=(0, 10))
    status_var = tk.StringVar(value=bug['status'])
    status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["W trakcie", "Zakończone"], state="readonly")
    status_dropdown.pack(side='left')

    # === Przycisk zapisu ===
    def save_status_change():
        try:
            # Wczytaj wszystkie bugi
            with open(BUGS_FILE, "r", encoding="utf-8") as f:
                bugs = json.load(f)

            # Znajdź i zaktualizuj
            for b in bugs:
                if b['title'] == bug['title'] and b['environment'] == bug['environment']:
                    b['status'] = status_var.get()
                    break

            # Zapisz ponownie
            with open(BUGS_FILE, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            print(f"✅ Zmieniono status: {bug['title']} → {status_var.get()}")
            detail_window.destroy()
            load_bugs()

        except Exception as e:
            print("❌ Błąd przy aktualizacji statusu:", e)

    tk.Button(detail_window, text="💾 Zapisz zmiany", command=save_status_change,
              bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=10)
    
        # === Przycisk usuwania ===
    def delete_bug():
        if tk.messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tego buga?"):
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

    tk.Button(detail_window, text="🗑️ Usuń buga", command=delete_bug,
              bg="#f44336", fg="white", padx=10, pady=5).pack(pady=(0, 10))



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
