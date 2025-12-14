import random

class InvalidWord(Exception):
    pass
class LongWord(Exception):
    pass

class Wordle:
    HighestStreak = 0
    def __init__(self):
        self.streak = 0
        self.answer = None

    def validGuess(self, guess):
        with open ("valid_guesses.csv", 'r') as f:
            lines = f.read().splitlines()
            if guess not in lines:
                raise InvalidWord("Use a real word")
            if len(guess) > 5:
                raise LongWord("Use a 5 letter word")
        return guess

    def generateSolution(self): #reads data and pickes a valid solution
        with open("valid_solutions.csv", 'r') as f:
            lines = f.read().splitlines()
            self.answer = list(lines[random.randrange(0, len(lines)+1)])
    
    def startGame(self):
        while True:
            print("To end game, type q or quit")
            guess = input("\n\nYour guess: ")
            if guess == 'q' or guess == 'quit':
                break #Add score streak here maybe?
            guess = list(guess)
    
    def singleGame(self, solution):
        solution = Wordle.generateSolution()
        print("__  __  __  __  __")
        for i in random.randint(0,5):
            x = list(input("\nPut guess here: "))
            if Wordle.validGuess(x) != x:
                x = list(input("\nPut guess here: "))

        
