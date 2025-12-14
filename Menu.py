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
        elif answer == '1':
            pass
        else:
            print("Please choose an option from the menu")

if __name__ == "__main__":
    __main__()