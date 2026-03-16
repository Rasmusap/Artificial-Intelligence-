# Kalaha GUI – Interactive Game Against AI

A complete graphical user interface for playing Kalaha against a powerful minimax AI opponent.

## Features

- **Interactive Pygame GUI** – Visual game board with clickable pits
- **Multiple Difficulty Levels**:
  - Easy (AI depth: 4)
  - Medium (AI depth: 6)
  - Hard (AI depth: 8)
- **Real-time Game State** – See the board, scores, and available moves
- **AI Opponent** – Uses alpha-beta pruning minimax algorithm with evalution functions
- **Game Rules Enforced**:
  - Distribute stones counter-clockwise
  - Extra turn if landing in your store
  - Capture opposite pit if landing in empty pit on your side
  - Game ends when one side is empty
- **Smooth UI** – Buttons, hover effects, status indicators

## How to Run

### GUI Version
From the `src` directory:
```bash
python kalaha_gui.py
```
### CLI Version
From the `src` directory:
```bash
python main.py
```

## How to Play

1. **Start Screen**: Select AI difficulty (Easy, Medium, or Hard)
2. **During Game**:
   - **Your Turn**: You play as Player 1 (bottom side)
     - Click on any pit on your side to play a move
     - Highlighted pits show valid moves
   - **AI Turn**: The AI (Player 2, top side) thinks and makes a move automatically
3. **Game Over**: See final scores and decide to play again or return home

## Game Board Layout

```
        Player 2 (AI)
    [Pit] [Pit] [Pit] [Pit] [Pit] [Pit]
[Store]                              [Store]
    [Pit] [Pit] [Pit] [Pit] [Pit] [Pit]
        Player 1 (You)
```

- **Pits**: Numbered 1-6 for each player
- **Stores**: Large circles on the sides (left for you, right for AI)
- **Stones**: Displayed in the center of each pit

## Kalaha Rules

1. **Setup**: Each pit starts with 4 stones
2. **Turn**: Pick a pit and distribute all its stones counter-clockwise
3. **Extra Turn**: If your last stone lands in your store, play again
4. **Capture**: If your last stone lands in an empty pit on your side and the opposite pit has stones, you capture both
5. **Game End**: When one player's pits are empty, the opponent collects remaining stones
6. **Win**: Highest score wins

## AI Difficulty

- **Easy (Depth 4)**: Looks 4 moves ahead – good for learning
- **Medium (Depth 6)**: Looks 6 moves ahead – balanced challenge
- **Hard (Depth 8)**: Looks 8 moves ahead – expert level (may take time to think)

## Files

- `src/kalaha_gui.py` – Main GUI application
- `scripts/run_gui.ps1` – PowerShell launcher script
- `src/game_engine.py` – Game logic and rules
- `src/minmax_pruning.py` – AI algorithm with alpha-beta pruning
- `src/evaluation.py` – AI evaluation functions

## Requirements

- Python 3.10+
- pygame >= 2.5

Install with:
```bash
pip install pygame
```
