"""
MySQL Database connection and setup for NeuroChess
Uses XAMPP MySQL
"""

import mysql.connector
from mysql.connector import Error
import os


class Database:
    """MySQL database connection and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self.connection = None
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Default XAMPP MySQL password (empty)
            'database': 'neurochess',
            'port': 3306
        }
        self.connect()
        self.create_database_if_not_exists()
        self.create_tables()
    
    def connect(self):
        """Connect to MySQL server and database."""
        try:
            # Try to connect directly to the database
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"Connected to MySQL database '{self.config['database']}'")
        except Error as e:
            # If database doesn't exist, connect without it first
            if "Unknown database" in str(e):
                try:
                    temp_config = self.config.copy()
                    temp_config.pop('database', None)
                    self.connection = mysql.connector.connect(**temp_config)
                    if self.connection.is_connected():
                        print("Connected to MySQL server (creating database...)")
                except Error as e2:
                    print(f"Error connecting to MySQL: {e2}")
                    self._print_connection_help()
                    raise
            else:
                print(f"Error connecting to MySQL: {e}")
                self._print_connection_help()
                raise
    
    def _print_connection_help(self):
        """Print connection help message."""
        print("\nMake sure XAMPP MySQL is running!")
        print("1. Open XAMPP Control Panel")
        print("2. Start MySQL service")
        print("3. Default settings:")
        print("   - Host: localhost")
        print("   - User: root")
        print("   - Password: (empty)")
        print("   - Database: neurochess")
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.execute(f"USE {self.config['database']}")
            print(f"Database '{self.config['database']}' ready")
            cursor.close()
        except Error as e:
            print(f"Error creating database: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables."""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                games_played INT DEFAULT 0,
                wins INT DEFAULT 0,
                losses INT DEFAULT 0,
                draws INT DEFAULT 0,
                INDEX idx_username (username)
            )
            """
            cursor.execute(create_users_table)
            
            # Game history table (optional, for future use)
            create_games_table = """
            CREATE TABLE IF NOT EXISTS game_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player1_username VARCHAR(50),
                player2_username VARCHAR(50),
                winner VARCHAR(50),
                result VARCHAR(10),
                moves TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player1_username) REFERENCES users(username) ON DELETE SET NULL,
                FOREIGN KEY (player2_username) REFERENCES users(username) ON DELETE SET NULL
            )
            """
            cursor.execute(create_games_table)
            
            self.connection.commit()
            cursor.close()
            print("Tables created successfully")
        except Error as e:
            print(f"Error creating tables: {e}")
            raise
    
    def get_connection(self):
        """Get database connection."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            # Ensure we're using the correct database
            try:
                if hasattr(self.connection, 'database') and self.connection.database != self.config['database']:
                    self.create_database_if_not_exists()
            except:
                # If we connected without database, create it
                self.create_database_if_not_exists()
        return self.connection
    
    def close(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")


# Global database instance
_db_instance = None

def get_database():
    """Get global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

