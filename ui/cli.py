"""
Command-line interface for playing against NeuroChess
"""

import chess
from engine.game import ChessGame
from engine.mcts import MCTS
from engine.utils import board_to_tensor
import config


class ChessCLI:
    """Command-line interface for chess gameplay."""
    
    def __init__(self, model, device: str = 'cpu'):
        """
        Initialize CLI.
        
        Args:
            model: Neural network model
            device: Device to run model on
        """
        self.model = model
        self.device = device
        self.mcts = MCTS(model, device=device, temperature=0.1)  # Low temperature for deterministic play
    
    def print_board(self, board: chess.Board):
        """Print the chess board in a readable format."""
        print("\n" + str(board) + "\n")
    
    def get_user_move(self, game: ChessGame) -> chess.Move:
        """
        Get move from user input.
        
        Args:
            game: Current game state
            
        Returns:
            chess.Move object
        """
        legal_moves = game.get_legal_moves()
        
        while True:
            move_str = input("Enter your move (e.g., e2e4): ").strip()
            
            if not move_str:
                print("Please enter a move.")
                continue
            
            try:
                move = chess.Move.from_uci(move_str)
                if move in legal_moves:
                    return move
                else:
                    print("Illegal move. Please try again.")
            except ValueError:
                print("Invalid move format. Use UCI notation (e.g., e2e4).")
    
    def play(self, human_plays_white: bool = True):
        """
        Play a game against the AI.
        
        Args:
            human_plays_white: Whether human plays as white
        """
        game = ChessGame()
        
        print("\n" + "="*50)
        print("Welcome to NeuroChess!")
        print("="*50)
        print(f"You are playing as {'White' if human_plays_white else 'Black'}")
        print("Enter moves in UCI notation (e.g., e2e4, e7e5)")
        print("Type 'quit' to exit\n")
        
        while not game.is_game_over():
            self.print_board(game.get_board())
            
            if game.get_turn() == human_plays_white:
                # Human's turn
                print("Your turn!")
                move = self.get_user_move(game)
                game.make_move(move)
            else:
                # AI's turn
                print("AI is thinking...")
                move, _ = self.mcts.search(game)
                
                if move is None:
                    print("AI has no legal moves!")
                    break
                
                print(f"AI plays: {move.uci()}")
                game.make_move(move)
        
        # Game over
        self.print_board(game.get_board())
        result = game.get_board().result()
        
        if result == "1-0":
            if human_plays_white:
                print("Congratulations! You won!")
            else:
                print("AI wins!")
        elif result == "0-1":
            if human_plays_white:
                print("AI wins!")
            else:
                print("Congratulations! You won!")
        else:
            print("It's a draw!")

