# Automated File Archiver

This is a command-line utility written in Python to help manage disk space by identifying, archiving, and eventually deleting old, unused files. It's a useful tool for cleaning up directories that accumulate lots of data over time, like download folders or log directories.

The application is configurable, allowing you to specify which directories to watch and how old files should be before they are archived or deleted.

## Features

- **Scan & Archive**: Automatically scans specified directories for files that haven't been modified in a configurable number of days and moves them to a central archive location.
- **Automated Purge**: Deletes files from the archive after they have been there for a configurable number of days.
- **Database Tracking**: Uses an SQLite database to keep a persistent record of all tracked files, their status (active, archived, restored), and important dates.
- **Interactive Menu**: Provides a simple command-line interface to list archived files, restore files from the archive, and force-delete files.
- **Configurable**: All settings (directories, time thresholds, database name) are managed in a simple config.yaml file.
- **Logging**: Keeps a detailed activity.log of all major actions, such as archiving, purging, and errors.

## Project Structure

The project is organized into source code, tests, and configuration files for clarity and maintainability.

file-archiver/
├── src/
│   ├── __init__.py         # Makes 'src' a Python package
│   ├── database.py         # Handles all database interactions
│   ├── file_handler.py     # Core logic for file operations
│   └── logger.py           # Configures the application logger
├── tests/
│   ├── __init__.py         # Makes 'tests' a Python package
│   ├── test_database.py    # Unit tests for the database
│   └── ...                 # Other test files
├── .gitignore              # Specifies files for Git to ignore
├── config.yaml             # Main configuration file
├── main.py                 # Main entry point for the application
├── populate_database.py    # Optional script to pre-load the DB
└── requirements.txt        # Project dependencies

## Setup and Installation

1. Clone the Repository (or download the files):
``` bash
git clone <your-repository-url>
cd file-archiver
```
2. Create a Virtual Environment (Recommended):
``` bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3. Install Dependencies:
The project requires PyYAML to read the configuration file.
``` bash
pip install -r requirements.txt
```
## Configuration

Before running the application, you need to set up the config.yaml file. This is where you define all the important settings.
``` bash
# config.yaml

database_name: "file_archiver.db"
log_file: "activity.log"

# List of directories to scan for inactive files.
scan_directories:
  - "./test_data/documents"
  - "./test_data/images"

# The central directory where inactive files will be moved.
archive_directory: "./__ARCHIVE__"

# Number of days of inactivity before a file is considered for archiving.
days_until_archive: 30

# Number of days a file stays in the archive before being deleted.
days_until_delete: 60
```

## How to Use

Run the main application from your terminal:
``` bash
python3 main.py
```

This will launch an interactive menu where you can choose from the following options:
1. Scan for and archive inactive files: Kicks off the process to find old files in your scan_directories and move them to the archive_directory.
2. Purge old archived files (delete them): Checks the archive for files that are older than days_until_delete and permanently removes them.
3. List currently archived files: Displays a list of all files currently in the archive, along with their database ID.
4. Restore an archived file: Prompts you for a file ID and moves that file from the archive back to its original location. Its modification time is reset to prevent it from being immediately re-archived.
5. Force delete an archived file: Prompts you for a file ID and immediately deletes that file from the archive and the database.
0. Exit: Closes the application.

## Running Tests

The project includes a suite of unit tests to ensure all components work as expected. To run the tests, navigate to the project's root directory and use the unittest discovery command:
``` bash
python3 -m unittest discover
```
