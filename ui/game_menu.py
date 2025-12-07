"""
Game menu for selecting game mode - Modern UI Design
"""

import tkinter as tk
from tkinter import font as tkfont
from ui.simple_gui import ChessGUI
from engine.neural_net import ChessNet
import torch
import os
from ui.database import get_database
from mysql.connector import Error
from datetime import datetime


class GameMenu:
    """Menu for selecting game mode with modern UI."""
    
    def __init__(self, username):
        """
        Initialize game menu.
        
        Args:
            username: Current logged in username
        """
        self.username = username
        self.root = tk.Tk()
        self.root.title("NeuroChess - Game Menu")
        self.root.geometry("1000x750")
        self.root.configure(bg='#0f0f1e')
        self.root.resizable(False, False)
        
        self.center_window()
        self.create_menu()
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_modern_button(self, parent, text, command, bg_color='#6366f1', hover_color='#7c3aed'):
        """Create a modern styled button with hover effects."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 13, "bold"),
            bg=bg_color,
            fg='white',
            activebackground=hover_color,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0,
            padx=30,
            pady=15
        )
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_menu(self):
        """Create the modern game menu interface."""
        # Main container with gradient effect simulation
        main_container = tk.Frame(self.root, bg='#0f0f1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header section with gradient background
        header_frame = tk.Frame(main_container, bg='#1a1a2e', height=200)
        header_frame.pack(fill=tk.X, pady=0)
        header_frame.pack_propagate(False)
        
        # Title with modern font
        title = tk.Label(
            header_frame,
            text="♔ NeuroChess ♚",
            font=("Segoe UI", 42, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack(pady=(40, 10))
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="AI-Powered Chess Experience",
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='#a0a0c0'
        )
        subtitle.pack(pady=(0, 20))
        
        # User info with modern styling
        user_frame = tk.Frame(main_container, bg='#16213e', height=80)
        user_frame.pack(fill=tk.X, pady=0)
        user_frame.pack_propagate(False)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 Welcome back, {self.username}!",
            font=("Segoe UI", 15, "bold"),
            bg='#16213e',
            fg='#e0e0ff'
        )
        user_label.pack(pady=25)
        
        # Content container for split layout
        content_container = tk.Frame(main_container, bg='#0f0f1e')
        content_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # LEFT COLUMN - Game Modes
        left_frame = tk.Frame(content_container, bg='#0f0f1e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Section title
        tk.Label(
            left_frame,
            text="Start New Game",
            font=("Segoe UI", 18, "bold"),
            bg='#0f0f1e',
            fg='#ffffff'
        ).pack(pady=(0, 30), anchor='w')
        
        # Two Player Mode Button
        two_player_btn = self.create_modern_button(
            left_frame,
            "🎮  Play with Friend\n(Two Players)",
            self.start_two_player,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        two_player_btn.pack(pady=10, fill=tk.X, ipady=10)
        
        # Play vs AI Button
        ai_btn = self.create_modern_button(
            left_frame,
            "🤖  Challenge the AI\n(Single Player)",
            self.start_ai_game,
            bg_color='#8b5cf6',
            hover_color='#a78bfa'
        )
        ai_btn.pack(pady=10, fill=tk.X, ipady=10)

        # RIGHT COLUMN - Recent Activity
        right_frame = tk.Frame(content_container, bg='#16213e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # History panel
        self.create_history_panel(right_frame)

        # Footer Buttons (Full Width)
        footer_frame = tk.Frame(main_container, bg='#0f0f1e')
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=40, pady=20)

        # View Full History Button
        history_btn = self.create_modern_button(
            footer_frame,
            "📜  View Full History",
            self.view_history,
            bg_color='#10b981',
            hover_color='#34d399'
        )
        history_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Logout button
        logout_btn = self.create_modern_button(
            footer_frame,
            "← Logout",
            self.logout,
            bg_color='#374151',
            hover_color='#4b5563'
        )
        logout_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

    def create_history_panel(self, parent):
        """Create the recent activity panel."""
        # Header
        header = tk.Frame(parent, bg='#1a1a2e', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📋 Recent Activity",
            font=("Segoe UI", 12, "bold"),
            bg='#1a1a2e',
            fg='#e0e0ff'
        ).pack(side=tk.LEFT, padx=15, pady=10)

        # List Container
        self.history_list_frame = tk.Frame(parent, bg='#16213e')
        self.history_list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.load_recent_games()

    def load_recent_games(self):
        """Load recent games into the history panel."""
        try:
            db = get_database()
            connection = db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM game_history 
                WHERE player1_username = %s OR player2_username = %s 
                ORDER BY played_at DESC 
                LIMIT 5
            """, (self.username, self.username))
            
            games = cursor.fetchall()
            cursor.close()
            
            if not games:
                tk.Label(
                    self.history_list_frame,
                    text="No games played yet.\nStart a game to see history!",
                    font=("Segoe UI", 10, "italic"),
                    bg='#16213e',
                    fg='#a0a0c0',
                    justify=tk.CENTER
                ).pack(expand=True)
            else:
                for game in games:
                    self.create_history_item(game)
                    
        except Error as e:
            print(f"Error loading recent games: {e}")
            tk.Label(
                self.history_list_frame,
                text="Unable to load history",
                font=("Segoe UI", 10),
                bg='#16213e',
                fg='#ef4444'
            ).pack(pady=10)

    def create_history_item(self, game):
        """Create a single history item widget."""
        item_frame = tk.Frame(self.history_list_frame, bg='#1a1a2e', height=60)
        item_frame.pack(fill=tk.X, pady=1, padx=5)
        item_frame.pack_propagate(False)
        
        # Determine details
        opponent = game['player2_username'] if game['player1_username'] == self.username else game['player1_username']
        winner = game['winner']
        
        if winner == self.username:
            result_color = '#10b981' # Green
            result_text = "V"
        elif winner == opponent:
            result_color = '#ef4444' # Red
            result_text = "L"
        else:
            result_color = '#f59e0b' # Yellow
            result_text = "D"
            
        date_str = game['played_at'].strftime('%b %d, %H:%M')

        # Result Indicator
        tk.Label(
            item_frame,
            text=result_text,
            font=("Segoe UI", 14, "bold"),
            bg='#1a1a2e',
            fg=result_color,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Game Info
        info_frame = tk.Frame(item_frame, bg='#1a1a2e')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(
            info_frame,
            text=f"vs {opponent}",
            font=("Segoe UI", 11, "bold"),
            bg='#1a1a2e',
            fg='white',
            anchor='w'
        ).pack(fill=tk.X)
        
        tk.Label(
            info_frame,
            text=date_str,
            font=("Segoe UI", 9),
            bg='#1a1a2e',
            fg='#a0a0c0',
            anchor='w'
        ).pack(fill=tk.X)
    
    def start_two_player(self):
        """Start two-player game."""
        # Show dialog to get player names
        dialog = tk.Toplevel(self.root)
        dialog.title("Two Player Setup")
        dialog.geometry("450x350")
        dialog.configure(bg='#0f0f1e')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f'450x350+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#1a1a2e', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚔️ Two Player Setup",
            font=("Segoe UI", 20, "bold"),
            bg='#1a1a2e',
            fg='white'
        ).pack(pady=25)
        
        # Form container
        frame = tk.Frame(dialog, bg='#0f0f1e')
        frame.pack(pady=30, padx=40, fill=tk.BOTH, expand=True)
        
        # Player 1
        tk.Label(
            frame,
            text="⚪ Player 1 (White):",
            font=("Segoe UI", 12, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        p1_entry = tk.Entry(
            frame,
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=2
        )
        p1_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)
        p1_entry.insert(0, self.username)
        p1_entry.focus()
        
        # Player 2
        tk.Label(
            frame,
            text="⚫ Player 2 (Black):",
            font=("Segoe UI", 12, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        p2_entry = tk.Entry(
            frame,
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=2
        )
        p2_entry.pack(fill=tk.X, pady=(0, 30), ipady=8)
        p2_entry.insert(0, "Player 2")
        p2_entry.bind('<Return>', lambda e: start_game())
        
        def start_game():
            p1_name = p1_entry.get().strip() or "Player 1"
            p2_name = p2_entry.get().strip() or "Player 2"
            dialog.destroy()
            self.root.destroy()
            from ui.two_player_gui import TwoPlayerChessGUI
            TwoPlayerChessGUI(p1_name, p2_name).run()
        
        # Start button
        btn = self.create_modern_button(
            frame,
            "🎮 Start Game",
            start_game,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        btn.pack(fill=tk.X, ipady=5)
        
        dialog.wait_window()
    
    def start_ai_game(self):
        """Start game vs AI."""
        self.root.destroy()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = ChessNet().to(device)
        
        # Try to load checkpoint
        checkpoint_dir = 'models/checkpoints'
        if os.path.exists(checkpoint_dir):
            checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.pth')]
            if checkpoints:
                checkpoint_path = os.path.join(checkpoint_dir, sorted(checkpoints)[-1])
                try:
                    checkpoint = torch.load(checkpoint_path, map_location=device)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    print(f"Loaded model from {checkpoint_path}")
                except:
                    print("Warning: Could not load checkpoint. Using untrained model.")
        
        model.eval()
        gui = ChessGUI(model, device=device, username=self.username)
        gui.run()
    
    def view_history(self):
        """View game history."""
        self.root.destroy()
        from ui.game_history import GameHistoryGUI
        history = GameHistoryGUI(self.username)
        history.run()
    
    def logout(self):
        """Logout and return to login."""
        self.root.destroy()
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ui.auth import AuthGUI
        
        def on_login_success(username):
            from ui.game_menu import GameMenu
            menu = GameMenu(username)
            menu.run()
        
        auth = AuthGUI(on_login_success)
        auth.run()
    
    def run(self):
        """Start the menu."""
        self.root.mainloop()

