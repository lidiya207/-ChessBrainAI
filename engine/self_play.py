"""
Self-play system for generating training data
"""

import os
import pickle
import numpy as np
from tqdm import tqdm
from typing import List, Tuple
import chess
from engine.game import ChessGame
from engine.mcts import MCTS
from engine.utils import board_to_tensor, move_to_index
import config


class SelfPlay:
    """Manages self-play games for training data generation."""
    
    def __init__(self, model, device: str = 'cpu'):
        """
        Initialize self-play system.
        
        Args:
            model: Neural network model
            device: Device to run model on
        """
        self.model = model
        self.device = device
        self.mcts = MCTS(model, device=device)
    
    def play_game(self, max_moves: int = None) -> List[Tuple]:
        """
        Play a single self-play game.
        
        Args:
            max_moves: Maximum number of moves before draw
            
        Returns:
            List of (board_state, policy, result) tuples
        """
        max_moves = max_moves or config.SELF_PLAY_CONFIG['max_moves']
        game = ChessGame()
        game_data = []
        
        move_count = 0
        while not game.is_game_over() and move_count < max_moves:
            # Get MCTS policy
            move, policy = self.mcts.search(game)
            
            if move is None:
                break
            
            # Store game state and policy
            board_tensor = board_to_tensor(game.get_board())
            game_data.append((board_tensor.copy(), policy.copy()))
            
            # Make move
            game.make_move(move)
            move_count += 1
        
        # Get final result
        result = game.get_result()
        if result is None:
            result = 0.0  # Draw
        
        # Assign result to all positions (from perspective of player who made the move)
        # We need to flip the result for positions where it was black's turn
        final_data = []
        for i, (board_state, policy) in enumerate(game_data):
            # Determine if this was white's or black's move
            # Even indices (0, 2, 4...) are white, odd are black
            is_white_move = (i % 2 == 0)
            position_result = result if is_white_move else -result
            final_data.append((board_state, policy, position_result))
        
        return final_data
    
    def generate_games(self, num_games: int = None, save: bool = None) -> List[Tuple]:
        """
        Generate multiple self-play games.
        
        Args:
            num_games: Number of games to generate
            save: Whether to save games to disk
            
        Returns:
            List of all game data tuples
        """
        num_games = num_games or config.SELF_PLAY_CONFIG['num_games']
        save = save if save is not None else config.SELF_PLAY_CONFIG['save_games']
        
        all_data = []
        
        print(f"Generating {num_games} self-play games...")
        for game_idx in tqdm(range(num_games), desc="Self-play games"):
            game_data = self.play_game()
            all_data.extend(game_data)
        
        # Save to disk if requested
        if save:
            os.makedirs(config.PATHS['game_data_dir'], exist_ok=True)
            filename = os.path.join(
                config.PATHS['game_data_dir'],
                f'self_play_data_{len(all_data)}_positions.pkl'
            )
            with open(filename, 'wb') as f:
                pickle.dump(all_data, f)
            print(f"Saved {len(all_data)} positions to {filename}")
        
        return all_data

