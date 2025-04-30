import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re  # For password validation
import bcrypt
from utils import connect_to_database, execute_query, soft_delete
from CTkMessagebox import CTkMessagebox  # Assuming you'll install this package

# Function to validate user credentials
def validate_user(email, password):
    """
    Validates user login credentials.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        dict or None: User data if credentials are valid, None otherwise
    """
    try:
        # Only get active users (not soft-deleted)
        query = "SELECT * FROM User WHERE Email = %s AND IsActive = True AND DeletedAt IS NULL"
        user = execute_query(query, (email,), fetch=True)
        
        if user and len(user) > 0:
            user = user[0]  # Get the first user
            if bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                # Remove the password before returning user data
                del user['Password']
                return user
        return None
    except Exception as err:
        print(f"Database Error: {err}")
        return None


# Function to add a new user
def register_user(first_name, last_name, email, password, role='customer'):
    """
    Registers a new user in the database with a hashed password.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email
        password (str): User's password (will be hashed)
        role (str): User's role (default: 'customer')
        
    Returns:
        bool: True if registration was successful, False otherwise
    """
    try:
        # Check if email already exists for active users
        check_query = "SELECT UserID FROM User WHERE Email = %s AND IsActive = True AND DeletedAt IS NULL"
        existing_user = execute_query(check_query, (email,), fetch=True)
        
        if existing_user:
            return False

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert the new user with IsActive flag
        query = """
        INSERT INTO User (FirstName, LastName, Email, Password, Role, IsActive, CreatedAt)
        VALUES (%s, %s, %s, %s, %s, True, NOW())
        """
        execute_query(query, (first_name, last_name, email, hashed_password, role), fetch=False)
        
        # Add default settings for the new user
        user_id_query = "SELECT UserID FROM User WHERE Email = %s"
        user_result = execute_query(user_id_query, (email,), fetch=True)
        
        if user_result and len(user_result) > 0:
            user_id = user_result[0]['UserID']
            
            # Default settings
            settings_query = """
            INSERT INTO UserSettings (UserID, SettingName, SettingValue, CreatedAt)
            VALUES (%s, %s, %s, NOW())
            """
            
            default_settings = [
                (user_id, "Notifications", True),
                (user_id, "DarkMode", False),
                (user_id, "AutoSaveAddress", True),
                (user_id, "SavePaymentInfo", False)
            ]
            
            for setting in default_settings:
                execute_query(settings_query, setting, fetch=False)
                
        return True
    except Exception as err:
        print(f"Database Error: {err}")
        return False


# Function to reset a user's password
def reset_password_logic(email, new_password):
    """
    Resets a user's password if the email exists in the database.
    
    Args:
        email (str): User's email
        new_password (str): New password to set
        
    Returns:
        tuple: (success_boolean, message_string)
    """
    try:
        # Check if email exists for active user
        query = "SELECT UserID FROM User WHERE Email = %s AND IsActive = True AND DeletedAt IS NULL"
        user = execute_query(query, (email,), fetch=True)
        
        if not user:
            return False, "Email not found or account is inactive."

        # Update password with hash
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_query = "UPDATE User SET Password = %s, UpdatedAt = NOW() WHERE Email = %s"
        execute_query(update_query, (hashed_password, email), fetch=False)
        
        return True, "Password reset successfully."
    except Exception as err:
        return False, f"Database error: {err}"


# Function to check password strength
def is_password_strong(password):
    """
    Checks if a password meets minimum security requirements.
    
    Args:
        password (str): Password to check
        
    Returns:
        bool: True if password is strong, False otherwise
    """
    # Password must be at least 8 characters, have 1 uppercase letter and 1 special character
    if len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return True
    return False


class LoginWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="#FF7F50")  # Coral background matching the design
        
        # Initialize variable for tracking current view
        self.is_signup_mode = False
        
        # Set window size to properly fit the layout
        self.master.geometry("950x650")
        self.master.minsize(950, 650)
        
        # Try to load background image (combined girl and mobile)
        try:
            background_image_path = "static/images/bg_img.png"  # Path to your combined background image
            pil_image = Image.open(background_image_path)
            self.background_image = ctk.CTkImage(light_image=pil_image, size=(950, 650))
            
            # Background Label
            self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Set a solid color as fallback
            self.configure(fg_color="#FF7F50")  # Coral background as fallback

        # Form Frame (white login box on the right)
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15, width=450, height=580)
        self.form_frame.place(relx=0.735, rely=0.5, anchor="center")
        self.form_frame.pack_propagate(False)
        
        # Initialize with the login view
        self.create_login_view()

    def clear_form_frame(self):
        """Clear all widgets in the form frame."""
        for widget in self.form_frame.winfo_children():
            widget.destroy()
            
    def add_back_button(self, parent_frame, command):
        """Add a back button to the top-left corner of the frame."""
        back_button = ctk.CTkButton(
            parent_frame,
            text="←",
            command=command,
            width=40,
            height=40,
            corner_radius=8,
            fg_color="#FF5722",
            hover_color="#E64A19",
            font=("Arial", 20, "bold")
        )
        back_button.place(x=10, y=10)

    def create_login_view(self):
        """Create Login View that resembles the Figma design while preserving functionality."""
        self.clear_form_frame()
        self.is_signup_mode = False

        # Create an inner frame to hold the form content
        self.inner_frame = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Add back button that goes to landing page
        self.add_back_button(self.inner_frame, self.master.show_landing_page)

        # Welcome Back! Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Welcome Back!", 
            font=("Arial", 24, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 30), anchor="center")
        
        # Email
        self.email_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter your email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        # Email error message (hidden initially)
        self.email_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red", 
            width=380,
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 10))

        # Password
        self.password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter your password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.password_entry.pack(pady=(0, 5), fill="x")
        
        # Password error message (hidden initially)
        self.password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red", 
            width=380,
            anchor="w"
        )
        self.password_error_label.pack(anchor="w", pady=(0, 5))

        # Show Password Checkbox 
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.inner_frame, 
            text="Show Password", 
            variable=self.show_password_var, 
            command=self.toggle_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_password_checkbox.pack(anchor="w", pady=(0, 15))

        # Login Button - Orange button that matches the design
        self.login_button = ctk.CTkButton(
            self.inner_frame, 
            text="Login", 
            command=self.login, 
            width=380, 
            height=45,
            fg_color="#FF5722",  # Orange color from the design
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(pady=(0, 20))

        # Bottom options frame for "Forgot Password?" and "Register Now"
        self.options_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 0))
        
        # Forgot Password Link - Left side
        self.forgot_password_label = ctk.CTkLabel(
            self.options_frame, 
            text="Forgot Password?", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.forgot_password_label.pack(side="left")
        self.forgot_password_label.bind("<Button-1>", lambda e: self.create_forgot_password_view())
        
        # Register Now Link - Right side
        self.register_now_label = ctk.CTkLabel(
            self.options_frame, 
            text="Register Now", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.register_now_label.pack(side="right")
        self.register_now_label.bind("<Button-1>", lambda e: self.create_signup_view())

    def create_signup_view(self):
        """Create Sign-Up View."""
        self.clear_form_frame()
        self.is_signup_mode = True

        # Create scrollable frame to accommodate all form fields
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.form_frame, 
            fg_color="white", 
            corner_radius=15,
            width=400,
            height=520
        )
        self.scrollable_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Add back button
        self.add_back_button(self.scrollable_frame, self.create_login_view)

        # Title
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Create a New Account", 
            font=("Arial", 20, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(10, 20), anchor="center")

        # First Name
        self.first_name_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="First Name", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.first_name_label.pack(anchor="w", pady=(0, 5))
        
        self.first_name_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your first name", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.first_name_entry.pack(pady=(0, 5), fill="x")
        
        self.first_name_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.first_name_error_label.pack(anchor="w", pady=(0, 5))

        # Last Name
        self.last_name_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Last Name", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.last_name_label.pack(anchor="w", pady=(0, 5))
        
        self.last_name_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your last name", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.last_name_entry.pack(pady=(0, 5), fill="x")
        
        self.last_name_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.last_name_error_label.pack(anchor="w", pady=(0, 5))

        # Email
        self.email_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        self.email_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 5))

        # Password
        self.password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.password_entry.pack(pady=(0, 5), fill="x")
        
        self.password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.password_error_label.pack(anchor="w", pady=(0, 5))
        
        # Confirm Password - NEW FIELD
        self.confirm_password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Confirm Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Confirm your password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.confirm_password_entry.pack(pady=(0, 5), fill="x")
        
        self.confirm_password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.confirm_password_error_label.pack(anchor="w", pady=(0, 5))
        
        # Show Password Checkbox 
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame, 
            text="Show Password", 
            variable=self.show_password_var, 
            command=self.toggle_signup_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_password_checkbox.pack(anchor="w", pady=(5, 5))
        
        # Password requirements hint
        self.password_hint_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password must be at least 8 characters with 1 uppercase\nletter and 1 special character", 
            font=("Arial", 10), 
            text_color="#777777",
            anchor="w"
        )
        self.password_hint_label.pack(anchor="w", pady=(0, 10))

        # User Type (Account Type)
        self.user_type_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Account Type", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.user_type_label.pack(anchor="w", pady=(0, 5))
        
        # Create a frame for radio buttons
        self.radio_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.radio_frame.pack(fill="x", pady=(0, 10))
        
        # Default role is customer
        self.user_type_var = ctk.StringVar(value="customer")
        
        # Radio buttons for user types
        self.customer_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="Customer",
            variable=self.user_type_var,
            value="customer",
            font=("Arial", 12),
            fg_color="#FF5722",
            border_color="#FF5722"
        )
        self.customer_radio.pack(side="left", padx=(0, 20))
        
        self.restaurant_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="Restaurant",
            variable=self.user_type_var,
            value="restaurant",
            font=("Arial", 12),
            fg_color="#FF5722",
            border_color="#FF5722"
        )
        self.restaurant_radio.pack(side="left")

        # Sign-Up Button
        self.signup_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Sign Up", 
            command=self.signup, 
            width=380, 
            height=45,
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.signup_button.pack(pady=(10, 15))

        # Back to Login Button - text link instead of button to match design
        self.back_to_login_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Already have an account? Login", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.back_to_login_label.pack(pady=(0, 10))
        self.back_to_login_label.bind("<Button-1>", lambda e: self.create_login_view())

    def create_forgot_password_view(self):
        """Create Forgot Password View."""
        self.clear_form_frame()

        # Create a scrollable frame to accommodate all form fields
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.form_frame, 
            fg_color="white", 
            corner_radius=15,
            width=400,
            height=520
        )
        self.scrollable_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Add back button
        self.add_back_button(self.scrollable_frame, self.create_login_view)

        # Title
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Reset Your Password", 
            font=("Arial", 20, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(10, 20), anchor="center")

        # Email
        self.email_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your registered email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        self.email_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 10))

        # New Password
        self.new_password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="New Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.new_password_label.pack(anchor="w", pady=(0, 5))
        
        self.new_password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter new password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.new_password_entry.pack(pady=(0, 5), fill="x")
        
        self.new_password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.new_password_error_label.pack(anchor="w", pady=(0, 5))

        # Confirm Password
        self.confirm_password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Confirm Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Re-enter new password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.confirm_password_entry.pack(pady=(0, 5), fill="x")
        
        # Show Password Checkbox 
        self.show_new_password_var = ctk.BooleanVar(value=False)
        self.show_new_password_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame, 
            text="Show Password", 
            variable=self.show_new_password_var, 
            command=self.toggle_new_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_new_password_checkbox.pack(anchor="w", pady=(5, 5))
        
        self.confirm_password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.confirm_password_error_label.pack(anchor="w", pady=(0, 5))
        
        # Password requirements hint
        self.password_hint_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password must be at least 8 characters with 1 uppercase\nletter and 1 special character", 
            font=("Arial", 10), 
            text_color="#777777",
            anchor="w"
        )
        self.password_hint_label.pack(anchor="w", pady=(0, 15))

        # Reset Password Button
        self.reset_password_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Reset Password", 
            command=self.reset_password, 
            width=380, 
            height=45,
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.reset_password_button.pack(pady=(10, 15))

        # Back to Login - text link
        self.back_to_login_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Back to Login", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.back_to_login_label.pack(pady=(0, 10))
        self.back_to_login_label.bind("<Button-1>", lambda e: self.create_login_view())
        
    def toggle_new_password(self):
        """Toggle new password visibility based on checkbox state."""
        if self.show_new_password_var.get():
            self.new_password_entry.configure(show="")
            self.confirm_password_entry.configure(show="")
        else:
            self.new_password_entry.configure(show="*")
            self.confirm_password_entry.configure(show="*")

    def toggle_password(self):
        """Toggle password visibility based on checkbox state."""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
            
    def toggle_signup_password(self):
        """Toggle password visibility for signup form."""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
            self.confirm_password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
            self.confirm_password_entry.configure(show="*")

    def login(self):
        """Handle login attempt."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # Reset error messages
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")
        
        # Validate input
        if not email:
            self.email_error_label.configure(text="Email is required.")
            return
        elif "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            return

        if not password:
            self.password_error_label.configure(text="Password is required.")
            return

        # Verify credentials - will only return active (not soft-deleted) users
        user = validate_user(email, password)
        if user:
            # Store user information in the main app
            self.master.current_user = user
            self.master.user_role = user['Role']
            self.master.user_id = user['UserID']
            
            # Show the appropriate dashboard
            self.master.show_dashboard()
        else:
            # Show error message for invalid credentials
            # Show error message for invalid credentials
            self.password_error_label.configure(text="Invalid email or password.")

    def signup(self):
        """Handle user registration."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        user_type = self.user_type_var.get()

        # Reset error messages
        self.first_name_error_label.configure(text="")
        self.last_name_error_label.configure(text="")
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")
        self.confirm_password_error_label.configure(text="")

        valid = True  # Validation flag
        
        # Validate first name
        if not first_name:
            self.first_name_error_label.configure(text="First Name is required.")
            valid = False

        # Validate last name
        if not last_name:
            self.last_name_error_label.configure(text="Last Name is required.")
            valid = False
            
        # Validate email
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            valid = False
            
        # Validate password strength
        if not is_password_strong(password):
            self.password_error_label.configure(
                text="Password must meet all requirements."
            )
            valid = False
            
        # Check if passwords match
        if password != confirm_password:
            self.confirm_password_error_label.configure(text="Passwords don't match.")
            valid = False

        if valid:
            # If all fields are valid, attempt to create the user
            if register_user(first_name, last_name, email, password, user_type):
                # Use the CTkMessagebox instead of standard messagebox
                CTkMessagebox(
                    title="Account Created", 
                    message="Your account has been created successfully.\nPlease login with your credentials.", 
                    icon="check",
                    option_1="OK"
                )
                self.create_login_view()  # Redirect to login view on success
            else:
                self.email_error_label.configure(text="Email already exists or registration failed.")

    def reset_password(self):
        """Handle password reset request."""
        email = self.email_entry.get().strip()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Reset error labels
        self.email_error_label.configure(text="")
        self.new_password_error_label.configure(text="")
        self.confirm_password_error_label.configure(text="")

        valid = True  # Validation flag

        # Validate email
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Enter a valid email address.")
            valid = False

        # Validate new password
        if not new_password or not is_password_strong(new_password):
            self.new_password_error_label.configure(
                text="Password must meet all requirements."
            )
            valid = False

        # Validate password match
        if new_password != confirm_password:
            self.confirm_password_error_label.configure(text="Passwords do not match.")
            valid = False

        if valid:
            success, message = reset_password_logic(email, new_password)
            if success:
                CTkMessagebox(
                    title="Password Reset", 
                    message="Your password has been reset successfully.", 
                    icon="check",
                    option_1="OK"
                )
                self.create_login_view()  # Redirect to login view on success
            else:
                self.email_error_label.configure(text=message)

# Function to create a custom message box with properly aligned buttons
def custom_messagebox(title, message, icon="info", option_1="OK", option_2=None):
    msg_box = CTkMessagebox(
        title=title,
        message=message,
        icon=icon,
        option_1=option_1,
        option_2=option_2
    )
    
    # Fix button alignment - find the button container and adjust
    for child in msg_box.winfo_children():
        if isinstance(child, ctk.CTkFrame):
            for inner_child in child.winfo_children():
                if isinstance(inner_child, ctk.CTkFrame) and inner_child.winfo_children() and isinstance(inner_child.winfo_children()[0], ctk.CTkButton):
                    button_container = inner_child
                    button_container.configure(fg_color="transparent")
                    
                    # Center the buttons
                    for button in button_container.winfo_children():
                        if isinstance(button, ctk.CTkButton):
                            button.pack_forget()
                    
                    # Repack the buttons centered
                    buttons = [b for b in button_container.winfo_children() if isinstance(b, ctk.CTkButton)]
                    for button in buttons:
                        button.pack(side="left", padx=10, pady=5, expand=True, fill="none")
    
    return msg_box.get()

# If module is run directly
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x600")
    app.title("Food Ordering System - Login")
    login_window = LoginWindow(app)
    login_window.pack(expand=True, fill="both")
    app.mainloop()