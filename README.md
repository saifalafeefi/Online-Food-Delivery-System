# Online Food Delivery System

![Version](https://img.shields.io/badge/version-1.3.1-blue.svg)

KU project food delivery management system that connects restaurants, customers, and delivery personnel through a Python backend with MySQL database integration. The system allows users to browse menus, place orders, and track deliveries in real-time.

## Features

- **Restaurant Management**: Add, update, and manage restaurant information
- **Menu Management**: Create and manage restaurant menus with prices and availability
- **Customer Management**: Track customer information and order history
- **Order Management**: Process and track orders with real-time status updates
- **Delivery Management**: Assign and track deliveries with estimated times
- **Delivery Personnel Management**: Manage delivery personnel with vehicle types
- **Search Functionality**: Search across all entities with advanced filtering
- **Export Capabilities**: Export search results to CSV files

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
2. The application should now start with a graphical user interface

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**: Make sure you've installed all requirements with `pip install -r requirements.txt`

2. **Database Connection Error**: 
   - Verify your MySQL server is running
   - Check your `.env` file has correct credentials
   - Ensure the database exists

3. **Application Won't Start**:
   - Make sure Python is in your PATH
   - Verify the database setup script has been run
   - Check the console for error messages

### Getting Help

If you encounter any issues not covered here, please:
1. Check the console output for error messages
2. Verify all installation steps were completed
3. Ensure MySQL server is running
4. Contact us or initiate a pull request when necessary