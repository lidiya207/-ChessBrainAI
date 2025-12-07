"""
Game History Viewer - Modern UI
Shows past games with details and statistics
"""

import tkinter as tk
from tkinter import ttk
from ui.database import get_database
from mysql.connector import Error
from datetime import datetime


class GameHistoryGUI:
    """Modern GUI for viewing game history."""
    
    def __init__(self, username):
        """
        Initialize game history viewer.
        
        Args:
            username: Current logged in username
        """
        self.username = username
        self.db = get_database()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("♟️ NeuroChess - Game History")
        self.root.geometry("900x700")
        self.root.configure(bg='#0f0f1e')
        self.root.resizable(True, True)
        
        self.center_window()
        self.create_ui()
        self.load_history()
    
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
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg='white',
            activebackground=hover_color,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0,
            pady=10
        )
        
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_ui(self):
        """Create the modern UI."""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a2e', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="📜 Game History",
            font=("Segoe UI", 28, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack(pady=(25, 5))
        
        subtitle = tk.Label(
            header_frame,
            text=f"Viewing games for {self.username}",
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='#a0a0c0'
        )
        subtitle.pack(pady=(0, 15))
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#0f0f1e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Stats section
        stats_frame = tk.Frame(content_frame, bg='#16213e')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_stats_display(stats_frame)
        
        # History table
        history_frame = tk.Frame(content_frame, bg='#16213e')
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            history_frame,
            text="📋 Recent Games",
            font=("Segoe UI", 14, "bold"),
            bg='#16213e',
            fg='#e0e0ff'
        ).pack(pady=15, padx=20, anchor='w')
        
        # Create treeview for game list
        self.create_game_list(history_frame)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#0f0f1e')
        button_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        back_btn = self.create_modern_button(
            button_frame,
            "← Back to Menu",
            self.back_to_menu,
            bg_color='#374151',
            hover_color='#4b5563'
        )
        back_btn.pack(side=tk.LEFT)
        
        refresh_btn = self.create_modern_button(
            button_frame,
            "🔄 Refresh",
            self.load_history,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        refresh_btn.pack(side=tk.RIGHT)
    
    def create_stats_display(self, parent):
        """Create statistics display."""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT games_played, wins, losses, draws FROM users WHERE username = %s",
                (self.username,)
            )
            stats = cursor.fetchone()
            cursor.close()
            
            if stats:
                stats_container = tk.Frame(parent, bg='#16213e')
                stats_container.pack(fill=tk.X, padx=20, pady=15)
                
                # Create stat boxes
                stat_items = [
                    ("🎮 Games Played", stats['games_played'], '#6366f1'),
                    ("🏆 Wins", stats['wins'], '#10b981'),
                    ("❌ Losses", stats['losses'], '#ef4444'),
                    ("🤝 Draws", stats['draws'], '#f59e0b')
                ]
                
                for label, value, color in stat_items:
                    stat_box = tk.Frame(stats_container, bg='#1a1a2e')
                    stat_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
                    
                    tk.Label(
                        stat_box,
                        text=str(value),
                        font=("Segoe UI", 24, "bold"),
                        bg='#1a1a2e',
                        fg=color
                    ).pack(pady=(10, 0))
                    
                    tk.Label(
                        stat_box,
                        text=label,
                        font=("Segoe UI", 10),
                        bg='#1a1a2e',
                        fg='#a0a0c0'
                    ).pack(pady=(0, 10))
        except Error as e:
            print(f"Error loading stats: {e}")
    
    def create_game_list(self, parent):
        """Create game list with treeview."""
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(parent, bg='#16213e')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#1a1a2e",
                       foreground="#e0e0ff",
                       fieldbackground="#1a1a2e",
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#6366f1",
                       foreground="white",
                       borderwidth=0,
                       font=("Segoe UI", 10, "bold"))
        style.map('Treeview', background=[('selected', '#6366f1')])
        
        columns = ('Date', 'Opponent', 'Result', 'Winner')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        # Define headings
        self.tree.heading('Date', text='📅 Date & Time')
        self.tree.heading('Opponent', text='👤 Opponent')
        self.tree.heading('Result', text='🎯 Result')
        self.tree.heading('Winner', text='🏆 Winner')
        
        # Define column widths
        self.tree.column('Date', width=200)
        self.tree.column('Opponent', width=150)
        self.tree.column('Result', width=100)
        self.tree.column('Winner', width=150)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
    
    def load_history(self):
        """Load game history from database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get games where user was player1 or player2
            cursor.execute("""
                SELECT * FROM game_history 
                WHERE player1_username = %s OR player2_username = %s 
                ORDER BY played_at DESC 
                LIMIT 100
            """, (self.username, self.username))
            
            games = cursor.fetchall()
            cursor.close()
            
            if not games:
                # Add a message if no games found
                self.tree.insert('', 'end', values=(
                    'No games yet',
                    '-',
                    '-',
                    'Start playing to see history!'
                ))
            else:
                for game in games:
                    # Determine opponent
                    opponent = game['player2_username'] if game['player1_username'] == self.username else game['player1_username']
                    
                    # Format date
                    date_str = game['played_at'].strftime('%Y-%m-%d %H:%M')
                    
                    # Determine result from user's perspective
                    if game['winner'] == self.username:
                        result = 'Win'
                    elif game['winner'] == opponent:
                        result = 'Loss'
                    elif game['result'] == 'draw':
                        result = 'Draw'
                    else:
                        result = game['result']
                    
                    winner = game['winner'] if game['winner'] else 'Draw'
                    
                    self.tree.insert('', 'end', values=(
                        date_str,
                        opponent,
                        result,
                        winner
                    ))
        except Error as e:
            print(f"Error loading game history: {e}")
            self.tree.insert('', 'end', values=(
                'Error loading games',
                '-',
                '-',
                'Please try again'
            ))
    
    def back_to_menu(self):
        """Return to game menu."""
        self.root.destroy()
        from ui.game_menu import GameMenu
        menu = GameMenu(self.username)
        menu.run()
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()
