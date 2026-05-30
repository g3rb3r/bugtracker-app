"""Global mouse wheel / keyboard scrolling for scrollable canvases."""

import tkinter as tk


def is_text_input_widget(widget):
    if widget is None:
        return False
    return widget.winfo_class() in {"Entry", "TEntry", "Text", "TCombobox", "Spinbox"}


class ScrollManager:
    def __init__(self, root: tk.Tk):
        self._root = root
        self._active_canvas = None
        self._bind_global_handlers()

    def register_canvas(self, canvas):
        def set_active(_event=None):
            self._active_canvas = canvas

        canvas.bind("<Enter>", set_active, add="+")
        canvas.bind("<Button-1>", set_active, add="+")
        return set_active

    def _scroll_units(self, delta):
        active = self._active_canvas
        if active is None or not active.winfo_exists():
            return
        active.yview_scroll(delta, "units")

    def _on_global_mousewheel(self, event):
        if event.delta:
            units = -1 if event.delta > 0 else 1
            self._scroll_units(units)

    def _on_global_arrow_scroll(self, event):
        if is_text_input_widget(event.widget):
            return
        key_to_units = {"Up": -1, "Down": 1, "Prior": -8, "Next": 8}
        units = key_to_units.get(event.keysym)
        if units:
            self._scroll_units(units)
            return "break"

    @staticmethod
    def _select_all_in_widget(event):
        widget = event.widget
        if widget.winfo_class() in {"Entry", "TEntry"}:
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        elif widget.winfo_class() == "Text":
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "end-1c")
        return "break"

    @staticmethod
    def _move_entry_by_word(event, direction, select=False):
        widget = event.widget
        text = widget.get()
        cursor = widget.index(tk.INSERT)
        if direction < 0:
            new_pos = cursor
            while new_pos > 0 and text[new_pos - 1].isspace():
                new_pos -= 1
            while new_pos > 0 and not text[new_pos - 1].isspace():
                new_pos -= 1
        else:
            new_pos = cursor
            text_len = len(text)
            while new_pos < text_len and text[new_pos].isspace():
                new_pos += 1
            while new_pos < text_len and not text[new_pos].isspace():
                new_pos += 1
        if select:
            anchor = widget.index("anchor") if widget.selection_present() else cursor
            widget.selection_range(min(anchor, new_pos), max(anchor, new_pos))
        else:
            widget.selection_clear()
        widget.icursor(new_pos)
        return "break"

    @staticmethod
    def _move_text_by_word(event, direction, select=False):
        widget = event.widget
        if direction < 0:
            target = widget.index("insert -1c wordstart")
        else:
            target = widget.index("insert wordend +1c")
        if select:
            if not widget.tag_ranges("sel"):
                widget.mark_set("anchor", "insert")
            widget.tag_remove("sel", "1.0", tk.END)
            widget.tag_add("sel", "anchor", target)
        else:
            widget.tag_remove("sel", "1.0", tk.END)
        widget.mark_set("insert", target)
        widget.see("insert")
        return "break"

    def _bind_global_handlers(self):
        root = self._root
        root.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        root.bind_all("<Button-4>", lambda _e: self._scroll_units(-1), add="+")
        root.bind_all("<Button-5>", lambda _e: self._scroll_units(1), add="+")
        for key in ("<Up>", "<Down>", "<Prior>", "<Next>"):
            root.bind_all(key, self._on_global_arrow_scroll, add="+")
        for class_name in ("Entry", "TEntry", "Text"):
            root.bind_class(class_name, "<Control-a>", self._select_all_in_widget, add="+")
            root.bind_class(class_name, "<Control-A>", self._select_all_in_widget, add="+")
        for class_name in ("Entry", "TEntry"):
            root.bind_class(class_name, "<Control-Left>", lambda e: self._move_entry_by_word(e, -1), add="+")
            root.bind_class(class_name, "<Control-Right>", lambda e: self._move_entry_by_word(e, 1), add="+")
            root.bind_class(
                class_name, "<Control-Shift-Left>",
                lambda e: self._move_entry_by_word(e, -1, select=True), add="+",
            )
            root.bind_class(
                class_name, "<Control-Shift-Right>",
                lambda e: self._move_entry_by_word(e, 1, select=True), add="+",
            )
        root.bind_class("Text", "<Control-Left>", lambda e: self._move_text_by_word(e, -1), add="+")
        root.bind_class("Text", "<Control-Right>", lambda e: self._move_text_by_word(e, 1), add="+")
        root.bind_class(
            "Text", "<Control-Shift-Left>",
            lambda e: self._move_text_by_word(e, -1, select=True), add="+",
        )
        root.bind_class(
            "Text", "<Control-Shift-Right>",
            lambda e: self._move_text_by_word(e, 1, select=True), add="+",
        )
