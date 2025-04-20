from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                             QSizePolicy, QSpacerItem, QStackedWidget, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QSpinBox, QDialog, QFormLayout, QTextEdit, QLineEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from db_utils import execute_query

class RestaurantView(QWidget):
    back_to_restaurants = Signal()
    add_to_cart = Signal(dict, int)  # Menu item, quantity
    
    def __init__(self, restaurant_id, parent=None):
        super().__init__(parent)
        self.restaurant_id = restaurant_id
        self.restaurant_data = None
        self.menu_items = []
        self.load_restaurant_data()
        self.initUI()
    
    def load_restaurant_data(self):
        # Load restaurant details
        result = execute_query(
            "SELECT * FROM restaurants WHERE restaurant_id = %s",
            (self.restaurant_id,)
        )
        if result:
            self.restaurant_data = result[0]
        
        # Load ALL menu items, regardless of stock status
        self.menu_items = execute_query(
            "SELECT * FROM menus WHERE restaurant_id = %s ORDER BY category, dish_name",
            (self.restaurant_id,)
        ) or []
    
    def initUI(self):
        if not self.restaurant_data:
            error_layout = QVBoxLayout(self)
            error_label = QLabel("Restaurant not found")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_layout.addWidget(error_label)
            return
        
        self.setWindowTitle(f"Food Delivery - {self.restaurant_data['name']}")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("restaurant-header")
        header_layout = QVBoxLayout(header_frame)
        
        # Back button
        back_btn = QPushButton("← Back to Restaurants")
        back_btn.setObjectName("back-button")
        back_btn.clicked.connect(self.back_to_restaurants.emit)
        
        # Restaurant name and info
        name_label = QLabel(self.restaurant_data['name'])
        name_label.setObjectName("restaurant-name")
        name_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        info_label = QLabel(f"{self.restaurant_data['cuisine_type']} • {self.restaurant_data['address']}")
        info_label.setObjectName("restaurant-info")
        
        # Rating
        rating = execute_query("""
            SELECT AVG(food_rating) as avg_rating, COUNT(*) as total_ratings
            FROM ratings
            WHERE restaurant_id = %s
        """, (self.restaurant_id,))
        
        rating_text = "No ratings yet"
        if rating and rating[0]['avg_rating']:
            rating_text = f"★ {rating[0]['avg_rating']:.1f} ({rating[0]['total_ratings']} ratings)"
        
        rating_label = QLabel(rating_text)
        rating_label.setObjectName("restaurant-rating")
        
        # Minimum order amount
        min_order_text = "No minimum order"
        if self.restaurant_data.get('min_order_amount') and float(self.restaurant_data['min_order_amount']) > 0:
            min_order_text = f"Minimum Order: AED {float(self.restaurant_data['min_order_amount']):.2f}"
        
        min_order_label = QLabel(min_order_text)
        min_order_label.setObjectName("min-order-amount")
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(name_label)
        header_layout.addWidget(info_label)
        header_layout.addWidget(rating_label)
        header_layout.addWidget(min_order_label)
        
        # Menu section
        menu_label = QLabel("Menu")
        menu_label.setObjectName("section-header")
        menu_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        # Search bar for menu items
        search_layout = QHBoxLayout()
        self.menu_search_input = QLineEdit()
        self.menu_search_input.setPlaceholderText("Search menu by dish name or ingredients...")
        self.menu_search_input.setObjectName("menu-search")
        
        category_filter = QComboBox()
        category_filter.addItem("All Categories")
        
        # Populate category filter
        categories_set = set()
        for item in self.menu_items:
            if item['category']:
                categories_set.add(item['category'])
        
        for category in sorted(categories_set):
            category_filter.addItem(category)
        
        self.category_filter = category_filter
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("action-button")
        search_btn.clicked.connect(self.filter_menu_items)
        
        search_layout.addWidget(self.menu_search_input, 3)
        search_layout.addWidget(self.category_filter, 2) 
        search_layout.addWidget(search_btn, 1)
        
        # Scroll area for menu items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add all widgets to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(menu_label)
        main_layout.addLayout(search_layout)
        
        # Initially display all menu items
        self.display_menu_items(self.menu_items)
        
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Apply styles
        self.setStyleSheet("""
            #restaurant-header {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
            #back-button {
                background-color: transparent;
                color: #3498db;
                border: none;
                padding: 5px 0;
                text-align: left;
                font-weight: bold;
            }
            #restaurant-name {
                margin-top: 10px;
                color: #2c3e50;
            }
            #restaurant-info {
                color: #7f8c8d;
                font-size: 14px;
            }
            #restaurant-rating {
                color: #f39c12;
                font-weight: bold;
                font-size: 16px;
                margin-top: 5px;
            }
            #min-order-amount {
                color: #e74c3c;
                font-weight: bold;
                font-size: 14px;
                margin-top: 5px;
            }
            #category-frame {
                margin-bottom: 20px;
            }
            #category-label {
                color: #2c3e50;
                border-bottom: 1px solid #ecf0f1;
                padding-bottom: 5px;
            }
            #menu-item {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #ecf0f1;
            }
            #menu-item:hover {
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            #item-name {
                color: #2c3e50;
            }
            #item-description {
                color: #7f8c8d;
                font-size: 13px;
                margin-top: 5px;
            }
            #item-price {
                color: #27ae60;
                font-weight: bold;
                margin-top: 10px;
            }
            #quantity-input {
                width: 60px;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            #add-to-cart-button {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                margin-top: 5px;
            }
            #add-to-cart-button:hover {
                background-color: #2980b9;
            }
            #menu-search {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 15px;
            }
        """)

    def filter_menu_items(self):
        """Filter menu items based on search criteria"""
        search_text = self.menu_search_input.text().lower()
        selected_category = self.category_filter.currentText()
        
        # If no filters are applied, show all items
        if not search_text and selected_category == "All Categories":
            self.display_menu_items(self.menu_items)
            return
        
        # Filter items based on search criteria
        filtered_items = []
        for item in self.menu_items:
            # Check if item matches search text
            text_match = True
            if search_text:
                item_name = item['dish_name'].lower() if item['dish_name'] else ""
                item_desc = item['description'].lower() if item['description'] else ""
                text_match = search_text in item_name or search_text in item_desc
            
            # Check if item matches selected category
            category_match = True
            if selected_category != "All Categories":
                category_match = item['category'] == selected_category
            
            # Add item if it matches all criteria
            if text_match and category_match:
                filtered_items.append(item)
        
        # Display filtered items
        self.display_menu_items(filtered_items)

    def display_menu_items(self, items):
        """Display menu items in the scroll area"""
        # Clear existing content
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # If no items to display
        if not items:
            empty_label = QLabel("No menu items found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return
        
        # Group menu items by category
        categories = {}
        for item in items:
            if item['category'] not in categories:
                categories[item['category']] = []
            categories[item['category']].append(item)
        
        # Add menu items by category
        for category, category_items in categories.items():
            category_frame = QFrame()
            category_frame.setObjectName("category-frame")
            category_layout = QVBoxLayout(category_frame)
            
            # Category label
            category_label = QLabel(category)
            category_label.setObjectName("category-label")
            category_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            category_layout.addWidget(category_label)
            
            # Add menu items for this category
            for item in category_items:
                item_frame = QFrame()
                item_frame.setObjectName("menu-item")
                item_layout = QHBoxLayout(item_frame)
                
                # Item details
                details_layout = QVBoxLayout()
                
                name = QLabel(item['dish_name'])
                name.setObjectName("item-name")
                name.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                
                description = QLabel(item['description'] or "")
                description.setObjectName("item-description")
                description.setWordWrap(True)
                
                price_text = f"{item['price']:.2f} AED"
                if item['discount_price']:
                    price_text = f"<s>{item['price']:.2f} AED</s> {item['discount_price']:.2f} AED"
                
                price = QLabel(price_text)
                price.setObjectName("item-price")
                
                # Stock status
                stock_status = QLabel(f"Available: {item['stock_quantity']}")
                stock_status.setObjectName("stock-status")
                stock_status.setStyleSheet("color: #27ae60;" if item['stock_quantity'] > 0 else "color: #e74c3c;")
                
                details_layout.addWidget(name)
                details_layout.addWidget(description)
                details_layout.addWidget(price)
                details_layout.addWidget(stock_status)
                
                # Add to cart controls
                add_layout = QVBoxLayout()
                
                quantity = QSpinBox()
                quantity.setObjectName("quantity-input")
                quantity.setMinimum(1)
                quantity.setMaximum(item['stock_quantity'] if item['stock_quantity'] > 0 else 0)
                quantity.setValue(1)
                
                add_btn = QPushButton("Add to Cart")
                add_btn.setObjectName("add-to-cart-button")
                add_btn.clicked.connect(lambda _, item=item, qty=quantity: self.handle_add_to_cart(item, qty))
                
                # Disable button and set grey style if out of stock
                if item['stock_quantity'] <= 0:
                    add_btn.setEnabled(False)
                    add_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #95a5a6;
                            color: white;
                            border-radius: 4px;
                            padding: 8px;
                            font-weight: bold;
                        }
                    """)
                
                add_layout.addWidget(quantity)
                add_layout.addWidget(add_btn)
                add_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Add to item frame
                item_layout.addLayout(details_layout, 7)
                item_layout.addLayout(add_layout, 3)
                
                category_layout.addWidget(item_frame)
            
            self.scroll_layout.addWidget(category_frame)
        
        self.scroll_layout.addStretch()
    
    def handle_add_to_cart(self, menu_item, quantity_spinbox):
        quantity = quantity_spinbox.value()
        
        # Check if item is in stock
        if menu_item['stock_quantity'] <= 0:
            QMessageBox.warning(
                self,
                "Out of Stock",
                f"Sorry, {menu_item['dish_name']} is currently out of stock."
            )
            return
        
        # Check if requested quantity exceeds available stock
        if quantity > menu_item['stock_quantity']:
            QMessageBox.warning(
                self,
                "Insufficient Stock",
                f"Sorry, only {menu_item['stock_quantity']} {menu_item['dish_name']} available."
            )
            return
        
        # Only emit the signal if we pass all checks
        self.add_to_cart.emit(menu_item, quantity) 