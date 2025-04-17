from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                             QSizePolicy, QSpacerItem, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QMessageBox, QSpinBox, QTextEdit,
                             QDoubleSpinBox, QTabWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from db_utils import execute_query

class RestaurantDashboard(QWidget):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.restaurant_id = None
        self.restaurant_data = None
        self._source_call = None  # Track source of method calls
        self.order_layouts = {
            "New": None,
            "Preparing": None,
            "Ready for Pickup": None,
            "Completed": None,
            "Cancelled": None
        }
        self.initUI()
        # Load restaurant profile after UI initialization
        self.load_restaurant_profile()
        if self.restaurant_data:
            self.load_profile_data()
            # Load dashboard stats if restaurant exists
            self.load_dashboard_stats()
            # Start with dashboard
            self.show_dashboard()
        else:
            # Only show profile setup if no restaurant exists
            self.show_profile_setup()
    
    def load_restaurant_profile(self):
        # Get the restaurant profile for this user
        result = execute_query(
            "SELECT * FROM restaurants WHERE user_id = %s",
            (self.user.user_id,)
        )
        
        if result:
            self.restaurant_data = result[0]
            self.restaurant_id = self.restaurant_data['restaurant_id']
    
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
        
        restaurant_name = "Your Restaurant"
        if self.restaurant_data:
            restaurant_name = self.restaurant_data['name']
        
        welcome_label = QLabel(f"Welcome, {self.user.username}")
        welcome_label.setObjectName("welcome-label")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        restaurant_label = QLabel(restaurant_name)
        restaurant_label.setObjectName("restaurant-name")
        
        user_info_layout.addWidget(welcome_label)
        user_info_layout.addWidget(restaurant_label)
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
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setObjectName("action-button")
        refresh_btn.clicked.connect(self.load_all_orders)
        
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
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
            orders = execute_query("""
                SELECT o.*, c.name as customer_name, c.phone as customer_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.restaurant_id = %s
                ORDER BY o.order_time DESC
            """, (self.restaurant_id,))
            
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
        
        order_id_label = QLabel(f"Order #{order['order_id']}")
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
                buttons_layout.addWidget(reject_btn)
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
        
        # Regular status update for non-cancelled orders
        try:
            query = "UPDATE orders SET delivery_status = %s WHERE order_id = %s"
            result = execute_query(query, (db_status, order_id), fetch=False)
            
            if result is not None:
                print(f"Order #{order_id} status updated to {db_status} successfully")
                QMessageBox.information(self, "Success", f"Order #{order_id} status updated to {new_status}")
                # Refresh orders
                self.load_all_orders()
                # Also refresh dashboard stats when order status changes
                self.load_dashboard_stats()
            else:
                print(f"Failed to update Order #{order_id} status to {db_status}")
                QMessageBox.warning(self, "Error", "Failed to update order status")
        except Exception as e:
            print(f"Error updating order status: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update order status: {str(e)}")
    
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
        
        # Header
        header = QLabel("Reports and Analytics")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 20))
        
        # Placeholder content
        placeholder = QLabel("Reports functionality will be available soon!")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(header)
        layout.addWidget(placeholder)
        layout.addStretch()
        
        return page
    
    def show_profile_setup(self):
        """Show profile setup if restaurant doesn't exist yet"""
        QMessageBox.information(self, "Profile Setup", "Please set up your restaurant profile first")
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
        
        # Set advanced fields if available
        if 'opening_time' in self.restaurant_data and self.restaurant_data['opening_time']:
            self.profile_opening.setText(str(self.restaurant_data['opening_time']))
        
        if 'closing_time' in self.restaurant_data and self.restaurant_data['closing_time']:
            self.profile_closing.setText(str(self.restaurant_data['closing_time']))
        
        if 'delivery_radius' in self.restaurant_data and self.restaurant_data['delivery_radius']:
            self.profile_delivery_radius.setValue(self.restaurant_data['delivery_radius'])
        
        if 'min_order_amount' in self.restaurant_data and self.restaurant_data['min_order_amount']:
            self.profile_min_order.setValue(float(self.restaurant_data['min_order_amount']))
    
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
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields")
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
                    QMessageBox.information(self, "Success", "Restaurant profile saved successfully!")
                
                # Reload restaurant data
                self.load_restaurant_profile()
                
                # Update restaurant name in sidebar
                sidebar_welcome = self.findChild(QLabel, "restaurant-name")
                if sidebar_welcome and self.restaurant_data:
                    sidebar_welcome.setText(self.restaurant_data['name'])
                
                # If this was a new restaurant, enable menu management
                if not self.restaurant_id and self.restaurant_data:
                    self.restaurant_id = self.restaurant_data['restaurant_id']
                    self.load_menu_items()
                    self.load_categories()
            else:
                # Only show error for manual saves
                if self._source_call != "load_profile":
                    QMessageBox.critical(self, "Error", "Failed to save profile")
                
        except Exception as e:
            # Only show error for manual saves
            if self._source_call != "load_profile":
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                
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
            QMessageBox.warning(self, "Profile Required", "Please set up your restaurant profile first")
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
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this menu item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM menus WHERE menu_id = %s",
                (menu_id,),
                fetch=False
            )
            
            if result is not None:
                QMessageBox.information(self, "Success", "Menu item deleted successfully")
                self.load_menu_items()
                self.load_categories()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete menu item")
    
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
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
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
                SELECT o.order_id, c.name as customer_name, o.total_amount, o.delivery_status, o.order_time
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
                # Order ID with timestamp
                order_id = QTableWidgetItem(f"#{order['order_id']}")
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
        """Cancel an order and restore stock"""
        try:
            # Get order items first
            items = execute_query("""
                SELECT menu_id, quantity 
                FROM order_items 
                WHERE order_id = %s
            """, (order_id,))
            
            # Restore stock for each item
            for item in items:
                execute_query("""
                    UPDATE menus 
                    SET stock_quantity = stock_quantity + %s,
                        availability = CASE 
                            WHEN stock_quantity + %s > 0 THEN 'In Stock' 
                            ELSE availability 
                        END
                    WHERE menu_id = %s
                """, (item['quantity'], item['quantity'], item['menu_id']), fetch=False)
            
            # Update order status - Fixed column name from order_status to delivery_status
            execute_query("""
                UPDATE orders 
                SET delivery_status = 'Cancelled' 
                WHERE order_id = %s
            """, (order_id,), fetch=False)
            
            # Refresh orders
            self.load_all_orders()
            
            # Also refresh dashboard stats
            self.load_dashboard_stats()
            
            QMessageBox.information(
                self,
                "Order Cancelled",
                "Order has been cancelled and stock quantities have been restored."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to cancel order: {str(e)}"
            )


class MenuItemDialog(QDialog):
    def __init__(self, parent=None, restaurant_id=None, menu_item=None):
        super().__init__(parent)
        self.restaurant_id = restaurant_id
        self.menu_item = menu_item
        self.setWindowTitle("Add Menu Item" if not menu_item else "Edit Menu Item")
        self.setMinimumWidth(500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Dish name field
        self.name_input = QLineEdit()
        if self.menu_item:
            self.name_input.setText(self.menu_item['dish_name'])
        
        # Description field
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
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
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_menu_item)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
    
    def save_menu_item(self):
        # Validate input
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        category = self.category_input.currentText()
        price = self.price_input.value()
        discount_price = self.discount_input.value() if self.discount_input.value() > 0 else None
        stock = self.stock_input.value()
        
        # Automatically set availability based on stock
        availability = "In Stock" if stock > 0 else "Out of Stock"
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a dish name")
            return
        
        try:
            if self.menu_item:  # Update existing
                query = """
                UPDATE menus 
                SET dish_name = %s, description = %s, category = %s, price = %s,
                discount_price = %s, stock_quantity = %s, availability = %s
                WHERE menu_id = %s
                """
                params = (name, description, category, price, discount_price, 
                        stock, availability, self.menu_item['menu_id'])
            else:  # Add new
                query = """
                INSERT INTO menus 
                (restaurant_id, dish_name, description, category, price, 
                discount_price, stock_quantity, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.restaurant_id, name, description, category, 
                        price, discount_price, stock, availability)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", 
                                      "Menu item updated successfully" if self.menu_item else "Menu item added successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save menu item")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}") 