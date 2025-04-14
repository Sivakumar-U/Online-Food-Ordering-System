import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime
from custom.navigation_frame_admin import NavigationFrameAdmin
from utils import connect_to_database, execute_query
from CTkMessagebox import CTkMessagebox
import bcrypt

class AdminDashboard(ctk.CTkFrame):
    """Dashboard for administrators to manage the entire food ordering system."""
    def __init__(self, master, user_id=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store user information
        self.master = master
        self.user_id = user_id
        self.admin_data = self.get_admin_data()
        
        # Configure this frame
        self.configure(fg_color="#f5f5f5")
        
        # Create main content container (all screens will be placed here)
        self.content_container = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)
        
        # Create and place navigation at bottom
        self.navigation_frame = NavigationFrameAdmin(self, user_id=self.user_id)
        self.navigation_frame.pack(side="bottom", fill="x")
        
        # Initialize frames for different screens
        self.home_frame = HomeFrame(self.content_container, self)
        self.users_frame = UsersFrame(self.content_container, self)
        self.restaurants_frame = RestaurantsFrame(self.content_container, self)
        self.orders_frame = OrdersFrame(self.content_container, self)
        self.settings_frame = SettingsFrame(self.content_container, self)
        
        # Show default frame (home)
        self.show_frame("home")
        
    def get_admin_data(self):
        """Fetch admin data from database."""
        if not self.user_id:
            return {"FirstName": "Admin", "LastName": "User"}
        
        query = "SELECT * FROM User WHERE UserID = %s AND Role = 'admin'"
        result = execute_query(query, (self.user_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return {"FirstName": "Admin", "LastName": "User"}
    
    def show_frame(self, frame_name, **kwargs):
        """Show selected frame and hide others."""
        # Hide all frames
        for frame in [self.home_frame, self.users_frame, self.restaurants_frame, 
                     self.orders_frame, self.settings_frame]:
            frame.pack_forget()
        
        # Show selected frame
        if frame_name == "home":
            self.home_frame.pack(fill="both", expand=True)
        elif frame_name == "users":
            self.users_frame.refresh_users()
            self.users_frame.pack(fill="both", expand=True)
        elif frame_name == "restaurants":
            self.restaurants_frame.refresh_restaurants()
            self.restaurants_frame.pack(fill="both", expand=True)
        elif frame_name == "orders":
            self.orders_frame.refresh_orders()
            self.orders_frame.pack(fill="both", expand=True)
        elif frame_name == "settings":
            self.settings_frame.pack(fill="both", expand=True)
    
    def sign_out(self):
        """Sign out and return to login screen."""
        confirm = CTkMessagebox(
            title="Sign Out",
            message="Are you sure you want to sign out?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        if confirm.get() == "Yes":
            self.master.current_user = None
            self.master.user_role = None
            self.master.show_login_window()

class HomeFrame(ctk.CTkFrame):
    """Home screen for admin dashboard with system overview."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title section
        admin_name = f"{controller.admin_data.get('FirstName', 'Admin')} {controller.admin_data.get('LastName', 'User')}"
        self.title_label = ctk.CTkLabel(
            self, 
            text=f"Welcome, {admin_name}",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Quick stats frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.stats_frame.pack(fill="x", padx=15, pady=10)
        
        # Define stats
        stats = [
            ("Total Users", self.get_total_users()),
            ("Total Restaurants", self.get_total_restaurants()),
            ("Total Orders", self.get_total_orders()),
            ("Total Revenue", f"${self.get_total_revenue():.2f}")
        ]
        
        # Display stats
        for stat, value in stats:
            stat_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10, pady=15)
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=("Arial", 18, "bold"),
                text_color="#333333"
            )
            value_label.pack()
            
            label = ctk.CTkLabel(
                stat_frame,
                text=stat,
                font=("Arial", 12),
                text_color="#666666"
            )
            label.pack()
        
        # Quick actions section
        self.actions_label = ctk.CTkLabel(
            self,
            text="Quick Actions",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.actions_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Actions frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.actions_frame.pack(fill="x", padx=15, pady=10)
        
        # Define actions
        actions = [
            ("Add User", self.add_user),
            ("Add Restaurant", self.add_restaurant),
            ("View Orders", lambda: self.controller.show_frame("orders"))
        ]
        
        # Create action buttons
        for action_text, command in actions:
            action_button = ctk.CTkButton(
                self.actions_frame,
                text=action_text,
                command=command,
                fg_color="#2196F3",
                hover_color="#1976D2",
                corner_radius=10,
                font=("Arial", 14),
                height=40
            )
            action_button.pack(fill="x", padx=10, pady=10)
    
    def get_total_users(self):
        """Get total number of users."""
        query = "SELECT COUNT(*) as total FROM User"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_restaurants(self):
        """Get total number of restaurants."""
        query = "SELECT COUNT(*) as total FROM Restaurant"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_orders(self):
        """Get total number of orders."""
        query = "SELECT COUNT(*) as total FROM `Order`"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_revenue(self):
        """Get total revenue from all orders."""
        query = "SELECT SUM(TotalAmount) as revenue FROM `Order`"
        result = execute_query(query, fetch=True)
        return result[0]["revenue"] if result and result[0]["revenue"] else 0.0
    
    def add_user(self):
        """Open add user dialog."""
        self.controller.show_frame("users")
    
    def add_restaurant(self):
        """Open add restaurant dialog."""
        self.controller.show_frame("restaurants")

class UsersFrame(ctk.CTkFrame):
    """Users management screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="User Management",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Add user button
        self.add_user_button = ctk.CTkButton(
            self,
            text="Add New User",
            command=self.open_add_user_dialog,
            fg_color="#2196F3",
            hover_color="#1976D2",
            corner_radius=10,
            font=("Arial", 14),
            height=40,
            width=250
        )
        self.add_user_button.pack(pady=(0, 15))
        
        # Users container
        self.users_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.users_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Refresh users
        self.refresh_users()
    
    def refresh_users(self):
        """Refresh and display users."""
        # Clear existing items
        for widget in self.users_container.winfo_children():
            widget.destroy()
        
        # Get users
        users = self.get_users()
        
        if not users:
            # No users
            no_users_label = ctk.CTkLabel(
                self.users_container,
                text="No users found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_users_label.pack(pady=50)
            return
        
        # Display users
        for user in users:
            self.create_user_card(user)
    
    def get_users(self):
        """Get all users from the database."""
        query = """
            SELECT UserID, FirstName, LastName, Email, Role, 
                   DATE_FORMAT(DATE(NOW()), '%Y-%m-%d') as JoinDate 
            FROM User
            ORDER BY UserID
        """
        return execute_query(query, fetch=True) or []
    
    def create_user_card(self, user):
        """Create a card for a user."""
        card = ctk.CTkFrame(self.users_container, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=5, ipady=10)
        
        # User details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Name
        name_label = ctk.CTkLabel(
            details_frame,
            text=f"{user['FirstName']} {user['LastName']}",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        name_label.pack(anchor="w")
        
        # Email
        email_label = ctk.CTkLabel(
            details_frame,
            text=user['Email'],
            font=("Arial", 12),
            text_color="#666666"
        )
        email_label.pack(anchor="w")
        
        # Role and Join Date
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        role_label = ctk.CTkLabel(
            info_frame,
            text=f"Role: {user['Role']}",
            font=("Arial", 12),
            text_color="#4CAF50"
        )
        role_label.pack(side="left")
        
        join_label = ctk.CTkLabel(
            info_frame,
            text=f"Joined: {user.get('JoinDate', 'N/A')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        join_label.pack(side="right")
        
        # Actions frame
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=100,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda u=user: self.edit_user(u)
        )
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=100,
            fg_color="#F44336",
            hover_color="#D32F2F",
            command=lambda u=user: self.delete_user(u)
        )
        delete_btn.pack(side="right", padx=5)
    
    def open_add_user_dialog(self):
        """Open dialog to add a new user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # First Name
        first_name_label = ctk.CTkLabel(dialog, text="First Name", anchor="w")
        first_name_label.pack(padx=20, pady=(20, 5), anchor="w")
        first_name_entry = ctk.CTkEntry(dialog, width=350)
        first_name_entry.pack(padx=20, pady=5)
        
        # Last Name
        last_name_label = ctk.CTkLabel(dialog, text="Last Name", anchor="w")
        last_name_label.pack(padx=20, pady=(10, 5), anchor="w")
        last_name_entry = ctk.CTkEntry(dialog, width=350)
        last_name_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.pack(padx=20, pady=5)
        
        # Password
        password_label = ctk.CTkLabel(dialog, text="Password", anchor="w")
        password_label.pack(padx=20, pady=(10, 5), anchor="w")
        password_entry = ctk.CTkEntry(dialog, width=350, show="*")
        password_entry.pack(padx=20, pady=5)
        
        # Role
        role_label = ctk.CTkLabel(dialog, text="User Role", anchor="w")
        role_label.pack(padx=20, pady=(10, 5), anchor="w")
        role_var = ctk.StringVar(value="customer")
        role_dropdown.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Create User", 
            command=lambda: self.save_new_user(
                first_name_entry.get(), 
                last_name_entry.get(), 
                email_entry.get(), 
                password_entry.get(), 
                role_var.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_new_user(self, first_name, last_name, email, password, role, dialog):
        """Save a new user to the database."""
        # Basic validation
        if not first_name or not last_name or not email or not password:
            CTkMessagebox(
                title="Validation Error",
                message="All fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid email address.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Password strength check
        from custom.auth import is_password_strong
        if not is_password_strong(password):
            CTkMessagebox(
                title="Password Requirements",
                message="Password must be at least 8 characters with 1 uppercase letter and 1 special character.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if email already exists
        check_query = "SELECT UserID FROM User WHERE Email = %s"
        existing_user = execute_query(check_query, (email,), fetch=True)
        
        if existing_user:
            CTkMessagebox(
                title="Registration Error",
                message="A user with this email already exists.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Insert new user
        query = """
            INSERT INTO User (FirstName, LastName, Email, Password, Role)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, hashed_password, role))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Refresh users list
            self.refresh_users()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="User created successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to create user: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def edit_user(self, user):
        """Open dialog to edit an existing user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit User")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # First Name
        first_name_label = ctk.CTkLabel(dialog, text="First Name", anchor="w")
        first_name_label.pack(padx=20, pady=(20, 5), anchor="w")
        first_name_entry = ctk.CTkEntry(dialog, width=350)
        first_name_entry.insert(0, user['FirstName'])
        first_name_entry.pack(padx=20, pady=5)
        
        # Last Name
        last_name_label = ctk.CTkLabel(dialog, text="Last Name", anchor="w")
        last_name_label.pack(padx=20, pady=(10, 5), anchor="w")
        last_name_entry = ctk.CTkEntry(dialog, width=350)
        last_name_entry.insert(0, user['LastName'])
        last_name_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.insert(0, user['Email'])
        email_entry.pack(padx=20, pady=5)
        
        # Role
        role_label = ctk.CTkLabel(dialog, text="User Role", anchor="w")
        role_label.pack(padx=20, pady=(10, 5), anchor="w")
        role_var = ctk.StringVar(value=user['Role'])
        role_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=["customer", "restaurant", "admin"],
            variable=role_var,
            width=350
        )
        role_dropdown.pack(padx=20, pady=5)
        
        # Password Reset Option
        reset_password_btn = ctk.CTkButton(
            dialog,
            text="Reset Password",
            command=lambda: self.reset_user_password(user['UserID']),
            width=350,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        reset_password_btn.pack(padx=20, pady=(10, 5))
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Update User", 
            command=lambda: self.save_user_changes(
                user['UserID'],
                first_name_entry.get(), 
                last_name_entry.get(), 
                email_entry.get(), 
                role_var.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_user_changes(self, user_id, first_name, last_name, email, role, dialog):
        """Save changes to an existing user."""
        # Basic validation
        if not first_name or not last_name or not email:
            CTkMessagebox(
                title="Validation Error",
                message="All fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid email address.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Update user query
        query = """
            UPDATE User 
            SET FirstName = %s, LastName = %s, Email = %s, Role = %s
            WHERE UserID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, role, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Refresh users list
            self.refresh_users()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="User updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update user: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def reset_user_password(self, user_id):
        """Reset a user's password."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Password")
        dialog.geometry("400x300")
        dialog.grab_set()  # Make dialog modal
        
        # New Password
        new_pass_label = ctk.CTkLabel(dialog, text="New Password", anchor="w")
        new_pass_label.pack(padx=20, pady=(20, 5), anchor="w")
        new_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        new_pass_entry.pack(padx=20, pady=5)
        
        # Confirm New Password
        confirm_pass_label = ctk.CTkLabel(dialog, text="Confirm New Password", anchor="w")
        confirm_pass_label.pack(padx=20, pady=(10, 5), anchor="w")
        confirm_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        confirm_pass_entry.pack(padx=20, pady=5)
        
        # Password requirements hint
        hint_label = ctk.CTkLabel(
            dialog,
            text="Password must be at least 8 characters\nwith 1 uppercase letter and 1 special character",
            font=("Arial", 10),
            text_color="#666666"
        )
        hint_label.pack(pady=(10, 5))
        
        # Reset button
        reset_btn = ctk.CTkButton(
            dialog, 
            text="Reset Password", 
            command=lambda: self.save_reset_password(
                user_id,
                new_pass_entry.get(), 
                confirm_pass_entry.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        reset_btn.pack(padx=20, pady=(20, 10))
    
    def save_reset_password(self, user_id, new_password, confirm_password, dialog):
        """Save the reset password."""
        # Validate passwords match
        if new_password != confirm_password:
            CTkMessagebox(
                title="Validation Error",
                message="Passwords do not match.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Check password strength
        from custom.auth import is_password_strong
        if not is_password_strong(new_password):
            CTkMessagebox(
                title="Password Requirements",
                message="Password must be at least 8 characters with 1 uppercase letter and 1 special character.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password query
        query = "UPDATE User SET Password = %s WHERE UserID = %s"
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (hashed_password, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Password reset successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to reset password: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def delete_user(self, user):
        """Delete a user from the database."""
        # Confirm deletion
        confirm = CTkMessagebox(
            title="Delete User",
            message=f"Are you sure you want to delete user {user['FirstName']} {user['LastName']}?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Delete user query
            query = "DELETE FROM User WHERE UserID = %s"
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(query, (user['UserID'],))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh users list
                self.refresh_users()
                
                # Show success message
                CTkMessagebox(
                    title="Success",
                    message="User deleted successfully!",
                    icon="check",
                    option_1="OK"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Database Error",
                    message=f"Failed to delete user: {e}",
                    icon="cancel",
                    option_1="OK"
                )