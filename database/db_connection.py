import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Qwertyu2003',
            database='food_ordering_system',
            # port=3306,
        )

        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None