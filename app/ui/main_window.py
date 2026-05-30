"""Main application window."""

import json
import os

import tkinter as tk
from tkinter import ttk

from app.config import load_config
from app.constants import (
    COLORS,
    GAME_FILTER_ALL,
    GAME_FILTER_NO_TITLE,
    STATUS_MAP,
    STYLES,
)
from app.ui.bug_details import open_bug_details
from app.ui.bug_form import open_bug_form
from app.ui.reports import generate_game_report
from app.ui.scroll import ScrollManager
from app.ui.theme import create_modern_button
from app.utils.text import normalize_status, normalized_game_title


class BugTrackerApp:
    def __init__(self):
        self.config = load_config()
        self.paths = self.config.paths
        self.root = tk.Tk()
        self.scroll = ScrollManager(self.root)
        self.tab_scroll_canvases = []
        self._tab_panels = {}
        self._tab_buttons = {}
        self._build_ui()

    def run(self):
        self.load_bugs()
        self.update_report_button_state()
        self.root.mainloop()

    def _build_ui(self):
        win = self.config.window
        self.root.title(win.title)
        self.root.geometry(f"{win.width}x{win.height}")
        self.root.configure(bg=COLORS["bg_primary"])
        self.root.minsize(win.min_width, win.min_height)

        header_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        header_frame.pack(fill="x", padx=STYLES["padding_large"], pady=STYLES["padding_medium"])
        tk.Label(
            header_frame, text="🐛 Bug Tracker", font=STYLES["font_heading"],
            bg=COLORS["bg_primary"], fg=COLORS["text_primary"],
        ).pack(side="left")
        tk.Label(
            header_frame, text="QA Panel - Bug Management", font=STYLES["font_body"],
            bg=COLORS["bg_primary"], fg=COLORS["text_secondary"],
        ).pack(side="left", padx=(STYLES["padding_medium"], 0), pady=(5, 0))

        self.game_filter_var = tk.StringVar(value=GAME_FILTER_ALL)
        filter_bar = tk.Frame(self.root, bg=COLORS["bg_primary"])
        filter_bar.pack(fill="x", padx=STYLES["padding_large"], pady=(0, STYLES["padding_small"]))
        tk.Label(
            filter_bar, text="Filter by game:", font=STYLES["font_body"],
            bg=COLORS["bg_primary"], fg=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, STYLES["padding_small"]))
        self.game_filter_combo = ttk.Combobox(
            filter_bar, textvariable=self.game_filter_var, state="readonly", width=48,
        )
        self.game_filter_combo.pack(side="left", fill="x", expand=True)

        notebook_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        notebook_frame.pack(fill="both", expand=True, padx=STYLES["padding_large"], pady=STYLES["padding_small"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "GameFilter.TCombobox",
            fieldbackground=COLORS["bg_tertiary"],
            background=COLORS["bg_secondary"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_primary"],
        )
        style.map(
            "GameFilter.TCombobox",
            fieldbackground=[("readonly", COLORS["bg_tertiary"])],
            selectbackground=[("readonly", COLORS["accent_blue"])],
            selectforeground=[("readonly", COLORS["text_primary"])],
        )
        self.game_filter_combo.configure(style="GameFilter.TCombobox")

        tabs_header = tk.Frame(notebook_frame, bg=COLORS["bg_primary"])
        tabs_header.pack(fill="x", pady=(0, 2))
        tabs_content = tk.Frame(notebook_frame, bg=COLORS["bg_secondary"])
        tabs_content.pack(fill="both", expand=True)

        self.tab_all = tk.Frame(tabs_content, bg=COLORS["bg_secondary"])
        self.tab_in_progress = tk.Frame(tabs_content, bg=COLORS["bg_secondary"])
        self.tab_done = tk.Frame(tabs_content, bg=COLORS["bg_secondary"])
        self._tab_panels = {
            "all": self.tab_all,
            "in_progress": self.tab_in_progress,
            "done": self.tab_done,
        }

        tab_btn_options = {
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "padx": STYLES["padding_medium"],
            "pady": STYLES["padding_small"],
            "font": STYLES["font_body"],
            "cursor": "hand2",
        }
        for tab_key, tab_label in (
            ("all", "📋 All"),
            ("in_progress", "🛠️ In Progress"),
            ("done", "✅ Completed"),
        ):
            btn = tk.Button(
                tabs_header,
                text=tab_label,
                command=lambda k=tab_key: self.show_status_tab(k),
                **tab_btn_options,
            )
            btn.pack(side="left")
            self._tab_buttons[tab_key] = btn

        self.tab_all_content = self._create_scrollable_tab(self.tab_all)
        self.tab_in_progress_content = self._create_scrollable_tab(self.tab_in_progress)
        self.tab_done_content = self._create_scrollable_tab(self.tab_done)
        self.show_status_tab("all")

        actions_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        actions_frame.pack(pady=STYLES["padding_medium"])
        tk.Button(
            actions_frame, text="Add new bug", command=lambda: open_bug_form(self),
            bg=COLORS["accent_blue"], fg=COLORS["text_primary"],
            font=STYLES["font_body"], padx=STYLES["padding_medium"],
            pady=STYLES["padding_small"], relief="flat",
            activebackground=COLORS["accent_green"],
            activeforeground=COLORS["text_primary"],
        ).pack(side="left", padx=(0, STYLES["padding_small"]))
        self.report_btn = tk.Button(
            actions_frame, text="Generate game report",
            command=lambda: generate_game_report(self),
            bg=COLORS["bg_tertiary"], fg=COLORS["text_primary"],
            font=STYLES["font_body"], padx=STYLES["padding_medium"],
            pady=STYLES["padding_small"], relief="flat",
            activebackground=COLORS["success"],
            activeforeground=COLORS["text_primary"],
        )
        self.report_btn.pack(side="left", padx=(STYLES["padding_small"], 0))

        self.game_filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: (self.load_bugs(), self.update_report_button_state()),
        )

    def _style_status_tab_button(self, btn, selected):
        if selected:
            btn.configure(
                bg=COLORS["accent_blue"], fg=COLORS["text_primary"],
                activebackground=COLORS["accent_blue"], activeforeground=COLORS["text_primary"],
            )
        else:
            btn.configure(
                bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                activebackground=COLORS["bg_secondary"], activeforeground=COLORS["text_primary"],
            )

    def show_status_tab(self, key):
        for tab_key, panel in self._tab_panels.items():
            if tab_key == key:
                panel.pack(fill="both", expand=True)
                self._style_status_tab_button(self._tab_buttons[tab_key], True)
            else:
                panel.pack_forget()
                self._style_status_tab_button(self._tab_buttons[tab_key], False)
        self.refresh_tab_scrollregions()

    def _create_scrollable_tab(self, parent_tab):
        canvas = tk.Canvas(parent_tab, bg=COLORS["bg_secondary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent_tab, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=COLORS["bg_secondary"])

        def on_content_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        content_frame.bind("<Configure>", on_content_configure)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        set_active = self.scroll.register_canvas(canvas)
        content_frame.bind("<Enter>", set_active, add="+")
        self.tab_scroll_canvases.append(canvas)
        return content_frame

    def refresh_tab_scrollregions(self):
        self.root.update_idletasks()
        for canvas in self.tab_scroll_canvases:
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)

    def update_report_button_state(self):
        selected_game = (self.game_filter_var.get() or "").strip()
        if selected_game and selected_game not in {GAME_FILTER_ALL, GAME_FILTER_NO_TITLE}:
            self.report_btn.config(state="normal", bg=COLORS["success"])
        else:
            self.report_btn.config(state="disabled", bg=COLORS["bg_tertiary"])

    def load_bugs(self):
        self.update_report_button_state()
        for tab in (self.tab_all_content, self.tab_in_progress_content, self.tab_done_content):
            for widget in tab.winfo_children():
                widget.destroy()

        def reset_game_filter_choices():
            self.game_filter_combo["values"] = (GAME_FILTER_ALL,)
            self.game_filter_var.set(GAME_FILTER_ALL)

        def apply_game_filter(all_bugs):
            titles = set()
            has_empty_title = False
            for b in all_bugs:
                gt = (b.get("game_title") or "").strip()
                if gt:
                    titles.add(gt)
                else:
                    has_empty_title = True
            options = [GAME_FILTER_ALL] + sorted(titles)
            if has_empty_title:
                options.append(GAME_FILTER_NO_TITLE)
            self.game_filter_combo["values"] = options
            sel = self.game_filter_var.get()
            if sel not in options:
                match = next(
                    (o for o in options
                     if o not in (GAME_FILTER_ALL, GAME_FILTER_NO_TITLE)
                     and normalized_game_title(o) == normalized_game_title(sel)),
                    None,
                )
                if match:
                    sel = match
                    self.game_filter_var.set(match)
                else:
                    self.game_filter_var.set(GAME_FILTER_ALL)
                    sel = GAME_FILTER_ALL
            if sel == GAME_FILTER_ALL:
                return all_bugs
            if sel == GAME_FILTER_NO_TITLE:
                return [b for b in all_bugs if not (b.get("game_title") or "").strip()]
            sel_key = normalized_game_title(sel)
            return [
                b for b in all_bugs
                if normalized_game_title(b.get("game_title")) == sel_key
            ]

        def create_bug_card(parent, bug):
            frame = tk.Frame(
                parent, bg=COLORS["bg_tertiary"], relief="flat",
                bd=STYLES["border_width"], highlightbackground=COLORS["border"],
                highlightthickness=STYLES["border_width"],
            )
            frame.pack(fill="x", padx=STYLES["padding_medium"], pady=STYLES["padding_small"])
            title = tk.Label(
                frame, text=f"{bug['title']}", font=STYLES["font_subheading"],
                anchor="w", cursor="hand2", wraplength=600, justify="left",
                bg=COLORS["bg_tertiary"], fg=COLORS["text_primary"],
            )
            title.pack(fill="x", padx=STYLES["padding_medium"], pady=(STYLES["padding_small"], 0))
            title.bind("<Button-1>", lambda e, b=bug: open_bug_details(self, b))
            gt = (bug.get("game_title") or "").strip()
            if gt:
                game_line = tk.Label(
                    frame, text=f"{gt}", font=STYLES["font_small"],
                    anchor="w", cursor="hand2", wraplength=600, justify="left",
                    fg=COLORS["accent_green"], bg=COLORS["bg_tertiary"],
                )
                game_line.pack(fill="x", padx=STYLES["padding_medium"], pady=(0, 0))
                game_line.bind("<Button-1>", lambda e, b=bug: open_bug_details(self, b))
            tk.Label(
                frame, text=f"Severity: {bug['severity']} | Status: {bug['status']}",
                font=STYLES["font_small"], fg=COLORS["text_secondary"], anchor="w",
                bg=COLORS["bg_tertiary"],
            ).pack(fill="x", padx=STYLES["padding_medium"], pady=(0, STYLES["padding_small"]))

        if not os.path.exists(self.paths.bugs_file):
            reset_game_filter_choices()
            for tab in (self.tab_all_content, self.tab_in_progress_content, self.tab_done_content):
                tk.Label(
                    tab, text="No bug file found",
                    fg=COLORS["text_muted"], bg=COLORS["bg_secondary"], font=STYLES["font_body"],
                ).pack(pady=STYLES["padding_large"])
            return

        try:
            with open(self.paths.bugs_file, encoding="utf-8") as f:
                bugs = json.load(f)
            for b in bugs:
                b["status"] = normalize_status(b.get("status"), STATUS_MAP)
        except Exception as e:
            reset_game_filter_choices()
            for tab in (self.tab_all_content, self.tab_in_progress_content, self.tab_done_content):
                tk.Label(
                    tab, text=f"Error while loading bugs: {e}",
                    fg=COLORS["error"], bg=COLORS["bg_secondary"], font=STYLES["font_body"],
                ).pack(pady=STYLES["padding_large"])
            return

        filtered = apply_game_filter(bugs)

        if not bugs:
            for tab in (self.tab_all_content, self.tab_in_progress_content, self.tab_done_content):
                tk.Label(
                    tab, text="No reported bugs",
                    fg=COLORS["text_muted"], bg=COLORS["bg_secondary"], font=STYLES["font_body"],
                ).pack(pady=STYLES["padding_large"])
            return

        if not filtered:
            for tab in (self.tab_all_content, self.tab_in_progress_content, self.tab_done_content):
                tk.Label(
                    tab, text="No bugs match this game filter",
                    fg=COLORS["text_muted"], bg=COLORS["bg_secondary"], font=STYLES["font_body"],
                ).pack(pady=STYLES["padding_large"])
            return

        for bug in filtered:
            create_bug_card(self.tab_all_content, bug)
            if bug["status"] == "In Progress":
                create_bug_card(self.tab_in_progress_content, bug)
            elif bug["status"] == "Completed":
                create_bug_card(self.tab_done_content, bug)

        self.refresh_tab_scrollregions()
