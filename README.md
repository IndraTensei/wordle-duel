# 🎯 Wordle Duel

Play Wordle against an AI opponent — take turns guessing a secret 5-letter word with color-coded feedback. Whoever guesses in fewer tries wins!

## Features

- 🟩🟨⬜ Color-coded feedback (green/yellow/gray)
- ⌨️ Live keyboard tracker showing letter status
- 📊 Multi-round scoreboard
- 🧠 Smart AI that makes educated guesses
- 🎮 Turn-based duel format — you vs AI

## How to Play

1. I pick a secret 5-letter word
2. You guess first with any 5-letter word
3. I give you color feedback:
   - 🟩 = right letter, right spot
   - 🟨 = right letter, wrong spot
   - ⬜ = letter not in word
4. Then I take my turn guessing
5. We alternate until someone gets it right

## Rules

- Only valid 5-letter English words
- 6 guesses maximum per player per round
- Invalid guesses don't count (we'll ask again)
- Play multiple rounds — track your score!

## Example

```
Your guess: C R A N E
Feedback:   ⬜🟨⬜⬜🟨

⌨️ Keyboard:
🟨 C . . . E . . . . . . N . . . . . . . . . . .
⬜ . . . . . . . . . . . . . . . . . R . A . . . .

🤖 My guess: STONE
Feedback:   ⬜🟩⬜⬜🟩
```

## Installation

This is a Hermes Agent skill. Installed automatically via skills folder.

## License

MIT
