import unittest
import os
import yaml
from unittest.mock import patch, mock_open
from main import load_config, main

class TestMain(unittest.TestCase):

    def setUp(self):
        """Create a dummy config file content."""
        self.config_data = {
            'database_name': 'test.db',
            'log_file': 'test.log',
            'scan_directories': ['./scan'],
            'archive_directory': './archive',
            'days_until_archive': 10,
            'days_until_delete': 20
        }
        # Convert dict to YAML string
        self.yaml_string = yaml.dump(self.config_data)

    def test_load_config_success(self):
        """Test loading a valid config file."""
        # mock_open reads the yaml_string data
        with patch("builtins.open", mock_open(read_data=self.yaml_string)):
            config = load_config()
            self.assertEqual(config, self.config_data)

    def test_load_config_file_not_found(self):
        """Test handling of a missing config file."""
        # Simulate FileNotFoundError when open is called
        with patch("builtins.open", side_effect=FileNotFoundError):
            config = load_config()
            self.assertIsNone(config)

    # This is a more advanced test that mocks multiple components
    @patch('main.load_config')
    @patch('main.logger.setup_logger')
    @patch('main.DatabaseHandler')
    @patch('main.fh')
    @patch('builtins.input', side_effect=['3', '0']) # Simulate user entering '3' then '0'
    def test_main_loop_list_files(self, mock_input, mock_fh, mock_db_handler, mock_logger, mock_load_config):
        """Test that entering '3' calls the list files logic."""
        # Setup mocks
        mock_load_config.return_value = self.config_data
        mock_db_instance = mock_db_handler.return_value
        mock_db_instance.connect.return_value = True
        
        # Run the main function
        main()
        
        # Assertions
        mock_logger.assert_called_with('test.log')
        mock_db_handler.assert_called_with('test.db')
        mock_db_instance.connect.assert_called_once()
        mock_db_instance.setup_table.assert_called_once()
        
        # Check that get_files_by_status was called because we entered '3'
        mock_db_instance.get_files_by_status.assert_called_with('archived')
        
        # Check that the connection was closed at the end
        mock_db_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
