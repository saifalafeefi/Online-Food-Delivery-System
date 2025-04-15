from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                            QSizePolicy, QSpacerItem, QStackedWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                            QLineEdit, QComboBox, QMessageBox, QRadioButton, QGroupBox,
                            QDateEdit, QTabWidget, QCheckBox, QProgressDialog, QApplication)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QFont, QIcon, QPainter
# Using matplotlib for charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import time
import re

from db_utils import execute_query

class AdminDashboard(QWidget):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Food Delivery - Administration")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # User info section
        user_info = QFrame()
        user_info.setObjectName("user-info")
        user_info_layout = QVBoxLayout(user_info)
        
        welcome_label = QLabel(f"Welcome, Admin")
        welcome_label.setObjectName("welcome-label")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        user_info_layout.addWidget(welcome_label)
        sidebar_layout.addWidget(user_info)
        
        # Navigation buttons
        nav_buttons = [
            {"text": "Dashboard", "icon": "📊", "slot": self.show_dashboard},
            {"text": "Users", "icon": "👥", "slot": self.manage_users},
            {"text": "Restaurants", "icon": "🏢", "slot": self.manage_restaurants},
            {"text": "Delivery Personnel", "icon": "🚚", "slot": self.manage_delivery},
            {"text": "Orders", "icon": "📦", "slot": self.manage_orders},
            {"text": "Reports", "icon": "📈", "slot": self.view_reports},
            {"text": "Settings", "icon": "⚙️", "slot": self.system_settings}
        ]
        
        for btn_info in nav_buttons:
            btn = QPushButton(f"{btn_info['icon']} {btn_info['text']}")
            btn.setObjectName("nav-button")
            btn.clicked.connect(btn_info["slot"])
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout-button")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        # Content area
        self.content_area = QStackedWidget()
        
        # Create all pages
        self.dashboard_page = self.create_dashboard_page()
        self.restaurants_page = self.create_restaurants_page()
        self.users_page = self.create_users_page()
        self.delivery_page = self.create_delivery_page()
        self.orders_page = self.create_orders_page()
        self.reports_page = self.create_reports_page()
        self.settings_page = self.create_settings_page()
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.restaurants_page)
        self.content_area.addWidget(self.users_page)
        self.content_area.addWidget(self.delivery_page)
        self.content_area.addWidget(self.orders_page)
        self.content_area.addWidget(self.reports_page)
        self.content_area.addWidget(self.settings_page)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        # Apply styles
        self.setStyleSheet("""
            #sidebar {
                background-color: #2c3e50;
                border-radius: 0px;
                padding: 10px;
            }
            #user-info {
                border-bottom: 1px solid #34495e;
                padding-bottom: 15px;
                margin-bottom: 15px;
            }
            #welcome-label {
                color: white;
            }
            #nav-button {
                text-align: left;
                padding: 12px;
                border-radius: 5px;
                background-color: transparent;
                color: white;
                font-size: 14px;
            }
            #nav-button:hover {
                background-color: #34495e;
            }
            #logout-button {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            #logout-button:hover {
                background-color: #c0392b;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QPushButton#action-button {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton#action-button:hover {
                background-color: #2980b9;
            }
            QPushButton#delete-button {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#delete-button:hover {
                background-color: #c0392b;
            }
        """)
        
        # Start with dashboard
        self.show_dashboard()
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Administration Dashboard")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 24))
        
        # Stats overview
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        # Load actual stats from database with fallbacks
        try:
            restaurant_count = execute_query("SELECT COUNT(*) as count FROM restaurants")
            if restaurant_count is None:
                restaurant_count = [{'count': 0}]
        except:
            restaurant_count = [{'count': 0}]
            
        try:
            user_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'customer'")
            if user_count is None:
                user_count = [{'count': 0}]
        except:
            user_count = [{'count': 0}]
            
        try:
            today_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE DATE(order_time) = CURDATE()")
            if today_orders is None:
                today_orders = [{'count': 0}]
        except:
            today_orders = [{'count': 0}]
            
        try:
            total_revenue = execute_query("SELECT SUM(total_amount) as total FROM orders WHERE delivery_status = 'Delivered'")
            if total_revenue is None or total_revenue[0]['total'] is None:
                total_revenue = [{'total': 0}]
        except:
            total_revenue = [{'total': 0}]
        
        # Create stat cards with fallback data
        stat_cards = [
            {"title": "Restaurants", "value": str(restaurant_count[0]['count']), "icon": "🏢"},
            {"title": "Active Users", "value": str(user_count[0]['count']), "icon": "👥"},
            {"title": "Orders Today", "value": str(today_orders[0]['count']), "icon": "📦"},
            {"title": "Total Revenue", "value": f"AED {float(total_revenue[0]['total']):.2f}", "icon": "💰"}
        ]
        
        for card in stat_cards:
            card_widget = QFrame()
            card_widget.setObjectName("stat-card")
            card_layout = QVBoxLayout(card_widget)
            
            title = QLabel(f"{card['icon']} {card['title']}")
            title.setObjectName("stat-title")
            
            value = QLabel(card["value"])
            value.setObjectName("stat-value")
            value.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            
            stats_layout.addWidget(card_widget)
        
        # Recent orders section
        recent_orders_label = QLabel("Recent Orders")
        recent_orders_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.recent_orders_table = QTableWidget()
        self.recent_orders_table.setColumnCount(5)
        self.recent_orders_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Restaurant", "Amount", "Status"])
        self.recent_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Load recent orders with fallback
        try:
            recent_orders = execute_query("""
                SELECT o.order_id, c.name as customer_name, r.name as restaurant_name, 
                       o.total_amount, o.delivery_status 
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                ORDER BY o.order_time DESC
                LIMIT 5
            """)
            
            if recent_orders:
                self.recent_orders_table.setRowCount(len(recent_orders))
                for i, order in enumerate(recent_orders):
                    self.recent_orders_table.setItem(i, 0, QTableWidgetItem(str(order['order_id'])))
                    self.recent_orders_table.setItem(i, 1, QTableWidgetItem(order['customer_name']))
                    self.recent_orders_table.setItem(i, 2, QTableWidgetItem(order['restaurant_name']))
                    self.recent_orders_table.setItem(i, 3, QTableWidgetItem(f"AED {float(order['total_amount']):.2f}"))
                    
                    status_item = QTableWidgetItem(order['delivery_status'])
                    if order['delivery_status'] == 'Delivered':
                        status_item.setForeground(Qt.GlobalColor.darkGreen)
                    elif order['delivery_status'] == 'Cancelled':
                        status_item.setForeground(Qt.GlobalColor.red)
                    self.recent_orders_table.setItem(i, 4, status_item)
            else:
                self.recent_orders_table.setRowCount(0)
                
        except Exception as e:
            print(f"Error loading recent orders: {e}")
            self.recent_orders_table.setRowCount(1)
            info_item = QTableWidgetItem("Database connection error. Please check your database connection.")
            self.recent_orders_table.setSpan(0, 0, 1, 5)
            self.recent_orders_table.setItem(0, 0, info_item)
        
        # Add to layout
        layout.addWidget(header)
        layout.addWidget(stats_frame)
        layout.addSpacing(20)
        layout.addWidget(recent_orders_label)
        layout.addWidget(self.recent_orders_table)
        
        page.setStyleSheet("""
            #stat-card {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                min-height: 120px;
                border: 1px solid #ddd;
            }
            #stat-title {
                color: #7f8c8d;
                font-size: 16px;
            }
            #stat-value {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        return page
    
    def create_restaurants_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header section
        header_layout = QHBoxLayout()
        header = QLabel("Restaurant Management")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Action buttons
        add_btn = QPushButton("Add Restaurant")
        add_btn.setObjectName("action-button")
        add_btn.clicked.connect(self.add_restaurant)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        
        # Table for restaurants
        self.restaurant_table = QTableWidget()
        self.restaurant_table.setColumnCount(6)
        self.restaurant_table.setHorizontalHeaderLabels(["ID", "Name", "Address", "Cuisine Type", "Rating", "Actions"])
        self.restaurant_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.restaurant_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.restaurant_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.restaurant_table.setAlternatingRowColors(True)
        
        # Add to layout
        layout.addLayout(header_layout)
        layout.addWidget(self.restaurant_table)
        
        # Load restaurants data
        self.load_restaurants()
        
        return page
    
    def load_restaurants(self):
        # Clear existing rows
        self.restaurant_table.setRowCount(0)
        
        try:
            restaurants = execute_query("SELECT * FROM restaurants ORDER BY restaurant_id")
            
            if not restaurants:
                self.display_no_data_message(self.restaurant_table, "No restaurants found")
                return
            
            for row, restaurant in enumerate(restaurants):
                self.restaurant_table.insertRow(row)
                self.restaurant_table.setItem(row, 0, QTableWidgetItem(str(restaurant['restaurant_id'])))
                self.restaurant_table.setItem(row, 1, QTableWidgetItem(restaurant['name']))
                self.restaurant_table.setItem(row, 2, QTableWidgetItem(restaurant['address']))
                self.restaurant_table.setItem(row, 3, QTableWidgetItem(restaurant['cuisine_type']))
                self.restaurant_table.setItem(row, 4, QTableWidgetItem(str(restaurant['rating'])))
                
                # Create buttons cell
                buttons_widget = QWidget()
                buttons_layout = QHBoxLayout(buttons_widget)
                buttons_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setObjectName("action-button")
                edit_btn.clicked.connect(lambda checked, r=restaurant: self.edit_restaurant(r))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("delete-button")
                delete_btn.clicked.connect(lambda checked, id=restaurant['restaurant_id']: self.delete_restaurant(id))
                
                buttons_layout.addWidget(edit_btn)
                buttons_layout.addWidget(delete_btn)
                
                self.restaurant_table.setCellWidget(row, 5, buttons_widget)
        except Exception as e:
            print(f"Error loading restaurants: {e}")
            self.display_db_error_message(self.restaurant_table)
    
    def add_restaurant(self):
        dialog = RestaurantDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_restaurants()
    
    def edit_restaurant(self, restaurant):
        dialog = RestaurantDialog(self, restaurant)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_restaurants()
    
    def delete_restaurant(self, restaurant_id):
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this restaurant? This will also delete all menus and orders associated with it.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM restaurants WHERE restaurant_id = %s",
                (restaurant_id,),
                fetch=False
            )
            
            if result is not None:
                QMessageBox.information(self, "Success", "Restaurant deleted successfully")
                self.load_restaurants()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete restaurant")
    
    def create_users_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header section
        header_layout = QHBoxLayout()
        header = QLabel("User Management")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Filter by role
        role_filter = QComboBox()
        role_filter.addItems(["All Users", "Customers", "Restaurants", "Delivery"])
        role_filter.currentIndexChanged.connect(self.filter_users)
        
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filter by role:"))
        header_layout.addWidget(role_filter)
        
        # Table for users
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role", "Created", "Actions"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Load users
        self.load_users()
        
        # Add to layout
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        layout.addWidget(self.users_table)
        
        return page
    
    def load_users(self, role_filter="All Users"):
        # Map filter to database role
        role_map = {
            "All Users": None,
            "Customers": "customer",
            "Restaurants": "restaurant",
            "Delivery": "delivery"
        }
        
        # Clear existing rows
        self.users_table.setRowCount(0)
        
        try:
            # Build query based on filter
            if role_map[role_filter]:
                query = "SELECT * FROM users WHERE role = %s ORDER BY created_at DESC"
                users = execute_query(query, (role_map[role_filter],))
            else:
                query = "SELECT * FROM users ORDER BY created_at DESC"
                users = execute_query(query)
            
            if not users:
                self.display_no_data_message(self.users_table, "No users found")
                return
            
            # Populate table
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                # User details
                user_id = QTableWidgetItem(str(user['user_id']))
                username = QTableWidgetItem(user['username'])
                email = QTableWidgetItem(user.get('email', 'N/A'))
                role = QTableWidgetItem(user['role'].capitalize())
                created = QTableWidgetItem(user['created_at'].strftime("%Y-%m-%d") if user.get('created_at') else 'N/A')
                
                self.users_table.setItem(i, 0, user_id)
                self.users_table.setItem(i, 1, username)
                self.users_table.setItem(i, 2, email)
                self.users_table.setItem(i, 3, role)
                self.users_table.setItem(i, 4, created)
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("View")
                view_btn.setObjectName("action-button")
                view_btn.clicked.connect(lambda _, uid=user['user_id']: self.view_user(uid))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("delete-button")
                delete_btn.clicked.connect(lambda _, uid=user['user_id']: self.delete_user(uid))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(delete_btn)
                
                self.users_table.setCellWidget(i, 5, actions_widget)
        except Exception as e:
            print(f"Error loading users: {e}")
            self.display_db_error_message(self.users_table)
    
    def filter_users(self, index):
        filter_text = self.sender().itemText(index)
        self.load_users(filter_text)
    
    def view_user(self, user_id):
        # Get user details
        user = execute_query("SELECT * FROM users WHERE user_id = %s", (user_id,))
        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            return
        
        user = user[0]
        role = user['role']
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"User Details - {user['username']}")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Basic user info
        basic_info = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_info)
        basic_layout.addRow("Username:", QLabel(user['username']))
        basic_layout.addRow("Email:", QLabel(user['email']))
        basic_layout.addRow("Role:", QLabel(role.capitalize()))
        
        # Role-specific info
        role_info = QGroupBox(f"{role.capitalize()} Information")
        role_layout = QFormLayout(role_info)
        
        if role == "customer":
            customer = execute_query("SELECT * FROM customers WHERE user_id = %s", (user_id,))
            if customer:
                customer = customer[0]
                role_layout.addRow("Name:", QLabel(customer['name']))
                role_layout.addRow("Address:", QLabel(customer['address']))
                role_layout.addRow("Phone:", QLabel(customer['phone']))
                
                # Get order count
                orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE customer_id = %s", (customer['customer_id'],))
                if orders:
                    role_layout.addRow("Total Orders:", QLabel(str(orders[0]['count'])))
        
        elif role == "restaurant":
            restaurant = execute_query("SELECT * FROM restaurants WHERE user_id = %s", (user_id,))
            if restaurant:
                restaurant = restaurant[0]
                role_layout.addRow("Restaurant Name:", QLabel(restaurant['name']))
                role_layout.addRow("Cuisine:", QLabel(restaurant['cuisine_type']))
                role_layout.addRow("Address:", QLabel(restaurant['address']))
                
                # Get menu item count
                menu_items = execute_query("SELECT COUNT(*) as count FROM menus WHERE restaurant_id = %s", (restaurant['restaurant_id'],))
                if menu_items:
                    role_layout.addRow("Menu Items:", QLabel(str(menu_items[0]['count'])))
        
        elif role == "delivery":
            delivery = execute_query("SELECT * FROM delivery_personnel WHERE user_id = %s", (user_id,))
            if delivery:
                delivery = delivery[0]
                role_layout.addRow("Name:", QLabel(delivery['name']))
                role_layout.addRow("Phone:", QLabel(delivery['phone']))
                role_layout.addRow("Status:", QLabel(delivery['status']))
                role_layout.addRow("Vehicle:", QLabel(delivery.get('vehicle_type', 'Not specified')))
                
                # Get delivery count
                deliveries = execute_query("SELECT COUNT(*) as count FROM orders WHERE delivery_person_id = %s AND delivery_status = 'Delivered'", (delivery['delivery_person_id'],))
                if deliveries:
                    role_layout.addRow("Completed Deliveries:", QLabel(str(deliveries[0]['count'])))
        
        # Add widgets to layout
        layout.addWidget(basic_info)
        layout.addWidget(role_info)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def delete_user(self, user_id):
        # Check if trying to delete admin
        user = execute_query("SELECT username, role FROM users WHERE user_id = %s", (user_id,))
        if not user:
            return
            
        # Prevent deletion of admin account
        if user[0]['username'] == 'admin' or user[0]['role'] == 'admin':
            QMessageBox.warning(self, "Cannot Delete", "The admin account cannot be deleted.")
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(self, "Confirm Deletion", 
                                      f"Are you sure you want to delete user '{user[0]['username']}'? This action cannot be undone.",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            role = user[0]['role']
            success = True
            
            try:
                # For restaurant users, cascade delete all associated data
                if role == 'restaurant':
                    # Get restaurant ID
                    restaurant = execute_query("SELECT restaurant_id FROM restaurants WHERE user_id = %s", (user_id,))
                    if restaurant:
                        restaurant_id = restaurant[0]['restaurant_id']
                        
                        # Delete menu items
                        execute_query("DELETE FROM menu_items WHERE restaurant_id = %s", (restaurant_id,), fetch=False)
                        
                        # Delete orders for this restaurant
                        # Note: In a production system, you might want to keep order history
                        execute_query("DELETE FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE restaurant_id = %s)", 
                                    (restaurant_id,), fetch=False)
                        execute_query("DELETE FROM orders WHERE restaurant_id = %s", (restaurant_id,), fetch=False)
                        
                        # Delete restaurant
                        execute_query("DELETE FROM restaurants WHERE restaurant_id = %s", (restaurant_id,), fetch=False)
                
                # For customer users, cascade delete all associated data
                elif role == 'customer':
                    # Get customer ID
                    customer = execute_query("SELECT customer_id FROM customers WHERE user_id = %s", (user_id,))
                    if customer:
                        customer_id = customer[0]['customer_id']
                        
                        # Delete orders
                        execute_query("DELETE FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE customer_id = %s)", 
                                    (customer_id,), fetch=False)
                        execute_query("DELETE FROM orders WHERE customer_id = %s", (customer_id,), fetch=False)
                        
                        # Delete customer
                        execute_query("DELETE FROM customers WHERE customer_id = %s", (customer_id,), fetch=False)
                
                # For delivery personnel, cascade delete
                elif role == 'delivery':
                    # Get delivery person ID
                    delivery_person = execute_query("SELECT delivery_person_id FROM delivery_personnel WHERE user_id = %s", (user_id,))
                    if delivery_person:
                        # For delivery users, update orders to remove delivery person reference
                        # Don't delete orders, just unassign delivery person
                        execute_query("UPDATE orders SET delivery_person_id = NULL WHERE delivery_person_id = %s", 
                                    (delivery_person[0]['delivery_person_id'],), fetch=False)
                        
                        # Delete delivery person
                        execute_query("DELETE FROM delivery_personnel WHERE delivery_person_id = %s", 
                                    (delivery_person[0]['delivery_person_id'],), fetch=False)
                
                # Finally delete the user
                result = execute_query("DELETE FROM users WHERE user_id = %s", (user_id,), fetch=False)
                if result is None:
                    success = False
                    
                if success:
                    QMessageBox.information(self, "Success", f"User '{user[0]['username']}' and all associated data have been deleted successfully")
                    self.load_users()  # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete user. There may be associated data that couldn't be deleted.")
                    
            except Exception as e:
                print(f"Error deleting user: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while deleting the user: {str(e)}")
                success = False
    
    def create_delivery_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header section
        header_layout = QHBoxLayout()
        header = QLabel("Delivery Personnel Management")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Status filter
        status_filter = QComboBox()
        status_filter.addItems(["All Status", "Available", "On Delivery", "Unavailable"])
        status_filter.currentIndexChanged.connect(self.filter_delivery_personnel)
        
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filter by status:"))
        header_layout.addWidget(status_filter)
        
        # Table for delivery personnel
        self.delivery_table = QTableWidget()
        self.delivery_table.setColumnCount(10)
        self.delivery_table.setHorizontalHeaderLabels([
            "ID", "Name", "Username", "Email", "Phone", 
            "Status", "Vehicle", "Deliveries", "Rating", "Actions"
        ])
        
        # Set resize modes for columns
        header = self.delivery_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Username
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Vehicle
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Deliveries
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Rating
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        self.delivery_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.delivery_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.delivery_table.setAlternatingRowColors(True)
        
        # Make rows resizable
        self.delivery_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.delivery_table.verticalHeader().setDefaultSectionSize(40)
        
        # Load delivery personnel
        self.load_delivery_personnel()
        
        # Add to layout
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        layout.addWidget(self.delivery_table)
        
        return page
    
    def load_delivery_personnel(self, status_filter="All Status"):
        # Clear existing rows
        self.delivery_table.setRowCount(0)
        
        try:
            # Build query based on filter
            if status_filter != "All Status":
                query = """
                    SELECT dp.*, u.username, u.email, 
                           COUNT(o.order_id) as delivery_count,
                           AVG(r.delivery_rating) as avg_rating
                    FROM delivery_personnel dp
                    JOIN users u ON dp.user_id = u.user_id
                    LEFT JOIN orders o ON dp.delivery_person_id = o.delivery_person_id AND o.delivery_status = 'Delivered'
                    LEFT JOIN ratings r ON r.delivery_person_id = dp.delivery_person_id
                    WHERE dp.status = %s
                    GROUP BY dp.delivery_person_id
                    ORDER BY dp.name
                """
                personnel = execute_query(query, (status_filter,))
            else:
                query = """
                    SELECT dp.*, u.username, u.email,
                           COUNT(o.order_id) as delivery_count,
                           AVG(r.delivery_rating) as avg_rating
                    FROM delivery_personnel dp
                    JOIN users u ON dp.user_id = u.user_id
                    LEFT JOIN orders o ON dp.delivery_person_id = o.delivery_person_id AND o.delivery_status = 'Delivered'
                    LEFT JOIN ratings r ON r.delivery_person_id = dp.delivery_person_id
                    GROUP BY dp.delivery_person_id
                    ORDER BY dp.name
                """
                personnel = execute_query(query)
            
            if not personnel:
                message = "No delivery personnel found" if status_filter == "All Status" else f"No delivery personnel with status: {status_filter}"
                self.display_no_data_message(self.delivery_table, message)
                return
            
            # Populate table
            self.delivery_table.setRowCount(len(personnel))
            for i, person in enumerate(personnel):
                # Person details
                person_id = QTableWidgetItem(str(person['delivery_person_id']))
                name = QTableWidgetItem(person['name'])
                username = QTableWidgetItem(person['username'])
                email = QTableWidgetItem(person['email'])
                phone = QTableWidgetItem(person['phone'])
                
                status_item = QTableWidgetItem(person['status'])
                if person['status'] == 'Available':
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif person['status'] == 'On Delivery':
                    status_item.setForeground(Qt.GlobalColor.blue)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                
                vehicle = QTableWidgetItem(person.get('vehicle_type', 'Not specified'))
                deliveries = QTableWidgetItem(str(person['delivery_count']))
                
                # Rating
                rating = person.get('avg_rating', 0)
                rating_item = QTableWidgetItem(f"{rating:.1f}" if rating else "No ratings")
                
                self.delivery_table.setItem(i, 0, person_id)
                self.delivery_table.setItem(i, 1, name)
                self.delivery_table.setItem(i, 2, username)
                self.delivery_table.setItem(i, 3, email)
                self.delivery_table.setItem(i, 4, phone)
                self.delivery_table.setItem(i, 5, status_item)
                self.delivery_table.setItem(i, 6, vehicle)
                self.delivery_table.setItem(i, 7, deliveries)
                self.delivery_table.setItem(i, 8, rating_item)
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(5)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setObjectName("action-button")
                edit_btn.setMinimumWidth(edit_btn.sizeHint().width() + 10)
                edit_btn.clicked.connect(lambda _, p=person: self.edit_delivery_person(p))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("delete-button")
                delete_btn.setMinimumWidth(delete_btn.sizeHint().width() + 10)
                delete_btn.clicked.connect(lambda _, pid=person['delivery_person_id']: self.delete_delivery_person(pid))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                
                self.delivery_table.setCellWidget(i, 9, actions_widget)
        except Exception as e:
            print(f"Error loading delivery personnel: {e}")
            self.display_db_error_message(self.delivery_table)
    
    def filter_delivery_personnel(self, index):
        filter_text = self.sender().itemText(index)
        self.load_delivery_personnel(filter_text)
    
    def edit_delivery_person(self, person):
        dialog = DeliveryPersonDialog(self, person)
        if dialog.exec():
            self.load_delivery_personnel()
    
    def delete_delivery_person(self, delivery_person_id):
        # Confirm deletion
        confirm = QMessageBox.question(self, "Confirm Deletion", 
                                      "Are you sure you want to delete this delivery person? This will only remove them from the delivery personnel list, not delete their user account.",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Check for active deliveries
            active = execute_query("SELECT COUNT(*) as count FROM orders WHERE delivery_person_id = %s AND delivery_status = 'Out for Delivery'", (delivery_person_id,))
            if active and active[0]['count'] > 0:
                QMessageBox.warning(self, "Cannot Delete", f"This delivery person has {active[0]['count']} active deliveries. They cannot be deleted until all deliveries are completed.")
                return
            
            # Delete the delivery person
            result = execute_query("DELETE FROM delivery_personnel WHERE delivery_person_id = %s", (delivery_person_id,), fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", "Delivery person has been removed successfully")
                self.load_delivery_personnel()  # Refresh the table
            else:
                QMessageBox.warning(self, "Error", "Failed to remove delivery person")
                
    def create_orders_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header and filter section
        header_layout = QHBoxLayout()
        header = QLabel("Order Management")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Status filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by status:")
        self.order_status_filter = QComboBox()
        self.order_status_filter.addItems(["All Orders", "Pending", "Confirmed", "Preparing", 
                                            "Ready for Pickup", "Out for Delivery", "Delivered", "Cancelled"])
        self.order_status_filter.currentIndexChanged.connect(self.load_orders)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(lambda: self.load_orders(force_refresh=True))
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.order_status_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_btn)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Customer", "Restaurant", "Amount", "Status", 
            "Delivery Person", "Date/Time", "Actions"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.orders_table.setAlternatingRowColors(True)
        
        # Add components to layout
        layout.addLayout(header_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.orders_table)
        
        # Load orders
        self.load_orders()
        
        return page
        
    def load_orders(self, force_refresh=False):
        """Load orders based on selected filter"""
        status_filter = self.order_status_filter.currentText() if hasattr(self, 'order_status_filter') else "All Orders"
        
        # Clear existing rows
        self.orders_table.setRowCount(0)
        
        try:
            # Build query based on filter
            if status_filter != "All Orders":
                query = """
                    SELECT o.*, c.name as customer_name, r.name as restaurant_name,
                           dp.name as delivery_person_name
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.customer_id
                    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                    LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
                    WHERE o.delivery_status = %s
                    ORDER BY o.order_time DESC
                """
                orders = execute_query(query, (status_filter,))
            else:
                query = """
                    SELECT o.*, c.name as customer_name, r.name as restaurant_name,
                           dp.name as delivery_person_name
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.customer_id
                    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                    LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
                    ORDER BY o.order_time DESC
                """
                orders = execute_query(query)
            
            if not orders:
                message = f"No orders with status: {status_filter}" if status_filter != "All Orders" else "No orders found"
                self.display_no_data_message(self.orders_table, message)
                return
            
            # Populate table
            self.orders_table.setRowCount(len(orders))
            
            for i, order in enumerate(orders):
                # Order ID
                self.orders_table.setItem(i, 0, QTableWidgetItem(str(order['order_id'])))
                
                # Customer
                self.orders_table.setItem(i, 1, QTableWidgetItem(order['customer_name']))
                
                # Restaurant
                self.orders_table.setItem(i, 2, QTableWidgetItem(order['restaurant_name']))
                
                # Amount
                amount_item = QTableWidgetItem(f"AED {float(order['total_amount']):.2f}")
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.orders_table.setItem(i, 3, amount_item)
                
                # Status with color coding
                status_item = QTableWidgetItem(order['delivery_status'])
                if order['delivery_status'] == 'Delivered':
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif order['delivery_status'] == 'Cancelled':
                    status_item.setForeground(Qt.GlobalColor.red)
                elif order['delivery_status'] in ['Preparing', 'Ready for Pickup', 'Out for Delivery']:
                    status_item.setForeground(Qt.GlobalColor.darkBlue)
                self.orders_table.setItem(i, 4, status_item)
                
                # Delivery Person
                delivery_name = order['delivery_person_name'] if order['delivery_person_name'] else "Not Assigned"
                self.orders_table.setItem(i, 5, QTableWidgetItem(delivery_name))
                
                # Order Date/Time
                date_time = order['order_time'].strftime("%Y-%m-%d %H:%M")
                self.orders_table.setItem(i, 6, QTableWidgetItem(date_time))
                
                # Actions buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("View")
                view_btn.setObjectName("action-button")
                view_btn.clicked.connect(lambda _, id=order['order_id']: self.view_order_details(id))
                
                action_layout.addWidget(view_btn)
                self.orders_table.setCellWidget(i, 7, action_widget)
                
        except Exception as e:
            print(f"Error loading orders: {e}")
            self.display_db_error_message(self.orders_table, f"Error loading orders: {str(e)}")
    
    def view_order_details(self, order_id):
        """Show a dialog with detailed order information"""
        try:
            # Get order details
            order = execute_query("""
                SELECT o.*, c.name as customer_name, c.phone as customer_phone, c.address as customer_address,
                       r.name as restaurant_name, r.address as restaurant_address, 
                       dp.name as delivery_person_name, dp.phone as delivery_person_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
                WHERE o.order_id = %s
            """, (order_id,))
            
            if not order:
                QMessageBox.warning(self, "Error", f"Order #{order_id} not found")
                return
            
            order = order[0]
            
            # Get order items
            items = execute_query("""
                SELECT oi.*, m.dish_name
                FROM order_items oi
                JOIN menus m ON oi.menu_id = m.menu_id
                WHERE oi.order_id = %s
            """, (order_id,))
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Order #{order_id} Details")
            dialog.setMinimumWidth(600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2c3e50;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-size: 12px;
                }
                QGroupBox {
                    color: white;
                    border: 1px solid #7f8c8d;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }
                QTableWidget {
                    background-color: #34495e;
                    color: white;
                    gridline-color: #7f8c8d;
                    alternate-background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: white;
                    padding: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Order header
            header_label = QLabel(f"Order #{order_id}")
            header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            
            # Status with color
            status_layout = QHBoxLayout()
            status_label = QLabel("Status:")
            status_value = QLabel(order['delivery_status'])
            
            status_color = "white"
            if order['delivery_status'] == 'Delivered':
                status_color = "#2ecc71"
            elif order['delivery_status'] == 'Cancelled':
                status_color = "#e74c3c"
            elif order['delivery_status'] in ['Preparing', 'Ready for Pickup', 'Out for Delivery']:
                status_color = "#3498db"
                
            status_value.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            status_layout.addWidget(status_label)
            status_layout.addWidget(status_value)
            status_layout.addStretch()
            
            date_label = QLabel(f"Order Date: {order['order_time'].strftime('%Y-%m-%d %H:%M')}")
            
            # Customer and Restaurant sections in 2 columns
            info_layout = QHBoxLayout()
            
            # Customer info
            customer_group = QGroupBox("Customer Information")
            customer_layout = QFormLayout(customer_group)
            customer_layout.addRow("Name:", QLabel(order['customer_name']))
            customer_layout.addRow("Phone:", QLabel(order['customer_phone']))
            customer_layout.addRow("Delivery Address:", QLabel(order['customer_address']))
            
            # Restaurant info
            restaurant_group = QGroupBox("Restaurant Information")
            restaurant_layout = QFormLayout(restaurant_group)
            restaurant_layout.addRow("Name:", QLabel(order['restaurant_name']))
            restaurant_layout.addRow("Address:", QLabel(order['restaurant_address']))
            
            info_layout.addWidget(customer_group)
            info_layout.addWidget(restaurant_group)
            
            # Delivery Person info if assigned
            delivery_group = None
            if order['delivery_person_name']:
                delivery_group = QGroupBox("Delivery Person")
                delivery_layout = QVBoxLayout(delivery_group)
                delivery_layout.addWidget(QLabel(f"Name: {order['delivery_person_name']}"))
                if order['delivery_person_phone']:
                    delivery_layout.addWidget(QLabel(f"Phone: {order['delivery_person_phone']}"))
            
            # Order items table
            items_label = QLabel("Order Items")
            items_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity", "Total"])
            items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            items_table.setAlternatingRowColors(True)
            items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            
            if items:
                items_table.setRowCount(len(items))
                
                for i, item in enumerate(items):
                    name_item = QTableWidgetItem(item['dish_name'])
                    price_item = QTableWidgetItem(f"AED {float(item['unit_price']):.2f}")
                    quantity_item = QTableWidgetItem(str(item['quantity']))
                    total_item = QTableWidgetItem(f"AED {float(item['total_price']):.2f}")
                    
                    # Set text color to white for all items
                    for item in [name_item, price_item, quantity_item, total_item]:
                        item.setForeground(Qt.GlobalColor.white)
                    
                    items_table.setItem(i, 0, name_item)
                    items_table.setItem(i, 1, price_item)
                    items_table.setItem(i, 2, quantity_item)
                    items_table.setItem(i, 3, total_item)
            else:
                items_table.setRowCount(1)
                no_items = QTableWidgetItem("No items found for this order")
                no_items.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                no_items.setForeground(Qt.GlobalColor.white)
                items_table.setSpan(0, 0, 1, 4)
                items_table.setItem(0, 0, no_items)
            
            # Order totals
            totals_layout = QHBoxLayout()
            
            subtotal_label = QLabel(f"Subtotal: AED {float(order['subtotal']):.2f}")
            delivery_fee_label = QLabel(f"Delivery Fee: AED {float(order['delivery_fee'] or 0):.2f}")
            tax_label = QLabel(f"Tax: AED {float(order['tax'] or 0):.2f}")
            
            total_label = QLabel(f"Total: AED {float(order['total_amount']):.2f}")
            total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            
            totals_layout.addWidget(subtotal_label)
            totals_layout.addWidget(delivery_fee_label)
            totals_layout.addWidget(tax_label)
            totals_layout.addStretch()
            totals_layout.addWidget(total_label)
            
            # Payment info
            payment_layout = QHBoxLayout()
            payment_method = QLabel(f"Payment Method: {order['payment_method']}")
            payment_status = QLabel(f"Payment Status: {order['payment_status']}")
            
            payment_layout.addWidget(payment_method)
            payment_layout.addStretch()
            payment_layout.addWidget(payment_status)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            
            # Add all to main layout
            layout.addWidget(header_label)
            layout.addLayout(status_layout)
            layout.addWidget(date_label)
            layout.addLayout(info_layout)
            if delivery_group:
                layout.addWidget(delivery_group)
            layout.addWidget(items_label)
            layout.addWidget(items_table)
            layout.addLayout(totals_layout)
            layout.addLayout(payment_layout)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load order details: {str(e)}")
            print(f"Error loading order details: {e}")
    
    def create_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Create a scroll area for the entire content - VERTICAL ONLY
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create a widget to hold all the content that will be scrollable
        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(15)
        
        # Header section
        header = QLabel("Reports & Analytics")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #ecf0f1; background-color: #2c3e50; padding: 10px; border-radius: 4px;")
        
        # Date range selector
        date_range_layout = QHBoxLayout()
        date_range_label = QLabel("Date Range:")
        date_range_label.setStyleSheet("color: #2c3e50;")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        
        # Style the date edit controls
        date_style = """
            QDateEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 5px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: 1px solid #3498db;
            }
            QCalendarWidget QWidget {
                background-color: #34495e;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #2c3e50;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 5px;
            }
            QCalendarWidget QMenu {
                color: white;
                background-color: #2c3e50;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #7f8c8d;
            }
        """
        self.start_date.setStyleSheet(date_style)
        self.end_date.setStyleSheet(date_style)
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.refresh_analytics)
        
        date_range_layout.addWidget(date_range_label)
        date_range_layout.addWidget(self.start_date)
        date_range_layout.addWidget(QLabel("to"))
        date_range_layout.addWidget(self.end_date)
        date_range_layout.addStretch()
        date_range_layout.addWidget(refresh_btn)
        
        # Key metrics cards
        metrics_layout = QHBoxLayout()
        
        # Total Orders Card
        total_orders_card = QFrame()
        total_orders_card.setObjectName("metric-card")
        total_orders_layout = QVBoxLayout(total_orders_card)
        self.total_orders_label = QLabel("0")
        self.total_orders_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        total_orders_layout.addWidget(QLabel("Total Orders"))
        total_orders_layout.addWidget(self.total_orders_label)
        
        # Total Revenue Card
        revenue_card = QFrame()
        revenue_card.setObjectName("metric-card")
        revenue_layout = QVBoxLayout(revenue_card)
        self.revenue_label = QLabel("AED 0.00")
        self.revenue_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        revenue_layout.addWidget(QLabel("Total Revenue"))
        revenue_layout.addWidget(self.revenue_label)
        
        # Average Order Value Card
        aov_card = QFrame()
        aov_card.setObjectName("metric-card")
        aov_layout = QVBoxLayout(aov_card)
        self.aov_label = QLabel("AED 0.00")
        self.aov_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        aov_layout.addWidget(QLabel("Average Order Value"))
        aov_layout.addWidget(self.aov_label)
        
        # Delivery Time Card
        delivery_time_card = QFrame()
        delivery_time_card.setObjectName("metric-card")
        delivery_time_layout = QVBoxLayout(delivery_time_card)
        self.delivery_time_label = QLabel("0 min")
        self.delivery_time_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        delivery_time_layout.addWidget(QLabel("Avg. Delivery Time"))
        delivery_time_layout.addWidget(self.delivery_time_label)
        
        metrics_layout.addWidget(total_orders_card)
        metrics_layout.addWidget(revenue_card)
        metrics_layout.addWidget(aov_card)
        metrics_layout.addWidget(delivery_time_card)
        
        # Charts section - ORIGINAL SIZES
        charts_layout = QHBoxLayout()
        
        # Orders by Status Chart
        status_chart_card = QFrame()
        status_chart_card.setObjectName("chart-card")
        status_chart_layout = QVBoxLayout(status_chart_card)
        status_chart_layout.addWidget(QLabel("Orders by Status"))
        
        # Create a frame for the chart with its own layout
        self.status_chart = QFrame()
        self.status_chart.setMinimumHeight(300)  # Original size
        chart_layout = QVBoxLayout(self.status_chart)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        status_chart_layout.addWidget(self.status_chart)
        
        # Revenue Trend Chart
        revenue_chart_card = QFrame()
        revenue_chart_card.setObjectName("chart-card")
        revenue_chart_layout = QVBoxLayout(revenue_chart_card)
        revenue_chart_layout.addWidget(QLabel("Revenue Trend"))
        
        # Create a frame for the chart with its own layout
        self.revenue_chart = QFrame()
        self.revenue_chart.setMinimumHeight(300)  # Original size
        chart_layout = QVBoxLayout(self.revenue_chart)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        revenue_chart_layout.addWidget(self.revenue_chart)
        
        charts_layout.addWidget(status_chart_card)
        charts_layout.addWidget(revenue_chart_card)
        
        # Detailed Reports Section - MORE SPACE
        reports_tabs = QTabWidget()
        reports_tabs.setMinimumHeight(300)  # More space for tables
        
        # Top Restaurants Tab
        restaurants_tab = QWidget()
        restaurants_layout = QVBoxLayout(restaurants_tab)
        self.top_restaurants_table = QTableWidget()
        self.top_restaurants_table.setColumnCount(5)
        self.top_restaurants_table.setHorizontalHeaderLabels(["Restaurant", "Orders", "Revenue", "Rating", "Completion Rate"])
        self.top_restaurants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        restaurants_layout.addWidget(self.top_restaurants_table)
        
        # Top Delivery Personnel Tab
        delivery_tab = QWidget()
        delivery_layout = QVBoxLayout(delivery_tab)
        self.top_delivery_table = QTableWidget()
        self.top_delivery_table.setColumnCount(5)
        self.top_delivery_table.setHorizontalHeaderLabels(["Name", "Deliveries", "Rating", "Avg. Time", "On-time Rate"])
        self.top_delivery_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        delivery_layout.addWidget(self.top_delivery_table)
        
        # Customer Insights Tab
        customer_tab = QWidget()
        customer_layout = QVBoxLayout(customer_tab)
        self.customer_insights_table = QTableWidget()
        self.customer_insights_table.setColumnCount(5)
        self.customer_insights_table.setHorizontalHeaderLabels(["Customer", "Orders", "Total Spent", "Avg. Order Value", "Last Order"])
        self.customer_insights_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        customer_layout.addWidget(self.customer_insights_table)
        
        reports_tabs.addTab(restaurants_tab, "Top Restaurants")
        reports_tabs.addTab(delivery_tab, "Delivery Performance")
        reports_tabs.addTab(customer_tab, "Customer Insights")
        
        # Add all sections to scroll layout
        scroll_layout.addWidget(header)
        scroll_layout.addLayout(date_range_layout)
        scroll_layout.addLayout(metrics_layout)
        scroll_layout.addLayout(charts_layout)
        scroll_layout.addWidget(reports_tabs)
        
        # Set scroll area widget and add to main layout
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Set styles
        page.setStyleSheet("""
            QFrame#metric-card {
                background-color: #34495e;
                border-radius: 8px;
                padding: 15px;
                min-width: 200px;
            }
            QFrame#chart-card {
                background-color: #34495e;
                border-radius: 8px;
                padding: 15px;
                min-width: 400px;
            }
            QLabel {
                color: white;
            }
            QTableWidget {
                background-color: #34495e;
                color: white;
                gridline-color: #7f8c8d;
                alternate-background-color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #7f8c8d;
                background-color: #34495e;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 8px 15px;
                border: 1px solid #7f8c8d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #34495e;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2c3e50;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Load initial data
        self.refresh_analytics()
        
        return page
    
    def refresh_analytics(self):
        """Refresh all analytics data based on selected date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        try:
            # Get key metrics
            metrics_query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    AVG(TIMESTAMPDIFF(MINUTE, order_time, actual_delivery_time)) as avg_delivery_time
                FROM orders 
                WHERE order_time BETWEEN %s AND %s
            """
            metrics = execute_query(metrics_query, (start_date, end_date))
            
            if metrics and metrics[0]:
                self.total_orders_label.setText(str(metrics[0]['total_orders']))
                self.revenue_label.setText(f"AED {float(metrics[0]['total_revenue'] or 0):.2f}")
                self.aov_label.setText(f"AED {float(metrics[0]['avg_order_value'] or 0):.2f}")
                self.delivery_time_label.setText(f"{int(metrics[0]['avg_delivery_time'] or 0)} min")
            
            # Get orders by status
            status_query = """
                SELECT delivery_status, COUNT(*) as count
                FROM orders
                WHERE order_time BETWEEN %s AND %s
                GROUP BY delivery_status
            """
            status_data = execute_query(status_query, (start_date, end_date))
            
            # Get revenue trend
            revenue_query = """
                SELECT DATE(order_time) as date, SUM(total_amount) as revenue
                FROM orders
                WHERE order_time BETWEEN %s AND %s
                GROUP BY DATE(order_time)
                ORDER BY date
            """
            revenue_data = execute_query(revenue_query, (start_date, end_date))
            
            # Clear previous charts
            for i in reversed(range(self.status_chart.layout().count())): 
                widget = self.status_chart.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            for i in reversed(range(self.revenue_chart.layout().count())): 
                widget = self.revenue_chart.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Create status pie chart with matplotlib
            if status_data:
                status_fig = Figure(figsize=(5, 4), dpi=100)
                status_canvas = FigureCanvas(status_fig)
                ax = status_fig.add_subplot(111)
                
                labels = [item['delivery_status'] for item in status_data]
                sizes = [item['count'] for item in status_data]
                
                # Use a colorful palette
                colors = plt.cm.Paired(np.arange(len(labels))/len(labels))
                
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                      startangle=90, colors=colors)
                ax.axis('equal')  # Equal aspect ratio ensures circular pie
                
                # Clear previous chart if any
                for i in reversed(range(self.status_chart.layout().count())): 
                    widget = self.status_chart.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Add the canvas to the layout
                self.status_chart.layout().addWidget(status_canvas)
                status_fig.tight_layout()
                status_canvas.draw()
            
            # Create revenue trend chart with matplotlib
            if revenue_data:
                revenue_fig = Figure(figsize=(5, 4), dpi=100)
                revenue_canvas = FigureCanvas(revenue_fig)
                ax = revenue_fig.add_subplot(111)
                
                dates = [item['date'] for item in revenue_data]
                revenue_values = [float(item['revenue']) for item in revenue_data]
                
                ax.plot(dates, revenue_values, 'o-', color='#3498db', linewidth=2)
                ax.set_title('Revenue Trend')
                ax.set_ylabel('Revenue (AED)')
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Rotate date labels for better readability
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
                # Clear previous chart if any
                for i in reversed(range(self.revenue_chart.layout().count())): 
                    widget = self.revenue_chart.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Add the canvas to the layout
                self.revenue_chart.layout().addWidget(revenue_canvas)
                revenue_fig.tight_layout()
                revenue_canvas.draw()
            
            # Get top restaurants
            restaurants_query = """
                SELECT 
                    r.name,
                    COUNT(o.order_id) as order_count,
                    SUM(o.total_amount) as revenue,
                    r.rating,
                    AVG(CASE WHEN o.delivery_status = 'Delivered' THEN 1 ELSE 0 END) * 100 as completion_rate
                FROM restaurants r
                JOIN orders o ON r.restaurant_id = o.restaurant_id
                WHERE o.order_time BETWEEN %s AND %s
                GROUP BY r.restaurant_id
                ORDER BY revenue DESC
                LIMIT 10
            """
            restaurants_data = execute_query(restaurants_query, (start_date, end_date))
            
            if restaurants_data:
                self.top_restaurants_table.setRowCount(len(restaurants_data))
                for i, restaurant in enumerate(restaurants_data):
                    self.top_restaurants_table.setItem(i, 0, QTableWidgetItem(restaurant['name']))
                    self.top_restaurants_table.setItem(i, 1, QTableWidgetItem(str(restaurant['order_count'])))
                    self.top_restaurants_table.setItem(i, 2, QTableWidgetItem(f"AED {float(restaurant['revenue']):.2f}"))
                    self.top_restaurants_table.setItem(i, 3, QTableWidgetItem(f"{float(restaurant['rating']):.1f}"))
                    self.top_restaurants_table.setItem(i, 4, QTableWidgetItem(f"{float(restaurant['completion_rate']):.1f}%"))
            
            # Get top delivery personnel
            delivery_query = """
                SELECT 
                    dp.name,
                    COUNT(o.order_id) as delivery_count,
                    AVG(r.delivery_rating) as rating,
                    AVG(TIMESTAMPDIFF(MINUTE, o.order_time, o.actual_delivery_time)) as avg_time,
                    AVG(CASE WHEN o.actual_delivery_time <= o.estimated_delivery_time THEN 1 ELSE 0 END) * 100 as on_time_rate
                FROM delivery_personnel dp
                JOIN orders o ON dp.delivery_person_id = o.delivery_person_id
                LEFT JOIN ratings r ON o.order_id = r.order_id
                WHERE o.order_time BETWEEN %s AND %s
                GROUP BY dp.delivery_person_id
                ORDER BY delivery_count DESC
                LIMIT 10
            """
            delivery_data = execute_query(delivery_query, (start_date, end_date))
            
            if delivery_data:
                self.top_delivery_table.setRowCount(len(delivery_data))
                for i, delivery in enumerate(delivery_data):
                    self.top_delivery_table.setItem(i, 0, QTableWidgetItem(delivery['name']))
                    self.top_delivery_table.setItem(i, 1, QTableWidgetItem(str(delivery['delivery_count'])))
                    self.top_delivery_table.setItem(i, 2, QTableWidgetItem(f"{float(delivery['rating'] or 0):.1f}"))
                    self.top_delivery_table.setItem(i, 3, QTableWidgetItem(f"{int(delivery['avg_time'] or 0)} min"))
                    self.top_delivery_table.setItem(i, 4, QTableWidgetItem(f"{float(delivery['on_time_rate'] or 0):.1f}%"))
            
            # Get customer insights
            customer_query = """
                SELECT 
                    c.name,
                    COUNT(o.order_id) as order_count,
                    SUM(o.total_amount) as total_spent,
                    AVG(o.total_amount) as avg_order_value,
                    MAX(o.order_time) as last_order
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                WHERE o.order_time BETWEEN %s AND %s
                GROUP BY c.customer_id
                ORDER BY total_spent DESC
                LIMIT 10
            """
            customer_data = execute_query(customer_query, (start_date, end_date))
            
            if customer_data:
                self.customer_insights_table.setRowCount(len(customer_data))
                for i, customer in enumerate(customer_data):
                    self.customer_insights_table.setItem(i, 0, QTableWidgetItem(customer['name']))
                    self.customer_insights_table.setItem(i, 1, QTableWidgetItem(str(customer['order_count'])))
                    self.customer_insights_table.setItem(i, 2, QTableWidgetItem(f"AED {float(customer['total_spent']):.2f}"))
                    self.customer_insights_table.setItem(i, 3, QTableWidgetItem(f"AED {float(customer['avg_order_value']):.2f}"))
                    self.customer_insights_table.setItem(i, 4, QTableWidgetItem(customer['last_order'].strftime("%Y-%m-%d %H:%M")))
                    
        except Exception as e:
            print(f"Error refreshing analytics: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load analytics data: {str(e)}")
    
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("System Settings")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #ecf0f1; background-color: #2c3e50; padding: 10px; border-radius: 4px; margin-bottom: 15px;")
        
        # Create a tab widget for different setting categories
        tabs = QTabWidget()
        
        # 1. General Settings Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # App settings group
        app_group = QGroupBox("Application Settings")
        app_group.setStyleSheet("QGroupBox { color: white; border: 1px solid #3498db; border-radius: 5px; margin-top: 15px; padding-top: 10px; }")
        app_layout = QFormLayout(app_group)
        
        # App Name
        self.app_name_input = QLineEdit("Food Delivery System")
        app_layout.addRow("Application Name:", self.app_name_input)
        
        # Remove Language selector and keep only necessary settings
        
        # Currency selector
        self.currency_selector = QComboBox()
        self.currency_selector.addItems(["AED", "USD", "EUR", "GBP", "CNY"])
        self.currency_selector.setCurrentText("AED")
        app_layout.addRow("Default Currency:", self.currency_selector)
        
        # Timezone selector
        self.timezone_selector = QComboBox()
        self.timezone_selector.addItems(["UTC", "UTC+4 (UAE)", "UTC+3 (KSA)", "UTC+1 (CET)", "UTC-5 (EST)"])
        self.timezone_selector.setCurrentText("UTC+4 (UAE)")
        app_layout.addRow("Default Timezone:", self.timezone_selector)
        
        # 2. Business Rules Group
        business_group = QGroupBox("Business Rules")
        business_group.setStyleSheet("QGroupBox { color: white; border: 1px solid #3498db; border-radius: 5px; margin-top: 15px; padding-top: 10px; }")
        business_layout = QFormLayout(business_group)
        
        # Default delivery fee
        self.delivery_fee_input = QLineEdit("10.00")
        business_layout.addRow("Default Delivery Fee (AED):", self.delivery_fee_input)
        
        # Default tax rate
        self.tax_rate_input = QLineEdit("5.0")
        business_layout.addRow("Default Tax Rate (%):", self.tax_rate_input)
        
        # Minimum order amount
        self.min_order_input = QLineEdit("25.00")
        business_layout.addRow("Minimum Order Amount (AED):", self.min_order_input)
        
        # Service fee
        self.service_fee_input = QLineEdit("2.0")
        business_layout.addRow("Service Fee (%):", self.service_fee_input)
        
        # Add groups to general tab layout
        general_layout.addWidget(app_group)
        general_layout.addWidget(business_group)
        general_layout.addStretch()
        
        # 2. Order Settings Tab
        order_tab = QWidget()
        order_layout = QVBoxLayout(order_tab)
        
        # Order behavior group
        order_group = QGroupBox("Order Processing")
        order_group.setStyleSheet("QGroupBox { color: white; border: 1px solid #3498db; border-radius: 5px; margin-top: 15px; padding-top: 10px; }")
        order_form = QFormLayout(order_group)
        
        # Auto-assign delivery
        self.auto_assign_checkbox = QCheckBox()
        self.auto_assign_checkbox.setChecked(True)
        order_form.addRow("Auto-assign Delivery Personnel:", self.auto_assign_checkbox)
        
        # Order prep time
        self.prep_time_input = QLineEdit("30")
        order_form.addRow("Default Preparation Time (min):", self.prep_time_input)
        
        # Delivery radius
        self.delivery_radius_input = QLineEdit("10")
        order_form.addRow("Maximum Delivery Radius (km):", self.delivery_radius_input)
        
        # Cancel order threshold
        self.cancel_threshold_input = QLineEdit("15")
        order_form.addRow("Order Cancellation Window (min):", self.cancel_threshold_input)
        
        # Add groups to order tab
        order_layout.addWidget(order_group)
        order_layout.addStretch()
        
        # 3. Database Backup Tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        # Database backup group
        backup_group = QGroupBox("Database Backup")
        backup_group.setStyleSheet("QGroupBox { color: white; border: 1px solid #3498db; border-radius: 5px; margin-top: 15px; padding-top: 10px; }")
        backup_inner_layout = QVBoxLayout(backup_group)
        
        backup_form = QFormLayout()
        self.backup_path_input = QLineEdit("backups/")
        
        # Add browse button for backup path
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.backup_path_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_backup_path)
        browse_btn.setMaximumWidth(80)
        path_layout.addWidget(browse_btn)
        
        backup_form.addRow("Backup Directory:", path_layout)
        
        self.auto_backup_checkbox = QCheckBox()
        self.auto_backup_checkbox.setChecked(True)
        backup_form.addRow("Enable Automatic Backups:", self.auto_backup_checkbox)
        
        self.backup_freq_combo = QComboBox()
        self.backup_freq_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_freq_combo.setCurrentText("Daily")
        backup_form.addRow("Backup Frequency:", self.backup_freq_combo)
        
        backup_inner_layout.addLayout(backup_form)
        
        # Backup buttons
        backup_buttons = QHBoxLayout()
        backup_now_btn = QPushButton("Backup Now")
        backup_now_btn.clicked.connect(self.backup_database)
        restore_btn = QPushButton("Restore from Backup")
        restore_btn.clicked.connect(self.restore_database)
        
        backup_buttons.addWidget(backup_now_btn)
        backup_buttons.addWidget(restore_btn)
        backup_inner_layout.addLayout(backup_buttons)
        
        # Add utility section
        utils_group = QGroupBox("Database Utilities")
        utils_group.setStyleSheet("QGroupBox { color: white; border: 1px solid #3498db; border-radius: 5px; margin-top: 15px; padding-top: 10px; }")
        utils_layout = QVBoxLayout(utils_group)
        
        utils_buttons = QHBoxLayout()
        optimize_btn = QPushButton("Optimize Database")
        optimize_btn.clicked.connect(self.optimize_database)
        clear_cache_btn = QPushButton("Clear System Cache")
        clear_cache_btn.clicked.connect(self.clear_system_cache)
        
        utils_buttons.addWidget(optimize_btn)
        utils_buttons.addWidget(clear_cache_btn)
        utils_layout.addLayout(utils_buttons)
        
        # Add groups to backup tab
        backup_layout.addWidget(backup_group)
        backup_layout.addWidget(utils_group)
        backup_layout.addStretch()
        
        # Add all tabs to tab widget
        tabs.addTab(general_tab, "General")
        tabs.addTab(order_tab, "Orders")
        tabs.addTab(backup_tab, "Backup & Maintenance")
        
        # Add buttons at the bottom
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        
        # Add all components to main layout
        layout.addWidget(header)
        layout.addWidget(tabs)
        layout.addLayout(button_layout)
        
        # Style the page
        page.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3498db;
                background-color: #34495e;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QLineEdit, QComboBox {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                min-width: 120px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        return page
        
    def browse_backup_path(self):
        """Open a file dialog to select backup directory"""
        from PySide6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Backup Directory",
            self.backup_path_input.text()
        )
        if directory:
            self.backup_path_input.setText(directory)
    
    def optimize_database(self):
        """Optimize database tables"""
        from db_utils import execute_query
        try:
            # Show progress dialog
            progress_msg = QMessageBox(self)
            progress_msg.setIcon(QMessageBox.Icon.Information)
            progress_msg.setWindowTitle("Database Optimization")
            progress_msg.setText("Optimizing database tables. Please wait...")
            progress_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress_msg.show()
            
            # Get list of tables
            tables = execute_query("SHOW TABLES")
            if not tables:
                progress_msg.close()
                QMessageBox.critical(self, "Optimization Failed", "Could not retrieve database tables.")
                return
            
            # Optimize each table
            for table_dict in tables:
                table_name = list(table_dict.values())[0]  # Get table name from dictionary
                execute_query(f"OPTIMIZE TABLE {table_name}", fetch=False)
            
            progress_msg.close()
            QMessageBox.information(self, "Optimization Complete", "Database tables have been optimized successfully.")
        
        except Exception as e:
            if 'progress_msg' in locals():
                progress_msg.close()
            QMessageBox.critical(self, "Optimization Failed", f"Failed to optimize database: {str(e)}")
    
    def clear_system_cache(self):
        """Clear application cache - simulated function"""
        import shutil
        import tempfile
        import os
        
        reply = QMessageBox.question(
            self, "Clear Cache", 
            "This will clear all temporary files and cached data.\nDo you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Create a progress message
            progress_msg = QMessageBox(self)
            progress_msg.setIcon(QMessageBox.Icon.Information)
            progress_msg.setWindowTitle("Clearing Cache")
            progress_msg.setText("Clearing system cache. Please wait...")
            progress_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress_msg.show()
            
            # Clear actual system temp files (optional - be careful with this)
            temp_dir = os.path.join(tempfile.gettempdir(), "food_delivery_cache")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                os.makedirs(temp_dir, exist_ok=True)
            
            progress_msg.close()
            QMessageBox.information(self, "Cache Cleared", "System cache has been cleared successfully.")
        
        except Exception as e:
            if 'progress_msg' in locals():
                progress_msg.close()
            QMessageBox.critical(self, "Operation Failed", f"Failed to clear cache: {str(e)}")
            
    def save_settings(self):
        """Save settings to config file or database"""
        import json
        import os
        
        settings = {
            "app_name": self.app_name_input.text(),
            "currency": self.currency_selector.currentText(),
            "timezone": self.timezone_selector.currentText(),
            "delivery_fee": self.delivery_fee_input.text(),
            "tax_rate": self.tax_rate_input.text(),
            "min_order": self.min_order_input.text(),
            "service_fee": self.service_fee_input.text(),
            "auto_assign": self.auto_assign_checkbox.isChecked(),
            "prep_time": self.prep_time_input.text(),
            "delivery_radius": self.delivery_radius_input.text(),
            "cancel_threshold": self.cancel_threshold_input.text(),
            "backup_path": self.backup_path_input.text(),
            "auto_backup": self.auto_backup_checkbox.isChecked(),
            "backup_frequency": self.backup_freq_combo.currentText()
        }
        
        try:
            # Create settings directory if it doesn't exist
            os.makedirs("settings", exist_ok=True)
            
            # Save settings to JSON file
            with open("settings/app_settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all fields to defaults
            self.app_name_input.setText("Food Delivery System")
            self.currency_selector.setCurrentText("AED")
            self.timezone_selector.setCurrentText("UTC+4 (UAE)")
            
            self.delivery_fee_input.setText("10.00")
            self.tax_rate_input.setText("5.0")
            self.min_order_input.setText("25.00")
            self.service_fee_input.setText("2.0")
            
            self.auto_assign_checkbox.setChecked(True)
            self.prep_time_input.setText("30")
            self.delivery_radius_input.setText("10")
            self.cancel_threshold_input.setText("15")
            
            self.backup_path_input.setText("backups/")
            self.auto_backup_checkbox.setChecked(True)
            self.backup_freq_combo.setCurrentText("Daily")
            
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to default values.")
    
    def backup_database(self):
        """Perform database backup using direct SQL connection with proper UI updates"""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import Qt
        import datetime
        import os
        from pathlib import Path
        import time
        
        # Start timing the operation
        start_time = time.time()
        
        # Log beginning of backup
        print("\n==== DATABASE BACKUP STARTED ====")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create backups directory if it doesn't exist
        backup_dir = Path(self.backup_path_input.text().strip())
        try:
            os.makedirs(backup_dir, exist_ok=True)
            print(f"Backup directory created/verified: {backup_dir}")
        except Exception as e:
            error_msg = f"Could not create backup directory: {str(e)}"
            print(f"ERROR: {error_msg}")
            QMessageBox.critical(self, "Backup Failed", error_msg)
            return
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"food_delivery_backup_{timestamp}.sql"
        print(f"Backup will be saved to: {backup_file}")
        
        # Get database connection details from environment
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_user = os.environ.get('DB_USER', 'root')
        db_password = os.environ.get('DB_PASSWORD', '')
        db_name = os.environ.get('DB_NAME', 'food_delivery')
        print(f"Database connection details: host={db_host}, user={db_user}, database={db_name}")
        
        # Use direct SQL queries for backup (no mysqldump required)
        from db_utils import get_db_connection
        
        # First, get table count to set up progress dialog
        try:
            print("Attempting to connect to database...")
            connection = get_db_connection()
            if not connection:
                error_msg = "Could not connect to database for backup."
                print(f"ERROR: {error_msg}")
                QMessageBox.critical(self, "Backup Failed", error_msg)
                return
            
            print("Successfully connected to database")
            cursor = connection.cursor(dictionary=True)
            
            print("Getting list of tables...")
            cursor.execute("SHOW TABLES")
            tables = [list(table.values())[0] for table in cursor.fetchall()]
            table_count = len(tables)
            print(f"Found {table_count} tables to backup: {', '.join(tables)}")
            
            # Create progress dialog
            progress = QProgressDialog("Preparing to backup database...", "Cancel", 0, table_count, self)
            progress.setWindowTitle("Database Backup")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)  # Show immediately
            progress.setValue(0)
            
            print("Starting backup process...")
            # Open backup file
            with open(backup_file, 'w') as f:
                # Write header
                f.write(f"-- Food Delivery System Database Backup\n")
                f.write(f"-- Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Database: {db_name}\n\n")
                print("Wrote backup file header")
                
                # Process each table
                for i, table in enumerate(tables):
                    # Update progress dialog
                    progress.setValue(i)
                    progress.setLabelText(f"Backing up table: {table} ({i+1}/{table_count})")
                    
                    # Check if user canceled
                    if progress.wasCanceled():
                        print("Backup cancelled by user")
                        cursor.close()
                        connection.close()
                        # Remove incomplete file
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                            print(f"Removed incomplete backup file: {backup_file}")
                        return
                    
                    # Allow UI to update
                    QApplication.processEvents()
                    
                    # Get table structure
                    try:
                        print(f"Backing up table structure for '{table}'...")
                        cursor.execute(f"SHOW CREATE TABLE `{table}`")
                        create_table_sql = cursor.fetchone()['Create Table']
                        
                        # Write create table statement
                        f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                        f.write(f"{create_table_sql};\n\n")
                        
                        # Get table data
                        print(f"Fetching data for table '{table}'...")
                        cursor.execute(f"SELECT * FROM `{table}`")
                        rows = cursor.fetchall()
                        print(f"Found {len(rows)} rows in table '{table}'")
                        
                        # If table has data, write INSERT statements
                        if rows:
                            columns = list(rows[0].keys())
                            print(f"Table '{table}' columns: {', '.join(columns)}")
                            
                            # Process in batches to avoid memory issues
                            batch_size = 100
                            total_rows = len(rows)
                            total_batches = (total_rows + batch_size - 1) // batch_size  # Ceiling division
                            
                            print(f"Processing {total_rows} rows in {total_batches} batches (size {batch_size})...")
                            for batch_start in range(0, total_rows, batch_size):
                                batch_num = batch_start // batch_size + 1
                                
                                # Update progress text for large tables
                                if total_rows > 1000:
                                    progress.setLabelText(f"Backing up table: {table} - Rows {batch_start}/{total_rows}")
                                    QApplication.processEvents()
                                
                                # Check for cancellation on each batch
                                if progress.wasCanceled():
                                    print("Backup cancelled by user during data processing")
                                    cursor.close()
                                    connection.close()
                                    if os.path.exists(backup_file):
                                        os.remove(backup_file)
                                        print(f"Removed incomplete backup file: {backup_file}")
                                    return
                                
                                # Process batch
                                batch = rows[batch_start:batch_start + batch_size]
                                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)")
                                
                                # Generate VALUES part
                                values_list = []
                                for row in batch:
                                    row_values = []
                                    for column in columns:
                                        if row[column] is None:
                                            row_values.append("NULL")
                                        elif isinstance(row[column], (int, float)):
                                            row_values.append(str(row[column]))
                                        elif isinstance(row[column], bytes):
                                            # Handle binary data
                                            hex_str = row[column].hex()
                                            row_values.append(f"0x{hex_str}")
                                        else:
                                            # Escape string values
                                            val = str(row[column]).replace("'", "''")
                                            row_values.append(f"'{val}'")
                                    values_list.append(f"({', '.join(row_values)})")
                                
                                # Write insert statement with multiple rows
                                f.write(f"INSERT INTO `{table}` (`{'`, `'.join(columns)}`) VALUES\n")
                                f.write(",\n".join(values_list))
                                f.write(";\n\n")
                                print(f"Wrote {len(batch)} rows in batch {batch_num}")
                        else:
                            print(f"Table '{table}' is empty - no data to backup")
                    
                    except Exception as table_error:
                        print(f"ERROR processing table '{table}': {str(table_error)}")
                        progress.close()
                        cursor.close()
                        connection.close()
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                            print(f"Removed incomplete backup file: {backup_file}")
                        QMessageBox.critical(self, "Backup Failed", f"Error while backing up table '{table}': {str(table_error)}")
                        return
                
                # Completed successfully
                progress.setValue(table_count)
                print("Backup completed successfully")
            
            # Close database connection
            cursor.close()
            connection.close()
            print("Database connection closed")
            
            # Check file size
            backup_size = os.path.getsize(backup_file)
            print(f"Backup file size: {backup_size/1024/1024:.2f} MB")
            
            # Success message
            end_time = time.time()
            duration = end_time - start_time
            print(f"Backup took {duration:.2f} seconds")
            print("==== DATABASE BACKUP COMPLETED ====\n")
            
            QMessageBox.information(
                self, 
                "Backup Complete", 
                f"Database backup completed successfully.\nBackup stored at: {backup_file}\nFile size: {backup_size/1024/1024:.2f} MB\nTime: {duration:.2f} seconds"
            )
            
        except Exception as e:
            # Handle any uncaught exceptions
            print(f"CRITICAL ERROR during backup: {str(e)}")
            if 'progress' in locals():
                progress.close()
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()
                print("Database connection closed after error")
            
            # Remove failed backup
            if os.path.exists(backup_file):
                try:
                    os.remove(backup_file)
                    print(f"Removed incomplete backup file: {backup_file}")
                except Exception as rm_err:
                    print(f"Warning: Could not remove incomplete backup file: {str(rm_err)}")
            
            print("==== DATABASE BACKUP FAILED ====\n")
            QMessageBox.critical(self, "Backup Failed", f"Failed to perform database backup: {str(e)}")
    
    def restore_database(self):
        """Restore database from a backup file using direct SQL connection"""
        from PySide6.QtWidgets import QFileDialog, QProgressDialog
        from PySide6.QtCore import Qt, QProcess
        import os
        import re
        import time
        import datetime
        import sys
        
        # Start timing the operation
        start_time = time.time()
        
        # Log beginning of restore
        print("\n==== DATABASE RESTORE STARTED ====")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        reply = QMessageBox.warning(
            self, "Restore Database", 
            "WARNING: Restoring from backup will overwrite the current database. This action cannot be undone.\n\nDo you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            print("Restore cancelled by user at confirmation dialog")
            return
        
        # Let user select the backup file
        backup_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            str(self.backup_path_input.text()),
            "SQL Files (*.sql)"
        )
        
        if not backup_file:
            print("Restore cancelled - no file selected")
            return  # User canceled
        
        print(f"Selected backup file: {backup_file}")
        
        # Check file size
        try:
            file_size = os.path.getsize(backup_file)
            print(f"Backup file size: {file_size/1024/1024:.2f} MB")
        except Exception as e:
            print(f"Warning: Could not determine file size: {str(e)}")
        
        # Use direct SQL connection instead of mysql client
        from db_utils import get_db_connection
        
        # Read SQL file first to count statements
        try:
            print("Reading backup file...")
            with open(backup_file, 'r') as f:
                sql_file = f.read()
                
            # Split file content into individual statements
            print("Splitting SQL file into statements...")
            statements = re.split(r';\s*\n', sql_file)
            total_statements = len([s for s in statements if s.strip()])
            print(f"Found {total_statements} SQL statements to execute")
            
            # Create progress dialog
            progress = QProgressDialog("Preparing to restore database...", "Cancel", 0, total_statements, self)
            progress.setWindowTitle("Database Restore")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)  # Show immediately
            progress.setValue(0)
            
            print("Attempting to connect to database...")
            connection = get_db_connection()
            if not connection:
                print("ERROR: Could not connect to database for restore")
                QMessageBox.critical(self, "Restore Failed", "Could not connect to database for restore.")
                return
            
            print("Successfully connected to database")
            cursor = connection.cursor()
            
            # Turn off foreign key checks temporarily
            print("Disabling foreign key checks...")
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            
            executed = 0
            skipped = 0
            
            # Execute each statement
            for i, statement in enumerate(statements):
                if statement.strip():  # Skip empty statements
                    progress.setValue(executed)
                    progress.setLabelText(f"Restoring database: {executed}/{total_statements}")
                    
                    # Check for user cancellation
                    if progress.wasCanceled():
                        print("Restore cancelled by user during execution")
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")  # Re-enable foreign key checks
                        cursor.close()
                        connection.close()
                        print("Database connection closed after cancellation")
                        return
                    
                    # Allow UI to update
                    QApplication.processEvents()
                    
                    # Execute the statement
                    try:
                        print(f"Executing statement {executed+1}/{total_statements} ({len(statement)} characters)...")
                        if len(statement) > 100:
                            print(f"Statement preview: {statement[:97]}...")
                        else:
                            print(f"Statement: {statement}")
                            
                        cursor.execute(statement)
                        connection.commit()
                        executed += 1
                        print(f"Statement {executed}/{total_statements} executed successfully")
                    except Exception as stmt_error:
                        print(f"ERROR executing statement: {str(stmt_error)}")
                        if len(statement) > 100:
                            print(f"Failed statement preview: {statement[:97]}...")
                        else:
                            print(f"Failed statement: {statement}")
                        skipped += 1
                        # Continue with next statement
            
            # Turn foreign key checks back on
            print("Re-enabling foreign key checks...")
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            
            cursor.close()
            connection.close()
            print("Database connection closed")
            
            progress.setValue(total_statements)
            
            # Success message
            end_time = time.time()
            duration = end_time - start_time
            print(f"Restore completed in {duration:.2f} seconds")
            print(f"Statements: {executed} executed, {skipped} skipped")
            print("==== DATABASE RESTORE COMPLETED ====\n")
            
            # Prepare restart message
            success_msg = (
                f"Database restore completed successfully.\n\n"
                f"Statements: {executed} executed, {skipped} skipped\n"
                f"Time: {duration:.2f} seconds\n\n"
                "The application will now restart to apply the changes."
            )
            
            # Show completion message
            restart_msg = QMessageBox(self)
            restart_msg.setIcon(QMessageBox.Icon.Information)
            restart_msg.setWindowTitle("Restore Complete")
            restart_msg.setText(success_msg)
            restart_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            restart_msg.buttonClicked.connect(self.restart_application)
            restart_msg.exec()
            
        except Exception as e:
            print(f"CRITICAL ERROR during restore: {str(e)}")
            if 'progress' in locals():
                progress.close()
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()
                print("Database connection closed after error")
            
            print("==== DATABASE RESTORE FAILED ====\n")
            QMessageBox.critical(self, "Restore Failed", f"Failed to restore database: {str(e)}")
            
    def restart_application(self):
        """Show a message instructing the user to manually restart the application"""
        print("Application requires manual restart after database restore.")
        
        # Create a detailed message for the user
        restart_message = QMessageBox(self)
        restart_message.setIcon(QMessageBox.Icon.Information)
        restart_message.setWindowTitle("Manual Restart Required")
        restart_message.setText(
            "Database has been restored successfully!\n\n"
            "Please close the application completely and restart it manually "
            "for the changes to take effect.\n\n"
            "Click OK to close the application."
        )
        restart_message.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # When user clicks OK, just close the application
        result = restart_message.exec()
        if result == QMessageBox.StandardButton.Ok:
            print("User acknowledged. Closing application...")
            # Signal logout to cleanup resources
            self.logout_requested.emit()
            # Close the main window
            QApplication.quit()
            print("Application closed.")
    
    def show_dashboard(self):
        self.content_area.setCurrentWidget(self.dashboard_page)
    
    def manage_users(self):
        self.content_area.setCurrentWidget(self.users_page)
    
    def manage_restaurants(self):
        self.content_area.setCurrentWidget(self.restaurants_page)
        self.load_restaurants()  # Refresh data
    
    def manage_delivery(self):
        self.content_area.setCurrentWidget(self.delivery_page)
    
    def manage_orders(self):
        self.content_area.setCurrentWidget(self.orders_page)
    
    def view_reports(self):
        self.content_area.setCurrentWidget(self.reports_page)
    
    def system_settings(self):
        self.content_area.setCurrentWidget(self.settings_page)
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()

    # Helper methods for displaying messages in tables
    def display_db_error_message(self, table, message="Database connection error. Please check your database connection."):
        """Display an error message in a table when database operations fail"""
        table.setRowCount(1)
        table.setColumnCount(1)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        error_item = QTableWidgetItem(message)
        error_item.setForeground(Qt.GlobalColor.red)
        error_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        error_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Make non-editable
        
        table.setItem(0, 0, error_item)
    
    def display_no_data_message(self, table, message):
        """Display a message in a table when no data is found"""
        # Save original column count and headers
        column_count = table.columnCount()
        headers = [table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else "" for i in range(column_count)]
        
        # Temporarily use a single column for the message
        table.setRowCount(1)
        table.setColumnCount(1)
        
        info_item = QTableWidgetItem(message)
        info_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        info_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Make non-editable
        
        table.setItem(0, 0, info_item)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Restore original column count and headers
        table.setColumnCount(column_count)
        table.horizontalHeader().setVisible(True)
        for i in range(column_count):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(headers[i]))


class RestaurantDialog(QDialog):
    def __init__(self, parent=None, restaurant=None):
        super().__init__(parent)
        self.restaurant = restaurant
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Name field
        self.name_input = QLineEdit()
        if self.restaurant:
            self.name_input.setText(self.restaurant['name'])
        
        # Address field
        self.address_input = QLineEdit()
        if self.restaurant:
            self.address_input.setText(self.restaurant['address'])
        
        # Contact number field
        self.contact_input = QLineEdit()
        if self.restaurant:
            self.contact_input.setText(self.restaurant['contact_number'])
        
        # Cuisine type field
        self.cuisine_input = QComboBox()
        cuisines = ["Italian", "Chinese", "Indian", "Japanese", "Mexican", "American", "Thai", "French", "Mediterranean", "Other"]
        self.cuisine_input.addItems(cuisines)
        if self.restaurant:
            index = self.cuisine_input.findText(self.restaurant['cuisine_type'])
            if index >= 0:
                self.cuisine_input.setCurrentIndex(index)
        
        # Add fields to form
        form_layout.addRow("Restaurant Name:", self.name_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Contact Number:", self.contact_input)
        form_layout.addRow("Cuisine Type:", self.cuisine_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_restaurant)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
    
    def save_restaurant(self):
        # Validate input
        name = self.name_input.text().strip()
        address = self.address_input.text().strip()
        contact = self.contact_input.text().strip()
        cuisine = self.cuisine_input.currentText()
        
        if not name or not address or not contact:
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields")
            return
        
        try:
            if self.restaurant:  # Update existing
                query = """
                UPDATE restaurants 
                SET name = %s, address = %s, contact_number = %s, cuisine_type = %s
                WHERE restaurant_id = %s
                """
                params = (name, address, contact, cuisine, self.restaurant['restaurant_id'])
            else:  # Add new
                query = """
                INSERT INTO restaurants (name, address, contact_number, cuisine_type, rating)
                VALUES (%s, %s, %s, %s, 0.0)
                """
                params = (name, address, contact, cuisine)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", 
                                      "Restaurant updated successfully" if self.restaurant else "Restaurant added successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save restaurant")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}") 


class DeliveryPersonDialog(QDialog):
    def __init__(self, parent=None, delivery_person=None):
        super().__init__(parent)
        self.delivery_person = delivery_person
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QFrame {
                background-color: #34495e;
                border-radius: 4px;
                padding: 5px;
            }
            QRadioButton {
                color: white;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
                border-radius: 7px;
                border: 2px solid #7f8c8d;
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #3498db;
            }
        """)
        self.initUI()
        
    def initUI(self):
        if self.delivery_person:
            self.setWindowTitle(f"Edit Delivery Person - {self.delivery_person['name']}")
        else:
            self.setWindowTitle("Add Delivery Person")
        
        layout = QFormLayout(self)
        
        # Form fields
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        self.status_combobox = QComboBox()
        self.status_combobox.addItems(["Available", "On Delivery", "Unavailable"])
        
        # Vehicle type options
        vehicle_layout = QVBoxLayout()
        
        self.vehicle_size_group = QFrame()
        vehicle_size_layout = QHBoxLayout(self.vehicle_size_group)
        self.light_vehicle_radio = QRadioButton("Light Vehicle")
        self.heavy_vehicle_radio = QRadioButton("Heavy Vehicle")
        self.light_vehicle_radio.setChecked(True)  # Default
        vehicle_size_layout.addWidget(self.light_vehicle_radio)
        vehicle_size_layout.addWidget(self.heavy_vehicle_radio)
        
        self.transmission_group = QFrame()
        transmission_layout = QHBoxLayout(self.transmission_group)
        self.auto_radio = QRadioButton("Automatic")
        self.manual_radio = QRadioButton("Manual")
        self.auto_radio.setChecked(True)  # Default
        transmission_layout.addWidget(self.auto_radio)
        transmission_layout.addWidget(self.manual_radio)
        
        vehicle_layout.addWidget(QLabel("Vehicle Type:"))
        vehicle_layout.addWidget(self.vehicle_size_group)
        vehicle_layout.addWidget(QLabel("Transmission:"))
        vehicle_layout.addWidget(self.transmission_group)
        
        # Add fields to form
        layout.addRow("Name:", self.name_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Status:", self.status_combobox)
        layout.addRow(vehicle_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_delivery_person)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
        
        # Fill with existing data if editing
        if self.delivery_person:
            self.name_input.setText(self.delivery_person['name'])
            self.phone_input.setText(self.delivery_person['phone'])
            
            # Set status
            index = self.status_combobox.findText(self.delivery_person['status'])
            if index >= 0:
                self.status_combobox.setCurrentIndex(index)
            
            # Set vehicle type
            vehicle_type = self.delivery_person.get('vehicle_type', 'Light Vehicle - Automatic')
            
            if "Light Vehicle" in vehicle_type:
                self.light_vehicle_radio.setChecked(True)
            elif "Heavy Vehicle" in vehicle_type:
                self.heavy_vehicle_radio.setChecked(True)
                
            if "Automatic" in vehicle_type:
                self.auto_radio.setChecked(True)
            elif "Manual" in vehicle_type:
                self.manual_radio.setChecked(True)
    
    def save_delivery_person(self):
        # Validate input
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        status = self.status_combobox.currentText()
        
        if not name or not phone:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return
        
        # Get vehicle type
        vehicle_size = "Light Vehicle" if self.light_vehicle_radio.isChecked() else "Heavy Vehicle"
        transmission = "Automatic" if self.auto_radio.isChecked() else "Manual"
        vehicle_type = f"{vehicle_size} - {transmission}"
        
        try:
            if self.delivery_person:
                # Update existing delivery person
                query = """
                UPDATE delivery_personnel 
                SET name = %s, phone = %s, status = %s, vehicle_type = %s
                WHERE delivery_person_id = %s
                """
                params = (name, phone, status, vehicle_type, self.delivery_person['delivery_person_id'])
            else:
                # We need a user_id to create a new delivery person, so this will prompt to select a user
                QMessageBox.warning(self, "Not Implemented", "Adding new delivery personnel is only possible during user registration.")
                return
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", "Delivery person saved successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save delivery person")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}") 