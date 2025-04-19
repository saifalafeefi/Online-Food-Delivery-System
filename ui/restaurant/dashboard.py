from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                             QSizePolicy, QSpacerItem, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QMessageBox, QSpinBox, QTextEdit,
                             QDoubleSpinBox, QTabWidget, QDateEdit, QProgressBar,
                             QMenu)
from PySide6.QtCore import Qt, Signal, QSize, QDate, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor
from db_utils import execute_query
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

class RestaurantDashboard(QWidget):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.restaurant_id = None
        self.restaurant_data = None
        self._source_call = None  # Track the source of profile save calls
        
        # Initialize order layouts dictionary
        self.order_layouts = {
            'New': None,
            'Preparing': None,
            'Ready for Pickup': None,
            'Completed': None,
            'Cancelled': None
        }
        
        self.initUI()
        
        # Load restaurant data
        self.load_restaurant_profile()
        
        # Set up auto-refresh timer for orders
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(60000)  # 60 seconds
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start()
        
    def initUI(self):
        self.setWindowTitle("Food Delivery - Restaurant Dashboard")
        
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
        
        # Initialize with a placeholder name
        restaurant_name = "Your Restaurant"
        
        welcome_label = QLabel(f"Welcome, {self.user.username}")
        welcome_label.setObjectName("welcome-label")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Create and store the restaurant name label
        self.restaurant_name_label = QLabel(restaurant_name)
        self.restaurant_name_label.setObjectName("restaurant-name")
        
        user_info_layout.addWidget(welcome_label)
        user_info_layout.addWidget(self.restaurant_name_label)
        sidebar_layout.addWidget(user_info)
        
        # Navigation buttons
        nav_buttons = [
            {"text": "Dashboard", "icon": "📊", "slot": self.show_dashboard},
            {"text": "Orders", "icon": "📦", "slot": self.manage_orders},
            {"text": "Menu", "icon": "🍽️", "slot": self.manage_menu},
            {"text": "Restaurant Profile", "icon": "🏢", "slot": self.edit_profile},
            {"text": "Reports", "icon": "📈", "slot": self.view_reports}
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
        
        # Content area with stacked pages
        self.content_area = QStackedWidget()
        
        # Create pages
        self.dashboard_page = self.create_dashboard_page()
        self.orders_page = self.create_orders_page()
        self.menu_page = self.create_menu_page()
        self.profile_page = self.create_profile_page()
        self.reports_page = self.create_reports_page()
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.orders_page)
        self.content_area.addWidget(self.menu_page)
        self.content_area.addWidget(self.profile_page)
        self.content_area.addWidget(self.reports_page)
        
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
            #restaurant-name {
                color: #3498db;
                font-size: 14px;
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
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Restaurant Dashboard")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 24))
        
        # Stats overview
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        # Create stat cards with empty data (will be populated in load_dashboard_stats)
        self.stat_cards = {
            "today_orders": {"title": "Today's Orders", "value": "0", "icon": "📦", "widget": None},
            "pending_orders": {"title": "Pending Orders", "value": "0", "icon": "⏳", "widget": None},
            "menu_items": {"title": "Menu Items", "value": "0", "icon": "🍽️", "widget": None},
            "total_sales": {"title": "Total Sales", "value": "0 AED", "icon": "��", "widget": None}
        }
        
        for key, card in self.stat_cards.items():
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
            
            # Store value label reference for later updates
            card["widget"] = value
        
        # Recent orders section
        recent_orders_label = QLabel("Recent Orders")
        recent_orders_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Add refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(recent_orders_label)
        refresh_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.load_dashboard_stats)
        refresh_layout.addWidget(refresh_btn)
        
        self.recent_orders_table = QTableWidget()
        self.recent_orders_table.setColumnCount(5)
        self.recent_orders_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Items", "Total", "Status"])
        self.recent_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_orders_table.setAlternatingRowColors(True)
        
        # Add to layout
        layout.addWidget(header)
        layout.addWidget(stats_frame)
        layout.addSpacing(20)
        layout.addLayout(refresh_layout)
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
    
    def create_orders_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Manage Orders")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Arial", 24))
        
        # Search and filter bar
        search_layout = QHBoxLayout()
        
        # Search input for customer name
        search_label = QLabel("Search:")
        self.orders_search_input = QLineEdit()
        self.orders_search_input.setPlaceholderText("Search by customer name...")
        
        # Date range for orders
        date_label = QLabel("Date:")
        self.orders_start_date = QDateEdit()
        self.orders_start_date.setCalendarPopup(True)
        self.orders_start_date.setDate(QDate.currentDate().addDays(-7))  # Default to last week
        
        # Style the date edit to match app theme
        self.orders_start_date.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QCalendarWidget {
                background-color: white;
                color: #2c3e50;
            }
            QCalendarWidget QToolButton {
                background-color: #3498db;
                color: white;
                border-radius: 2px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #2c3e50;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #ccc;
            }
        """)
        
        to_label = QLabel("to")
        
        self.orders_end_date = QDateEdit()
        self.orders_end_date.setCalendarPopup(True)
        self.orders_end_date.setDate(QDate.currentDate())  # Default to today
        self.orders_end_date.setStyleSheet(self.orders_start_date.styleSheet())  # Use same style
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setObjectName("action-button")
        search_btn.clicked.connect(self.search_orders)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.load_all_orders)
        
        # Add to layout
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.orders_search_input, 3)
        search_layout.addWidget(date_label)
        search_layout.addWidget(self.orders_start_date)
        search_layout.addWidget(to_label)
        search_layout.addWidget(self.orders_end_date)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(refresh_btn)
        
        # Tab widget for different order statuses
        tabs = QTabWidget()
        
        # Create tabs for different order states
        new_orders_tab = self.create_orders_tab("New")
        preparing_tab = self.create_orders_tab("Preparing")
        ready_tab = self.create_orders_tab("Ready for Pickup")
        completed_tab = self.create_orders_tab("Completed")
        cancelled_tab = self.create_orders_tab("Cancelled")
        
        # Add tabs to widget
        tabs.addTab(new_orders_tab, "New Orders")
        tabs.addTab(preparing_tab, "Preparing")
        tabs.addTab(ready_tab, "Ready for Pickup")
        tabs.addTab(completed_tab, "Completed")
        tabs.addTab(cancelled_tab, "Cancelled")
        
        layout.addWidget(header)
        layout.addLayout(search_layout)
        layout.addWidget(tabs)
        
        # Store tab references
        self.order_tabs = {
            "New": new_orders_tab,
            "Preparing": preparing_tab,
            "Ready for Pickup": ready_tab,
            "Completed": completed_tab,
            "Cancelled": cancelled_tab
        }
        
        # Load orders
        self.load_all_orders()
        
        return page
    
    def create_orders_tab(self, status):
        """Create a tab for orders with the given status"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area for orders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Content widget
        content = QWidget()
        self.order_layouts[status] = QVBoxLayout(content)
        self.order_layouts[status].setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def load_all_orders(self):
        """Load orders for all tabs"""
        # Clear existing orders
        for status, layout in self.order_layouts.items():
            # Clear layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
        # Add "No orders" message to each tab initially
        for status, layout in self.order_layouts.items():
            no_orders = QLabel(f"No {status.lower()} orders")
            no_orders.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_orders)
        
        if not self.restaurant_id:
            return
        
        # Get all orders for this restaurant
        try:
            restaurant_orders = execute_query("""
                SELECT o.*, c.name as customer_name, c.phone as customer_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.restaurant_id = %s
                ORDER BY o.order_time DESC
            """, (self.restaurant_id,))
            
            if not restaurant_orders:
                return
            
            # Clear "No orders" messages
            for status, layout in self.order_layouts.items():
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            # Map order statuses to tab names
            status_map = {
                "Pending": "New",
                "Confirmed": "New",
                "Preparing": "Preparing", 
                "On Delivery": "Ready for Pickup",
                "Delivered": "Completed",
                "Cancelled": "Cancelled"
            }
            
            # Group by status
            for order in restaurant_orders:
                # Map delivery_status to tab status
                tab_status = status_map.get(order['delivery_status'], "New")
                self.add_order_card(order, tab_status)
                
        except Exception as e:
            print(f"Error loading orders: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load orders: {str(e)}")
    
    def add_order_card(self, order, tab_status):
        """Add an order card to the appropriate tab"""
        # Create order card
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
            
        order_id_label = QLabel(f"Order {order_display}")
        order_id_label.setObjectName("order-id")
        order_id_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        time_label = QLabel(order['order_time'].strftime("%Y-%m-%d %H:%M"))
        time_label.setObjectName("order-time")
        
        header_layout.addWidget(order_id_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        # Status label
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_value = QLabel(order['delivery_status'])
        
        # Set color based on status
        status_color = "#95a5a6"  # Default gray
        if order['delivery_status'] == "Pending" or order['delivery_status'] == "Confirmed":
            status_color = "#3498db"  # Blue
        elif order['delivery_status'] == "Preparing":
            status_color = "#f39c12"  # Orange
        elif order['delivery_status'] == "Ready for Pickup":
            status_color = "#2ecc71"  # Green
        elif order['delivery_status'] == "Delivered":
            status_color = "#27ae60"  # Dark green
        elif order['delivery_status'] == "Cancelled":
            status_color = "#e74c3c"  # Red
        
        status_value.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(status_value)
        status_layout.addStretch()
        
        # Customer info
        customer_label = QLabel(f"Customer: {order['customer_name']} ({order['customer_phone']})")
        customer_label.setObjectName("customer-info")
        
        # Order items
        items_label = QLabel("Order Items:")
        items_label.setObjectName("items-label")
        items_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Get order items
        items = execute_query("""
            SELECT oi.*, m.dish_name, m.price, m.discount_price
            FROM order_items oi
            JOIN menus m ON oi.menu_id = m.menu_id
            WHERE oi.order_id = %s
        """, (order['order_id'],))
        
        # Create items list
        items_frame = QFrame()
        items_layout = QVBoxLayout(items_frame)
        items_layout.setContentsMargins(0, 0, 0, 0)
        
        total = 0
        
        for item in items:
            item_price = float(item['discount_price'] if item['discount_price'] else item['price'])
            item_total = item_price * item['quantity']
            total += item_total
            
            item_layout = QHBoxLayout()
            
            item_name = QLabel(f"{item['quantity']} x {item['dish_name']}")
            item_price = QLabel(f"{item_total:.2f} AED")
            item_price.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            item_layout.addWidget(item_name)
            item_layout.addWidget(item_price)
            
            items_layout.addLayout(item_layout)
        
        # Order total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        total_amount = QLabel(f"{total:.2f} AED")
        total_amount.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(total_amount)
        
        # Action buttons based on tab status
        buttons_layout = QHBoxLayout()
        
        if tab_status == "New":
            # For new orders (Pending or Confirmed)
            if order['delivery_status'] == "Pending":
                accept_btn = QPushButton("Confirm Order")
                accept_btn.setObjectName("action-button")
                accept_btn.clicked.connect(lambda: self.update_order_status(order['order_id'], "Confirmed"))
                
                reject_btn = QPushButton("Reject Order")
                reject_btn.setObjectName("delete-button")
                reject_btn.clicked.connect(lambda: self.update_order_status(order['order_id'], "Cancelled"))
                
                buttons_layout.addWidget(accept_btn)
            else:
                # Already confirmed, just start preparing
                prepare_btn = QPushButton("Start Preparing")
                prepare_btn.setObjectName("action-button")
                prepare_btn.clicked.connect(lambda: self.update_order_status(order['order_id'], "Preparing"))
                
                buttons_layout.addWidget(prepare_btn)
        
        elif tab_status == "Preparing":
            # For orders in preparation
            ready_btn = QPushButton("Mark as Ready")
            ready_btn.setObjectName("action-button")
            ready_btn.clicked.connect(lambda: self.update_order_status(order['order_id'], "Ready for Pickup"))
            
            buttons_layout.addWidget(ready_btn)
        
        # Add all components to card
        card_layout.addLayout(header_layout)
        card_layout.addLayout(status_layout)
        card_layout.addWidget(customer_label)
        card_layout.addWidget(items_label)
        card_layout.addWidget(items_frame)
        card_layout.addLayout(total_layout)
        card_layout.addLayout(buttons_layout)
        
        # Add card to appropriate layout
        if tab_status in self.order_layouts:
            self.order_layouts[tab_status].addWidget(card)
    
    def update_order_status(self, order_id, new_status):
        """Update an order's status"""
        # Map UI status names to database enum values
        status_db_map = {
            "Confirmed": "Confirmed",
            "Preparing": "Preparing",
            "Ready for Pickup": "On Delivery",  # This MUST match the database enum value
            "Completed": "Delivered",
            "Cancelled": "Cancelled"
        }
        
        # Get the database enum value
        db_status = status_db_map.get(new_status, new_status)
        
        # Special handling for cancelled orders to restore stock
        if new_status == "Cancelled":
            # Use cancel_order method which handles both status update and stock restoration
            self.cancel_order(order_id)
            return
        
        # Get order_number for display
        order_info = execute_query("SELECT order_number FROM orders WHERE order_id = %s", (order_id,))
        order_display = f"#{order_id}"
        if order_info and order_info[0]['order_number']:
            order_display = f"#{order_info[0]['order_number']}"
        
        # Regular status update for non-cancelled orders
        try:
            query = "UPDATE orders SET delivery_status = %s WHERE order_id = %s"
            result = execute_query(query, (db_status, order_id), fetch=False)
            
            if result is not None:
                print(f"Order {order_display} status updated to {db_status} successfully")
                self.show_info_message("Success", f"Order {order_display} status updated to {new_status}")
                # Refresh orders
                self.load_all_orders()
                # Also refresh dashboard stats when order status changes
                self.load_dashboard_stats()
            else:
                print(f"Failed to update Order {order_display} status to {db_status}")
                self.show_warning_message("Error", "Failed to update order status")
        except Exception as e:
            print(f"Error updating order status: {e}")
            self.show_error_message("Error", f"Failed to update order status: {str(e)}")
    
    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header section
        header_layout = QHBoxLayout()
        header = QLabel("Menu Management")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Action buttons
        add_btn = QPushButton("Add Menu Item")
        add_btn.setObjectName("action-button")
        add_btn.clicked.connect(self.add_menu_item)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        
        # Category filter
        category_layout = QHBoxLayout()
        category_label = QLabel("Filter by category:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filter_menu_items)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_filter)
        category_layout.addStretch()
        
        # Menu items table
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(7)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Discount", "Stock", "Actions"])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.menu_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.menu_table.setAlternatingRowColors(True)
        
        # Add to layout
        layout.addLayout(header_layout)
        layout.addLayout(category_layout)
        layout.addWidget(self.menu_table)
        
        # Load menu items if restaurant exists
        if self.restaurant_id:
            self.load_menu_items()
            self.load_categories()
        
        return page
    
    def create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Restaurant Profile")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        # Form layout
        form_layout = QFormLayout()
        
        # Profile fields
        self.profile_name = QLineEdit()
        self.profile_address = QLineEdit()
        self.profile_contact = QLineEdit()
        self.profile_cuisine = QComboBox()
        cuisines = ["Italian", "Chinese", "Indian", "Japanese", "Mexican", "American", "Thai", "French", "Mediterranean", "Other"]
        self.profile_cuisine.addItems(cuisines)
        
        # Add fields to form
        form_layout.addRow("Restaurant Name:", self.profile_name)
        form_layout.addRow("Address:", self.profile_address)
        form_layout.addRow("Contact Number:", self.profile_contact)
        form_layout.addRow("Cuisine Type:", self.profile_cuisine)
        
        # Advanced options
        advanced_section = QFrame()
        advanced_layout = QFormLayout(advanced_section)
        
        self.profile_opening = QLineEdit()
        self.profile_opening.setPlaceholderText("HH:MM (e.g. 09:00)")
        self.profile_closing = QLineEdit()
        self.profile_closing.setPlaceholderText("HH:MM (e.g. 22:00)")
        self.profile_delivery_radius = QSpinBox()
        self.profile_delivery_radius.setMinimum(1)
        self.profile_delivery_radius.setMaximum(50)
        self.profile_delivery_radius.setValue(5)
        self.profile_min_order = QDoubleSpinBox()
        self.profile_min_order.setMinimum(0)
        self.profile_min_order.setMaximum(1000)
        self.profile_min_order.setSingleStep(10)
        self.profile_min_order.setPrefix("AED ")
        
        advanced_layout.addRow("Opening Time:", self.profile_opening)
        advanced_layout.addRow("Closing Time:", self.profile_closing)
        advanced_layout.addRow("Delivery Radius (km):", self.profile_delivery_radius)
        advanced_layout.addRow("Minimum Order Amount:", self.profile_min_order)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Profile")
        save_btn.setObjectName("action-button")
        save_btn.clicked.connect(self.save_profile)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        # Add all components to main layout
        layout.addWidget(header)
        layout.addSpacing(10)
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Advanced Settings"))
        layout.addWidget(advanced_section)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # Load profile data if exists
        if self.restaurant_data:
            self.load_profile_data()
        
        return page
    
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
        
        # Create and style start date picker
        self.reports_start_date = QDateEdit()
        self.reports_start_date.setCalendarPopup(True)
        self.reports_start_date.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        self.reports_start_date.setObjectName("date-picker")
        self.reports_start_date.setFixedWidth(140)
        self.reports_start_date.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        self.reports_start_date.setDisplayFormat("dd MMM yyyy")
        
        # Create and style end date picker
        self.reports_end_date = QDateEdit()
        self.reports_end_date.setCalendarPopup(True)
        self.reports_end_date.setDate(QDate.currentDate())
        self.reports_end_date.setObjectName("date-picker")
        self.reports_end_date.setFixedWidth(140)
        self.reports_end_date.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        self.reports_end_date.setDisplayFormat("dd MMM yyyy")
        
        # From-To separator label with styling
        date_separator = QLabel("to")
        date_separator.setStyleSheet("color: #2c3e50; margin: 0 10px;")
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.refresh_restaurant_analytics)
        
        date_range_layout.addWidget(date_range_label)
        date_range_layout.addWidget(self.reports_start_date)
        date_range_layout.addWidget(date_separator)
        date_range_layout.addWidget(self.reports_end_date)
        date_range_layout.addStretch()
        date_range_layout.addWidget(refresh_btn)
        
        # Key metrics cards
        metrics_layout = QHBoxLayout()
        
        # Total Orders Card
        total_orders_card = QFrame()
        total_orders_card.setObjectName("metric-card")
        total_orders_layout = QVBoxLayout(total_orders_card)
        self.report_total_orders_label = QLabel("0")
        self.report_total_orders_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        total_orders_layout.addWidget(QLabel("Total Orders"))
        total_orders_layout.addWidget(self.report_total_orders_label)
        
        # Total Revenue Card
        revenue_card = QFrame()
        revenue_card.setObjectName("metric-card")
        revenue_layout = QVBoxLayout(revenue_card)
        self.report_revenue_label = QLabel("AED 0.00")
        self.report_revenue_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        revenue_layout.addWidget(QLabel("Total Revenue"))
        revenue_layout.addWidget(self.report_revenue_label)
        
        # Average Order Value Card
        aov_card = QFrame()
        aov_card.setObjectName("metric-card")
        aov_layout = QVBoxLayout(aov_card)
        self.report_aov_label = QLabel("AED 0.00")
        self.report_aov_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        aov_layout.addWidget(QLabel("Average Order Value"))
        aov_layout.addWidget(self.report_aov_label)
        
        # Average Delivery Time Card
        delivery_time_card = QFrame()
        delivery_time_card.setObjectName("metric-card")
        delivery_time_layout = QVBoxLayout(delivery_time_card)
        self.report_delivery_time_label = QLabel("0 min")
        self.report_delivery_time_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        delivery_time_layout.addWidget(QLabel("Avg. Delivery Time"))
        delivery_time_layout.addWidget(self.report_delivery_time_label)
        
        metrics_layout.addWidget(total_orders_card)
        metrics_layout.addWidget(revenue_card)
        metrics_layout.addWidget(aov_card)
        metrics_layout.addWidget(delivery_time_card)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Orders by Status Chart
        status_chart_card = QFrame()
        status_chart_card.setObjectName("chart-card")
        status_chart_layout = QVBoxLayout(status_chart_card)
        status_chart_layout.addWidget(QLabel("Orders by Status"))
        
        # Create a frame for the chart with its own layout
        self.report_status_chart = QFrame()
        self.report_status_chart.setMinimumHeight(300)
        chart_layout = QVBoxLayout(self.report_status_chart)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        status_chart_layout.addWidget(self.report_status_chart)
        
        # Revenue Trend Chart
        revenue_chart_card = QFrame()
        revenue_chart_card.setObjectName("chart-card")
        revenue_chart_layout = QVBoxLayout(revenue_chart_card)
        revenue_chart_layout.addWidget(QLabel("Revenue Trend"))
        
        # Create a frame for the chart with its own layout
        self.report_revenue_chart = QFrame()
        self.report_revenue_chart.setMinimumHeight(300)
        chart_layout = QVBoxLayout(self.report_revenue_chart)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        revenue_chart_layout.addWidget(self.report_revenue_chart)
        
        charts_layout.addWidget(status_chart_card)
        charts_layout.addWidget(revenue_chart_card)
        
        # Detailed Reports Section
        reports_tabs = QTabWidget()
        reports_tabs.setMinimumHeight(300)
        
        # Top Menu Items Tab
        menu_tab = QWidget()
        menu_layout = QVBoxLayout(menu_tab)
        self.top_menu_items_table = QTableWidget()
        self.top_menu_items_table.setColumnCount(5)
        self.top_menu_items_table.setHorizontalHeaderLabels(["Dish Name", "Orders", "Revenue", "Average Rating", "Stock Level"])
        self.top_menu_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        menu_layout.addWidget(self.top_menu_items_table)
        
        # Delivery Performance Tab
        delivery_tab = QWidget()
        delivery_layout = QVBoxLayout(delivery_tab)
        self.delivery_performance_table = QTableWidget()
        self.delivery_performance_table.setColumnCount(5)
        self.delivery_performance_table.setHorizontalHeaderLabels(["Delivery Person", "Deliveries", "Rating", "Avg. Time", "On-time Rate"])
        self.delivery_performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        delivery_layout.addWidget(self.delivery_performance_table)
        
        # Customer Insights Tab
        customer_tab = QWidget()
        customer_layout = QVBoxLayout(customer_tab)
        self.customer_insights_table = QTableWidget()
        self.customer_insights_table.setColumnCount(5)
        self.customer_insights_table.setHorizontalHeaderLabels(["Customer", "Orders", "Total Spent", "Avg. Order Value", "Last Order"])
        self.customer_insights_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        customer_layout.addWidget(self.customer_insights_table)
        
        reports_tabs.addTab(menu_tab, "Top Menu Items")
        reports_tabs.addTab(delivery_tab, "Delivery Performance")
        reports_tabs.addTab(customer_tab, "Top Customers")
        
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
            QDateEdit#date-picker {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 25px;
            }
            QDateEdit#date-picker::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border-left: 1px solid #7f8c8d;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QDateEdit#date-picker::down-arrow {
                image: url(ui/icons/calendar.png);
                width: 16px;
                height: 16px;
            }
            QDateEdit#date-picker:hover {
                background-color: #3d5a74;
                border: 1px solid #3498db;
            }
            QDateEdit#date-picker:focus {
                border: 2px solid #3498db;
            }
            QCalendarWidget {
                background-color: #34495e;
                color: white;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #2c3e50;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #34495e;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #2c3e50;
                border-radius: 3px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #3498db;
            }
            QPushButton#action-button {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton#action-button:hover {
                background-color: #2980b9;
            }
            QPushButton#action-button:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        # Load initial data
        if self.restaurant_id:
            self.refresh_restaurant_analytics()
        
        return page
        
    def refresh_restaurant_analytics(self):
        """Refresh all restaurant analytics data based on selected date range"""
        if not self.restaurant_id:
            return
            
        start_date = self.reports_start_date.date().toString("yyyy-MM-dd")
        
        # Get end date and add 1 day to make it inclusive of orders on the end date
        end_date_obj = self.reports_end_date.date()
        end_date_obj = end_date_obj.addDays(1)  # Add one day to include orders on the selected end date
        end_date = end_date_obj.toString("yyyy-MM-dd")
        
        try:
            # Get key metrics for this restaurant
            metrics_query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    AVG(TIMESTAMPDIFF(MINUTE, order_time, actual_delivery_time)) as avg_delivery_time
                FROM orders 
                WHERE restaurant_id = %s
                AND order_time BETWEEN %s AND %s
            """
            metrics = execute_query(metrics_query, (self.restaurant_id, start_date, end_date))
            
            if metrics and metrics[0]:
                self.report_total_orders_label.setText(str(metrics[0]['total_orders'] or 0))
                self.report_revenue_label.setText(f"AED {float(metrics[0]['total_revenue'] or 0):.2f}")
                self.report_aov_label.setText(f"AED {float(metrics[0]['avg_order_value'] or 0):.2f}")
                self.report_delivery_time_label.setText(f"{int(metrics[0]['avg_delivery_time'] or 0)} min")
            
            # Get orders by status for this restaurant
            status_query = """
                SELECT delivery_status, COUNT(*) as count
                FROM orders
                WHERE restaurant_id = %s
                AND order_time BETWEEN %s AND %s
                GROUP BY delivery_status
            """
            status_data = execute_query(status_query, (self.restaurant_id, start_date, end_date))
            
            # Get revenue trend for this restaurant
            revenue_query = """
                SELECT DATE(order_time) as date, SUM(total_amount) as revenue
                FROM orders
                WHERE restaurant_id = %s
                AND order_time BETWEEN %s AND %s
                GROUP BY DATE(order_time)
                ORDER BY date
            """
            revenue_data = execute_query(revenue_query, (self.restaurant_id, start_date, end_date))
            
            # Clear previous charts
            for i in reversed(range(self.report_status_chart.layout().count())): 
                widget = self.report_status_chart.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            for i in reversed(range(self.report_revenue_chart.layout().count())): 
                widget = self.report_revenue_chart.layout().itemAt(i).widget()
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
                
                # Add the canvas to the layout
                self.report_status_chart.layout().addWidget(status_canvas)
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
                
                # Add the canvas to the layout
                self.report_revenue_chart.layout().addWidget(revenue_canvas)
                revenue_fig.tight_layout()
                revenue_canvas.draw()
            
            # Get top menu items for this restaurant
            menu_query = """
                SELECT 
                    m.dish_name,
                    COUNT(oi.order_item_id) as order_count,
                    SUM(oi.total_price) as revenue,
                    m.preparation_time,
                    m.stock_quantity
                FROM menus m
                LEFT JOIN order_items oi ON m.menu_id = oi.menu_id
                LEFT JOIN orders o ON oi.order_id = o.order_id
                WHERE m.restaurant_id = %s
                AND (o.order_time IS NULL OR (o.order_time BETWEEN %s AND %s))
                GROUP BY m.menu_id
                ORDER BY revenue DESC, order_count DESC
                LIMIT 10
            """
            menu_data = execute_query(menu_query, (self.restaurant_id, start_date, end_date))
            
            if menu_data:
                self.top_menu_items_table.setRowCount(len(menu_data))
                for i, item in enumerate(menu_data):
                    self.top_menu_items_table.setItem(i, 0, QTableWidgetItem(item['dish_name']))
                    self.top_menu_items_table.setItem(i, 1, QTableWidgetItem(str(item['order_count'] or 0)))
                    self.top_menu_items_table.setItem(i, 2, QTableWidgetItem(f"AED {float(item['revenue'] or 0):.2f}"))
                    self.top_menu_items_table.setItem(i, 3, QTableWidgetItem(f"{float(item['preparation_time'] or 0)} min"))
                    self.top_menu_items_table.setItem(i, 4, QTableWidgetItem(f"{item['stock_quantity']}"))
            
            # Get delivery personnel performance for this restaurant's orders
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
                WHERE o.restaurant_id = %s
                AND o.order_time BETWEEN %s AND %s
                GROUP BY dp.delivery_person_id
                ORDER BY delivery_count DESC
                LIMIT 10
            """
            delivery_data = execute_query(delivery_query, (self.restaurant_id, start_date, end_date))
            
            if delivery_data:
                self.delivery_performance_table.setRowCount(len(delivery_data))
                for i, delivery in enumerate(delivery_data):
                    self.delivery_performance_table.setItem(i, 0, QTableWidgetItem(delivery['name']))
                    self.delivery_performance_table.setItem(i, 1, QTableWidgetItem(str(delivery['delivery_count'])))
                    self.delivery_performance_table.setItem(i, 2, QTableWidgetItem(f"{float(delivery['rating'] or 0):.1f}"))
                    self.delivery_performance_table.setItem(i, 3, QTableWidgetItem(f"{int(delivery['avg_time'] or 0)} min"))
                    self.delivery_performance_table.setItem(i, 4, QTableWidgetItem(f"{float(delivery['on_time_rate'] or 0):.1f}%"))
            
            # Get customer insights for this restaurant
            customer_query = """
                SELECT 
                    c.name,
                    COUNT(o.order_id) as order_count,
                    SUM(o.total_amount) as total_spent,
                    AVG(o.total_amount) as avg_order_value,
                    MAX(o.order_time) as last_order
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                WHERE o.restaurant_id = %s
                AND o.order_time BETWEEN %s AND %s
                GROUP BY c.customer_id
                ORDER BY total_spent DESC
                LIMIT 10
            """
            customer_data = execute_query(customer_query, (self.restaurant_id, start_date, end_date))
            
            if customer_data:
                self.customer_insights_table.setRowCount(len(customer_data))
                for i, customer in enumerate(customer_data):
                    self.customer_insights_table.setItem(i, 0, QTableWidgetItem(customer['name']))
                    self.customer_insights_table.setItem(i, 1, QTableWidgetItem(str(customer['order_count'])))
                    self.customer_insights_table.setItem(i, 2, QTableWidgetItem(f"AED {float(customer['total_spent']):.2f}"))
                    self.customer_insights_table.setItem(i, 3, QTableWidgetItem(f"AED {float(customer['avg_order_value']):.2f}"))
                    self.customer_insights_table.setItem(i, 4, QTableWidgetItem(customer['last_order'].strftime("%Y-%m-%d %H:%M")))
                    
        except Exception as e:
            print(f"Error refreshing restaurant analytics: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load analytics data: {str(e)}")
    
    def show_styled_message_box(self, icon, title, text, buttons=QMessageBox.StandardButton.Ok):
        """Show a styled message box that matches the app theme"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        
        # Apply dark theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        return msg_box.exec()

    def show_info_message(self, title, text):
        """Show styled information message"""
        return self.show_styled_message_box(QMessageBox.Icon.Information, title, text)
        
    def show_warning_message(self, title, text):
        """Show styled warning message"""
        return self.show_styled_message_box(QMessageBox.Icon.Warning, title, text)
        
    def show_error_message(self, title, text):
        """Show styled error message"""
        return self.show_styled_message_box(QMessageBox.Icon.Critical, title, text)
        
    def show_question_message(self, title, text):
        """Show styled question message with Yes/No buttons"""
        return self.show_styled_message_box(
            QMessageBox.Icon.Question, 
            title, 
            text, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
    
    def show_suspension_banner(self):
        """Show a red banner indicating account suspension"""
        # Create a red banner at the top of the dashboard
        banner = QFrame()
        banner.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin: 5px;
        """)
        banner_layout = QHBoxLayout(banner)
        
        warning_label = QLabel("⚠️ ACCOUNT SUSPENDED: Your restaurant is not visible to customers")
        warning_label.setStyleSheet("font-weight: bold; color: white;")
        
        contact_btn = QPushButton("Contact Support")
        contact_btn.setStyleSheet("""
            background-color: white;
            color: #e74c3c;
            border: none;
            padding: 5px 10px;
        """)
        
        banner_layout.addWidget(warning_label)
        banner_layout.addStretch()
        banner_layout.addWidget(contact_btn)
        
        # Find main layout and insert at the top
        main_layout = self.findChild(QHBoxLayout)
        if main_layout:
            # Get the widget that contains all content (usually a QStackedWidget)
            content_widget = None
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if item.widget() and not item.widget().objectName() == "sidebar":
                    content_widget = item.widget()
                    break
            
            if content_widget:
                # Find the content layout
                content_layout = content_widget.findChild(QVBoxLayout)
                if content_layout:
                    # Insert banner at the top
                    content_layout.insertWidget(0, banner)
    
    def load_restaurant_profile(self):
        # Get the restaurant profile for this user
        result = execute_query(
            "SELECT r.*, u.is_active FROM restaurants r JOIN users u ON r.user_id = u.user_id WHERE r.user_id = %s",
            (self.user.user_id,)
        )
        
        if result:
            self.restaurant_data = result[0]
            self.restaurant_id = self.restaurant_data['restaurant_id']
            
            # Update restaurant name in the sidebar
            self.update_restaurant_name()
            
            # Check if restaurant is suspended
            if 'is_active' in self.restaurant_data and not self.restaurant_data['is_active']:
                # Show suspension notice
                self.show_warning_message(
                    "Account Suspended",
                    "Your restaurant account has been suspended by the administrator. " +
                    "While you can still access your dashboard, your restaurant will not be visible to customers. " +
                    "Please contact support for assistance."
                )
                
                # Add a persistent suspension banner
                self.show_suspension_banner()
    
    def update_restaurant_name(self):
        """Update the restaurant name display in UI"""
        if hasattr(self, 'restaurant_name_label') and self.restaurant_data:
            restaurant_name = self.restaurant_data.get('name', 'Your Restaurant')
            self.restaurant_name_label.setText(restaurant_name)
    
    def show_profile_setup(self):
        """Show profile setup if restaurant doesn't exist yet"""
        self.show_info_message("Profile Setup", "Please set up your restaurant profile first")
        self.show_profile_page()
        
        # Pre-fill with defaults if fields are accessible
        if hasattr(self, 'profile_name'):
            self.profile_name.setText("Your Restaurant")
            # Set cuisine type to "Other" by default
            self.profile_cuisine.setCurrentText("Other")
    
    def load_profile_data(self):
        """Load restaurant data into profile form"""
        if not self.restaurant_data:
            return
        
        self.profile_name.setText(self.restaurant_data.get('name', ''))
        self.profile_address.setText(self.restaurant_data.get('address', ''))
        self.profile_contact.setText(self.restaurant_data.get('contact_number', ''))
        
        # Set cuisine type
        cuisine = self.restaurant_data.get('cuisine_type', 'Other')
        index = self.profile_cuisine.findText(cuisine)
        if index >= 0:
            self.profile_cuisine.setCurrentIndex(index)
        else:
            self.profile_cuisine.setCurrentText(cuisine)
        
        # Set advanced fields if available
        if 'opening_time' in self.restaurant_data and self.restaurant_data['opening_time']:
            self.profile_opening.setText(str(self.restaurant_data['opening_time']))
        
        if 'closing_time' in self.restaurant_data and self.restaurant_data['closing_time']:
            self.profile_closing.setText(str(self.restaurant_data['closing_time']))
        
        if 'delivery_radius' in self.restaurant_data and self.restaurant_data['delivery_radius']:
            self.profile_delivery_radius.setValue(self.restaurant_data['delivery_radius'])
        
        if 'min_order_amount' in self.restaurant_data and self.restaurant_data['min_order_amount']:
            self.profile_min_order.setValue(float(self.restaurant_data['min_order_amount']))
            
        # Update the restaurant name in the sidebar
        self.update_restaurant_name()
    
    def save_profile(self):
        """Save restaurant profile"""
        name = self.profile_name.text().strip()
        address = self.profile_address.text().strip()
        contact = self.profile_contact.text().strip()
        cuisine = self.profile_cuisine.currentText()
        opening_time = self.profile_opening.text().strip()
        closing_time = self.profile_closing.text().strip()
        delivery_radius = self.profile_delivery_radius.value()
        min_order_amount = self.profile_min_order.value()
        
        # Validate required fields only for manual saves
        if (not name or not address or not contact) and self._source_call != "load_profile":
            self.show_warning_message("Validation Error", "Please fill in all required fields")
            return
            
        # Use defaults if empty
        name = name or "Your Restaurant"
        address = address or ""
        contact = contact or ""
        
        try:
            if self.restaurant_id:  # Update existing
                query = """
                UPDATE restaurants 
                SET name = %s, address = %s, contact_number = %s, cuisine_type = %s,
                opening_time = %s, closing_time = %s, delivery_radius = %s, min_order_amount = %s
                WHERE restaurant_id = %s
                """
                params = (name, address, contact, cuisine, opening_time, closing_time,
                         delivery_radius, min_order_amount, self.restaurant_id)
            else:  # Create new
                query = """
                INSERT INTO restaurants 
                (user_id, name, address, contact_number, cuisine_type, rating, 
                opening_time, closing_time, delivery_radius, min_order_amount)
                VALUES (%s, %s, %s, %s, %s, 0.0, %s, %s, %s, %s)
                """
                params = (self.user.user_id, name, address, contact, cuisine,
                         opening_time, closing_time, delivery_radius, min_order_amount)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                # Only show success message for manual saves
                if self._source_call != "load_profile":
                    self.show_info_message("Success", "Restaurant profile saved successfully!")
                
                # Reload restaurant data
                self.load_restaurant_profile()
                
                # Update restaurant name in sidebar using our method
                self.update_restaurant_name()
                
                # If this was a new restaurant, enable menu management
                if not self.restaurant_id and self.restaurant_data:
                    self.restaurant_id = self.restaurant_data['restaurant_id']
                    self.load_menu_items()
                    self.load_categories()
            else:
                # Only show error for manual saves
                if self._source_call != "load_profile":
                    self.show_error_message("Error", "Failed to save profile")
                
        except Exception as e:
            # Only show error for manual saves
            if self._source_call != "load_profile":
                self.show_error_message("Error", f"An error occurred: {str(e)}")
                
        # Reset source call tracker
        self._source_call = None
    
    def load_menu_items(self):
        """Load menu items for the restaurant"""
        if not self.restaurant_id:
            return
            
        menu_items = execute_query(
            "SELECT * FROM menus WHERE restaurant_id = %s ORDER BY category, dish_name",
            (self.restaurant_id,)
        )
        
        self.menu_table.setRowCount(0)
        
        if not menu_items:
            return
        
        for row, item in enumerate(menu_items):
            self.menu_table.insertRow(row)
            self.menu_table.setItem(row, 0, QTableWidgetItem(str(item['menu_id'])))
            self.menu_table.setItem(row, 1, QTableWidgetItem(item['dish_name']))
            self.menu_table.setItem(row, 2, QTableWidgetItem(item['category']))
            
            # Format price
            price = f"{item['price']:.2f} AED"
            self.menu_table.setItem(row, 3, QTableWidgetItem(price))
            
            # Format discount price if exists
            discount = "-"
            if item['discount_price'] and float(item['discount_price']) > 0:
                discount = f"{item['discount_price']:.2f} AED"
            self.menu_table.setItem(row, 4, QTableWidgetItem(discount))
            
            # Stock and availability
            stock = f"{item['stock_quantity']} ({item['availability']})"
            self.menu_table.setItem(row, 5, QTableWidgetItem(stock))
            
            # Create buttons cell
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("action-button")
            edit_btn.clicked.connect(lambda checked, i=item: self.edit_menu_item(i))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("delete-button")
            delete_btn.clicked.connect(lambda checked, id=item['menu_id']: self.delete_menu_item(id))
            
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(delete_btn)
            
            self.menu_table.setCellWidget(row, 6, buttons_widget)
    
    def load_categories(self):
        """Load unique categories for filter dropdown"""
        if not self.restaurant_id:
            return
            
        categories = execute_query(
            "SELECT DISTINCT category FROM menus WHERE restaurant_id = %s ORDER BY category",
            (self.restaurant_id,)
        )
        
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        if categories:
            for category in categories:
                self.category_filter.addItem(category['category'])
    
    def filter_menu_items(self):
        """Filter menu items by category"""
        category = self.category_filter.currentText()
        
        if category == "All Categories":
            self.load_menu_items()
        else:
            menu_items = execute_query(
                "SELECT * FROM menus WHERE restaurant_id = %s AND category = %s ORDER BY dish_name",
                (self.restaurant_id, category)
            )
            
            self.menu_table.setRowCount(0)
            
            if not menu_items:
                return
                
            # The rest of the code is the same as load_menu_items
            for row, item in enumerate(menu_items):
                self.menu_table.insertRow(row)
                self.menu_table.setItem(row, 0, QTableWidgetItem(str(item['menu_id'])))
                self.menu_table.setItem(row, 1, QTableWidgetItem(item['dish_name']))
                self.menu_table.setItem(row, 2, QTableWidgetItem(item['category']))
                
                # Format price
                price = f"{item['price']:.2f} AED"
                self.menu_table.setItem(row, 3, QTableWidgetItem(price))
                
                # Format discount price if exists
                discount = "-"
                if item['discount_price'] and float(item['discount_price']) > 0:
                    discount = f"{item['discount_price']:.2f} AED"
                self.menu_table.setItem(row, 4, QTableWidgetItem(discount))
                
                # Stock and availability
                stock = f"{item['stock_quantity']} ({item['availability']})"
                self.menu_table.setItem(row, 5, QTableWidgetItem(stock))
                
                # Create buttons cell
                buttons_widget = QWidget()
                buttons_layout = QHBoxLayout(buttons_widget)
                buttons_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setObjectName("action-button")
                edit_btn.clicked.connect(lambda checked, i=item: self.edit_menu_item(i))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("delete-button")
                delete_btn.clicked.connect(lambda checked, id=item['menu_id']: self.delete_menu_item(id))
                
                buttons_layout.addWidget(edit_btn)
                buttons_layout.addWidget(delete_btn)
                
                self.menu_table.setCellWidget(row, 6, buttons_widget)
    
    def add_menu_item(self):
        """Add a new menu item"""
        if not self.restaurant_id:
            self.show_warning_message("Profile Required", "Please set up your restaurant profile first")
            self.show_profile_page()
            return
            
        dialog = MenuItemDialog(self, self.restaurant_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_menu_items()
            self.load_categories()
    
    def edit_menu_item(self, menu_item):
        """Edit an existing menu item"""
        dialog = MenuItemDialog(self, self.restaurant_id, menu_item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_menu_items()
    
    def delete_menu_item(self, menu_id):
        """Delete a menu item"""
        reply = self.show_question_message(
            "Confirm Deletion", 
            "Are you sure you want to delete this menu item?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM menus WHERE menu_id = %s",
                (menu_id,),
                fetch=False
            )
            
            if result is not None:
                self.show_info_message("Success", "Menu item deleted successfully")
                self.load_menu_items()
                self.load_categories()
            else:
                self.show_error_message("Error", "Failed to delete menu item")
    
    def show_dashboard(self):
        self.content_area.setCurrentWidget(self.dashboard_page)
        # Refresh dashboard stats
        self.load_dashboard_stats()
    
    def manage_orders(self):
        self.content_area.setCurrentWidget(self.orders_page)
        # Refresh orders when tab is visited
        self.load_all_orders()
    
    def manage_menu(self):
        if not self.restaurant_id:
            self.show_profile_setup()
        else:
            self.content_area.setCurrentWidget(self.menu_page)
            self.load_menu_items()
    
    def edit_profile(self):
        self.content_area.setCurrentWidget(self.profile_page)
    
    def show_profile_page(self):
        self.content_area.setCurrentWidget(self.profile_page)
    
    def view_reports(self):
        self.content_area.setCurrentWidget(self.reports_page)
        # Refresh analytics data when reports page is viewed
        if self.restaurant_id:
            self.refresh_restaurant_analytics()
    
    def logout(self):
        reply = self.show_question_message(
            "Confirm Logout", 
            "Are you sure you want to logout?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
    
    def load_dashboard_stats(self):
        """Load real-time statistics for the dashboard"""
        if not self.restaurant_id:
            return
            
        try:
            # Today's orders
            today_orders = execute_query("""
                SELECT COUNT(*) as count 
                FROM orders 
                WHERE restaurant_id = %s 
                  AND DATE(order_time) = CURRENT_DATE()
            """, (self.restaurant_id,))
            
            today_count = today_orders[0]['count'] if today_orders else 0
            self.stat_cards["today_orders"]["widget"].setText(str(today_count))
            
            # Pending orders
            pending_orders = execute_query("""
                SELECT COUNT(*) as count 
                FROM orders 
                WHERE restaurant_id = %s 
                  AND delivery_status IN ('Pending', 'Confirmed', 'Preparing')
            """, (self.restaurant_id,))
            
            pending_count = pending_orders[0]['count'] if pending_orders else 0
            self.stat_cards["pending_orders"]["widget"].setText(str(pending_count))
            
            # Menu items
            menu_items = execute_query("""
                SELECT COUNT(*) as count 
                FROM menus 
                WHERE restaurant_id = %s
            """, (self.restaurant_id,))
            
            menu_count = menu_items[0]['count'] if menu_items else 0
            self.stat_cards["menu_items"]["widget"].setText(str(menu_count))
            
            # Total sales
            total_sales = execute_query("""
                SELECT SUM(total_amount) as total 
                FROM orders 
                WHERE restaurant_id = %s 
                  AND delivery_status = 'Delivered'
            """, (self.restaurant_id,))
            
            sales_amount = total_sales[0]['total'] if total_sales and total_sales[0]['total'] else 0
            self.stat_cards["total_sales"]["widget"].setText(f"{float(sales_amount):.2f} AED")
            
            # Recent orders (last 5)
            self.recent_orders_table.setRowCount(0)
            
            recent_orders = execute_query("""
                SELECT o.order_id, o.order_number, o.customer_id, o.order_time, o.delivery_status, o.total_amount, 
                       c.name as customer_name, c.phone as customer_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.restaurant_id = %s
                ORDER BY o.order_time DESC
                LIMIT 5
            """, (self.restaurant_id,))
            
            if not recent_orders:
                self.recent_orders_table.setRowCount(1)
                no_orders = QTableWidgetItem("No orders found")
                no_orders.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.recent_orders_table.setSpan(0, 0, 1, 5)
                self.recent_orders_table.setItem(0, 0, no_orders)
                return
                
            self.recent_orders_table.setRowCount(len(recent_orders))
            
            for i, order in enumerate(recent_orders):
                # Use order_number if available, otherwise fall back to order_id
                order_display = order.get('order_number', '')
                if not order_display or order_display.strip() == '':
                    order_display = f"#{order['order_id']}"
                else:
                    order_display = f"#{order_display}"
                
                # Order number with timestamp
                order_id = QTableWidgetItem(order_display)
                order_time = order['order_time'].strftime("%m/%d %H:%M")
                order_id.setToolTip(order_time)
                
                # Customer
                customer = QTableWidgetItem(order['customer_name'])
                
                # Get order items summary (count of items)
                items_count = execute_query("""
                    SELECT SUM(quantity) as total_items
                    FROM order_items
                    WHERE order_id = %s
                """, (order['order_id'],))
                
                items_text = f"{items_count[0]['total_items']} items" if items_count and items_count[0]['total_items'] else "0 items"
                items = QTableWidgetItem(items_text)
                
                # Amount
                amount = QTableWidgetItem(f"{float(order['total_amount']):.2f} AED")
                
                # Status with color
                status = QTableWidgetItem(order['delivery_status'])
                
                if order['delivery_status'] == 'Delivered':
                    status.setForeground(Qt.GlobalColor.darkGreen)
                elif order['delivery_status'] == 'Cancelled':
                    status.setForeground(Qt.GlobalColor.red)
                elif order['delivery_status'] in ['Preparing', 'Ready for Pickup']:
                    status.setForeground(Qt.GlobalColor.blue)
                
                # Add to table
                self.recent_orders_table.setItem(i, 0, order_id)
                self.recent_orders_table.setItem(i, 1, customer)
                self.recent_orders_table.setItem(i, 2, items)
                self.recent_orders_table.setItem(i, 3, amount)
                self.recent_orders_table.setItem(i, 4, status)
                
        except Exception as e:
            print(f"Error loading dashboard stats: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load dashboard statistics: {str(e)}")

    def cancel_order(self, order_id):
        """Cancel an order and restore stock quantities"""
        try:
            # Get the order details for reference
            order_info = execute_query("SELECT order_number FROM orders WHERE order_id = %s", (order_id,))
            order_display = f"#{order_id}"
            if order_info and order_info[0].get('order_number'):
                order_display = f"#{order_info[0]['order_number']}"
            
            # Get all order items to restore stock
            order_items = execute_query("""
                SELECT oi.menu_id, oi.quantity 
                FROM order_items oi 
                WHERE oi.order_id = %s
            """, (order_id,))
            
            # Update order status to Cancelled
            status_query = "UPDATE orders SET delivery_status = 'Cancelled' WHERE order_id = %s"
            execute_query(status_query, (order_id,), fetch=False)
            
            # Restore stock for each item
            for item in order_items:
                menu_id = item['menu_id']
                quantity = item['quantity']
                
                # Get current stock
                current_stock = execute_query(
                    "SELECT stock_quantity FROM menus WHERE menu_id = %s", 
                    (menu_id,)
                )
                
                if current_stock:
                    new_stock = current_stock[0]['stock_quantity'] + quantity
                    
                    # Update stock
                    execute_query(
                        "UPDATE menus SET stock_quantity = %s WHERE menu_id = %s",
                        (new_stock, menu_id),
                        fetch=False
                    )
            
            # Refresh orders
            self.load_all_orders()
            
            # Also refresh dashboard stats
            self.load_dashboard_stats()
            
            self.show_info_message(
                "Order Cancelled",
                f"Order {order_display} has been cancelled and stock quantities have been restored."
            )
        except Exception as e:
            self.show_error_message(
                "Error",
                f"Failed to cancel order: {str(e)}"
            )
    
    def search_orders(self):
        """Search orders with the provided criteria"""
        search_term = self.orders_search_input.text().strip()
        start_date = self.orders_start_date.date().toString("yyyy-MM-dd")
        end_date = self.orders_end_date.date().toString("yyyy-MM-dd")
        
        # Clear existing orders
        for status, layout in self.order_layouts.items():
            # Clear layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Add "No orders" message to each tab initially
        for status, layout in self.order_layouts.items():
            no_orders = QLabel(f"No {status.lower()} orders")
            no_orders.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_orders)
        
        if not self.restaurant_id:
            return
        
        # Get all orders for this restaurant with search filters
        try:
            # Build the query with parameters
            query = """
                SELECT o.*, c.name as customer_name, c.phone as customer_phone
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.restaurant_id = %s
            """
            params = [self.restaurant_id]
            
            # Add date filters if provided
            if start_date:
                query += " AND DATE(o.order_time) >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(o.order_time) <= %s"
                params.append(end_date)
            
            # Add customer name search if provided
            if search_term:
                query += " AND c.name LIKE %s"
                params.append(f"%{search_term}%")
            
            # Add order by clause
            query += " ORDER BY o.order_time DESC"
            
            orders = execute_query(query, tuple(params))
            
            if not orders:
                return
            
            # Clear "No orders" messages
            for status, layout in self.order_layouts.items():
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            # Map order statuses to tab names
            status_map = {
                "Pending": "New",
                "Confirmed": "New",
                "Preparing": "Preparing", 
                "On Delivery": "Ready for Pickup",
                "Delivered": "Completed",
                "Cancelled": "Cancelled"
            }
            
            # Group by status
            for order in orders:
                # Map delivery_status to tab status
                tab_status = status_map.get(order['delivery_status'], "New")
                self.add_order_card(order, tab_status)
                
        except Exception as e:
            print(f"Error searching orders: {e}")
            QMessageBox.critical(self, "Error", f"Failed to search orders: {str(e)}")
    
    def auto_refresh(self):
        """Automatically refresh data based on current page"""
        try:
            # Skip refresh if mouse button is pressed to prevent click interference
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            if QApplication.mouseButtons() != Qt.MouseButton.NoButton:
                return
                
            current_widget = self.content_area.currentWidget()
            
            # Only refresh certain pages that need real-time updates
            if current_widget == self.orders_page:
                # Refresh all orders
                self.load_all_orders()
            elif current_widget == self.dashboard_page:
                # Refresh dashboard stats
                self.load_dashboard_stats()
        except Exception as e:
            # Silent exception handling for auto-refresh
            print(f"Auto-refresh error in restaurant dashboard: {e}")
            # Don't show error to user since this runs automatically

    def load_orders_for_tab(self, tab_status):
        """Load orders for a specific tab"""
        if not self.restaurant_id:
            return
            
        try:
            # Clear existing orders
            layout = self.order_layouts[tab_status]
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Map tab status to database status values
            status_db_map = {
                'New': "('Pending')",
                'Preparing': "('Confirmed', 'Preparing')",
                'Ready for Pickup': "('On Delivery')",
                'Completed': "('Delivered')",
                'Cancelled': "('Cancelled')"
            }
            
            # Get status values for the query
            status_clause = status_db_map.get(tab_status, "('Pending')")
            
            # Get orders with the appropriate status
            query = f"""
                SELECT o.*, c.name as customer_name, c.phone as customer_phone, dp.name as delivery_person_name
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.delivery_person_id
                WHERE o.restaurant_id = %s
                AND o.delivery_status IN {status_clause}
                ORDER BY o.order_time DESC
            """
            
            orders = execute_query(query, (self.restaurant_id,))
            
            if not orders:
                no_orders = QLabel(f"No {tab_status.lower()} orders")
                no_orders.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_orders)
                return
            
            # Add orders to the tab
            for order in orders:
                self.add_order_card(order, tab_status)
                
        except Exception as e:
            self.show_error_message("Error", f"Failed to load orders: {str(e)}")


class MenuItemDialog(QDialog):
    def __init__(self, parent=None, restaurant_id=None, menu_item=None):
        super().__init__(parent)
        self.restaurant_id = restaurant_id
        self.menu_item = menu_item
        self.parent = parent
        
        self.setWindowTitle("Add Menu Item" if not menu_item else "Edit Menu Item")
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Menu Item Details")
        header_label.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form container with white background
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(12)
        
        # Dish name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter dish name")
        if self.menu_item:
            self.name_input.setText(self.menu_item['dish_name'])
        
        # Description field
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Enter dish description")
        if self.menu_item and self.menu_item['description']:
            self.description_input.setText(self.menu_item['description'])
        
        # Category field
        self.category_input = QComboBox()
        categories = ["Main Course", "Appetizer", "Dessert", "Beverage", "Side Dish", 
                     "Pizza", "Pasta", "Burger", "Salad", "Breakfast", "Lunch", "Dinner"]
        self.category_input.addItems(categories)
        self.category_input.setEditable(True)
        if self.menu_item:
            index = self.category_input.findText(self.menu_item['category'])
            if index >= 0:
                self.category_input.setCurrentIndex(index)
            else:
                self.category_input.setCurrentText(self.menu_item['category'])
        
        # Price field
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(1000)
        self.price_input.setSingleStep(0.50)
        self.price_input.setPrefix("AED ")
        if self.menu_item:
            self.price_input.setValue(float(self.menu_item['price']))
        
        # Discount price field
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(1000)
        self.discount_input.setSingleStep(0.50)
        self.discount_input.setPrefix("AED ")
        if self.menu_item and self.menu_item['discount_price']:
            self.discount_input.setValue(float(self.menu_item['discount_price']))
        
        # Stock quantity
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(1000)
        if self.menu_item:
            self.stock_input.setValue(self.menu_item['stock_quantity'])
        else:
            self.stock_input.setValue(10)  # Default
        
        # Availability
        self.availability_input = QComboBox()
        self.availability_input.addItems(["In Stock", "Out of Stock"])
        if self.menu_item:
            index = self.availability_input.findText(self.menu_item['availability'])
            if index >= 0:
                self.availability_input.setCurrentIndex(index)
        
        # Add fields to form
        form_layout.addRow("Dish Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Price:", self.price_input)
        form_layout.addRow("Discount Price:", self.discount_input)
        form_layout.addRow("Stock Quantity:", self.stock_input)
        form_layout.addRow("Availability:", self.availability_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("save-btn")
        save_btn.clicked.connect(self.save_menu_item)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel-btn")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        # Add to main layout
        main_layout.addWidget(header_label)
        main_layout.addWidget(form_container)
        main_layout.addLayout(button_layout)
    
    def save_menu_item(self):
        # Validate input
        name = self.name_input.text().strip()
        if not name:
            self.show_warning_message("Validation Error", "Please enter a dish name")
            return
            
        # Get all the values
        description = self.description_input.toPlainText().strip()
        price = self.price_input.value()
        discount_price = self.discount_input.value() if self.discount_input.value() > 0 else None
        category = self.category_input.currentText()
        preparation_time = self.prep_time_input.value()
        stock_quantity = self.stock_input.value()
        
        # Special dietary options
        is_vegetarian = self.vegetarian_input.isChecked()
        is_vegan = self.vegan_input.isChecked()
        is_gluten_free = self.gluten_free_input.isChecked()
        
        # Determine availability based on stock
        availability = "In Stock" if stock_quantity > 0 else "Out of Stock"
        
        try:
            # Prepare the query based on whether we're adding or editing
            if self.menu_item:
                # Update existing menu item
                query = """
                UPDATE menus 
                SET dish_name = %s, description = %s, price = %s, discount_price = %s,
                    category = %s, preparation_time = %s, is_vegetarian = %s,
                    is_vegan = %s, is_gluten_free = %s, availability = %s,
                    stock_quantity = %s
                WHERE menu_id = %s
                """
                params = (name, description, price, discount_price, category, 
                         preparation_time, is_vegetarian, is_vegan, is_gluten_free,
                         availability, stock_quantity, self.menu_item['menu_id'])
            else:
                # Insert new menu item
                query = """
                INSERT INTO menus (restaurant_id, dish_name, description, price, discount_price,
                                 category, preparation_time, is_vegetarian, is_vegan,
                                 is_gluten_free, availability, stock_quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.restaurant_id, name, description, price, discount_price,
                         category, preparation_time, is_vegetarian, is_vegan,
                         is_gluten_free, availability, stock_quantity)
            
            # Execute the query
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                self.show_info_message("Success", 
                                  "Menu item updated successfully" if self.menu_item else "Menu item added successfully")
                self.accept()
            else:
                self.show_error_message("Error", "Failed to save menu item")
                
        except Exception as e:
            self.show_error_message("Error", f"An error occurred: {str(e)}")
    
    def show_styled_message_box(self, icon, title, text):
        """Show a styled message box that matches the app theme"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        # Apply dark theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        return msg_box.exec()
        
    def show_warning_message(self, title, text):
        """Show styled warning message"""
        return self.show_styled_message_box(QMessageBox.Icon.Warning, title, text)
        
    def show_info_message(self, title, text):
        """Show styled information message"""
        return self.show_styled_message_box(QMessageBox.Icon.Information, title, text)
        
    def show_error_message(self, title, text):
        """Show styled error message"""
        return self.show_styled_message_box(QMessageBox.Icon.Critical, title, text)