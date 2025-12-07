# MySQL/XAMPP Setup Guide for NeuroChess

## Prerequisites

1. **Install XAMPP**
   - Download from: https://www.apachefriends.org/
   - Install XAMPP on your computer
   - Default installation path: `C:\xampp`

## Setup Steps

### Step 1: Start MySQL in XAMPP

1. Open **XAMPP Control Panel**
2. Find **MySQL** in the list
3. Click **Start** button next to MySQL
4. Wait until MySQL status shows "Running" (green)

### Step 2: Install Python MySQL Connector

Open PowerShell/Command Prompt and run:

```bash
cd "C:\Users\Lidiya Getale\Desktop\NeuroChess"
pip install mysql-connector-python
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Database (Optional)

The default settings work with XAMPP:
- **Host**: localhost
- **User**: root
- **Password**: (empty)
- **Port**: 3306
- **Database**: neurochess (auto-created)

If you changed MySQL password in XAMPP, edit `ui/database.py`:

```python
self.config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',  # Change this
    'database': 'neurochess',
    'port': 3306
}
```

### Step 4: Run the Application

```bash
python main.py
```

The database and tables will be created automatically on first run!

## Database Structure

### Users Table
- `id` - Auto-increment primary key
- `username` - Unique username
- `password_hash` - SHA256 hashed password
- `created_at` - Registration timestamp
- `games_played` - Total games
- `wins` - Number of wins
- `losses` - Number of losses
- `draws` - Number of draws

### Game History Table (for future use)
- Stores game records with players and results

## Troubleshooting

### Error: "Could not connect to MySQL"

**Solution:**
1. Make sure XAMPP MySQL is running (green in XAMPP Control Panel)
2. Check if port 3306 is not blocked by firewall
3. Verify MySQL password in `ui/database.py` matches your XAMPP MySQL password

### Error: "Access denied for user 'root'@'localhost'"

**Solution:**
1. Open XAMPP Control Panel
2. Click **Config** next to MySQL
3. Select **my.ini** or **my.cnf**
4. Find `[mysqld]` section
5. Add or modify: `skip-grant-tables` (temporary, for testing)
6. Restart MySQL in XAMPP

Or set a password and update `ui/database.py` with the password.

### Error: "ModuleNotFoundError: No module named 'mysql'"

**Solution:**
```bash
pip install mysql-connector-python
```

## Viewing Data in phpMyAdmin

1. In XAMPP Control Panel, click **Admin** next to MySQL
2. Or go to: http://localhost/phpmyadmin
3. Select database: **neurochess**
4. View tables: **users**, **game_history**

## Default XAMPP MySQL Settings

- **Host**: localhost
- **Port**: 3306
- **Username**: root
- **Password**: (empty by default)
- **phpMyAdmin**: http://localhost/phpmyadmin

## Security Note

For production use, consider:
- Setting a strong MySQL root password
- Creating a dedicated database user (not root)
- Using environment variables for credentials
- Enabling SSL connections

