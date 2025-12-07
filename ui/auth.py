"""
User authentication system for NeuroChess - Modern UI
Login and registration interface using MySQL with premium design
"""

import tkinter as tk
from tkinter import messagebox
import hashlib
from ui.database import get_database
from mysql.connector import Error


class AuthSystem:
    """Handles user authentication - login and registration using MySQL."""
    
    def __init__(self):
        """Initialize authentication system."""
        self.db = get_database()
    
    def hash_password(self, password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password):
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            True if successful, False if username already exists
        """
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                return False
            
            # Insert new user
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error registering user: {e}")
            return False
    
    def login(self, username, password):
        """
        Login a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            True if successful, False if invalid credentials
        """
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "SELECT id FROM users WHERE username = %s AND password_hash = %s",
                (username, password_hash)
            )
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            print(f"Error logging in: {e}")
            return False
    
    def get_user_stats(self, username):
        """Get user statistics."""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT games_played, wins, losses, draws FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error getting user stats: {e}")
            return None
    
    def update_user_stats(self, username, won=False, lost=False, draw=False):
        """Update user game statistics."""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            if won:
                cursor.execute(
                    "UPDATE users SET games_played = games_played + 1, wins = wins + 1 WHERE username = %s",
                    (username,)
                )
            elif lost:
                cursor.execute(
                    "UPDATE users SET games_played = games_played + 1, losses = losses + 1 WHERE username = %s",
                    (username,)
                )
            elif draw:
                cursor.execute(
                    "UPDATE users SET games_played = games_played + 1, draws = draws + 1 WHERE username = %s",
                    (username,)
                )
            
            connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error updating user stats: {e}")


class AuthGUI:
    """GUI for user authentication."""
    
    def __init__(self, on_login_success):
        """
        Initialize authentication GUI.
        
        Args:
            on_login_success: Callback function called with username when login succeeds
        """
        self.auth_system = AuthSystem()
        self.on_login_success = on_login_success
        self.current_user = None
        
        # Check database connection
        try:
            get_database()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not connect to MySQL database!\n\n"
                f"Error: {str(e)}\n\n"
                f"Please make sure:\n"
                f"1. XAMPP is installed\n"
                f"2. MySQL service is running in XAMPP\n"
                f"3. Default MySQL settings:\n"
                f"   - Host: localhost\n"
                f"   - User: root\n"
                f"   - Password: (empty)\n\n"
                f"You can change settings in ui/database.py"
            )
            return
        
        # Create main window with modern styling
        self.root = tk.Tk()
        self.root.title("♔ NeuroChess - Login")
        self.root.geometry("500x650")  # Increased height for better visibility
        self.root.configure(bg='#0f0f1e')
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Create login frame
        self.show_login()
    
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
            font=("Segoe UI", 12, "bold"),
            bg=bg_color,
            fg='white',
            activebackground=hover_color,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0,
            pady=12
        )
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def show_login(self):
        """Show modern login interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header section - reduced height
        header_frame = tk.Frame(self.root, bg='#1a1a2e', height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header_frame,
            text="♔ NeuroChess ♚",
            font=("Segoe UI", 30, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack(pady=(25, 5))
        
        subtitle = tk.Label(
            header_frame,
            text="Login to Play",
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='#a0a0c0'
        )
        subtitle.pack(pady=(0, 15))
        
        # Login form container - reduced padding
        login_frame = tk.Frame(self.root, bg='#0f0f1e')
        login_frame.pack(pady=25, padx=50, fill=tk.BOTH, expand=True)
        
        # Username
        tk.Label(
            login_frame,
            text="👤 Username",
            font=("Segoe UI", 11, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 6))
        
        self.username_entry = tk.Entry(
            login_frame,
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 15), ipady=9)
        self.username_entry.focus()
        
        # Password
        tk.Label(
            login_frame,
            text="🔒 Password",
            font=("Segoe UI", 11, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 6))
        
        self.password_entry = tk.Entry(
            login_frame,
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            show='●',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 20), ipady=9)
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Buttons
        button_frame = tk.Frame(login_frame, bg='#0f0f1e')
        button_frame.pack(fill=tk.X, pady=5)
        
        # Login button
        login_btn = self.create_modern_button(
            button_frame,
            "🎮 Login",
            self.login,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        login_btn.pack(fill=tk.X, pady=4)
        
        # Register button
        register_btn = self.create_modern_button(
            button_frame,
            "✨ Create New Account",
            self.show_register,
            bg_color='#8b5cf6',
            hover_color='#a78bfa'
        )
        register_btn.pack(fill=tk.X, pady=4)
        
        # Guest button
        guest_btn = self.create_modern_button(
            button_frame,
            "👻 Play as Guest",
            self.play_as_guest,
            bg_color='#374151',
            hover_color='#4b5563'
        )
        guest_btn.pack(fill=tk.X, pady=4)
    
    def show_register(self):
        """Show modern registration interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header section
        header_frame = tk.Frame(self.root, bg='#1a1a2e', height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header_frame,
            text="✨ Create Account",
            font=("Segoe UI", 28, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(
            header_frame,
            text="Join the NeuroChess community",
            font=("Segoe UI", 12),
            bg='#1a1a2e',
            fg='#a0a0c0'
        )
        subtitle.pack(pady=(0, 15))
        
        # Register form container
        register_frame = tk.Frame(self.root, bg='#0f0f1e')
        register_frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)
        
        # Username
        tk.Label(
            register_frame,
            text="👤 Username",
            font=("Segoe UI", 11, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 6))
        
        self.reg_username_entry = tk.Entry(
            register_frame,
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.reg_username_entry.pack(fill=tk.X, pady=(0, 15), ipady=9)
        self.reg_username_entry.focus()
        
        # Password
        tk.Label(
            register_frame,
            text="🔒 Password",
            font=("Segoe UI", 11, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 6))
        
        self.reg_password_entry = tk.Entry(
            register_frame,
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            show='●',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.reg_password_entry.pack(fill=tk.X, pady=(0, 15), ipady=9)
        
        # Confirm Password
        tk.Label(
            register_frame,
            text="🔐 Confirm Password",
            font=("Segoe UI", 11, "bold"),
            bg='#0f0f1e',
            fg='#e0e0ff',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 6))
        
        self.reg_confirm_entry = tk.Entry(
            register_frame,
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white',
            insertbackground='white',
            show='●',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.reg_confirm_entry.pack(fill=tk.X, pady=(0, 25), ipady=9)
        self.reg_confirm_entry.bind('<Return>', lambda e: self.register())
        
        # Buttons
        button_frame = tk.Frame(register_frame, bg='#0f0f1e')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create Account button
        register_btn = self.create_modern_button(
            button_frame,
            "🎮 Create Account",
            self.register,
            bg_color='#6366f1',
            hover_color='#7c3aed'
        )
        register_btn.pack(fill=tk.X, pady=5)
        
        # Back button
        back_btn = self.create_modern_button(
            button_frame,
            "← Back to Login",
            self.show_login,
            bg_color='#374151',
            hover_color='#4b5563'
        )
        back_btn.pack(fill=tk.X, pady=5)
    
    def login(self):
        """Handle login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        try:
            if self.auth_system.login(username, password):
                self.current_user = username
                self.root.destroy()
                self.on_login_success(username)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{str(e)}")
    
    def register(self):
        """Handle registration."""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            if self.auth_system.register(username, password):
                messagebox.showinfo("Success", f"Account created for {username}!\nYou can now login.")
                self.show_login()
            else:
                messagebox.showerror("Error", "Username already exists")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not create account:\n{str(e)}")
    
    def play_as_guest(self):
        """Play as guest without login."""
        self.current_user = "Guest"
        self.root.destroy()
        self.on_login_success("Guest")
    
    def run(self):
        """Start the authentication GUI."""
        self.root.mainloop()
