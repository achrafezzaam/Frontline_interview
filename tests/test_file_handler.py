import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from src import file_handler as fh

class TestFileHandler(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.scan_dir = os.path.join(self.test_dir, 'scan')
        self.archive_dir = os.path.join(self.test_dir, 'archive')
        os.makedirs(self.scan_dir)
        os.makedirs(self.archive_dir)

        # Create mock config and db_handler
        self.mock_config = {
            'scan_directories': [self.scan_dir],
            'archive_directory': self.archive_dir,
            'days_until_archive': 30,
            'days_until_delete': 60
        }
        self.mock_db_handler = MagicMock()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def test_find_inactive_files(self):
        """Test the logic for finding inactive files."""
        # Create a recent file (should not be found)
        with open(os.path.join(self.scan_dir, "recent.txt"), "w") as f:
            f.write("recent")

        # Create an old file (should be found)
        old_file_path = os.path.join(self.scan_dir, "old.txt")
        with open(old_file_path, "w") as f:
            f.write("old")
        
        # Modify its modification time to be 40 days ago
        forty_days_ago = (datetime.now() - timedelta(days=40)).timestamp()
        os.utime(old_file_path, (forty_days_ago, forty_days_ago))

        inactive_files = fh.find_inactive_files([self.scan_dir], 30)
        
        self.assertEqual(len(inactive_files), 1)
        self.assertIn("old.txt", inactive_files[0])

    def test_scan_and_archive_files(self):
        """Test the complete scan and archive process."""
        # Create an old file to be archived
        old_file_path = os.path.join(self.scan_dir, "file_to_archive.txt")
        with open(old_file_path, "w") as f:
            f.write("archive me")
        
        thirty_days_ago = (datetime.now() - timedelta(days=35)).timestamp()
        os.utime(old_file_path, (thirty_days_ago, thirty_days_ago))

        fh.scan_and_archive_files(self.mock_db_handler, self.mock_config)

        # Check that the file was moved
        self.assertFalse(os.path.exists(old_file_path))
        self.assertTrue(os.path.exists(os.path.join(self.archive_dir, "file_to_archive.txt")))
        
        # Check that the database was updated
        self.mock_db_handler.add_file_record.assert_called_once()

    def test_restore_file(self):
        """Test restoring a file from the archive."""
        # Setup a file in the archive
        archived_file_name = "restorable.txt"
        original_path = os.path.join(self.scan_dir, archived_file_name)
        archived_path = os.path.join(self.archive_dir, archived_file_name)
        with open(archived_path, "w") as f:
            f.write("restore me")

        # Mock the database response
        self.mock_db_handler.get_file_by_id.return_value = (1, original_path, 'archived', 'some_date')
        
        fh.restore_file(self.mock_db_handler, self.mock_config, 1)

        # Check file was moved back
        self.assertTrue(os.path.exists(original_path))
        self.assertFalse(os.path.exists(archived_path))

        # Check db was updated
        self.mock_db_handler.update_file_status.assert_called_with(1, 'restored')

if __name__ == '__main__':
    unittest.main()
