"""Bug database read/write helpers."""

import json
import os

from app.constants import ENV_FIELD_PREFIXES
from app.utils.text import normalize_status, normalized_game_title, parse_environment


def load_bugs_list(bugs_file):
    if not os.path.exists(bugs_file):
        return None
    with open(bugs_file, encoding="utf-8") as f:
        return json.load(f)


def save_bugs_list(bugs_file, bugs):
    with open(bugs_file, "w", encoding="utf-8") as f:
        json.dump(bugs, f, indent=2, ensure_ascii=False)


def normalize_bugs_statuses(bugs, status_map):
    for b in bugs:
        b["status"] = normalize_status(b.get("status"), status_map)


def get_game_prefill_data(bugs_file, game_title):
    prefill = {"game_title": game_title, **{key: "" for key in ENV_FIELD_PREFIXES}}
    bugs = load_bugs_list(bugs_file)
    if not bugs:
        return prefill
    title_key = normalized_game_title(game_title)
    game_bugs = [
        b for b in bugs
        if normalized_game_title(b.get("game_title")) == title_key
    ]
    if game_bugs:
        prefill.update(parse_environment(game_bugs[-1].get("environment", "")))
    return prefill


def bugs_match(a, b):
    return (
        a["title"] == b["title"]
        and a["environment"] == b["environment"]
        and a.get("game_title", "") == b.get("game_title", "")
    )
