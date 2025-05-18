from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db_connection import get_db_connection
from models.user import authenticate_user, register_user, get_user_by_id
from models.restaurant import get_restaurants_by_city, get_restaurant_by_id, search_restaurants
from models.menu import get_menu_items_by_restaurant, get_menu_item_by_id
from models.order import create_order, get_orders_by_customer, get_orders_by_restaurant, update_order_status, get_order_details
from models.rating import add_rating, get_ratings_by_restaurant
from utils.auth import login_required, customer_required, manager_required
from utils.helpers import calculate_discounted_price
import mysql.connector
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Hanifahlovesfood1@',
    'database': 'food_ordering_system'
    #  'port' =3306,
}

def format_datetime(value, format='short'):
    """
    Jinja filter to format a Python datetime.
    Usage in template: {{ mydt|datetime('short') }}
    """
    if not isinstance(value, datetime):
        return value
    if format == 'short':
        return value.strftime('%b %d, %Y')
    elif format == 'full':
        return value.strftime('%A, %B %d %Y %H:%M')
    return value.strftime('%Y-%m-%d %H:%M')
app.jinja_env.filters['datetime'] = format_datetime

def format_currency(value):
    """Get numeric value into currrency """
    try:
        return f"₺{float(value):,.2f}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['currency'] = format_currency
@app.route('/')
def home():
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user['user_type'] == 'customer':
            return redirect(url_for('customer_dashboard'))
        else:
            return redirect(url_for('manager_dashboard'))
    return render_template('auth/login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['user_id']
            session['user_type'] = user['user_type']
            if user['user_type'] == 'customer':
                return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_type = request.form['user_type']
        
        try:
            register_user(username, password, email, first_name, last_name, user_type)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Registration failed: {err}', 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Customer Routes
@app.route('/customer/dashboard')
@login_required
@customer_required
def customer_dashboard():
    user_id = session['user_id']
    # Get user's default city from their default address
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT city FROM addresses 
        WHERE user_id = %s AND is_default = TRUE
    """, (user_id,))
    address = cursor.fetchone()
    city = address['city'] if address else 'Istanbul'  # Default city
    
    restaurants = get_restaurants_by_city(city)
    cursor.close()
    conn.close()
    
    return render_template('customer/dashboard.html', restaurants=restaurants, city=city)

@app.route('/customer/restaurants')
@login_required
@customer_required
def customer_restaurants():
    search_query = request.args.get('q', '')
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT city FROM addresses 
        WHERE user_id = %s AND is_default = TRUE
    """, (user_id,))
    address = cursor.fetchone()
    city = address['city'] if address else 'Istanbul'
    
    if search_query:
        restaurants = search_restaurants(search_query, city)
    else:
        restaurants = get_restaurants_by_city(city)
    
    cursor.close()
    conn.close()
    
    return render_template('customer/restaurants.html', restaurants=restaurants, search_query=search_query)

@app.route(
    '/customer/restaurant/<int:restaurant_id>',
    endpoint='customer_menu'
)
@login_required
@customer_required
def view_restaurant_menu(restaurant_id):
    # Fetch restaurant and its raw menu items
    restaurant = get_restaurant_by_id(restaurant_id)
    menu_items = get_menu_items_by_restaurant(restaurant_id)

    # Pull any active discounts
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Build a CSV list of item IDs for the IN(...)
    ids_csv = ','.join(str(item['item_id']) for item in menu_items) or 'NULL'
    cursor.execute(f"""
        SELECT d.item_id, d.discount_percentage
        FROM discounts d
        WHERE d.item_id IN ({ids_csv})
          AND CURDATE() BETWEEN d.start_date AND d.end_date
    """)
    discounts = {d['item_id']: d['discount_percentage'] for d in cursor.fetchall()}
    cursor.close()
    conn.close()

    # Apply discounts and group by category
    menu_by_category = defaultdict(list)
    for item in menu_items:
        # apply discount if present
        item['discounted_price'] = (
            calculate_discounted_price(item['price'], discounts[item['item_id']])
            if item['item_id'] in discounts
            else item['price']
        )
        # group by the category key that your model returns
        # change 'category' to whatever your column is named (e.g. 'cat_name')
        category = item.get('category') or item.get('cat_name') or 'Uncategorized'
        menu_by_category[category].append(item)

    return render_template(
        'customer/menu.html',
        restaurant=restaurant,
        menu_by_category=menu_by_category
    )
@app.route('/customer/cart', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_cart():
    if request.method == 'POST':
        # Handle adding to cart (would use session in a real implementation)
        pass
    
    # Display cart contents
    return render_template('customer/cart.html')

@app.route('/customer/orders')
@login_required
@customer_required
def customer_orders():
    user_id = session['user_id']
    orders = get_orders_by_customer(user_id)
    return render_template('customer/orders.html', orders=orders)

@app.route('/customer/rate/<int:order_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def rate_order(order_id):
    if request.method == 'POST':
        rating_value = int(request.form['rating'])
        comment = request.form.get('comment', '')
        
        try:
            add_rating(order_id, session['user_id'], rating_value, comment)
            flash('Thank you for your rating!', 'success')
            return redirect(url_for('customer_orders'))
        except mysql.connector.Error as err:
            flash(f'Failed to submit rating: {err}', 'error')
    
    # GET request - show rating form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.cart_id, r.name as restaurant_name
        FROM carts c
        JOIN restaurants r ON c.restaurant_id = r.restaurant_id
        WHERE c.cart_id = %s AND c.customer_id = %s
    """, (order_id, session['user_id']))
    
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('customer_orders'))
    
    return render_template('customer/rate.html', order=order)


# Manager Routes
@app.route('/manager/dashboard')
@login_required
@manager_required
def manager_dashboard():
    manager_id = session.get('user_id')
    
    # Get manager's restaurants
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get manager's restaurants
        cursor.execute("SELECT * FROM restaurants WHERE manager_id = %s", (manager_id,))
        restaurants = cursor.fetchall()
        
        if not restaurants:
            return render_template('manager/dashboard.html', 
                                restaurants=[], 
                                pending_orders=[])
        
        # Get pending orders for all of manager's restaurants
        restaurant_ids = [r['restaurant_id'] for r in restaurants]
        placeholders = ','.join(['%s'] * len(restaurant_ids))
        
        # Main orders query
        cursor.execute(f"""
            SELECT 
                c.cart_id, c.customer_id, c.restaurant_id, c.status,
                c.order_time, c.accepted_time,
                u.first_name, u.last_name,
                r.name as restaurant_name,
                COUNT(ci.cart_item_id) as item_count,
                SUM(ci.quantity * IFNULL(ci.discounted_price, 
                    (SELECT price FROM menu_items WHERE item_id = ci.item_id))) as total_price
            FROM carts c
            JOIN users u ON c.customer_id = u.user_id
            JOIN restaurants r ON c.restaurant_id = r.restaurant_id
            JOIN cart_items ci ON c.cart_id = ci.cart_id
            WHERE c.restaurant_id IN ({placeholders}) AND c.status != 'completed'
            GROUP BY c.cart_id
            ORDER BY c.order_time DESC
        """, tuple(restaurant_ids))
        
        orders = cursor.fetchall()
        
        # Get items for each order
        for order in orders:
            cursor.execute("""
                SELECT 
                    mi.name, 
                    mi.price, 
                    ci.quantity, 
                    ci.discounted_price,
                    (ci.discounted_price or mi.price) * ci.quantity as item_total
                FROM cart_items ci
                JOIN menu_items mi ON ci.item_id = mi.item_id
                WHERE ci.cart_id = %s
            """, (order['cart_id'],))
            order['order_items'] = cursor.fetchall()  # Using 'order_items' instead of 'items'
        
        return render_template('manager/dashboard.html',
                            restaurants=restaurants,
                            pending_orders=orders)
    
    except Exception as e:
        print(f"Error in manager_dashboard: {str(e)}")
        return render_template('manager/dashboard.html', 
                            restaurants=[], 
                            pending_orders=[])
    
    finally:
        cursor.close()
        conn.close()


@app.route('/manager/orders')
@login_required
@manager_required
def manager_orders():
    user_id = session['user_id']
    restaurant_id = request.args.get('restaurant_id')
    
    if restaurant_id:
        orders = get_orders_by_restaurant(restaurant_id)
    else:
        # Get all orders for all restaurants managed by this user
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.*, u.first_name, u.last_name, r.name as restaurant_name
            FROM carts c
            JOIN users u ON c.customer_id = u.user_id
            JOIN restaurants r ON c.restaurant_id = r.restaurant_id
            WHERE c.restaurant_id IN (SELECT restaurant_id FROM restaurants WHERE manager_id = %s)
            ORDER BY c.order_time DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('manager/orders.html', orders=orders)

@app.route('/manager/order/<int:order_id>/update', methods=['POST'])
@login_required
@manager_required
def update_order_status(order_id):
    new_status = request.form.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if new_status == 'accepted':
            cursor.execute("""
                UPDATE carts 
                SET status = %s, accepted_time = CURRENT_TIMESTAMP
                WHERE cart_id = %s AND status != 'completed'
            """, (new_status, order_id))
        else:
            cursor.execute("""
                UPDATE carts 
                SET status = %s
                WHERE cart_id = %s AND status != 'completed'
            """, (new_status, order_id))
        
        conn.commit()
        flash('Order status updated successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash('Failed to update order status', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manager_dashboard'))

@app.route('/manager/order/<int:order_id>')
@login_required
@manager_required
def view_order(order_id):
    order, items = get_order_details(order_id, session['user_id'])
    
    if not order:
        flash('Order not found or not authorized', 'danger')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('manager/order_detail.html', 
                         order=order, 
                         items=items)

@app.route('/manager/order/<int:order_id>/update', methods=['POST'])
@login_required
@manager_required
def update_order_status2(order_id):
    new_status = request.form.get('status')
    
    if update_order_status(order_id, session['user_id'], new_status):
        flash('Order status updated successfully!', 'success')
    else:
        flash('Failed to update order status', 'danger')
    
    return redirect(url_for('view_order', order_id=order_id))

@app.route('/add_keyword', methods=['POST'])
@login_required
@manager_required
def add_keyword():
    restaurant_id = request.form['restaurant_id']
    keyword = request.form['keyword'].strip().lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the keyword already exists for the restaurant
    cursor.execute("""
        SELECT 1 FROM restaurant_keywords 
        WHERE restaurant_id = %s AND LOWER(keyword) = %s
    """, (restaurant_id, keyword))
    exists = cursor.fetchone()

    if exists:
        flash("Keyword already exists for this restaurant.", "warning")
    else:
        cursor.execute("""
            INSERT INTO restaurant_keywords (restaurant_id, keyword)
            VALUES (%s, %s)
        """, (restaurant_id, keyword))
        conn.commit()
        flash("Keyword added successfully!", "success")

    cursor.close()
    conn.close()

    return redirect(url_for('manager_dashboard'))


@app.route('/manager/menu/<int:restaurant_id>')
@login_required
@manager_required
def manager_menu(restaurant_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Step 1: Verify this restaurant belongs to the logged-in manager
    cursor.execute("""
        SELECT * FROM restaurants 
        WHERE restaurant_id = %s AND manager_id = %s
    """, (restaurant_id, session['user_id']))
    restaurant = cursor.fetchone()

    if not restaurant:
        cursor.close()
        conn.close()
        flash('Restaurant not found or not authorized.', 'error')
        return redirect(url_for('manager_dashboard'))

    # ✅ Step 2: Get menu items with currently active discounts
    cursor.execute("""
        SELECT 
            i.*, 
            d.discount_percentage, 
            d.start_date, 
            d.end_date
        FROM menu_items i
        LEFT JOIN discounts d 
            ON i.item_id = d.item_id 
            AND CURDATE() BETWEEN d.start_date AND d.end_date
        WHERE i.restaurant_id = %s
    """, (restaurant_id,))
    menu_items = cursor.fetchall()

    # ✅ Step 3: Get list of active discounts (optional for display)
    cursor.execute("""
        SELECT d.*, i.name as item_name
        FROM discounts d
        JOIN menu_items i ON d.item_id = i.item_id
        WHERE i.restaurant_id = %s
        AND CURDATE() BETWEEN d.start_date AND d.end_date
    """, (restaurant_id,))
    active_discounts = cursor.fetchall()

    cursor.close()
    conn.close()

    # ✅ Step 4: Pass everything to the template
    return render_template('manager/menu.html',
                           restaurant=restaurant,
                           menu_items=menu_items,
                           active_discounts=active_discounts)



# Add a new menu item route

@app.route('/manager/menu/add', methods=['POST'])
@login_required
@manager_required
def add_menu_item():
    restaurant_id = request.form['restaurant_id']
    name = request.form['name']
    description = request.form.get('description')
    price = request.form['price']
    category = request.form.get('category')
    image = request.files['image']
    image_url = image.filename if image else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO menu_items (restaurant_id, name, description, price, image_url, category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (restaurant_id, name, description, price, image_url, category))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Menu item added successfully.")
    return redirect(url_for('manager_menu', restaurant_id=restaurant_id))


#apply discount to menu item route
@app.route('/manager/menu/discount/<int:item_id>', methods=['POST'])
@login_required
@manager_required
def apply_discount(item_id):
    percentage = request.form['discount_percentage']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO discounts (item_id, discount_percentage, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """, (item_id, percentage, start_date, end_date))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Discount applied successfully.")
    return redirect(request.referrer or url_for('manager_dashboard'))



@app.route('/manager/statistics/<int:restaurant_id>')
@login_required
@manager_required
def manager_statistics(restaurant_id):
    # Verify this restaurant belongs to the current manager
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.* FROM restaurants r
        WHERE r.restaurant_id = %s AND r.manager_id = %s
    """, (restaurant_id, session['user_id']))
    
    restaurant = cursor.fetchone()
    if not restaurant:
        cursor.close()
        conn.close()
        flash('Restaurant not found or not authorized', 'error')
        return redirect(url_for('manager_dashboard'))
    
    # Get statistics for the past month
    cursor.execute("""
        SELECT 
            COUNT(c.cart_id) as total_orders,
            SUM(ci.quantity * IFNULL(ci.discounted_price, i.price)) as total_revenue
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN menu_items i ON ci.item_id = i.item_id
        WHERE c.restaurant_id = %s
        AND c.status = 'completed'
        AND c.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    """, (restaurant_id,))
    
    stats = cursor.fetchone()
    
    # Get item-wise statistics
    cursor.execute("""
        SELECT 
            i.item_id,
            i.name,
            SUM(ci.quantity) as total_quantity,
            SUM(ci.quantity * IFNULL(ci.discounted_price, i.price)) as item_revenue
        FROM cart_items ci
        JOIN menu_items i ON ci.item_id = i.item_id
        JOIN carts c ON ci.cart_id = c.cart_id
        WHERE c.restaurant_id = %s
        AND c.status = 'completed'
        AND c.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY i.item_id, i.name
        ORDER BY item_revenue DESC
    """, (restaurant_id,))
    
    item_stats = cursor.fetchall()
    
    # Get top customers
    cursor.execute("""
        SELECT 
            u.user_id,
            u.first_name,
            u.last_name,
            COUNT(c.cart_id) as order_count,
            SUM(ci.quantity * IFNULL(ci.discounted_price, i.price)) as total_spent
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN menu_items i ON ci.item_id = i.item_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE c.restaurant_id = %s
        AND c.status = 'completed'
        AND c.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY u.user_id, u.first_name, u.last_name
        ORDER BY order_count DESC
        LIMIT 1
    """, (restaurant_id,))
    
    frequent_customer = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            u.user_id,
            u.first_name,
            u.last_name,
            c.cart_id,
            SUM(ci.quantity * IFNULL(ci.discounted_price, i.price)) as order_value
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN menu_items i ON ci.item_id = i.item_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE c.restaurant_id = %s
        AND c.status = 'completed'
        AND c.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY u.user_id, u.first_name, u.last_name, c.cart_id
        ORDER BY order_value DESC
        LIMIT 1
    """, (restaurant_id,))
    
    highest_order = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('manager/statistics.html',
                         restaurant=restaurant,
                         stats=stats,
                         item_stats=item_stats,
                         frequent_customer=frequent_customer,
                         highest_order=highest_order)

if __name__ == '__main__':
    app.run(debug=True)