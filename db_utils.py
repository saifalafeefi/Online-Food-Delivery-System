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
    try:
        connection = mysql.connector.connect(**get_connection_config())
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Check your username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
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
                connection.commit()  # Commit the transaction for non-fetch operations
                result = cursor.lastrowid
                
            return result
        except mysql.connector.Error as err:
            error_msg = f"Error executing query: {err}"
            print(error_msg)
            
            # Print the query for debugging
            param_str = str(params) if params else "None"
            print(f"Failed query: {query}")
            print(f"Parameters: {param_str}")
            
            connection.rollback()  # Rollback on error
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None 

def search_restaurants(search_term=None, cuisine_type=None, location=None):
    """Search restaurants by name, cuisine type, or location"""
    try:
        query = """
        SELECT r.*, u.email, u.username 
        FROM restaurants r
        JOIN users u ON r.user_id = u.user_id
        WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (r.name LIKE %s OR r.description LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        if cuisine_type:
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
    """Search menu items with various filters"""
    try:
        query = """
        SELECT m.*, r.name as restaurant_name, r.cuisine_type
        FROM menus m
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        WHERE m.availability = 'In Stock'
        """
        params = []
        
        if search_term:
            query += " AND (m.dish_name LIKE %s OR m.description LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        if restaurant_id:
            query += " AND m.restaurant_id = %s"
            params.append(restaurant_id)
            
        if category:
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
                 start_date=None, end_date=None):
    """Search orders with various filters"""
    try:
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
        
        if customer_id:
            query += " AND o.customer_id = %s"
            params.append(customer_id)
            
        if restaurant_id:
            query += " AND o.restaurant_id = %s"
            params.append(restaurant_id)
            
        if status:
            query += " AND o.delivery_status = %s"
            params.append(status)
            
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY o.order_date DESC"
        
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