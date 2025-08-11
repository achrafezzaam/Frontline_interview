import unittest
import os
from datetime import datetime
from src.database import DatabaseHandler

class TestDatabaseHandler(unittest.TestCase):

    def setUp(self):
        """Set up a temporary in-memory database for each test."""
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
        
        record_id = self.db_handler.add_file_record(file_path, status)
        self.assertIsNotNone(record_id)

        retrieved_record = self.db_handler.get_file_by_id(record_id)
        self.assertIsNotNone(retrieved_record)
        self.assertEqual(retrieved_record[1], file_path)

    def test_get_file_by_path(self):
        """Test retrieving a file record by its unique path."""
        file_path = "/test/path/unique_file.txt"
        self.db_handler.add_file_record(file_path, "active")

        retrieved_record = self.db_handler.get_file_by_path(file_path)
        self.assertIsNotNone(retrieved_record)
        self.assertEqual(retrieved_record[1], file_path)

    def test_update_file_status(self):
        """Test updating a file's status and the archive date."""
        record_id = self.db_handler.add_file_record("/path/to_update.txt", "active")
        
        # Update status to 'archived'
        self.db_handler.update_file_status(record_id, "archived")
        updated_record = self.db_handler.get_file_by_id(record_id)
        self.assertEqual(updated_record[2], "archived")
        self.assertIsNotNone(updated_record[3], "date_archived should be set when status is 'archived'")

        # Update status back to 'restored'
        self.db_handler.update_file_status(record_id, "restored")
        restored_record = self.db_handler.get_file_by_id(record_id)
        self.assertEqual(restored_record[2], "restored")
        self.assertIsNone(restored_record[3], "date_archived should be NULL when status is 'restored'")

    def test_remove_file_record(self):
        """Test removing a file record from the database."""
        record_id = self.db_handler.add_file_record("/path/to_delete.txt", "active")
        self.assertIsNotNone(self.db_handler.get_file_by_id(record_id))

        self.db_handler.remove_file_record(record_id)
        self.assertIsNone(self.db_handler.get_file_by_id(record_id))

if __name__ == '__main__':
    unittest.main()
