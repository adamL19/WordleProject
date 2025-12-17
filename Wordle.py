import random

class InvalidWordException(Exception):
    pass

class LongWordException(Exception):
    pass

class Wordle:
    HighestStreak = 0
    def __init__(self):
        self.streak = 0
        self.solution = Wordle.generateSolution(self)

    def addToStreak(self):
        self.streak += 1
    
    def resetStreak(self):
        self.streak = 0
    
    def updateHighscore(self):
        if self.streak > self.HighestStreak:
            self.HighestStreak = self.streak
        
    def printHighscore(self):
        print(f"Highest streak: {self.HighestStreak}")
    
    #checks if word is long OR in word list 
    def validGuess(self, guess): 
        with open ("valid_guesses.csv", 'r') as f:
            lines = f.read().splitlines()
            if guess not in lines:
                raise InvalidWordException("Use a real word")
            if len(guess) > 5:
                raise LongWordException("Use a 5 letter word")

    #reads data and pickes a valid solution
    #returns a LIST
    def generateSolution(self): 
        with open("valid_solutions.csv", 'r') as f:
            lines = f.read().splitlines()
            self.answer = list(lines[random.randrange(0, len(lines)+1)])
    
    #will run 6 times, one for each guess
    #generates the solution
    #returns win to add to streak in menu
    #restarts lost to reset streak in menu
    def startGame(self):
        print("To go to menu, type menu")
        spaces = ["__",  "__",  "__",  "__",  "__"]
        print(spaces)
        for i in range(0,7):
            guess = input("\n\nYour guess: ")
            if guess == 'menu':
                break #Add score streak here maybe?
            guess = list(guess)
    
    #check guess with solution
    #creates a list of right letters wrong spots
    #creates dict of right letters right spots
    def singleCheck(self, input):
        wrongSpot = []
        rightSpot = {}
        try:
            Wordle.validGuess(input)
        except InvalidWordException as e:
            print("Error:", e)
        except LongWordException as e:
            print("Error:", e)
        
        #check for proper position first (green)
        #can probably be written with an inside loop
        x = 0
        for i in self.solution:
            if i == input[x]:
                rightSpot[input[x]] = x
            x += 1
            
            
            
            

        
