"""
Test suite for Wordle Duel.
Run with: python3 test_wordle_duel.py
"""
import sys, tempfile, unittest.mock
sys.path.insert(0, '/home/ubuntu/daily-projects/wordle-duel')
from wordle_duel import evaluate_guess, WordleAI, is_valid_word, load_stats, save_stats, WORD_LIST
from pathlib import Path

passed = 0
failed = 0

def check(name, condition, msg=""):
    global passed, failed
    if condition:
        print(f'  ✓ {name}')
        passed += 1
    else:
        print(f'  ✗ {name}: {msg}')
        failed += 1

print('=' * 50)
print('WORDLE DUEL TEST SUITE')
print('=' * 50)

# --- Test 1: evaluate_guess ---
print()
print('Test 1: evaluate_guess')

check('All green', evaluate_guess('crane', 'crane') == ['green'] * 5)
check('All gray', evaluate_guess('crane', 'blitz') == ['gray'] * 5)

result = evaluate_guess('crane', 'coder')
check('Mixed feedback', result == ['green', 'gray', 'gray', 'yellow', 'yellow'], str(result))

check('Duplicate in guess', evaluate_guess('crane', 'eeeee') == ['gray', 'gray', 'gray', 'gray', 'green'])
check('Duplicate in secret', evaluate_guess('abbey', 'essex') == ['gray', 'gray', 'gray', 'green', 'gray'])
check('Partial overlap', evaluate_guess('apple', 'zebra') == ['gray', 'yellow', 'gray', 'gray', 'yellow'])

result = evaluate_guess('abcde', 'edcba')
check('All yellow+center green', result == ['yellow', 'yellow', 'green', 'yellow', 'yellow'], str(result))

# --- Test 2: AI ---
print()
print('Test 2: AI opponent')

ai = WordleAI(['crane', 'blame', 'trace', 'stare', 'brave', 'grape', 'charm', 'crisp'])
result = evaluate_guess('crane', 'blame')
ai.learn('blame', result)
check('AI filters candidates', all(w[2] == 'a' and w[4] == 'e' for w in ai.candidates), str(ai.candidates))
check('AI removes gray letters', all('b' not in w and 'l' not in w and 'm' not in w for w in ai.candidates))

ai3 = WordleAI(['crane', 'crisp', 'blame', 'brave'])
result3 = evaluate_guess('crane', 'brave')
check('brave feedback', result3 == ['gray', 'green', 'green', 'gray', 'green'], str(result3))
ai3.learn('brave', result3)
check('AI green map', ai3.green == {1: 'r', 2: 'a', 4: 'e'}, str(ai3.green))
check('AI yellow empty', ai3.yellow_all == set(), str(ai3.yellow_all))
check('AI gray letters', 'b' in ai3.gray and 'v' in ai3.gray, str(ai3.gray))

# --- Test 3: is_valid_word ---
print()
print('Test 3: is_valid_word')
check('Valid word', is_valid_word('crane') == True)
check('Valid uppercase', is_valid_word('CRANE') == True)
check('Too short', is_valid_word('abc') == False)
check('Too long', is_valid_word('abcdef') == False)
check('Numbers', is_valid_word('12345') == False)
check('Mixed alphanum', is_valid_word('ab3de') == False)
check('Empty', is_valid_word('') == False)

# --- Test 4: Stats ---
print()
print('Test 4: Stats persistence')
mock_path = Path(tempfile.mktemp(suffix='.json'))
with unittest.mock.patch('wordle_duel.STATS_FILE', mock_path):
    stats = load_stats()
    check('Default stats', stats['games_played'] == 0)
    stats['games_played'] = 12
    stats['wins'] = 8
    stats['current_streak'] = 4
    stats['best_streak'] = 7
    save_stats(stats)
    loaded = load_stats()
    check('Save/load games', loaded['games_played'] == 12)
    check('Save/load wins', loaded['wins'] == 8)
    check('Save/load streak', loaded['current_streak'] == 4)
    check('Save/load best', loaded['best_streak'] == 7)
    mock_path.unlink(missing_ok=True)

# --- Test 5: AI guesses ---
print()
print('Test 5: AI guesses')
ai5 = WordleAI(['crane', 'brave', 'grape'])
g = ai5.guess()
check('Valid guess', g in ['crane', 'brave', 'grape'], str(g))
check('Guess tracked', g in ai5.guesses)

# --- Test 6: No repeats ---
print()
print('Test 6: No repeat guesses')
ai6 = WordleAI(WORD_LIST)
ok = True
for _ in range(10):
    g = ai6.guess()
    if ai6.guesses.count(g) != 1:
        ok = False
        break
check('No repeats in 10 guesses', ok)

# --- Test 7: Word list ---
print()
print('Test 7: Word list integrity')
check('No duplicates', len(WORD_LIST) == len(set(WORD_LIST)))
check('All 5 letters', all(len(w) == 5 for w in WORD_LIST))
check('All alpha', all(w.isalpha() for w in WORD_LIST))
print(f'  -> {len(WORD_LIST)} unique 5-letter words')

# --- Test 8: AI fallback ---
print()
print('Test 8: AI fallback')
ai7 = WordleAI(['crane'])
ai7.learn('crane', ['gray'] * 5)
g = ai7.guess()
check('Fallback to original list', g == 'crane', str(g))

# --- Test 9: CLI flags ---
print()
print('Test 9: CLI flags')
import subprocess
r = subprocess.run([sys.executable, '/home/ubuntu/daily-projects/wordle-duel/wordle_duel.py', '--help'], capture_output=True, text=True)
check('--help works', 'Wordle Duel' in r.stdout or 'wordle_duel' in r.stdout.lower(), r.stdout[:100])

r = subprocess.run([sys.executable, '/home/ubuntu/daily-projects/wordle-duel/wordle_duel.py', '--stats'], capture_output=True, text=True)
check('--stats works', 'STATISTICS' in r.stdout or 'No games' in r.stdout, r.stdout[:100])

# --- Test 10: Syntax ---
print()
print('Test 10: Syntax check')
import py_compile
try:
    py_compile.compile('/home/ubuntu/daily-projects/wordle-duel/wordle_duel.py', doraise=True)
    check('No syntax errors', True)
except py_compile.PyCompileError as e:
    check('No syntax errors', False, str(e))

# --- Summary ---
print()
print('=' * 50)
if failed == 0:
    print(f'ALL {passed} TESTS PASSED')
else:
    print(f'{passed} passed, {failed} FAILED')
print('=' * 50)
sys.exit(1 if failed else 0)
