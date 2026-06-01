---
name: wordle-duel
description: Play Wordle against the agent — take turns guessing a 5-letter word with color-coded feedback
metadata:
  hermes:
    tags: [game, wordle, puzzle, word-game, duel, turn-based]
---

# Wordle Duel

Play Wordle against the agent. You and the agent take turns guessing a secret 5-letter word. Fewer attempts = winner.

## Rules

1. Agent picks a secret 5-letter word (hidden from user)
2. User guesses first, then agent guesses, alternating turns
3. After each guess, provide color feedback:
   - 🟩 = correct letter, correct position
   - 🟨 = correct letter, wrong position
   - ⬜ = letter not in word
4. Show a keyboard tracker after each guess (green/yellow/gray/unknown letters)
5. Whoever guesses correctly wins the round
6. Track score across multiple rounds
7. Max 6 guesses per player per round; reveal word if both exhaust guesses

## Word List

Use common 5-letter English words: apple, brave, crane, dance, eagle, flame, grape, house, image, juice, knife, lemon, mango, night, ocean, piano, queen, river, stone, tiger, ultra, vivid, water, young, zebra, beach, cloud, dream, earth, fresh, ghost, happy, ivory, jewel, light, magic, noble, olive, peace, quest, royal, solar, truth, unity, voice, world, amber, black, crisp, delta, elite, frost, hover, input, karma, lunar, marsh, nexus, orbit, prism, quilt, rusty, swift, turbo, urban, vault, whirl, brick, charm, dwarf, exile, giant, heart, index, jolly, kite, lunar, mount, nerve, opal, plumb, quiet, rival, storm, tower, urban, vivid, wheat, xerox, yield, zesty.

## Game Flow

When user says "wordle", "play wordle", "wordle duel":

1. Announce game, pick secret word (don't reveal)
2. Ask user for first guess
3. Validate: must be 5 letters, alphabetic only
4. Give feedback with colors + keyboard tracker
5. Agent makes its own smart guess (use green positions, include yellow letters in new spots, avoid gray)
6. Show agent's guess and its feedback
7. Alternate until someone wins
8. Update scoreboard, ask for another round

## Agent Strategy

- Always use confirmed green letters in their positions
- Include yellow letters but in different positions
- Never reuse gray letters
- Make educated guesses based on remaining possibilities

## Scoreboard

```
📊 Scoreboard (Best of N)
  You: 2  🤖 Agent: 1
```

## Constraints

- Only valid 5-letter English words as guesses
- Invalid input = ask again (no penalty)
- No repeated secret words in a session
- Keep it fun with light commentary
