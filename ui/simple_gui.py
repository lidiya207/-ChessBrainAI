"""
Modern Tkinter GUI for playing against NeuroChess
Real chess features with premium design: move highlighting, move history, promotion dialog, etc.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import chess
from engine.game import ChessGame
from engine.mcts import MCTS
import config


class ChessGUI:
    """Enhanced GUI for chess gameplay using Tkinter."""
    
    def __init__(self, model, device: str = 'cpu', username: str = 'Guest'):
        """
        Initialize GUI.
        
        Args:
            model: Neural network model
            device: Device to run model on
            username: Current logged in username
        """
        self.model = model
        self.device = device
        self.username = username
        self.mcts = MCTS(model, device=device, temperature=0.1)
        self.game = ChessGame()
        self.selected_square = None
        self.human_plays_white = True
        self.last_move = None
        self.legal_moves_for_selected = []
        self.board_flipped = False
        self.move_history = []
        
        # Create main window with modern styling
        self.root = tk.Tk()
        self.root.title("♔ NeuroChess - AI Challenge")
        self.root.geometry("1100x750")
        self.root.configure(bg='#0f0f1e')
        self.root.minsize(900, 650)
        
        # Main container with modern background
        main_container = tk.Frame(self.root, bg='#0f0f1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Board with modern styling
        left_panel = tk.Frame(main_container, bg='#1a1a2e', relief=tk.FLAT)
        left_panel.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.BOTH)
        
        # Board frame with coordinates
        board_container = tk.Frame(left_panel, bg='#1a1a2e')
        board_container.pack(padx=20, pady=20)
        
        # Top coordinates (a-h) with modern styling
        coord_top = tk.Frame(board_container, bg='#1a1a2e')
        coord_top.pack()
        tk.Label(coord_top, text="  ", bg='#1a1a2e', width=2).pack(side=tk.LEFT)  # Spacer
        for col in range(8):
            label = tk.Label(
                coord_top,
                text=chr(97 + col),  # a-h
                font=("Segoe UI", 11, "bold"),
                bg='#1a1a2e',
                fg='#a0a0c0',
                width=7
            )
            label.pack(side=tk.LEFT)
        
        # Board with side coordinates
        board_row = tk.Frame(board_container, bg='#1a1a2e')
        board_row.pack(pady=5)
        
        # Left coordinates (8-1) with modern styling
        coord_left = tk.Frame(board_row, bg='#1a1a2e')
        coord_left.pack(side=tk.LEFT, padx=(0, 5))
        for row in range(8):
            label = tk.Label(
                coord_left,
                text=str(8 - row),
                font=("Segoe UI", 11, "bold"),
                bg='#1a1a2e',
                fg='#a0a0c0',
                width=2,
                height=3
            )
            label.pack()
        
        # Board frame with modern border and shadow effect
        self.board_frame = tk.Frame(
            board_row, 
            bg='#2d2d44', 
            relief=tk.FLAT, 
            borderwidth=0,
            highlightthickness=4,
            highlightbackground='#4a4a6a'
        )
        self.board_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create squares
        self.squares = {}
        self.create_board()
        
        # Right coordinates (8-1) with modern styling
        coord_right = tk.Frame(board_row, bg='#1a1a2e')
        coord_right.pack(side=tk.LEFT, padx=(5, 0))
        for row in range(8):
            label = tk.Label(
                coord_right,
                text=str(8 - row),
                font=("Segoe UI", 11, "bold"),
                bg='#1a1a2e',
                fg='#a0a0c0',
                width=2,
                height=3
            )
            label.pack()
        
        # Bottom coordinates (a-h) with modern styling
        coord_bottom = tk.Frame(board_container, bg='#1a1a2e')
        coord_bottom.pack(pady=(5, 0))
        tk.Label(coord_bottom, text="  ", bg='#1a1a2e', width=2).pack(side=tk.LEFT)  # Spacer
        for col in range(8):
            label = tk.Label(
                coord_bottom,
                text=chr(97 + col),  # a-h
                font=("Segoe UI", 11, "bold"),
                bg='#1a1a2e',
                fg='#a0a0c0',
                width=7
            )
            label.pack(side=tk.LEFT)
        
        # Right panel - Info and controls with modern styling
        right_panel = tk.Frame(main_container, bg='#16213e', width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0), pady=10)
        
        # Status frame with prominent win display
        status_frame = tk.Frame(right_panel, bg='#16213e')
        status_frame.pack(fill=tk.X, pady=15, padx=15)
        
        # Win banner (hidden by default, shown when game ends) - Modern design
        self.win_banner = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 18, "bold"),
            bg='#6366f1',
            fg='white',
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=20
        )
        self.win_banner.pack(fill=tk.X, pady=(0, 10))
        self.win_banner.pack_forget()  # Hide initially
        
        self.status_label = tk.Label(
            status_frame,
            text="⚪ White to move",
            font=("Segoe UI", 15, "bold"),
            bg='#16213e',
            fg='#e0e0ff',
            wraplength=280,
            pady=15
        )
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Move history frame with modern styling
        history_frame = tk.Frame(right_panel, bg='#16213e')
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=15)
        
        tk.Label(
            history_frame,
            text="📜 Move History",
            font=("Segoe UI", 13, "bold"),
            bg='#16213e',
            fg='#e0e0ff'
        ).pack(pady=(0, 10))
        
        # Scrollable move history
        history_scroll = tk.Scrollbar(history_frame)
        history_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            history_frame,
            height=15,
            width=28,
            font=("Consolas", 11),
            bg='#0f0f1e',
            fg='#d0d0e0',
            yscrollcommand=history_scroll.set,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scroll.config(command=self.history_text.yview)
        
        # Button frame with modern styling
        button_frame = tk.Frame(right_panel, bg='#16213e')
        button_frame.pack(fill=tk.X, pady=10, padx=15)
        
        # Helper function for modern buttons
        def create_btn(text, command, bg='#6366f1', hover='#7c3aed'):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Segoe UI", 11, "bold"),
                bg=bg,
                fg='white',
                activebackground=hover,
                relief=tk.FLAT,
                cursor='hand2',
                borderwidth=0,
                pady=10
            )
            btn.bind("<Enter>", lambda e: btn.config(bg=hover))
            btn.bind("<Leave>", lambda e: btn.config(bg=bg))
            return btn
        
        self.new_game_btn = create_btn("🔄 New Game", self.new_game, '#6366f1', '#7c3aed')
        self.new_game_btn.pack(fill=tk.X, pady=5)
        
        self.undo_btn = create_btn("↶ Undo Move", self.undo_move, '#8b5cf6', '#a78bfa')
        self.undo_btn.pack(fill=tk.X, pady=5)
        
        self.flip_btn = create_btn("🔃 Flip Board", self.flip_board, '#6366f1', '#7c3aed')
        self.flip_btn.pack(fill=tk.X, pady=5)
        
        self.ai_move_btn = create_btn("🤖 AI Move", self.make_ai_move, '#8b5cf6', '#a78bfa')
        self.ai_move_btn.pack(fill=tk.X, pady=5)
        
        self.update_display()
    
    def create_board(self):
        """Create the chess board GUI."""
        for row in range(8):
            for col in range(8):
                square = tk.Button(
                    self.board_frame,
                    width=7,
                    height=3,
                    font=("Arial", 24, "bold"),
                    command=lambda r=row, c=col: self.on_square_click(r, c),
                    relief=tk.FLAT,
                    borderwidth=0,
                    highlightthickness=0,
                    cursor='hand2'
                )
                square.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
                self.squares[(row, col)] = square
        
        # Configure grid weights for proper sizing
        for i in range(8):
            self.board_frame.grid_rowconfigure(i, weight=1, uniform='square')
            self.board_frame.grid_columnconfigure(i, weight=1, uniform='square')
    
    def square_to_coords(self, square: int) -> tuple:
        """Convert chess square index to (row, col)."""
        if self.board_flipped:
            row = square // 8
            col = 7 - (square % 8)
        else:
            row = 7 - (square // 8)
            col = square % 8
        return (row, col)
    
    def coords_to_square(self, row: int, col: int) -> int:
        """Convert (row, col) to chess square index."""
        if self.board_flipped:
            square = row * 8 + (7 - col)
        else:
            square = (7 - row) * 8 + col
        return square
    
    def get_piece_symbol(self, piece: chess.Piece) -> str:
        """Get Unicode symbol for a chess piece."""
        symbols = {
            chess.PAWN: '♟' if piece.color == chess.BLACK else '♙',
            chess.ROOK: '♜' if piece.color == chess.BLACK else '♖',
            chess.KNIGHT: '♞' if piece.color == chess.BLACK else '♘',
            chess.BISHOP: '♝' if piece.color == chess.BLACK else '♗',
            chess.QUEEN: '♛' if piece.color == chess.BLACK else '♕',
            chess.KING: '♚' if piece.color == chess.BLACK else '♔',
        }
        return symbols.get(piece.piece_type, '')
    
    def get_square_color(self, row: int, col: int) -> str:
        """Get modern base color for a square."""
        if (row + col) % 2 == 0:
            return '#ebecd0'  # Light square - soft cream
        else:
            return '#739552'  # Dark square - modern green
    
    def update_display(self):
        """Update the board display."""
        board = self.game.get_board()
        
        # Reset all squares
        for row in range(8):
            for col in range(8):
                square_idx = self.coords_to_square(row, col)
                square = self.squares[(row, col)]
                
                # Base color - ensure all squares are visible with borders
                base_color = self.get_square_color(row, col)
                square.config(
                    bg=base_color, 
                    activebackground=base_color,
                    relief=tk.RAISED,
                    borderwidth=2,
                    highlightthickness=1,
                    highlightbackground='#000000',
                    highlightcolor='#000000'
                )
                
                # Highlight last move
                if self.last_move:
                    from_row, from_col = self.square_to_coords(self.last_move.from_square)
                    to_row, to_col = self.square_to_coords(self.last_move.to_square)
                    if (row, col) == (from_row, from_col) or (row, col) == (to_row, to_col):
                        square.config(bg='#baca44')  # Highlighted yellow-green for last move
                
                # Highlight selected square
                if self.selected_square is not None:
                    sel_row, sel_col = self.square_to_coords(self.selected_square)
                    if (row, col) == (sel_row, sel_col):
                        square.config(bg='#f6f669')  # Bright yellow for selected
                
                # Highlight legal moves
                if self.selected_square is not None and square_idx in [m.to_square for m in self.legal_moves_for_selected]:
                    if (row, col) != (sel_row, sel_col):
                        # Highlight legal move destinations
                        square.config(bg='#a8d5ba')  # Soft mint green for legal moves
                
                # Highlight king in check
                if board.is_check():
                    king_square = board.king(board.turn)
                    if king_square is not None:
                        king_row, king_col = self.square_to_coords(king_square)
                        if (row, col) == (king_row, king_col):
                            square.config(bg='#ff5252')  # Bright red for check
                
                # Add piece
                piece = board.piece_at(square_idx)
                if piece:
                    square.config(text=self.get_piece_symbol(piece))
                else:
                    square.config(text='')
        
        # Update status and win banner
        status_text = ""
        if self.game.is_game_over():
            result = board.result()
            if result == "1-0":
                status_text = "White wins!"
                win_text = "🏆 WHITE WINS! 🏆"
                win_color = '#ffffff'
                text_color = '#000000'
            elif result == "0-1":
                status_text = "Black wins!"
                win_text = "🏆 BLACK WINS! 🏆"
                win_color = '#000000'
                text_color = '#ffffff'
            else:
                status_text = "Draw!"
                win_text = "🤝 IT'S A DRAW! 🤝"
                win_color = '#888888'
                text_color = '#ffffff'
            
            # Show win banner
            self.win_banner.config(
                text=win_text,
                bg=win_color,
                fg=text_color
            )
            self.win_banner.pack(fill=tk.X, pady=5)
        else:
            # Hide win banner during game
            self.win_banner.pack_forget()
            
            if board.turn == chess.WHITE:
                status_text = "⚪ White to move"
            else:
                status_text = "⚫ Black to move"
            
            # Add check indicator
            if board.is_check():
                status_text += " ⚠️ CHECK!"
            if board.is_checkmate():
                status_text = "Checkmate!"
            elif board.is_stalemate():
                status_text = "Stalemate - Draw!"
        
        self.status_label.config(text=status_text)
    
    def show_promotion_dialog(self) -> chess.PieceType:
        """Show modern dialog to choose promotion piece."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pawn Promotion")
        dialog.geometry("350x280")
        dialog.configure(bg='#0f0f1e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg='#1a1a2e', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="👑 Promote Pawn",
            font=("Segoe UI", 16, "bold"),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=22)
        
        # Content
        content = tk.Frame(dialog, bg='#0f0f1e')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text="Choose promotion piece:",
            font=("Segoe UI", 11),
            bg='#0f0f1e',
            fg='#a0a0c0'
        ).pack(pady=(0, 15))
        
        choice = [None]
        
        button_frame = tk.Frame(content, bg='#0f0f1e')
        button_frame.pack(fill=tk.X)
        
        pieces = [
            (chess.QUEEN, '♕ Queen'),
            (chess.ROOK, '♖ Rook'),
            (chess.BISHOP, '♗ Bishop'),
            (chess.KNIGHT, '♘ Knight')
        ]
        
        def create_promo_btn(piece_type, label):
            btn = tk.Button(
                button_frame,
                text=label,
                font=("Segoe UI", 11, "bold"),
                bg='#6366f1',
                fg='white',
                activebackground='#7c3aed',
                relief=tk.FLAT,
                cursor='hand2',
                borderwidth=0,
                pady=8,
                command=lambda pt=piece_type: self._set_promotion_choice(dialog, choice, pt)
            )
            btn.bind("<Enter>", lambda e: btn.config(bg='#7c3aed'))
            btn.bind("<Leave>", lambda e: btn.config(bg='#6366f1'))
            return btn
        
        for piece_type, label in pieces:
            btn = create_promo_btn(piece_type, label)
            btn.pack(fill=tk.X, pady=3)
        
        dialog.wait_window()
        return choice[0] if choice[0] else chess.QUEEN
    
    def _set_promotion_choice(self, dialog, choice, piece_type):
        """Helper for promotion dialog."""
        choice[0] = piece_type
        dialog.destroy()
    
    def on_square_click(self, row: int, col: int):
        """Handle square click."""
        if self.game.is_game_over():
            return
        
        square_idx = self.coords_to_square(row, col)
        board = self.game.get_board()
        
        # Check if it's human's turn
        is_human_turn = (board.turn == chess.WHITE) == self.human_plays_white
        if not is_human_turn:
            return
        
        if self.selected_square is None:
            # Select square
            piece = board.piece_at(square_idx)
            if piece and piece.color == board.turn:
                self.selected_square = square_idx
                # Get legal moves for this piece
                self.legal_moves_for_selected = [
                    m for m in board.legal_moves if m.from_square == square_idx
                ]
                self.update_display()
        else:
            # Try to make move
            move = None
            
            # Check if clicking same square (deselect)
            if square_idx == self.selected_square:
                self.selected_square = None
                self.legal_moves_for_selected = []
                self.update_display()
                return
            
            # Find the move
            for legal_move in self.legal_moves_for_selected:
                if legal_move.to_square == square_idx:
                    move = legal_move
                    break
            
            # Check for promotion
            if move and board.piece_at(self.selected_square) and \
               board.piece_at(self.selected_square).piece_type == chess.PAWN and \
               (square_idx // 8 == 0 or square_idx // 8 == 7):
                # Need promotion
                promotion_piece = self.show_promotion_dialog()
                move = chess.Move(self.selected_square, square_idx, promotion=promotion_piece)
            
            if move and move in board.legal_moves:
                # Get move notation before making the move
                move_san = board.san(move)
                is_white_move = board.turn == chess.WHITE
                
                self.game.make_move(move)
                self.last_move = move
                self.selected_square = None
                self.legal_moves_for_selected = []
                
                # Add to move history
                if is_white_move:  # White just moved
                    self.move_history.append(f"{len(self.move_history) + 1}. {move_san}")
                else:  # Black just moved
                    if self.move_history and '.' in self.move_history[-1] and '...' not in self.move_history[-1]:
                        self.move_history[-1] += f" {move_san}"
                    else:
                        self.move_history.append(f"{len(self.move_history) + 1}... {move_san}")
                
                self.update_history_display()
                self.update_display()
                
                # Check if game is over
                if self.game.is_game_over():
                    self.show_game_over()
                else:
                    # Auto-make AI move if it's AI's turn
                    if (board.turn == chess.WHITE) != self.human_plays_white:
                        self.root.after(500, self.make_ai_move)
            else:
                # Invalid move or clicked different piece - select new piece
                piece = board.piece_at(square_idx)
                if piece and piece.color == board.turn:
                    self.selected_square = square_idx
                    self.legal_moves_for_selected = [
                        m for m in board.legal_moves if m.from_square == square_idx
                    ]
                else:
                    self.selected_square = None
                    self.legal_moves_for_selected = []
                self.update_display()
    
    def update_history_display(self):
        """Update the move history display."""
        self.history_text.delete(1.0, tk.END)
        for move in self.move_history:
            self.history_text.insert(tk.END, move + "\n")
        self.history_text.see(tk.END)
    
    def make_ai_move(self):
        """Make AI move."""
        if self.game.is_game_over():
            return
        
        board = self.game.get_board()
        is_ai_turn = (board.turn == chess.WHITE) != self.human_plays_white
        if not is_ai_turn:
            return
        
        self.status_label.config(text="AI is thinking...")
        self.root.update()
        
        move, _ = self.mcts.search(self.game)
        
        if move is None:
            messagebox.showinfo("Game Over", "AI has no legal moves!")
            return
        
        # Get move notation before making the move
        move_san = board.san(move)
        is_white_move = board.turn == chess.WHITE
        
        self.game.make_move(move)
        self.last_move = move
        
        # Add to move history
        if is_white_move:  # White (AI) just moved
            self.move_history.append(f"{len(self.move_history) + 1}. {move_san}")
        else:  # Black (AI) just moved
            if self.move_history and '.' in self.move_history[-1] and '...' not in self.move_history[-1]:
                self.move_history[-1] += f" {move_san}"
            else:
                self.move_history.append(f"{len(self.move_history) + 1}... {move_san}")
        
        self.update_history_display()
        self.update_display()
        
        if self.game.is_game_over():
            self.show_game_over()
    
    def new_game(self):
        """Start a new game."""
        self.game = ChessGame()
        self.selected_square = None
        self.last_move = None
        self.legal_moves_for_selected = []
        self.move_history = []
        self.win_banner.pack_forget()  # Hide win banner
        self.update_history_display()
        self.update_display()
    
    def undo_move(self):
        """Undo the last move."""
        board = self.game.get_board()
        if len(board.move_stack) == 0:
            return
        
        # Undo one move
        board.pop()
        
        # Update move history
        if len(self.move_history) > 0:
            last_move = self.move_history[-1]
            # If it's a black move (has ...), remove it
            if '...' in last_move:
                self.move_history.pop()
            # If it's a white move, check if it has black's move too
            elif ' ' in last_move and '.' in last_move:
                # Has both moves, remove black's part
                parts = last_move.split(' ', 1)
                if len(parts) == 2:
                    self.move_history[-1] = parts[0]
                else:
                    self.move_history.pop()
            else:
                self.move_history.pop()
        
        self.selected_square = None
        self.legal_moves_for_selected = []
        self.last_move = board.peek() if len(board.move_stack) > 0 else None
        self.update_history_display()
        self.update_display()
    
    def flip_board(self):
        """Flip the board view."""
        self.board_flipped = not self.board_flipped
        self.selected_square = None
        self.legal_moves_for_selected = []
        self.update_display()
    
    def show_game_over(self):
        """Show game over message and save to database."""
        result = self.game.get_board().result()
        board = self.game.get_board()
        
        # Determine winner
        winner = None
        result_str = 'draw'
        if result == "1-0":
            winner = self.username if self.human_plays_white else "AI"
            result_str = '1-0'
            messagebox.showinfo("Game Over", "White wins!")
        elif result == "0-1":
            winner = "AI" if self.human_plays_white else self.username
            result_str = '0-1'
            messagebox.showinfo("Game Over", "Black wins!")
        else:
            result_str = 'draw'
            messagebox.showinfo("Game Over", "It's a draw!")
        
        # Save game to database
        try:
            from ui.database import get_database
            db = get_database()
            connection = db.get_connection()
            cursor = connection.cursor()
            
            # Get move list as string
            moves_str = ' '.join([board.san(move) for move in board.move_stack])
            
            # Determine player names
            player1 = self.username if self.human_plays_white else "AI"
            player2 = "AI" if self.human_plays_white else self.username
            
            # Insert game record
            cursor.execute("""
                INSERT INTO game_history (player1_username, player2_username, winner, result, moves)
                VALUES (%s, %s, %s, %s, %s)
            """, (player1, player2, winner, result_str, moves_str))
            
            connection.commit()
            cursor.close()
            
            # Update user stats if not guest
            if self.username != 'Guest':
                from ui.auth import AuthSystem
                auth = AuthSystem()
                if winner == self.username:
                    auth.update_user_stats(self.username, won=True)
                elif winner == "AI":
                    auth.update_user_stats(self.username, lost=True)
                else:
                    auth.update_user_stats(self.username, draw=True)
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()
