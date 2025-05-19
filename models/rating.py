from database.db_connection import get_db_connection

def add_rating(cart_id, customer_id, rating_value, comment):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ratings (cart_id, customer_id, restaurant_id, rating_value, comment)
        SELECT %s, %s, c.restaurant_id, %s, %s
        FROM carts c
        WHERE c.cart_id = %s AND c.customer_id = %s AND c.status = 'completed'
    """, (cart_id, customer_id, rating_value, comment, cart_id, customer_id))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_ratings_by_restaurant(restaurant_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, u.first_name, u.last_name
        FROM ratings r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.restaurant_id = %s
        ORDER BY r.rating_value DESC
    """, (restaurant_id,))
    
    ratings = cursor.fetchall()
    cursor.close()
    conn.close()
    return ratings


def get_average_rating(restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ROUND(AVG(rating_value), 1)
        FROM ratings
        WHERE restaurant_id = %s
    """, (restaurant_id,))
    avg = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return avg or 0
