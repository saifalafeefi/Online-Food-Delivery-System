from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                             QSizePolicy, QSpacerItem, QStackedWidget, QMessageBox,
                             QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QHeaderView, QSlider, QGroupBox, QTextEdit,
                             QSpinBox, QProgressBar, QMenu, QCheckBox, QRadioButton)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QCursor
import os

from ui.customer.restaurant_view import RestaurantView
from db_utils import execute_query


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search")
        self.setMinimumWidth(400)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Search type selection
        self.search_type = QComboBox()
        self.search_type.addItems(["Restaurants", "Menu Items", "Orders"])
        self.search_type.currentTextChanged.connect(self.update_search_fields)
        layout.addWidget(QLabel("Search Type:"))
        layout.addWidget(self.search_type)
        
        # Common search field
        self.search_term = QLineEdit()
        self.search_term.setPlaceholderText("Enter search term...")
        layout.addWidget(QLabel("Search Term:"))
        layout.addWidget(self.search_term)
        
        # Restaurant specific fields
        self.restaurant_fields = QWidget()
        restaurant_layout = QVBoxLayout(self.restaurant_fields)
        self.cuisine_type = QComboBox()
        self.cuisine_type.addItems(["All", "Italian", "Chinese", "Indian", "Mexican", "American", "Japanese"])
        restaurant_layout.addWidget(QLabel("Cuisine Type:"))
        restaurant_layout.addWidget(self.cuisine_type)
        self.location = QLineEdit()
        self.location.setPlaceholderText("Enter location...")
        restaurant_layout.addWidget(QLabel("Location:"))
        restaurant_layout.addWidget(self.location)
        layout.addWidget(self.restaurant_fields)
        
        # Menu items specific fields
        self.menu_fields = QWidget()
        menu_layout = QVBoxLayout(self.menu_fields)
        self.category = QComboBox()
        self.category.addItems(["All", "Main Course", "Appetizer", "Dessert", "Beverage"])
        menu_layout.addWidget(QLabel("Category:"))
        menu_layout.addWidget(self.category)
        self.min_price = QLineEdit()
        self.min_price.setPlaceholderText("Min price")
        menu_layout.addWidget(QLabel("Price Range:"))
        menu_layout.addWidget(self.min_price)
        self.max_price = QLineEdit()
        self.max_price.setPlaceholderText("Max price")
        menu_layout.addWidget(self.max_price)
        self.is_vegetarian = QComboBox()
        self.is_vegetarian.addItems(["All", "Vegetarian", "Non-Vegetarian"])
        menu_layout.addWidget(QLabel("Dietary:"))
        menu_layout.addWidget(self.is_vegetarian)
        layout.addWidget(self.menu_fields)
        
        # Orders specific fields
        self.order_fields = QWidget()
        order_layout = QVBoxLayout(self.order_fields)
        self.status = QComboBox()
        self.status.addItems(["All", "Pending", "Confirmed", "Preparing", "On Delivery", "Delivered", "Cancelled"])
        order_layout.addWidget(QLabel("Order Status:"))
        order_layout.addWidget(self.status)
        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("Start date (YYYY-MM-DD)")
        order_layout.addWidget(QLabel("Date Range:"))
        order_layout.addWidget(self.start_date)
        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("End date (YYYY-MM-DD)")
        order_layout.addWidget(self.end_date)
        layout.addWidget(self.order_fields)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(search_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Hide all specific fields initially
        self.restaurant_fields.hide()
        self.menu_fields.hide()
        self.order_fields.hide()
        
    def update_search_fields(self, search_type):
        self.restaurant_fields.hide()
        self.menu_fields.hide()
        self.order_fields.hide()
        
        if search_type == "Restaurants":
            self.restaurant_fields.show()
        elif search_type == "Menu Items":
            self.menu_fields.show()
        elif search_type == "Orders":
            self.order_fields.show()

class CustomerDashboard(QWidget):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_restaurant = None
        self.cart_items = []  # List of dictionaries containing menu_item and quantity
        self.customer_id = None
        self._source_call = None  # Track the source of method calls
        
        # Set up auto-refresh timer for real-time updates
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(500)  # Refresh every 0.5 seconds
        
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
                background-color: #34495e;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                padding: 12px;
                margin: 5px 0;
            }
            #nav-button:hover {
                background-color: #3498db;
            }
            #logout-button {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 12px;
            }
            #logout-button:hover {
                background-color: #c0392b;
            }
            
            /* Restaurant and favorite cards */
            #restaurant-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin: 10px;
                border: 1px solid #e0e0e0;
            }
            #restaurant-card:hover {
                border: 1px solid #3498db;
            }
            .restaurant-name {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .restaurant-cuisine, .restaurant-rating {
                color: #7f8c8d;
                margin-bottom: 10px;
            }
            .restaurant-rating {
                color: #f39c12;
                font-weight: bold;
            }
            #action-button {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            #action-button:hover {
                background-color: #2980b9;
            }
            
            /* Favorite buttons */
            #add-favorite-button {
                background-color: #ffffff;
                color: #e74c3c;
                border: 1px solid #e74c3c;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            #add-favorite-button:hover {
                background-color: #e74c3c;
                color: white;
            }
            #favorite-button {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            #unfavorite-button {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            #unfavorite-button:hover {
                background-color: #c0392b;
            }
            
            /* Refresh button */
            #refresh-button {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            #refresh-button:hover {
                background-color: #27ae60;
            }
            
            /* Table Styles */
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
            
            /* Dialog Styles */
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            /* Menu Item Card Styles */
            .menu-item-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                border: 1px solid #e0e0e0;
            }
            .menu-item-card:hover {
                border: 1px solid #3498db;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .menu-item-name {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
            }
            .menu-item-price {
                font-weight: bold;
                color: #27ae60;
            }
            .menu-item-restaurant {
                color: #7f8c8d;
                font-size: 14px;
            }
            .menu-item-desc {
                color: #34495e;
                font-size: 14px;
                margin: 10px 0;
            }
            #add-to-cart-btn {
                background-color: #27ae60;
                color: white;
            }
            #add-to-cart-btn:hover {
                background-color: #219a52;
            }
            
            /* Order Card Styles */
            .order-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                border: 1px solid #e0e0e0;
            }
            .order-card:hover {
                border: 1px solid #3498db;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .order-number {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
            }
            .order-date {
                color: #7f8c8d;
                font-size: 14px;
            }
            .order-restaurant {
                color: #34495e;
                font-size: 14px;
                margin: 5px 0;
            }
            .order-status {
                color: #f39c12;
                font-weight: bold;
                font-size: 14px;
            }
            .order-total {
                color: #27ae60;
                font-weight: bold;
                font-size: 16px;
                margin: 5px 0;
            }
            #view-details-btn {
                background-color: #3498db;
                color: white;
            }
            #view-details-btn:hover {
                background-color: #2980b9;
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
        header.setFont(QFont("Arial", 24))
        
        # Search bar and filter section
        search_bar_layout = QHBoxLayout()
        
        # Search input
        self.restaurant_search_input = QLineEdit()
        self.restaurant_search_input.setPlaceholderText("Search by name, cuisine, or location...")
        
        # Filter dropdown
        self.cuisine_filter = QComboBox()
        self.cuisine_filter.addItem("All Cuisines")
        cuisines = ["Italian", "Chinese", "Indian", "Japanese", "Mexican", "American", "Thai", "French", "Mediterranean", "Other"]
        self.cuisine_filter.addItems(cuisines)
        
        # Location input
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Location...")
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setObjectName("action-button")
        search_btn.clicked.connect(self.perform_restaurant_search)
        
        # Add to layout
        search_bar_layout.addWidget(self.restaurant_search_input, 3)
        search_bar_layout.addWidget(self.cuisine_filter, 2)
        search_bar_layout.addWidget(self.location_input, 2)
        search_bar_layout.addWidget(search_btn, 1)
        
        # Restaurants grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Content widget
        content = QWidget()
        self.restaurants_grid = QGridLayout(content)
        self.restaurants_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(content)
        
        # Add to main layout
        layout.addWidget(header)
        layout.addLayout(search_bar_layout)
        layout.addWidget(scroll)
        
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
        
        # Add scroll area for favorites
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.favorites_grid = QGridLayout(scroll_content)
        self.favorites_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.favorites_grid.setSpacing(20)
        scroll_area.setWidget(scroll_content)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refresh-button")
        refresh_btn.clicked.connect(self.load_favorites)
        
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(scroll_area)
        
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
    
    def create_restaurant_card(self, restaurant):
        """Create a card for displaying a restaurant"""
        # Get customer's favorite restaurants for comparison
        favorite_restaurant_ids = []
        if self.customer_id:
            favorites_query = """
                SELECT restaurant_id
                FROM favorites
                WHERE customer_id = %s
            """
            favorites = execute_query(favorites_query, (self.customer_id,))
            if favorites:
                favorite_restaurant_ids = [f['restaurant_id'] for f in favorites]
        
        # Create restaurant card
        card = QFrame()
        card.setObjectName("restaurant-card")
        card.setProperty("class", "restaurant-card")
        card_layout = QVBoxLayout(card)
        
        # Check if restaurant is active
        is_active = restaurant.get('is_active', True)
        
        name_label = QLabel(restaurant['name'])
        name_label.setProperty("class", "restaurant-name")
        name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        cuisine_label = QLabel(f"Cuisine: {restaurant['cuisine_type']}")
        cuisine_label.setProperty("class", "restaurant-cuisine")
        
        rating_label = QLabel(f"Rating: {restaurant['rating']:.1f}★")
        rating_label.setProperty("class", "restaurant-rating")
        
        # Button container
        btn_container = QHBoxLayout()
        
        view_button = QPushButton("View Menu")
        view_button.setObjectName("action-button")
        view_button.clicked.connect(lambda _, id=restaurant['restaurant_id']: self.view_restaurant(id))
        
        # Check if restaurant is already in favorites
        is_favorite = restaurant['restaurant_id'] in favorite_restaurant_ids
        favorite_button = QPushButton("♥ Favorited" if is_favorite else "♡ Add to Favorites")
        favorite_button.setObjectName("favorite-button" if is_favorite else "add-favorite-button")
        
        # Set button properties
        if is_favorite:
            favorite_button.setEnabled(False)  # Disable if already a favorite
        else:
            favorite_button.clicked.connect(
                lambda _, id=restaurant['restaurant_id']: self.add_to_favorites(id)
            )
        
        btn_container.addWidget(view_button)
        btn_container.addWidget(favorite_button)
        
        card_layout.addWidget(name_label)
        card_layout.addWidget(cuisine_label)
        card_layout.addWidget(rating_label)
        card_layout.addLayout(btn_container)
        
        # If restaurant is suspended, add overlay and disable buttons
        if not is_active:
            # Style the card to look greyed out
            card.setStyleSheet("""
                QFrame {
                    background-color: rgba(200, 200, 200, 0.8);
                    border-radius: 8px;
                    border: 1px solid #ddd;
                }
                QLabel {
                    color: #555;
                }
            """)
            
            # Create suspended label overlay
            suspended_label = QLabel("SUSPENDED")
            suspended_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            suspended_label.setStyleSheet("""
                background-color: rgba(231, 76, 60, 0.8);
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 8px;
                border-radius: 4px;
            """)
            
            # Add to layout (on top of everything)
            card_layout.insertWidget(0, suspended_label)
            
            # Disable the buttons
            view_button.setEnabled(False)
            favorite_button.setEnabled(False)
        
        return card

    def load_restaurants(self):
        # Clear existing restaurants
        while self.restaurants_grid.count():
            item = self.restaurants_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get search term from input
        search_term = self.restaurant_search_input.text().strip()
        cuisine_type = self.cuisine_filter.currentText()
        if cuisine_type == "All Cuisines":
            cuisine_type = None
        location = self.location_input.text().strip()
        
        # Get restaurants from database - include inactive to show as suspended
        from db_utils import search_restaurants
        restaurants = search_restaurants(
            search_term=search_term, 
            cuisine_type=cuisine_type, 
            location=location, 
            include_inactive=True  # Include inactive restaurants to display as suspended
        )
        
        if not restaurants:
            empty_label = QLabel("No restaurants found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.restaurants_grid.addWidget(empty_label, 0, 0)
            return
        
        # Display the restaurants
        self.display_restaurants(restaurants)
    
    def view_restaurant(self, restaurant_id):
        # Check if restaurant is active before displaying
        restaurant_info = execute_query("""
            SELECT r.*, u.is_active
            FROM restaurants r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.restaurant_id = %s
        """, (restaurant_id,))
        
        if not restaurant_info or not restaurant_info[0]['is_active']:
            QMessageBox.warning(
                self, 
                "Restaurant Suspended", 
                "This restaurant is currently suspended and not accepting orders.\n\nPlease choose another restaurant."
            )
            return
        
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
            price_item = QTableWidgetItem(f"AED {unit_price:.2f}")
            self.cart_table.setItem(i, 1, price_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(quantity))
            self.cart_table.setItem(i, 2, quantity_item)
            
            # Total
            total_item = QTableWidgetItem(f"AED {item_total:.2f}")
            self.cart_table.setItem(i, 3, total_item)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("delete-button")
            remove_btn.clicked.connect(lambda _, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
        
        # Update total label
        self.cart_total_label.setText(f"Total: AED {total:.2f}")
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart_items):
            del self.cart_items[index]
            self.update_cart_display()
    
    def browse_restaurants(self):
        self.content_area.setCurrentWidget(self.restaurants_page)
        self.load_restaurants()  # Load restaurants when switching to the page
    
    def my_orders(self):
        self.content_area.setCurrentWidget(self.orders_page)
        self.load_orders()
    
    def favorites(self):
        self.content_area.setCurrentWidget(self.favorites_page)
        self.load_favorites()  # Load favorites when switching to the page
    
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
            item_price = QLabel(f"AED {item_total:.2f}")
            item_price.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            item_layout.addWidget(item_name)
            item_layout.addWidget(item_price)
            
            items_layout.addLayout(item_layout)
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount = QLabel(f"AED {float(total):.2f}")
        total_amount.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
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
                               delivery_status, payment_method, delivery_address, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Set payment status based on payment method
            payment_method = self.payment_method.currentText()
            if payment_method in ["Credit Card", "Digital Wallet"]:
                payment_status = "Paid"
            else:  # Cash on Delivery
                payment_status = "Pending"
                
            order_id = execute_query(
                order_query, 
                (customer_id, restaurant_id, subtotal, total, 
                 "Pending", payment_method, address, payment_status), 
                fetch=False
            )
            
            # Generate and update order number
            import datetime
            today = datetime.datetime.now()
            order_number = f"ORD-{today.strftime('%Y%m%d')}-{order_id:04d}"
            
            # Update the order with the generated order number
            update_order_number = """
            UPDATE orders SET order_number = %s WHERE order_id = %s
            """
            execute_query(update_order_number, (order_number, order_id), fetch=False)
            
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
            
            # Show success message with order number instead of ID
            QMessageBox.information(
                self, 
                "Order Placed", 
                f"Your order has been placed successfully. Order #: {order_number}"
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
        
        # Use order_number if available, otherwise fall back to order_id
        order_display = order.get('order_number', '')
        if not order_display or order_display.strip() == '':
            order_display = f"#{order['order_id']}"
        else:
            order_display = f"#{order_display}"
            
        # Order number and date
        order_id_label = QLabel(f"Order {order_display}")
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
        total_amount = QLabel(f"Total: AED {float(order['total_amount']):.2f}")
        total_amount.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        payment_layout.addWidget(payment_method)
        payment_layout.addStretch()
        payment_layout.addWidget(total_amount)
        
        # View details button
        details_btn = QPushButton("View Details")
        details_btn.setObjectName("view-details-btn")
        details_btn.clicked.connect(lambda checked, oid=order['order_id']: self.view_order_details(oid))
        
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
            SELECT o.*, r.name as restaurant_name, r.restaurant_id, c.customer_id,
                   dp.delivery_person_id, dp.name as delivery_person_name,
                   (SELECT COUNT(*) FROM ratings WHERE order_id = o.order_id) as has_rating
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
            WHERE o.order_id = %s
        """, (order_id,))[0]
        
        # Get order items
        items = execute_query("""
            SELECT oi.*, m.dish_name
            FROM order_items oi
            JOIN menus m ON oi.menu_id = m.menu_id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        # Use order_number if available, otherwise fall back to order_id
        order_display = order.get('order_number', '')
        if not order_display or order_display.strip() == '':
            order_display = f"#{order_id}"
        else:
            order_display = f"#{order_display}"
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Order {order_display} Details")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Order header
        header_label = QLabel(f"Order {order_display}")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # Order info
        info_frame = QFrame()
        info_layout = QFormLayout(info_frame)
        
        restaurant_name = QLabel(order['restaurant_name'])
        order_date = QLabel(order['order_time'].strftime("%Y-%m-%d %H:%M"))
        order_status = QLabel(order['delivery_status'])
        payment_method = QLabel(order['payment_method'])
        
        # Set delivery person name if available
        delivery_person_text = "Not assigned"
        if order.get('delivery_person_name'):
            delivery_person_text = order['delivery_person_name']
        delivery_person = QLabel(delivery_person_text)
        
        info_layout.addRow("Restaurant:", restaurant_name)
        info_layout.addRow("Order Date:", order_date)
        info_layout.addRow("Status:", order_status)
        info_layout.addRow("Payment Method:", payment_method)
        info_layout.addRow("Delivery Person:", delivery_person)
        
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
            price_item = QTableWidgetItem(f"AED {float(item['unit_price']):.2f}")
            quantity_item = QTableWidgetItem(str(item['quantity']))
            item_total = float(item['unit_price']) * item['quantity']
            total_item = QTableWidgetItem(f"AED {item_total:.2f}")
            
            items_table.setItem(i, 0, name_item)
            items_table.setItem(i, 1, price_item)
            items_table.setItem(i, 2, quantity_item)
            items_table.setItem(i, 3, total_item)
            
            total += item_total
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total Amount:")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount = QLabel(f"AED {float(order['total_amount']):.2f}")
        total_amount.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_amount)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        # Add Rate Order button for completed orders that haven't been rated
        if order['delivery_status'] == 'Delivered' and not order['has_rating']:
            rate_btn = QPushButton("Rate Order")
            rate_btn.setObjectName("action-button")
            rate_btn.clicked.connect(lambda: self.show_rating_dialog(order_id, order['restaurant_id'], 
                                                                    order['customer_id'], order['delivery_person_id']))
            buttons_layout.addWidget(rate_btn)
        
        # Add all to layout
        layout.addWidget(header_label)
        layout.addWidget(info_frame)
        layout.addWidget(items_label)
        layout.addWidget(items_table)
        layout.addLayout(total_layout)
        layout.addLayout(buttons_layout)
        
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
            #action-button {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            #action-button:hover {
                background-color: #2980b9;
            }
        """)
        
        # Show dialog
        dialog.exec()

    def show_rating_dialog(self, order_id, restaurant_id, customer_id, delivery_person_id):
        """Show dialog to rate food and delivery"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Rate Your Order")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header = QLabel("Please Rate Your Experience")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Food Rating
        food_group = QGroupBox("Food Quality")
        food_layout = QVBoxLayout(food_group)
        
        food_label = QLabel("How would you rate the food?")
        
        food_rating_layout = QHBoxLayout()
        food_rating = QSlider(Qt.Orientation.Horizontal)
        food_rating.setRange(1, 5)
        food_rating.setValue(5)  # Default value
        food_rating.setTickPosition(QSlider.TickPosition.TicksBelow)
        food_rating.setTickInterval(1)
        
        food_value_label = QLabel("5 ★")
        food_value_label.setFixedWidth(30)
        
        # Update label when slider value changes
        food_rating.valueChanged.connect(lambda value: food_value_label.setText(f"{value} ★"))
        
        food_rating_layout.addWidget(food_rating)
        food_rating_layout.addWidget(food_value_label)
        
        food_layout.addWidget(food_label)
        food_layout.addLayout(food_rating_layout)
        
        # Delivery Rating
        delivery_group = QGroupBox("Delivery Service")
        delivery_layout = QVBoxLayout(delivery_group)
        
        delivery_label = QLabel("How would you rate the delivery service?")
        
        delivery_rating_layout = QHBoxLayout()
        delivery_rating = QSlider(Qt.Orientation.Horizontal)
        delivery_rating.setRange(1, 5)
        delivery_rating.setValue(5)  # Default value
        delivery_rating.setTickPosition(QSlider.TickPosition.TicksBelow)
        delivery_rating.setTickInterval(1)
        
        delivery_value_label = QLabel("5 ★")
        delivery_value_label.setFixedWidth(30)
        
        # Update label when slider value changes
        delivery_rating.valueChanged.connect(lambda value: delivery_value_label.setText(f"{value} ★"))
        
        delivery_rating_layout.addWidget(delivery_rating)
        delivery_rating_layout.addWidget(delivery_value_label)
        
        delivery_layout.addWidget(delivery_label)
        delivery_layout.addLayout(delivery_rating_layout)
        
        # Comment
        comment_group = QGroupBox("Additional Comments")
        comment_layout = QVBoxLayout(comment_group)
        
        comment_edit = QTextEdit()
        comment_edit.setPlaceholderText("Share your feedback about the food and delivery (optional)")
        comment_edit.setFixedHeight(80)
        
        comment_layout.addWidget(comment_edit)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        submit_btn = QPushButton("Submit Rating")
        submit_btn.setObjectName("submit-button")
        submit_btn.clicked.connect(lambda: self.submit_rating(
            dialog,
            order_id,
            restaurant_id,
            customer_id,
            delivery_person_id,
            food_rating.value(),
            delivery_rating.value(),
            comment_edit.toPlainText()
        ))
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(submit_btn)
        
        # Add all to layout
        layout.addWidget(header)
        layout.addWidget(food_group)
        layout.addWidget(delivery_group)
        layout.addWidget(comment_group)
        layout.addLayout(buttons_layout)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 1.5em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #f39c12;
                border: 1px solid #777;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }
            #submit-button {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            #submit-button:hover {
                background-color: #27ae60;
            }
        """)
        
        dialog.exec()

    def submit_rating(self, dialog, order_id, restaurant_id, customer_id, delivery_person_id, 
                     food_rating, delivery_rating, comment):
        """Submit rating to database"""
        try:
            # Insert rating into database
            query = """
            INSERT INTO ratings (customer_id, order_id, restaurant_id, delivery_person_id, 
                               food_rating, delivery_rating, comment, rating_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            result = execute_query(query, (
                customer_id, 
                order_id, 
                restaurant_id, 
                delivery_person_id, 
                food_rating, 
                delivery_rating, 
                comment
            ), fetch=False)
            
            # Update order as rated
            update_query = """
            UPDATE orders SET is_rated = TRUE WHERE order_id = %s
            """
            execute_query(update_query, (order_id,), fetch=False)
            
            # Update restaurant rating average
            restaurant_update = """
            UPDATE restaurants r
            SET rating = (
                SELECT AVG(food_rating) 
                FROM ratings 
                WHERE restaurant_id = %s
            )
            WHERE restaurant_id = %s
            """
            execute_query(restaurant_update, (restaurant_id, restaurant_id), fetch=False)
            
            # Update delivery person rating average
            if delivery_person_id:
                delivery_update = """
                UPDATE delivery_personnel dp
                SET avg_rating = (
                    SELECT AVG(delivery_rating) 
                    FROM ratings 
                    WHERE delivery_person_id = %s
                )
                WHERE delivery_person_id = %s
                """
                execute_query(delivery_update, (delivery_person_id, delivery_person_id), fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", "Thank you for your rating!")
                dialog.accept()
                
                # Refresh orders list to show updated status
                self.load_orders()
            else:
                QMessageBox.critical(self, "Error", "Failed to submit rating")
        except Exception as e:
            print(f"Error submitting rating: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

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

    def perform_restaurant_search(self):
        """Execute restaurant search based on the search bar inputs"""
        search_term = self.restaurant_search_input.text()
        cuisine_type = self.cuisine_filter.currentText()
        if cuisine_type == "All Cuisines":
            cuisine_type = None
        location = self.location_input.text()
        
        self.search_restaurants(search_term, cuisine_type, location)

    def search_restaurants(self, search_term=None, cuisine_type=None, location=None):
        from db_utils import search_restaurants
        
        # If empty search term, empty location, and "All" cuisines, just load all restaurants
        if not search_term and not cuisine_type and not location:
            self.load_restaurants()
            return
            
        # Otherwise perform the search - include inactive so we can display them as suspended
        results = search_restaurants(search_term, cuisine_type, location, include_inactive=True)
        
        # Handle case where results is None (error in search)
        if results is None:
            print("Error: search_restaurants returned None")
            empty_results = []
            self.display_restaurants(empty_results)
            return
            
        self.display_restaurants(results)
    
    def search_menu_items(self, search_term=None, category=None, min_price=None, max_price=None, is_vegetarian=None):
        from db_utils import search_menu_items
        is_veg = None
        if is_vegetarian == "Vegetarian":
            is_veg = True
        elif is_vegetarian == "Non-Vegetarian":
            is_veg = False
            
        results = search_menu_items(
            search_term=search_term,
            restaurant_id=self.current_restaurant['restaurant_id'] if self.current_restaurant else None,
            category=category if category != "All" else None,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            is_vegetarian=is_veg
        )
        self.display_menu_items(results)
    
    def search_orders(self, search_term=None, status=None, start_date=None, end_date=None):
        from db_utils import search_orders
        results = search_orders(
            customer_id=self.customer_id,
            customer_name=search_term,
            status=status if status != "All" else None,
            start_date=start_date,
            end_date=end_date
        )
        self.display_orders(results)
    
    def display_restaurants(self, restaurants):
        # Clear existing restaurants
        while self.restaurants_grid.count():
            item = self.restaurants_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not restaurants:
            no_results = QLabel("No restaurants found")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.restaurants_grid.addWidget(no_results, 0, 0)
            return
        
        row, col = 0, 0
        for restaurant in restaurants:
            card = self.create_restaurant_card(restaurant)
            self.restaurants_grid.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
    
    def display_menu_items(self, menu_items):
        # Clear existing items
        while self.restaurants_grid.count():
            item = self.restaurants_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not menu_items:
            no_results = QLabel("No menu items found")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.restaurants_grid.addWidget(no_results, 0, 0)
            return
        
        row, col = 0, 0
        for item in menu_items:
            card = QFrame()
            card.setObjectName("menu-item-card")
            card_layout = QVBoxLayout(card)
            
            # Item name and price
            name_price = QHBoxLayout()
            name_label = QLabel(item['dish_name'])
            name_label.setObjectName("menu-item-name")
            price_label = QLabel(f"AED {item['price']:.2f}")
            price_label.setObjectName("menu-item-price")
            name_price.addWidget(name_label)
            name_price.addStretch()
            name_price.addWidget(price_label)
            
            # Restaurant name
            restaurant_label = QLabel(f"From: {item['restaurant_name']}")
            restaurant_label.setObjectName("menu-item-restaurant")
            
            # Description
            desc_label = QLabel(item['description'])
            desc_label.setObjectName("menu-item-desc")
            desc_label.setWordWrap(True)
            
            # Add to cart button
            add_to_cart_btn = QPushButton("Add to Cart")
            add_to_cart_btn.setObjectName("add-to-cart-btn")
            add_to_cart_btn.clicked.connect(lambda checked, i=item: self.handle_add_to_cart(i, 1))
            
            card_layout.addLayout(name_price)
            card_layout.addWidget(restaurant_label)
            card_layout.addWidget(desc_label)
            card_layout.addWidget(add_to_cart_btn)
            
            self.restaurants_grid.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
    
    def display_orders(self, orders):
        # Clear existing items
        while self.restaurants_grid.count():
            item = self.restaurants_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not orders:
            no_results = QLabel("No orders found")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.restaurants_grid.addWidget(no_results, 0, 0)
            return
        
        row, col = 0, 0
        for order in orders:
            card = QFrame()
            card.setObjectName("order-card")
            card_layout = QVBoxLayout(card)
            
            # Order number and date
            order_header = QHBoxLayout()
            order_num = QLabel(f"Order #{order['order_number']}")
            order_num.setObjectName("order-number")
            order_date = QLabel(order['order_date'].strftime("%Y-%m-%d %H:%M"))
            order_date.setObjectName("order-date")
            order_header.addWidget(order_num)
            order_header.addStretch()
            order_header.addWidget(order_date)
            
            # Restaurant name
            restaurant_label = QLabel(f"Restaurant: {order['restaurant_name']}")
            restaurant_label.setObjectName("order-restaurant")
            
            # Status
            status_label = QLabel(f"Status: {order['delivery_status']}")
            status_label.setObjectName("order-status")
            
            # Total amount
            total_label = QLabel(f"Total: AED {float(order['total_amount']):.2f}")
            total_label.setObjectName("order-total")
            
            # View details button
            details_btn = QPushButton("View Details")
            details_btn.setObjectName("view-details-btn")
            details_btn.clicked.connect(lambda checked, oid=order['order_id']: self.view_order_details(oid))
            
            card_layout.addLayout(order_header)
            card_layout.addWidget(restaurant_label)
            card_layout.addWidget(status_label)
            card_layout.addWidget(total_label)
            card_layout.addWidget(details_btn)
            
            self.restaurants_grid.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1

    def load_favorites(self):
        """Load favorite restaurants from database"""
        # Clear existing favorites
        while self.favorites_grid.count():
            item = self.favorites_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get customer ID
        if not self.customer_id:
            customer = execute_query("SELECT customer_id FROM customers WHERE user_id = %s", (self.user.user_id,))
            if customer:
                self.customer_id = customer[0]['customer_id']
            else:
                # No customer profile yet
                placeholder = QLabel("Please complete your profile first to use favorites")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.favorites_grid.addWidget(placeholder, 0, 0)
                return
        
        # Get favorites from database
        favorites_query = """
            SELECT r.*, f.favorite_id
            FROM favorites f
            JOIN restaurants r ON f.restaurant_id = r.restaurant_id
            WHERE f.customer_id = %s
            ORDER BY r.name ASC
        """
        favorites = execute_query(favorites_query, (self.customer_id,))
        
        if not favorites:
            placeholder = QLabel("You don't have any favorite restaurants yet")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.favorites_grid.addWidget(placeholder, 0, 0)
            return
        
        # Create restaurant cards
        row, col = 0, 0
        max_cols = 2
        
        for restaurant in favorites:
            card = QFrame()
            card.setObjectName("restaurant-card")
            card.setProperty("class", "favorite-card")
            card_layout = QVBoxLayout(card)
            
            name_label = QLabel(restaurant['name'])
            name_label.setProperty("class", "restaurant-name")
            name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            
            cuisine_label = QLabel(f"Cuisine: {restaurant['cuisine_type']}")
            cuisine_label.setProperty("class", "restaurant-cuisine")
            
            rating_label = QLabel(f"Rating: {restaurant['rating']:.1f}★")
            rating_label.setProperty("class", "restaurant-rating")
            
            # Button container for view and unfavorite
            btn_container = QHBoxLayout()
            
            view_button = QPushButton("View Menu")
            view_button.setObjectName("action-button")
            view_button.clicked.connect(lambda _, id=restaurant['restaurant_id']: self.view_restaurant(id))
            
            unfavorite_button = QPushButton("♥ Remove")
            unfavorite_button.setObjectName("unfavorite-button")
            unfavorite_button.clicked.connect(lambda _, fav_id=restaurant['favorite_id']: self.remove_favorite(fav_id))
            
            btn_container.addWidget(view_button)
            btn_container.addWidget(unfavorite_button)
            
            card_layout.addWidget(name_label)
            card_layout.addWidget(cuisine_label)
            card_layout.addWidget(rating_label)
            card_layout.addLayout(btn_container)
            
            self.favorites_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def add_to_favorites(self, restaurant_id):
        """Add a restaurant to favorites"""
        if not self.customer_id:
            customer = execute_query("SELECT customer_id FROM customers WHERE user_id = %s", (self.user.user_id,))
            if customer:
                self.customer_id = customer[0]['customer_id']
            else:
                QMessageBox.warning(self, "Profile Incomplete", 
                                   "Please complete your profile first to add favorites.")
                self.profile()
                return
        
        # Check if already in favorites
        check_query = "SELECT * FROM favorites WHERE customer_id = %s AND restaurant_id = %s"
        existing = execute_query(check_query, (self.customer_id, restaurant_id))
        
        if existing:
            QMessageBox.information(self, "Already Favorited", 
                                   "This restaurant is already in your favorites.")
            return
        
        # Add to favorites
        insert_query = "INSERT INTO favorites (customer_id, restaurant_id) VALUES (%s, %s)"
        result = execute_query(insert_query, (self.customer_id, restaurant_id), fetch=False)
        
        if result:
            QMessageBox.information(self, "Added to Favorites", 
                                   "Restaurant has been added to your favorites.")
        else:
            QMessageBox.warning(self, "Error", 
                               "Could not add restaurant to favorites. Please try again.")
    
    def remove_favorite(self, favorite_id):
        """Remove a restaurant from favorites"""
        try:
            # Check if the favorite exists
            query = """
                DELETE FROM favorites
                WHERE favorite_id = %s AND customer_id = %s
            """
            result = execute_query(query, (favorite_id, self.customer_id), fetch=False)
            
            if result is not None:
                # Refresh favorites
                self.load_favorites()
                QMessageBox.information(self, "Success", "Restaurant removed from favorites.")
            else:
                QMessageBox.warning(self, "Error", "Failed to remove restaurant from favorites.")
                
        except Exception as e:
            print(f"Error removing favorite: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def auto_refresh(self):
        """Automatically refresh data based on current page"""
        try:
            # Skip refresh if mouse button is pressed to prevent click interference
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            if QApplication.mouseButtons() != Qt.MouseButton.NoButton:
                return
                
            current_widget = self.content_area.currentWidget()
            
            # Only refresh orders page for real-time updates
            if current_widget == self.orders_page:
                # Get currently selected order ID if in details view
                current_order_id = None
                for order_id, frame in getattr(self, '_order_frames', {}).items():
                    # Check if any order details are expanded
                    if hasattr(frame, '_details_visible') and frame._details_visible:
                        current_order_id = order_id
                        break
                
                # Refresh orders list
                self.load_orders()
                
                # Re-expand details if there was an expanded order
                if current_order_id:
                    if hasattr(self, '_order_frames') and current_order_id in self._order_frames:
                        # Expand the order details again
                        self.view_order_details(current_order_id)
        except Exception as e:
            # Silent exception handling for auto-refresh
            print(f"Auto-refresh error in customer dashboard: {e}")
            # Don't show error to user since this runs automatically