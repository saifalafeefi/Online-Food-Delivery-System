import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                            QLineEdit, QComboBox, QMessageBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFrame, QDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from db_utils import execute_query

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Food Delivery System")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Add logo/title
        title = QLabel("Food Delivery")
        title.setObjectName("sidebar-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Add menu buttons
        self.menu_buttons = []
        menu_items = [
            "Restaurant Management",
            "Menu Management",
            "Customer Management",
            "Order Management",
            "Delivery Tracking",
            "Search"
        ]
        
        for item in menu_items:
            btn = QPushButton(item)
            btn.setObjectName("sidebar-button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, text=item: self.switch_page(text))
            sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.restaurant_page = RestaurantPage()
        self.menu_page = MenuPage()
        self.customer_page = CustomerPage()
        self.order_page = OrderPage()
        self.delivery_page = DeliveryPage()
        self.search_page = SearchPage()
        
        self.stacked_widget.addWidget(self.restaurant_page)
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.customer_page)
        self.stacked_widget.addWidget(self.order_page)
        self.stacked_widget.addWidget(self.delivery_page)
        self.stacked_widget.addWidget(self.search_page)
        
        # Add widgets to main layout
        layout.addWidget(sidebar)
        layout.addWidget(self.stacked_widget)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            #sidebar {
                background-color: #2c3e50;
                border: none;
            }
            #sidebar-title {
                color: white;
                font-size: 24px;
                padding: 20px;
                font-weight: bold;
            }
            #sidebar-button {
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 16px;
            }
            #sidebar-button:hover {
                background-color: #34495e;
            }
            #sidebar-button:checked {
                background-color: #3498db;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
    
    def switch_page(self, page_name):
        # Uncheck all buttons
        for btn in self.menu_buttons:
            btn.setChecked(False)
        
        # Check clicked button
        for btn in self.menu_buttons:
            if btn.text() == page_name:
                btn.setChecked(True)
                break
        
        # Switch to corresponding page
        page_index = {
            "Restaurant Management": 0,
            "Menu Management": 1,
            "Customer Management": 2,
            "Order Management": 3,
            "Delivery Tracking": 4,
            "Search": 5
        }
        self.stacked_widget.setCurrentIndex(page_index[page_name])

class RestaurantPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Restaurant Management")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Restaurant")
        update_btn = QPushButton("Update Restaurant")
        remove_btn = QPushButton("Remove Restaurant")
        
        add_btn.clicked.connect(self.add_restaurant)
        update_btn.clicked.connect(self.update_restaurant)
        remove_btn.clicked.connect(self.remove_restaurant)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(remove_btn)
        layout.addLayout(button_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Address", "Contact", "Cuisine", "Rating"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_restaurants()
    
    def load_restaurants(self):
        restaurants = execute_query("SELECT * FROM restaurants")
        self.table.setRowCount(len(restaurants))
        
        for i, restaurant in enumerate(restaurants):
            self.table.setItem(i, 0, QTableWidgetItem(str(restaurant['restaurant_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(restaurant['name']))
            self.table.setItem(i, 2, QTableWidgetItem(restaurant['address']))
            self.table.setItem(i, 3, QTableWidgetItem(restaurant['contact_number']))
            self.table.setItem(i, 4, QTableWidgetItem(restaurant['cuisine_type']))
            self.table.setItem(i, 5, QTableWidgetItem(str(restaurant['rating'])))
    
    def add_restaurant(self):
        dialog = RestaurantDialog(self)
        if dialog.exec():
            self.load_restaurants()
    
    def update_restaurant(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a restaurant to update")
            return
        
        restaurant_id = int(self.table.item(selected_items[0].row(), 0).text())
        dialog = RestaurantDialog(self, restaurant_id)
        if dialog.exec():
            self.load_restaurants()
    
    def remove_restaurant(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a restaurant to remove")
            return
        
        restaurant_id = int(self.table.item(selected_items[0].row(), 0).text())
        restaurant_name = self.table.item(selected_items[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove {restaurant_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query(
                "DELETE FROM restaurants WHERE restaurant_id = %s",
                (restaurant_id,),
                fetch=False
            )
            if result:
                self.load_restaurants()
                QMessageBox.information(self, "Success", "Restaurant removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove restaurant")

class RestaurantDialog(QDialog):
    def __init__(self, parent=None, restaurant_id=None):
        super().__init__(parent)
        self.restaurant_id = restaurant_id
        self.setWindowTitle("Add Restaurant" if not restaurant_id else "Update Restaurant")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add form fields
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.cuisine_input = QLineEdit()
        
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("Contact:"))
        layout.addWidget(self.contact_input)
        layout.addWidget(QLabel("Cuisine:"))
        layout.addWidget(self.cuisine_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.save_restaurant)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load restaurant data if updating
        if restaurant_id:
            self.load_restaurant_data()
    
    def load_restaurant_data(self):
        restaurant = execute_query(
            "SELECT * FROM restaurants WHERE restaurant_id = %s",
            (self.restaurant_id,)
        )
        if restaurant:
            self.name_input.setText(restaurant[0]['name'])
            self.address_input.setText(restaurant[0]['address'])
            self.contact_input.setText(restaurant[0]['contact_number'])
            self.cuisine_input.setText(restaurant[0]['cuisine_type'])
    
    def save_restaurant(self):
        name = self.name_input.text()
        address = self.address_input.text()
        contact = self.contact_input.text()
        cuisine = self.cuisine_input.text()
        
        if not all([name, address, contact, cuisine]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return
        
        if self.restaurant_id:
            query = """
            UPDATE restaurants 
            SET name = %s, address = %s, contact_number = %s, cuisine_type = %s
            WHERE restaurant_id = %s
            """
            params = (name, address, contact, cuisine, self.restaurant_id)
        else:
            query = """
            INSERT INTO restaurants (name, address, contact_number, cuisine_type)
            VALUES (%s, %s, %s, %s)
            """
            params = (name, address, contact, cuisine)
        
        result = execute_query(query, params, fetch=False)
        if result:
            QMessageBox.information(self, "Success", "Restaurant saved successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save restaurant")

class MenuPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Menu Management - Coming Soon"))

class CustomerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Customer Management - Coming Soon"))

class OrderPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Order Management - Coming Soon"))

class DeliveryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Delivery Tracking - Coming Soon"))

class SearchPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Search - Coming Soon"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 