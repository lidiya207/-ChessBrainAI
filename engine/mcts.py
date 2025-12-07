"""
Monte Carlo Tree Search implementation for NeuroChess
"""

import numpy as np
import chess
from typing import Dict, List, Optional, Tuple
import math
from engine.game import ChessGame
from engine.utils import board_to_tensor, move_to_index, create_move_mask, apply_temperature
import config


class MCTSNode:
    """Node in the Monte Carlo Tree."""
    
    def __init__(self, game: ChessGame, parent: Optional['MCTSNode'] = None, move: Optional[chess.Move] = None):
        """
        Initialize MCTS node.
        
        Args:
            game: ChessGame object representing the position
            parent: Parent node
            move: Move that led to this position
        """
        self.game = game
        self.parent = parent
        self.move = move
        self.children: Dict[chess.Move, 'MCTSNode'] = {}
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = 0.0  # Prior probability from neural network
    
    def is_expanded(self) -> bool:
        """Check if node has been expanded."""
        return len(self.children) > 0
    
    def get_value(self) -> float:
        """Get average value of this node."""
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count
    
    def select_child(self, c_puct: float) -> 'MCTSNode':
        """
        Select child using UCT formula.
        
        Args:
            c_puct: Exploration constant
            
        Returns:
            Selected child node
        """
        best_score = float('-inf')
        best_child = None
        
        for move, child in self.children.items():
            # UCT formula: Q + c_puct * P * sqrt(N_parent) / (1 + N_child)
            u = c_puct * child.prior * math.sqrt(self.visit_count) / (1 + child.visit_count)
            score = child.get_value() + u
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    
    def expand(self, policy: np.ndarray):
        """
        Expand node by creating children for all legal moves.
        
        Args:
            policy: Policy vector from neural network (4096 elements)
        """
        legal_moves = self.game.get_legal_moves()
        move_mask = create_move_mask(self.game.get_board())
        
        # Normalize policy over legal moves only
        legal_policy = np.zeros(len(legal_moves))
        for i, move in enumerate(legal_moves):
            idx = move_to_index(move, self.game.get_board())
            legal_policy[i] = policy[idx] * move_mask[idx]
        
        # Normalize
        total = legal_policy.sum()
        if total > 0:
            legal_policy = legal_policy / total
        else:
            # Uniform distribution if all zeros
            legal_policy = np.ones(len(legal_moves)) / len(legal_moves)
        
        # Create children
        for i, move in enumerate(legal_moves):
            new_game = self.game.copy()
            new_game.make_move(move)
            child = MCTSNode(new_game, parent=self, move=move)
            child.prior = legal_policy[i]
            self.children[move] = child
    
    def backpropagate(self, value: float):
        """
        Backpropagate value up the tree.
        
        Args:
            value: Value to propagate (from current player's perspective)
        """
        self.visit_count += 1
        self.value_sum += value
        
        if self.parent is not None:
            # Flip value for parent (opponent's perspective)
            self.parent.backpropagate(-value)


class MCTS:
    """Monte Carlo Tree Search with neural network guidance."""
    
    def __init__(self, model, num_simulations: int = None, c_puct: float = None,
                 temperature: float = None, device: str = 'cpu'):
        """
        Initialize MCTS.
        
        Args:
            model: Neural network model
            num_simulations: Number of MCTS simulations
            c_puct: Exploration constant
            temperature: Temperature for move selection
            device: Device to run model on
        """
        self.model = model
        self.num_simulations = num_simulations or config.MCTS_CONFIG['num_simulations']
        self.c_puct = c_puct or config.MCTS_CONFIG['c_puct']
        self.temperature = temperature or config.MCTS_CONFIG['temperature']
        self.device = device
    
    def search(self, game: ChessGame) -> Tuple[chess.Move, np.ndarray]:
        """
        Perform MCTS search and return best move.
        
        Args:
            game: Current game state
            
        Returns:
            best_move: Best move according to MCTS
            visit_counts: Visit counts for all moves (normalized as probabilities)
        """
        root = MCTSNode(game)
        
        # Get initial policy and value from neural network
        board_tensor = board_to_tensor(game.get_board())
        policy, value = self.model.predict(board_tensor, self.device)
        
        # Add Dirichlet noise to root policy for exploration
        legal_moves = game.get_legal_moves()
        if len(legal_moves) > 0:
            dirichlet_noise = np.random.dirichlet(
                [config.MCTS_CONFIG['dirichlet_alpha']] * len(legal_moves)
            )
            move_mask = create_move_mask(game.get_board())
            
            for i, move in enumerate(legal_moves):
                idx = move_to_index(move, game.get_board())
                policy[idx] = (1 - config.MCTS_CONFIG['dirichlet_epsilon']) * policy[idx] + \
                             config.MCTS_CONFIG['dirichlet_epsilon'] * dirichlet_noise[i]
                policy[idx] *= move_mask[idx]
            
            # Renormalize
            policy = policy / (policy.sum() + 1e-8)
        
        root.expand(policy)
        
        # Perform simulations
        for _ in range(self.num_simulations):
            node = root
            
            # Selection: traverse to leaf
            while node.is_expanded() and not node.game.is_game_over():
                node = node.select_child(self.c_puct)
            
            # Evaluation
            if node.game.is_game_over():
                value = node.game.get_result()
                if value is None:
                    value = 0.0
            else:
                # Expand and evaluate with neural network
                board_tensor = board_to_tensor(node.game.get_board())
                policy, value = self.model.predict(board_tensor, self.device)
                node.expand(policy)
            
            # Backpropagation
            node.backpropagate(value)
        
        # Select move based on visit counts
        visit_counts = np.zeros(4096)
        for move, child in root.children.items():
            idx = move_to_index(move, game.get_board())
            visit_counts[idx] = child.visit_count
        
        # Normalize visit counts to get move probabilities
        total_visits = visit_counts.sum()
        if total_visits > 0:
            visit_counts = visit_counts / total_visits
        else:
            # Fallback to uniform
            legal_moves = game.get_legal_moves()
            for move in legal_moves:
                idx = move_to_index(move, game.get_board())
                visit_counts[idx] = 1.0 / len(legal_moves)
        
        # Apply temperature
        visit_counts = apply_temperature(visit_counts, self.temperature)
        
        # Select best move
        legal_moves = game.get_legal_moves()
        if len(legal_moves) == 0:
            return None, visit_counts
        
        best_move = None
        best_score = -1
        
        for move in legal_moves:
            idx = move_to_index(move, game.get_board())
            if visit_counts[idx] > best_score:
                best_score = visit_counts[idx]
                best_move = move
        
        return best_move, visit_counts

