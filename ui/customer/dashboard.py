from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                            QSizePolicy, QSpacerItem, QStackedWidget, QMessageBox,
                            QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                            QLineEdit, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
import os

from ui.customer.restaurant_view import RestaurantView
from db_utils import execute_query


class CustomerDashboard(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_restaurant = None
        self.cart_items = []  # List of dictionaries containing menu_item and quantity
        self.customer_id = None
        self._source_call = None  # Track the source of method calls
        self.initUI()
        # Load customer profile data after UI is initialized
        self.load_customer_profile()
    
    def initUI(self):
        self.setWindowTitle("Food Delivery - Customer Dashboard")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Set zero margins to fix white box
        main_layout.setSpacing(0)  # Remove spacing between sidebar and content
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)  # Add proper padding
        
        # User info section
        user_info = QFrame()
        user_info.setObjectName("user-info")
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
        
        # Create image container with dark background
        image_container = QFrame()
        image_container.setObjectName("image-container")
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        profile_pic = QLabel()
        profile_pic.setObjectName("profile-pic")
        profile_pic.setPixmap(QPixmap("assets/img/customer-avatar.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(profile_pic)
        
        welcome_label = QLabel(f"Welcome, {self.user.username}")
        welcome_label.setObjectName("welcome-label")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        user_info_layout.addWidget(image_container)
        user_info_layout.addWidget(welcome_label)
        sidebar_layout.addWidget(user_info)
        
        # Navigation buttons
        nav_buttons = [
            {"text": "Browse Restaurants", "icon": "🏠", "slot": self.browse_restaurants},
            {"text": "My Orders", "icon": "📦", "slot": self.my_orders},
            {"text": "Favorites", "icon": "❤️", "slot": self.favorites},
            {"text": "My Profile", "icon": "👤", "slot": self.profile},
            {"text": "Cart", "icon": "🛒", "slot": self.cart}
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
        
        # Create pages
        self.home_page = self.create_home_page()
        self.restaurants_page = self.create_restaurants_page()
        self.orders_page = self.create_orders_page()
        self.favorites_page = self.create_favorites_page()
        self.profile_page = self.create_profile_page()
        self.cart_page = self.create_cart_page()
        
        # Add pages to content area
        self.content_area.addWidget(self.home_page)
        self.content_area.addWidget(self.restaurants_page)
        self.content_area.addWidget(self.orders_page)
        self.content_area.addWidget(self.favorites_page)
        self.content_area.addWidget(self.profile_page)
        self.content_area.addWidget(self.cart_page)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        # Apply styles
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50; 
            }
            #sidebar {
                background-color: #2c3e50;
                border-radius: 0px;
                padding: 10px;
                color: white;
            }
            #user-info {
                border-bottom: 1px solid #34495e;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #243342;
                border-radius: 8px;
            }
            #image-container {
                background-color: transparent;
                margin: 0;
                padding: 0;
            }
            #profile-pic {
                background-color: transparent;
                padding: 0;
                margin: 0;
            }
            #welcome-label {
                color: white;
                background-color: transparent;
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
            .restaurant-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                border: 1px solid #e0e0e0;
            }
            .restaurant-card:hover {
                border: 1px solid #3498db;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .restaurant-name {
                font-weight: bold;
                font-size: 18px;
                color: #2c3e50;
            }
            .restaurant-cuisine {
                color: #7f8c8d;
                font-size: 14px;
            }
            .restaurant-rating {
                color: #f39c12;
                font-weight: bold;
            }
        """)
        
        # Start with home page
        self.content_area.setCurrentWidget(self.home_page)
    
    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Welcome content
        placeholder_label = QLabel("Welcome to the Food Delivery App")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setFont(QFont("Arial", 24))
        
        placeholder_sublabel = QLabel("Browse restaurants and order your favorite food")
        placeholder_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_sublabel.setFont(QFont("Arial", 14))
        
        # Quick access buttons
        buttons_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse Restaurants")
        browse_btn.setObjectName("action-button")
        browse_btn.clicked.connect(self.browse_restaurants)
        browse_btn.setMinimumHeight(80)
        
        orders_btn = QPushButton("My Orders")
        orders_btn.setObjectName("action-button")
        orders_btn.clicked.connect(self.my_orders)
        orders_btn.setMinimumHeight(80)
        
        cart_btn = QPushButton("My Cart")
        cart_btn.setObjectName("action-button")
        cart_btn.clicked.connect(self.cart)
        cart_btn.setMinimumHeight(80)
        
        buttons_layout.addWidget(browse_btn)
        buttons_layout.addWidget(orders_btn)
        buttons_layout.addWidget(cart_btn)
        
        layout.addStretch()
        layout.addWidget(placeholder_label)
        layout.addWidget(placeholder_sublabel)
        layout.addSpacing(40)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return page
    
    def create_restaurants_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Browse Restaurants")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Restaurants grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        self.restaurants_grid = QGridLayout(scroll_content)
        self.restaurants_grid.setSpacing(15)
        
        scroll_area.setWidget(scroll_content)
        
        layout.addWidget(header)
        layout.addWidget(scroll_area)
        
        # Load restaurants
        self.load_restaurants()
        
        return page
    
    def create_orders_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("My Orders")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Orders scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        self.orders_layout = QVBoxLayout(scroll_content)
        self.orders_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.load_orders)
        
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(scroll_area)
        
        return page
    
    def create_favorites_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("My Favorites")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Placeholder content
        placeholder = QLabel("Your favorite restaurants will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(header)
        layout.addWidget(placeholder)
        
        return page
    
    def create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("My Profile")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Profile form container
        form_container = QFrame()
        form_container.setObjectName("profile-card")
        form_layout = QVBoxLayout(form_container)
        
        # Input fields
        input_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.email_input = QLineEdit()
        
        # Save button
        save_btn = QPushButton("Save Profile")
        save_btn.setObjectName("action-button")
        save_btn.clicked.connect(self.save_profile)
        
        # Add fields to form
        input_layout.addRow("Name:", self.name_input)
        input_layout.addRow("Phone:", self.phone_input)
        input_layout.addRow("Address:", self.address_input)
        input_layout.addRow("Email:", self.email_input)
        
        # Add to container
        form_layout.addLayout(input_layout)
        form_layout.addWidget(save_btn)
        
        # Load customer profile data
        self.load_customer_profile()
        
        # Add to main layout
        layout.addWidget(header)
        layout.addWidget(form_container)
        layout.addStretch()
        
        return page
    
    def create_cart_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("My Cart")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Cart items table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity", "Total", "Actions"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.setAlternatingRowColors(True)
        
        # Order summary and checkout button
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)
        
        self.cart_total_label = QLabel("Total: 0.00 AED")
        self.cart_total_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.cart_total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        checkout_btn = QPushButton("Proceed to Checkout")
        checkout_btn.setObjectName("action-button")
        checkout_btn.setMinimumHeight(50)
        checkout_btn.clicked.connect(self.show_checkout_dialog)
        
        summary_layout.addWidget(self.cart_total_label)
        summary_layout.addWidget(checkout_btn)
        
        layout.addWidget(header)
        layout.addWidget(self.cart_table)
        layout.addWidget(summary_frame)
        
        return page
    
    def load_restaurants(self):
        # Clear existing restaurants
        while self.restaurants_grid.count():
            item = self.restaurants_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get restaurants from database
        restaurants = execute_query("SELECT * FROM restaurants ORDER BY name")
        
        if not restaurants:
            empty_label = QLabel("No restaurants found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.restaurants_grid.addWidget(empty_label, 0, 0)
            return
        
        # Create restaurant cards
        row, col = 0, 0
        max_cols = 2
        
        for restaurant in restaurants:
            card = QFrame()
            card.setObjectName("restaurant-card")
            card.setProperty("class", "restaurant-card")
            card_layout = QVBoxLayout(card)
            
            name_label = QLabel(restaurant['name'])
            name_label.setProperty("class", "restaurant-name")
            
            cuisine_label = QLabel(f"Cuisine: {restaurant['cuisine_type']}")
            cuisine_label.setProperty("class", "restaurant-cuisine")
            
            rating_label = QLabel(f"Rating: {restaurant['rating']:.1f}★")
            rating_label.setProperty("class", "restaurant-rating")
            
            view_button = QPushButton("View Menu")
            view_button.setObjectName("action-button")
            view_button.clicked.connect(lambda _, id=restaurant['restaurant_id']: self.view_restaurant(id))
            
            card_layout.addWidget(name_label)
            card_layout.addWidget(cuisine_label)
            card_layout.addWidget(rating_label)
            card_layout.addWidget(view_button)
            
            self.restaurants_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def view_restaurant(self, restaurant_id):
        # Get restaurant view
        restaurant_view = RestaurantView(restaurant_id)
        restaurant_view.back_to_restaurants.connect(self.browse_restaurants)
        restaurant_view.add_to_cart.connect(self.handle_add_to_cart)
        
        # Add to content area
        if self.current_restaurant:
            self.content_area.removeWidget(self.current_restaurant)
            self.current_restaurant.deleteLater()
        
        self.current_restaurant = restaurant_view
        self.content_area.addWidget(restaurant_view)
        self.content_area.setCurrentWidget(restaurant_view)
    
    def handle_add_to_cart(self, menu_item, quantity):
        # Check if item already in cart
        total_quantity = quantity
        for item in self.cart_items:
            if item['menu_item']['menu_id'] == menu_item['menu_id']:
                total_quantity += item['quantity']
        
        # Check if total quantity exceeds stock
        if total_quantity > menu_item['stock_quantity']:
            QMessageBox.warning(
                self,
                "Insufficient Stock",
                f"Sorry, only {menu_item['stock_quantity']} {menu_item['dish_name']} available. You already have {total_quantity - quantity} in your cart."
            )
            return
        
        # Add new item to cart or update existing
        for item in self.cart_items:
            if item['menu_item']['menu_id'] == menu_item['menu_id']:
                item['quantity'] += quantity
                self.update_cart_display()
                QMessageBox.information(
                    self,
                    "Added to Cart",
                    f"{quantity} x {menu_item['dish_name']} added to your cart"
                )
                return
        
        # Add new item to cart
        self.cart_items.append({
            'menu_item': menu_item,
            'quantity': quantity
        })
        
        self.update_cart_display()
        QMessageBox.information(
            self,
            "Added to Cart",
            f"{quantity} x {menu_item['dish_name']} added to your cart"
        )
    
    def update_cart_display(self):
        # Clear existing items
        self.cart_table.setRowCount(0)
        
        # Calculate total
        total = 0
        
        # Add items to table
        for i, item in enumerate(self.cart_items):
            menu_item = item['menu_item']
            quantity = item['quantity']
            
            # Calculate item price
            unit_price = float(menu_item['discount_price'] if menu_item['discount_price'] else menu_item['price'])
            item_total = unit_price * quantity
            total += item_total
            
            # Add row to table
            self.cart_table.insertRow(i)
            
            # Item name
            name_item = QTableWidgetItem(menu_item['dish_name'])
            self.cart_table.setItem(i, 0, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"{unit_price:.2f} AED")
            self.cart_table.setItem(i, 1, price_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(quantity))
            self.cart_table.setItem(i, 2, quantity_item)
            
            # Total
            total_item = QTableWidgetItem(f"{item_total:.2f} AED")
            self.cart_table.setItem(i, 3, total_item)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("delete-button")
            remove_btn.clicked.connect(lambda _, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
        
        # Update total label
        self.cart_total_label.setText(f"Total: {total:.2f} AED")
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart_items):
            del self.cart_items[index]
            self.update_cart_display()
    
    def browse_restaurants(self):
        self.content_area.setCurrentWidget(self.restaurants_page)
    
    def my_orders(self):
        self.content_area.setCurrentWidget(self.orders_page)
        self.load_orders()
    
    def favorites(self):
        self.content_area.setCurrentWidget(self.favorites_page)
    
    def profile(self):
        self.content_area.setCurrentWidget(self.profile_page)
        self.load_customer_profile()  # Refresh profile data
    
    def cart(self):
        self.content_area.setCurrentWidget(self.cart_page)
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
    
    def show_checkout_dialog(self):
        """Show checkout dialog to confirm order"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty. Add items before checkout.")
            return
        
        # Get total price
        total = 0
        for item in self.cart_items:
            menu_item = item['menu_item']
            quantity = item['quantity']
            unit_price = float(menu_item['discount_price'] if menu_item['discount_price'] else menu_item['price'])
            total += unit_price * quantity
        
        # Create checkout dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Checkout")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Order summary
        summary_label = QLabel("Order Summary")
        summary_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # Restaurant info (first item's restaurant)
        restaurant_id = self.cart_items[0]['menu_item']['restaurant_id']
        restaurant = execute_query("SELECT * FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))[0]
        restaurant_label = QLabel(f"Restaurant: {restaurant['name']}")
        
        # Items summary
        items_frame = QFrame()
        items_layout = QVBoxLayout(items_frame)
        
        for item in self.cart_items:
            menu_item = item['menu_item']
            quantity = item['quantity']
            unit_price = float(menu_item['discount_price'] if menu_item['discount_price'] else menu_item['price'])
            item_total = unit_price * quantity
            
            item_layout = QHBoxLayout()
            item_name = QLabel(f"{quantity} x {menu_item['dish_name']}")
            item_price = QLabel(f"{item_total:.2f} AED")
            item_price.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            item_layout.addWidget(item_name)
            item_layout.addWidget(item_price)
            
            items_layout.addLayout(item_layout)
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount = QLabel(f"{total:.2f} AED")
        total_amount.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(total_amount)
        
        # Delivery info
        delivery_label = QLabel("Delivery Information")
        delivery_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        form_layout = QFormLayout()
        
        # Get customer info
        customer = execute_query("SELECT * FROM customers WHERE user_id = %s", (self.user.user_id,))
        if customer:
            customer = customer[0]
        else:
            customer = {"name": "", "phone": "", "address": ""}
        
        self.delivery_name = QLineEdit(customer['name'])
        self.delivery_phone = QLineEdit(customer['phone'])
        self.delivery_address = QLineEdit(customer['address'])
        
        form_layout.addRow("Name:", self.delivery_name)
        form_layout.addRow("Phone:", self.delivery_phone)
        form_layout.addRow("Delivery Address:", self.delivery_address)
        
        # Payment method
        payment_label = QLabel("Payment Method")
        payment_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash on Delivery", "Credit Card", "Digital Wallet"])
        
        form_layout.addRow("Payment Method:", self.payment_method)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        place_order_btn = QPushButton("Place Order")
        place_order_btn.setObjectName("action-button")
        place_order_btn.clicked.connect(lambda: self.place_order(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(place_order_btn)
        
        # Add all to layout
        layout.addWidget(summary_label)
        layout.addWidget(restaurant_label)
        layout.addWidget(items_frame)
        layout.addLayout(total_layout)
        layout.addWidget(QLabel(""))  # Spacer
        layout.addWidget(delivery_label)
        layout.addLayout(form_layout)
        layout.addWidget(QLabel(""))  # Spacer
        layout.addLayout(buttons_layout)
        
        # Show dialog
        dialog.exec()
    
    def place_order(self, dialog):
        """Place an order with the items in the cart"""
        # Validate input
        name = self.delivery_name.text().strip()
        phone = self.delivery_phone.text().strip()
        address = self.delivery_address.text().strip()
        
        if not name or not phone or not address:
            QMessageBox.warning(dialog, "Missing Information", "Please fill in all delivery information fields.")
            return
        
        try:
            # Calculate subtotal and total
            subtotal = 0
            for item in self.cart_items:
                menu_item = item['menu_item']
                quantity = item['quantity']
                unit_price = float(menu_item['discount_price'] if menu_item['discount_price'] else menu_item['price'])
                subtotal += unit_price * quantity
            
            # For now, total is the same as subtotal (no delivery fee or tax applied)
            total = subtotal
            
            # Get restaurant ID from first item
            restaurant_id = self.cart_items[0]['menu_item']['restaurant_id']
            
            # Get customer email from user
            user_email = execute_query("SELECT email FROM users WHERE user_id = %s", (self.user.user_id,))[0]['email']
            
            # Get or create customer
            customer_query = "SELECT * FROM customers WHERE user_id = %s"
            customer = execute_query(customer_query, (self.user.user_id,))
            
            if not customer:
                # Create customer profile with email
                insert_customer = """
                INSERT INTO customers (user_id, name, phone, address, email) 
                VALUES (%s, %s, %s, %s, %s)
                """
                customer_id = execute_query(
                    insert_customer, 
                    (self.user.user_id, name, phone, address, user_email), 
                    fetch=False
                )
            else:
                customer_id = customer[0]['customer_id']
                
                # Update customer details
                update_customer = """
                UPDATE customers 
                SET name = %s, phone = %s, address = %s 
                WHERE customer_id = %s
                """
                execute_query(
                    update_customer, 
                    (name, phone, address, customer_id), 
                    fetch=False
                )
            
            # Create order with all required fields
            order_query = """
            INSERT INTO orders (customer_id, restaurant_id, subtotal, total_amount, 
                               delivery_status, payment_method, delivery_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            order_id = execute_query(
                order_query, 
                (customer_id, restaurant_id, subtotal, total, 
                 "Pending", self.payment_method.currentText(), address), 
                fetch=False
            )
            
            # Add order items with unit_price and total_price
            for item in self.cart_items:
                menu_item = item['menu_item']
                quantity = item['quantity']
                unit_price = float(menu_item['discount_price'] if menu_item['discount_price'] else menu_item['price'])
                total_price = unit_price * quantity
                
                item_query = """
                INSERT INTO order_items (order_id, menu_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
                """
                execute_query(
                    item_query, 
                    (order_id, menu_item['menu_id'], quantity, unit_price, total_price), 
                    fetch=False
                )
                
                # Update stock quantity
                update_stock_query = """
                UPDATE menus 
                SET stock_quantity = stock_quantity - %s,
                    availability = CASE 
                        WHEN stock_quantity - %s <= 0 THEN 'Out of Stock' 
                        ELSE availability 
                    END
                WHERE menu_id = %s
                """
                execute_query(
                    update_stock_query,
                    (quantity, quantity, menu_item['menu_id']),
                    fetch=False
                )
            
            # Clear cart and close dialog
            self.cart_items = []
            self.update_cart_display()
            dialog.accept()
            
            # Show success message
            QMessageBox.information(
                self, 
                "Order Placed", 
                f"Your order has been placed successfully. Order #: {order_id}"
            )
            
            # Go to orders page
            self.my_orders()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to place order: {str(e)}")
            print(f"Order placement error: {e}")
    
    def load_orders(self):
        """Load customer orders"""
        # Clear existing orders
        while self.orders_layout.count():
            item = self.orders_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get customer ID
        customer = execute_query("SELECT customer_id FROM customers WHERE user_id = %s", (self.user.user_id,))
        if not customer:
            # No orders yet
            no_orders_label = QLabel("You haven't placed any orders yet.")
            no_orders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_layout.addWidget(no_orders_label)
            return
        
        customer_id = customer[0]['customer_id']
        
        # Get orders
        orders = execute_query("""
            SELECT o.*, r.name as restaurant_name, r.address as restaurant_address
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.customer_id = %s
            ORDER BY o.order_time DESC
        """, (customer_id,))
        
        if not orders:
            # No orders yet
            no_orders_label = QLabel("You haven't placed any orders yet.")
            no_orders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_layout.addWidget(no_orders_label)
            return
        
        # Create order cards
        for order in orders:
            self.create_order_card(order)
    
    def create_order_card(self, order):
        """Create a card displaying order information"""
        card = QFrame()
        card.setObjectName("order-card")
        card_layout = QVBoxLayout(card)
        
        # Order header
        header_layout = QHBoxLayout()
        
        # Order ID and date
        order_id_label = QLabel(f"Order #{order['order_id']}")
        order_id_label.setObjectName("order-id")
        order_id_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        date_label = QLabel(order['order_time'].strftime("%Y-%m-%d %H:%M"))
        date_label.setObjectName("order-date")
        
        header_layout.addWidget(order_id_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        
        # Restaurant info
        restaurant_label = QLabel(f"Restaurant: {order['restaurant_name']}")
        restaurant_label.setObjectName("restaurant-name")
        
        # Status with color coding
        status_layout = QHBoxLayout()
        status_text = QLabel("Status:")
        status_value = QLabel(order['delivery_status'])
        
        # Set color based on status
        status_color = "#95a5a6"  # Default gray
        if order['delivery_status'] == "New":
            status_color = "#3498db"  # Blue
        elif order['delivery_status'] == "Preparing":
            status_color = "#f39c12"  # Orange
        elif order['delivery_status'] == "Ready for Pickup":
            status_color = "#2ecc71"  # Green
        elif order['delivery_status'] == "Completed":
            status_color = "#27ae60"  # Dark green
        elif order['delivery_status'] == "Cancelled":
            status_color = "#e74c3c"  # Red
        
        status_value.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        status_layout.addWidget(status_text)
        status_layout.addWidget(status_value)
        status_layout.addStretch()
        
        # Payment method and total
        payment_layout = QHBoxLayout()
        payment_method = QLabel(f"Payment: {order['payment_method']}")
        total_amount = QLabel(f"Total: {float(order['total_amount']):.2f} AED")
        total_amount.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        payment_layout.addWidget(payment_method)
        payment_layout.addStretch()
        payment_layout.addWidget(total_amount)
        
        # View details button
        details_btn = QPushButton("View Order Details")
        details_btn.setObjectName("action-button")
        details_btn.clicked.connect(lambda: self.view_order_details(order['order_id']))
        
        # Add all elements to card
        card_layout.addLayout(header_layout)
        card_layout.addWidget(restaurant_label)
        card_layout.addLayout(status_layout)
        card_layout.addLayout(payment_layout)
        card_layout.addWidget(details_btn)
        
        # Add to orders layout
        self.orders_layout.addWidget(card)
    
    def view_order_details(self, order_id):
        """Show a dialog with order details"""
        # Get order details
        order = execute_query("""
            SELECT o.*, r.name as restaurant_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.order_id = %s
        """, (order_id,))[0]
        
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
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Order header
        header_label = QLabel(f"Order #{order_id}")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # Order info
        info_frame = QFrame()
        info_layout = QFormLayout(info_frame)
        
        restaurant_name = QLabel(order['restaurant_name'])
        order_date = QLabel(order['order_time'].strftime("%Y-%m-%d %H:%M"))
        order_status = QLabel(order['delivery_status'])
        payment_method = QLabel(order['payment_method'])
        
        info_layout.addRow("Restaurant:", restaurant_name)
        info_layout.addRow("Order Date:", order_date)
        info_layout.addRow("Status:", order_status)
        info_layout.addRow("Payment Method:", payment_method)
        
        # Order items
        items_label = QLabel("Order Items")
        items_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity", "Total"])
        items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        items_table.setAlternatingRowColors(True)
        items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Add items to table
        total = 0
        items_table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            name_item = QTableWidgetItem(item['dish_name'])
            price_item = QTableWidgetItem(f"{float(item['unit_price']):.2f} AED")
            quantity_item = QTableWidgetItem(str(item['quantity']))
            item_total = float(item['unit_price']) * item['quantity']
            total_item = QTableWidgetItem(f"{item_total:.2f} AED")
            
            items_table.setItem(i, 0, name_item)
            items_table.setItem(i, 1, price_item)
            items_table.setItem(i, 2, quantity_item)
            items_table.setItem(i, 3, total_item)
            
            total += item_total
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total Amount:")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount = QLabel(f"{float(order['total_amount']):.2f} AED")
        total_amount.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_amount)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        # Add all to layout
        layout.addWidget(header_label)
        layout.addWidget(info_frame)
        layout.addWidget(items_label)
        layout.addWidget(items_table)
        layout.addLayout(total_layout)
        layout.addWidget(close_btn)
        
        dialog.setStyleSheet("""
            #order-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #e0e0e0;
            }
            #order-card:hover {
                border: 1px solid #3498db;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            #order-id {
                color: #2c3e50;
            }
            #order-date {
                color: #7f8c8d;
                font-size: 14px;
            }
            #restaurant-name {
                color: #2c3e50;
                font-size: 16px;
                margin: 5px 0;
            }
        """)
        
        # Show dialog
        dialog.exec()

    def load_customer_profile(self):
        """Load customer profile information from database"""
        try:
            # Try to get customer info with email from joined tables
            result = execute_query(
                """
                SELECT c.*, u.email FROM customers c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.user_id = %s
                """,
                (self.user.user_id,)
            )
            
            if result:
                customer_info = result[0]
                self.customer_id = customer_info['customer_id']
                
                # Update profile fields if they exist
                if hasattr(self, 'name_input') and hasattr(self, 'phone_input'):
                    self.name_input.setText(customer_info.get('name', ''))
                    self.phone_input.setText(customer_info.get('phone', ''))
                    self.address_input.setText(customer_info.get('address', ''))
                    self.email_input.setText(customer_info.get('email', ''))
            else:
                # No customer record yet, but we can still get user email
                user_result = execute_query(
                    "SELECT email FROM users WHERE user_id = %s",
                    (self.user.user_id,)
                )
                
                if user_result and hasattr(self, 'email_input'):
                    self.email_input.setText(user_result[0].get('email', ''))
                    # Pre-fill name with username
                    self.name_input.setText(self.user.username)
                
                self.customer_id = None
                
                # Create a basic customer profile record if none exists
                self._source_call = "load_profile"
                self.save_profile()
                
        except Exception as e:
            print(f"Error loading customer profile: {e}")
            self.customer_id = None

    def save_profile(self):
        """Save customer profile"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        email = self.email_input.text().strip()
        
        # Only show warning if this is a manual save (not auto-save during loading)
        if (not name or not phone or not address) and self._source_call != "load_profile":
            QMessageBox.warning(self, "Missing Information", "Please fill in all required fields.")
            return
            
        # Use default values for empty fields
        name = name or self.user.username
        phone = phone or ""
        address = address or ""
        email = email or ""
        
        try:
            # Update email in users table
            email_query = """
            UPDATE users 
            SET email = %s
            WHERE user_id = %s
            """
            execute_query(email_query, (email, self.user.user_id), fetch=False)
            
            if self.customer_id:
                # Update existing profile
                query = """
                UPDATE customers 
                SET name = %s, phone = %s, address = %s, email = %s
                WHERE customer_id = %s
                """
                params = (name, phone, address, email, self.customer_id)
            else:
                # Create new profile - include email field
                query = """
                INSERT INTO customers (user_id, name, phone, address, email)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (self.user.user_id, name, phone, address, email)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                # Only show success message for manual saves
                if self._source_call != "load_profile":
                    QMessageBox.information(self, "Success", "Profile saved successfully")
                
                # If this was a new profile, load the new ID
                if not self.customer_id:
                    # Avoid infinite recursion by just getting the ID
                    new_id_result = execute_query(
                        "SELECT customer_id FROM customers WHERE user_id = %s",
                        (self.user.user_id,)
                    )
                    if new_id_result:
                        self.customer_id = new_id_result[0]['customer_id']
            else:
                # Only show error for manual saves
                if self._source_call != "load_profile":
                    QMessageBox.critical(self, "Error", "Failed to save profile")
        except Exception as e:
            # Only show error for manual saves
            if self._source_call != "load_profile":
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            print(f"Profile save error: {e}")
        
        # Reset the source call tracker
        self._source_call = None

# ... rest of file unchanged ... 