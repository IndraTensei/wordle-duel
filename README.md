# 🎯 Wordle Duel

Play Wordle against an AI opponent — take turns guessing a secret 5-letter word with color-coded feedback. Whoever guesses in fewer tries wins!

Now a **standalone CLI game** — no Hermes Agent required! Just run it in your terminal.

## ✨ Features

- 🟩🟨⬜ **Color-coded feedback** — green/yellow/gray with ANSI colors + emoji fallback
- ⌨️ **Live keyboard tracker** — see which letters are confirmed, possible, or eliminated
- 📊 **Persistent statistics** — win rate, streak, guess distribution, difficulty breakdown
- 💡 **Hint system** — stuck? Request a hint to reveal a correct letter (Easy & Normal only)
- 🎮 **Difficulty levels** — Easy (8 guesses), Normal (6), Hard (4, no hints)
- 📖 **Word definitions** — after each round, learn what the word means via dictionary API
- 🧠 **Smart AI** — the AI learns from its guesses and narrows down candidates
- 🔄 **Multi-round matches** — play best-of-N with running scoreboard

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/IndraTensei/wordle-duel.git
cd wordle-duel

# Play!
python3 wordle_duel.py
```

## Usage

```bash
python3 wordle_duel.py           # Normal difficulty (6 guesses)
python3 wordle_duel.py --easy    # Easy mode (8 guesses, 1 hint)
python3 wordle_duel.py --hard    # Hard mode (4 guesses, no hints)
python3 wordle_duel.py --stats   # View lifetime statistics
python3 wordle_duel.py --reset   # Reset statistics
python3 wordle_duel.py --help    # Show help
```

## How to Play

1. The AI picks a secret 5-letter word
2. You guess first with any valid 5-letter word
3. Get color feedback:
   - 🟩 = right letter, right spot
   - 🟨 = right letter, wrong spot
   - ⬜ = letter not in word
4. Then the AI takes its turn
5. Alternate until someone guesses correctly
6. Play multiple rounds — track your score!

### During a Game

- Type any 5-letter word to guess
- Type `hint` to reveal a correct letter (costs your hint for the round)
- Type `quit` to give up the round

## Example

```
🎯  W O R D L E   D U E L
  You vs AI — who guesses the word first?
  Difficulty: 🟡 Normal (6 guesses)

  Round 1  |  Score: You 0 — 0 AI

🎯 I'm thinking of a 5-letter word...
📏 Difficulty: 🟡 Normal (6 guesses)
💡 Hints available: 1

  Your guess (6 left): crane
  [colored output]  ⬜🟨🟨⬜⬜

  ⌨️  Keyboard:
      Q   W   E   R   T   Y   U   I   O   P
      A   S   D   F   G   H   J   K   L
      Z   X   C   V   B   N   M

  🤖 AI guesses: [colored]  ⬜🟨⬜⬜🟨  (5 left)
  Your guess (5 left):
```

## Statistics

Your stats are saved to `~/.wordle_duel_stats.json`:

```
📊  WORDLE DUEL — LIFETIME STATISTICS
  Games Played:    12
  Wins:            8 (66.7%)
  Losses:          3
  Draws:           1
  Current Streak:  3 🔥
  Best Streak:     5 🏆

  Guess Distribution:
    1: ██ 1
    2: ████ 2
    3: ████████ 4
    4: ████ 2
    5: ██ 1
    6: █ 0

  By Difficulty:  🟢 Easy: 3  🟡 Normal: 7  🔴 Hard: 2
```

## Requirements

- Python 3.10+
- No external dependencies! (uses only stdlib)
- Terminal with ANSI color support recommended (works without)

## Project Structure

```
wordle-duel/
├── wordle_duel.py    # Main game (standalone CLI)
├── SKILL.md          # Hermes Agent skill instructions
├── README.md         # This file
└── .gitignore
```

## License

MIT
