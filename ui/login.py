from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFormLayout, QComboBox, QMessageBox,
                            QDialog, QHBoxLayout, QGroupBox, QRadioButton,
                            QGridLayout, QCheckBox, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon, QKeyEvent
from auth.user import User, UserRole
from db_utils import execute_query
import json
import os
import hashlib

class LoginWindow(QWidget):
    login_successful = Signal(object)
    switch_to_register = Signal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_saved_login()
    
    def initUI(self):
        self.setWindowTitle("Food Delivery - Login")
        self.setMinimumSize(400, 500)
        
        layout = QVBoxLayout()
        
        # Logo/Header Section
        header_layout = QVBoxLayout()
        title = QLabel("Food Delivery")
        title.setObjectName("app-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        subtitle = QLabel("Sign in to your account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addSpacing(20)
        
        # Form Section
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.remember_checkbox = QCheckBox("Remember Me")
        
        form_layout.addRow("Username/Email:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow(self.remember_checkbox)
        
        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("primary-button")
        login_btn.clicked.connect(self.attempt_login)
        
        # Register Link
        register_layout = QHBoxLayout()
        register_label = QLabel("Don't have an account?")
        register_btn = QPushButton("Register")
        register_btn.setFlat(True)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.clicked.connect(lambda: self.switch_to_register.emit())
        
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_btn)
        register_layout.addStretch()
        
        # Connect Enter key press to login
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
        
        # Add all sections to main layout
        layout.addLayout(header_layout)
        layout.addSpacing(30)
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(login_btn)
        layout.addSpacing(10)
        layout.addLayout(register_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            #app-title {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            #primary-button {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            #primary-button:hover {
                background-color: #2980b9;
            }
            QPushButton:flat {
                color: #3498db;
                text-decoration: none;
            }
            QPushButton:flat:hover {
                text-decoration: underline;
            }
        """)
    
    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        # Hardcoded admin login with correct credentials
        if username == "admin" and password == "admin123":
            admin_user = User(user_id=1, username="admin", role=UserRole.ADMIN)
            admin_user.is_authenticated = True
            
            # Save login if checkbox is checked
            if self.remember_checkbox.isChecked():
                self.save_login(username, password)
                
            self.login_successful.emit(admin_user)
            return
        
        # Try database login with error handling
        try:
            # Regular login attempt
            user, message = User.login(username, password)
            
            if user:
                # Save login if checkbox is checked
                if self.remember_checkbox.isChecked():
                    self.save_login(username, password)
                else:
                    self.clear_saved_login()
                    
                self.login_successful.emit(user)
            else:
                QMessageBox.warning(self, "Login Failed", message)
        except Exception as e:
            print(f"Login error: {e}")
            QMessageBox.critical(self, "Database Error", 
                               "Cannot connect to the database. Please check your database connection. " +
                               "Only the admin account (admin/admin123) is available in offline mode.")
    
    def load_saved_login(self):
        """Load saved login information if available"""
        try:
            if os.path.exists('settings/login.json'):
                with open('settings/login.json', 'r') as f:
                    login_data = json.load(f)
                
                self.username_input.setText(login_data.get('username', ''))
                self.password_input.setText(login_data.get('password', ''))
                self.remember_checkbox.setChecked(True)
        except Exception as e:
            print(f"Error loading saved login: {e}")
    
    def save_login(self, username, password):
        """Save login information to a file"""
        try:
            login_data = {
                'username': username,
                'password': password  # Consider encrypting this in a real application
            }
            
            # Create settings directory if it doesn't exist
            os.makedirs('settings', exist_ok=True)
            
            # Save to file
            with open('settings/login.json', 'w') as f:
                json.dump(login_data, f)
        except Exception as e:
            print(f"Error saving login info: {e}")
    
    def clear_saved_login(self):
        """Remove saved login information"""
        try:
            if os.path.exists('settings/login.json'):
                os.remove('settings/login.json')
        except Exception as e:
            print(f"Error clearing saved login: {e}")


class RegisterWindow(QWidget):
    register_successful = Signal(User)
    switch_to_login = Signal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Food Delivery - Register")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Logo/Header Section
        header_layout = QVBoxLayout()
        title = QLabel("Food Delivery")
        title.setObjectName("app-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        subtitle = QLabel("Create a new account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addSpacing(20)
        
        # Form Section
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Your email address")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Your phone number")
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Your address (optional)")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # User Role Selection
        role_group = QGroupBox("I want to join as a:")
        role_layout = QHBoxLayout()
        
        self.customer_radio = QRadioButton("Customer")
        self.restaurant_radio = QRadioButton("Restaurant Owner")
        self.delivery_radio = QRadioButton("Delivery Person")
        
        self.customer_radio.setChecked(True)  # Default selection
        
        role_layout.addWidget(self.customer_radio)
        role_layout.addWidget(self.restaurant_radio)
        role_layout.addWidget(self.delivery_radio)
        
        role_group.setLayout(role_layout)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address (optional):", self.address_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        # Register Button
        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("primary-button")
        register_btn.clicked.connect(self.register)
        
        # Login Link
        login_layout = QHBoxLayout()
        login_label = QLabel("Already have an account?")
        login_btn = QPushButton("Login")
        login_btn.setFlat(True)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(lambda: self.switch_to_login.emit())
        
        login_layout.addWidget(login_label)
        login_layout.addWidget(login_btn)
        login_layout.addStretch()
        
        # Add all sections to main layout
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addWidget(role_group)
        layout.addSpacing(20)
        layout.addWidget(register_btn)
        layout.addSpacing(10)
        layout.addLayout(login_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            #app-title {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
            }
            QRadioButton {
                padding: 5px;
            }
            #primary-button {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            #primary-button:hover {
                background-color: #2980b9;
            }
            QPushButton:flat {
                color: #3498db;
                text-decoration: none;
            }
            QPushButton:flat:hover {
                text-decoration: underline;
            }
        """)
    
    def register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs - phone and address are now optional
        if not username or not email or not password or not confirm_password:
            QMessageBox.warning(self, "Warning", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Warning", "Passwords do not match")
            return
        
        # Determine user role
        if self.customer_radio.isChecked():
            role = UserRole.CUSTOMER
        elif self.restaurant_radio.isChecked():
            role = UserRole.RESTAURANT
        elif self.delivery_radio.isChecked():
            role = UserRole.DELIVERY
        else:
            role = UserRole.CUSTOMER  # Default
        
        # Attempt to register
        success, message = User.register(username, email, password, role, phone, address)
        
        if success:
            QMessageBox.information(self, "Success", message)
            
            # Log in the user
            user, _ = User.login(username, password)
            if user:
                self.register_successful.emit(user)
            else:
                self.switch_to_login.emit()
        else:
            QMessageBox.critical(self, "Error", message) 