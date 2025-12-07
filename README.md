# NeuroChess

An AI chess engine that learns to play chess using deep reinforcement learning, inspired by AlphaZero. The engine uses Monte Carlo Tree Search (MCTS) guided by a neural network to make decisions, and improves through self-play.

## Features

- **Neural Network Architecture**: Convolutional neural network with residual blocks that evaluates board positions and predicts move probabilities
- **Monte Carlo Tree Search**: MCTS implementation with UCT algorithm for move selection
- **Self-Play Training**: Automatic generation of training data through self-play games
- **Reinforcement Learning**: Trains using policy and value losses from self-play data
- **Multiple Interfaces**: Command-line interface (CLI) and optional Tkinter GUI for playing against the AI
- **Checkpoint System**: Save and load model checkpoints for continuous training

## Requirements

- Python 3.10+
- PyTorch 2.0.0+
- python-chess 1.999+
- numpy 1.24.0+
- tqdm 4.65.0+

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
NeuroChess/
│── main.py                 # Main entry point
│── requirements.txt        # Python dependencies
│── README.md              # This file
│── config.py              # Configuration and hyperparameters
│
├── engine/
│   ├── neural_net.py      # PyTorch neural network model
│   ├── mcts.py            # Monte Carlo Tree Search
│   ├── game.py            # Chess game wrapper
│   ├── self_play.py       # Self-play system
│   ├── trainer.py         # Training pipeline
│   └── utils.py           # Utility functions
│
├── models/
│   └── checkpoints/       # Saved model checkpoints
│
├── data/
│   └── self_play_games/   # Self-play game data
│
└── ui/
    ├── cli.py             # Command-line interface
    └── simple_gui.py      # Tkinter GUI
```

## Usage

### Training the Model

Train the model using self-play reinforcement learning:

```bash
python main.py train --iterations 10
```

This will:
1. Generate self-play games
2. Train the neural network on the generated data
3. Save checkpoints periodically

To resume training from a checkpoint:

```bash
python main.py train --iterations 10 --resume models/checkpoints/neurochess_model_iter_5.pth
```

### Playing Against the AI (CLI)

Play against the AI using the command-line interface:

```bash
python main.py play
```

To play as black:

```bash
python main.py play --black
```

To use a specific checkpoint:

```bash
python main.py play --checkpoint models/checkpoints/neurochess_model_iter_10.pth
```

**Move Input Format**: Enter moves in UCI notation (e.g., `e2e4`, `g1f3`, `e7e5`)

### Playing Against the AI (GUI)

Launch the graphical interface:

```bash
python main.py gui
```

The GUI allows you to:
- Click squares to make moves
- See the board visually
- Start new games
- Request AI moves manually

## Configuration

Edit `config.py` to adjust hyperparameters:

- **Neural Network**: Number of residual blocks, filters, hidden units
- **MCTS**: Number of simulations, exploration constant, temperature
- **Self-Play**: Number of games per iteration, maximum moves
- **Training**: Batch size, learning rate, number of epochs

## How It Works

1. **Board Encoding**: The chess board is encoded into 18 planes (6 for white pieces, 6 for black pieces, 4 for castling rights, 1 for side to move, 1 for move count)

2. **Neural Network**: A CNN with residual blocks processes the board state and outputs:
   - **Policy**: Probability distribution over all possible moves (4096 possible moves)
   - **Value**: Position evaluation (-1 to 1, where 1 = win, -1 = loss)

3. **MCTS**: Monte Carlo Tree Search uses the neural network to:
   - Evaluate positions during tree search
   - Select moves using UCT (Upper Confidence Bound for Trees)
   - Build a search tree with visit counts and values

4. **Self-Play**: The AI plays games against itself, storing:
   - Board states
   - MCTS policy distributions
   - Game results

5. **Training**: The neural network learns by:
   - Minimizing policy loss (cross-entropy between predicted and MCTS policy)
   - Minimizing value loss (MSE between predicted and actual game outcome)
   - Using the stored self-play data

## Training Tips

- Start with fewer iterations to test the setup
- Increase `num_simulations` in MCTS for stronger play (but slower)
- Adjust `num_games` in self-play to balance training data quantity vs. time
- Monitor training losses - they should decrease over iterations
- The model improves gradually - early games may be weak

## Limitations

- The model starts untrained and will be weak initially
- Training requires significant computation time
- The move encoding (4096 possible moves) includes some invalid moves that are masked
- No opening book or endgame tablebase integration

## Future Improvements

- Add opening book support
- Implement endgame tablebase integration
- Add more sophisticated neural network architectures
- Implement distributed training
- Add tournament evaluation against other engines
- Implement time controls for gameplay

## License

This project is open source and available for educational purposes.

## Acknowledgments

Inspired by AlphaZero and other reinforcement learning chess engines. Uses the excellent `python-chess` library for chess rules and board representation.

