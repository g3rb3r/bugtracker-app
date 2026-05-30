"""Bug detail / edit window."""
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

def open_bug_details(app, bug):

    detail_window = tk.Toplevel(app.root)
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
    set_active = app.scroll.register_canvas(canvas)
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

    severity_frame = tk.Frame(read_only_frame, bg=COLORS['bg_primary'])
    severity_frame.pack(anchor='w', fill='x', pady=(STYLES['padding_small'], 0))
    tk.Label(severity_frame, text="Severity:", font=STYLES['font_body'],
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, STYLES['padding_small']))
    current_severity = bug.get('severity') or 'Minor'
    severity_values = list(SEVERITY_OPTIONS)
    if current_severity not in severity_values:
        severity_values = [current_severity] + severity_values
    severity_var = tk.StringVar(value=current_severity)
    severity_dropdown = ttk.Combobox(
        severity_frame, textvariable=severity_var, values=severity_values, state='disabled', width=18
    )
    severity_dropdown.pack(side='left')

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
            screenshot_path = get_screenshot_path(app.paths.screenshots_dir, screenshot_filename)
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
    status_var = tk.StringVar(value=normalize_status(bug['status'], STATUS_MAP))
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
            severity_dropdown.config(state="readonly")
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
            severity_dropdown.config(state="disabled")
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
            # Restore original status and severity
            status_var.set(bug['status'])
            severity_var.set(bug.get('severity') or 'Minor')

    def save_changes():
        try:
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Validation error", "Bug title cannot be empty.")
                return
            if len(new_title) < 5:
                messagebox.showerror("Validation error", "Bug title must be at least 5 characters.")
                return

            new_severity = severity_var.get().strip()
            if not new_severity:
                messagebox.showerror("Validation error", "Please select bug severity.")
                return

            # Load all bugs
            with open(app.paths.bugs_file, "r", encoding="utf-8") as f:
                bugs = json.load(f)
                for b in bugs:
                    b['status'] = normalize_status(b.get('status', STATUS_MAP))
            # Find and update selected bug
            matched_bug = None
            for b in bugs:
                if (b['title'] == bug['title'] and b['environment'] == bug['environment']
                        and b.get('game_title', '') == bug.get('game_title', '')):
                    matched_bug = b
                    b['title'] = new_title
                    b['status'] = status_var.get()
                    b['severity'] = new_severity
                    b['steps'] = steps_text.get("1.0", tk.END).strip()
                    b['expected'] = expected_text.get("1.0", tk.END).strip()
                    b['actual'] = actual_text.get("1.0", tk.END).strip()
                    b['notes'] = notes_text.get("1.0", tk.END).strip()
                    if new_screenshots:
                        existing_count = len(b.get('screenshots', []))
                        for i, screenshot_path in enumerate(new_screenshots):
                            filename = copy_screenshot_to_folder(app.paths.screenshots_dir,
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
            with open(app.paths.bugs_file, "w", encoding="utf-8") as f:
                json.dump(bugs, f, indent=2, ensure_ascii=False)

            bug['title'] = new_title
            bug['status'] = matched_bug['status']
            bug['severity'] = matched_bug['severity']
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
            app.load_bugs()  # refresh bug list in the main window
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
                with open(app.paths.bugs_file, "r", encoding="utf-8") as f:
                    bugs = json.load(f)
                    for b in bugs:
                        b['status'] = normalize_status(b.get('status', STATUS_MAP))

                # Delete bug by title, environment, and game title
                bugs = [b for b in bugs if not (
                    b['title'] == bug['title'] and b['environment'] == bug['environment']
                    and b.get('game_title', '') == bug.get('game_title', '')
                )]

                with open(app.paths.bugs_file, "w", encoding="utf-8") as f:
                    json.dump(bugs, f, indent=2, ensure_ascii=False)

                print(f"Deleted bug: {bug['title']}")
                detail_window.destroy()
                app.load_bugs()

            except Exception as e:
                print("Error while deleting bug:", e)

    delete_btn = create_modern_button(buttons_center_frame, "Delete bug", delete_bug, 'error')
    delete_btn.pack(side='left', padx=STYLES['padding_small'])
