import sqlite3

DATABASE_NAME = "users.db"


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    The row_factory allows us to access database columns by name.
    """
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_users_table():
    """
    Creates the users table if it does not already exist.
    This ensures the database is ready when the application starts.
    """
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            bio TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()