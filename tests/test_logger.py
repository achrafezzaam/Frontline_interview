import unittest
import logging
import os
from unittest.mock import patch
from src import logger as app_logger

class TestLogger(unittest.TestCase):

    def setUp(self):
        """Create a temporary log file path."""
        self.log_file = "test_app.log"
    
    def tearDown(self):
        """Clean up the log file if it exists."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        # Reset logging configuration
        logging.getLogger().handlers = []

    @patch('logging.StreamHandler')
    @patch('logging.FileHandler')
    def test_setup_logger(self, mock_file_handler, mock_stream_handler):
        """Test that logger setup adds the correct handlers."""
        app_logger.setup_logger(self.log_file)
        
        # Check that FileHandler and StreamHandler were created with the correct args
        mock_file_handler.assert_called_with(self.log_file)
        mock_stream_handler.assert_called_once()
        
        # Check that the handlers were added to the root logger
        logger = logging.getLogger()
        self.assertEqual(len(logger.handlers), 2)

    def test_log_output(self):
        """Test that a message is actually written to the log file."""
        app_logger.setup_logger(self.log_file)
        
        test_message = "This is a test log message."
        logging.info(test_message)
        
        # We need to remove the handlers to properly close the file before reading
        logging.getLogger().handlers = []
        
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn(test_message, content)

if __name__ == '__main__':
    unittest.main()
