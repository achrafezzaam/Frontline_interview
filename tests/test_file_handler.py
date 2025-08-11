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

        self.mock_config = {
            'scan_directories': [self.scan_dir],
            'archive_directory': self.archive_dir,
            'days_until_archive': 3,
            'days_until_delete': 6
        }
        self.mock_db_handler = MagicMock()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def _create_old_file(self, filename, days_old):
        """Helper function to create a file with a past modification time."""
        file_path = os.path.join(self.scan_dir, filename)
        with open(file_path, "w") as f:
            f.write("content")
        past_date = (datetime.now() - timedelta(days=days_old)).timestamp()
        os.utime(file_path, (past_date, past_date))
        return file_path

    def test_scan_and_archive_new_file(self):
        """Test archiving a file that has no previous record in the database."""
        self._create_old_file("new_archive.txt", 35)
        
        # Simulate that the file does not exist in the DB
        self.mock_db_handler.get_file_by_path.return_value = None
        
        fh.scan_and_archive_files(self.mock_db_handler, self.mock_config)

        # Verify it tries to get the file by path, then adds a new record
        self.mock_db_handler.get_file_by_path.assert_called_once()
        self.mock_db_handler.add_file_record.assert_called_once()
        self.mock_db_handler.update_file_status.assert_not_called()

    def test_scan_and_rearchive_existing_file(self):
        """Test re-archiving a file that was previously restored."""
        old_file_path = self._create_old_file("re_archive.txt", 40)
        
        # Simulate that the file DOES exist in the DB (it was restored)
        self.mock_db_handler.get_file_by_path.return_value = (1, old_file_path, 'restored', None)

        fh.scan_and_archive_files(self.mock_db_handler, self.mock_config)

        # Verify it finds the existing record and updates it, instead of adding a new one
        self.mock_db_handler.get_file_by_path.assert_called_once()
        self.mock_db_handler.add_file_record.assert_not_called()
        self.mock_db_handler.update_file_status.assert_called_once_with(1, 'archived')

    @patch('os.utime')
    def test_restore_file_updates_mtime(self, mock_utime):
        """Test that restoring a file updates its modification time."""
        archived_file_name = "restorable.txt"
        original_path = os.path.join(self.scan_dir, archived_file_name)
        archived_path = os.path.join(self.archive_dir, archived_file_name)
        with open(archived_path, "w") as f:
            f.write("restore me")

        self.mock_db_handler.get_file_by_id.return_value = (1, original_path, 'archived', 'some_date')
        
        fh.restore_file(self.mock_db_handler, self.mock_config, 1)

        # Check that os.utime was called on the restored file path with None (to set to now)
        mock_utime.assert_called_once_with(original_path, None)
        self.mock_db_handler.update_file_status.assert_called_with(1, 'restored')

if __name__ == '__main__':
    unittest.main()
    