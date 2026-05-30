"""Add new bug form."""
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

def open_bug_form(app):

    top = tk.Toplevel(app.root)
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
    set_active = app.scroll.register_canvas(canvas)
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

    active_game = (app.game_filter_var.get() or "").strip()
    if active_game not in (GAME_FILTER_ALL, GAME_FILTER_NO_TITLE, ""):
        prefill = get_game_prefill_data(app.paths.bugs_file, active_game)
        fields['game_title'].insert(0, prefill["game_title"])
        for env_key in ENV_FIELD_PREFIXES:
            if prefill[env_key]:
                fields[env_key].insert(0, prefill[env_key])

    fields['steps'] = create_field("4. Steps to reproduce: *", is_multiline=True)
    fields['expected'] = create_field("5. Expected result: *", is_multiline=True)
    fields['actual'] = create_field("6. Actual result: *", is_multiline=True)

    tk.Label(scrollable_frame, text="7. Bug severity: *", anchor='w', 
            bg=COLORS['bg_primary'], fg=COLORS['text_primary'], 
            font=STYLES['font_body']).pack(anchor='w', padx=STYLES['padding_large'], pady=(STYLES['padding_medium'], 0), fill='x')
    severity_var = tk.StringVar(value="Minor")
    severity_dropdown = ttk.Combobox(
        scrollable_frame, textvariable=severity_var, values=SEVERITY_OPTIONS, state="readonly"
    )
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
                filename = copy_screenshot_to_folder(app.paths.screenshots_dir, screenshot_path, bug_title, i + 1)
                if filename:
                    bug_data["screenshots"].append(filename)

            # Load existing bugs (if file exists)
            if os.path.exists(app.paths.bugs_file):
                with open(app.paths.bugs_file, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
            else:
                bugs = []

            # Add new bug
            bugs.append(bug_data)

            # Save to file
            with open(app.paths.bugs_file, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            # Success info
            print("New bug saved:", bug_data)
            if bug_data["screenshots"]:
                print(f"📎 Saved {len(bug_data['screenshots'])} attachment(s)")

            # Close form
            app.load_bugs()
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
