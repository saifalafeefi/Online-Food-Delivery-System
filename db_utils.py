import mysql.connector
from dotenv import load_dotenv
import os
import platform

# Load environment variables from .env file first
load_dotenv()

# Then set defaults if not found
if 'DB_HOST' not in os.environ:
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = '12345678'
    os.environ['DB_NAME'] = 'food_delivery'

# Flag to track if we've shown debug information in the current session
_debug_shown = False

def reset_debug_state():
    """Reset the debug state - call this at the start of a new session"""
    global _debug_shown
    _debug_shown = False

def get_connection_config():
    """Get database connection configuration based on platform"""
    config = {
        'host': os.environ.get('DB_HOST'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'use_pure': True  # Use pure Python implementation for compatibility
    }
    
    # Add database name if it exists (not for initial setup)
    if os.environ.get('DB_NAME'):
        config['database'] = os.environ.get('DB_NAME')
    
    # Handle different authentication methods based on platform
    if platform.system() == 'Darwin':  # macOS
        # Try without auth_plugin first
        try:
            test_conn = mysql.connector.connect(**config)
            test_conn.close()
            return config
        except mysql.connector.Error:
            # If that fails, try with auth_plugin
            config['auth_plugin'] = 'caching_sha2_password'
    
    # For Windows, specify auth_plugin as we've set to mysql_native_password
    if platform.system() == 'Windows':
        config['auth_plugin'] = 'mysql_native_password'
    
    return config

def test_connection():
    """Test the database connection and return True if successful, False otherwise"""
    print("\nTesting database connection...")
    print(f"Platform: {platform.system()}")
    print(f"Using configuration:")
    config = get_connection_config()
    for key, value in config.items():
        if key != 'password':  # Don't print password
            print(f"  {key}: {value}")
    
    try:
        connection = mysql.connector.connect(**config)
        if connection and connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✓ Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"✓ Connected to database: {db_name}")
            cursor.close()
            connection.close()
            return True
        return False
    except mysql.connector.Error as err:
        print(f"✗ Error testing connection: {err}")
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("  Please check your username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("  Database does not exist")
        return False

def get_db_connection():
    """Get database connection using platform-specific configuration"""
    global _debug_shown
    
    try:
        config = get_connection_config()
        
        # Only show debug info the first time in this session
        first_connection = not _debug_shown
        if first_connection:
            debug_config = {k: v for k, v in config.items() if k != 'password'}
            print(f"DEBUG - Connecting with config: {debug_config}")
            _debug_shown = True
        
        connection = mysql.connector.connect(**config)
        
        # Show connection established message the first time
        if first_connection:
            print(f"DEBUG - Connection established successfully")
        
        return connection
    except mysql.connector.Error as err:
        print(f"ERROR - Database connection error: {err}")
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("ERROR - Check your username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("ERROR - Database does not exist")
        return None
    except Exception as e:
        print(f"ERROR - Unexpected error during connection: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    try:
        connection = get_db_connection()
        if not connection:
            print("Database connection failed. Check your database settings or server status.")
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
                connection.commit()
                result = cursor.lastrowid
                
            return result
        except mysql.connector.Error as err:
            error_msg = f"Error executing query: {err}"
            print(error_msg)
            
            connection.rollback()
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def search_restaurants(search_term=None, cuisine_type=None, location=None, include_inactive=False):
    """Search restaurants by name, cuisine type, or location
    
    Args:
        search_term (str): Term to search in name, cuisine, description, address
        cuisine_type (str): Specific cuisine type to filter
        location (str): Location to search in address
        include_inactive (bool): If True, include suspended restaurants (for admin use)
    """
    try:
        query = """
        SELECT r.*, u.email, u.username, u.is_active
        FROM restaurants r
        JOIN users u ON r.user_id = u.user_id
        WHERE 1=1
        """
        params = []
        
        # Only include active restaurants unless explicitly requested
        if not include_inactive:
            query += " AND u.is_active = 1"
        
        if search_term:
            query += """ AND (
                r.name LIKE %s OR 
                r.cuisine_type LIKE %s OR 
                r.description LIKE %s OR 
                r.address LIKE %s
            )"""
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
            
        if cuisine_type:  # Only add this filter if cuisine_type is not None
            query += " AND r.cuisine_type = %s"
            params.append(cuisine_type)
            
        if location:
            query += " AND r.address LIKE %s"
            params.append(f"%{location}%")
            
        query += " ORDER BY r.rating DESC, r.name ASC"
        
        return execute_query(query, params)
    except Exception as e:
        print(f"Error searching restaurants: {e}")
        return None

def search_menu_items(search_term=None, restaurant_id=None, category=None, 
                     min_price=None, max_price=None, is_vegetarian=None):
    """Search menu items with various filters, including by name and ingredients"""
    try:
        query = """
        SELECT m.*, r.name as restaurant_name, r.cuisine_type
        FROM menus m
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        WHERE m.availability = 'In Stock'
        """
        params = []
        
        if search_term:
            # Search in dish name and description (which may contain ingredients)
            query += """ AND (
                m.dish_name LIKE %s OR 
                m.description LIKE %s
            )"""
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        if restaurant_id:
            query += " AND m.restaurant_id = %s"
            params.append(restaurant_id)
            
        if category and category != "All":
            query += " AND m.category = %s"
            params.append(category)
            
        if min_price:
            query += " AND m.price >= %s"
            params.append(min_price)
            
        if max_price:
            query += " AND m.price <= %s"
            params.append(max_price)
            
        if is_vegetarian is not None:
            query += " AND m.is_vegetarian = %s"
            params.append(is_vegetarian)
            
        query += " ORDER BY m.price ASC, m.dish_name ASC"
        
        return execute_query(query, params)
    except Exception as e:
        print(f"Error searching menu items: {e}")
        return None

def search_orders(customer_id=None, restaurant_id=None, status=None, 
                 start_date=None, end_date=None, customer_name=None, order_id=None, order_number=None):
    """Search orders with various filters including customer name, order date, status, and order number"""
    try:
        # Basic query with JOIN statements
        query = """
        SELECT o.*, 
               c.name as customer_name, 
               r.name as restaurant_name,
               dp.name as delivery_person_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
        WHERE 1=1
        """
        params = []
        
        # Apply individual filters based on provided parameters
        if customer_id:
            query += " AND o.customer_id = %s"
            params.append(customer_id)
            
        if restaurant_id:
            query += " AND o.restaurant_id = %s"
            params.append(restaurant_id)
            
        if status and status != "All":
            query += " AND o.delivery_status = %s"
            params.append(status)
            
        if start_date:
            query += " AND DATE(o.order_date) >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND DATE(o.order_date) <= %s"
            params.append(end_date)
        
        # Search for customer name or order number/ID
        # This is important - we need to handle the search term properly
        if order_number or customer_name:
            search_term = order_number if order_number else customer_name
            # Create a complex OR condition for searching
            query += """ AND (
                c.name LIKE %s 
                OR o.order_id = %s 
                OR CAST(o.order_id AS CHAR) = %s
                OR o.order_number LIKE %s
            )"""
            # Add wildcards for text searches
            name_pattern = f"%{search_term}%"
            order_pattern = f"%{search_term}%"
            # Try to convert to integer for direct ID comparison
            try:
                id_val = int(search_term)
            except (ValueError, TypeError):
                id_val = -1  # Use -1 which won't match any ID
            
            params.extend([name_pattern, id_val, search_term, order_pattern])
        
        # Order by most recent first
        query += " ORDER BY o.order_date DESC"

        # Debug the query
        print(f"Query: {query}")
        print(f"Params: {params}")
        
        return execute_query(query, params)
    except Exception as e:
        print(f"Error searching orders: {e}")
        return None

def get_order_items(order_id):
    """Get all items for a specific order"""
    try:
        query = """
        SELECT oi.*, m.dish_name, m.description
        FROM order_items oi
        JOIN menus m ON oi.menu_id = m.menu_id
        WHERE oi.order_id = %s
        """
        return execute_query(query, [order_id])
    except Exception as e:
        print(f"Error getting order items: {e}")
        return None 