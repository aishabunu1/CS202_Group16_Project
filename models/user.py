from database.db_connection import get_db_connection

def authenticate_user(username, password):
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT user_id, username, user_type 
        FROM users 
        WHERE username = %s AND password = %s
    """, (username, password))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_user(username, password, email, first_name, last_name, user_type):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, email, first_name, last_name, user_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, password, email, first_name, last_name, user_type))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT user_id, username, email, first_name, last_name, user_type
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user