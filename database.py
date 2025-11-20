import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create necessary database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                package TEXT DEFAULT 'free',
                monthly_used INTEGER DEFAULT 0,
                gdrive_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Upload history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT,
                file_size INTEGER,
                upload_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, name, package='free'):
        """Add new user to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, name, package)
                VALUES (?, ?, ?)
            ''', (user_id, name, package))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # User already exists
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id):
        """Get user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_users(self):
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_package(self, user_id, package):
        """Update user package"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET package = ?
            WHERE user_id = ?
        ''', (package, user_id))
        
        conn.commit()
        conn.close()
    
    def update_monthly_usage(self, user_id, size):
        """Update user's monthly usage"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET monthly_used = monthly_used + ?
            WHERE user_id = ?
        ''', (size, user_id))
        
        conn.commit()
        conn.close()
    
    def reset_monthly_usage(self, user_id=None):
        """Reset monthly usage for user(s)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                UPDATE users 
                SET monthly_used = 0, last_reset = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
        else:
            # Reset all users
            cursor.execute('''
                UPDATE users 
                SET monthly_used = 0, last_reset = CURRENT_TIMESTAMP
            ''')
        
        conn.commit()
        conn.close()
    
    def update_gdrive_token(self, user_id, token):
        """Update Google Drive token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert token dict to JSON string
        token_str = json.dumps(token) if token else None
        
        cursor.execute('''
            UPDATE users 
            SET gdrive_token = ?
            WHERE user_id = ?
        ''', (token_str, user_id))
        
        conn.commit()
        conn.close()
    
    def add_upload_record(self, user_id, file_name, file_size, upload_type):
        """Add upload record to history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO uploads (user_id, file_name, file_size, upload_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, file_name, file_size, upload_type))
        
        conn.commit()
        conn.close()
    
    def get_user_uploads(self, user_id, limit=10):
        """Get user's upload history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM uploads 
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self):
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        
        # Total uploads
        cursor.execute('SELECT COUNT(*) as count FROM uploads')
        total_uploads = cursor.fetchone()['count']
        
        # Total data uploaded
        cursor.execute('SELECT SUM(file_size) as total FROM uploads')
        result = cursor.fetchone()
        total_data = result['total'] if result['total'] else 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_uploads': total_uploads,
            'total_data': total_data
        }
    
    def check_and_reset_monthly(self):
        """Check if month has changed and reset usage"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, last_reset FROM users
        ''')
        
        users = cursor.fetchall()
        current_month = datetime.now().month
        
        for user in users:
            last_reset = datetime.fromisoformat(user['last_reset'])
            if last_reset.month != current_month:
                self.reset_monthly_usage(user['user_id'])
        
        conn.close()