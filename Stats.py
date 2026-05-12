"""
Stats.py
Manages local persistent statistics stored in wordle_stats.json.

Tracked data:
  - highest_streak      : int
  - current_streak      : int
  - unlimited_wins      : int
  - unlimited_losses    : int
  - guess_distribution  : {1: n, 2: n, 3: n, 4: n, 5: n, 6: n}
  - previous_solved     : {"Month Year Day": true}   e.g. "May 2025 11"
"""
import json
import os

STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordle_stats.json")

_DEFAULT = {
    "highest_streak": 0,
    "current_streak": 0,
    "unlimited_wins": 0,
    "unlimited_losses": 0,
    "guess_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0},
    "previous_solved": {},
}


def load() -> dict:
    """Load stats from file, creating it with defaults if missing."""
    if not os.path.exists(STATS_FILE):
        save(_DEFAULT.copy())
        return _DEFAULT.copy()
    with open(STATS_FILE, "r") as f:
        data = json.load(f)
    # Patch any missing keys (forward-compat)
    for k, v in _DEFAULT.items():
        if k not in data:
            data[k] = v
    return data


def save(data: dict):
    """Persist stats to file."""
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ------------------------------------------------------------------
# Mutation helpers
# ------------------------------------------------------------------

def record_win(guess_number: int):
    """Record an unlimited-mode win on guess #guess_number (1-6)."""
    data = load()
    data["unlimited_wins"] += 1
    data["current_streak"] += 1
    if data["current_streak"] > data["highest_streak"]:
        data["highest_streak"] = data["current_streak"]
    key = str(guess_number)
    data["guess_distribution"][key] = data["guess_distribution"].get(key, 0) + 1
    save(data)


def record_loss():
    """Record an unlimited-mode loss."""
    data = load()
    data["unlimited_losses"] += 1
    data["current_streak"] = 0
    save(data)


def record_previous_solved(month: str, year: int, day: int):
    """Mark a previous-wordle date as solved."""
    data = load()
    key = f"{month} {year} {day}"
    data["previous_solved"][key] = True
    save(data)


def is_previous_solved(month: str, year: int, day: int) -> bool:
    data = load()
    key = f"{month} {year} {day}"
    return data["previous_solved"].get(key, False)


def get_previous_solved_count() -> int:
    data = load()
    return len(data["previous_solved"])
