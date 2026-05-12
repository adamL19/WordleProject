"""
Wordle.py
Core game logic: word validation, solution generation, and guess checking.
Used by both Unlimited Mode and Previous Wordle Mode.
"""
import random
import os


class InvalidWordException(Exception):
    pass


class LengthWordException(Exception):
    pass


class Wordle:
    """Handles word loading, validation, and guess evaluation."""

    def __init__(self):
        self.solution = None
        self._valid_words = None  # cached word set

    # ------------------------------------------------------------------
    # Word loading
    # ------------------------------------------------------------------

    def _load_words(self):
        """Load and cache all valid words (guesses + solutions)."""
        if self._valid_words is not None:
            return self._valid_words

        base = os.path.dirname(os.path.abspath(__file__))
        words = set()

        for fname in ("valid_guesses.csv", "valid_solutions.csv"):
            path = os.path.join(base, fname)
            with open(path, "r") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        words.add(w)

        self._valid_words = words
        return words

    def _load_solutions(self):
        """Return list of valid solution words."""
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "valid_solutions.csv")
        with open(path, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]

    # ------------------------------------------------------------------
    # Game operations
    # ------------------------------------------------------------------

    def generateSolution(self):
        """Pick a random word from the solutions list."""
        solutions = self._load_solutions()
        self.solution = random.choice(solutions)

    def setSolution(self, word: str):
        """Set a specific solution (used by Previous Wordle mode)."""
        self.solution = word.lower()

    def validGuess(self, guess: str):
        """Raise an exception if the guess is not valid."""
        guess = guess.strip().lower()
        if len(guess) != 5:
            raise LengthWordException("Word must be 5 letters.")
        if guess not in self._load_words():
            raise InvalidWordException("Not a valid word.")

    def singleCheck(self, guess: str):
        """
        Evaluate a guess against self.solution.

        Returns:
            "win"  — if guess == solution
            list of (letter, index, status) tuples where status is:
                "correct"  — right letter, right position  (green)
                "present"  — right letter, wrong position  (yellow)
                "absent"   — letter not in word            (grey)
        """
        guess = guess.strip().lower()

        if guess == self.solution:
            return "win"

        result = [None] * 5
        solution_counts = {}
        for ch in self.solution:
            solution_counts[ch] = solution_counts.get(ch, 0) + 1

        # First pass: correct positions
        for i in range(5):
            if guess[i] == self.solution[i]:
                result[i] = (guess[i], i, "correct")
                solution_counts[guess[i]] -= 1

        # Second pass: present / absent
        for i in range(5):
            if result[i] is not None:
                continue
            ch = guess[i]
            if ch in solution_counts and solution_counts[ch] > 0:
                result[i] = (ch, i, "present")
                solution_counts[ch] -= 1
            else:
                result[i] = (ch, i, "absent")

        return result
