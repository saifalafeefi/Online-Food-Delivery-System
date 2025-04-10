from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QScrollArea, QFrame, QGridLayout, 
                            QSizePolicy, QSpacerItem, QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from db_utils import execute_query

class RestaurantView(QWidget):
    back_to_restaurants = pyqtSignal()
    add_to_cart = pyqtSignal(dict, int)  # Menu item, quantity
    
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
        
        # Load menu items
        self.menu_items = execute_query(
            "SELECT * FROM menus WHERE restaurant_id = %s AND availability = 'In Stock'",
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
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
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
        
        info_layout = QHBoxLayout()
        
        cuisine_label = QLabel(f"Cuisine: {self.restaurant_data['cuisine_type']}")
        cuisine_label.setObjectName("restaurant-info")
        
        rating_label = QLabel(f"Rating: {self.restaurant_data['rating']:.1f}★")
        rating_label.setObjectName("restaurant-rating")
        
        info_layout.addWidget(cuisine_label)
        info_layout.addWidget(rating_label)
        info_layout.addStretch()
        
        # Add to header
        header_layout.addWidget(back_btn)
        header_layout.addWidget(name_label)
        header_layout.addLayout(info_layout)
        
        # Menu section
        menu_label = QLabel("Menu")
        menu_label.setObjectName("section-header")
        menu_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # Categories and menu items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Group menu items by category
        categories = {}
        for item in self.menu_items:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Create category sections
        for category, items in categories.items():
            category_frame = QFrame()
            category_frame.setObjectName("category-frame")
            category_layout = QVBoxLayout(category_frame)
            
            category_label = QLabel(category)
            category_label.setObjectName("category-label")
            category_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            
            category_layout.addWidget(category_label)
            
            # Add menu items for this category
            for item in items:
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
                
                price_text = f"${item['price']:.2f}"
                if item['discount_price']:
                    price_text = f"<s>${item['price']:.2f}</s> ${item['discount_price']:.2f}"
                
                price = QLabel(price_text)
                price.setObjectName("item-price")
                
                details_layout.addWidget(name)
                details_layout.addWidget(description)
                details_layout.addWidget(price)
                
                # Add to cart controls
                add_layout = QVBoxLayout()
                
                quantity = QSpinBox()
                quantity.setObjectName("quantity-input")
                quantity.setMinimum(1)
                quantity.setMaximum(10)
                quantity.setValue(1)
                
                add_btn = QPushButton("Add to Cart")
                add_btn.setObjectName("add-to-cart-button")
                add_btn.clicked.connect(lambda _, item=item, qty=quantity: self.handle_add_to_cart(item, qty))
                
                add_layout.addWidget(quantity)
                add_layout.addWidget(add_btn)
                add_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Add to item frame
                item_layout.addLayout(details_layout, 7)
                item_layout.addLayout(add_layout, 3)
                
                category_layout.addWidget(item_frame)
            
            scroll_layout.addWidget(category_frame)
        
        # If no menu items
        if not self.menu_items:
            empty_label = QLabel("No menu items available")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(empty_label)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(menu_label)
        main_layout.addWidget(scroll_area)
        
        # Apply styles
        self.setStyleSheet("""
            #restaurant-header {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
                padding: 15px;
                margin-bottom: 10px;
            }
            #back-button {
                background-color: transparent;
                color: #3498db;
                border: none;
                padding: 5px 0;
                text-align: left;
                font-weight: normal;
            }
            #back-button:hover {
                color: #2980b9;
                text-decoration: underline;
            }
            #restaurant-name {
                margin: 10px 0;
                color: #2c3e50;
            }
            #restaurant-info {
                color: #7f8c8d;
                font-size: 14px;
            }
            #restaurant-rating {
                color: #f39c12;
                font-weight: bold;
                font-size: 14px;
            }
            #section-header {
                color: #2c3e50;
                margin: 10px 0;
            }
            #category-frame {
                margin-bottom: 20px;
            }
            #category-label {
                color: #2c3e50;
                padding: 5px 0;
                border-bottom: 1px solid #e0e0e0;
            }
            #menu-item {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #e0e0e0;
            }
            #menu-item:hover {
                border: 1px solid #3498db;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            #item-name {
                color: #2c3e50;
            }
            #item-description {
                color: #7f8c8d;
                font-size: 13px;
            }
            #item-price {
                color: #e74c3c;
                font-weight: bold;
                font-size: 14px;
            }
            #quantity-input {
                width: 50px;
                padding: 5px;
            }
            #add-to-cart-button {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            #add-to-cart-button:hover {
                background-color: #27ae60;
            }
        """)
    
    def handle_add_to_cart(self, menu_item, quantity_spinbox):
        quantity = quantity_spinbox.value()
        self.add_to_cart.emit(menu_item, quantity)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Added to Cart",
            f"{quantity} x {menu_item['dish_name']} added to your cart"
        ) 