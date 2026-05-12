"""
PreviousWordle.py
Parses previous_wordle_answers.txt into a structured calendar.
Provides lookup: (month, year) -> {day: answer}
"""
import os


class PreviousWordle:
    MONTH_ORDER = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December",
    ]

    def __init__(self):
        # calendar[(month, year_int)] = {day_int: "WORD"}
        self.calendar: dict[tuple, dict[int, str]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _load(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "previous_wordle_answers.txt")

        with open(path, "r") as f:
            lines = f.read().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("All") or line.startswith("Date"):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            try:
                month = parts[0]
                day = int(parts[1].replace(",", ""))
                year = int(parts[2])
                answer = parts[-1].upper()

                key = (month, year)
                if key not in self.calendar:
                    self.calendar[key] = {}
                self.calendar[key][day] = answer
            except (ValueError, IndexError):
                continue

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get_years(self) -> list[int]:
        """Return sorted list of years with data (descending)."""
        years = set(y for (_, y) in self.calendar)
        return sorted(years, reverse=True)

    def get_months_for_year(self, year: int) -> list[str]:
        """Return months (in calendar order) that have data for the given year."""
        months = [m for (m, y) in self.calendar if y == year]
        return sorted(months, key=lambda m: self.MONTH_ORDER.index(m))

    def get_days(self, month: str, year: int) -> dict[int, str]:
        """Return {day: answer} for the given month/year, or empty dict."""
        return self.calendar.get((month, year), {})

    def get_answer(self, month: str, year: int, day: int) -> str | None:
        """Return the answer word for a specific date, or None."""
        return self.calendar.get((month, year), {}).get(day)
