import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
import requests

# Create a SQLite database connection
conn = sqlite3.connect('spelly')
c = conn.cursor()

# Create a table for word management
c.execute('''CREATE TABLE IF NOT EXISTS words
             (word text PRIMARY KEY)''')
conn.commit()

class SpellyGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Spelly Game")
        self.window.geometry("400x400")

        # Fetch word list from URL and store as instance attribute
        word_list_url = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_list_url)
        self.word_list = [line.strip() for line in response.text.splitlines()]

        # Create a label for the current word
        self.current_word_label = tk.Label(self.window, text="", font=("Arial", 24))
        self.current_word_label.pack(pady=10)

        # Create an entry field for player input
        self.player_input_entry = tk.Entry(self.window, width=20)
        self.player_input_entry.pack(pady=10)

        # Create buttons for game actions
        self.create_buttons()

        # Create a label for the score display
        self.score_label = tk.Label(self.window, text="Score: 0", font=("Arial", 18))
        self.score_label.pack(pady=10)

        # Initialize game variables
        self.current_word = self.get_random_word()
        self.current_word_label['text'] = self.shuffle_word(self.current_word)
        self.player_score = 0
        self.computer_score = 0

        # Initialize SQLite in-memory database connection and create table
        self.setup_database()

        # Create a computer opponent using self.word_list
        self.computer_opponent = ComputerOpponent(self.word_list)

        # Start the game loop
        self.window.mainloop()

    def setup_database(self):
        try:
            # Create a SQLite in-memory database connection
            self.conn = sqlite3.connect(':memory:')
            self.c = self.conn.cursor()

            # Create a table for word management
            self.c.execute('''CREATE TABLE IF NOT EXISTS words
                              (id INTEGER PRIMARY KEY, word TEXT UNIQUE)''')
            self.conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"SQLite error: {e}")

    def create_buttons(self):
        # Create buttons for game actions
        submit_button = tk.Button(self.window, text="Submit", command=self.submit_player_input)
        submit_button.pack(pady=10)

        hint_button = tk.Button(self.window, text="Hint", command=self.show_hint)
        hint_button.pack(pady=10)

        add_word_button = tk.Button(self.window, text="Add Word", command=self.add_word)
        add_word_button.pack(pady=10)

        modify_view_button = tk.Button(self.window, text="Modify/View Words", command=self.modify_and_view_words)
        modify_view_button.pack(pady=10)

        delete_word_button = tk.Button(self.window, text="Delete Word", command=self.delete_word)
        delete_word_button.pack(pady=10)

    def add_word(self):
        new_word = self.player_input_entry.get().strip()
        if new_word:
            try:
                self.c.execute("INSERT INTO words (word) VALUES (?)", (new_word,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Added word: {new_word}")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Word '{new_word}' already exists in the database.")
        else:
            messagebox.showerror("Error", "Please enter a word to add.")

    def modify_and_view_words(self):
        def view_words():
            try:
                self.c.execute("SELECT * FROM words ORDER BY word")
                rows = self.c.fetchall()
                if rows:
                    word_list_str = "\n".join([f"{row[0]}. {row[1]}" for row in rows])
                    messagebox.showinfo("Words in Database", f"Words in database:\n{word_list_str}")
                else:
                    messagebox.showinfo("Empty Database", "No words found in the database.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error viewing words: {e}")

        def modify_word():
            old_word = self.player_input_entry.get().strip()
            new_word = self.get_random_word()  # Replace with desired logic for new word
            if old_word:
                try:
                    self.c.execute("UPDATE words SET word = ? WHERE word = ?", (new_word, old_word))
                    self.conn.commit()
                    messagebox.showinfo("Success", f"Updated word '{old_word}' to '{new_word}'")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error updating word: {e}")
            else:
                messagebox.showerror("Error", "Please enter a word to update.")

        choice = messagebox.askquestion("Modify or View Words", "Do you want to Modify or View words?")
        if choice == 'yes':
            view_words()
        else:
            modify_word()

    def delete_word(self):
        word_to_delete = self.player_input_entry.get().strip()
        if word_to_delete:
            try:
                self.c.execute("DELETE FROM words WHERE word = ?", (word_to_delete,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Deleted word: {word_to_delete}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting word: {e}")
        else:
            messagebox.showerror("Error", "Please enter a word to delete.")

    def get_random_word(self):
        return random.choice(self.word_list)

    def shuffle_word(self, word):
        return ''.join(random.sample(word, len(word)))

    def submit_player_input(self):
        player_input = self.player_input_entry.get()
        if player_input == self.current_word:
            self.player_score += 1
            self.score_label['text'] = f"Score: {self.player_score}"
            self.current_word = self.get_random_word()
            self.current_word_label['text'] = self.shuffle_word(self.current_word)
        elif player_input in self.word_list:
            messagebox.showinfo("Correct", "Correct spelling!")
        else:
            messagebox.showerror("Error", "Incorrect input!")

    def show_hint(self):
        hint = self.computer_opponent.get_hint(self.current_word)
        messagebox.showinfo("Hint", hint)

class ComputerOpponent:
    def __init__(self, word_list):
        self.word_list = word_list

    # Methods for AI-driven opponent
    def get_hint(self, word):
        # Implement hint logic here
        return f"Hint: First letter is '{word[0]}'"

    def get_input(self, word):
        # Implement opponent's input logic here
        return random.choice(self.word_list)

def main():
    game = SpellyGame()

if __name__ == "__main__":
    main()

