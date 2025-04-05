import mysql.connector
from dotenv import load_dotenv
import os

# here we load environment variables
load_dotenv()

def create_database():
    try:
        # MySQL server connection
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = conn.cursor()

        # Drop existing database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME')}")
        
        # Create new database
        cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
        cursor.execute(f"USE {os.getenv('DB_NAME')}")

        #tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(200) NOT NULL,
                contact_number VARCHAR(20) NOT NULL,
                cuisine_type VARCHAR(50) NOT NULL,
                rating DECIMAL(3,2) DEFAULT 0.00,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(200) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                account_status ENUM('Active', 'Inactive') DEFAULT 'Active',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS menus (
                menu_id INT AUTO_INCREMENT PRIMARY KEY,
                restaurant_id INT,
                dish_name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                availability ENUM('In Stock', 'Out of Stock') DEFAULT 'In Stock',
                stock_quantity INT DEFAULT 0,
                info_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS delivery_personnel (
                delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                status ENUM('Available', 'Assigned', 'On Delivery') DEFAULT 'Available'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                menu_id INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_status ENUM('Pending', 'On Delivery', 'Delivered', 'Cancelled') DEFAULT 'Pending',
                delivery_time TIMESTAMP NULL,
                total_amount DECIMAL(10,2),
                payment_status ENUM('Pending', 'Paid', 'Failed') DEFAULT 'Pending',
                delivery_person_id INT,
                assigned_time TIMESTAMP NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (menu_id) REFERENCES menus(menu_id),
                FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(delivery_person_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                restaurant_id INT,
                menu_id INT,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
                FOREIGN KEY (menu_id) REFERENCES menus(menu_id)
            )
            """
        ]

        for table in tables:
            cursor.execute(table)
            print(f"Table created successfully: {table.split('IF NOT EXISTS')[1].split()[0]}")

        conn.commit()
        print("Database setup completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database() 