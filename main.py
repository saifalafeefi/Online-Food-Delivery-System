import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                            QLineEdit, QComboBox, QMessageBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFrame, QDialog, 
                            QGroupBox, QRadioButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from db_utils import execute_query, test_connection
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Test database connection at startup
if not test_connection():
    print("WARNING: Database connection failed. The application may not work correctly.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Food Delivery System")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Add logo/title
        title = QLabel("Food Delivery")
        title.setObjectName("sidebar-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Add menu buttons
        self.menu_buttons = []
        menu_items = [
            "Restaurant Management",
            "Menu Management",
            "Customer Management",
            "Order Management",
            "Delivery Management",
            "Delivery Personnel",
            "Search"
        ]
        
        for item in menu_items:
            btn = QPushButton(item)
            btn.setObjectName("sidebar-button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, text=item: self.switch_page(text))
            sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Add quit button at the bottom
        quit_btn = QPushButton("Quit")
        quit_btn.setObjectName("quit-button")
        quit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(quit_btn)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.restaurant_page = RestaurantPage()
        self.menu_page = MenuPage()
        self.customer_page = CustomerPage()
        self.order_page = OrderPage()
        self.delivery_page = DeliveryPage()
        self.delivery_personnel_page = DeliveryPersonnelPage()
        self.search_page = SearchPage()
        
        self.stacked_widget.addWidget(self.restaurant_page)
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.customer_page)
        self.stacked_widget.addWidget(self.order_page)
        self.stacked_widget.addWidget(self.delivery_page)
        self.stacked_widget.addWidget(self.delivery_personnel_page)
        self.stacked_widget.addWidget(self.search_page)
        
        # Add widgets to main layout
        layout.addWidget(sidebar)
        layout.addWidget(self.stacked_widget)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            #sidebar {
                background-color: #2c3e50;
                border: none;
            }
            #sidebar-title {
                color: white;
                font-size: 24px;
                padding: 20px;
                font-weight: bold;
            }
            #sidebar-button {
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 16px;
            }
            #sidebar-button:hover {
                background-color: #34495e;
            }
            #sidebar-button:checked {
                background-color: #3498db;
            }
            #quit-button {
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 16px;
                background-color: #c0392b;
                margin: 10px;
            }
            #quit-button:hover {
                background-color: #e74c3c;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
    
    def switch_page(self, page_name):
        # Uncheck all buttons
        for btn in self.menu_buttons:
            btn.setChecked(False)
        
        # Check clicked button
        for btn in self.menu_buttons:
            if btn.text() == page_name:
                btn.setChecked(True)
                break
        
        # Switch to corresponding page
        page_index = {
            "Restaurant Management": 0,
            "Menu Management": 1,
            "Customer Management": 2,
            "Order Management": 3,
            "Delivery Management": 4,
            "Delivery Personnel": 5,
            "Search": 6
        }
        self.stacked_widget.setCurrentIndex(page_index[page_name])

class RestaurantPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Restaurant Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Restaurant")
        update_btn = QPushButton("Update Restaurant")
        remove_btn = QPushButton("Remove Restaurant")
        delete_all_btn = QPushButton("Delete All Restaurants")
        
        add_btn.clicked.connect(self.add_restaurant)
        update_btn.clicked.connect(self.update_restaurant)
        remove_btn.clicked.connect(self.remove_restaurant)
        delete_all_btn.clicked.connect(self.delete_all_restaurants)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Address", "Contact", "Cuisine", "Rating"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_restaurants()
    
    def load_restaurants(self):
        restaurants = execute_query("SELECT * FROM restaurants")
        self.table.setRowCount(len(restaurants))
        
        for i, restaurant in enumerate(restaurants):
            self.table.setItem(i, 0, QTableWidgetItem(str(restaurant['restaurant_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(restaurant['name']))
            self.table.setItem(i, 2, QTableWidgetItem(restaurant['address']))
            self.table.setItem(i, 3, QTableWidgetItem(restaurant['contact_number']))
            self.table.setItem(i, 4, QTableWidgetItem(restaurant['cuisine_type']))
            self.table.setItem(i, 5, QTableWidgetItem(str(restaurant['rating'])))
    
    def add_restaurant(self):
        dialog = RestaurantDialog(self)
        if dialog.exec():
            self.load_restaurants()
    
    def update_restaurant(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a restaurant to update")
            return
        
        restaurant_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = RestaurantDialog(self, restaurant_id)
        if dialog.exec():
            self.load_restaurants()
    
    def remove_restaurant(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a restaurant to remove")
            return
        
        restaurant_id = int(self.table.item(selected_items[0].row(), 0).text())
        restaurant_name = self.table.item(selected_items[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {restaurant_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM restaurants WHERE restaurant_id = %s",
                (restaurant_id,),
                fetch=False
            )
            if result:
                self.load_restaurants()
                QMessageBox.information(self, "Success", "Restaurant removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove restaurant")
    
    def delete_all_restaurants(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL restaurants? This will also delete all associated menu items and orders. This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query("DELETE FROM restaurants", fetch=False)
            if result:
                self.load_restaurants()
                QMessageBox.information(self, "Success", "All restaurants deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete restaurants")

class RestaurantDialog(QDialog):
    def __init__(self, parent=None, restaurant_id=None):
        super().__init__(parent)
        self.restaurant_id = restaurant_id
        self.setWindowTitle("Add Restaurant" if not restaurant_id else "Update Restaurant")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.cuisine_input = QLineEdit()
        
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("Contact:"))
        layout.addWidget(self.contact_input)
        layout.addWidget(QLabel("Cuisine:"))
        layout.addWidget(self.cuisine_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_restaurant)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load restaurant data if updating
        if restaurant_id:
            self.load_restaurant_data()
    
    def load_restaurant_data(self):
        restaurant = execute_query(
            "SELECT * FROM restaurants WHERE restaurant_id = %s",
            (self.restaurant_id,)
        )
        if restaurant:
            self.name_input.setText(restaurant[0]['name'])
            self.address_input.setText(restaurant[0]['address'])
            self.contact_input.setText(restaurant[0]['contact_number'])
            self.cuisine_input.setText(restaurant[0]['cuisine_type'])
    
    def save_restaurant(self):
        name = self.name_input.text()
        address = self.address_input.text()
        contact = self.contact_input.text()
        cuisine = self.cuisine_input.text()
        
        if not all([name, address, contact, cuisine]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return
        
        if self.restaurant_id:
            query = """
            UPDATE restaurants 
            SET name = %s, address = %s, contact_number = %s, cuisine_type = %s
            WHERE restaurant_id = %s
            """
            params = (name, address, contact, cuisine, self.restaurant_id)
        else:
            query = """
            INSERT INTO restaurants (name, address, contact_number, cuisine_type)
            VALUES (%s, %s, %s, %s)
            """
            params = (name, address, contact, cuisine)
        
        result = execute_query(query, params, fetch=False)
        if result:
            QMessageBox.information(self, "Success", "Restaurant saved successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save restaurant")

class MenuPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Menu Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add restaurant selector
        restaurant_layout = QHBoxLayout()
        restaurant_layout.addWidget(QLabel("Select Restaurant:"))
        self.restaurant_selector = QComboBox()
        self.restaurant_selector.currentIndexChanged.connect(self.load_menu_items)
        restaurant_layout.addWidget(self.restaurant_selector)
        layout.addLayout(restaurant_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Menu Item")
        update_btn = QPushButton("Update Menu Item")
        remove_btn = QPushButton("Remove Menu Item")
        update_stock_btn = QPushButton("Update Stock")
        delete_all_btn = QPushButton("Delete All Menu Items")
        
        add_btn.clicked.connect(self.show_add_menu_dialog)
        update_btn.clicked.connect(self.show_update_menu_dialog)
        remove_btn.clicked.connect(self.remove_menu_item)
        update_stock_btn.clicked.connect(self.update_stock)
        delete_all_btn.clicked.connect(self.delete_all_menu_items)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(update_stock_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add menu table
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(6)
        self.menu_table.setHorizontalHeaderLabels([
            "Menu ID", "Dish Name", "Description", "Price", 
            "Stock Quantity", "Availability"
        ])
        layout.addWidget(self.menu_table)
        
        self.load_restaurants()
        self.load_menu_items()
    
    def load_menu_items(self):
        try:
            restaurant_id = self.restaurant_selector.currentData()
            if not restaurant_id:
                self.menu_table.setRowCount(0)
                return
            
            query = """
            SELECT menu_id, dish_name, description, price, 
                   stock_quantity, availability
            FROM menus 
            WHERE restaurant_id = %s
            ORDER BY dish_name
            """
            
            menu_items = execute_query(query, (restaurant_id,))
            
            if menu_items is None:
                menu_items = []
                QMessageBox.warning(self, "Warning", "Could not load menu items. Please check database connection.")
            
            self.menu_table.setRowCount(len(menu_items))
            
            for i, item in enumerate(menu_items):
                self.menu_table.setItem(i, 0, QTableWidgetItem(str(item['menu_id'])))
                self.menu_table.setItem(i, 1, QTableWidgetItem(item['dish_name']))
                self.menu_table.setItem(i, 2, QTableWidgetItem(item['description']))
                self.menu_table.setItem(i, 3, QTableWidgetItem(f"${item['price']}"))
                self.menu_table.setItem(i, 4, QTableWidgetItem(str(item['stock_quantity'])))
                self.menu_table.setItem(i, 5, QTableWidgetItem(item['availability']))
                
                # Color code based on availability
                if item['availability'] == "Out of Stock":
                    for j in range(6):
                        self.menu_table.item(i, j).setBackground(QColor("#ffe6e6"))  # Light red
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load menu items: {str(e)}")
    
    def update_stock(self):
        selected_items = self.menu_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a menu item to update stock")
            return
        
        menu_id = int(self.menu_table.item(selected_items[0].row(), 0).text())
        current_stock = int(self.menu_table.item(selected_items[0].row(), 4).text())
        current_availability = self.menu_table.item(selected_items[0].row(), 5).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Stock")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Add stock quantity input
        layout.addWidget(QLabel("Current Stock:"))
        current_stock_label = QLabel(str(current_stock))
        layout.addWidget(current_stock_label)
        
        layout.addWidget(QLabel("New Stock Quantity:"))
        stock_input = QLineEdit()
        stock_input.setText(str(current_stock))
        layout.addWidget(stock_input)
        
        # Add availability selector
        layout.addWidget(QLabel("Availability:"))
        availability_selector = QComboBox()
        availability_selector.addItems(["In Stock", "Out of Stock"])
        availability_selector.setCurrentText(current_availability)
        layout.addWidget(availability_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(lambda: self.save_stock(
            dialog, menu_id, stock_input.text(), 
            availability_selector.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def save_stock(self, dialog, menu_id, new_stock, new_availability):
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                QMessageBox.warning(self, "Warning", "Stock quantity cannot be negative")
                return
            
            result = execute_query(
                "UPDATE menus SET stock_quantity = %s, availability = %s WHERE menu_id = %s",
                (new_stock, new_availability, menu_id),
                fetch=False
            )
            
            if result is not None:
                dialog.accept()
                self.load_menu_items()
                QMessageBox.information(self, "Success", "Stock updated successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to update stock")
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid number for stock quantity")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update stock: {str(e)}")
    
    def delete_all_menu_items(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL menu items? This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            restaurant_id = self.restaurant_selector.currentData()
            if not restaurant_id:
                QMessageBox.warning(self, "Warning", "Please select a restaurant first")
                return
            
            result = execute_query(
                "DELETE FROM menus WHERE restaurant_id = %s",
                (restaurant_id,),
                fetch=False
            )
            
            if result is not None:
                self.load_menu_items()
                QMessageBox.information(self, "Success", "All menu items deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete menu items")
    
    def show_add_menu_dialog(self):
        dialog = MenuItemDialog(self)
        if dialog.exec():
            self.load_menu_items()
    
    def show_update_menu_dialog(self):
        selected_items = self.menu_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a menu item to update")
            return
        
        menu_id = int(self.menu_table.item(selected_items[0].row(), 0).text())
        dialog = MenuItemDialog(self, menu_id)
        if dialog.exec():
            self.load_menu_items()
    
    def remove_menu_item(self):
        selected_items = self.menu_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a menu item to remove")
            return
        
        menu_id = int(self.menu_table.item(selected_items[0].row(), 0).text())
        dish_name = self.menu_table.item(selected_items[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {dish_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM menus WHERE menu_id = %s",
                (menu_id,),
                fetch=False
            )
            if result is not None:
                self.load_menu_items()
                QMessageBox.information(self, "Success", "Menu item removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove menu item")
    
    def load_restaurants(self):
        try:
            restaurants = execute_query(
                "SELECT restaurant_id, name FROM restaurants"
            )
            
            if restaurants is None:
                restaurants = []
                QMessageBox.warning(self, "Warning", "Could not load restaurants")
            
            self.restaurant_selector.clear()
            for restaurant in restaurants:
                self.restaurant_selector.addItem(restaurant['name'], restaurant['restaurant_id'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load restaurants: {str(e)}")

class MenuItemDialog(QDialog):
    def __init__(self, parent=None, menu_id=None):
        super().__init__(parent)
        self.menu_id = menu_id
        self.setWindowTitle("Add Menu Item" if not menu_id else "Update Menu Item")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.restaurant_selector = QComboBox()
        self.dish_name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.price_input = QLineEdit()
        self.availability_selector = QComboBox()
        self.availability_selector.addItems(["In Stock", "Out of Stock"])
        
        # Load restaurants
        restaurants = execute_query("SELECT restaurant_id, name FROM restaurants")
        for restaurant in restaurants:
            self.restaurant_selector.addItem(restaurant['name'], restaurant['restaurant_id'])
        
        layout.addWidget(QLabel("Restaurant:"))
        layout.addWidget(self.restaurant_selector)
        layout.addWidget(QLabel("Dish Name:"))
        layout.addWidget(self.dish_name_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_input)
        layout.addWidget(QLabel("Availability:"))
        layout.addWidget(self.availability_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_menu_item)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load menu item data if updating
        if menu_id:
            self.load_menu_item_data()
    
    def load_menu_item_data(self):
        menu_item = execute_query(
            "SELECT * FROM menus WHERE menu_id = %s",
            (self.menu_id,)
        )
        if menu_item:
            # Set restaurant
            index = self.restaurant_selector.findData(menu_item[0]['restaurant_id'])
            if index >= 0:
                self.restaurant_selector.setCurrentIndex(index)
            
            self.dish_name_input.setText(menu_item[0]['dish_name'])
            self.description_input.setText(menu_item[0]['description'] or '')
            self.price_input.setText(str(menu_item[0]['price']))
            
            # Set availability
            index = self.availability_selector.findText(menu_item[0]['availability'])
            if index >= 0:
                self.availability_selector.setCurrentIndex(index)
    
    def save_menu_item(self):
        restaurant_id = self.restaurant_selector.currentData()
        dish_name = self.dish_name_input.text()
        description = self.description_input.text()
        price = self.price_input.text()
        availability = self.availability_selector.currentText()
        
        if not all([restaurant_id, dish_name, price]):
            QMessageBox.warning(self, "Warning", "Please fill in all required fields")
            return
        
        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Price must be a valid number")
            return
        
        if self.menu_id:
            query = """
            UPDATE menus 
            SET restaurant_id = %s, dish_name = %s, description = %s, 
                price = %s, availability = %s
            WHERE menu_id = %s
            """
            params = (restaurant_id, dish_name, description, price, availability, self.menu_id)
        else:
            query = """
            INSERT INTO menus (restaurant_id, dish_name, description, price, availability)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (restaurant_id, dish_name, description, price, availability)
        
        result = execute_query(query, params, fetch=False)
        if result:
            QMessageBox.information(self, "Success", "Menu item saved successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save menu item")

class CustomerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Customer Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Customer")
        update_btn = QPushButton("Update Customer")
        remove_btn = QPushButton("Remove Customer")
        view_orders_btn = QPushButton("View Order History")
        delete_all_btn = QPushButton("Delete All Customers")
        
        add_btn.clicked.connect(self.add_customer)
        update_btn.clicked.connect(self.update_customer)
        remove_btn.clicked.connect(self.remove_customer)
        view_orders_btn.clicked.connect(self.view_order_history)
        delete_all_btn.clicked.connect(self.delete_all_customers)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(view_orders_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Address", "Phone", "Email", "Status", "Registration Date", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_customers()
    
    def load_customers(self):
        customers = execute_query("SELECT * FROM customers")
        self.table.setRowCount(len(customers))
        
        for i, customer in enumerate(customers):
            self.table.setItem(i, 0, QTableWidgetItem(str(customer['customer_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(customer['name']))
            self.table.setItem(i, 2, QTableWidgetItem(customer['address']))
            self.table.setItem(i, 3, QTableWidgetItem(customer['phone']))
            self.table.setItem(i, 4, QTableWidgetItem(customer['email']))
            self.table.setItem(i, 5, QTableWidgetItem(customer['account_status']))
            self.table.setItem(i, 6, QTableWidgetItem(str(customer['registration_date'])))
            self.table.setItem(i, 7, QTableWidgetItem(str(customer['info_update_time'])))
    
    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_customers()
    
    def update_customer(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a customer to update")
            return
        
        customer_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = CustomerDialog(self, customer_id)
        if dialog.exec():
            self.load_customers()
    
    def remove_customer(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a customer to remove")
            return
        
        customer_id = int(self.table.item(selected_items[0].row(), 0).text())
        customer_name = self.table.item(selected_items[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {customer_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM customers WHERE customer_id = %s",
                (customer_id,),
                fetch=False
            )
            if result:
                self.load_customers()
                QMessageBox.information(self, "Success", "Customer removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove customer")
    
    def view_order_history(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a customer to view order history")
            return
        
        customer_id = int(self.table.item(selected_items[0].row(), 0).text())
        customer_name = self.table.item(selected_items[0].row(), 1).text()
        
        dialog = OrderHistoryDialog(self, customer_id, customer_name)
        dialog.exec()
    
    def delete_all_customers(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL customers? This will also delete all associated orders. This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query("DELETE FROM customers", fetch=False)
            if result:
                self.load_customers()
                QMessageBox.information(self, "Success", "All customers deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete customers")

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_id=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.setWindowTitle("Add Customer" if not customer_id else "Update Customer")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.status_selector = QComboBox()
        self.status_selector.addItems(["Active", "Inactive"])
        
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Account Status:"))
        layout.addWidget(self.status_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_customer)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load customer data if updating
        if customer_id:
            self.load_customer_data()
    
    def load_customer_data(self):
        customer = execute_query(
            "SELECT * FROM customers WHERE customer_id = %s",
            (self.customer_id,)
        )
        if customer:
            self.name_input.setText(customer[0]['name'])
            self.address_input.setText(customer[0]['address'])
            self.phone_input.setText(customer[0]['phone'])
            self.email_input.setText(customer[0]['email'])
            
            # Set status
            index = self.status_selector.findText(customer[0]['account_status'])
            if index >= 0:
                self.status_selector.setCurrentIndex(index)
    
    def save_customer(self):
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        status = self.status_selector.currentText()
        
        if not all([name, address, phone, email]):
            QMessageBox.warning(self, "Warning", "Please fill in all required fields")
            return
        
        if self.customer_id:
            query = """
            UPDATE customers 
            SET name = %s, address = %s, phone = %s, email = %s, account_status = %s
            WHERE customer_id = %s
            """
            params = (name, address, phone, email, status, self.customer_id)
        else:
            query = """
            INSERT INTO customers (name, address, phone, email, account_status)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (name, address, phone, email, status)
        
        result = execute_query(query, params, fetch=False)
        if result:
            QMessageBox.information(self, "Success", "Customer saved successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save customer")

class OrderHistoryDialog(QDialog):
    def __init__(self, parent=None, customer_id=None, customer_name=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.setWindowTitle(f"Order History - {customer_name}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel(f"Order History for {customer_name}")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Order ID", "Restaurant", "Dish", "Order Date", "Delivery Status", 
            "Delivery Time", "Total Amount", "Payment Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Load order history
        self.load_order_history()
    
    def load_order_history(self):
        query = """
        SELECT o.*, r.name as restaurant_name, m.dish_name
        FROM orders o
        JOIN menus m ON o.menu_id = m.menu_id
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        WHERE o.customer_id = %s
        ORDER BY o.order_date DESC
        """
        orders = execute_query(query, (self.customer_id,))
        
        self.table.setRowCount(len(orders))
        
        for i, order in enumerate(orders):
            self.table.setItem(i, 0, QTableWidgetItem(str(order['order_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(order['restaurant_name']))
            self.table.setItem(i, 2, QTableWidgetItem(order['dish_name']))
            self.table.setItem(i, 3, QTableWidgetItem(str(order['order_date'])))
            self.table.setItem(i, 4, QTableWidgetItem(order['delivery_status']))
            self.table.setItem(i, 5, QTableWidgetItem(str(order['delivery_time'] or 'Not delivered')))
            self.table.setItem(i, 6, QTableWidgetItem(f"${order['total_amount']:.2f}"))
            self.table.setItem(i, 7, QTableWidgetItem(order['payment_status']))

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Order Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add buttons
        button_layout = QHBoxLayout()
        place_order_btn = QPushButton("Place New Order")
        update_status_btn = QPushButton("Update Order Status")
        delete_all_btn = QPushButton("Delete All Orders")
        
        place_order_btn.clicked.connect(self.show_place_order_dialog)
        update_status_btn.clicked.connect(self.show_update_status_dialog)
        delete_all_btn.clicked.connect(self.delete_all_orders)
        
        button_layout.addWidget(place_order_btn)
        button_layout.addWidget(update_status_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add order table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(8)
        self.order_table.setHorizontalHeaderLabels([
            "Order ID", "Customer", "Restaurant", "Menu Item", 
            "Quantity", "Stock Left", "Status", "Payment Status"
        ])
        layout.addWidget(self.order_table)
        
        self.load_orders()
    
    def load_orders(self):
        try:
            query = """
            SELECT o.order_id, o.quantity, o.delivery_status, o.payment_status,
                   c.name as customer_name, r.name as restaurant_name,
                   m.dish_name, m.stock_quantity
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            JOIN menus m ON o.menu_id = m.menu_id
            ORDER BY o.order_time DESC
            """
            
            logging.debug("Executing query to load orders: %s", query)
            orders = execute_query(query)
            logging.debug("Orders loaded: %s", orders)
            
            if orders is None:
                orders = []
                QMessageBox.warning(self, "Warning", "Could not load orders. Please check database connection.")
            
            self.order_table.setRowCount(len(orders))
            
            for i, order in enumerate(orders):
                self.order_table.setItem(i, 0, QTableWidgetItem(str(order['order_id'])))
                self.order_table.setItem(i, 1, QTableWidgetItem(order['customer_name']))
                self.order_table.setItem(i, 2, QTableWidgetItem(order['restaurant_name']))
                self.order_table.setItem(i, 3, QTableWidgetItem(order['dish_name']))
                self.order_table.setItem(i, 4, QTableWidgetItem(str(order['quantity'])))
                self.order_table.setItem(i, 5, QTableWidgetItem(str(order['stock_quantity'])))
                self.order_table.setItem(i, 6, QTableWidgetItem(order['delivery_status']))
                self.order_table.setItem(i, 7, QTableWidgetItem(order['payment_status']))
                
                # Color code based on status
                if order['delivery_status'] == "Delivered":
                    for j in range(8):
                        self.order_table.item(i, j).setBackground(QColor("#e6ffe6"))  # Light green
                elif order['delivery_status'] == "Cancelled":
                    for j in range(8):
                        self.order_table.item(i, j).setBackground(QColor("#ffe6e6"))  # Light red
                
        except Exception as e:
            logging.error("Failed to load orders: %s", str(e))
            QMessageBox.critical(self, "Error", f"Failed to load orders: {str(e)}")
    
    def show_place_order_dialog(self):
        dialog = PlaceOrderDialog(self)
        if dialog.exec():
            self.load_orders()
    
    def show_update_status_dialog(self):
        selected_items = self.order_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an order to update")
            return
        
        order_id = int(self.order_table.item(selected_items[0].row(), 0).text())
        current_status = self.order_table.item(selected_items[0].row(), 6).text()
        
        dialog = UpdateOrderStatusDialog(self, order_id, current_status)
        if dialog.exec():
            self.load_orders()
    
    def delete_all_orders(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL orders? This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                logging.debug("Executing query to delete all orders")
                result = execute_query("DELETE FROM orders", fetch=False)
                if result is not None:
                    self.load_orders()
                    QMessageBox.information(self, "Success", "All orders deleted successfully!")
                else:
                    logging.error("Failed to delete orders: No result returned")
                    QMessageBox.critical(self, "Error", "Failed to delete orders")
            except Exception as e:
                logging.error("Failed to delete orders: %s", str(e))
                QMessageBox.critical(self, "Error", f"Failed to delete orders: {str(e)}")

class PlaceOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Place New Order")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.customer_selector = QComboBox()
        self.restaurant_selector = QComboBox()
        self.menu_selector = QComboBox()
        self.quantity_input = QLineEdit()
        self.quantity_input.setText("1")
        
        # Load customers
        customers = execute_query("SELECT customer_id, name FROM customers WHERE account_status = 'Active'")
        for customer in customers:
            self.customer_selector.addItem(customer['name'], customer['customer_id'])
        
        # Load restaurants
        restaurants = execute_query("SELECT restaurant_id, name FROM restaurants")
        for restaurant in restaurants:
            self.restaurant_selector.addItem(restaurant['name'], restaurant['restaurant_id'])
        
        # Connect signals
        self.restaurant_selector.currentIndexChanged.connect(self.load_menu_items)
        
        layout.addWidget(QLabel("Customer:"))
        layout.addWidget(self.customer_selector)
        layout.addWidget(QLabel("Restaurant:"))
        layout.addWidget(self.restaurant_selector)
        layout.addWidget(QLabel("Menu Item:"))
        layout.addWidget(self.menu_selector)
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.quantity_input)
        
        # Add order summary
        self.summary_label = QLabel("Order Summary:")
        self.summary_label.setObjectName("summary-label")
        layout.addWidget(self.summary_label)
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        # Connect signals for summary update
        self.menu_selector.currentIndexChanged.connect(self.update_summary)
        self.quantity_input.textChanged.connect(self.update_summary)
        
        # Add buttons
        button_layout = QHBoxLayout()
        place_btn = QPushButton("Place Order")
        cancel_btn = QPushButton("Cancel")
        
        place_btn.clicked.connect(self.place_order)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(place_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load initial menu items
        self.load_menu_items()
    
    def load_menu_items(self):
        self.menu_selector.clear()
        restaurant_id = self.restaurant_selector.currentData()
        
        if restaurant_id:
            query = """
            SELECT menu_id, dish_name, price, availability, stock_quantity 
            FROM menus 
            WHERE restaurant_id = %s
            """
            menu_items = execute_query(query, (restaurant_id,))
            
            for item in menu_items:
                # Only add items that are in stock and have stock quantity > 0
                if item['availability'] == 'In Stock' and item['stock_quantity'] > 0:
                    self.menu_selector.addItem(
                        f"{item['dish_name']} - ${item['price']:.2f} (Stock: {item['stock_quantity']})", 
                        item['menu_id']
                    )
    
    def update_summary(self):
        menu_id = self.menu_selector.currentData()
        if not menu_id:
            self.details_label.setText("Please select a menu item")
            return
        
        try:
            quantity = int(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            self.details_label.setText("Please enter a valid quantity")
            return
        
        menu_item = execute_query(
            "SELECT dish_name, price, stock_quantity FROM menus WHERE menu_id = %s",
            (menu_id,)
        )[0]
        
        if quantity > menu_item['stock_quantity']:
            self.details_label.setText(f"Error: Only {menu_item['stock_quantity']} items available in stock")
            return
        
        total = menu_item['price'] * quantity
        self.details_label.setText(
            f"Dish: {menu_item['dish_name']}\n"
            f"Price: ${menu_item['price']:.2f}\n"
            f"Quantity: {quantity}\n"
            f"Available Stock: {menu_item['stock_quantity']}\n"
            f"Total: ${total:.2f}"
        )
    
    def place_order(self):
        try:
            customer_id = self.customer_selector.currentData()
            restaurant_id = self.restaurant_selector.currentData()
            menu_id = self.menu_selector.currentData()
            
            if not customer_id:
                QMessageBox.warning(self, "Warning", "Please select a customer")
                return
            
            if not restaurant_id:
                QMessageBox.warning(self, "Warning", "Please select a restaurant")
                return
            
            if not menu_id:
                QMessageBox.warning(self, "Warning", "Please select a menu item")
                return
            
            quantity = int(self.quantity_input.text() or 0)
            if quantity <= 0:
                QMessageBox.warning(self, "Warning", "Please enter a valid quantity")
                return
            
            # Get current stock for the menu item
            current_stock = execute_query(
                "SELECT stock_quantity FROM menus WHERE menu_id = %s",
                (menu_id,)
            )
            
            if not current_stock or current_stock[0]['stock_quantity'] < quantity:
                QMessageBox.warning(self, "Warning", "Item is no longer available in stock")
                return
            
            # Place order
            logging.debug("Placing order for customer_id: %s, restaurant_id: %s, menu_id: %s, quantity: %s", 
                        customer_id, restaurant_id, menu_id, quantity)
            result = execute_query(
                """
                INSERT INTO orders (
                    customer_id, restaurant_id, menu_id, quantity,
                    delivery_status, payment_status, order_time
                ) VALUES (%s, %s, %s, %s, 'Pending', 'Pending', CURRENT_TIMESTAMP)
                """,
                (customer_id, restaurant_id, menu_id, quantity),
                fetch=False
            )
            
            if result is not None:
                # Update menu stock
                execute_query(
                    """
                    UPDATE menus 
                    SET stock_quantity = stock_quantity - %s,
                        availability = CASE 
                            WHEN stock_quantity - %s = 0 THEN 'Out of Stock'
                            ELSE 'In Stock'
                        END
                    WHERE menu_id = %s
                    """,
                    (quantity, quantity, menu_id),
                    fetch=False
                )
                
                QMessageBox.information(self, "Success", "Order placed successfully!")
                self.accept()
            else:
                logging.error("Failed to place order: No result returned")
                QMessageBox.critical(self, "Error", "Failed to place order")
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid quantity")
        except Exception as e:
            logging.error("Failed to place order: %s", str(e))
            QMessageBox.critical(self, "Error", f"Failed to place order: {str(e)}")

class UpdateOrderStatusDialog(QDialog):
    def __init__(self, parent=None, order_id=None, current_status=None):
        super().__init__(parent)
        self.order_id = order_id
        self.current_status = current_status
        self.setWindowTitle(f"Update Order Status - Order #{order_id}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add status selector
        layout.addWidget(QLabel("Current Status:"))
        current_status_label = QLabel(current_status)
        current_status_label.setObjectName("current-status")
        layout.addWidget(current_status_label)
        
        layout.addWidget(QLabel("New Status:"))
        self.status_selector = QComboBox()
        
        # Always show all status options
        self.status_selector.addItems(["Pending", "On Delivery", "Delivered", "Cancelled"])
        
        # Set current status as selected
        index = self.status_selector.findText(current_status)
        if index >= 0:
            self.status_selector.setCurrentIndex(index)
        
        layout.addWidget(self.status_selector)
        
        # Add payment status selector
        layout.addWidget(QLabel("Payment Status:"))
        self.payment_selector = QComboBox()
        self.payment_selector.addItems(["Pending", "Paid", "Failed"])
        layout.addWidget(self.payment_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_status)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def save_status(self):
        new_status = self.status_selector.currentText()
        payment_status = self.payment_selector.currentText()
        
        try:
            # Get the menu_id and quantity for this order first
            order_result = execute_query(
                "SELECT menu_id, quantity FROM orders WHERE order_id = %s",
                (self.order_id,)
            )
            
            if not order_result or len(order_result) == 0:
                QMessageBox.critical(self, "Error", "Could not find menu item for this order")
                return
                
            menu_id = order_result[0]['menu_id']
            quantity = order_result[0]['quantity']
            
            # Update order status
            query = """
            UPDATE orders 
            SET delivery_status = %s, payment_status = %s
            """
            params = [new_status, payment_status]
            
            # If status is Delivered, set delivery time
            if new_status == "Delivered":
                query += ", delivery_time = CURRENT_TIMESTAMP"
            
            query += " WHERE order_id = %s"
            params.append(self.order_id)
            
            result = execute_query(query, tuple(params), fetch=False)
            
            if result is not None:
                # Update menu availability based on order status
                if new_status == "Cancelled":
                    # If order is cancelled, restore the stock quantity
                    execute_query(
                        "UPDATE menus SET stock_quantity = stock_quantity + %s, availability = 'In Stock' WHERE menu_id = %s",
                        (quantity, menu_id),
                        fetch=False
                    )
                elif new_status == "Delivered" and self.current_status == "On Delivery":
                    # If order is delivered, keep the menu item out of stock
                    execute_query(
                        "UPDATE menus SET availability = 'Out of Stock' WHERE menu_id = %s AND stock_quantity = 0",
                        (menu_id,),
                        fetch=False
                    )
                
                QMessageBox.information(self, "Success", "Order status updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update order status. Please check the database connection.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update order status: {str(e)}")

class OrderDetailsDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle(f"Order Details - Order #{order_id}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Get order details
        query = """
        SELECT o.*, c.name as customer_name, c.address as customer_address, c.phone as customer_phone,
               r.name as restaurant_name, r.address as restaurant_address, r.contact_number as restaurant_phone,
               m.dish_name, m.description, m.price
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN menus m ON o.menu_id = m.menu_id
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        WHERE o.order_id = %s
        """
        order = execute_query(query, (order_id,))[0]
        
        # Add header
        header = QLabel(f"Order Details - #{order_id}")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add order details
        details_layout = QVBoxLayout()
        
        # Customer details
        customer_group = QFrame()
        customer_group.setObjectName("details-group")
        customer_layout = QVBoxLayout(customer_group)
        customer_layout.addWidget(QLabel("Customer Information"))
        customer_layout.addWidget(QLabel(f"Name: {order['customer_name']}"))
        customer_layout.addWidget(QLabel(f"Address: {order['customer_address']}"))
        customer_layout.addWidget(QLabel(f"Phone: {order['customer_phone']}"))
        details_layout.addWidget(customer_group)
        
        # Restaurant details
        restaurant_group = QFrame()
        restaurant_group.setObjectName("details-group")
        restaurant_layout = QVBoxLayout(restaurant_group)
        restaurant_layout.addWidget(QLabel("Restaurant Information"))
        restaurant_layout.addWidget(QLabel(f"Name: {order['restaurant_name']}"))
        restaurant_layout.addWidget(QLabel(f"Address: {order['restaurant_address']}"))
        restaurant_layout.addWidget(QLabel(f"Phone: {order['restaurant_phone']}"))
        details_layout.addWidget(restaurant_group)
        
        # Order details
        order_group = QFrame()
        order_group.setObjectName("details-group")
        order_layout = QVBoxLayout(order_group)
        order_layout.addWidget(QLabel("Order Information"))
        order_layout.addWidget(QLabel(f"Dish: {order['dish_name']}"))
        order_layout.addWidget(QLabel(f"Description: {order['description'] or 'N/A'}"))
        order_layout.addWidget(QLabel(f"Price: ${order['price']:.2f}"))
        order_layout.addWidget(QLabel(f"Total Amount: ${order['total_amount']:.2f}"))
        order_layout.addWidget(QLabel(f"Order Date: {order['order_date']}"))
        order_layout.addWidget(QLabel(f"Delivery Status: {order['delivery_status']}"))
        order_layout.addWidget(QLabel(f"Delivery Time: {order['delivery_time'] or 'Not delivered'}"))
        order_layout.addWidget(QLabel(f"Payment Status: {order['payment_status']}"))
        details_layout.addWidget(order_group)
        
        layout.addLayout(details_layout)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class DeliveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Delivery Tracking")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add filter section
        filter_layout = QHBoxLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "On Delivery", "Delivered", "Cancelled"])
        self.status_filter.currentTextChanged.connect(self.load_deliveries)
        
        # Date filter
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Today", "This Week", "This Month", "All Time"])
        self.date_filter.currentTextChanged.connect(self.load_deliveries)
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.date_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        assign_btn = QPushButton("Assign Delivery")
        update_status_btn = QPushButton("Update Status")
        view_details_btn = QPushButton("View Details")
        delete_all_btn = QPushButton("Delete All Deliveries")
        
        assign_btn.clicked.connect(self.assign_delivery)
        update_status_btn.clicked.connect(self.update_delivery_status)
        view_details_btn.clicked.connect(self.view_delivery_details)
        delete_all_btn.clicked.connect(self.delete_all_deliveries)
        
        button_layout.addWidget(assign_btn)
        button_layout.addWidget(update_status_btn)
        button_layout.addWidget(view_details_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Order ID", "Customer", "Restaurant", "Delivery Personnel", 
            "Status", "Assigned Time", "Delivery Time", "Estimated Time"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_deliveries()
    
    def load_deliveries(self):
        status_filter = self.status_filter.currentText()
        date_filter = self.date_filter.currentText()
        
        query = """
        SELECT o.*, c.name as customer_name, r.name as restaurant_name,
               dp.name as delivery_person_name, dp.phone as delivery_person_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN menus m ON o.menu_id = m.menu_id
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
        WHERE 1=1
        """
        params = []
        
        if status_filter != "All":
            query += " AND o.delivery_status = %s"
            params.append(status_filter)
        
        if date_filter == "Today":
            query += " AND DATE(o.order_date) = CURDATE()"
        elif date_filter == "This Week":
            query += " AND YEARWEEK(o.order_date) = YEARWEEK(CURDATE())"
        elif date_filter == "This Month":
            query += " AND MONTH(o.order_date) = MONTH(CURDATE()) AND YEAR(o.order_date) = YEAR(CURDATE())"
        
        query += " ORDER BY o.order_date DESC"
        
        try:
            deliveries = execute_query(query, tuple(params) if params else None)
            if deliveries is None:
                deliveries = []
            
            self.table.setRowCount(len(deliveries))
            
            for i, delivery in enumerate(deliveries):
                self.table.setItem(i, 0, QTableWidgetItem(str(delivery['order_id'])))
                self.table.setItem(i, 1, QTableWidgetItem(delivery['customer_name']))
                self.table.setItem(i, 2, QTableWidgetItem(delivery['restaurant_name']))
                self.table.setItem(i, 3, QTableWidgetItem(delivery['delivery_person_name'] or 'Not assigned'))
                self.table.setItem(i, 4, QTableWidgetItem(delivery['delivery_status']))
                self.table.setItem(i, 5, QTableWidgetItem(str(delivery['assigned_time'] or 'Not assigned')))
                self.table.setItem(i, 6, QTableWidgetItem(str(delivery['delivery_time'] or 'Not delivered')))
                
                # Calculate estimated delivery time (30 minutes from assignment)
                if delivery['assigned_time'] and not delivery['delivery_time']:
                    estimated_time = delivery['assigned_time'] + timedelta(minutes=30)
                    self.table.setItem(i, 7, QTableWidgetItem(str(estimated_time)))
                else:
                    self.table.setItem(i, 7, QTableWidgetItem('N/A'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load deliveries: {str(e)}")
            self.table.setRowCount(0)
    
    def assign_delivery(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an order to assign delivery")
            return
        
        order_id = int(self.table.item(selected_items[0].row(), 0).text())
        current_status = self.table.item(selected_items[0].row(), 4).text()
        
        if current_status != "Pending":
            QMessageBox.warning(self, "Warning", "Can only assign delivery to pending orders")
            return
        
        dialog = AssignDeliveryDialog(self, order_id)
        if dialog.exec():
            self.load_deliveries()
    
    def update_delivery_status(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a delivery to update")
            return
        
        order_id = int(self.table.item(selected_items[0].row(), 0).text())
        current_status = self.table.item(selected_items[0].row(), 4).text()
        
        dialog = UpdateDeliveryStatusDialog(self, order_id, current_status)
        if dialog.exec():
            self.load_deliveries()
    
    def view_delivery_details(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a delivery to view details")
            return
        
        order_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = DeliveryDetailsDialog(self, order_id)
        dialog.exec()
    
    def delete_all_deliveries(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL deliveries? This will also delete all associated orders. This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query("DELETE FROM orders WHERE delivery_person_id IS NOT NULL", fetch=False)
            if result:
                self.load_deliveries()
                QMessageBox.information(self, "Success", "All deliveries deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete deliveries")

class AssignDeliveryDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle(f"Assign Delivery - Order #{order_id}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add delivery person selector
        layout.addWidget(QLabel("Select Delivery Personnel:"))
        self.delivery_selector = QComboBox()
        
        # Load available delivery personnel
        query = """
        SELECT delivery_person_id, name, phone 
        FROM delivery_personnel 
        WHERE status = 'Available'
        """
        delivery_personnel = execute_query(query)
        
        if delivery_personnel:
            for person in delivery_personnel:
                self.delivery_selector.addItem(
                    f"{person['name']} ({person['phone']})", 
                    person['delivery_person_id']
                )
        else:
            QMessageBox.warning(self, "Warning", "No delivery personnel available at the moment")
            self.reject()
            return
        
        layout.addWidget(self.delivery_selector)
        
        # Add estimated delivery time
        layout.addWidget(QLabel("Estimated Delivery Time:"))
        estimated_time = QLabel("30 minutes from assignment")
        estimated_time.setObjectName("estimated-time")
        layout.addWidget(estimated_time)
        
        # Add buttons
        button_layout = QHBoxLayout()
        assign_btn = QPushButton("Assign")
        cancel_btn = QPushButton("Cancel")
        
        assign_btn.clicked.connect(self.assign_delivery)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(assign_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def assign_delivery(self):
        delivery_person_id = self.delivery_selector.currentData()
        
        if not delivery_person_id:
            QMessageBox.warning(self, "Warning", "Please select a delivery person")
            return
        
        # Update order with delivery person and status
        query = """
        UPDATE orders 
        SET delivery_person_id = %s, 
            delivery_status = 'On Delivery',
            assigned_time = CURRENT_TIMESTAMP
        WHERE order_id = %s
        """
        result = execute_query(query, (delivery_person_id, self.order_id), fetch=False)
        
        if result:
            # Update delivery person status
            execute_query(
                "UPDATE delivery_personnel SET status = 'On Delivery' WHERE delivery_person_id = %s",
                (delivery_person_id,),
                fetch=False
            )
            
            QMessageBox.information(self, "Success", "Delivery assigned successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to assign delivery")

class UpdateDeliveryStatusDialog(QDialog):
    def __init__(self, parent=None, order_id=None, current_status=None):
        super().__init__(parent)
        self.order_id = order_id
        self.current_status = current_status
        self.setWindowTitle(f"Update Delivery Status - Order #{order_id}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add status selector
        layout.addWidget(QLabel("Current Status:"))
        current_status_label = QLabel(current_status)
        current_status_label.setObjectName("current-status")
        layout.addWidget(current_status_label)
        
        layout.addWidget(QLabel("New Status:"))
        self.status_selector = QComboBox()
        
        # Always show all status options
        self.status_selector.addItems(["Pending", "On Delivery", "Delivered", "Cancelled"])
        
        # Set current status as selected
        index = self.status_selector.findText(current_status)
        if index >= 0:
            self.status_selector.setCurrentIndex(index)
        
        layout.addWidget(self.status_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_status)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def save_status(self):
        new_status = self.status_selector.currentText()
        
        # Update delivery status
        query = """
        UPDATE orders 
        SET delivery_status = %s
        """
        params = [new_status]
        
        # If status is Delivered, set delivery time
        if new_status == "Delivered":
            query += ", delivery_time = CURRENT_TIMESTAMP"
        
        query += " WHERE order_id = %s"
        params.append(self.order_id)
        
        result = execute_query(query, tuple(params), fetch=False)
        
        if result:
            # If delivery is completed or cancelled, update delivery person availability
            if new_status in ["Delivered", "Cancelled"]:
                delivery_person = execute_query(
                    "SELECT delivery_person_id FROM orders WHERE order_id = %s",
                    (self.order_id,)
                )
                
                execute_query(
                    "UPDATE delivery_personnel SET availability = 'Available' WHERE delivery_person_id = %s",
                    (delivery_person['delivery_person_id'],),
                    fetch=False
                )
            
            QMessageBox.information(self, "Success", "Delivery status updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update delivery status")

class DeliveryDetailsDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle(f"Delivery Details - Order #{order_id}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Get delivery details
        query = """
        SELECT o.*, c.name as customer_name, c.address as customer_address, c.phone as customer_phone,
               r.name as restaurant_name, r.address as restaurant_address, r.contact_number as restaurant_phone,
               dp.name as delivery_person_name, dp.phone as delivery_person_phone, dp.vehicle_type
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN menus m ON o.menu_id = m.menu_id
        JOIN restaurants r ON m.restaurant_id = r.restaurant_id
        LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
        WHERE o.order_id = %s
        """
        delivery = execute_query(query, (order_id,))[0]
        
        # Add header
        header = QLabel(f"Delivery Details - #{order_id}")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add delivery details
        details_layout = QVBoxLayout()
        
        # Customer details
        customer_group = QFrame()
        customer_group.setObjectName("details-group")
        customer_layout = QVBoxLayout(customer_group)
        customer_layout.addWidget(QLabel("Customer Information"))
        customer_layout.addWidget(QLabel(f"Name: {delivery['customer_name']}"))
        customer_layout.addWidget(QLabel(f"Address: {delivery['customer_address']}"))
        customer_layout.addWidget(QLabel(f"Phone: {delivery['customer_phone']}"))
        details_layout.addWidget(customer_group)
        
        # Restaurant details
        restaurant_group = QFrame()
        restaurant_group.setObjectName("details-group")
        restaurant_layout = QVBoxLayout(restaurant_group)
        restaurant_layout.addWidget(QLabel("Restaurant Information"))
        restaurant_layout.addWidget(QLabel(f"Name: {delivery['restaurant_name']}"))
        restaurant_layout.addWidget(QLabel(f"Address: {delivery['restaurant_address']}"))
        restaurant_layout.addWidget(QLabel(f"Phone: {delivery['restaurant_phone']}"))
        details_layout.addWidget(restaurant_group)
        
        # Delivery person details
        if delivery['delivery_person_id']:
            delivery_group = QFrame()
            delivery_group.setObjectName("details-group")
            delivery_layout = QVBoxLayout(delivery_group)
            delivery_layout.addWidget(QLabel("Delivery Personnel Information"))
            delivery_layout.addWidget(QLabel(f"Name: {delivery['delivery_person_name']}"))
            delivery_layout.addWidget(QLabel(f"Phone: {delivery['delivery_person_phone']}"))
            delivery_layout.addWidget(QLabel(f"Vehicle: {delivery['vehicle_type']}"))
            details_layout.addWidget(delivery_group)
        
        # Delivery status details
        status_group = QFrame()
        status_group.setObjectName("details-group")
        status_layout = QVBoxLayout(status_group)
        status_layout.addWidget(QLabel("Delivery Status Information"))
        status_layout.addWidget(QLabel(f"Status: {delivery['delivery_status']}"))
        status_layout.addWidget(QLabel(f"Assigned Time: {delivery['assigned_time'] or 'Not assigned'}"))
        status_layout.addWidget(QLabel(f"Delivery Time: {delivery['delivery_time'] or 'Not delivered'}"))
        
        # Add estimated time if delivery is in progress
        if delivery['assigned_time'] and not delivery['delivery_time']:
            estimated_time = delivery['assigned_time'] + timedelta(minutes=30)
            status_layout.addWidget(QLabel(f"Estimated Delivery: {estimated_time}"))
        
        details_layout.addWidget(status_group)
        
        layout.addLayout(details_layout)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class SearchPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Search")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add search filters
        filter_layout = QHBoxLayout()
        
        # Search type selector
        self.search_type = QComboBox()
        self.search_type.addItems([
            "Restaurants", "Menu Items", "Customers", "Orders", "Deliveries"
        ])
        self.search_type.currentTextChanged.connect(self.update_search_fields)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search term...")
        self.search_field.textChanged.connect(self.perform_search)
        
        # Advanced filters
        self.advanced_filters = QComboBox()
        self.advanced_filters.addItem("No Additional Filters")
        self.advanced_filters.currentTextChanged.connect(self.perform_search)
        
        filter_layout.addWidget(QLabel("Search Type:"))
        filter_layout.addWidget(self.search_type)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_field)
        filter_layout.addWidget(QLabel("Additional Filter:"))
        filter_layout.addWidget(self.advanced_filters)
        
        layout.addLayout(filter_layout)
        
        # Add results table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Details", "Status", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Add export button
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)
        
        # Initialize search fields
        self.update_search_fields()
    
    def update_search_fields(self):
        search_type = self.search_type.currentText()
        self.advanced_filters.clear()
        self.advanced_filters.addItem("No Additional Filters")
        
        if search_type == "Restaurants":
            self.advanced_filters.addItems([
                "By Cuisine Type",
                "By Rating",
                "By Location"
            ])
        elif search_type == "Menu Items":
            self.advanced_filters.addItems([
                "By Price Range",
                "By Availability",
                "By Restaurant"
            ])
        elif search_type == "Customers":
            self.advanced_filters.addItems([
                "By Account Status",
                "By Registration Date",
                "By Order History"
            ])
        elif search_type == "Orders":
            self.advanced_filters.addItems([
                "By Status",
                "By Date Range",
                "By Payment Status"
            ])
        elif search_type == "Deliveries":
            self.advanced_filters.addItems([
                "By Delivery Status",
                "By Delivery Person",
                "By Time Range"
            ])
        
        self.perform_search()
    
    def perform_search(self):
        search_term = self.search_field.text().strip()
        search_type = self.search_type.currentText()
        advanced_filter = self.advanced_filters.currentText()
        
        if not search_term and advanced_filter == "No Additional Filters":
            self.table.setRowCount(0)
            return
        
        query = ""
        params = []
        
        if search_type == "Restaurants":
            query = """
            SELECT restaurant_id as id, name, 
                   CONCAT(cuisine_type, ' - ', address) as details,
                   CONCAT('Rating: ', rating) as status,
                   info_update_time as last_updated
            FROM restaurants
            WHERE name LIKE %s OR cuisine_type LIKE %s OR address LIKE %s
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if advanced_filter == "By Cuisine Type":
                query += " ORDER BY cuisine_type"
            elif advanced_filter == "By Rating":
                query += " ORDER BY rating DESC"
            elif advanced_filter == "By Location":
                query += " ORDER BY address"
        
        elif search_type == "Menu Items":
            query = """
            SELECT m.menu_id as id, m.dish_name as name,
                   CONCAT(r.name, ' - ', m.description) as details,
                   m.availability as status,
                   m.info_update_time as last_updated
            FROM menus m
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            WHERE m.dish_name LIKE %s OR m.description LIKE %s
            """
            params = [f"%{search_term}%", f"%{search_term}%"]
            
            if advanced_filter == "By Price Range":
                query += " ORDER BY m.price"
            elif advanced_filter == "By Availability":
                query += " ORDER BY m.availability"
            elif advanced_filter == "By Restaurant":
                query += " ORDER BY r.name"
        
        elif search_type == "Customers":
            query = """
            SELECT customer_id as id, name,
                   CONCAT(address, ' - ', phone) as details,
                   account_status as status,
                   info_update_time as last_updated
            FROM customers
            WHERE name LIKE %s OR address LIKE %s OR phone LIKE %s
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if advanced_filter == "By Account Status":
                query += " ORDER BY account_status"
            elif advanced_filter == "By Registration Date":
                query += " ORDER BY registration_date DESC"
            elif advanced_filter == "By Order History":
                query = """
                SELECT c.customer_id as id, c.name,
                       CONCAT(c.address, ' - ', c.phone) as details,
                       c.account_status as status,
                       c.info_update_time as last_updated
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                WHERE c.name LIKE %s OR c.address LIKE %s OR c.phone LIKE %s
                GROUP BY c.customer_id
                ORDER BY COUNT(o.order_id) DESC
                """
        
        elif search_type == "Orders":
            query = """
            SELECT o.order_id as id, 
                   CONCAT(c.name, ' - ', r.name) as name,
                   CONCAT(m.dish_name, ' - $', o.total_amount) as details,
                   o.delivery_status as status,
                   o.order_date as last_updated
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN menus m ON o.menu_id = m.menu_id
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            WHERE c.name LIKE %s OR r.name LIKE %s OR m.dish_name LIKE %s
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if advanced_filter == "By Status":
                query += " ORDER BY o.delivery_status"
            elif advanced_filter == "By Date Range":
                query += " ORDER BY o.order_date DESC"
            elif advanced_filter == "By Payment Status":
                query += " ORDER BY o.payment_status"
        
        elif search_type == "Deliveries":
            query = """
            SELECT o.order_id as id,
                   CONCAT(c.name, ' - ', r.name) as name,
                   CONCAT(dp.name, ' - ', o.delivery_status) as details,
                   o.delivery_status as status,
                   o.assigned_time as last_updated
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN menus m ON o.menu_id = m.menu_id
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
            WHERE c.name LIKE %s OR r.name LIKE %s OR dp.name LIKE %s
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if advanced_filter == "By Delivery Status":
                query += " ORDER BY o.delivery_status"
            elif advanced_filter == "By Delivery Person":
                query += " ORDER BY dp.name"
            elif advanced_filter == "By Time Range":
                query += " ORDER BY o.assigned_time DESC"
        
        try:
            results = execute_query(query, tuple(params))
            if results is None:
                results = []
            
            self.table.setRowCount(len(results))
            
            for i, result in enumerate(results):
                self.table.setItem(i, 0, QTableWidgetItem(str(result['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(result['name']))
                self.table.setItem(i, 2, QTableWidgetItem(result['details']))
                self.table.setItem(i, 3, QTableWidgetItem(result['status']))
                self.table.setItem(i, 4, QTableWidgetItem(str(result['last_updated'])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
            self.table.setRowCount(0)
    
    def export_results(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No results to export")
            return
        
        try:
            from datetime import datetime
            import csv
            
            filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Write headers
                headers = []
                for i in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(i).text())
                writer.writerow(headers)
                
                # Write data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Results exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")

class DeliveryPersonnelPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Delivery Personnel Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Delivery Person")
        update_btn = QPushButton("Update Delivery Person")
        remove_btn = QPushButton("Remove Delivery Person")
        delete_all_btn = QPushButton("Delete All Delivery Personnel")
        
        add_btn.clicked.connect(self.add_delivery_person)
        update_btn.clicked.connect(self.update_delivery_person)
        remove_btn.clicked.connect(self.remove_delivery_person)
        delete_all_btn.clicked.connect(self.delete_all_delivery_personnel)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(delete_all_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Vehicle Type", "Status", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_delivery_personnel()
    
    def load_delivery_personnel(self):
        delivery_personnel = execute_query("SELECT * FROM delivery_personnel")
        self.table.setRowCount(len(delivery_personnel))
        
        for i, person in enumerate(delivery_personnel):
            self.table.setItem(i, 0, QTableWidgetItem(str(person['delivery_person_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(person['name']))
            self.table.setItem(i, 2, QTableWidgetItem(person['phone']))
            self.table.setItem(i, 3, QTableWidgetItem(person.get('vehicle_type', 'Not specified')))
            self.table.setItem(i, 4, QTableWidgetItem(person['status']))
            self.table.setItem(i, 5, QTableWidgetItem(str(person.get('info_update_time', 'N/A'))))
            
            # Color code based on status
            if person['status'] == "Available":
                for j in range(6):
                    self.table.item(i, j).setBackground(QColor("#e6ffe6"))  # Light green
            elif person['status'] == "On Delivery":
                for j in range(6):
                    self.table.item(i, j).setBackground(QColor("#fff3e6"))  # Light orange
    
    def add_delivery_person(self):
        dialog = DeliveryPersonDialog(self)
        if dialog.exec():
            self.load_delivery_personnel()
    
    def update_delivery_person(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a delivery person to update")
            return
        
        delivery_person_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = DeliveryPersonDialog(self, delivery_person_id)
        if dialog.exec():
            self.load_delivery_personnel()
    
    def remove_delivery_person(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a delivery person to remove")
            return
        
        delivery_person_id = int(self.table.item(selected_items[0].row(), 0).text())
        person_name = self.table.item(selected_items[0].row(), 1).text()
        
        # Check if delivery person has any associated orders
        orders = execute_query(
            "SELECT COUNT(*) as count FROM orders WHERE delivery_person_id = %s",
            (delivery_person_id,)
        )
        
        if orders and orders[0]['count'] > 0:
            reply = QMessageBox.question(
                self, "Warning",
                f"This delivery person has {orders[0]['count']} associated orders. Removing them will also remove these orders. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # First delete associated orders
                result = execute_query(
                    "DELETE FROM orders WHERE delivery_person_id = %s",
                    (delivery_person_id,),
                    fetch=False
                )
                if not result:
                    QMessageBox.critical(self, "Error", "Failed to remove associated orders")
                    return
            else:
                return
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {person_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = execute_query(
                    "DELETE FROM delivery_personnel WHERE delivery_person_id = %s",
                    (delivery_person_id,),
                    fetch=False
                )
                
                if result is not None:  # Changed from if result to if result is not None
                    self.load_delivery_personnel()  # Refresh the table immediately
                    QMessageBox.information(self, "Success", "Delivery person removed successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to remove delivery person")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while removing the delivery person: {str(e)}")
    
    def delete_all_delivery_personnel(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete ALL delivery personnel? This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query("DELETE FROM delivery_personnel", fetch=False)
            if result:
                self.load_delivery_personnel()
                QMessageBox.information(self, "Success", "All delivery personnel deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete delivery personnel")

class DeliveryPersonDialog(QDialog):
    def __init__(self, parent=None, delivery_person_id=None):
        super().__init__(parent)
        self.delivery_person_id = delivery_person_id
        self.setWindowTitle("Add Delivery Person" if not delivery_person_id else "Update Delivery Person")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        # Vehicle type selection with radio buttons
        vehicle_type_group = QGroupBox("Vehicle Type")
        vehicle_type_layout = QVBoxLayout()
        
        # Vehicle category
        vehicle_category_group = QGroupBox("Vehicle Category")
        vehicle_category_layout = QVBoxLayout()
        self.light_vehicle_radio = QRadioButton("Light Vehicle")
        self.heavy_vehicle_radio = QRadioButton("Heavy Vehicle")
        self.light_vehicle_radio.setChecked(True)  # Default selection
        vehicle_category_layout.addWidget(self.light_vehicle_radio)
        vehicle_category_layout.addWidget(self.heavy_vehicle_radio)
        vehicle_category_group.setLayout(vehicle_category_layout)
        
        # Transmission type
        transmission_group = QGroupBox("Transmission")
        transmission_layout = QVBoxLayout()
        self.automatic_radio = QRadioButton("Automatic")
        self.manual_radio = QRadioButton("Manual")
        self.automatic_radio.setChecked(True)  # Default selection
        transmission_layout.addWidget(self.automatic_radio)
        transmission_layout.addWidget(self.manual_radio)
        transmission_group.setLayout(transmission_layout)
        
        vehicle_type_layout.addWidget(vehicle_category_group)
        vehicle_type_layout.addWidget(transmission_group)
        vehicle_type_group.setLayout(vehicle_type_layout)
        
        # Status selector
        self.status_selector = QComboBox()
        self.status_selector.addItems(["Available", "On Delivery"])
        
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(vehicle_type_group)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_selector)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_delivery_person)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load delivery person data if updating
        if delivery_person_id:
            self.load_delivery_person_data()
    
    def load_delivery_person_data(self):
        delivery_person = execute_query(
            "SELECT * FROM delivery_personnel WHERE delivery_person_id = %s",
            (self.delivery_person_id,)
        )
        if delivery_person:
            person = delivery_person[0]
            self.name_input.setText(person['name'])
            self.phone_input.setText(person['phone'])
            
            # Set status
            index = self.status_selector.findText(person['status'])
            if index >= 0:
                self.status_selector.setCurrentIndex(index)
            
            # Set vehicle type
            if 'vehicle_type' in person and person['vehicle_type']:
                vehicle_type = person['vehicle_type']
                if 'Light Vehicle' in vehicle_type:
                    self.light_vehicle_radio.setChecked(True)
                    self.heavy_vehicle_radio.setChecked(False)
                else:
                    self.light_vehicle_radio.setChecked(False)
                    self.heavy_vehicle_radio.setChecked(True)
                
                if 'Automatic' in vehicle_type:
                    self.automatic_radio.setChecked(True)
                    self.manual_radio.setChecked(False)
                else:
                    self.automatic_radio.setChecked(False)
                    self.manual_radio.setChecked(True)
    
    def get_vehicle_type(self):
        category = "Light Vehicle" if self.light_vehicle_radio.isChecked() else "Heavy Vehicle"
        transmission = "Automatic" if self.automatic_radio.isChecked() else "Manual"
        return f"{category} - {transmission}"
    
    def save_delivery_person(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        status = self.status_selector.currentText()
        vehicle_type = self.get_vehicle_type()
        
        if not name or not phone:
            QMessageBox.warning(self, "Warning", "Please fill in all required fields")
            return
        
        try:
            if self.delivery_person_id:  # Update existing delivery person
                query = """
                UPDATE delivery_personnel 
                SET name = %s, phone = %s, status = %s, vehicle_type = %s
                WHERE delivery_person_id = %s
                """
                params = (name, phone, status, vehicle_type, self.delivery_person_id)
            else:  # Add new delivery person
                query = """
                INSERT INTO delivery_personnel (name, phone, status, vehicle_type)
                VALUES (%s, %s, %s, %s)
                """
                params = (name, phone, status, vehicle_type)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:  # Changed from if result to if result is not None
                QMessageBox.information(self, "Success", "Delivery person saved successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save delivery person")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 