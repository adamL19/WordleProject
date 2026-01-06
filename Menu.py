from Wordle import *
from PreviousWordle import *
def welcome():
    print("\nWelcome to Wordle Expansion. Please choose what you want to play:")
    print("\n  Previous Wordles (1)")
    print("  Unlimited Version (2)")
    print("  Quit (3)")
    return input("\n")

def __main__():
    answer = welcome()

    while True:
        if answer == '3':
            print("\nBye!")
            break

        elif answer == '2':
            w = Wordle()

            while True:
                result = w.startGame()
                #updates based on return value of startGame()
                if result == "win":
                    w.addToStreak()
                    w.updateHighscore()
                elif result == "lose":
                    w.resetStreak()
                    w.printHighscore()
                elif result is None:
                    w.printHighscore()
                    break

            answer = welcome()

        elif answer == '1':
            pw = PreviousWordle()
            pw.createCalendar()
            print(pw)

            month = input("Enter month (e.g. December): ")
            year = int(input("Enter year: "))

            print(pw.printWordleMonth(month, year))
            input("Press Enter to return to menu...")
            answer = welcome()

        else:
            print("Please choose an option from the menu")

if __name__ == "__main__":
    __main__()