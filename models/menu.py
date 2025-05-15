from database.db_connection import get_db_connection

def get_menu_items_by_restaurant(restaurant_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM menu_items
        WHERE restaurant_id = %s
        ORDER BY category, name
    """, (restaurant_id,))
    
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def get_menu_item_by_id(item_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM menu_items
        WHERE item_id = %s
    """, (item_id,))
    
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    return item