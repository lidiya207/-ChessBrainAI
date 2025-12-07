"""
Two-player chess GUI with modern design - play with a friend
"""

import tkinter as tk
from tkinter import messagebox
import chess
from engine.game import ChessGame


class TwoPlayerChessGUI:
    """GUI for two-player chess game."""
    
    def __init__(self, player1_name="Player 1", player2_name="Player 2"):
        """
        Initialize two-player chess GUI.
        
        Args:
            player1_name: Name of player 1 (White)
            player2_name: Name of player 2 (Black)
        """
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.game = ChessGame()
        self.selected_square = None
        self.last_move = None
        self.legal_moves_for_selected = []
        self.board_flipped = False
        self.move_history = []
        
        # Create main window with modern styling
        self.root = tk.Tk()
        self.root.title("♔ NeuroChess - Two Player Mode")
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
        tk.Label(coord_top, text="  ", bg='#1a1a2e', width=2).pack(side=tk.LEFT)
        for col in range(8):
            label = tk.Label(
                coord_top,
                text=chr(97 + col),
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
        tk.Label(coord_bottom, text="  ", bg='#1a1a2e', width=2).pack(side=tk.LEFT)
        for col in range(8):
            label = tk.Label(
                coord_bottom,
                text=chr(97 + col),
                font=("Segoe UI", 11, "bold"),
                bg='#1a1a2e',
                fg='#a0a0c0',
                width=7
            )
            label.pack(side=tk.LEFT)
        
        # Right panel - Info and controls with modern styling
        right_panel = tk.Frame(main_container, bg='#16213e', width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0), pady=10)
        
        # Player info with modern styling
        player_frame = tk.Frame(right_panel, bg='#16213e')
        player_frame.pack(fill=tk.X, pady=15, padx=15)
        
        self.white_player_label = tk.Label(
            player_frame,
            text=f"⚪ {self.player1_name}",
            font=("Segoe UI", 13, "bold"),
            bg='#16213e',
            fg='#e0e0ff',
            anchor='w',
            padx=10,
            pady=8
        )
        self.white_player_label.pack(fill=tk.X, pady=5)
        
        self.black_player_label = tk.Label(
            player_frame,
            text=f"⚫ {self.player2_name}",
            font=("Segoe UI", 13, "bold"),
            bg='#16213e',
            fg='#a0a0c0',
            anchor='w',
            padx=10,
            pady=8
        )
        self.black_player_label.pack(fill=tk.X, pady=5)
        
        # Status frame with win banner - modern styling
        status_frame = tk.Frame(right_panel, bg='#16213e')
        status_frame.pack(fill=tk.X, pady=10, padx=15)
        
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
        self.win_banner.pack_forget()
        
        self.status_label = tk.Label(
            status_frame,
            text=f"⚪ {self.player1_name} to move",
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
        
        self.menu_btn = create_btn("← Back to Menu", self.back_to_menu, '#374151', '#4b5563')
        self.menu_btn.pack(fill=tk.X, pady=5)
        
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
        
        # Update player labels with modern highlighting
        if board.turn == chess.WHITE:
            self.white_player_label.config(fg='#6ef1ff', font=("Segoe UI", 14, "bold"))
            self.black_player_label.config(fg='#a0a0c0', font=("Segoe UI", 13))
        else:
            self.white_player_label.config(fg='#a0a0c0', font=("Segoe UI", 13))
            self.black_player_label.config(fg='#6ef1ff', font=("Segoe UI", 14, "bold"))
        
        # Reset all squares
        for row in range(8):
            for col in range(8):
                square_idx = self.coords_to_square(row, col)
                square = self.squares[(row, col)]
                
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
                    sel_row, sel_col = self.square_to_coords(self.selected_square)
                    if (row, col) != (sel_row, sel_col):
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
        
        # Update status
        status_text = ""
        if self.game.is_game_over():
            result = board.result()
            if result == "1-0":
                status_text = f"{self.player1_name} (White) wins!"
                win_text = f"🏆 {self.player1_name} WINS! 🏆"
                win_color = '#ffffff'
                text_color = '#000000'
            elif result == "0-1":
                status_text = f"{self.player2_name} (Black) wins!"
                win_text = f"🏆 {self.player2_name} WINS! 🏆"
                win_color = '#000000'
                text_color = '#ffffff'
            else:
                status_text = "Draw!"
                win_text = "🤝 IT'S A DRAW! 🤝"
                win_color = '#888888'
                text_color = '#ffffff'
            
            self.win_banner.config(text=win_text, bg=win_color, fg=text_color)
            self.win_banner.pack(fill=tk.X, pady=5)
        else:
            self.win_banner.pack_forget()
            turn = self.player1_name if board.turn == chess.WHITE else self.player2_name
            status_text = f"{turn} to move"
            
            if board.is_check():
                status_text += " - CHECK!"
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
        
        if self.selected_square is None:
            piece = board.piece_at(square_idx)
            if piece and piece.color == board.turn:
                self.selected_square = square_idx
                self.legal_moves_for_selected = [
                    m for m in board.legal_moves if m.from_square == square_idx
                ]
                self.update_display()
        else:
            move = None
            
            if square_idx == self.selected_square:
                self.selected_square = None
                self.legal_moves_for_selected = []
                self.update_display()
                return
            
            for legal_move in self.legal_moves_for_selected:
                if legal_move.to_square == square_idx:
                    move = legal_move
                    break
            
            if move and board.piece_at(self.selected_square) and \
               board.piece_at(self.selected_square).piece_type == chess.PAWN and \
               (square_idx // 8 == 0 or square_idx // 8 == 7):
                promotion_piece = self.show_promotion_dialog()
                move = chess.Move(self.selected_square, square_idx, promotion=promotion_piece)
            
            if move and move in board.legal_moves:
                move_san = board.san(move)
                is_white_move = board.turn == chess.WHITE
                
                self.game.make_move(move)
                self.last_move = move
                self.selected_square = None
                self.legal_moves_for_selected = []
                
                if is_white_move:
                    self.move_history.append(f"{len(self.move_history) + 1}. {move_san}")
                else:
                    if self.move_history and '.' in self.move_history[-1] and '...' not in self.move_history[-1]:
                        self.move_history[-1] += f" {move_san}"
                    else:
                        self.move_history.append(f"{len(self.move_history) + 1}... {move_san}")
                
                self.update_history_display()
                self.update_display()
                
                if self.game.is_game_over():
                    self.show_game_over()
            else:
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
    
    def new_game(self):
        """Start a new game."""
        self.game = ChessGame()
        self.selected_square = None
        self.last_move = None
        self.legal_moves_for_selected = []
        self.move_history = []
        self.win_banner.pack_forget()
        self.update_history_display()
        self.update_display()
    
    def undo_move(self):
        """Undo the last move."""
        board = self.game.get_board()
        if len(board.move_stack) == 0:
            return
        
        board.pop()
        
        if len(self.move_history) > 0:
            last_move = self.move_history[-1]
            if '...' in last_move:
                self.move_history.pop()
            elif ' ' in last_move and '.' in last_move:
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
        self.win_banner.pack_forget()
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
            winner = self.player1_name
            result_str = '1-0'
            messagebox.showinfo("Game Over", f"{self.player1_name} (White) wins!")
        elif result == "0-1":
            winner = self.player2_name
            result_str = '0-1'
            messagebox.showinfo("Game Over", f"{self.player2_name} (Black) wins!")
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
            
            # Insert game record
            cursor.execute("""
                INSERT INTO game_history (player1_username, player2_username, winner, result, moves)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.player1_name, self.player2_name, winner, result_str, moves_str))
            
            connection.commit()
            cursor.close()
            
            # Update user stats if not guest
            from ui.auth import AuthSystem
            auth = AuthSystem()
            
            if self.player1_name != 'Guest':
                if winner == self.player1_name:
                    auth.update_user_stats(self.player1_name, won=True)
                elif winner == self.player2_name:
                    auth.update_user_stats(self.player1_name, lost=True)
                else:
                    auth.update_user_stats(self.player1_name, draw=True)
            
            if self.player2_name != 'Guest':
                if winner == self.player2_name:
                    auth.update_user_stats(self.player2_name, won=True)
                elif winner == self.player1_name:
                    auth.update_user_stats(self.player2_name, lost=True)
                else:
                    auth.update_user_stats(self.player2_name, draw=True)
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def back_to_menu(self):
        """Return to game menu."""
        self.root.destroy()
        # Import here to avoid circular imports
        from ui.game_menu import GameMenu
        menu = GameMenu(self.player1_name)
        menu.run()
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()

