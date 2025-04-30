import mysql.connector
from mysql.connector import Error
import os
from tkinter import messagebox
from config import Config
import bcrypt
from datetime import datetime

def connect_to_database():
    """
    Establishes a connection to the MySQL database using credentials from config.py.
    
    Returns:
        connection (mysql.connector.connection): Database connection object
    """
    try:
        # Connect to the database using Config class
        connection = mysql.connector.connect(
            host=Config.db_host,
            user=Config.user,
            password=Config.password,
            database=Config.database
        )
        
        # Check if the connection was successful
        if connection.is_connected():
            return connection
            
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """
    Executes a SQL query with optional parameters and returns results if requested.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch (bool, optional): Whether to fetch and return results
        
    Returns:
        result: Query results if fetch=True, otherwise None
    """
    connection = connect_to_database()
    result = None
    
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                
            cursor.close()
            
    except Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            
    return result

def soft_delete(table, id_column, id_value):
    """
    Perform a soft delete by setting IsActive=False and updating DeletedAt.
    
    Args:
        table (str): Table name (e.g., 'User', 'Restaurant')
        id_column (str): Primary key column name (e.g., 'UserID', 'RestaurantID') 
        id_value: Primary key value
        
    Returns:
        bool: True if successful, False otherwise
    """
    query = f"UPDATE {table} SET IsActive = False, DeletedAt = NOW() WHERE {id_column} = %s"
    try:
        execute_query(query, (id_value,), fetch=False)
        return True
    except Exception as e:
        messagebox.showerror("Delete Error", f"Failed to delete record: {e}")
        return False

def get_active_records(table, conditions=None):
    """
    Get only active (non-deleted) records from a table.
    
    Args:
        table (str): Table name
        conditions (dict, optional): Additional WHERE conditions as a dictionary
        
    Returns:
        list: List of records or None if error
    """
    query = f"SELECT * FROM {table} WHERE IsActive = True AND DeletedAt IS NULL"
    
    # Add additional conditions if provided
    params = None
    if conditions:
        for key, value in conditions.items():
            query += f" AND {key} = %s"
        params = tuple(conditions.values())
    
    return execute_query(query, params, fetch=True)

def restore_deleted_record(table, id_column, id_value):
    """
    Restore a soft-deleted record by setting IsActive=True and clearing DeletedAt.
    
    Args:
        table (str): Table name
        id_column (str): Primary key column name
        id_value: Primary key value
        
    Returns:
        bool: True if successful, False otherwise
    """
    query = f"UPDATE {table} SET IsActive = True, DeletedAt = NULL WHERE {id_column} = %s"
    try:
        execute_query(query, (id_value,), fetch=False)
        return True
    except Exception as e:
        messagebox.showerror("Restore Error", f"Failed to restore record: {e}")
        return False

def validate_user(email, password):
    """
    Validates user credentials and returns user info if valid.
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        dict: User information if credentials are valid, otherwise None
    """
    # Get the user with the provided email that is active
    query = """
        SELECT UserID, FirstName, LastName, Email, Password, Role, Phone, Address
        FROM User 
        WHERE Email = %s AND IsActive = True AND DeletedAt IS NULL
    """
    
    result = execute_query(query, (email,), fetch=True)
    
    if result and len(result) > 0:
        user = result[0]
        stored_password = user['Password']
        
        # Use bcrypt to check the password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            # Remove the password from the result before returning
            del user['Password']
            return user
    
    return None

def register_user(first_name, last_name, email, password, role='customer'):
    """
    Registers a new user in the database.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email
        password (str): User's password
        role (str, optional): User role (default: 'customer')
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    # Check if user already exists and is active
    check_query = "SELECT UserID FROM User WHERE Email = %s AND IsActive = True AND DeletedAt IS NULL"
    existing_user = execute_query(check_query, (email,), fetch=True)
    
    if existing_user:
        messagebox.showerror("Registration Error", "A user with this email already exists.")
        return False
    
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new user
    insert_query = """
        INSERT INTO User (FirstName, LastName, Email, Password, Role, IsActive, CreatedAt)
        VALUES (%s, %s, %s, %s, %s, True, NOW())
    """
    
    try:
        execute_query(insert_query, (first_name, last_name, email, hashed_password, role))
        return True
    except Exception as e:
        messagebox.showerror("Registration Error", f"Failed to register user: {e}")
        return False

def update_user_profile(user_id, first_name, last_name, email, phone, address):
    """
    Updates a user's profile information.
    
    Args:
        user_id: User's ID
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email
        phone (str): User's phone number
        address (str): User's address
        
    Returns:
        bool: True if update successful, False otherwise
    """
    query = """
        UPDATE User 
        SET FirstName = %s, LastName = %s, Email = %s, Phone = %s, Address = %s, UpdatedAt = NOW()
        WHERE UserID = %s AND IsActive = True
    """
    
    try:
        execute_query(query, (first_name, last_name, email, phone, address, user_id))
        return True
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update profile: {e}")
        return False

def change_password(user_id, current_password, new_password):
    """
    Changes a user's password.
    
    Args:
        user_id: User's ID
        current_password (str): User's current password
        new_password (str): User's new password
        
    Returns:
        bool: True if password change successful, False otherwise
    """
    # Verify current password
    verify_query = "SELECT Password FROM User WHERE UserID = %s AND IsActive = True"
    result = execute_query(verify_query, (user_id,), fetch=True)
    
    if not result:
        messagebox.showerror("Password Error", "User not found.")
        return False
    
    stored_password = result[0]['Password']
    
    # Check if the current password matches
    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password.encode('utf-8')):
        messagebox.showerror("Password Error", "Current password is incorrect.")
        return False
    
    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update the password
    update_query = "UPDATE User SET Password = %s, UpdatedAt = NOW() WHERE UserID = %s"
    
    try:
        execute_query(update_query, (hashed_password, user_id))
        return True
    except Exception as e:
        messagebox.showerror("Password Error", f"Failed to change password: {e}")
        return False

def update_user_settings(user_id, setting_name, setting_value):
    """
    Update or create a user setting.
    
    Args:
        user_id: User ID
        setting_name (str): Name of the setting (e.g., 'Notifications', 'DarkMode')
        setting_value (bool): Boolean value for the setting
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if the setting already exists
    check_query = "SELECT * FROM UserSettings WHERE UserID = %s AND SettingName = %s"
    result = execute_query(check_query, (user_id, setting_name), fetch=True)
    
    try:
        if result:
            # Update existing setting
            update_query = "UPDATE UserSettings SET SettingValue = %s, UpdatedAt = NOW() WHERE UserID = %s AND SettingName = %s"
            execute_query(update_query, (setting_value, user_id, setting_name))
        else:
            # Create new setting
            insert_query = "INSERT INTO UserSettings (UserID, SettingName, SettingValue, CreatedAt) VALUES (%s, %s, %s, NOW())"
            execute_query(insert_query, (user_id, setting_name, setting_value))
        return True
    except Exception as e:
        messagebox.showerror("Settings Error", f"Failed to update setting: {e}")
        return False

def get_user_settings(user_id):
    """
    Get all settings for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        dict: Dictionary of settings or empty dict if none found
    """
    query = "SELECT SettingName, SettingValue FROM UserSettings WHERE UserID = %s"
    results = execute_query(query, (user_id,), fetch=True)
    
    settings = {}
    if results:
        for row in results:
            settings[row['SettingName']] = row['SettingValue']
    
    return settings

def update_address(user_id, address, delivery_instructions=None):
    """
    Updates a user's address and delivery instructions.
    
    Args:
        user_id: User's ID
        address (str): User's address
        delivery_instructions (str, optional): Delivery instructions
        
    Returns:
        bool: True if update successful, False otherwise
    """
    query = """
        UPDATE User 
        SET Address = %s, DeliveryInstructions = %s, UpdatedAt = NOW()
        WHERE UserID = %s AND IsActive = True
    """
    
    try:
        execute_query(query, (address, delivery_instructions, user_id))
        return True
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update address: {e}")
        return False