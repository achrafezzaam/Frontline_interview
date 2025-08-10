import unittest
import os
from datetime import datetime
from src.database import DatabaseHandler

class TestDatabaseHandler(unittest.TestCase):

    def setUp(self):
        """Set up a temporary in-memory database for each test."""
        # ':memory:' creates a temporary database in RAM
        self.db_path = ":memory:"
        self.db_handler = DatabaseHandler(self.db_path)
        self.db_handler.connect()
        self.db_handler.setup_table()

    def tearDown(self):
        """Close the database connection after each test."""
        self.db_handler.close()

    def test_connection(self):
        """Test that the database connection is established."""
        self.assertIsNotNone(self.db_handler.conn)
        self.assertIsNotNone(self.db_handler.cursor)

    def test_add_and_get_file_record(self):
        """Test adding a file record and retrieving it by ID."""
        file_path = "/test/path/file1.txt"
        status = "active"
        
        # Add a record and get its ID
        record_id = self.db_handler.add_file_record(file_path, status)
        self.assertIsNotNone(record_id)

        # Retrieve the record
        retrieved_record = self.db_handler.get_file_by_id(record_id)
        self.assertIsNotNone(retrieved_record)
        self.assertEqual(retrieved_record[0], record_id)
        self.assertEqual(retrieved_record[1], file_path)
        self.assertEqual(retrieved_record[2], status)

    def test_get_files_by_status(self):
        """Test retrieving files based on their status."""
        self.db_handler.add_file_record("/path/file_active.txt", "active")
        self.db_handler.add_file_record("/path/file_archived.txt", "archived", datetime.now().isoformat())
        self.db_handler.add_file_record("/path/another_active.txt", "active")

        active_files = self.db_handler.get_files_by_status("active")
        self.assertEqual(len(active_files), 2)

        archived_files = self.db_handler.get_files_by_status("archived")
        self.assertEqual(len(archived_files), 1)
        self.assertEqual(archived_files[0][1], "/path/file_archived.txt")

    def test_update_file_status(self):
        """Test updating a file's status."""
        record_id = self.db_handler.add_file_record("/path/to_update.txt", "active")
        
        # Update the status to 'archived'
        self.db_handler.update_file_status(record_id, "archived")
        
        updated_record = self.db_handler.get_file_by_id(record_id)
        self.assertEqual(updated_record[2], "archived")

    def test_remove_file_record(self):
        """Test removing a file record from the database."""
        record_id = self.db_handler.add_file_record("/path/to_delete.txt", "active")
        self.assertIsNotNone(self.db_handler.get_file_by_id(record_id))

        # Remove the record
        self.db_handler.remove_file_record(record_id)
        
        # Verify it's gone
        self.assertIsNone(self.db_handler.get_file_by_id(record_id))
        
    def test_unique_constraint(self):
        """Test that adding a duplicate file_path fails gracefully."""
        file_path = "/path/unique_file.txt"
        self.db_handler.add_file_record(file_path, "active")
        
        # Attempt to add the same file path again
        duplicate_id = self.db_handler.add_file_record(file_path, "active")
        self.assertIsNone(duplicate_id, "Adding a duplicate file path should fail and return None")

if __name__ == '__main__':
    unittest.main()
