import hashlib
import os
from enum import Enum, auto
from db_utils import execute_query

class UserRole(Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DELIVERY = "delivery"
    ADMIN = "admin"

class User:
    def __init__(self, user_id=None, username=None, role=None):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.is_authenticated = user_id is not None
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash a password for storing."""
        if salt is None:
            salt = os.urandom(32)  # 32 bytes salt
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',  # Hash algorithm
            password.encode('utf-8'),  # Convert password to bytes
            salt,  # Salt
            100000  # Number of iterations
        )
        
        return salt + password_hash  # Concatenate salt and hash
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against a provided password."""
        salt = stored_password[:32]  # First 32 bytes are salt
        stored_password_hash = stored_password[32:]
        
        # Hash the provided password with the stored salt
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            100000
        )
        
        # Compare the calculated hash with the stored hash
        return new_hash == stored_password_hash
    
    @staticmethod
    def register(username, email, password, role):
        """Register a new user with the given details."""
        # Check if username or email already exists
        existing_user = execute_query(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (username, email)
        )
        
        if existing_user:
            return False, "Username or email already exists"
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert the new user
        result = execute_query(
            """
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (username, email, hashed_password, role.value),
            fetch=False
        )
        
        if result is not None:
            # Get the user_id of the newly created user
            user_data = execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            
            if user_data:
                user_id = user_data[0]['user_id']
                
                # Create initial profile based on role
                try:
                    if role == UserRole.CUSTOMER:
                        execute_query(
                            """
                            INSERT INTO customers (user_id, name, phone, address, email)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (user_id, username, "", "", email),
                            fetch=False
                        )
                    elif role == UserRole.RESTAURANT:
                        execute_query(
                            """
                            INSERT INTO restaurants (user_id, name, address, contact_number, cuisine_type, rating)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (user_id, "Your Restaurant", "", "", "Other", 0.0),
                            fetch=False
                        )
                    elif role == UserRole.DELIVERY:
                        execute_query(
                            """
                            INSERT INTO delivery_personnel (user_id, name, phone, status, vehicle_type)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (user_id, username, "", "Available", "Light Vehicle - Automatic"),
                            fetch=False
                        )
                except Exception as e:
                    print(f"Error creating initial profile: {e}")
                    
            return True, "User registered successfully"
        else:
            return False, "Failed to register user"
    
    @staticmethod
    def login(username_or_email, password):
        """Authenticate a user with the given credentials."""
        # First try getting the user to see the password format
        debug_data = execute_query(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (username_or_email, username_or_email)
        )
        
        if debug_data:
            print(f"Debug user data: {debug_data[0]}")
            
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        print(f"Generated hash: {hashed_password}")
        
        # Try both formats - hex string and binary
        user_data = execute_query(
            "SELECT * FROM users WHERE (username = %s OR email = %s) AND password_hash = %s",
            (username_or_email, username_or_email, hashed_password)
        )
        
        if not user_data:
            # Try alternate format
            try:
                binary_hash = bytes.fromhex(hashed_password)
                user_data = execute_query(
                    "SELECT * FROM users WHERE (username = %s OR email = %s) AND password_hash = %s",
                    (username_or_email, username_or_email, binary_hash)
                )
            except Exception as e:
                print(f"Binary conversion error: {e}")
        
        if not user_data:
            return None, "Invalid username or password"
        
        user_data = user_data[0]
        
        user = User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            role=UserRole(user_data['role'])
        )
        user.is_authenticated = True
        return user, "Login successful"
    
    @staticmethod
    def get_by_id(user_id):
        """Retrieve a user by their ID."""
        user_data = execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if not user_data:
            return None
        
        user_data = user_data[0]
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            role=UserRole(user_data['role'])
        )
    
    def get_profile(self):
        """Get the user's profile data based on their role."""
        if self.role == UserRole.CUSTOMER:
            profile_data = execute_query(
                "SELECT * FROM customers WHERE user_id = %s",
                (self.user_id,)
            )
        elif self.role == UserRole.RESTAURANT:
            profile_data = execute_query(
                "SELECT * FROM restaurants WHERE user_id = %s",
                (self.user_id,)
            )
        elif self.role == UserRole.DELIVERY:
            profile_data = execute_query(
                "SELECT * FROM delivery_personnel WHERE user_id = %s",
                (self.user_id,)
            )
        else:
            # Admins don't have separate profiles
            return {'user_id': self.user_id, 'username': self.username}
        
        if not profile_data:
            return None
        
        return profile_data[0]
    
    def update_password(self, current_password, new_password):
        """Update the user's password."""
        # Verify current password
        user_data = execute_query(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (self.user_id,)
        )
        
        if not user_data:
            return False, "User not found"
        
        stored_password = user_data[0]['password_hash']
        
        if not User.verify_password(stored_password, current_password):
            return False, "Current password is incorrect"
        
        # Hash the new password
        new_password_hash = User.hash_password(new_password)
        
        # Update the password
        result = execute_query(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_password_hash, self.user_id),
            fetch=False
        )
        
        if result is not None:
            return True, "Password updated successfully"
        else:
            return False, "Failed to update password" 