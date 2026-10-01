import random
from words import WORDS, HINTS
from stats import SessionStats

DIFFICULTIES = {
    "easy":   {"lives": 8, "multiplier": 1.0, "hint_penalty": 1},
    "medium": {"lives": 6, "multiplier": 1.5, "hint_penalty": 2},
    "hard":   {"lives": 4, "multiplier": 2.0, "hint_penalty": 3},
}


class HangmanGame:
    def __init__(self):
        self.score = 0
        self.streak = 0
        self.category = "technology"
        self.difficulty = "medium"
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 6
        self.hint_used = False
        self.stats = SessionStats()

    def start_round(self):
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."
        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."
        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        if self.hint_used:
            return None
        self.hint_used = True
        penalty = DIFFICULTIES[self.difficulty]["hint_penalty"]
        self.score = max(0, self.score - penalty)
        return HINTS.get(self.secret, "No hint available.")

    def play_round(self):
        self.start_round()
        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print("Lives:", self.lives, "Score:", self.score, "Streak:", self.streak)
            raw = input("Letter, /hint, or /quit: ").strip().lower()
            if raw == "/quit":
                return False
            if raw == "/hint":
                hint = self.use_hint()
                print(hint if hint else "Hint already used.")
                continue
            print(self.guess(raw))

        if self.won():
            self.streak += 1
            mult = DIFFICULTIES[self.difficulty]["multiplier"]
            base = 5 + self.streak
            earned = int(base * mult)
            if self.hint_used:
                earned = max(1, earned - DIFFICULTIES[self.difficulty]["hint_penalty"])
            self.score += earned
            print(f"Solved: {self.secret} (+{earned} points)")
            self.stats.record(True, self.streak)
            return True

        self.streak = 0
        print("Out of lives. The word was:", self.secret)
        self.stats.record(False, self.streak)
        return True

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        while True:
            print("\nCategories:", ", ".join(WORDS))
            raw = input("Choose category or q: ").strip().lower()
            if raw == "q":
                return
            if raw not in WORDS:
                print("Unknown category.")
                continue
            self.category = raw

            print("Difficulties:", ", ".join(DIFFICULTIES))
            diff = input("Choose difficulty [easy/medium/hard]: ").strip().lower()
            if diff in DIFFICULTIES:
                self.difficulty = diff
            else:
                print(f"Unknown difficulty. Using {self.difficulty}.")
            if not self.play_round():
                return
            again = input("Another round? [y/n]: ").strip().lower()
            if again != "y":
                print("\n--- Session Summary ---")
                print("Final score:", self.score)
                print("Current streak:", self.streak)
                print("Rounds played:", self.stats.rounds)
                print("Rounds won:", self.stats.wins)
                print("Best streak:", self.stats.best_streak)
                return
