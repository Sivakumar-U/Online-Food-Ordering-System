import customtkinter as ctk
from custom.auth import LoginWindow  # Import the login window to handle user authentication
from utils import connect_to_database  # Import the database connection utility
from tkinter import messagebox
from PIL import Image
import bcrypt
from datetime import datetime

# Function to create the required tables for the Online Food Ordering system
def create_tables():
    """
    Creates the necessary tables for the Online Food Ordering System.
    Tables include User, Restaurant, Menu, Order, OrderItem, and Delivery.
    Added soft delete functionality and additional fields for profile features.
    """
    queries = {
        "users": """
            CREATE TABLE IF NOT EXISTS User (
                UserID INT NOT NULL AUTO_INCREMENT,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Email VARCHAR(100) NOT NULL UNIQUE,
                Password VARCHAR(255) NOT NULL,
                Phone VARCHAR(20),
                Address VARCHAR(255),
                DeliveryInstructions TEXT,
                Role VARCHAR(20) NOT NULL DEFAULT 'customer',
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (UserID)
            );
        """,
        "restaurants": """
            CREATE TABLE IF NOT EXISTS Restaurant (
                RestaurantID INT NOT NULL AUTO_INCREMENT,
                Name VARCHAR(100) NOT NULL,
                Cuisine VARCHAR(50),
                Contact VARCHAR(50),
                Location VARCHAR(100),
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (RestaurantID)
            );
        """,
        "restaurant_owners": """
            CREATE TABLE IF NOT EXISTS RestaurantOwner (
                ID INT NOT NULL AUTO_INCREMENT,
                UserID INT NOT NULL,
                RestaurantID INT NOT NULL,
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (ID),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
            );
        """,
        "menus": """
            CREATE TABLE IF NOT EXISTS Menu (
                MenuID INT NOT NULL AUTO_INCREMENT,
                RestaurantID INT NOT NULL,
                ItemName VARCHAR(100) NOT NULL,
                Description TEXT,
                Price DECIMAL(10, 2) NOT NULL,
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (MenuID),
                FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
            );
        """,
        "orders": """
            CREATE TABLE IF NOT EXISTS `Order` (
                OrderID INT NOT NULL AUTO_INCREMENT,
                UserID INT NOT NULL,
                RestaurantID INT NOT NULL,
                TotalAmount DECIMAL(10, 2) NOT NULL,
                OrderStatus VARCHAR(20) NOT NULL DEFAULT 'pending',
                OrderDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (OrderID),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
            );
        """,
        "order_items": """
            CREATE TABLE IF NOT EXISTS OrderItem (
                OrderItemID INT NOT NULL AUTO_INCREMENT,
                OrderID INT NOT NULL,
                MenuID INT NOT NULL,
                Quantity INT NOT NULL,
                Subtotal DECIMAL(10, 2) NOT NULL,
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (OrderItemID),
                FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
                FOREIGN KEY (MenuID) REFERENCES Menu(MenuID) ON DELETE CASCADE
            );
        """,
        "delivery": """
            CREATE TABLE IF NOT EXISTS Delivery (
                DeliveryID INT NOT NULL AUTO_INCREMENT,
                OrderID INT NOT NULL,
                PersonnelID INT NOT NULL,
                DeliveryStatus VARCHAR(20) NOT NULL DEFAULT 'pending',
                EstimatedTime DATETIME,
                IsActive BOOLEAN NOT NULL DEFAULT TRUE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                DeletedAt TIMESTAMP NULL,
                PRIMARY KEY (DeliveryID),
                FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
                FOREIGN KEY (PersonnelID) REFERENCES User(UserID) ON DELETE CASCADE
            );
        """,
        "settings": """
            CREATE TABLE IF NOT EXISTS UserSettings (
                SettingID INT NOT NULL AUTO_INCREMENT,
                UserID INT NOT NULL,
                SettingName VARCHAR(50) NOT NULL,
                SettingValue BOOLEAN NOT NULL DEFAULT FALSE,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (SettingID),
                UNIQUE KEY unique_user_setting (UserID, SettingName),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
        """
    }

    conn = None
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            for table_name, query in queries.items():
                cursor.execute(query)
            conn.commit()
            print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# Function to add sample data to the database
def add_sample_data():
    """Add sample data to the database tables."""
    conn = None
    try:
        conn = connect_to_database()
        if not conn:
            print("Failed to connect to database")
            return
            
        cursor = conn.cursor()
        
        # Check if sample data already exists
        cursor.execute("SELECT COUNT(*) FROM User")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print("Sample data already exists")
            return
            
        # Add sample users
        hashed_password = bcrypt.hashpw("Password123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sample_users = [
            # Format: FirstName, LastName, Email, Password, Phone, Address, Role
            ("John", "Doe", "john@food.com", hashed_password, "555-123-4567", "123 Main St, Chicago, IL 60601", "customer"),
            ("Jane", "Smith", "jane@food.com", hashed_password, "555-987-6543", "456 Oak Ave, New York, NY 10001", "customer"),
            ("Admin", "User", "admin@food.com", hashed_password, "555-111-2222", "789 Admin St, San Francisco, CA 94105", "admin"),
            ("Rest", "Owner", "restaurant@food.com", hashed_password, "555-444-5555", "321 Chef Blvd, Miami, FL 33101", "restaurant"),
            ("Delivery", "Person", "delivery@food.com", hashed_password, "555-777-8888", "555 Delivery Rd, Austin, TX 78701", "customer")
        ]
        
        user_query = """
            INSERT INTO User (FirstName, LastName, Email, Password, Phone, Address, Role) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(user_query, sample_users)
        
        # Add default user settings
        settings_query = """
            INSERT INTO UserSettings (UserID, SettingName, SettingValue)
            VALUES (%s, %s, %s)
        """
        
        # Default settings for John
        default_settings = [
            # UserID 1 (John Doe) settings
            (1, "Notifications", True),
            (1, "DarkMode", False),
            (1, "AutoSaveAddress", True),
            (1, "SavePaymentInfo", False),
            # UserID 2 (Jane Smith) settings
            (2, "Notifications", True),
            (2, "DarkMode", False),
            (2, "AutoSaveAddress", True),
            (2, "SavePaymentInfo", False)
        ]
        cursor.executemany(settings_query, default_settings)
        
        # Add sample restaurants
        sample_restaurants = [
            ("Pizza Palace", "Italian", "555-1234", "123 Main St"),
            ("Burger Haven", "American", "555-5678", "456 Oak Ave"),
            ("Sweet Treats", "Desserts", "555-9012", "789 Maple Dr"),
            ("Sushi Spot", "Japanese", "555-3456", "321 Pine Rd"),
            ("Taco Town", "Mexican", "555-7890", "654 Elm St")
        ]
        
        restaurant_query = """
            INSERT INTO Restaurant (Name, Cuisine, Contact, Location)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(restaurant_query, sample_restaurants)
        
        # Link restaurant owner (UserID 4) to Restaurant 1 (Pizza Palace)
        restaurant_owner_query = """
            INSERT INTO RestaurantOwner (UserID, RestaurantID)
            VALUES (%s, %s)
        """
        cursor.execute(restaurant_owner_query, (4, 1))  # User ID 4 (Rest Owner) linked to Restaurant ID 1
        
        # Add sample menu items
        sample_menu_items = [
            # Pizza Palace (RestaurantID 1)
            (1, "Margherita Pizza", "Classic cheese and tomato pizza", 12.99),
            (1, "Pepperoni Pizza", "Pizza with pepperoni toppings", 14.99),
            (1, "Vegetarian Pizza", "Pizza with assorted vegetables", 13.99),
            # Burger Haven (RestaurantID 2)
            (2, "Classic Cheeseburger", "Beef patty with cheese", 9.99),
            (2, "Bacon Burger", "Burger with bacon and cheese", 11.99),
            (2, "Veggie Burger", "Plant-based patty with vegetables", 10.99),
            # Sweet Treats (RestaurantID 3)
            (3, "Chocolate Cake", "Rich chocolate cake with frosting", 5.99),
            (3, "Ice Cream Sundae", "Vanilla ice cream with toppings", 4.99),
            (3, "Apple Pie", "Homemade apple pie with cinnamon", 6.99),
            # Sushi Spot (RestaurantID 4)
            (4, "California Roll", "Crab, avocado and cucumber roll", 8.99),
            (4, "Salmon Nigiri", "Fresh salmon over rice", 7.99),
            (4, "Tempura Roll", "Shrimp tempura and vegetables", 9.99),
            # Taco Town (RestaurantID 5)
            (5, "Beef Taco", "Seasoned beef in a corn tortilla", 3.99),
            (5, "Chicken Quesadilla", "Grilled chicken and cheese in a flour tortilla", 7.99),
            (5, "Veggie Burrito", "Bean and rice burrito with vegetables", 6.99)
        ]
        
        menu_query = """
            INSERT INTO Menu (RestaurantID, ItemName, Description, Price)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(menu_query, sample_menu_items)
        
        # Add sample orders and order items
        # First order for John Doe (UserID 1)
        cursor.execute("""
            INSERT INTO `Order` (UserID, RestaurantID, TotalAmount, OrderStatus, OrderDate)
            VALUES (1, 1, 27.98, 'delivered', DATE_SUB(NOW(), INTERVAL 2 DAY))
        """)
        order_id_1 = cursor.lastrowid
        
        # Order items for first order
        order_items_1 = [
            (order_id_1, 1, 1, 12.99),  # Margherita Pizza
            (order_id_1, 2, 1, 14.99)   # Pepperoni Pizza
        ]
        
        order_items_query = """
            INSERT INTO OrderItem (OrderID, MenuID, Quantity, Subtotal)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(order_items_query, order_items_1)
        
        # Second order for John Doe (UserID 1)
        cursor.execute("""
            INSERT INTO `Order` (UserID, RestaurantID, TotalAmount, OrderStatus, OrderDate)
            VALUES (1, 2, 21.98, 'delivered', DATE_SUB(NOW(), INTERVAL 1 DAY))
        """)
        order_id_2 = cursor.lastrowid
        
        # Order items for second order
        order_items_2 = [
            (order_id_2, 4, 1, 9.99),   # Classic Cheeseburger
            (order_id_2, 5, 1, 11.99)   # Bacon Burger
        ]
        cursor.executemany(order_items_query, order_items_2)
        
        # Third order for John Doe (UserID 1) - current order
        cursor.execute("""
            INSERT INTO `Order` (UserID, RestaurantID, TotalAmount, OrderStatus, OrderDate)
            VALUES (1, 3, 17.97, 'preparing', NOW())
        """)
        order_id_3 = cursor.lastrowid
        
        # Order items for third order
        order_items_3 = [
            (order_id_3, 7, 1, 5.99),   # Chocolate Cake
            (order_id_3, 8, 1, 4.99),   # Ice Cream Sundae
            (order_id_3, 9, 1, 6.99)    # Apple Pie
        ]
        cursor.executemany(order_items_query, order_items_3)
        
        # Add delivery for the orders
        delivery_query = """
            INSERT INTO Delivery (OrderID, PersonnelID, DeliveryStatus, EstimatedTime)
            VALUES (%s, %s, %s, %s)
        """
        
        # Deliveries
        deliveries = [
            (order_id_1, 5, 'delivered', '2025-04-12 15:30:00'),
            (order_id_2, 5, 'delivered', '2025-04-13 18:45:00'),
            (order_id_3, 5, 'pending', '2025-04-14 19:30:00')
        ]
        cursor.executemany(delivery_query, deliveries)
        
        # Commit changes
        conn.commit()
        print("Sample data added successfully!")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Function to center any window
def center_window(window, width=800, height=650):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


# Initialize the CustomTkinter application with a landing page
class FoodOrderingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Online Food Ordering System")
        self.geometry("800x650")
        self.resizable(False,False)
        center_window(self)  # Center the main application window
        
        # Set the application theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # User session data
        self.current_user = None
        self.user_role = None
        self.user_id = None
        
        # Start with the landing page
        self.show_landing_page()

    def show_landing_page(self):
        """Display the landing page."""
        self.clear_window()
        landing_page = LandingPage(master=self)
        landing_page.pack(expand=True, fill="both")

    def show_login_window(self):
        """Display the login window."""
        self.clear_window()
        login_window = LoginWindow(master=self)
        login_window.pack(expand=True, fill="both")
    
    def show_dashboard(self):
        """Display the appropriate dashboard based on user role."""
        self.clear_window()  # Clear the current content
        
        if self.user_role == "admin":
            from custom.admin_dashboard import AdminDashboard
            self.dashboard = AdminDashboard(master=self, user_id=self.current_user["UserID"])
        elif self.user_role == "restaurant":
            from custom.restaurant_dashboard import RestaurantDashboard
            self.dashboard = RestaurantDashboard(master=self, user_id=self.current_user["UserID"])
        else:  # default to user/customer
            from custom.user_dashboard import UserDashboard
            self.dashboard = UserDashboard(master=self, user_id=self.current_user["UserID"])
        
        # Store user ID for easy access
        self.user_id = self.current_user["UserID"]
        
        # Place the dashboard in the window
        self.dashboard.pack(fill="both", expand=True)

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.winfo_children():
            widget.destroy()
            
    def sign_out(self):
        """Log out the current user and return to landing page."""
        # Confirm sign out
        from CTkMessagebox import CTkMessagebox
        confirm = CTkMessagebox(
            title="Sign Out",
            message="Are you sure you want to sign out?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        if confirm.get() == "Yes":
            self.current_user = None
            self.user_role = None
            self.user_id = None
            self.show_landing_page()


# Landing Page
class LandingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="white")

        # Background Image
        try:
            background_image_path = "static/images/landing_page_bg.jpg"
            pil_image = Image.open(background_image_path).resize((800, 650))
            self.background_image = ctk.CTkImage(light_image=pil_image, size=(800, 650))
            
            # Background Label
            self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Fallback to plain background
            self.configure(fg_color="#ffaa66")

        # Page title
        # self.title_label = ctk.CTkLabel(
        #     self,
        #     text="Food Delivery Made Easy",
        #     font=("Arial", 28, "bold"),
        #     text_color="#ffffff",
        #     bg_color="transparent"
        # )
        # self.title_label.place(relx=0.5, rely=0.2, anchor="center")

        # # Subtitle
        # self.subtitle_label = ctk.CTkLabel(
        #     self,
        #     text="Order food from your favorite restaurants",
        #     font=("Arial", 16),
        #     text_color="#ffffff",
        #     bg_color="transparent"
        # )
        # self.subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

        # Get Started Button
        self.get_started_button = ctk.CTkButton(
            self,
            text="Get Started",
            command=self.open_login_window,
            width=250,
            height=70,
            corner_radius=0,
            fg_color="#FF5722",
            hover_color="#E64A19",
            bg_color="transparent",
            font=("Arial", 14, "bold")
        )
        self.get_started_button.place(relx=0.2, rely=0.71, anchor="center")  

    def open_login_window(self):
        """Open the login window."""
        self.master.show_login_window()


# Main function to start the application
def main():
    # Create necessary tables
    create_tables()
    
    # Add sample data
    add_sample_data()

    # Start the application
    app = FoodOrderingApp()
    app.mainloop()


if __name__ == "__main__":
    main()