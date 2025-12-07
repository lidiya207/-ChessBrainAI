"""
Utility functions for NeuroChess
"""

import chess
import numpy as np
import torch


def board_to_tensor(board: chess.Board) -> np.ndarray:
    """
    Convert a chess board to a tensor representation.
    
    Creates 18 planes:
    - 6 planes for white pieces (pawn, rook, knight, bishop, queen, king)
    - 6 planes for black pieces (pawn, rook, knight, bishop, queen, king)
    - 4 planes for castling rights (white kingside, white queenside, black kingside, black queenside)
    - 1 plane for side to move (1 if white, 0 if black)
    - 1 plane for move count (normalized)
    
    Args:
        board: python-chess Board object
        
    Returns:
        numpy array of shape (18, 8, 8)
    """
    planes = np.zeros((18, 8, 8), dtype=np.float32)
    
    # Piece planes (0-11)
    piece_types = [
        chess.PAWN, chess.ROOK, chess.KNIGHT,
        chess.BISHOP, chess.QUEEN, chess.KING
    ]
    
    for i, piece_type in enumerate(piece_types):
        # White pieces (planes 0-5)
        for square in board.pieces(piece_type, chess.WHITE):
            row, col = divmod(square, 8)
            planes[i, row, col] = 1.0
        
        # Black pieces (planes 6-11)
        for square in board.pieces(piece_type, chess.BLACK):
            row, col = divmod(square, 8)
            planes[i + 6, row, col] = 1.0
    
    # Castling rights (planes 12-15)
    if board.has_kingside_castling_rights(chess.WHITE):
        planes[12, :, :] = 1.0
    if board.has_queenside_castling_rights(chess.WHITE):
        planes[13, :, :] = 1.0
    if board.has_kingside_castling_rights(chess.BLACK):
        planes[14, :, :] = 1.0
    if board.has_queenside_castling_rights(chess.BLACK):
        planes[15, :, :] = 1.0
    
    # Side to move (plane 16)
    if board.turn == chess.WHITE:
        planes[16, :, :] = 1.0
    
    # Move count (plane 17) - normalized
    planes[17, :, :] = min(board.fullmove_number / 100.0, 1.0)
    
    return planes


def move_to_index(move: chess.Move, board: chess.Board) -> int:
    """
    Convert a chess move to a unique index.
    
    Uses a simple encoding: from_square * 64 + to_square
    This gives 4096 possible moves (some invalid, but we'll mask them).
    
    Args:
        move: chess.Move object
        board: chess.Board object (for validation)
        
    Returns:
        integer index
    """
    return move.from_square * 64 + move.to_square


def index_to_move(index: int, board: chess.Board) -> chess.Move:
    """
    Convert an index back to a chess move.
    
    Args:
        index: integer index
        board: chess.Board object
        
    Returns:
        chess.Move object or None if invalid
    """
    from_square = index // 64
    to_square = index % 64
    
    move = chess.Move(from_square, to_square)
    
    # Check if move is legal
    if move in board.legal_moves:
        return move
    
    # Try to find promotion moves
    for promotion in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
        move = chess.Move(from_square, to_square, promotion=promotion)
        if move in board.legal_moves:
            return move
    
    return None


def create_move_mask(board: chess.Board) -> np.ndarray:
    """
    Create a mask for valid moves.
    
    Args:
        board: chess.Board object
        
    Returns:
        numpy array of shape (4096,) with 1.0 for valid moves, 0.0 otherwise
    """
    mask = np.zeros(4096, dtype=np.float32)
    
    for move in board.legal_moves:
        idx = move_to_index(move, board)
        mask[idx] = 1.0
    
    return mask


def apply_temperature(policy: np.ndarray, temperature: float) -> np.ndarray:
    """
    Apply temperature to policy distribution.
    
    Args:
        policy: policy array
        temperature: temperature parameter (1.0 = no change, <1.0 = sharper, >1.0 = flatter)
        
    Returns:
        temperature-adjusted policy
    """
    if temperature == 1.0:
        return policy
    
    policy = policy ** (1.0 / temperature)
    policy = policy / (policy.sum() + 1e-8)
    return policy


def save_checkpoint(model, optimizer, iteration, filepath: str):
    """Save model checkpoint."""
    torch.save({
        'iteration': iteration,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, filepath)


def load_checkpoint(model, optimizer, filepath: str):
    """Load model checkpoint."""
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['iteration']

