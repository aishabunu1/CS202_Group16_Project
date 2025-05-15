from database.db_connection import get_db_connection

def get_restaurants_by_city(city):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, 
               AVG(rt.rating_value) as avg_rating,
               COUNT(rt.rating_id) as rating_count
        FROM restaurants r
        LEFT JOIN ratings rt ON r.restaurant_id = rt.restaurant_id
        WHERE r.city = %s
        GROUP BY r.restaurant_id
    """, (city,))
    
    restaurants = cursor.fetchall()
    
    # Format rating display
    for restaurant in restaurants:
        if restaurant['rating_count'] >= 10:
            restaurant['rating_display'] = f"{restaurant['avg_rating']:.1f}/5"
        else:
            restaurant['rating_display'] = "New"
            restaurant['avg_rating'] = 0
    
    cursor.close()
    conn.close()
    return restaurants

def search_restaurants(query, city):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT r.*, 
               AVG(rt.rating_value) as avg_rating,
               COUNT(rt.rating_id) as rating_count
        FROM restaurants r
        LEFT JOIN ratings rt ON r.restaurant_id = rt.restaurant_id
        LEFT JOIN restaurant_keywords rk ON r.restaurant_id = rk.restaurant_id
        WHERE r.city = %s
        AND (r.name LIKE %s OR r.cuisine_type LIKE %s OR rk.keyword LIKE %s)
        GROUP BY r.restaurant_id
    """, (city, f"%{query}%", f"%{query}%", f"%{query}%"))
    
    restaurants = cursor.fetchall()
    
    # Format rating display
    for restaurant in restaurants:
        if restaurant['rating_count'] >= 10:
            restaurant['rating_display'] = f"{restaurant['avg_rating']:.1f}/5"
        else:
            restaurant['rating_display'] = "New"
            restaurant['avg_rating'] = 0
    
    cursor.close()
    conn.close()
    return restaurants

def get_restaurant_by_id(restaurant_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, 
               AVG(rt.rating_value) as avg_rating,
               COUNT(rt.rating_id) as rating_count
        FROM restaurants r
        LEFT JOIN ratings rt ON r.restaurant_id = rt.restaurant_id
        WHERE r.restaurant_id = %s
        GROUP BY r.restaurant_id
    """, (restaurant_id,))
    
    restaurant = cursor.fetchone()
    
    if restaurant:
        if restaurant['rating_count'] >= 10:
            restaurant['rating_display'] = f"{restaurant['avg_rating']:.1f}/5"
        else:
            restaurant['rating_display'] = "New"
            restaurant['avg_rating'] = 0
    
    cursor.close()
    conn.close()
    return restaurant