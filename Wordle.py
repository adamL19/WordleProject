import random

class InvalidWordException(Exception):
    pass

class LengthWordException(Exception):
    pass

class Wordle:
    HighestStreak = 0
    def __init__(self):
        self.streak = 0
        self.solution = None

    def addToStreak(self):
        self.streak += 1
    
    def resetStreak(self):
        self.streak = 0
    
    def updateHighscore(self):
        if self.streak > Wordle.HighestStreak:
            Wordle.HighestStreak = self.streak
        
    def printHighscore(self):
        print(f"Highest streak: {self.HighestStreak}")
    
    #checks if word is 5 letters OR in word list 
    def validGuess(self, guess): 
        with open ("valid_guesses.csv", 'r') as f:
            lines = f.read().splitlines()
            
        with open ("valid_solutions.csv", 'r') as f:
            lines2 = f.read().splitlines()

        lines.extend(lines2)
            
        if len(guess) != 5:
            raise LengthWordException("Use a 5 letter word")
            
        if guess not in lines:
            raise InvalidWordException("Use a real word")

    #reads data and picks a valid solution
    #sets solution as string
    def generateSolution(self): 
        with open("valid_solutions.csv", 'r') as f:
            
            lines = f.read().splitlines()
            self.solution = lines[random.randrange(0, len(lines))]
    
    #will run 6 times, one for each guess
    #generates the solution
    #returns win to add to streak in menu
    #restarts lost to reset streak in menu
    def startGame(self):
        self.generateSolution()

        print("\nTo go to menu, type menu")
        spaces = "__ __ __ __ __"
        print(spaces)
        spaces = spaces.split(" ")
        
        attempts = 1
        while attempts < 7:
            guess = input(f"\n\n [{attempts}] Your guess: ")

            if guess == 'menu':
                #Make sure highscore is updated
                #Make sure streak reset. Done with 'menu' prompt so it doesn't reset every new game
                self.updateHighscore()
                self.resetStreak()
                return None

            try:
                self.validGuess(guess)
            except (InvalidWordException, LengthWordException) as e:
                print("Error:", e)
                continue
                #gets a new input and doesn't use 1 of 6 guesses
            
            singleResult = self.singleCheck(guess)
            #check
            if singleResult == "win":
                print(f"\n Correct!, {guess} is the correct word!")
                return "win"
            
            rightSpot, wrongSpot = singleResult

            for letter, index in rightSpot.items():
                spaces[index] = letter

            stringSpaces = " ".join(spaces)
            print(f"{stringSpaces}\nWrong postions: {wrongSpot}")

            spaces = ["__", "__", "__", "__", "__"]
            
            attempts += 1
        #if while loop left, return lose
        print(f"\nThe word was {self.solution}")
        return "lose"
    
    #check guess with solution, returns True
    #creates a list of right letters wrong spots
    #creates dict of right letters right spots
    def singleCheck(self, input):
        if self.solution is None:
            raise RuntimeError("Solution not generated befyre singleCheck()")
        wrongSpot = []
        rightSpot = {}

        if input == self.solution:
            return "win"

        # Track how many times each letter appears in the solution
        solution_counts = {}
        for i in range(len(self.solution)):
            letter = self.solution[i]
            solution_counts[letter] = solution_counts.get(letter, 0) + 1

        # First pass: correct letter, correct spot
        # Key = letter, value = index
        for i in range(len(input)):
            if input[i] == self.solution[i]:
                rightSpot[input[i]] = i
                solution_counts[input[i]] -= 1

        # Second pass: correct letter, wrong spot
        for i in range(len(input)):
            # skip letters already in the correct spot
            if i in rightSpot.values():
                continue

            letter = input[i]
            if letter in solution_counts and solution_counts[letter] > 0:
                wrongSpot.append(letter)
                solution_counts[letter] -= 1

        return rightSpot, wrongSpot
            
            

        
