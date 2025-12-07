"""
Game menu for selecting game mode - Modern UI Design
"""

import tkinter as tk
from tkinter import font as tkfont
from ui.simple_gui import ChessGUI
from engine.neural_net import ChessNet
import torch
import os


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
        self.root.geometry("600x750")
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
        
        # Menu section
        menu_frame = tk.Frame(main_container, bg='#0f0f1e')
        menu_frame.pack(pady=40, padx=60, fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            menu_frame,
            text="Choose Your Game Mode",
            font=("Segoe UI", 18, "bold"),
            bg='#0f0f1e',
            fg='#ffffff'
        ).pack(pady=(0, 30))
        
        # Two Player Mode Button
        two_player_btn = self.create_modern_button(
            menu_frame,
            "🎮  Play with Friend\n(Two Players)",
            self.start_two_player,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        two_player_btn.pack(pady=15, fill=tk.X, ipady=10)
        
        # Play vs AI Button
        ai_btn = self.create_modern_button(
            menu_frame,
            "🤖  Challenge the AI\n(Single Player)",
            self.start_ai_game,
            bg_color='#8b5cf6',
            hover_color='#a78bfa'
        )
        ai_btn.pack(pady=15, fill=tk.X, ipady=10)
        
        # View History Button
        history_btn = self.create_modern_button(
            menu_frame,
            "📜  View Game History",
            self.view_history,
            bg_color='#10b981',
            hover_color='#34d399'
        )
        history_btn.pack(pady=15, fill=tk.X, ipady=10)
        
        # Spacer
        tk.Frame(menu_frame, bg='#0f0f1e', height=30).pack()
        
        # Logout button with different styling
        logout_btn = self.create_modern_button(
            menu_frame,
            "← Logout",
            self.logout,
            bg_color='#374151',
            hover_color='#4b5563'
        )
        logout_btn.pack(pady=10, fill=tk.X, ipady=5)
    
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

