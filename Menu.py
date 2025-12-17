from Wordle import *
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
                #updates based on return value of startGame() [not finished]
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
            pass
        
        else:
            print("Please choose an option from the menu")

if __name__ == "__main__":
    __main__()