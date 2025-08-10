import sqlite3

def initialize_database():
    try:
        conn = sqlite3.connect("my_database.db")
        cursor = conn.cursor()
        cursor.execute(''' CREATE TABLE IF NOT EXISTS archive (
                            id INTEGER PRIMARY KEY,
                            file_path TEXT NOT NULL,
                            status TEXT DEFAULT 'actived'
                       )''')
        conn.commit()
        return conn
    except sqlite3.Error as e:
        print(f"An error has occured: {e}")

def add_file_record(conn, file_info):
    cursor = conn.cursor()
    insert_query = "INSERT INTO archive (file_path, status) VALUES (?, ?)"
    cursor.execute(insert_query, file_info)
    conn.commit()

def get_files(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive")
    rows = cursor.fetchall()
    return rows

def update_file_status(conn, file_id, new_status):
    cursor = conn.cursor()
    query = "UPDATE archive SET status = ? WHERE id = ?"
    cursor.execute(query, (new_status, file_id))
    conn.commit()

def get_files_by_status(conn, status):
    cursor = conn.cursor()
    query = "SELECT * FROM archive WHERE status = ?"
    cursor.execute(query, (status,))
    record = cursor.fetchall()
    return record

def get_file_by_id(conn, file_id):
    cursor = conn.cursor()
    query = "SELECT * FROM archive WHERE id = ?"
    cursor.execute(query, (file_id,))
    record = cursor.fetchone()
    return record

def remove_file_record(conn, file_id):
    cursor = conn.cursor()
    query = "DELETE FROM archive WHERE id = ?"
    cursor.execute(query, (file_id,))
    conn.commit()
