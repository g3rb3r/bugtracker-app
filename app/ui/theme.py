"""Shared UI styling helpers."""

import tkinter as tk

from app.constants import COLORS, STYLES


def create_modern_button(parent, text, command, button_type="primary"):
    colors = {
        "primary": {"bg": COLORS["accent_blue"], "active_bg": COLORS["accent_green"]},
        "success": {"bg": COLORS["success"], "active_bg": COLORS["accent_green"]},
        "danger": {"bg": COLORS["error"], "active_bg": COLORS["accent_red"]},
        "warning": {"bg": COLORS["warning"], "active_bg": COLORS["accent_orange"]},
        "secondary": {"bg": COLORS["bg_tertiary"], "active_bg": COLORS["border_hover"]},
    }
    btn_colors = colors.get(button_type, colors["primary"])
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=btn_colors["bg"],
        fg=COLORS["text_primary"],
        font=STYLES["font_body"],
        padx=STYLES["padding_medium"],
        pady=STYLES["padding_small"],
        relief="flat",
        activebackground=btn_colors["active_bg"],
        activeforeground=COLORS["text_primary"],
        cursor="hand2",
    )
