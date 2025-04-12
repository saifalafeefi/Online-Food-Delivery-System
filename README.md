# Online Food Delivery System

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)

A comprehensive food delivery platform that connects customers, restaurants, and delivery personnel, similar to commercial services like DoorDash, Deliveroo, and Talabat. The application features multiple interfaces for different user roles and real-time order tracking.

## Key Features

### For Customers
- User registration and login
- Browse restaurants by cuisine type, location, or ratings
- View restaurant menus with detailed descriptions and prices
- Place and customize food orders
- Real-time order tracking
- Payment processing
- Order history and reordering
- Rating and review system

### For Restaurants
- Restaurant dashboard for menu management
- Real-time order notifications
- Inventory and stock management
- Order acceptance/rejection
- Business analytics and reporting
- Profile management

### For Delivery Personnel
- Delivery app for order pickup and delivery
- Navigation assistance
- Delivery status updates
- Earnings tracking
- Profile and availability management

### For Administrators
- System-wide management dashboard
- User account management
- Restaurant approval process
- Dispute resolution
- System metrics and analytics

## System Requirements

- Windows 10 or later
- Python 3.8 or later
- MySQL Server 8.0 or later
- 4GB RAM minimum
- 500MB free disk space

## Installation Guide

### 1. Install Python

1. Download Python from the [official website](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check the box that says "Add Python to PATH" during installation
4. Complete the installation

### 2. Install MySQL

1. Download MySQL Server from the [official website](https://dev.mysql.com/downloads/mysql/)
2. Run the installer
3. Choose "Developer Default" installation type
4. Follow the installation wizard
5. **Important**: Remember the root password you set during installation

### 3. Clone the Repository

1. Download and install [Git](https://git-scm.com/downloads) if you don't have it
2. Open Command Prompt or PowerShell
3. Navigate to your desired directory
4. Run the following command:
   ```
   git clone https://github.com/saifalafeefi/Online-Food-Delivery-System.git
   ```
5. Navigate to the project directory:
   ```
   cd Online-Food-Delivery-System
   ```

### 4. Configure Environment Variables

1. Create a new file named `.env` in the project root directory
2. Add the following content (replace with your actual MySQL credentials):
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=food_delivery
   ```

### 5. Install Required Python Packages

1. Open Command Prompt or PowerShell in the project directory
2. Run the following command:
   ```
   pip install -r requirements.txt
   ```

### 6. Set Up the Database

1. In the project directory, run:
   ```
   python setup_database.py
   ```
2. This will create the database and all necessary tables automatically

### 7. Launch the Application

1. In the project directory, run:
   ```
   python main.py
   ```
2. The application will start with the login screen

## User Guide

### Customer Interface
1. Register a new account or login with existing credentials
2. Browse restaurants or search for specific cuisines
3. Select a restaurant to view its menu
4. Add items to your cart
5. Review your order and proceed to checkout
6. Track your order status in real-time
7. Rate and review after delivery

### Restaurant Interface
1. Login with restaurant credentials
2. Manage your menu (add, update, or remove items)
3. View and process incoming orders
4. Update inventory and availability
5. View ratings and customer feedback

### Delivery Personnel Interface
1. Login with delivery personnel credentials
2. View available orders for pickup
3. Accept delivery assignments
4. Update delivery status
5. Complete deliveries and confirm with customers

### Admin Interface
1. Login with admin credentials
2. Manage users, restaurants, and delivery personnel
3. View system metrics and reports
4. Handle disputes and issues
5. Configure system settings

## Troubleshooting

### Common Issues

1. **Login Problems**: Reset your password or contact support
2. **Database Connection Error**: 
   - Verify your MySQL server is running
   - Check your `.env` file has correct credentials

3. **Application Won't Start**:
   - Make sure Python is in your PATH
   - Verify the database setup script has been run
   - Check the console for error messages

### Getting Help

If you encounter any issues not covered here, please:
1. Check the console output for error messages
2. Verify all installation steps were completed
3. Contact us through the support section in the app