"""Text and filename helpers."""

from app.constants import ENV_FIELD_PREFIXES


def normalize_status(status, status_map):
    return status_map.get(status, status or "In Progress")


def normalized_game_title(title):
    return (title or "").strip().casefold()


def safe_filename(value):
    allowed = {" ", "-", "_"}
    sanitized = "".join(c for c in value if c.isalnum() or c in allowed).strip()
    return sanitized.replace(" ", "_") or "report"


def parse_environment(env_str):
    result = {key: "" for key in ENV_FIELD_PREFIXES}
    if not env_str:
        return result
    for line in env_str.splitlines():
        line = line.strip()
        for key, prefix in ENV_FIELD_PREFIXES.items():
            if line.startswith(prefix):
                result[key] = line[len(prefix) :].strip()
                break
    return result
