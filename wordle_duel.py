#!/usr/bin/env python3
"""
Wordle Duel — Play Wordle against an AI opponent!

A standalone CLI game where you and an AI take turns guessing
a secret 5-letter word. Whoever guesses in fewer tries wins!

Usage:
    python wordle_duel.py           # Start a game (Normal difficulty)
    python wordle_duel.py --easy    # Easy mode (8 guesses)
    python wordle_duel.py --hard    # Hard mode (4 guesses)
    python wordle_duel.py --stats   # View your lifetime statistics
    python wordle_duel.py --reset   # Reset statistics

Features:
    - 🟩🟨⬜ Color-coded feedback
    - ⌨️  Live keyboard tracker
    - 📊 Persistent statistics (win rate, streak, guess distribution)
    - 💡 Hint system (reveal a correct letter)
    - 🎮 Difficulty levels (Easy/Normal/Hard)
    - 📖 Word definition reveal after each round
"""

import json
import os
import random
import sys
import textwrap
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Word list — common 5-letter English words
# ---------------------------------------------------------------------------
WORD_LIST = [
    "apple", "brave", "crane", "dance", "eagle", "flame", "grape", "house",
    "image", "juice", "knife", "lemon", "mango", "night", "ocean", "piano",
    "queen", "river", "stone", "tiger", "ultra", "vivid", "water", "young",
    "zebra", "beach", "cloud", "dream", "earth", "fresh", "ghost", "happy",
    "ivory", "jewel", "light", "magic", "noble", "olive", "peace", "quest",
    "royal", "solar", "truth", "unity", "voice", "world", "amber", "black",
    "crisp", "delta", "elite", "frost", "hover", "input", "karma", "lunar",
    "marsh", "nexus", "orbit", "prism", "quilt", "rusty", "swift", "turbo",
    "urban", "vault", "whirl", "brick", "charm", "dwarf", "exile", "giant",
    "heart", "index", "jolly", "kneel", "mount", "nerve", "omega", "plumb",
    "quiet", "rival", "storm", "tower", "vivid", "wheat", "yield", "zesty",
    "adapt", "blaze", "crown", "drift", "ember", "flint", "grain", "haste",
    "inlet", "joust", "knack", "lodge", "merit", "niche", "onset", "pluck",
    "quote", "roast", "sleek", "thorn", "usher", "vigor", "wrist", "yearn",
    "zonal", "align", "brisk", "champ", "dodge", "equip", "forge", "glyph",
    "haven", "irony", "jewel", "kiosk", "latch", "mirth", "nudge", "oasis",
    "pixel", "quirk", "reign", "shale", "tramp", "unify", "valor", "widen",
    "oxide", "yacht", "zones", "avert", "badge", "cider", "drape", "epoch",
    "flask", "glide", "heron", "ivory", "judge", "kayak", "lunar", "mocha",
    "naval", "olive", "pouch", "quota", "raven", "swirl", "trend", "ultra",
    "vocal", "wager", "xenon", "youth", "zippy", "angel", "bloom", "coral",
    "daisy", "flora", "grove", "hazel", "jazzy", "kinky", "llama", "moose",
    "nymph", "otter", "panda", "quail", "robin", "sloth", "tapir", "umbra",
    "viper", "whale", "xerus", "yodel", "zebus",
]

# Deduplicate while preserving order
seen = set()
WORD_LIST = [w for w in WORD_LIST if not (w in seen or seen.add(w))]

# ---------------------------------------------------------------------------
# Difficulty settings
# ---------------------------------------------------------------------------
DIFFICULTIES = {
    "easy":   {"guesses": 8, "label": "🟢 Easy (8 guesses)"},
    "normal": {"guesses": 6, "label": "🟡 Normal (6 guesses)"},
    "hard":   {"guesses": 4, "label": "🔴 Hard (4 guesses)"},
}

# ---------------------------------------------------------------------------
# Statistics file
# ---------------------------------------------------------------------------
STATS_FILE = Path.home() / ".wordle_duel_stats.json"


def load_stats() -> dict:
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "games_played": 0,
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "current_streak": 0,
        "best_streak": 0,
        "guess_distribution": {str(i): 0 for i in range(1, 9)},
        "difficulty_breakdown": {"easy": 0, "normal": 0, "hard": 0},
        "last_played": None,
    }


def save_stats(stats: dict):
    STATS_FILE.write_text(json.dumps(stats, indent=2))


def reset_stats():
    if STATS_FILE.exists():
        STATS_FILE.unlink()
    print("📊 Statistics reset!")


def display_stats(stats: dict):
    print("\n" + "=" * 45)
    print("📊  WORDLE DUEL — LIFETIME STATISTICS")
    print("=" * 45)
    played = stats["games_played"]
    if played == 0:
        print("  No games played yet. Start playing!")
        print("=" * 45 + "\n")
        return

    win_pct = (stats["wins"] / played) * 100
    print(f"  Games Played:    {played}")
    print(f"  Wins:            {stats['wins']} ({win_pct:.1f}%)")
    print(f"  Losses:          {stats['losses']}")
    print(f"  Draws:           {stats['draws']}")
    print(f"  Current Streak:  {stats['current_streak']} 🔥")
    print(f"  Best Streak:     {stats['best_streak']} 🏆")
    print()
    print("  Guess Distribution:")
    max_count = max(stats["guess_distribution"].values(), default=0)
    for guess_num in range(1, 9):
        count = stats["guess_distribution"].get(str(guess_num), 0)
        bar_len = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"    {guess_num}: {bar} {count}")
    print()
    diff = stats["difficulty_breakdown"]
    print(f"  By Difficulty:  🟢 Easy: {diff['easy']}  🟡 Normal: {diff['normal']}  🔴 Hard: {diff['hard']}")
    print(f"  Last Played:    {stats['last_played'] or 'N/A'}")
    print("=" * 45 + "\n")


# ---------------------------------------------------------------------------
# Color / emoji helpers
# ---------------------------------------------------------------------------
try:
    _tty = sys.stdout.isatty()
except Exception:
    _tty = False

USE_COLOR = _tty

# ANSI codes
GREEN_BG = "\033[42m\033[30m" if USE_COLOR else ""
YELLOW_BG = "\033[43m\033[30m" if USE_COLOR else ""
GRAY_BG = "\033[100m\033[37m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""
BOLD = "\033[1m" if USE_COLOR else ""


def color_letter(letter: str, status: str) -> str:
    """Return a letter wrapped in the appropriate color."""
    letter = letter.upper()
    if status == "green":
        return f"{GREEN_BG} {letter} {RESET}"
    elif status == "yellow":
        return f"{YELLOW_BG} {letter} {RESET}"
    elif status == "gray":
        return f"{GRAY_BG} {letter} {RESET}"
    return f" {letter} "


def emoji_feedback(statuses: list[str]) -> str:
    """Return emoji-only feedback string."""
    mapping = {"green": "🟩", "yellow": "🟨", "gray": "⬜"}
    return "".join(mapping[s] for s in statuses)


# ---------------------------------------------------------------------------
# Core game logic
# ---------------------------------------------------------------------------
def evaluate_guess(secret: str, guess: str) -> list[str]:
    """
    Compare guess against secret and return per-letter statuses.
    'green' = correct position, 'yellow' = wrong position, 'gray' = not in word.
    """
    assert len(secret) == len(guess) == 5
    statuses = ["gray"] * 5
    secret_remaining: list[str | None] = list(secret)

    # First pass: mark greens
    for i in range(5):
        if guess[i] == secret[i]:
            statuses[i] = "green"
            secret_remaining[i] = None

    # Second pass: mark yellows
    for i in range(5):
        if statuses[i] == "green":
            continue
        if guess[i] in secret_remaining:
            statuses[i] = "yellow"
            secret_remaining[secret_remaining.index(guess[i])] = None

    return statuses


def is_valid_word(word: str) -> bool:
    """Check if a word is a valid 5-letter English word."""
    if len(word) != 5 or not word.isalpha():
        return False
    return word.lower() in WORD_LIST


# ---------------------------------------------------------------------------
# Keyboard tracker
# ---------------------------------------------------------------------------
def display_keyboard(letter_status: dict[str, str]):
    """Show keyboard with color-coded letter statuses."""
    rows = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM",
    ]
    status_order = {"green": 0, "yellow": 1, "gray": 2, "unknown": 3}
    status_colors = {
        "green": GREEN_BG,
        "yellow": YELLOW_BG,
        "gray": GRAY_BG,
        "unknown": "",
    }

    print("  ⌨️  Keyboard:")
    for row in rows:
        line = "     "
        for ch in row:
            st = letter_status.get(ch, "unknown")
            bg = status_colors[st]
            if bg:
                line += f"{bg} {ch} {RESET}"
            else:
                line += f" {ch} "
            line += " "
        print(line)
    print()


# ---------------------------------------------------------------------------
# AI opponent
# ---------------------------------------------------------------------------
class WordleAI:
    """AI opponent that makes educated guesses."""

    def __init__(self, word_list: list[str]):
        self.original_list = list(word_list)
        self.candidates = list(word_list)
        self.green: dict[int, str] = {}       # position -> letter
        self.yellow: dict[int, set[str]] = {}  # position -> letters that can't be here
        self.yellow_all: set[str] = set()      # letters that must appear somewhere
        self.gray: set[str] = set()            # letters not in word
        self.guesses: list[str] = []

    def filter_candidates(self):
        """Narrow down candidates based on accumulated knowledge."""
        new_candidates = []
        for word in self.candidates:
            ok = True

            # Check green constraints
            for pos, letter in self.green.items():
                if word[pos] != letter:
                    ok = False
                    break
            if not ok:
                continue

            # Check yellow constraints (letter must exist, but not at known-bad positions)
            word_letters = set(word)
            for letter in self.yellow_all:
                if letter not in word_letters:
                    ok = False
                    break
            if not ok:
                continue

            for pos, bad_letters in self.yellow.items():
                for bl in bad_letters:
                    if word[pos] == bl:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue

            # Check gray constraints
            for letter in self.gray:
                # A letter might be gray but also yellow/green (duplicate letters)
                if letter in self.green.values() or letter in self.yellow_all:
                    continue
                if letter in word:
                    ok = False
                    break
            if not ok:
                continue

            new_candidates.append(word)

        if new_candidates:
            self.candidates = new_candidates

    def learn(self, guess: str, statuses: list[str]):
        """Update knowledge from a guess and its feedback."""
        letter_count_in_secret: dict[str, int] = {}

        for i, (letter, status) in enumerate(zip(guess, statuses)):
            if status == "green":
                self.green[i] = letter
                letter_count_in_secret[letter] = letter_count_in_secret.get(letter, 0) + 1
            elif status == "yellow":
                self.yellow.setdefault(i, set()).add(letter)
                self.yellow_all.add(letter)
                letter_count_in_secret[letter] = letter_count_in_secret.get(letter, 0) + 1
            else:  # gray
                # Only truly gray if not also green/yellow
                pass

        # Handle gray: letter is gray only if we haven't confirmed it elsewhere
        for i, (letter, status) in enumerate(zip(guess, statuses)):
            if status == "gray":
                if letter not in self.green.values() and letter not in self.yellow_all:
                    self.gray.add(letter)

        self.filter_candidates()

    def guess(self) -> str:
        """Make a guess. Pick from candidates, preferring common-ish words."""
        if not self.candidates:
            # Fallback: pick any unused word from original list
            remaining = [w for w in self.original_list if w not in self.guesses]
            if remaining:
                choice = random.choice(remaining)
            else:
                choice = random.choice(self.original_list)
            self.guesses.append(choice)
            return choice

        # Prefer candidates that haven't been guessed
        fresh = [w for w in self.candidates if w not in self.guesses]
        pool = fresh if fresh else self.candidates
        choice = random.choice(pool)
        self.guesses.append(choice)
        return choice


# ---------------------------------------------------------------------------
# Word definition (free dictionary API)
# ---------------------------------------------------------------------------
def get_word_definition(word: str) -> str | None:
    """Fetch word definition from the Free Dictionary API."""
    try:
        import urllib.request
        import json as _json
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
        req = urllib.request.Request(url, headers={"User-Agent": "WordleDuel/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = _json.loads(resp.read().decode())
            meanings = data[0].get("meanings", [])
            if meanings:
                defs = meanings[0].get("definitions", [])
                if defs:
                    return defs[0].get("definition", "")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Game round
# ---------------------------------------------------------------------------
def play_round(secret: str, difficulty: str, stats: dict) -> str:
    """
    Play one round. Returns 'player', 'ai', or 'draw'.
    """
    max_guesses = DIFFICULTIES[difficulty]["guesses"]
    ai = WordleAI(WORD_LIST)

    # Track letter statuses for keyboard
    letter_status: dict[str, str] = {}

    player_guesses = 0
    ai_guesses = 0
    player_hints = 0
    max_hints = 1 if difficulty != "hard" else 0

    print(f"\n🎯 I'm thinking of a 5-letter word...")
    print(f"📏 Difficulty: {DIFFICULTIES[difficulty]['label']}")
    print(f"💡 Hints available: {max_hints}")
    print(f"📝 Type 'hint' for a hint, 'quit' to give up.\n")

    player_board: list[tuple[str, list[str]]] = []
    ai_board: list[tuple[str, list[str]]] = []

    turn = 0  # 0 = player, 1 = ai
    while True:
        # Check if both exhausted guesses
        if player_guesses >= max_guesses and ai_guesses >= max_guesses:
            print(f"\n😔 Both players exhausted their guesses!")
            print(f"🔤 The word was: {BOLD}{secret.upper()}{RESET}")
            definition = get_word_definition(secret)
            if definition:
                print(f"📖 Definition: {definition}")
            print()
            print_board(player_board, ai_board)
            return "draw"

        if turn == 0:  # Player's turn
            if player_guesses >= max_guesses:
                print("⏭️  You're out of guesses! Skipping to AI...")
                turn = 1
                continue

            remaining = max_guesses - player_guesses
            prompt = f"  Your guess ({remaining} left): "
            raw = input(prompt).strip().lower()

            if raw == "quit":
                print(f"\n🏳️  You gave up! The word was: {BOLD}{secret.upper()}{RESET}")
                definition = get_word_definition(secret)
                if definition:
                    print(f"📖 Definition: {definition}")
                return "ai"

            if raw == "hint":
                if player_hints >= max_hints:
                    print("  ❌ No hints remaining!\n")
                    continue
                player_hints += 1
                # Reveal a random unrevealed correct letter
                unrevealed = [
                    i for i in range(5)
                    if not any(
                        g[i] == secret[i] and s[i] == "green"
                        for g, s in player_board
                    )
                ]
                if not unrevealed:
                    print("  🤷 All letters already revealed!\n")
                    continue
                idx = random.choice(unrevealed)
                hint_letter = secret[idx]
                print(f"  💡 Hint: Position {idx + 1} is '{hint_letter.upper()}'\n")
                # Update letter status
                letter_status[hint_letter.upper()] = "green"
                display_keyboard(letter_status)
                continue

            if len(raw) != 5 or not raw.isalpha():
                print("  ❌ Please enter exactly 5 letters.\n")
                continue

            if raw not in WORD_LIST:
                print("  ❌ Not in word list! Try again.\n")
                continue

            if raw in [g for g, _ in player_board]:
                print("  ⚠️  You already guessed that word! Try another.\n")
                continue

            player_guesses += 1
            statuses = evaluate_guess(secret, raw)
            player_board.append((raw, statuses))

            # Update keyboard
            for letter, st in zip(raw, statuses):
                current = letter_status.get(letter.upper(), "unknown")
                priority = {"green": 0, "yellow": 1, "gray": 2, "unknown": 3}
                if priority.get(st, 3) < priority.get(current, 3):
                    letter_status[letter.upper()] = st

            # Display
            colored = "".join(color_letter(l, s) for l, s in zip(raw, statuses))
            emojis = emoji_feedback(statuses)
            print(f"  {colored}  {emojis}")
            display_keyboard(letter_status)

            if raw == secret:
                print(f"  🎉 You got it in {player_guesses} guess{'es' if player_guesses > 1 else ''}!\n")
                print_board(player_board, ai_board)
                definition = get_word_definition(secret)
                if definition:
                    print(f"📖 Definition: {definition}")
                return "player"

            turn = 1

        else:  # AI's turn
            if ai_guesses >= max_guesses:
                turn = 0
                continue

            ai_guess_word = ai.guess()
            ai_guesses += 1
            statuses = evaluate_guess(secret, ai_guess_word)
            ai.learn(ai_guess_word, statuses)
            ai_board.append((ai_guess_word, statuses))

            colored = "".join(color_letter(l, s) for l, s in zip(ai_guess_word, statuses))
            emojis = emoji_feedback(statuses)
            remaining_ai = max_guesses - ai_guesses
            print(f"  🤖 AI guesses: {colored}  {emojis}  ({remaining_ai} left)")

            if ai_guess_word == secret:
                print(f"  🤖 AI got it in {ai_guesses} guess{'es' if ai_guesses > 1 else ''}!\n")
                print(f"  🔤 The word was: {BOLD}{secret.upper()}{RESET}")
                print_board(player_board, ai_board)
                definition = get_word_definition(secret)
                if definition:
                    print(f"📖 Definition: {definition}")
                return "ai"

            turn = 0


def print_board(player_board: list[tuple[str, list[str]]], ai_board: list[tuple[str, list[str]]]):
    """Print both players' boards side by side."""
    print("\n  📋 Board:")
    print(f"  {'You':>22}  |  {'AI':<22}")
    print(f"  {'-' * 22}-+-{'-' * 22}")
    max_rows = max(len(player_board), len(ai_board))
    for i in range(max_rows):
        if i < len(player_board):
            _, statuses = player_board[i]
            left = emoji_feedback(statuses)
        else:
            left = "     "
        if i < len(ai_board):
            _, statuses = ai_board[i]
            right = emoji_feedback(statuses)
        else:
            right = "     "
        print(f"  {left:>22}  |  {right:<22}")
    print()


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------
def main():
    # Parse args
    difficulty = "normal"
    if "--easy" in sys.argv:
        difficulty = "easy"
    elif "--hard" in sys.argv:
        difficulty = "hard"
    elif "--stats" in sys.argv:
        display_stats(load_stats())
        return
    elif "--reset" in sys.argv:
        reset_stats()
        return
    elif "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    stats = load_stats()
    used_words: list[str] = []
    score = {"player": 0, "ai": 0}

    print("\n" + "=" * 45)
    print("🎯  W O R D L E   D U E L")
    print("=" * 45)
    print("  You vs AI — who guesses the word first?")
    print(f"  Difficulty: {DIFFICULTIES[difficulty]['label']}")
    print("=" * 45)

    round_num = 0
    while True:
        round_num += 1
        print(f"\n{'─' * 45}")
        print(f"  Round {round_num}  |  Score: You {score['player']} — {score['ai']} AI")
        print(f"{'─' * 45}")

        # Pick a secret word not yet used
        available = [w for w in WORD_LIST if w not in used_words]
        if not available:
            used_words = []  # Reset if we've used all words
            available = list(WORD_LIST)
        secret = random.choice(available)
        used_words.append(secret)

        result = play_round(secret, difficulty, stats)

        # Update stats
        stats["games_played"] += 1
        stats["difficulty_breakdown"][difficulty] = stats["difficulty_breakdown"].get(difficulty, 0) + 1
        stats["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        if result == "player":
            score["player"] += 1
            stats["wins"] += 1
            stats["current_streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        elif result == "ai":
            score["ai"] += 1
            stats["losses"] += 1
            stats["current_streak"] = 0
        else:
            stats["draws"] += 1
            # Draw doesn't break streak but doesn't extend it either

        save_stats(stats)

        # Ask to play again
        print(f"\n📊 Score: You {score['player']} — {score['ai']} AI")
        again = input("Play another round? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print(f"\n🏁 Final Score: You {score['player']} — {score['ai']} AI")
            if score["player"] > score["ai"]:
                print("🎊 You won the match! Congratulations!")
            elif score["ai"] > score["player"]:
                print("🤖 AI wins the match! Better luck next time!")
            else:
                print("🤝 It's a draw! Well played!")
            print(f"\n📊 Lifetime stats: {stats['wins']}W / {stats['losses']}L / {stats['draws']}D")
            if stats["best_streak"] > 0:
                print(f"🏆 Best win streak: {stats['best_streak']}")
            print()
            break


if __name__ == "__main__":
    main()
