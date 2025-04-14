from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                            QSizePolicy, QSpacerItem, QStackedWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                            QLineEdit, QComboBox, QMessageBox, QRadioButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from db_utils import execute_query

class AdminDashboard(QWidget):
    logout_requested = pyqtSignal()
    
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
            customer_layout = QVBoxLayout(customer_group)
            customer_layout.addWidget(QLabel(f"Name: {order['customer_name']}"))
            customer_layout.addWidget(QLabel(f"Phone: {order['customer_phone']}"))
            customer_layout.addWidget(QLabel(f"Delivery Address: {order['delivery_address']}"))
            
            # Restaurant info
            restaurant_group = QGroupBox("Restaurant Information")
            restaurant_layout = QVBoxLayout(restaurant_group)
            restaurant_layout.addWidget(QLabel(f"Name: {order['restaurant_name']}"))
            restaurant_layout.addWidget(QLabel(f"Address: {order['restaurant_address']}"))
            
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
        
        # Placeholder label
        label = QLabel("Reports and Analytics")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 20))
        
        layout.addWidget(label)
        layout.addStretch()
        
        return page
    
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Placeholder label
        label = QLabel("System Settings")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 20))
        
        layout.addWidget(label)
        layout.addStretch()
        
        return page
    
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