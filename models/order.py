from database.db_connection import get_db_connection

def create_order(customer_id, restaurant_id, delivery_address_id, items):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # Create the cart
        cursor.execute("""
            INSERT INTO carts (customer_id, restaurant_id, delivery_address_id, status)
            VALUES (%s, %s, %s, 'preparing')
        """, (customer_id, restaurant_id, delivery_address_id))
        
        cart_id = cursor.lastrowid
        
        # Add cart items
        for item in items:
            cursor.execute("""
                INSERT INTO cart_items (cart_id, item_id, quantity, discounted_price)
                VALUES (%s, %s, %s, %s)
            """, (cart_id, item['item_id'], item['quantity'], item.get('discounted_price')))
        
        conn.commit()
        return cart_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_orders_by_customer(customer_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, r.name as restaurant_name, 
               COUNT(ci.cart_item_id) as item_count,
               SUM(ci.quantity * IFNULL(ci.discounted_price, 
                   (SELECT price FROM menu_items WHERE item_id = ci.item_id))) as total_price
        FROM carts c
        JOIN restaurants r ON c.restaurant_id = r.restaurant_id
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        WHERE c.customer_id = %s
        GROUP BY c.cart_id
        ORDER BY c.order_time DESC
    """, (customer_id,))
    
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def get_orders_by_restaurant(restaurant_id):
    conn = get_db_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, u.first_name, u.last_name,
               COUNT(ci.cart_item_id) as item_count,
               SUM(ci.quantity * IFNULL(ci.discounted_price, 
                   (SELECT price FROM menu_items WHERE item_id = ci.item_id))) as total_price
        FROM carts c
        JOIN users u ON c.customer_id = u.user_id
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        WHERE c.restaurant_id = %s
        GROUP BY c.cart_id
        ORDER BY c.order_time DESC
    """, (restaurant_id,))
    
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def get_order_details(order_id, manager_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get basic order info
        cursor.execute("""
            SELECT c.*, u.first_name, u.last_name, a.address, a.city, a.postal_code, r.name as restaurant_name
            FROM carts c
            JOIN users u ON c.customer_id = u.user_id
            JOIN addresses a ON c.delivery_address_id = a.address_id
            JOIN restaurants r ON c.restaurant_id = r.restaurant_id
            WHERE c.cart_id = %s AND c.restaurant_id IN (
                SELECT restaurant_id FROM restaurants WHERE manager_id = %s
            )
        """, (order_id, manager_id))
        order = cursor.fetchone()
        
        if not order:
            return None, None
        
        # Get order items
        cursor.execute("""
            SELECT mi.name, mi.price, ci.quantity, ci.discounted_price
            FROM cart_items ci
            JOIN menu_items mi ON ci.item_id = mi.item_id
            WHERE ci.cart_id = %s
        """, (order_id,))
        items = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
        return order, items

def update_order_status(order_id, new_status):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    
    if new_status == 'accepted':
        cursor.execute("""
            UPDATE carts 
            SET status = %s, accepted_time = CURRENT_TIMESTAMP
            WHERE cart_id = %s
        """, (new_status, order_id))
    else:
        cursor.execute("""
            UPDATE carts 
            SET status = %s
            WHERE cart_id = %s
        """, (new_status, order_id))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_order_by_id(cart_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT cart_id, customer_id, restaurant_id, order_time, status
        FROM carts
        WHERE cart_id = %s
    """, (cart_id,))
    
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    return order


    