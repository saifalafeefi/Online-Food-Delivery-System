from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                            QSizePolicy, QSpacerItem, QStackedWidget, QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                            QLineEdit, QComboBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from db_utils import execute_query

class DeliveryDashboard(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        # Initialize delivery person properties
        self.delivery_person_id = None
        self.delivery_person_info = None
        self.is_available = False
        self._source_call = None  # Track source of method calls
        self.initUI()
        # Load delivery person info after UI is initialized
        self.load_delivery_person_info()
    
    def load_delivery_person_info(self):
        """Load delivery person information from database"""
        try:
            result = execute_query(
                "SELECT * FROM delivery_personnel WHERE user_id = %s",
                (self.user.user_id,)
            )
            
            if result:
                self.delivery_person_info = result[0]
                self.delivery_person_id = result[0]['delivery_person_id']
                
                # Set status
                self.is_available = result[0]['status'] == 'Available'
                
                # Update status button if it exists
                if hasattr(self, 'status_btn'):
                    if self.is_available:
                        self.status_btn.setText("🟢 Available")
                        self.status_btn.setStyleSheet("background-color: #27ae60;")
                    else:
                        self.status_btn.setText("🔴 Unavailable")
                        self.status_btn.setStyleSheet("background-color: #c0392b;")
                
                # Update profile fields if they exist
                if hasattr(self, 'name_input') and hasattr(self, 'phone_input'):
                    self.name_input.setText(self.delivery_person_info['name'])
                    self.phone_input.setText(self.delivery_person_info['phone'])
                    
                    # Set vehicle type radio buttons if they exist
                    if hasattr(self, 'light_vehicle') and hasattr(self, 'heavy_vehicle'):
                        vehicle_type = self.delivery_person_info.get('vehicle_type', 'Light Vehicle - Automatic')
                        
                        # Set vehicle size
                        if "Light Vehicle" in vehicle_type:
                            self.light_vehicle.setChecked(True)
                        else:
                            self.heavy_vehicle.setChecked(True)
                        
                        # Set transmission type
                        if "Automatic" in vehicle_type:
                            self.automatic.setChecked(True)
                        else:
                            self.manual.setChecked(True)
            else:
                # Create a basic profile with defaults
                if hasattr(self, 'name_input') and hasattr(self, 'phone_input'):
                    self.name_input.setText(self.user.username)
                    self.light_vehicle.setChecked(True)
                    self.automatic.setChecked(True)
                
                # Create a basic profile record if none exists
                self._source_call = "load_profile"
                self.save_profile()
                
        except Exception as e:
            print(f"Error loading delivery person info: {e}")
            # Create an empty profile if not found
            self.delivery_person_info = None
            self.delivery_person_id = None
            self.is_available = False
    
    def initUI(self):
        """Initialize the UI components"""
        self.setWindowTitle("Food Delivery - Delivery Dashboard")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to fix white box
        main_layout.setSpacing(0)
        
        # Sidebar for navigation
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
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
        
        self.profile_pic = QLabel()
        self.profile_pic.setObjectName("profile-pic")
        self.profile_pic.setPixmap(QPixmap("assets/img/delivery-avatar.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(self.profile_pic)
        
        welcome_label = QLabel(f"Welcome, {self.user.username}")
        welcome_label.setObjectName("welcome-label")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Status toggle button
        self.status_btn = QPushButton("Available")
        self.status_btn.setObjectName("status-button")
        if self.is_available:
            self.status_btn.setText("🟢 Available")
            self.status_btn.setStyleSheet("background-color: #27ae60;")
        else:
            self.status_btn.setText("🔴 Unavailable")
            self.status_btn.setStyleSheet("background-color: #c0392b;")
        self.status_btn.clicked.connect(self.toggle_status)
        
        user_info_layout.addWidget(image_container)
        user_info_layout.addWidget(welcome_label)
        user_info_layout.addWidget(self.status_btn)
        sidebar_layout.addWidget(user_info)
        
        # Navigation buttons
        nav_buttons = [
            {"text": "New Orders", "icon": "🔔", "slot": self.show_new_orders},
            {"text": "Active Deliveries", "icon": "🚚", "slot": self.show_active_deliveries},
            {"text": "Delivery History", "icon": "📜", "slot": self.show_delivery_history},
            {"text": "My Profile", "icon": "👤", "slot": self.show_profile},
            {"text": "Earnings", "icon": "💰", "slot": self.show_earnings}
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
        
        # Create all pages
        self.new_orders_page = self.create_new_orders_page()
        self.active_deliveries_page = self.create_active_deliveries_page()
        self.delivery_history_page = self.create_delivery_history_page()
        self.profile_page = self.create_profile_page()
        self.earnings_page = self.create_earnings_page()
        
        # Add pages to content area
        self.content_area.addWidget(self.new_orders_page)
        self.content_area.addWidget(self.active_deliveries_page)
        self.content_area.addWidget(self.delivery_history_page)
        self.content_area.addWidget(self.profile_page)
        self.content_area.addWidget(self.earnings_page)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        # Set default page to new orders
        self.show_new_orders()
        
        # Apply stylesheets
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
            }
            #sidebar {
                background-color: #2c3e50;
                color: white;
                border: none;
            }
            #user-info {
                padding: 10px;
                border-bottom: 1px solid #34495e;
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
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
                background-color: transparent;
            }
            #nav-button {
                text-align: left;
                padding: 12px 15px;
                margin: 4px 0;
                border: none;
                border-radius: 4px;
                background-color: transparent;
                color: white;
                font-size: 16px;
            }
            #nav-button:hover {
                background-color: #34495e;
            }
            #logout-button {
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
            }
            #logout-button:hover {
                background-color: #c0392b;
            }
            #page-header {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
            }
            QFrame#order-card {
                background-color: white;
                border-radius: 8px;
                margin: 10px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            QPushButton#accept-button {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#accept-button:hover {
                background-color: #2ecc71;
            }
            QPushButton#complete-button {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#complete-button:hover {
                background-color: #2980b9;
            }
        """)
    
    def show_new_orders(self):
        self.content_area.setCurrentWidget(self.new_orders_page)
        self.load_new_orders()
    
    def show_active_deliveries(self):
        self.content_area.setCurrentWidget(self.active_deliveries_page)
        self.load_active_deliveries()
    
    def show_delivery_history(self):
        self.content_area.setCurrentWidget(self.delivery_history_page)
        self.load_delivery_history()
    
    def show_profile(self):
        self.content_area.setCurrentWidget(self.profile_page)
    
    def show_earnings(self):
        self.content_area.setCurrentWidget(self.earnings_page)
        self.load_earnings()
    
    def toggle_status(self):
        """Toggle availability status for delivery person"""
        self.is_available = not self.is_available
        
        if not self.delivery_person_id:
            QMessageBox.warning(self, "Profile Required", "Please complete your profile first.")
            return
        
        status = "Available" if self.is_available else "Assigned"
        
        # Update status in database
        query = """
        UPDATE delivery_personnel 
        SET status = %s 
        WHERE delivery_person_id = %s
        """
        result = execute_query(query, (status, self.delivery_person_id), fetch=False)
        
        if result is not None:
            if self.is_available:
                self.status_btn.setText("🟢 Available")
                self.status_btn.setStyleSheet("background-color: #27ae60;")
            else:
                self.status_btn.setText("🔴 Unavailable")
                self.status_btn.setStyleSheet("background-color: #c0392b;")
        else:
            QMessageBox.warning(self, "Error", "Failed to update status. Please try again.")
            # Revert toggle
            self.is_available = not self.is_available
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
    
    def load_new_orders(self):
        """Load new orders ready for pickup"""
        # Clear existing orders
        while self.new_orders_layout.count():
            item = self.new_orders_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        try:
            # Get orders ready for pickup
            orders = execute_query("""
                SELECT o.*, r.name as restaurant_name, r.address as restaurant_address,
                      c.name as customer_name, c.address as customer_address,
                      c.phone as customer_phone
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_status = 'Ready for Pickup' AND o.delivery_person_id IS NULL
                ORDER BY o.order_time ASC
            """)
            
            if not orders:
                no_orders = QLabel("No orders available for pickup at this time.")
                no_orders.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.new_orders_layout.addWidget(no_orders)
                return
            
            # Create order cards
            for order in orders:
                order_card = self._create_order_card(order, is_new=True)
                self.new_orders_layout.addWidget(order_card)
        
        except Exception as e:
            print(f"Error loading new orders: {e}")
            error_label = QLabel(f"Error loading orders: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.new_orders_layout.addWidget(error_label)
    
    def _create_order_card(self, order, is_new=False, is_active=False):
        """Create a card UI for an order"""
        card = QFrame()
        card.setObjectName("order-card")
        card_layout = QVBoxLayout(card)
        
        # Header with order ID and time
        header = QLabel(f"Order #{order['order_id']} - {order['order_time'].strftime('%Y-%m-%d %H:%M')}")
        header.setObjectName("order-header")
        
        # Restaurant and customer info
        restaurant = QLabel(f"Restaurant: {order['restaurant_name']}")
        restaurant_address = QLabel(f"Address: {order['restaurant_address']}")
        
        customer = QLabel(f"Customer: {order['customer_name']}")
        customer_address = QLabel(f"Delivery to: {order['customer_address']}")
        customer_phone = QLabel(f"Phone: {order['customer_phone']}")
        
        # Amount
        amount = QLabel(f"Order Total: ${float(order['total_amount']):.2f}")
        amount.setObjectName("order-amount")
        
        # Add to layout
        card_layout.addWidget(header)
        card_layout.addWidget(restaurant)
        card_layout.addWidget(restaurant_address)
        card_layout.addWidget(QLabel("")) # Spacer
        card_layout.addWidget(customer)
        card_layout.addWidget(customer_address)
        card_layout.addWidget(customer_phone)
        card_layout.addWidget(QLabel("")) # Spacer
        card_layout.addWidget(amount)
        
        # Add action button based on card type
        if is_new:
            accept_btn = QPushButton("Accept Delivery")
            accept_btn.setObjectName("accept-button")
            accept_btn.clicked.connect(lambda: self.accept_order(order['order_id']))
            card_layout.addWidget(accept_btn)
        elif is_active:
            complete_btn = QPushButton("Complete Delivery")
            complete_btn.setObjectName("complete-button")
            complete_btn.clicked.connect(lambda: self.complete_delivery(order['order_id']))
            card_layout.addWidget(complete_btn)
        
        return card
    
    def accept_order(self, order_id):
        """Accept an order for delivery"""
        try:
            # Update order status and assign delivery person
            query = """
            UPDATE orders 
            SET delivery_status = 'Out for Delivery', delivery_person_id = %s
            WHERE order_id = %s
            """
            result = execute_query(query, (self.delivery_person_id, order_id), fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", "Order accepted for delivery")
                # Refresh pages
                self.load_new_orders()
                self.load_active_deliveries()
                self.show_active_deliveries()
            else:
                QMessageBox.critical(self, "Error", "Failed to accept order")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def load_active_deliveries(self):
        """Load active deliveries for the delivery person"""
        # Clear existing deliveries
        while self.active_deliveries_layout.count():
            item = self.active_deliveries_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.delivery_person_id:
            no_deliveries = QLabel("No active deliveries.")
            no_deliveries.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.active_deliveries_layout.addWidget(no_deliveries)
            return
        
        try:
            # Get active deliveries
            orders = execute_query("""
                SELECT o.*, r.name as restaurant_name, r.address as restaurant_address,
                      c.name as customer_name, c.address as customer_address,
                      c.phone as customer_phone
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_person_id = %s AND o.delivery_status = 'Out for Delivery'
                ORDER BY o.order_time ASC
            """, (self.delivery_person_id,))
            
            if not orders:
                no_deliveries = QLabel("No active deliveries.")
                no_deliveries.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.active_deliveries_layout.addWidget(no_deliveries)
                return
            
            # Create delivery cards
            for order in orders:
                order_card = self._create_order_card(order, is_new=False)
                self.active_deliveries_layout.addWidget(order_card)
                
        except Exception as e:
            print(f"Error loading active deliveries: {e}")
            error_label = QLabel(f"Error loading deliveries: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.active_deliveries_layout.addWidget(error_label)
    
    def complete_delivery(self, order_id):
        """Mark delivery as completed"""
        try:
            # Update order status
            query = """
            UPDATE orders 
            SET delivery_status = 'Delivered', actual_delivery_time = NOW()
            WHERE order_id = %s
            """
            result = execute_query(query, (order_id,), fetch=False)
            
            if result is not None:
                QMessageBox.information(self, "Success", "Delivery marked as completed")
                # Update delivery person status if needed
                query = """
                UPDATE delivery_personnel 
                SET total_deliveries = total_deliveries + 1
                WHERE delivery_person_id = %s
                """
                execute_query(query, (self.delivery_person_id,), fetch=False)
                
                # Refresh pages
                self.load_active_deliveries()
                self.load_delivery_history()
                self.load_earnings()
            else:
                QMessageBox.critical(self, "Error", "Failed to complete delivery")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def load_earnings(self):
        """Load earnings for delivery person"""
        if not self.delivery_person_id:
            self.total_earnings_value.setText("$0.00")
            self.total_deliveries_value.setText("0")
            self.avg_rating_value.setText("N/A")
            return
        
        try:
            # Get total deliveries and earnings
            earnings = execute_query("""
                SELECT COUNT(*) as delivery_count, SUM(total_amount) as total_earnings
                FROM orders
                WHERE delivery_person_id = %s AND delivery_status = 'Delivered'
            """, (self.delivery_person_id,))
            
            if not earnings or earnings[0]['delivery_count'] == 0:
                self.total_earnings_value.setText("$0.00")
                self.total_deliveries_value.setText("0")
                self.avg_rating_value.setText("N/A")
                return
            
            # Calculate earnings (10% of total order value)
            delivery_count = earnings[0]['delivery_count']
            total_earnings = earnings[0]['total_earnings'] * 0.10 if earnings[0]['total_earnings'] else 0
            
            # Set values
            self.total_earnings_value.setText(f"${total_earnings:.2f}")
            self.total_deliveries_value.setText(str(delivery_count))
            
            # Get average rating if available
            ratings = execute_query("""
                SELECT AVG(delivery_rating) as avg_rating
                FROM ratings
                WHERE delivery_person_id = %s
            """, (self.delivery_person_id,))
            
            if ratings and ratings[0]['avg_rating']:
                self.avg_rating_value.setText(f"{ratings[0]['avg_rating']:.1f} / 5.0")
            else:
                self.avg_rating_value.setText("N/A")
                
        except Exception as e:
            print(f"Error loading earnings: {e}")
            self.total_earnings_value.setText("Error")
            self.total_deliveries_value.setText("Error")
            self.avg_rating_value.setText("Error")
    
    def load_delivery_history(self):
        """Load delivery history for the delivery person"""
        # Clear existing history
        self.history_table.setRowCount(0)
        
        if not self.delivery_person_id:
            return
        
        try:
            # Get delivery history
            orders = execute_query("""
                SELECT o.order_id, o.order_time, o.total_amount, 
                       r.name as restaurant_name, c.name as customer_name
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_person_id = %s AND o.delivery_status = 'Delivered'
                ORDER BY o.order_time DESC
            """, (self.delivery_person_id,))
            
            if not orders:
                return
            
            # Add to table
            self.history_table.setRowCount(len(orders))
            
            for i, order in enumerate(orders):
                order_id = QTableWidgetItem(str(order['order_id']))
                date = QTableWidgetItem(order['order_time'].strftime("%Y-%m-%d %H:%M"))
                restaurant = QTableWidgetItem(order['restaurant_name'])
                customer = QTableWidgetItem(order['customer_name'])
                amount = QTableWidgetItem(f"${float(order['total_amount']):.2f}")
                
                self.history_table.setItem(i, 0, order_id)
                self.history_table.setItem(i, 1, date)
                self.history_table.setItem(i, 2, restaurant)
                self.history_table.setItem(i, 3, customer)
                self.history_table.setItem(i, 4, amount)
        except Exception as e:
            print(f"Error loading delivery history: {e}")
    
    def create_new_orders_page(self):
        """Create page for new orders available for pickup"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Available Orders")
        header.setObjectName("page-header")
        
        # Orders scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        self.new_orders_layout = QVBoxLayout(scroll_content)
        self.new_orders_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.clicked.connect(self.load_new_orders)
        
        # Add to layout
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(scroll_area)
        
        return page
    
    def create_active_deliveries_page(self):
        """Create page for active deliveries"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Active Deliveries")
        header.setObjectName("page-header")
        
        # Active deliveries scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        self.active_deliveries_layout = QVBoxLayout(scroll_content)
        self.active_deliveries_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Deliveries")
        refresh_btn.clicked.connect(self.load_active_deliveries)
        
        # Add to layout
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(scroll_area)
        
        return page
    
    def create_delivery_history_page(self):
        """Create page for delivery history"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("Delivery History")
        header.setObjectName("page-header")
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Order ID", "Date", "Restaurant", "Customer", "Amount"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.clicked.connect(self.load_delivery_history)
        
        # Add to layout
        layout.addWidget(header)
        layout.addWidget(refresh_btn)
        layout.addWidget(self.history_table)
        
        return page
    
    def create_profile_page(self):
        """Create profile page for delivery personnel"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Profile header
        header = QLabel("My Profile")
        header.setObjectName("page-header")
        
        # Profile form container
        form_container = QFrame()
        form_container.setObjectName("profile-card")
        form_layout = QVBoxLayout(form_container)
        
        # Input fields
        input_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        # Vehicle type selection
        vehicle_container = QWidget()
        vehicle_layout = QVBoxLayout(vehicle_container)
        
        # Vehicle size options
        size_label = QLabel("Vehicle Size:")
        self.vehicle_size_group = QButtonGroup(self)
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.setContentsMargins(0, 0, 0, 0)
        
        self.light_vehicle = QRadioButton("Light Vehicle")
        self.heavy_vehicle = QRadioButton("Heavy Vehicle")
        self.vehicle_size_group.addButton(self.light_vehicle, 1)
        self.vehicle_size_group.addButton(self.heavy_vehicle, 2)
        
        size_layout.addWidget(self.light_vehicle)
        size_layout.addWidget(self.heavy_vehicle)
        
        # Transmission options
        trans_label = QLabel("Transmission:")
        self.transmission_group = QButtonGroup(self)
        trans_widget = QWidget()
        trans_layout = QHBoxLayout(trans_widget)
        trans_layout.setContentsMargins(0, 0, 0, 0)
        
        self.automatic = QRadioButton("Automatic")
        self.manual = QRadioButton("Manual")
        self.transmission_group.addButton(self.automatic, 1)
        self.transmission_group.addButton(self.manual, 2)
        
        trans_layout.addWidget(self.automatic)
        trans_layout.addWidget(self.manual)
        
        # Default selections
        self.light_vehicle.setChecked(True)
        self.automatic.setChecked(True)
        
        # Add vehicle options to layout
        vehicle_layout.addWidget(size_label)
        vehicle_layout.addWidget(size_widget)
        vehicle_layout.addWidget(trans_label)
        vehicle_layout.addWidget(trans_widget)
        
        # Save button
        save_btn = QPushButton("Save Profile")
        save_btn.clicked.connect(self.save_profile)
        
        # Add fields to form
        input_layout.addRow("Name:", self.name_input)
        input_layout.addRow("Phone:", self.phone_input)
        input_layout.addRow("Vehicle:", vehicle_container)
        
        # Add to container
        form_layout.addLayout(input_layout)
        form_layout.addWidget(save_btn)
        
        # Add to main layout
        layout.addWidget(header)
        layout.addWidget(form_container)
        
        return page
    
    def create_earnings_page(self):
        """Create earnings page"""
        page = QWidget()
        self.earnings_layout = QVBoxLayout(page)
        
        # Header
        header = QLabel("My Earnings")
        header.setObjectName("page-header")
        
        # Earnings summary
        summary_frame = QFrame()
        summary_layout = QGridLayout(summary_frame)
        
        # Total earnings
        total_label = QLabel("Total Earnings:")
        total_label.setObjectName("total-earnings-label")
        self.total_earnings_value = QLabel("$0.00")
        self.total_earnings_value.setObjectName("total-earnings-value")
        
        summary_layout.addWidget(total_label, 0, 0)
        summary_layout.addWidget(self.total_earnings_value, 0, 1)
        
        # Total deliveries
        deliveries_label = QLabel("Total Deliveries:")
        deliveries_label.setObjectName("total-deliveries-label")
        self.total_deliveries_value = QLabel("0")
        self.total_deliveries_value.setObjectName("total-deliveries-value")
        
        summary_layout.addWidget(deliveries_label, 1, 0)
        summary_layout.addWidget(self.total_deliveries_value, 1, 1)
        
        # Average rating
        rating_label = QLabel("Average Rating:")
        rating_label.setObjectName("average-rating-label")
        self.avg_rating_value = QLabel("N/A")
        self.avg_rating_value.setObjectName("average-rating-value")
        
        summary_layout.addWidget(rating_label, 2, 0)
        summary_layout.addWidget(self.avg_rating_value, 2, 1)
        
        # Recent earnings table
        earnings_label = QLabel("Earnings Details")
        earnings_label.setObjectName("section-header")
        
        self.earnings_table = QTableWidget()
        self.earnings_table.setColumnCount(4)
        self.earnings_table.setHorizontalHeaderLabels(["Order ID", "Date", "Restaurant", "Amount"])
        self.earnings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Earnings")
        refresh_btn.clicked.connect(self.load_earnings)
        
        # Add to layout
        self.earnings_layout.addWidget(header)
        self.earnings_layout.addWidget(summary_frame)
        self.earnings_layout.addWidget(earnings_label)
        self.earnings_layout.addWidget(self.earnings_table)
        self.earnings_layout.addWidget(refresh_btn)
        
        return page
    
    def save_profile(self):
        """Save delivery person profile"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        # Only show warning if this is a manual save
        if (not name or not phone) and self._source_call != "load_profile":
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return
            
        # Use defaults if empty
        name = name or self.user.username
        phone = phone or ""
        
        # Get vehicle type
        vehicle_size = "Light Vehicle" if self.light_vehicle.isChecked() else "Heavy Vehicle"
        transmission = "Automatic" if self.automatic.isChecked() else "Manual"
        vehicle_type = f"{vehicle_size} - {transmission}"
        
        try:
            if self.delivery_person_id:
                # Update existing profile
                query = """
                UPDATE delivery_personnel 
                SET name = %s, phone = %s, vehicle_type = %s
                WHERE delivery_person_id = %s
                """
                params = (name, phone, vehicle_type, self.delivery_person_id)
            else:
                # Create new profile
                query = """
                INSERT INTO delivery_personnel (user_id, name, phone, status, vehicle_type)
                VALUES (%s, %s, %s, 'Available', %s)
                """
                params = (self.user.user_id, name, phone, vehicle_type)
            
            result = execute_query(query, params, fetch=False)
            
            if result is not None:
                # Only show success message for manual saves
                if self._source_call != "load_profile":
                    QMessageBox.information(self, "Success", "Profile saved successfully")
                
                # If this was a new profile, load the new ID
                if not self.delivery_person_id:
                    # Avoid infinite recursion by just getting the ID
                    new_id_result = execute_query(
                        "SELECT delivery_person_id FROM delivery_personnel WHERE user_id = %s",
                        (self.user.user_id,)
                    )
                    if new_id_result:
                        self.delivery_person_id = new_id_result[0]['delivery_person_id']
                        self.is_available = True  # New profiles are available by default
                        
                        # Update status button
                        if hasattr(self, 'status_btn'):
                            self.status_btn.setText("🟢 Available")
                            self.status_btn.setStyleSheet("background-color: #27ae60;")
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