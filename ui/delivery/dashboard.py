from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                             QSizePolicy, QSpacerItem, QStackedWidget, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QLineEdit, QComboBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from db_utils import execute_query
from datetime import datetime
import os

class DeliveryDashboard(QWidget):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        # Initialize delivery person properties
        self.delivery_person_id = None
        self.delivery_person_info = None
        self.is_available = False
        self._source_call = None  # Track source of method calls
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(500)  # Refresh every 0.5 seconds
        
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
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Profile Required")
            msg.setText("Please complete your profile first.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2c3e50;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            msg.exec()
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
        """Load new orders that are ready for pickup and not assigned"""
        try:
            self.clear_new_orders_layout()
            
            if not hasattr(self, "user") or not self.user:
                self.display_no_orders_message(self.new_orders_container, "No user information available")
                return
            
            # Get delivery person info
            if not self.delivery_person_id:
                self.display_no_orders_message(self.new_orders_container, "No delivery profile found. Please update your profile.")
                return
            
            # Get vehicle type
            vehicle_query = "SELECT vehicle_type FROM delivery_personnel WHERE delivery_person_id = %s"
            vehicle_result = execute_query(vehicle_query, (self.delivery_person_id,))
            
            if not vehicle_result:
                self.display_no_orders_message(self.new_orders_container, "Could not retrieve vehicle information.")
                return
            
            vehicle_type = vehicle_result[0]['vehicle_type']
            
            # Get orders that are ready for pickup and not assigned
            query = """
                SELECT o.order_id, o.order_date, 
                       r.name as restaurant_name, r.address as restaurant_address, 
                       c.name as customer_name, c.address as customer_address, c.phone as customer_phone, 
                       o.total_amount 
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_status = 'On Delivery'
                AND o.delivery_person_id IS NULL
                ORDER BY o.order_date DESC
            """
            
            orders = execute_query(query)
            
            if not orders:
                self.display_no_orders_message(self.new_orders_container, "No new orders available for pickup")
                return
            
            # Add each order to the layout
            for order in orders:
                order_card = self.create_new_order_card(
                    order['order_id'],
                    order['order_date'],
                    order['restaurant_name'],
                    order['restaurant_address'],
                    order['customer_name'],
                    order['customer_address'],
                    order['customer_phone'],
                    order['total_amount']
                )
                if order_card:  # Only add if card was created successfully
                    self.new_orders_layout.addWidget(order_card)
            
        except Exception as e:
            self.display_no_orders_message(self.new_orders_container, f"Error loading orders: {str(e)}")
            print(f"Error loading new orders: {str(e)}")
    
    def load_active_deliveries(self):
        """Load active deliveries for the current delivery person"""
        try:
            self.clear_active_deliveries_layout()
            
            if not hasattr(self, "user") or not self.user:
                self.display_no_orders_message(self.active_deliveries_container, "No user information available")
                return
            
            # Get delivery person info
            if not self.delivery_person_id:
                self.display_no_orders_message(self.active_deliveries_container, "No delivery profile found. Please update your profile.")
                return
            
            # Get orders assigned to this delivery person that are on delivery
            query = """
                SELECT o.order_id, o.order_date, 
                       r.name as restaurant_name, r.address as restaurant_address, 
                       c.name as customer_name, c.address as customer_address, c.phone as customer_phone, 
                       o.total_amount 
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_status = 'On Delivery'
                AND o.delivery_person_id = %s
                ORDER BY o.order_date DESC
            """
            deliveries = execute_query(query, (self.delivery_person_id,))
            
            if not deliveries:
                self.display_no_orders_message(self.active_deliveries_container, "No active deliveries")
                return
            
            # Add each delivery to the layout
            for delivery in deliveries:
                order_id = delivery['order_id']
                order_date = delivery['order_date']
                restaurant_name = delivery['restaurant_name']
                restaurant_address = delivery['restaurant_address']
                customer_name = delivery['customer_name']
                customer_address = delivery['customer_address']
                customer_phone = delivery['customer_phone']
                total_amount = delivery['total_amount']
                
                # Format the date for better readability
                try:
                    date_obj = datetime.strptime(str(order_date), "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    date_obj = datetime.now()
                
                delivery_card = self.create_active_delivery_card(
                    order_id, date_obj, restaurant_name, restaurant_address,
                    customer_name, customer_address, customer_phone, total_amount
                )
                self.active_deliveries_layout.addWidget(delivery_card)
                
        except Exception as e:
            self.display_no_orders_message(self.active_deliveries_container, f"Error loading deliveries: {str(e)}")
            print(f"Error loading active deliveries: {str(e)}")
    
    def load_earnings(self):
        """Load earnings for delivery person"""
        if not self.delivery_person_id:
            self.total_earnings_value.setText("0 AED")
            self.total_deliveries_value.setText("0")
            self.avg_rating_value.setText("N/A")
            
            # Clear earnings table
            self.earnings_table.setRowCount(0)
            return
        
        try:
            # Get total deliveries and earnings
            earnings = execute_query("""
                SELECT COUNT(*) as delivery_count, SUM(total_amount) as total_earnings
                FROM orders
                WHERE delivery_person_id = %s AND delivery_status = 'Delivered'
            """, (self.delivery_person_id,))
            
            if not earnings or earnings[0]['delivery_count'] == 0:
                self.total_earnings_value.setText("0 AED")
                self.total_deliveries_value.setText("0")
                self.avg_rating_value.setText("N/A")
                
                # Clear earnings table
                self.earnings_table.setRowCount(0)
                return
            
            # Calculate earnings (10% of total order value in AED)
            delivery_count = earnings[0]['delivery_count']
            total_earnings = float(earnings[0]['total_earnings'] or 0) * 0.10 * 3.67  # Convert to AED
            
            # Set values
            self.total_earnings_value.setText(f"{total_earnings:.2f} AED")
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
            
            # Populate earnings table with completed deliveries
            completed_deliveries = execute_query("""
                SELECT o.order_id, o.order_date, o.actual_delivery_time, 
                       r.name as restaurant_name, o.total_amount
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                WHERE o.delivery_person_id = %s AND o.delivery_status = 'Delivered'
                ORDER BY o.actual_delivery_time DESC
            """, (self.delivery_person_id,))
            
            if completed_deliveries:
                # Clear table
                self.earnings_table.setRowCount(0)
                
                # Set row count
                self.earnings_table.setRowCount(len(completed_deliveries))
                
                # Fill table with data
                for row, delivery in enumerate(completed_deliveries):
                    # Format date
                    try:
                        date_obj = datetime.strptime(str(delivery['order_date']), "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%b %d, %Y")
                    except:
                        formatted_date = str(delivery['order_date'])
                    
                    # Calculate delivery fee (10% of order total)
                    fee = float(delivery['total_amount']) * 0.10 * 3.67  # Convert to AED
                    
                    # Add data to table
                    self.earnings_table.setItem(row, 0, QTableWidgetItem(str(delivery['order_id'])))
                    self.earnings_table.setItem(row, 1, QTableWidgetItem(formatted_date))
                    self.earnings_table.setItem(row, 2, QTableWidgetItem(delivery['restaurant_name']))
                    self.earnings_table.setItem(row, 3, QTableWidgetItem(f"{fee:.2f} AED"))
            else:
                # Clear table if no deliveries
                self.earnings_table.setRowCount(0)
                
        except Exception as e:
            print(f"Error loading earnings: {e}")
            self.total_earnings_value.setText("Error")
            self.total_deliveries_value.setText("Error")
            self.avg_rating_value.setText("Error")
            self.earnings_table.setRowCount(0)
    
    def load_delivery_history(self):
        """Load delivery history for the current delivery person"""
        try:
            self.clear_delivery_history_layout()
            
            if not hasattr(self, "user") or not self.user:
                self.display_no_orders_message(self.delivery_history_container, "No user information available")
                return
            
            # Get delivery person info
            if not self.delivery_person_id:
                self.display_no_orders_message(self.delivery_history_container, "No delivery profile found. Please update your profile.")
                return
            
            # Get completed deliveries for this delivery person
            query = """
                SELECT o.order_id, o.order_date, r.name as restaurant_name, c.name as customer_name, o.total_amount 
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.delivery_status = 'Delivered'
                AND o.delivery_person_id = %s
                ORDER BY o.order_date DESC
            """
            history = execute_query(query, (self.delivery_person_id,))
            
            if not history:
                self.display_no_orders_message(self.delivery_history_container, "No delivery history found")
                return
            
            # Create a table to display delivery history
            table = QTableWidget()
            table.setObjectName("delivery-history-table")
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Order ID", "Date", "Restaurant", "Customer", "Amount"])
            table.setRowCount(len(history))
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                QHeaderView::section {
                    background-color: #f2f2f2;
                    padding: 5px;
                    border: 1px solid #ddd;
                    font-weight: bold;
                }
                QTableWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #eee;
                }
            """)
            
            # Populate the table with delivery history
            for row, delivery in enumerate(history):
                order_id = delivery['order_id']
                order_date = delivery['order_date']
                restaurant_name = delivery['restaurant_name']
                customer_name = delivery['customer_name']
                total_amount = delivery['total_amount']
                
                # Format the date for better readability
                try:
                    date_obj = datetime.strptime(str(order_date), "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%b %d, %Y %I:%M %p")
                except (ValueError, TypeError) as e:
                    print(f"Date formatting error: {e}, using original date")
                    formatted_date = str(order_date)
                
                # Format the amount with currency symbol
                try:
                    formatted_amount = f"{float(total_amount):.2f} AED"
                except (ValueError, TypeError):
                    formatted_amount = f"0 AED"
                
                table.setItem(row, 0, QTableWidgetItem(str(order_id)))
                table.setItem(row, 1, QTableWidgetItem(formatted_date))
                table.setItem(row, 2, QTableWidgetItem(restaurant_name))
                table.setItem(row, 3, QTableWidgetItem(customer_name))
                table.setItem(row, 4, QTableWidgetItem(formatted_amount))
            
            self.delivery_history_layout.addWidget(table)
            
        except Exception as e:
            self.display_no_orders_message(self.delivery_history_container, f"Error loading delivery history: {str(e)}")
            print(f"Error loading delivery history: {str(e)}")
    
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
        scroll_content.setObjectName("new-orders-container")
        self.new_orders_container = scroll_content
        
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
        scroll_content.setObjectName("active-deliveries-container")
        self.active_deliveries_container = scroll_content
        
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
        """Create the delivery history page showing completed deliveries"""
        # Create main container
        container = QWidget()
        container.setObjectName("delivery-history-page")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Delivery History")
        title.setObjectName("page-title")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refresh-btn")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_btn.clicked.connect(self.load_delivery_history)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        # Create scroll area for history
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f9f9f9;
            }
        """)
        
        # Container for delivery history content
        self.delivery_history_container = QWidget()
        self.delivery_history_layout = QVBoxLayout(self.delivery_history_container)
        self.delivery_history_layout.setContentsMargins(20, 20, 20, 20)
        self.delivery_history_layout.setSpacing(20)
        
        scroll_area.setWidget(self.delivery_history_container)
        
        # Add to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(scroll_area)
        
        return container
    
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
        self.total_earnings_value = QLabel("0 AED")
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
    
    def clear_new_orders_layout(self):
        """Clear all widgets from the new orders layout"""
        if hasattr(self, 'new_orders_layout'):
            while self.new_orders_layout.count():
                item = self.new_orders_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def clear_active_deliveries_layout(self):
        """Clear all widgets from the active deliveries layout"""
        if hasattr(self, 'active_deliveries_layout'):
            while self.active_deliveries_layout.count():
                item = self.active_deliveries_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def display_no_orders_message(self, container, message):
        """Display a message when no orders are available"""
        # Create a label with the message
        label = QLabel(message)
        label.setObjectName("no-orders-label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 16px;
            color: #666;
            padding: 20px;
        """)
        
        # Add it to the appropriate layout
        if container == self.new_orders_container:
            self.clear_new_orders_layout()
            self.new_orders_layout.addWidget(label)
        elif container == self.active_deliveries_container:
            self.clear_active_deliveries_layout()
            self.active_deliveries_layout.addWidget(label)
        elif container == self.delivery_history_container:
            self.clear_delivery_history_layout()
            self.delivery_history_layout.addWidget(label)
    
    def create_new_order_card(self, order_id, order_date, restaurant_name, restaurant_address, customer_name, customer_address, customer_phone, total_amount):
        """Create a card for a new order"""
        try:
            # Format the date
            if isinstance(order_date, datetime):
                formatted_date = order_date.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_date = str(order_date)
            
            # Create the card widget
            card = QWidget()
            card.setObjectName("order-card")
            card.setStyleSheet("""
                #order-card {
                    background-color: white;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            # Order header
            header_layout = QHBoxLayout()
            order_label = QLabel(f"Order #{order_id}")
            order_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            date_label = QLabel(formatted_date)
            date_label.setStyleSheet("color: #666;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            header_layout.addWidget(order_label)
            header_layout.addWidget(date_label)
            card_layout.addLayout(header_layout)
            
            # Restaurant & Customer info
            info_layout = QGridLayout()
            info_layout.addWidget(QLabel("Restaurant:"), 0, 0)
            info_layout.addWidget(QLabel(restaurant_name), 0, 1)
            info_layout.addWidget(QLabel("Customer:"), 1, 0)
            info_layout.addWidget(QLabel(customer_name), 1, 1)
            
            # Delivery address
            info_layout.addWidget(QLabel("Delivery Address:"), 2, 0)
            address = f"{restaurant_address} → {customer_address}"
            info_layout.addWidget(QLabel(address), 2, 1)
            
            # Amount
            info_layout.addWidget(QLabel("Amount:"), 3, 0)
            info_layout.addWidget(QLabel(f"{float(total_amount) * 3.67:.2f} AED"), 3, 1)
            
            card_layout.addLayout(info_layout)
            
            # Accept button
            accept_btn = QPushButton("Accept Delivery")
            accept_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            accept_btn.clicked.connect(lambda: self.accept_delivery(order_id))
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(accept_btn)
            card_layout.addLayout(button_layout)
            
            return card
        except Exception as e:
            print(f"Error creating order card: {e}")
            return None
    
    def create_active_delivery_card(self, order_id, order_date, restaurant_name, restaurant_address, customer_name, customer_address, customer_phone, total_amount):
        """Create a card for an active delivery"""
        try:
            # Format the date
            if isinstance(order_date, datetime):
                formatted_date = order_date.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_date = str(order_date)
            
            # Create the card widget
            card = QWidget()
            card.setObjectName("delivery-card")
            card.setStyleSheet("""
                #delivery-card {
                    background-color: white;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            # Order header
            header_layout = QHBoxLayout()
            order_label = QLabel(f"Order #{order_id}")
            order_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            date_label = QLabel(formatted_date)
            date_label.setStyleSheet("color: #666;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            header_layout.addWidget(order_label)
            header_layout.addWidget(date_label)
            card_layout.addLayout(header_layout)
            
            # Restaurant & Customer info
            info_layout = QGridLayout()
            info_layout.addWidget(QLabel("Restaurant:"), 0, 0)
            info_layout.addWidget(QLabel(restaurant_name), 0, 1)
            info_layout.addWidget(QLabel("Customer:"), 1, 0)
            info_layout.addWidget(QLabel(customer_name), 1, 1)
            
            # Delivery address
            info_layout.addWidget(QLabel("Delivery Address:"), 2, 0)
            address = f"{restaurant_address} → {customer_address}"
            info_layout.addWidget(QLabel(address), 2, 1)
            
            # Amount
            info_layout.addWidget(QLabel("Amount:"), 3, 0)
            info_layout.addWidget(QLabel(f"{float(total_amount) * 3.67:.2f} AED"), 3, 1)
            
            card_layout.addLayout(info_layout)
            
            # Complete button
            complete_btn = QPushButton("Complete Delivery")
            complete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            complete_btn.clicked.connect(lambda: self.complete_delivery(order_id))
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(complete_btn)
            card_layout.addLayout(button_layout)
            
            return card
        except Exception as e:
            print(f"Error creating delivery card: {e}")
            return None
    
    def accept_delivery(self, order_id):
        """Accept a delivery order"""
        try:
            if not self.delivery_person_id:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Error")
                msg.setText("Delivery personnel profile not found!")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
                return
            
            # Update the order status and assign the delivery person
            query = """
                UPDATE orders 
                SET delivery_status = %s, delivery_person_id = %s 
                WHERE order_id = %s
            """
            result = execute_query(query, ("On Delivery", self.delivery_person_id, order_id), fetch=False)
            
            if result is not None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Order #{order_id} accepted for delivery!")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
                
                # Refresh the orders
                self.load_new_orders()
                self.load_active_deliveries()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Error")
                msg.setText("Failed to update order. Please try again.")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to accept delivery: {str(e)}")
    
    def complete_delivery(self, order_id):
        """Mark a delivery as completed"""
        try:
            # First check the payment method
            payment_query = """
                SELECT payment_method, payment_status FROM orders 
                WHERE order_id = %s
            """
            payment_info = execute_query(payment_query, (order_id,))
            
            if not payment_info:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Error")
                msg.setText("Could not retrieve order information.")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
                return
                
            # Always update payment status to 'Paid' for ALL delivery methods when order is completed
            # This ensures consistency across the system
            query = """
                UPDATE orders 
                SET delivery_status = %s, 
                    actual_delivery_time = NOW(),
                    payment_status = 'Paid'
                WHERE order_id = %s
            """
            
            result = execute_query(query, ("Delivered", order_id), fetch=False)
            
            if result is not None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Order #{order_id} marked as delivered!")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
                
                # Refresh the orders
                self.load_active_deliveries()
                self.load_delivery_history()
                self.load_earnings()  # Update earnings
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Error")
                msg.setText("Failed to update order. Please try again.")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2c3e50;
                    }
                    QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to complete delivery: {str(e)}")
    
    def clear_delivery_history_layout(self):
        """Clear all widgets from the delivery history layout"""
        if hasattr(self, 'delivery_history_layout') and self.delivery_history_layout:
            while self.delivery_history_layout.count():
                item = self.delivery_history_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def auto_refresh(self):
        """Automatically refresh data based on current page"""
        try:
            # Skip refresh if mouse button is pressed to prevent click interference
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            if QApplication.mouseButtons() != Qt.MouseButton.NoButton:
                return
            
            # Skip if no delivery person ID is set yet
            if not self.delivery_person_id:
                return
                
            current_widget = self.content_area.currentWidget()
            
            # For real-time sensitive pages, refresh every cycle
            if current_widget == self.new_orders_page:
                # New orders should refresh in real-time
                self.load_new_orders()
            elif current_widget == self.active_deliveries_page:
                # Active deliveries should also refresh in real-time
                self.load_active_deliveries()
            elif current_widget == self.delivery_history_page or current_widget == self.earnings_page:
                # These pages change less frequently, so refresh them less often
                if not hasattr(self, '_slow_refresh_counter'):
                    self._slow_refresh_counter = 0
                
                self._slow_refresh_counter += 1
                if self._slow_refresh_counter >= 10:  # Refresh every 5 seconds (10 * 0.5s)
                    self._slow_refresh_counter = 0
                    
                    if current_widget == self.delivery_history_page:
                        self.load_delivery_history()
                    elif current_widget == self.earnings_page:
                        self.load_earnings()
        except Exception as e:
            # Silent exception handling for auto-refresh
            print(f"Auto-refresh error in delivery dashboard: {e}")
            # Don't show error to user since this runs automatically