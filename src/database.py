import sqlite3
import logging
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseHandler:
    """
    A class to handle all interactions with the SQLite database.
    Manages its own connection and cursor.
    """
    def __init__(self, db_path):
        """
        Initializes the DatabaseHandler.
        :param db_path: The file path for the SQLite database.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Establishes a connection to the database and creates a cursor.
        Returns True on success, False on failure.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logging.info(f"Successfully connected to database at {self.db_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {e}")
            return False

    def close(self):
        """Closes the database connection if it exists."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def setup_table(self):
        """
        Creates the 'archive' table if it doesn't already exist.
        This should be run once after connecting.
        """
        if not self.cursor:
            logging.error("Cannot set up table. No active cursor.")
            return
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS archive (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'restored')),
                    date_archived TEXT
                )
            ''')
            self.conn.commit()
            logging.info("'archive' table is ready.")
        except sqlite3.Error as e:
            logging.error(f"Error setting up table: {e}")

    def add_file_record(self, file_path, status, date_archived=None):
        """Adds a new file record to the archive table."""
        query = "INSERT INTO archive (file_path, status, date_archived) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(query, (file_path, status, date_archived))
            self.conn.commit()
            logging.info(f"Added record for: {file_path}")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Failed to add record for {file_path}: {e}")
            return None

    def update_file_status(self, file_id, new_status):
        """
        Updates the status of an existing file record.
        Also updates the archive date accordingly.
        """
        params = (new_status, file_id)
        if new_status == 'archived':
            query = "UPDATE archive SET status = ?, date_archived = ? WHERE id = ?"
            params = (new_status, datetime.now().isoformat(), file_id)
        else: # For restoring, we clear the archive date
            query = "UPDATE archive SET status = ?, date_archived = NULL WHERE id = ?"
        
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            logging.info(f"Updated status for file ID {file_id} to '{new_status}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to update status for file ID {file_id}: {e}")

    def get_files_by_status(self, status):
        """Retrieves all records with a specific status."""
        query = "SELECT * FROM archive WHERE status = ?"
        try:
            self.cursor.execute(query, (status,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Failed to get files by status '{status}': {e}")
            return []

    def get_file_by_id(self, file_id):
        """Retrieves a single record by its ID."""
        query = "SELECT * FROM archive WHERE id = ?"
        try:
            self.cursor.execute(query, (file_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Failed to get file by ID {file_id}: {e}")
            return None
            
    def get_file_by_path(self, file_path):
        """Retrieves a single record by its file path. (NEW)"""
        query = "SELECT * FROM archive WHERE file_path = ?"
        try:
            self.cursor.execute(query, (file_path,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Failed to get file by path {file_path}: {e}")
            return None

    def remove_file_record(self, file_id):
        """Deletes a record from the archive table."""
        query = "DELETE FROM archive WHERE id = ?"
        try:
            self.cursor.execute(query, (file_id,))
            self.conn.commit()
            logging.info(f"Removed record for file ID {file_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to remove record for file ID {file_id}: {e}")