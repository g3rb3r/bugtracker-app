import tkinter as tk
from tkinter import ttk

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
    top.geometry("500x600")
    tk.Label(top, text="Tutaj pojawi się formularz 🔧", font=("Helvetica", 12)).pack(pady=20)

add_bug_btn = tk.Button(root, text="➕ Dodaj nowy bug", command=open_bug_form, bg="#4CAF50", fg="white", padx=10, pady=5)
add_bug_btn.pack(pady=10)

# ====== Uruchomienie ======
root.mainloop()
