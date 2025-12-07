"""
Configuration file for NeuroChess
Contains hyperparameters and settings for training and gameplay
"""

# Neural Network Configuration
NN_CONFIG = {
    'num_res_blocks': 3,          # Number of residual blocks
    'num_filters': 64,            # Number of filters in CNN
    'value_head_hidden': 256,     # Hidden units in value head
    'policy_head_hidden': 256,    # Hidden units in policy head
    'dropout': 0.3,               # Dropout rate
}

# MCTS Configuration
MCTS_CONFIG = {
    'num_simulations': 100,       # Number of MCTS simulations per move
    'c_puct': 1.0,                # Exploration constant (UCT)
    'temperature': 1.0,           # Temperature for move selection
    'dirichlet_alpha': 0.3,       # Dirichlet noise parameter
    'dirichlet_epsilon': 0.25,    # Dirichlet noise weight
}

# Self-Play Configuration
SELF_PLAY_CONFIG = {
    'num_games': 100,             # Number of games per iteration
    'max_moves': 400,             # Maximum moves per game
    'save_games': True,           # Whether to save game data
}

# Training Configuration
TRAINING_CONFIG = {
    'batch_size': 32,             # Training batch size
    'learning_rate': 0.001,       # Learning rate
    'weight_decay': 1e-4,         # L2 regularization
    'num_epochs': 10,             # Epochs per training iteration
    'value_loss_weight': 1.0,     # Weight for value loss
    'policy_loss_weight': 1.0,    # Weight for policy loss
    'checkpoint_dir': 'models/checkpoints',
    'checkpoint_interval': 10,    # Save checkpoint every N iterations
}

# Game Configuration
GAME_CONFIG = {
    'board_size': 8,              # Chess board size (always 8)
    'num_planes': 18,              # Number of input planes for board encoding
}

# Paths
PATHS = {
    'checkpoint_dir': 'models/checkpoints',
    'game_data_dir': 'data/self_play_games',
    'model_name': 'neurochess_model',
}

