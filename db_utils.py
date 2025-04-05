import mysql.connector
from dotenv import load_dotenv
import os

#environment variables
load_dotenv()

def test_connection():
    """Test the database connection and return True if successful, False otherwise"""
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"Connected to database: {db_name}")
            cursor.close()
            connection.close()
            return True
        return False
    except mysql.connector.Error as err:
        print(f"Error testing connection: {err}")
        return False

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def execute_query(query, params=None, fetch=True):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()  # Commit the transaction for non-fetch operations
            result = cursor.lastrowid
            
        return result
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        connection.rollback()  # Rollback on error
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close() 