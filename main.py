import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                            QLineEdit, QComboBox, QMessageBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFrame, QDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from db_utils import execute_query

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
            "Delivery Tracking",
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
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.restaurant_page = RestaurantPage()
        self.menu_page = MenuPage()
        self.customer_page = CustomerPage()
        self.order_page = OrderPage()
        self.delivery_page = DeliveryPage()
        self.search_page = SearchPage()
        
        self.stacked_widget.addWidget(self.restaurant_page)
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.customer_page)
        self.stacked_widget.addWidget(self.order_page)
        self.stacked_widget.addWidget(self.delivery_page)
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
            "Delivery Tracking": 4,
            "Search": 5
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
        
        add_btn.clicked.connect(self.add_restaurant)
        update_btn.clicked.connect(self.update_restaurant)
        remove_btn.clicked.connect(self.remove_restaurant)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
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
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Menu Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add restaurant selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Restaurant:"))
        self.restaurant_selector = QComboBox()
        self.restaurant_selector.currentIndexChanged.connect(self.load_menu_items)
        selector_layout.addWidget(self.restaurant_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Menu Item")
        update_btn = QPushButton("Update Menu Item")
        remove_btn = QPushButton("Remove Menu Item")
        
        add_btn.clicked.connect(self.add_menu_item)
        update_btn.clicked.connect(self.update_menu_item)
        remove_btn.clicked.connect(self.remove_menu_item)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Restaurant", "Dish Name", "Description", "Price", "Availability", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_restaurants()
    
    def load_restaurants(self):
        restaurants = execute_query("SELECT restaurant_id, name FROM restaurants")
        self.restaurant_selector.clear()
        self.restaurant_selector.addItem("All Restaurants", None)
        
        for restaurant in restaurants:
            self.restaurant_selector.addItem(restaurant['name'], restaurant['restaurant_id'])
    
    def load_menu_items(self):
        restaurant_id = self.restaurant_selector.currentData()
        
        if restaurant_id:
            query = """
            SELECT m.*, r.name as restaurant_name 
            FROM menus m
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            WHERE m.restaurant_id = %s
            """
            params = (restaurant_id,)
        else:
            query = """
            SELECT m.*, r.name as restaurant_name 
            FROM menus m
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            """
            params = None
        
        menu_items = execute_query(query, params)
        self.table.setRowCount(len(menu_items))
        
        for i, item in enumerate(menu_items):
            self.table.setItem(i, 0, QTableWidgetItem(str(item['menu_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(item['restaurant_name']))
            self.table.setItem(i, 2, QTableWidgetItem(item['dish_name']))
            self.table.setItem(i, 3, QTableWidgetItem(item['description'] or ''))
            self.table.setItem(i, 4, QTableWidgetItem(f"${item['price']:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(item['availability']))
            self.table.setItem(i, 6, QTableWidgetItem(str(item['info_update_time'])))
    
    def add_menu_item(self):
        dialog = MenuItemDialog(self)
        if dialog.exec():
            self.load_menu_items()
    
    def update_menu_item(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a menu item to update")
            return
        
        menu_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = MenuItemDialog(self, menu_id)
        if dialog.exec():
            self.load_menu_items()
    
    def remove_menu_item(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a menu item to remove")
            return
        
        menu_id = int(self.table.item(selected_items[0].row(), 0).text())
        dish_name = self.table.item(selected_items[0].row(), 2).text()
        
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
            if result:
                self.load_menu_items()
                QMessageBox.information(self, "Success", "Menu item removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove menu item")

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
        
        add_btn.clicked.connect(self.add_customer)
        update_btn.clicked.connect(self.update_customer)
        remove_btn.clicked.connect(self.remove_customer)
        view_orders_btn.clicked.connect(self.view_order_history)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(view_orders_btn)
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
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Order Management - Coming Soon"))

class DeliveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Delivery Tracking - Coming Soon"))

class SearchPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Search - Coming Soon"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 