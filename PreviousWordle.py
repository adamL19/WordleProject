'''Creates dictionaries of all previous worlde answers
    will remember how many have been solved'''
from Wordle import *
from datetime import date

class PreviousWordle:
    def __init__(self):
        self.calendar = {}

    #create dictionaries of dictionaries
    def createCalendar(self):
        with open("previous_wordle_answers.txt", "r") as f:
            lines = f.read().splitlines()

        # Skip header lines if present
        for line in lines:
            # Skip empty lines or titles
            if not line or line.startswith("All") or line.startswith("Date"):
                continue

            # Split by whitespace
            parts = line.split()

            month = parts[0]
            day = int(parts[1].replace(",", ""))  # remove comma
            year = parts[2]
            number = parts[3] #probably unused
            answer = parts[-1]

            month_year = f"{month} {year}"

            # Create month dict if it doesn't exist
            if month_year not in self.calendar:
                self.calendar[month_year] = {}

            # Store day → answer
            self.calendar[month_year][day] = answer

    #format days accurately
    def printWordleMonth(self, month, year):
        month_names = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        month_index = month_names.index(month) + 1
        month_year = f"{month} {year}"

        if month_year not in self.calendar:
            return "No Wordle data for this month.\n"

        days_with_wordle = self.calendar[month_year]

        result = ""
        result += f"{month} {year}".center(20) + "\n"
        result += "Su Mo Tu We Th Fr Sa\n"

        first_day = date(year, month_index, 1)
        start_day = (first_day.weekday() + 1) % 7  # Sunday = 0

        result += "   " * start_day

        for day in range(1, 32):
            if day in days_with_wordle:
                result += f"{day:2} "
            else:
                result += "   "

            start_day += 1
            if start_day % 7 == 0:
                result += "\n"

        result += "\n"
        return result


    #print all previous month with year
    def __str__(self):
        month_order = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        years = {}
        for month_year in self.calendar:
            month, year = month_year.split()
            year = int(year)
            years.setdefault(year, []).append(month)

        result = "Previous Wordles\n\n"

        for year in sorted(years.keys(), reverse=True):
            result += f"{year}\n  "
            months_sorted = sorted(
                years[year],
                key=lambda m: month_order.index(m),
                reverse=True
            )

            for i, month in enumerate(months_sorted, 1):
                result += f"{month:<10} "
                if i % 4 == 0:
                    result += "\n  "
            result += "\n\n"

        return result

