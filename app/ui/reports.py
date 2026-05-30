"""HTML game report export."""
import os
import json
import shutil
from datetime import datetime
from html import escape

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.constants import (
    COLORS, STYLES, MEDIA_FILE_TYPES, GAME_FILTER_ALL, GAME_FILTER_NO_TITLE,
    SEVERITY_OPTIONS, ENV_FIELD_PREFIXES, STATUS_MAP,
)
from app.utils.text import normalize_status, normalized_game_title, safe_filename
from app.utils.bugs import load_bugs_list, save_bugs_list, normalize_bugs_statuses, bugs_match
from app.screenshots.media import (
    is_video_file, copy_screenshot_to_folder, get_screenshot_path,
    open_attachment_external, create_thumbnail, show_image_preview,
)
from app.ui.theme import create_modern_button

def generate_game_report(app):

    selected_game = (app.game_filter_var.get() or "").strip()
    if not selected_game or selected_game in {GAME_FILTER_ALL, GAME_FILTER_NO_TITLE}:
        messagebox.showinfo("Report", "Choose a specific game in the filter first.")
        return

    if not os.path.exists(app.paths.bugs_file):
        messagebox.showerror("Report", "No bugs file found.")
        return

    try:
        with open(app.paths.bugs_file, "r", encoding="utf-8") as f:
            bugs = json.load(f)
        for b in bugs:
            b["status"] = normalize_status(b.get("status", STATUS_MAP))
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

    default_reports_dir = os.path.join(os.getcwd(), app.paths.reports_dir)
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
            source_path = get_screenshot_path(app.paths.screenshots_dir, filename)
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
