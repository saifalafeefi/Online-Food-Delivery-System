import mysql.connector
from dotenv import load_dotenv
import os
import platform
from auth.user import User
from db_utils import get_connection_config

# Load environment variables
load_dotenv()

# Use environment variables from .env file or set defaults if not found
if 'DB_HOST' not in os.environ:
    os.environ['DB_HOST'] = 'localhost'
if 'DB_USER' not in os.environ:
    os.environ['DB_USER'] = 'root'  # Use root as default
if 'DB_PASSWORD' not in os.environ:
    os.environ['DB_PASSWORD'] = ''  # Empty password by default
if 'DB_NAME' not in os.environ:
    os.environ['DB_NAME'] = 'food_delivery'

# Print current working directory and env file location
print(f"Current working directory: {os.getcwd()}")
print(f"Environment variables set:")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}")

def create_database():
    try:
        # Get base configuration without database name
        config = get_connection_config()
        if 'database' in config:
            del config['database']  # Remove database name for initial connection
        
        print(f"\nAttempting to connect with:")
        print(f"Host: {config['host']}")
        print(f"User: {config['user']}")
        print(f"System: {platform.system()}")
        
        # MySQL server connection
        conn = mysql.connector.connect(**config)
        print("Connection successful!")
        
        cursor = conn.cursor()

        # Drop existing database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {os.environ.get('DB_NAME')}")
        print(f"Dropped database {os.environ.get('DB_NAME')} if it existed")
        
        # Create new database
        cursor.execute(f"CREATE DATABASE {os.environ.get('DB_NAME')}")
        print(f"Created database {os.environ.get('DB_NAME')}")
        
        cursor.execute(f"USE {os.environ.get('DB_NAME')}")
        print(f"Using database {os.environ.get('DB_NAME')}")

        #tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARBINARY(255) NOT NULL,
                role ENUM('customer', 'restaurant', 'delivery', 'admin') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(200) NOT NULL,
                contact_number VARCHAR(20) NOT NULL,
                cuisine_type VARCHAR(50) NOT NULL,
                rating DECIMAL(3,2) DEFAULT 0.00,
                opening_time TIME DEFAULT '09:00:00',
                closing_time TIME DEFAULT '22:00:00',
                delivery_radius INT DEFAULT 5,
                min_order_amount DECIMAL(10,2) DEFAULT 0.00,
                is_featured BOOLEAN DEFAULT FALSE,
                logo_url VARCHAR(255),
                banner_url VARCHAR(255),
                description TEXT,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(200) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100) NOT NULL,
                account_status ENUM('Active', 'Inactive') DEFAULT 'Active',
                default_address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS menus (
                menu_id INT AUTO_INCREMENT PRIMARY KEY,
                restaurant_id INT,
                dish_name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                discount_price DECIMAL(10,2),
                category VARCHAR(50) DEFAULT 'Main Course',
                preparation_time INT DEFAULT 20,
                calories INT,
                is_vegetarian BOOLEAN DEFAULT FALSE,
                is_vegan BOOLEAN DEFAULT FALSE,
                is_gluten_free BOOLEAN DEFAULT FALSE,
                spice_level ENUM('Mild', 'Medium', 'Hot', 'Extra Hot') DEFAULT 'Medium',
                image_url VARCHAR(255),
                availability ENUM('In Stock', 'Out of Stock') DEFAULT 'In Stock',
                stock_quantity INT DEFAULT 10,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS delivery_personnel (
                delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                status ENUM('Available', 'Assigned', 'On Delivery') DEFAULT 'Available',
                vehicle_type VARCHAR(50) DEFAULT 'Light Vehicle - Automatic',
                latitude DECIMAL(10, 8) NULL,
                longitude DECIMAL(11, 8) NULL,
                current_location VARCHAR(255),
                avg_rating DECIMAL(3, 2) DEFAULT 0.00,
                total_deliveries INT DEFAULT 0,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                restaurant_id INT,
                order_number VARCHAR(20) UNIQUE,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_address TEXT NOT NULL,
                delivery_status ENUM('Pending', 'Confirmed', 'Preparing', 'On Delivery', 'Delivered', 'Cancelled') DEFAULT 'Pending',
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estimated_delivery_time TIMESTAMP NULL,
                actual_delivery_time TIMESTAMP NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                delivery_fee DECIMAL(10,2) DEFAULT 0.00,
                tax DECIMAL(10,2) DEFAULT 0.00,
                total_amount DECIMAL(10,2) NOT NULL,
                payment_method ENUM('Credit Card', 'Debit Card', 'Cash on Delivery', 'Digital Wallet') DEFAULT 'Cash on Delivery',
                payment_status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending',
                promocode VARCHAR(50),
                discount_amount DECIMAL(10,2) DEFAULT 0.00,
                special_instructions TEXT,
                delivery_person_id INT,
                assigned_time TIMESTAMP NULL,
                tracking_number VARCHAR(20),
                is_rated BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
                FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(delivery_person_id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                menu_id INT,
                quantity INT DEFAULT 1,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                special_requests TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (menu_id) REFERENCES menus(menu_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                order_id INT,
                restaurant_id INT,
                delivery_person_id INT,
                food_rating INT CHECK (food_rating >= 1 AND food_rating <= 5),
                delivery_rating INT CHECK (delivery_rating >= 1 AND delivery_rating <= 5),
                comment TEXT,
                rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
                FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(delivery_person_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS cart (
                cart_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
                cart_id INT,
                menu_id INT,
                quantity INT DEFAULT 1,
                special_requests TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE CASCADE,
                FOREIGN KEY (menu_id) REFERENCES menus(menu_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS favorites (
                favorite_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                restaurant_id INT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
                UNIQUE KEY (customer_id, restaurant_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS addresses (
                address_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                address_type ENUM('Home', 'Work', 'Other') DEFAULT 'Home',
                address_line1 VARCHAR(255) NOT NULL,
                address_line2 VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100),
                postal_code VARCHAR(20) NOT NULL,
                country VARCHAR(100) DEFAULT 'United Arab Emirates',
                is_default BOOLEAN DEFAULT FALSE,
                latitude DECIMAL(10, 8) NULL,
                longitude DECIMAL(11, 8) NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )
            """
        ]

        for table in tables:
            cursor.execute(table)
            print(f"Table created successfully: {table.split('IF NOT EXISTS')[1].split()[0]}")

        # Create an admin user
        admin_password = "admin123"  # Default password for admin
        admin_pwd_hash = User.hash_password(admin_password)
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES ('admin', 'admin@fooddelivery.com', %s, 'admin', NOW())
        """, (admin_pwd_hash,))
        print(f"Admin user created with username 'admin' and password '{admin_password}'")
        
        # Add sample data for testing
        print("Adding sample data for testing...")
        
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES
            ('restaurant1', 'restaurant1@example.com', %s, 'restaurant', NOW()),
            ('customer1', 'customer1@example.com', %s, 'customer', NOW()),
            ('delivery1', 'delivery1@example.com', %s, 'delivery', NOW())
        """, (b'\x00' * 64, b'\x00' * 64, b'\x00' * 64))
        
        # Get the user IDs
        cursor.execute("SELECT user_id, role FROM users WHERE username != 'admin'")
        user_data = cursor.fetchall()
        
        for user_id, role in user_data:
            if role == 'restaurant':
                cursor.execute("""
                INSERT INTO restaurants (user_id, name, address, contact_number, cuisine_type, rating)
                VALUES (%s, 'Sample Restaurant', '123 Main St, Dubai', '+971-55-1234567', 'Italian', 4.5)
                """, (user_id,))
            elif role == 'customer':
                cursor.execute("""
                INSERT INTO customers (user_id, name, address, phone, email)
                VALUES (%s, 'John Doe', '456 Market St, Dubai', '+971-55-9876543', 'customer1@example.com')
                """, (user_id,))
            elif role == 'delivery':
                cursor.execute("""
                INSERT INTO delivery_personnel (user_id, name, phone)
                VALUES (%s, 'Mike Smith', '+971-55-5555555')
                """, (user_id,))
        
        # Get the restaurant ID
        cursor.execute("SELECT restaurant_id FROM restaurants LIMIT 1")
        restaurant_id = cursor.fetchone()[0]
        
        # Add some menu items
        cursor.execute("""
        INSERT INTO menus (restaurant_id, dish_name, description, price, category, stock_quantity)
        VALUES
            (%s, 'Margherita Pizza', 'Classic pizza with tomato sauce, mozzarella, and basil', 45.00, 'Pizza', 20),
            (%s, 'Spaghetti Carbonara', 'Creamy pasta with pancetta and egg', 38.00, 'Pasta', 15),
            (%s, 'Tiramisu', 'Coffee-flavored Italian dessert', 25.00, 'Dessert', 10)
        """, (restaurant_id, restaurant_id, restaurant_id))
        
        conn.commit()
        print("Database setup completed successfully with sample data!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()