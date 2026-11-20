import json
import os
from pathlib import Path


APP_NAME = "Vista"

DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "output_width": 1500,
    "output_height": 250,
    "min_font_size": 12,
    "max_font_size": 120,
    "transparent_output": True,
    "background_color": "#000000",
}


def load_settings():
    settings = DEFAULT_SETTINGS.copy()

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf8") as f:
                loaded = json.load(f)

            if isinstance(loaded, dict):
                settings.update(loaded)
        except (OSError, json.JSONDecodeError):
            pass

    return normalize_settings(settings)


def save_settings(settings):
    normalized = normalize_settings(settings)

    with open(SETTINGS_FILE, "w", encoding="utf8") as f:
        json.dump(normalized, f, indent=2)

    return normalized


def normalize_settings(settings):
    normalized = DEFAULT_SETTINGS.copy()
    normalized.update(settings)

    normalized["output_width"] = clamp_int(normalized["output_width"], 200, 10000)
    normalized["output_height"] = clamp_int(normalized["output_height"], 100, 10000)
    normalized["min_font_size"] = clamp_int(normalized["min_font_size"], 6, 300)
    normalized["max_font_size"] = clamp_int(normalized["max_font_size"], 6, 300)

    if normalized["min_font_size"] > normalized["max_font_size"]:
        normalized["max_font_size"] = normalized["min_font_size"]

    normalized["transparent_output"] = bool(normalized["transparent_output"])

    color = str(normalized["background_color"])
    if not color.startswith("#") or len(color) not in (4, 7, 9):
        color = DEFAULT_SETTINGS["background_color"]
    normalized["background_color"] = color

    return normalized


def clamp_int(value, minimum, maximum):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = minimum

    return max(minimum, min(maximum, value))
