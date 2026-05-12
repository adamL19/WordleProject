"""
Menu.py  —  Wordle Project GUI
Entry point. Run this file to launch the application.

Requires: Python 3.10+, tkinter (bundled with standard Python installs),
          matplotlib  (pip install matplotlib)

File structure expected in the same directory:
  valid_guesses.csv
  valid_solutions.csv
  previous_wordle_answers.txt
  Wordle.py
  PreviousWordle.py
  Stats.py
"""

import tkinter as tk
from tkinter import font as tkfont
import sys
import os

# Make sure sibling modules are importable when run from any cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Wordle import Wordle, InvalidWordException, LengthWordException
from PreviousWordle import PreviousWordle
import Stats

# ──────────────────────────────────────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────────────────────────────────────
C = {
    "bg":        "#121213",   # page background
    "surface":   "#1a1a1b",   # card / panel background
    "border":    "#3a3a3c",   # tile border (empty)
    "absent":    "#3a3a3c",   # grey key / tile
    "present":   "#b59f3b",   # yellow
    "correct":   "#538d4e",   # green
    "text":      "#ffffff",
    "subtext":   "#818384",
    "btn":       "#538d4e",
    "btn_hover": "#6aaf61",
    "btn2":      "#3a3a3c",
    "btn2_hover":"#565758",
    "key_text":  "#ffffff",
    "tile_empty":"#121213",
    "tile_fill": "#121213",
    "header":    "#1a1a1b",
    "divider":   "#3a3a3c",
    "warn":      "#b59f3b",
    "error":     "#cf4a4a",
    "gold":      "#f5c518",
}

FONT_TITLE   = ("Helvetica", 28, "bold")
FONT_SUB     = ("Helvetica", 13)
FONT_TILE    = ("Helvetica", 22, "bold")
FONT_KEY     = ("Helvetica", 11, "bold")
FONT_BTN     = ("Helvetica", 13, "bold")
FONT_BTN_SM  = ("Helvetica", 11, "bold")
FONT_LABEL   = ("Helvetica", 12)
FONT_SMALL   = ("Helvetica", 10)

TILE_SIZE    = 62
TILE_GAP     = 6
KEY_W        = 40
KEY_H        = 56
KEY_GAP      = 6


# ──────────────────────────────────────────────────────────────────────────────
# Reusable widget helpers
# ──────────────────────────────────────────────────────────────────────────────

def styled_button(parent, text, command, width=18, style="primary", font=FONT_BTN):
    bg     = C["btn"]       if style == "primary" else C["btn2"]
    hov    = C["btn_hover"] if style == "primary" else C["btn2_hover"]
    btn = tk.Button(
        parent, text=text, command=command,
        font=font, bg=bg, fg=C["text"],
        activebackground=hov, activeforeground=C["text"],
        relief="flat", bd=0, cursor="hand2",
        padx=16, pady=10, width=width,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


# ──────────────────────────────────────────────────────────────────────────────
# Tile grid widget
# ──────────────────────────────────────────────────────────────────────────────

class TileGrid(tk.Frame):
    """6×5 grid of letter tiles."""

    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._tiles = []   # list of rows; each row = list of (frame, label)
        self._build()

    def _build(self):
        for r in range(6):
            row = []
            for c in range(5):
                f = tk.Frame(self, width=TILE_SIZE, height=TILE_SIZE,
                             bg=C["tile_empty"], highlightthickness=2,
                             highlightbackground=C["border"])
                f.grid(row=r, column=c, padx=TILE_GAP//2, pady=TILE_GAP//2)
                f.grid_propagate(False)
                lbl = tk.Label(f, text="", font=FONT_TILE,
                               bg=C["tile_empty"], fg=C["text"])
                lbl.place(relx=0.5, rely=0.5, anchor="center")
                row.append((f, lbl))
            self._tiles.append(row)

    def set_letter(self, row, col, letter):
        f, lbl = self._tiles[row][col]
        lbl.config(text=letter.upper())
        f.config(highlightbackground=C["subtext"])

    def color_row(self, row, result):
        """Color a completed row from singleCheck result list."""
        status_map = {
            "correct": C["correct"],
            "present": C["present"],
            "absent":  C["absent"],
        }
        for letter, col, status in result:
            f, lbl = self._tiles[row][col]
            bg = status_map[status]
            f.config(bg=bg, highlightbackground=bg)
            lbl.config(bg=bg, fg=C["text"])

    def color_row_win(self, row, word):
        """Color all tiles green for a winning row."""
        for col in range(5):
            f, lbl = self._tiles[row][col]
            f.config(bg=C["correct"], highlightbackground=C["correct"])
            lbl.config(bg=C["correct"], fg=C["text"],
                       text=word[col].upper())

    def reset(self):
        for row in self._tiles:
            for f, lbl in row:
                f.config(bg=C["tile_empty"], highlightbackground=C["border"])
                lbl.config(text="", bg=C["tile_empty"])


# ──────────────────────────────────────────────────────────────────────────────
# On-screen keyboard widget
# ──────────────────────────────────────────────────────────────────────────────

KEYBOARD_ROWS = [
    list("qwertyuiop"),
    list("asdfghjkl"),
    list("zxcvbnm"),
]


class KeyboardWidget(tk.Frame):
    """Visual keyboard showing letter status. Non-interactive (display only)."""

    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._keys: dict[str, tk.Label] = {}
        self._build()

    def _build(self):
        for r, row_letters in enumerate(KEYBOARD_ROWS):
            row_frame = tk.Frame(self, bg=C["bg"])
            row_frame.pack(pady=KEY_GAP // 2)
            for ch in row_letters:
                lbl = tk.Label(
                    row_frame, text=ch.upper(),
                    font=FONT_KEY, bg=C["border"], fg=C["key_text"],
                    width=3, height=2, relief="flat",
                )
                lbl.pack(side="left", padx=KEY_GAP // 2)
                self._keys[ch] = lbl

    def update_key(self, letter: str, status: str):
        """
        status: "correct" | "present" | "absent"
        Correct overrides present overrides absent (never downgrade).
        """
        ch = letter.lower()
        if ch not in self._keys:
            return
        lbl = self._keys[ch]
        current_bg = lbl.cget("bg")
        priority = {C["correct"]: 3, C["present"]: 2, C["absent"]: 1, C["border"]: 0}
        new_bg = {"correct": C["correct"], "present": C["present"], "absent": C["absent"]}[status]
        if priority.get(new_bg, 0) > priority.get(current_bg, 0):
            lbl.config(bg=new_bg)

    def reset(self):
        for lbl in self._keys.values():
            lbl.config(bg=C["border"])


# ──────────────────────────────────────────────────────────────────────────────
# Shared Wordle board (used by both Unlimited and Previous modes)
# ──────────────────────────────────────────────────────────────────────────────

class WordleBoard(tk.Frame):
    """
    Self-contained Wordle board: grid + keyboard + input + message.
    Calls on_win(guess_number) or on_lose() when game ends.
    """

    def __init__(self, parent, wordle: Wordle,
                 on_win=None, on_lose=None, on_back=None,
                 mode_label="Unlimited Mode"):
        super().__init__(parent, bg=C["bg"])
        self.wordle   = wordle
        self.on_win   = on_win
        self.on_lose  = on_lose
        self.on_back  = on_back
        self.current_row = 0
        self.game_over   = False
        self._build(mode_label)

    def _build(self, mode_label):
        # Header bar
        hdr = tk.Frame(self, bg=C["header"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=mode_label, font=("Helvetica", 15, "bold"),
                 bg=C["header"], fg=C["text"]).pack(side="left", padx=16)
        if self.on_back:
            styled_button(hdr, "← Menu", self.on_back,
                          width=8, style="secondary", font=FONT_BTN_SM
                          ).pack(side="right", padx=8)

        # Grid
        grid_frame = tk.Frame(self, bg=C["bg"], pady=12)
        grid_frame.pack()
        self.grid_widget = TileGrid(grid_frame)
        self.grid_widget.pack()

        # Message
        self.msg_var = tk.StringVar()
        tk.Label(self, textvariable=self.msg_var,
                 font=("Helvetica", 12, "bold"), bg=C["bg"],
                 fg=C["warn"], height=2).pack()

        # Keyboard
        kb_frame = tk.Frame(self, bg=C["bg"], pady=6)
        kb_frame.pack()
        self.keyboard = KeyboardWidget(kb_frame)
        self.keyboard.pack()

        # Input row
        inp_frame = tk.Frame(self, bg=C["bg"], pady=12)
        inp_frame.pack()
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            inp_frame, textvariable=self.entry_var,
            font=("Helvetica", 18, "bold"),
            width=8, justify="center",
            bg=C["surface"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            highlightthickness=2, highlightbackground=C["border"],
            highlightcolor=C["correct"],
        )
        self.entry.pack(side="left", padx=8, ipady=6)
        self.entry.bind("<Return>", lambda e: self._submit())
        self.entry.bind("<KeyRelease>", self._cap_input)
        self.entry.focus_set()

        styled_button(inp_frame, "Guess", self._submit, width=8).pack(side="left")

    # ------------------------------------------------------------------

    def _cap_input(self, event=None):
        val = self.entry_var.get().upper()[:5]
        self.entry_var.set(val)

    def _submit(self):
        if self.game_over:
            return
        guess = self.entry_var.get().strip().lower()
        self.entry_var.set("")

        try:
            self.wordle.validGuess(guess)
        except LengthWordException:
            self.msg_var.set("Word must be 5 letters.")
            return
        except InvalidWordException:
            self.msg_var.set("Not in word list.")
            return

        self.msg_var.set("")

        result = self.wordle.singleCheck(guess)

        if result == "win":
            self.grid_widget.color_row_win(self.current_row, guess)
            self.keyboard.update_key(ch, "correct") if False else None
            for ch in guess:
                self.keyboard.update_key(ch, "correct")
            self.game_over = True
            guess_num = self.current_row + 1
            self.msg_var.set(f"🎉  Correct in {guess_num}!  The word was {guess.upper()}")
            self.entry.config(state="disabled")
            if self.on_win:
                self.on_win(guess_num)
        else:
            # Fill tiles with letters first
            for letter, col, status in result:
                self.grid_widget.set_letter(self.current_row, col, letter)

            # Delay coloring for a subtle reveal feel
            self.after(100, lambda r=result: self._color_and_update_kb(r))
            self.current_row += 1

            if self.current_row >= 6:
                self.game_over = True
                self.msg_var.set(f"The word was  {self.wordle.solution.upper()}")
                self.entry.config(state="disabled")
                if self.on_lose:
                    self.on_lose()

    def _color_and_update_kb(self, result):
        row = self.current_row - 1
        self.grid_widget.color_row(row, result)
        for letter, col, status in result:
            self.keyboard.update_key(letter, status)

    def reset(self, new_wordle: Wordle):
        self.wordle      = new_wordle
        self.current_row = 0
        self.game_over   = False
        self.msg_var.set("")
        self.entry_var.set("")
        self.entry.config(state="normal")
        self.grid_widget.reset()
        self.keyboard.reset()
        self.entry.focus_set()


# ──────────────────────────────────────────────────────────────────────────────
# Unlimited Mode view
# ──────────────────────────────────────────────────────────────────────────────

class UnlimitedView(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg=C["bg"])
        self.on_back      = on_back
        self.wordle       = Wordle()
        self.wordle.generateSolution()
        self.board        = None
        self._build()

    def _build(self):
        self.board = WordleBoard(
            self, self.wordle,
            on_win  = self._on_win,
            on_lose = self._on_lose,
            on_back = self.on_back,
            mode_label="Unlimited Mode",
        )
        self.board.pack(fill="both", expand=True)

    def _on_win(self, guess_number):
        Stats.record_win(guess_number)
        self._show_end_buttons()

    def _on_lose(self):
        Stats.record_loss()
        self._show_end_buttons()

    def _show_end_buttons(self):
        btn_frame = tk.Frame(self, bg=C["bg"], pady=8)
        btn_frame.pack()
        styled_button(btn_frame, "New Word", self._new_game,
                      width=12).pack(side="left", padx=6)
        styled_button(btn_frame, "← Menu", self.on_back,
                      width=12, style="secondary").pack(side="left", padx=6)

    def _new_game(self):
        # Remove any end-buttons frames
        for w in self.winfo_children():
            if w is not self.board:
                w.destroy()
        new_wordle = Wordle()
        new_wordle.generateSolution()
        self.board.reset(new_wordle)


# ──────────────────────────────────────────────────────────────────────────────
# Previous Wordle views
# ──────────────────────────────────────────────────────────────────────────────

class PreviousYearView(tk.Frame):
    """Top level: pick a year."""

    def __init__(self, parent, pw: PreviousWordle, on_back, on_select_year):
        super().__init__(parent, bg=C["bg"])
        self.pw             = pw
        self.on_back        = on_back
        self.on_select_year = on_select_year
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Previous Wordles", font=("Helvetica", 15, "bold"),
                 bg=C["header"], fg=C["text"]).pack(side="left", padx=16)
        styled_button(hdr, "← Menu", self.on_back,
                      width=8, style="secondary", font=FONT_BTN_SM
                      ).pack(side="right", padx=8)

        tk.Label(self, text="Select a Year", font=("Helvetica", 20, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(30, 10))
        tk.Label(self, text="Browse previous Wordle puzzles by date.",
                 font=FONT_SUB, bg=C["bg"], fg=C["subtext"]).pack(pady=(0, 24))

        btn_frame = tk.Frame(self, bg=C["bg"])
        btn_frame.pack()

        for year in self.pw.get_years():
            y = year  # capture
            styled_button(btn_frame, str(y),
                          lambda yr=y: self.on_select_year(yr),
                          width=10).pack(pady=5)


class PreviousMonthView(tk.Frame):
    """Pick a month within a year."""

    def __init__(self, parent, pw: PreviousWordle, year: int,
                 on_back, on_select_month):
        super().__init__(parent, bg=C["bg"])
        self.pw              = pw
        self.year            = year
        self.on_back         = on_back
        self.on_select_month = on_select_month
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Previous Wordles — {self.year}",
                 font=("Helvetica", 15, "bold"),
                 bg=C["header"], fg=C["text"]).pack(side="left", padx=16)
        styled_button(hdr, "← Years", self.on_back,
                      width=8, style="secondary", font=FONT_BTN_SM
                      ).pack(side="right", padx=8)

        tk.Label(self, text="Select a Month", font=("Helvetica", 20, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(30, 10))

        grid = tk.Frame(self, bg=C["bg"])
        grid.pack(pady=10)

        months = self.pw.get_months_for_year(self.year)
        for i, month in enumerate(months):
            m = month
            btn = styled_button(grid, m,
                                lambda mo=m: self.on_select_month(mo),
                                width=12)
            btn.grid(row=i // 3, column=i % 3, padx=8, pady=5)


class PreviousDayView(tk.Frame):
    """Calendar grid of days for a month — click a day to play."""

    def __init__(self, parent, pw: PreviousWordle, year: int, month: str,
                 on_back, on_select_day):
        super().__init__(parent, bg=C["bg"])
        self.pw            = pw
        self.year          = year
        self.month         = month
        self.on_back       = on_back
        self.on_select_day = on_select_day
        self._build()

    def _build(self):
        from datetime import date

        hdr = tk.Frame(self, bg=C["header"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{self.month} {self.year}",
                 font=("Helvetica", 15, "bold"),
                 bg=C["header"], fg=C["text"]).pack(side="left", padx=16)
        styled_button(hdr, "← Months", self.on_back,
                      width=8, style="secondary", font=FONT_BTN_SM
                      ).pack(side="right", padx=8)

        tk.Label(self, text="Select a Day", font=("Helvetica", 18, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(20, 4))

        # Legend
        leg = tk.Frame(self, bg=C["bg"])
        leg.pack(pady=(0, 10))
        tk.Label(leg, text="■", fg=C["correct"], bg=C["bg"],
                 font=("Helvetica", 12)).pack(side="left", padx=4)
        tk.Label(leg, text="Solved", fg=C["subtext"], bg=C["bg"],
                 font=FONT_SMALL).pack(side="left", padx=(0, 12))
        tk.Label(leg, text="■", fg=C["btn"], bg=C["bg"],
                 font=("Helvetica", 12)).pack(side="left", padx=4)
        tk.Label(leg, text="Available", fg=C["subtext"], bg=C["bg"],
                 font=FONT_SMALL).pack(side="left")

        days_data = self.pw.get_days(self.month, self.year)

        # Calendar header
        cal_frame = tk.Frame(self, bg=C["bg"])
        cal_frame.pack(padx=20, pady=4)

        day_names = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for col, dn in enumerate(day_names):
            tk.Label(cal_frame, text=dn, font=("Helvetica", 10, "bold"),
                     bg=C["bg"], fg=C["subtext"], width=4).grid(row=0, column=col)

        month_names = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December",
        ]
        month_index = month_names.index(self.month) + 1
        first_day   = date(self.year, month_index, 1)
        start_col   = (first_day.weekday() + 1) % 7  # Sunday = 0

        col = start_col
        row = 1
        for day in sorted(days_data.keys()):
            d = day
            solved = Stats.is_previous_solved(self.month, self.year, d)
            bg  = C["correct"] if solved else C["btn"]
            hov = C["btn_hover"] if not solved else C["correct"]
            lbl_text = f"{d}\n{'✓' if solved else ''}"

            btn = tk.Button(
                cal_frame, text=lbl_text,
                font=("Helvetica", 10, "bold"),
                bg=bg, fg=C["text"],
                activebackground=hov, activeforeground=C["text"],
                relief="flat", bd=0, cursor="hand2",
                width=3, height=2,
                command=lambda day_=d: self.on_select_day(day_),
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 6:
                col = 0
                row += 1


class PreviousPlayView(tk.Frame):
    """Play a specific previous Wordle puzzle."""

    def __init__(self, parent, pw: PreviousWordle,
                 year: int, month: str, day: int,
                 on_back, on_back_to_days):
        super().__init__(parent, bg=C["bg"])
        self.pw           = pw
        self.year         = year
        self.month        = month
        self.day          = day
        self.on_back      = on_back        # back to day picker
        self.on_back_menu = on_back_to_days

        answer = pw.get_answer(month, year, day)
        self.wordle = Wordle()
        self.wordle.setSolution(answer)
        self._already_solved = Stats.is_previous_solved(month, year, day)
        self._build()

    def _build(self):
        label = f"{self.month} {self.day}, {self.year}"
        self.board = WordleBoard(
            self, self.wordle,
            on_win   = self._on_win,
            on_lose  = self._on_lose,
            on_back  = self.on_back,
            mode_label=f"Previous Wordle — {label}",
        )
        self.board.pack(fill="both", expand=True)

        if self._already_solved:
            banner = tk.Frame(self, bg=C["correct"], pady=6)
            banner.pack(fill="x")
            tk.Label(banner,
                     text="✓  You've already solved this one — play again for fun!",
                     font=("Helvetica", 11, "bold"),
                     bg=C["correct"], fg=C["text"]).pack()

    def _on_win(self, guess_number):
        if not self._already_solved:
            Stats.record_previous_solved(self.month, self.year, self.day)
            self._already_solved = True
        self._show_end_buttons()

    def _on_lose(self):
        self._show_end_buttons()

    def _show_end_buttons(self):
        btn_frame = tk.Frame(self, bg=C["bg"], pady=8)
        btn_frame.pack()
        styled_button(btn_frame, "← Back to Days", self.on_back,
                      width=14, style="secondary").pack(side="left", padx=6)
        styled_button(btn_frame, "← Menu", self.on_back_menu,
                      width=10, style="secondary").pack(side="left", padx=6)


# ──────────────────────────────────────────────────────────────────────────────
# Stats View
# ──────────────────────────────────────────────────────────────────────────────

class StatsView(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg=C["bg"])
        self.on_back = on_back
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Statistics", font=("Helvetica", 15, "bold"),
                 bg=C["header"], fg=C["text"]).pack(side="left", padx=16)
        styled_button(hdr, "← Menu", self.on_back,
                      width=8, style="secondary", font=FONT_BTN_SM
                      ).pack(side="right", padx=8)

        data = Stats.load()

        # Summary row
        summary = tk.Frame(self, bg=C["bg"], pady=20)
        summary.pack()

        def stat_box(parent, value, label):
            f = tk.Frame(parent, bg=C["surface"], padx=20, pady=14,
                         highlightthickness=1, highlightbackground=C["border"])
            f.pack(side="left", padx=10)
            tk.Label(f, text=str(value), font=("Helvetica", 32, "bold"),
                     bg=C["surface"], fg=C["gold"]).pack()
            tk.Label(f, text=label, font=FONT_SMALL,
                     bg=C["surface"], fg=C["subtext"]).pack()

        total_played = data["unlimited_wins"] + data["unlimited_losses"]
        win_pct = (
            int(data["unlimited_wins"] / total_played * 100)
            if total_played else 0
        )

        stat_box(summary, total_played,                "Played")
        stat_box(summary, f"{win_pct}%",               "Win %")
        stat_box(summary, data["current_streak"],      "Current\nStreak")
        stat_box(summary, data["highest_streak"],      "Max\nStreak")
        stat_box(summary, Stats.get_previous_solved_count(), "Previous\nSolved")

        tk.Label(self, text="Guess Distribution",
                 font=("Helvetica", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(10, 6))

        self._draw_distribution(data["guess_distribution"])

    def _draw_distribution(self, dist: dict):
        """Draw a horizontal bar chart using tkinter Canvas."""
        total = sum(dist.values()) or 1
        max_val = max(dist.values()) if any(dist.values()) else 1

        container = tk.Frame(self, bg=C["bg"])
        container.pack(padx=40, pady=4, fill="x")

        bar_max_px = 260

        for guess_num in range(1, 7):
            count = dist.get(str(guess_num), 0)
            bar_w = max(30, int((count / max_val) * bar_max_px)) if max_val else 30

            row = tk.Frame(container, bg=C["bg"], pady=3)
            row.pack(fill="x")

            tk.Label(row, text=str(guess_num), font=("Helvetica", 12, "bold"),
                     bg=C["bg"], fg=C["text"], width=2).pack(side="left")

            bar_frame = tk.Frame(row, bg=C["correct"],
                                 width=bar_w, height=26)
            bar_frame.pack(side="left", padx=(4, 0))
            bar_frame.pack_propagate(False)

            tk.Label(bar_frame, text=str(count),
                     font=("Helvetica", 11, "bold"),
                     bg=C["correct"], fg=C["text"]).pack(
                side="right", padx=6, pady=3)


# ──────────────────────────────────────────────────────────────────────────────
# Main Menu View
# ──────────────────────────────────────────────────────────────────────────────

class MenuView(tk.Frame):
    def __init__(self, parent,
                 on_unlimited, on_previous, on_stats, on_exit):
        super().__init__(parent, bg=C["bg"])
        self._build(on_unlimited, on_previous, on_stats, on_exit)

    def _build(self, on_unlimited, on_previous, on_stats, on_exit):
        # Top spacer
        tk.Frame(self, bg=C["bg"], height=60).pack()

        # Title
        tk.Label(self, text="Welcome to my project",
                 font=FONT_TITLE, bg=C["bg"], fg=C["text"]).pack()

        tk.Frame(self, bg=C["divider"], height=2, width=320).pack(pady=14)

        # Subtitle
        tk.Label(self, text="choose a game mode",
                 font=("Helvetica", 14), bg=C["bg"],
                 fg=C["subtext"]).pack(pady=(0, 30))

        # Buttons
        for label, cmd, style in [
            ("Unlimited Mode",  on_unlimited, "primary"),
            ("Previous Mode",   on_previous,  "primary"),
            ("Statistics",      on_stats,     "secondary"),
            ("Exit",            on_exit,      "secondary"),
        ]:
            styled_button(self, label, cmd, width=20, style=style).pack(pady=6)

        # Footer streak display
        tk.Frame(self, bg=C["bg"], height=30).pack()
        data = Stats.load()
        streak_text = (
            f"Current Streak: {data['current_streak']}   "
            f"Best: {data['highest_streak']}"
        )
        tk.Label(self, text=streak_text, font=FONT_SMALL,
                 bg=C["bg"], fg=C["subtext"]).pack()


# ──────────────────────────────────────────────────────────────────────────────
# Application shell
# ──────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    """Root window. Manages view switching via a single content frame."""

    def __init__(self):
        super().__init__()
        self.title("Wordle Project")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.geometry("560x780")

        self._pw = PreviousWordle()   # loaded once

        # Navigation state for Previous mode
        self._prev_year  = None
        self._prev_month = None

        self._content: tk.Frame | None = None
        self._show_menu()

    # ------------------------------------------------------------------
    # View transitions
    # ------------------------------------------------------------------

    def _swap(self, new_frame: tk.Frame):
        if self._content:
            self._content.destroy()
        self._content = new_frame
        self._content.pack(fill="both", expand=True)

    def _show_menu(self):
        self._swap(MenuView(
            self,
            on_unlimited = self._show_unlimited,
            on_previous  = self._show_previous_years,
            on_stats     = self._show_stats,
            on_exit      = self.destroy,
        ))

    def _show_unlimited(self):
        self._swap(UnlimitedView(self, on_back=self._show_menu))

    def _show_stats(self):
        self._swap(StatsView(self, on_back=self._show_menu))

    # Previous Wordle navigation chain
    def _show_previous_years(self):
        self._swap(PreviousYearView(
            self, self._pw,
            on_back        = self._show_menu,
            on_select_year = self._show_previous_months,
        ))

    def _show_previous_months(self, year: int):
        self._prev_year = year
        self._swap(PreviousMonthView(
            self, self._pw, year,
            on_back          = self._show_previous_years,
            on_select_month  = self._show_previous_days,
        ))

    def _show_previous_days(self, month: str):
        self._prev_month = month
        self._swap(PreviousDayView(
            self, self._pw, self._prev_year, month,
            on_back        = lambda: self._show_previous_months(self._prev_year),
            on_select_day  = self._show_previous_play,
        ))

    def _show_previous_play(self, day: int):
        self._swap(PreviousPlayView(
            self, self._pw,
            self._prev_year, self._prev_month, day,
            on_back        = lambda: self._show_previous_days(self._prev_month),
            on_back_to_days= self._show_menu,
        ))


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
