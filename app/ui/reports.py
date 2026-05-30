"""UI: generate game report dialog and success message."""

import json
import os

from tkinter import filedialog, messagebox

from app.constants import GAME_FILTER_ALL, GAME_FILTER_NO_TITLE, STATUS_MAP
from app.reports.builder import build_game_report
from app.utils.text import normalize_status, normalized_game_title


def generate_game_report(app):
    selected_game = (app.game_filter_var.get() or "").strip()
    if not selected_game or selected_game in {GAME_FILTER_ALL, GAME_FILTER_NO_TITLE}:
        messagebox.showinfo("Report", "Choose a specific game in the filter first.")
        return

    if not os.path.exists(app.paths.bugs_file):
        messagebox.showerror("Report", "No bugs file found.")
        return

    try:
        with open(app.paths.bugs_file, encoding="utf-8") as f:
            bugs = json.load(f)
        for b in bugs:
            b["status"] = normalize_status(b.get("status"), STATUS_MAP)
    except Exception as e:
        messagebox.showerror("Report", f"Could not read bugs file: {e}")
        return

    sel_key = normalized_game_title(selected_game)
    game_bugs = [
        b for b in bugs if normalized_game_title(b.get("game_title")) == sel_key
    ]
    if not game_bugs:
        messagebox.showinfo("Report", f"No bugs found for game: {selected_game}")
        return

    os.makedirs(app.paths.reports_dir, exist_ok=True)
    target_dir = filedialog.askdirectory(
        title="Choose folder for generated report",
        initialdir=app.paths.reports_dir,
    )
    if not target_dir:
        return

    try:
        result = build_game_report(
            game_title=selected_game,
            game_bugs=game_bugs,
            screenshots_dir=app.paths.screenshots_dir,
            install_root=app.paths.install_root,
            target_parent_dir=target_dir,
            export_pdf=True,
        )
    except Exception as e:
        messagebox.showerror("Report", f"Could not generate report: {e}")
        return

    info_lines = [
        "Report generated.",
        "",
        f"Folder:\n{result['report_dir']}",
        f"\nHTML:\n{result['index_path']}",
        f"\nZIP:\n{result['zip_path']}",
        "",
        f"Bugs: {result['total_bugs']}",
        f"Attachments copied: {result['total_attachments']}",
    ]
    if result.get("pdf_path"):
        info_lines.append(f"\nPDF:\n{result['pdf_path']}")
    elif result.get("pdf_message"):
        info_lines.append(f"\nPDF: {result['pdf_message']}")

    if result["missing_attachments"]:
        info_lines.append(f"\nMissing attachments: {len(result['missing_attachments'])}")

    messagebox.showinfo("Report ready", "\n".join(info_lines))
