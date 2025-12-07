# How to Play NeuroChess - Step by Step Guide

## Quick Start - Play in Command Line (Easiest)

1. **Open PowerShell or Command Prompt**
2. **Navigate to the project folder:**
   ```
   cd "C:\Users\Lidiya Getale\Desktop\NeuroChess"
   ```

3. **Run the game:**
   ```
   python main.py play
   ```

4. **How to play:**
   - The board will be displayed in text format
   - When it's your turn, enter moves in UCI notation:
     - `e2e4` - moves pawn from e2 to e4
     - `g1f3` - moves knight from g1 to f3
     - `e7e5` - moves pawn from e7 to e5
   - The AI will automatically make its move after yours
   - Type `quit` to exit

## Example Moves (UCI Notation):
- `e2e4` - Pawn e2 to e4
- `e7e5` - Pawn e7 to e5
- `g1f3` - Knight g1 to f3
- `b8c6` - Knight b8 to c6
- `f1b5` - Bishop f1 to b5

## Play with GUI (Visual Interface)

1. **Run:**
   ```
   python main.py gui
   ```

2. **How to play:**
   - Click on a piece (it will highlight in yellow)
   - Click on the destination square
   - The AI will move automatically after your turn
   - Use "New Game" button to restart
   - Use "AI Move" button to manually trigger AI move

## Play as Black

```
python main.py play --black
```

## Important Notes:

⚠️ **The model starts untrained** - it will play randomly at first!

To train the AI (make it stronger):
```
python main.py train --iterations 10
```
This will take a while but makes the AI much better!

