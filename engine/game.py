"""
Game wrapper for python-chess
Handles game state, moves, and game termination
"""

import chess
from typing import Optional, List, Tuple
import numpy as np


class ChessGame:
    """Wrapper class for chess game management."""
    
    def __init__(self, fen: Optional[str] = None):
        """
        Initialize a chess game.
        
        Args:
            fen: Optional FEN string to start from a specific position
        """
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
        self.move_history = []
        self.result = None
    
    def get_board(self) -> chess.Board:
        """Get the current board state."""
        return self.board
    
    def make_move(self, move: chess.Move) -> bool:
        """
        Make a move on the board.
        
        Args:
            move: chess.Move object
            
        Returns:
            True if move was legal and made, False otherwise
        """
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            return True
        return False
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()
    
    def get_result(self) -> Optional[float]:
        """
        Get game result from current player's perspective.
        
        Returns:
            1.0 if current player wins
            -1.0 if current player loses
            0.0 if draw
            None if game not over
        """
        if not self.is_game_over():
            return None
        
        result = self.board.result()
        
        if result == "1-0":  # White wins
            return 1.0 if self.board.turn == chess.BLACK else -1.0
        elif result == "0-1":  # Black wins
            return 1.0 if self.board.turn == chess.WHITE else -1.0
        else:  # Draw
            return 0.0
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get list of legal moves."""
        return list(self.board.legal_moves)
    
    def copy(self) -> 'ChessGame':
        """Create a deep copy of the game."""
        new_game = ChessGame()
        new_game.board = self.board.copy()
        new_game.move_history = self.move_history.copy()
        new_game.result = self.result
        return new_game
    
    def get_fen(self) -> str:
        """Get FEN representation of current position."""
        return self.board.fen()
    
    def get_turn(self) -> bool:
        """Get current player (True = White, False = Black)."""
        return self.board.turn == chess.WHITE

