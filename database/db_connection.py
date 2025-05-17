import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='sabinait',
            database='food_ordering_system'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None