import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime
from custom.navigation_frame_user import NavigationFrameUser
from utils import connect_to_database, execute_query
from CTkMessagebox import CTkMessagebox

class UserDashboard(ctk.CTkFrame):
    """Dashboard for regular customers to browse restaurants and place orders."""
    def __init__(self, master, user_id=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store user information
        self.master = master
        self.user_id = user_id
        self.user_data = self.get_user_data()
        
        # Initialize shopping cart
        self.cart = []
        
        # Configure this frame
        self.configure(fg_color="#f5f5f5")
        
        # Create main content container (all screens will be placed here)
        self.content_container = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)
        
        # Create and place navigation at bottom
        self.navigation_frame = NavigationFrameUser(self, user_id=self.user_id)
        self.navigation_frame.pack(side="bottom", fill="x")
        
        # Initialize frames for different screens
        self.home_frame = HomeFrame(self.content_container, self)
        self.orders_frame = OrdersFrame(self.content_container, self)
        self.cart_frame = CartFrame(self.content_container, self)
        self.profile_frame = ProfileFrame(self.content_container, self)
        self.settings_frame = SettingsFrame(self.content_container, self)
        
        # Also add restaurant menu frame (not directly accessible from navigation)
        self.restaurant_menu_frame = RestaurantMenuFrame(self.content_container, self)
        
        # Show default frame (home)
        self.show_frame("home")
        
    def get_user_data(self):
        """Fetch user data from database."""
        if not self.user_id:
            return {"FirstName": "User", "LastName": ""}
        
        query = "SELECT * FROM User WHERE UserID = %s"
        result = execute_query(query, (self.user_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return {"FirstName": "User", "LastName": ""}
    
    def show_frame(self, frame_name, **kwargs):
        """Show selected frame and hide others."""
        # Hide all frames
        for frame in [self.home_frame, self.orders_frame, self.cart_frame, 
                     self.profile_frame, self.settings_frame, self.restaurant_menu_frame]:
            frame.pack_forget()
        
        # Show selected frame
        if frame_name == "home":
            self.home_frame.pack(fill="both", expand=True)
        elif frame_name == "orders":
            self.orders_frame.refresh_orders()
            self.orders_frame.pack(fill="both", expand=True)
        elif frame_name == "cart":
            self.cart_frame.refresh_cart()
            self.cart_frame.pack(fill="both", expand=True)
        elif frame_name == "profile":
            self.profile_frame.pack(fill="both", expand=True)
        elif frame_name == "settings":
            self.settings_frame.pack(fill="both", expand=True)
        elif frame_name == "restaurant_menu":
            restaurant_id = kwargs.get("restaurant_id")
            if restaurant_id:
                self.restaurant_menu_frame.load_restaurant(restaurant_id)
            self.restaurant_menu_frame.pack(fill="both", expand=True)
    
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
            
    def get_image_path(self, filename, folder='restaurant'):
        """
        Get the full path to an image file.
        
        :param filename: Name of the image file
        :param folder: Subfolder in static/images (restaurant or menu)
        :return: Full path to the image
        """
        base_path = os.path.join('static', 'images', folder)
        full_path = os.path.join(base_path, filename)
        
        # Fallback image if specific image not found
        if not os.path.exists(full_path):
            fallback_path = os.path.join(base_path, 'default.png')
            if os.path.exists(fallback_path):
                return fallback_path
            return None
        
        return full_path
class HomeFrame(ctk.CTkScrollableFrame):
    """Home screen with restaurant listings and search functionality."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title section
        self.title_label = ctk.CTkLabel(
            self, 
            text="Find Your Favorite Food",
            font=("Arial", 20, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Search bar
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search for restaurants or dishes...",
            width=350,
            height=40,
            corner_radius=8,
            border_color="#e0e0e0"
        )
        self.search_entry.pack(pady=(0, 15))
        self.search_entry.bind("<Return>", lambda e: self.search_restaurants())
        
        # Category buttons in horizontal row
        self.categories_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.categories_frame.pack(pady=(0, 15))
        
        # Get available cuisines from database
        cuisines = self.get_cuisines()
        if not cuisines:
            cuisines = ["FastFood", "Desserts", "Healthy", "Indian", "Chinese"]
        
        # Colors for category buttons
        colors = ["#22C55E", "#FF9800", "#F44336", "#FFC107", "#9C27B0"]
        
        # Create "All Restaurants" button first with distinct color
        all_btn = ctk.CTkButton(
            self.categories_frame,
            text="All Restaurants",
            fg_color="#3498db",  # Blue color for distinction
            hover_color="#2980b9",
            corner_radius=15,
            width=120,  # Make it wider than other category buttons
            height=30,
            command=lambda: self.load_restaurants()
        )
        all_btn.pack(side="left", padx=5)
        
        # Create category buttons
        for i, cuisine in enumerate(cuisines[:5]):  # Limit to 5 categories
            color = colors[i % len(colors)]
            btn = ctk.CTkButton(
                self.categories_frame,
                text=cuisine,
                fg_color=color,
                hover_color=self.adjust_color_brightness(color, -20),
                corner_radius=15,
                width=80,
                height=30,
                command=lambda c=cuisine: self.filter_by_cuisine(c)
            )
            btn.pack(side="left", padx=5)
        
        # Create a frame for the restaurant grid
        self.restaurants_container = ctk.CTkFrame(self, fg_color="transparent")
        self.restaurants_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid columns for restaurants (3 columns)
        for i in range(3):
            self.restaurants_container.columnconfigure(i, weight=1, uniform="column")
        
        # Load all restaurants by default
        self.load_restaurants()
    

    
    def get_cuisines(self):
        """Get unique cuisines from the database."""
        query = "SELECT DISTINCT Cuisine FROM Restaurant WHERE Cuisine IS NOT NULL AND Cuisine != ''"
        result = execute_query(query, fetch=True)
        if result:
            return [item["Cuisine"] for item in result]
        return []
    
    def adjust_color_brightness(self, hex_color, brightness_offset=0):
        """Adjust the brightness of a hex color."""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust brightness
        rgb = tuple(max(0, min(255, c + brightness_offset)) for c in rgb)
        
        # Convert back to hex
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def search_restaurants(self):
        """Search restaurants by name or menu items."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_restaurants()
            return
            
        # Search in restaurant names and menu items
        query = """
            SELECT DISTINCT r.* FROM Restaurant r
            LEFT JOIN Menu m ON r.RestaurantID = m.RestaurantID
            WHERE r.Name LIKE %s OR m.ItemName LIKE %s OR r.Cuisine LIKE %s
        """
        search_pattern = f"%{search_term}%"
        restaurants = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True)
        
        # Clear existing restaurants
        for widget in self.restaurants_container.winfo_children():
            widget.destroy()
        
        if restaurants and len(restaurants) > 0:
            # Create a restaurant card for each restaurant in grid layout
            row_size = 3  # Number of restaurants per row
            for i, restaurant in enumerate(restaurants):
                row = i // row_size
                col = i % row_size
                self.create_restaurant_card(restaurant, i, row, col)
        else:
            # No results found
            no_results = ctk.CTkLabel(
                self.restaurants_container,
                text="No restaurants found matching your search.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_results.grid(row=0, column=0, columnspan=3, pady=50)
    
    def filter_by_cuisine(self, cuisine):
        """Filter restaurants by cuisine."""
        query = "SELECT * FROM Restaurant WHERE Cuisine = %s"
        restaurants = execute_query(query, (cuisine,), fetch=True)
        
        # Clear existing restaurants
        for widget in self.restaurants_container.winfo_children():
            widget.destroy()
        
        if restaurants and len(restaurants) > 0:
            # Create a restaurant card for each restaurant in grid layout
            row_size = 3  # Number of restaurants per row
            for i, restaurant in enumerate(restaurants):
                row = i // row_size
                col = i % row_size
                self.create_restaurant_card(restaurant, i, row, col)
        else:
            # No results found
            no_results = ctk.CTkLabel(
                self.restaurants_container,
                text=f"No restaurants found with cuisine: {cuisine}",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_results.grid(row=0, column=0, columnspan=3, pady=50)
    
    def load_restaurants(self):
        """Load all restaurants."""
        # Clear existing restaurants
        for widget in self.restaurants_container.winfo_children():
            widget.destroy()
        
        # Get restaurants from database
        restaurants = self.get_restaurants()
        
        if not restaurants:
            # No restaurants found
            no_results = ctk.CTkLabel(
                self.restaurants_container,
                text="No restaurants available.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_results.grid(row=0, column=0, columnspan=3, pady=50)
            return
        
        # Create a restaurant card for each restaurant in a grid layout
        row_size = 3  # Number of restaurants per row
        for i, restaurant in enumerate(restaurants):
            row = i // row_size
            col = i % row_size
            self.create_restaurant_card(restaurant, i, row, col)
    
    def get_restaurants(self):
        """Fetch restaurant data from database."""
        query = "SELECT * FROM Restaurant ORDER BY Name"
        return execute_query(query, fetch=True) or []
    
    def create_restaurant_card(self, restaurant, index, row=0, col=0):
        """Create a card displaying restaurant information with actual image."""
        # Main card frame - with shadow effect using nested frames
        outer_card = ctk.CTkFrame(self.restaurants_container, fg_color="#f5f5f5", corner_radius=15)
        
        # Position the card in the grid
        outer_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Inner card with white background
        card = ctk.CTkFrame(outer_card, fg_color="white", corner_radius=15, width=300, height=350)
        card.pack(padx=2, pady=2)  # Small padding creates shadow effect
        
        # Store restaurant ID for click handling
        outer_card.restaurant_id = restaurant["RestaurantID"]
        card.restaurant_id = restaurant["RestaurantID"]
        
        # Restaurant image area - grey placeholder
        image_frame = ctk.CTkFrame(card, width=300, height=180, fg_color="#e0e0e0", corner_radius=10)
        image_frame.pack(padx=0, pady=0)
        image_frame.restaurant_id = restaurant["RestaurantID"]
        
        # Try to load restaurant image
        image_filename = f"restaurant_{restaurant['RestaurantID']}.png"
        image_path = self.controller.get_image_path(image_filename)
        
        if image_path:
            try:
                # Use CTkImage for proper scaling
                image = ctk.CTkImage(
                    light_image=Image.open(image_path),
                    size=(300, 180)
                )
                
                # Create label with image
                image_label = ctk.CTkLabel(
                    image_frame, 
                    image=image, 
                    text=""
                )
                image_label.pack(fill="both", expand=True)
                image_label.restaurant_id = restaurant["RestaurantID"]
            except Exception as e:
                print(f"Error loading image: {e}")
                # Fallback to placeholder if image fails to load
                name_label = ctk.CTkLabel(
                    image_frame,
                    text=f"Restaurant {restaurant['RestaurantID']}",
                    font=("Arial", 16),
                    text_color="#888888"
                )
                name_label.place(relx=0.5, rely=0.5, anchor="center")
                name_label.restaurant_id = restaurant["RestaurantID"]
        else:
            # No image found, use grey placeholder with text
            name_label = ctk.CTkLabel(
                image_frame,
                text=f"Restaurant {restaurant['RestaurantID']}",
                font=("Arial", 16),
                text_color="#888888"
            )
            name_label.place(relx=0.5, rely=0.5, anchor="center")
            name_label.restaurant_id = restaurant["RestaurantID"]
        
        # Restaurant name (large, bold)
        name_label = ctk.CTkLabel(
            card,
            text=restaurant["Name"],
            font=("Arial", 16, "bold"),
            text_color="#333333",
            anchor="w"
        )
        name_label.pack(anchor="w", padx=15, pady=(10, 0))
        name_label.restaurant_id = restaurant["RestaurantID"]
        
        # Star rating display
        ratings = {"Pizza Place": 4.4, "Burger Haven": 4.5, "Sweet Treats": 3.5}
        rating_value = ratings.get(restaurant["Name"], round(3.5 + (index % 15) / 10, 1))  # Fallback to generated rating
        
        # Create star rating with Unicode stars
        rating_text = ""
        for i in range(5):
            if i < int(rating_value):
                rating_text += "★"  # Full star
            elif i < rating_value:
                rating_text += "★"  # Should be half star but using full for simplicity
            else:
                rating_text += "☆"  # Empty star
                
        rating_frame = ctk.CTkFrame(card, fg_color="transparent")
        rating_frame.pack(fill="x", anchor="w", padx=15, pady=(5, 0))
        rating_frame.restaurant_id = restaurant["RestaurantID"]
        
        rating_stars = ctk.CTkLabel(
            rating_frame,
            text=rating_text,
            font=("Arial", 14),
            text_color="#FFC107",  # Yellow for stars
            anchor="w"
        )
        rating_stars.pack(side="left")
        rating_stars.restaurant_id = restaurant["RestaurantID"]
        
        rating_number = ctk.CTkLabel(
            rating_frame,
            text=f"({rating_value})",
            font=("Arial", 12),
            text_color="#666666",
            anchor="w"
        )
        rating_number.pack(side="left", padx=(5, 0))
        rating_number.restaurant_id = restaurant["RestaurantID"]
        
        # Delivery time 
        delivery_times = {"Pizza Place": 30, "Burger Haven": 25, "Sweet Treats": 20}
        delivery_time = delivery_times.get(restaurant["Name"], 20 + (index % 3) * 5)
        
        delivery_label = ctk.CTkLabel(
            card,
            text=f"Estimated Delivery: {delivery_time} mins",
            font=("Arial", 12),
            text_color="#555555",
            anchor="w"
        )
        delivery_label.pack(anchor="w", padx=15, pady=(5, 10))
        delivery_label.restaurant_id = restaurant["RestaurantID"]
        
        # View menu button
        view_menu_btn = ctk.CTkButton(
            card,
            text="View Menu",
            command=lambda r_id=restaurant["RestaurantID"]: self.view_restaurant_menu(r_id),
            fg_color="#22C55E",
            hover_color="#1DA346",
            corner_radius=8,
            width=270,
            height=35
        )
        view_menu_btn.pack(padx=15, pady=(10, 15))
        
        # Direct click handler without binding
        def on_card_click(event):
            r_id = getattr(event.widget, "restaurant_id", None)
            if r_id:
                self.view_restaurant_menu(r_id)
        
        # Bind events to the card and outer card only (not all child widgets)
        outer_card.bind("<Button-1>", on_card_click)
        card.bind("<Button-1>", on_card_click)
        
        # Simplified hover effect - only change the outer card color
        outer_card.bind("<Enter>", lambda e: outer_card.configure(cursor="hand2"))
        outer_card.bind("<Leave>", lambda e: outer_card.configure(cursor=""))
    
    def view_restaurant_menu(self, restaurant_id):
        """Open the restaurant menu screen."""
        self.controller.show_frame("restaurant_menu", restaurant_id=restaurant_id)

class RestaurantMenuFrame(ctk.CTkScrollableFrame):
    """Restaurant menu screen showing available food items."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        self.current_restaurant_id = None
        
        # Top section with back button and banner
        self.top_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#e0e0e0", height=150)
        self.top_frame.pack(fill="x", pady=(0, 10))
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.top_frame,
            text="Back",
            command=lambda: controller.show_frame("home"),
            fg_color="#22C55E",
            hover_color="#1DA346",
            corner_radius=15,
            width=80,
            height=30
        )
        self.back_button.pack(anchor="nw", padx=15, pady=15)
        
        # Restaurant banner label
        self.banner_label = ctk.CTkLabel(
            self.top_frame,
            text="Restaurant Banner",
            font=("Arial", 24),
            text_color="#888888"
        )
        self.banner_label.pack(pady=10)
        
        # Menu label
        self.menu_label = ctk.CTkLabel(
            self,
            text="Menu",
            font=("Arial", 20, "bold"),
            text_color="#333333"
        )
        self.menu_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Menu items container
        self.menu_items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_items_frame.pack(fill="both", expand=True, padx=10)
    
    # Update the load_restaurant method in RestaurantMenuFrame class
    def load_restaurant(self, restaurant_id):
        """Load restaurant information and menu items."""
        self.current_restaurant_id = restaurant_id
        
        # Get restaurant data
        restaurant = self.get_restaurant_data(restaurant_id)
        if restaurant:
            # Update top frame with restaurant banner
            self.top_frame.configure(height=180)
            
            # Clear any existing banner content
            for widget in self.top_frame.winfo_children():
                widget.destroy()
                
            # Back button
            self.back_button = ctk.CTkButton(
                self.top_frame,
                text="Back to Home",
                command=lambda: self.controller.show_frame("home"),
                fg_color="#22C55E",
                hover_color="#1DA346",
                corner_radius=8,
                width=120,
                height=30
            )
            self.back_button.pack(anchor="nw", padx=15, pady=15)
            
            # Try to load restaurant banner image
            image_filename = f"restaurant_{restaurant_id}.png"
            image_path = self.controller.get_image_path(image_filename)
            
            if image_path:
                try:
                    # Load and resize image
                    banner_image = ctk.CTkImage(
                        light_image=Image.open(image_path),
                        size=(400, 150)
                    )
                    banner_label = ctk.CTkLabel(
                        self.top_frame, 
                        image=banner_image, 
                        text=""
                    )
                    banner_label.pack(expand=True, fill="both", padx=15, pady=(0, 15))
                except Exception as e:
                    print(f"Error loading banner: {e}")
                    # Fallback to text banner
                    self.banner_label = ctk.CTkLabel(
                        self.top_frame,
                        text=restaurant['Name'],
                        font=("Arial", 24, "bold"),
                        text_color="#333333"
                    )
                    self.banner_label.pack(pady=10)
            else:
                # No image, use text banner
                self.banner_label = ctk.CTkLabel(
                    self.top_frame,
                    text=restaurant['Name'],
                    font=("Arial", 24, "bold"),
                    text_color="#333333"
                )
                self.banner_label.pack(pady=10)
            
            # Restaurant details below banner
            details_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
            details_frame.pack(fill="x", padx=15, pady=10)
            
            details_label = ctk.CTkLabel(
                details_frame,
                text=f"Cuisine: {restaurant.get('Cuisine', 'Various')} • {restaurant.get('Location', 'Local Area')}",
                font=("Arial", 14),
                text_color="#555555"
            )
            details_label.pack(pady=10)
            
            # Menu label
            self.menu_label = ctk.CTkLabel(
                self,
                text="Menu Items",
                font=("Arial", 20, "bold"),
                text_color="#333333"
            )
            self.menu_label.pack(anchor="w", padx=15, pady=(10, 5))
            
            # Clear existing menu items
            for widget in self.menu_items_frame.winfo_children():
                widget.destroy()
            
            # Load menu items
            menu_items = self.get_menu_items(restaurant_id)
            
            if not menu_items:
                no_menu = ctk.CTkLabel(
                    self.menu_items_frame,
                    text="No menu items available for this restaurant.",
                    font=("Arial", 14),
                    text_color="#999999"
                )
                no_menu.pack(pady=50)
                return
            
            # Create menu item grid
            self.create_menu_grid(self.menu_items_frame, menu_items)
    
    def create_menu_grid(self, parent, items):
        """Create a grid of menu items."""
        # Configure grid for 3 items per row
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1, uniform="column")
        
        # Create menu items
        for i, item in enumerate(items):
            row = i // 3
            col = i % 3
            self.create_menu_item(parent, item, row, col)
    
    def create_menu_item(self, parent, item, row, col):
        """Create a menu item card with actual image."""
        # Item frame
        item_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="white", width=100, height=200)
        item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Item image
        image_frame = ctk.CTkFrame(item_frame, width=100, height=100, fg_color="#e0e0e0")
        image_frame.pack(fill="x", padx=5, pady=5)
        
        # Try to load menu item image
        image_filename = f"menu_item_{item['MenuID']}.jpg"
        image_path = self.controller.get_image_path(image_filename, folder='menu')
        
        if image_path:
            try:
                # Load and resize image
                image = ctk.CTkImage(
                    light_image=Image.open(image_path),
                    size=(100, 100)
                )
                image_label = ctk.CTkLabel(
                    image_frame, 
                    image=image, 
                    text=""
                )
                image_label.pack(expand=True, fill="both")
            except Exception as e:
                # Fallback to text placeholder if image loading fails
                placeholder_label = ctk.CTkLabel(
                    image_frame,
                    text="Food",
                    font=("Arial", 20, "bold"),
                    text_color="#888888"
                )
                placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # No image found, use text placeholder
            placeholder_label = ctk.CTkLabel(
                image_frame,
                text="Food",
                font=("Arial", 20, "bold"),
                text_color="#888888"
            )
            placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Item name
        name_label = ctk.CTkLabel(
            item_frame,
            text=item["ItemName"],
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        name_label.pack(pady=(5, 0))
        
        # Item description if available
        if item.get("Description"):
            desc_label = ctk.CTkLabel(
                item_frame,
                text=item["Description"],
                font=("Arial", 10),
                text_color="#555555",
                wraplength=150
            )
            desc_label.pack(pady=(0, 5))
        
        # Item price
        price_label = ctk.CTkLabel(
            item_frame,
            text=f"${item['Price']:.2f}",
            font=("Arial", 14),
            text_color="#22C55E"
        )
        price_label.pack()
        
        # Add to cart button
        add_button = ctk.CTkButton(
            item_frame,
            text="Add to Cart",
            command=lambda i=item: self.add_to_cart(i),
            fg_color="#22C55E",
            hover_color="#1DA346",
            corner_radius=8,
            width=100,
            height=30
        )
        add_button.pack(pady=10)
    
    def get_restaurant_data(self, restaurant_id):
        """Get restaurant data from database."""
        query = "SELECT * FROM Restaurant WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        return None
    
    def get_menu_items(self, restaurant_id):
        """Get menu items for the restaurant."""
        query = "SELECT * FROM Menu WHERE RestaurantID = %s"
        return execute_query(query, (restaurant_id,), fetch=True) or []
    
    def add_to_cart(self, item):
        """Add item to cart."""
        # Check if item is already in cart
        for cart_item in self.controller.cart:
            if cart_item["MenuID"] == item["MenuID"]:
                # Just increment quantity
                cart_item["Quantity"] += 1
                CTkMessagebox(
                    title="Added to Cart",
                    message=f"{item['ItemName']} quantity increased in your cart.",
                    icon="check",
                    option_1="OK"
                )
                return
        
        # Add new item to cart
        self.controller.cart.append({
            "MenuID": item["MenuID"],
            "ItemName": item["ItemName"],
            "Price": float(item["Price"]),
            "Quantity": 1
        })
        
        # Show confirmation
        CTkMessagebox(
            title="Added to Cart",
            message=f"{item['ItemName']} has been added to your cart.",
            icon="check",
            option_1="OK"
        )

class CartFrame(ctk.CTkFrame):
    """Shopping cart screen showing items and checkout option."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Your Shopping Cart",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Cart items container (scrollable)
        self.cart_items_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=350
        )
        self.cart_items_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Total section
        self.total_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", height=50)
        self.total_frame.pack(fill="x", padx=10, pady=10)
        
        # Total label
        self.total_label = ctk.CTkLabel(
            self.total_frame,
            text="Total:",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.total_label.pack(side="left", padx=10)
        
        # Total amount
        self.total_amount = ctk.CTkLabel(
            self.total_frame,
            text="$0.00",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.total_amount.pack(side="right", padx=10)
        
        # Checkout button
        self.checkout_button = ctk.CTkButton(
            self,
            text="Proceed to Payment",
            command=self.checkout,
            fg_color="#4CAF50",  # Green
            hover_color="#388E3C",
            corner_radius=5,
            font=("Arial", 16),
            height=50,
            width=350
        )
        self.checkout_button.pack(pady=(10, 20))
    
    def refresh_cart(self):
        """Refresh cart items display."""
        # Clear existing items
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        # Get cart
        cart = self.controller.cart
        
        if not cart:
            # No items in cart
            empty_label = ctk.CTkLabel(
                self.cart_items_frame,
                text="Your cart is empty.",
                font=("Arial", 14),
                text_color="#999999"
            )
            empty_label.pack(pady=50)
            
            # Update total
            self.update_total(0)
            return
        
        # Add items to display
        for item in cart:
            self.create_cart_item(item)
        
        # Update total
        total = sum(item["Price"] * item["Quantity"] for item in cart)
        self.update_total(total)
    
    def create_cart_item(self, item):
        """Create a cart item display with actual image."""
        # Item frame
        item_frame = ctk.CTkFrame(self.cart_items_frame, corner_radius=10, fg_color="white", height=80)
        item_frame.pack(fill="x", pady=5, ipady=10)
        
        # Left side - food image
        image_frame = ctk.CTkFrame(item_frame, width=60, height=60, fg_color="#e0e0e0")
        image_frame.pack(side="left", padx=10, pady=10)
        
        # Try to load menu item image
        image_filename = f"menu_item_{item['MenuID']}.jpg"
        image_path = self.controller.get_image_path(image_filename, folder='menu')
        
        if image_path:
            try:
                # Load and resize image
                image = ctk.CTkImage(
                    light_image=Image.open(image_path),
                    size=(60, 60)
                )
                image_label = ctk.CTkLabel(
                    image_frame, 
                    image=image, 
                    text=""
                )
                image_label.pack(expand=True, fill="both")
            except Exception as e:
                # Fallback to text placeholder if image loading fails
                food_label = ctk.CTkLabel(image_frame, text="Food Item", font=("Arial", 10), text_color="#888888")
                food_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # No image found, use text placeholder
            food_label = ctk.CTkLabel(image_frame, text="Food Item", font=("Arial", 10), text_color="#888888")
            food_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Middle - item details
        details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        # Item name
        name_label = ctk.CTkLabel(
            details_frame,
            text=item["ItemName"],
            font=("Arial", 14, "bold"),
            text_color="#333333",
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Item price
        price_label = ctk.CTkLabel(
            details_frame,
            text=f"${item['Price']:.2f}",
            font=("Arial", 14),
            text_color="#333333",
            anchor="w"
        )
        price_label.pack(anchor="w")
        
        # Right side - quantity controls
        controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)
        
        # Decrease button
        decrease_btn = ctk.CTkButton(
            controls_frame,
            text="-",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#f2f2f2",
            hover_color="#e0e0e0",
            text_color="#333333",
            command=lambda i=item: self.update_quantity(i, -1)
        )
        decrease_btn.pack(side="left", padx=(0, 5))
        
        # Quantity display
        quantity_label = ctk.CTkLabel(
            controls_frame,
            text=str(item["Quantity"]),
            width=30,
            font=("Arial", 14)
        )
        quantity_label.pack(side="left")
        
        # Increase button
        increase_btn = ctk.CTkButton(
            controls_frame,
            text="+",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#f2f2f2",
            hover_color="#e0e0e0",
            text_color="#333333",
            command=lambda i=item: self.update_quantity(i, 1)
        )
        increase_btn.pack(side="left", padx=(5, 0))

        # Add a delete button after the quantity controls
        delete_btn = ctk.CTkButton(
            item_frame,
            text="Delete",
            width=60,
            height=30,
            corner_radius=5,
            fg_color="#F44336",
            hover_color="#D32F2F",
            text_color="white",
            command=lambda i=item: self.delete_item(i)
        )
        delete_btn.pack(side="right", padx=10)
        
        # Store reference to quantity label in item for updates
        item["quantity_label"] = quantity_label
    
    def update_quantity(self, item, change):
        """Update item quantity when + or - is clicked."""
        new_quantity = max(1, item["Quantity"] + change)
        item["Quantity"] = new_quantity
        
        # Update displayed quantity
        if "quantity_label" in item:
            item["quantity_label"].configure(text=str(new_quantity))
        
        # Update total
        cart = self.controller.cart
        total = sum(item["Price"] * item["Quantity"] for item in cart)
        self.update_total(total)
    
    def update_total(self, total):
        """Update the total amount displayed."""
        self.total_amount.configure(text=f"${total:.2f}")
    
    def checkout(self):
        """Process the checkout."""
        cart = self.controller.cart
        
        if not cart:
            CTkMessagebox(
                title="Empty Cart",
                message="Your cart is empty. Please add items before checkout.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Show confirmation and process order
        confirm = CTkMessagebox(
            title="Confirm Order",
            message="Proceed with your order?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Calculate total price
            total_amount = sum(item["Price"] * item["Quantity"] for item in cart)
            
            # Get user ID and restaurant ID (assuming all items from same restaurant)
            user_id = self.controller.user_id
            restaurant_id = self.get_restaurant_id_from_menu(cart[0]["MenuID"])
            
            if not restaurant_id:
                CTkMessagebox(
                    title="Order Error",
                    message="Could not determine restaurant. Please try again.",
                    icon="cancel",
                    option_1="OK"
                )
                return
                
            # Insert order in database
            order_id = self.create_order(user_id, restaurant_id, total_amount)
            
            if order_id:
                # Insert order items
                success = self.create_order_items(order_id, cart)
                
                if success:
                    CTkMessagebox(
                        title="Order Placed",
                        message="Your order has been placed successfully!",
                        icon="check",
                        option_1="OK"
                    )
                    
                    # Clear cart
                    self.controller.cart = []
                    
                    # Show empty cart
                    self.refresh_cart()
                    
                    # Navigate to orders page to see the order
                    self.controller.show_frame("orders")
                else:
                    # Report error
                    CTkMessagebox(
                        title="Order Error",
                        message="There was an error processing your order items.",
                        icon="cancel",
                        option_1="OK"
                    )
            else:
                # Report error
                CTkMessagebox(
                    title="Order Error",
                    message="There was an error processing your order.",
                    icon="cancel",
                    option_1="OK"
                )
    
    def get_restaurant_id_from_menu(self, menu_id):
        """Get restaurant ID from a menu item ID."""
        query = "SELECT RestaurantID FROM Menu WHERE MenuID = %s"
        result = execute_query(query, (menu_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]["RestaurantID"]
        return None
    
    def create_order(self, user_id, restaurant_id, total_amount):
        """Create a new order in the database."""
        query = """
            INSERT INTO `Order` (UserID, RestaurantID, TotalAmount, OrderStatus, OrderDate)
            VALUES (%s, %s, %s, 'pending', NOW())
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (user_id, restaurant_id, total_amount))
            order_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return order_id
        except Exception as e:
            print(f"Database error creating order: {e}")
            return None
    
    def create_order_items(self, order_id, cart):
        """Create order items in the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            for item in cart:
                query = """
                    INSERT INTO OrderItem (OrderID, MenuID, Quantity, Subtotal)
                    VALUES (%s, %s, %s, %s)
                """
                subtotal = item["Price"] * item["Quantity"]
                cursor.execute(query, (order_id, item["MenuID"], item["Quantity"], subtotal))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error creating order items: {e}")
            return False
    def delete_item(self, item):
        """Remove item from cart."""
        # Find and remove item from cart
        for i, cart_item in enumerate(self.controller.cart):
            if cart_item["MenuID"] == item["MenuID"]:
                self.controller.cart.pop(i)
                break
        
        # Refresh cart display
        self.refresh_cart()

class OrdersFrame(ctk.CTkScrollableFrame):
    """Orders screen showing past and current orders."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Order Tracking",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Order details container
        self.order_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.order_container.pack(fill="x", padx=15, pady=10)
        
        # Initialize with mock order or empty state
        self.refresh_orders()
    
    def refresh_orders(self):
        """Refresh orders display."""
        # Clear container
        for widget in self.order_container.winfo_children():
            widget.destroy()
        
        # Fetch orders from database
        orders = self.get_orders()
        
        if not orders:
            # No orders
            no_orders = ctk.CTkLabel(
                self.order_container,
                text="No orders found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_orders.pack(pady=50)
            return
        
        # Display first (most recent) order
        self.display_order(orders[0])
    
    def get_orders(self):
        """Get orders from database."""
        # Try to fetch from database based on user_id
        user_id = self.controller.user_id
        if user_id:
            query = """
                SELECT o.*, r.Name as RestaurantName 
                FROM `Order` o
                JOIN Restaurant r ON o.RestaurantID = r.RestaurantID
                WHERE o.UserID = %s
                ORDER BY o.OrderDate DESC
            """
            orders = execute_query(query, (user_id,), fetch=True)
            
            if orders and len(orders) > 0:
                # Add order items
                for order in orders:
                    items_query = """
                        SELECT oi.*, m.ItemName
                        FROM OrderItem oi
                        JOIN Menu m ON oi.MenuID = m.MenuID
                        WHERE oi.OrderID = %s
                    """
                    order["Items"] = execute_query(items_query, (order["OrderID"],), fetch=True) or []
                
                return orders
        
        return []
    
    # Update the display_order method in OrdersFrame class
    # Fix for the OrdersFrame.display_order method
    def display_order(self, order):
        """Display order details with improved layout."""
        # Order tracking title
        tracking_title = ctk.CTkLabel(
            self.order_container,
            text="Order Status",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        tracking_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Estimated delivery time
        delivery_frame = ctk.CTkFrame(self.order_container, fg_color="transparent")
        delivery_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        delivery_label = ctk.CTkLabel(
            delivery_frame,
            text="Estimated Delivery:",
            font=("Arial", 14),
            text_color="#555555"
        )
        delivery_label.pack(side="left")
        
        # Calculate estimated time (15-45 minutes from order time)
        import datetime
        if "OrderDate" in order:
            from datetime import datetime, timedelta
            try:
                order_time = datetime.strptime(str(order["OrderDate"]), "%Y-%m-%d %H:%M:%S")
                delivery_time = order_time + timedelta(minutes=30)
                time_str = delivery_time.strftime("%H:%M")
            except Exception:
                time_str = "15:00"  # Fallback
        else:
            time_str = "15:00"  # Fallback
        
        time_label = ctk.CTkLabel(
            delivery_frame,
            text=time_str,
            font=("Arial", 14, "bold"),
            text_color="#FF5722"
        )
        time_label.pack(side="right")
        
        # Status tracker with equal spacing
        status_frame = ctk.CTkFrame(self.order_container, fg_color="transparent", height=100)
        status_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # Configure columns for equal spacing
        for i in range(4):
            status_frame.columnconfigure(i, weight=1, uniform="status_col")
        
        # Status steps with string values only (not tuples)
        status_steps = ["Order Placed", "Preparing", "Out for Delivery", "Delivered"]
        status_icons = ["✅", "🔍", "🚲", "🎁"]
        
        # Current status (from order or mock)
        current_status = order.get("OrderStatus", "pending").lower()
        
        # Map database status to display status
        status_map = {
            "pending": "Order Placed",
            "preparing": "Preparing",
            "shipping": "Out for Delivery",
            "delivered": "Delivered"
        }
        
        display_status = status_map.get(current_status, "Order Placed")
        
        # Find the index of the current status
        current_status_index = 0
        for i, status in enumerate(status_steps):
            if status == display_status:
                current_status_index = i
                break
        
        # Connection lines between status steps
        for i in range(3):
            line_frame = ctk.CTkFrame(
                status_frame, 
                fg_color="#CCCCCC" if i >= current_status_index else "#22C55E",
                height=4
            )
            line_frame.grid(row=1, column=i, columnspan=1, sticky="ew", padx=10)
        
        for i, status in enumerate(status_steps):
            # Is this the current or completed status?
            is_current = status == display_status
            is_completed = i <= current_status_index
            
            # Status icon
            status_label = ctk.CTkLabel(
                status_frame,
                text=status_icons[i],
                font=("Arial", 20),
                text_color="#22C55E" if is_current or is_completed else "#CCCCCC"
            )
            status_label.grid(row=0, column=i, padx=10)
            
            # Status text
            status_text = ctk.CTkLabel(
                status_frame,
                text=status,
                font=("Arial", 12),
                text_color="#333333" if is_current or is_completed else "#999999"
            )
            status_text.grid(row=2, column=i, padx=10, pady=(5, 0))
            
        # Order details label
        order_label = ctk.CTkLabel(
            self.order_container,
            text="Your Order",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        order_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Order items with images
        for item in order.get("Items", []):
            # Item frame
            item_frame = ctk.CTkFrame(self.order_container, fg_color="#f9f9f9", corner_radius=10)
            item_frame.pack(fill="x", padx=15, pady=5)
            
            # Try to load menu item image
            menu_id = item.get("MenuID", 0)
            image_filename = f"menu_item_{menu_id}.jpg"
            image_path = self.controller.get_image_path(image_filename, folder='menu')
            
            # Item image
            img_frame = ctk.CTkFrame(item_frame, width=60, height=60, fg_color="#e0e0e0", corner_radius=5)
            img_frame.pack(side="left", padx=10, pady=10)
            
            if image_path:
                try:
                    # Load and resize image
                    image = ctk.CTkImage(
                        light_image=Image.open(image_path),
                        size=(60, 60)
                    )
                    image_label = ctk.CTkLabel(
                        img_frame, 
                        image=image, 
                        text=""
                    )
                    image_label.pack(expand=True, fill="both")
                except Exception as e:
                    # Fallback to text placeholder
                    placeholder_label = ctk.CTkLabel(img_frame, text="Food", text_color="#999999")
                    placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # No image, use text placeholder
                placeholder_label = ctk.CTkLabel(img_frame, text="Food", text_color="#999999")
                placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Item details
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            # Item name
            name_label = ctk.CTkLabel(
                details_frame,
                text=item.get("ItemName", "Food Item"),
                font=("Arial", 14, "bold"),
                text_color="#333333",
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            # Item price
            price_label = ctk.CTkLabel(
                details_frame,
                text=f"${item.get('Subtotal', 0.00):.2f}",
                font=("Arial", 12),
                text_color="#555555",
                anchor="w"
            )
            price_label.pack(anchor="w")
            
            # Quantity
            quantity_label = ctk.CTkLabel(
                item_frame,
                text=f"× {item.get('Quantity', 1)}",
                font=("Arial", 14, "bold"),
                text_color="#555555"
            )
            quantity_label.pack(side="right", padx=15)
        
        # Map section
        location_label = ctk.CTkLabel(
            self.order_container,
            text="Delivery Location",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        location_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Map frame with placeholder map image
        map_frame = ctk.CTkFrame(self.order_container, fg_color="#e0e0e0", height=180)
        map_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # Try to load a map image
        map_path = os.path.join('static', 'images', 'Map.png')
        
        if os.path.exists(map_path):
            try:
                map_image = ctk.CTkImage(
                    light_image=Image.open(map_path),
                    size=(400, 180)
                )
                map_label = ctk.CTkLabel(
                    map_frame, 
                    image=map_image, 
                    text=""
                )
                map_label.pack(expand=True, fill="both")
            except Exception as e:
                # Fallback to text placeholder
                map_label = ctk.CTkLabel(map_frame, text="Delivery Map", font=("Arial", 18), text_color="#999999")
                map_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # No image, use text placeholder
            map_label = ctk.CTkLabel(map_frame, text="Delivery Map", font=("Arial", 18), text_color="#999999")
            map_label.place(relx=0.5, rely=0.5, anchor="center")

class ProfileFrame(ctk.CTkScrollableFrame):
    """User profile screen showing user details and order history."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="User Profile",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Past orders section
        self.orders_label = ctk.CTkLabel(
            self,
            text="Past Orders",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.orders_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Back to home button
        self.back_button = ctk.CTkButton(
            self,
            text="Back to Home",
            command=lambda: controller.show_frame("home"),
            fg_color="#22C55E",
            hover_color="#1DA346",
            corner_radius=8,
            width=120,
            height=30
        )
        self.back_button.pack(anchor="ne", padx=15, pady=(0, 10))
        
        # Past orders container - use grid layout
        self.orders_container = ctk.CTkFrame(self, fg_color="transparent")
        self.orders_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Configure grid columns for side-by-side cards
        for i in range(3):  # Support up to 3 columns
            self.orders_container.columnconfigure(i, weight=1, uniform="order_card")
        
        # Create past order cards in a grid
        past_orders = self.get_past_orders()
        if past_orders:
            for i, order in enumerate(past_orders):
                column = i % 3  # Place in columns 0, 1, 2
                row = i // 3     # New row after every 3 cards
                self.create_order_card(order, row, column)
        else:
            no_orders = ctk.CTkLabel(
                self.orders_container,
                text="No past orders found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_orders.pack(pady=20)
        
        # Profile and settings section
        self.profile_label = ctk.CTkLabel(
            self,
            text="Profile & Settings",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.profile_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Profile container
        self.profile_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.profile_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Load user data
        self.user_data = self.controller.user_data
        
        # Profile fields
        self.fields_and_values = [
            ("Name:", f"{self.user_data.get('FirstName', 'John')} {self.user_data.get('LastName', 'Doe')}"),
            ("Email:", self.user_data.get('Email', 'user@example.com')),
            ("Address:", self.user_data.get('Address', '123 Food St, Flavor Town')),
            ("Phone:", self.user_data.get('Phone', '+1 (555) 123-4567'))
        ]
        
        self.field_widgets = {}  # Store references to field labels for updating
        
        for i, (field, value) in enumerate(self.fields_and_values):
            # Field container
            field_frame = ctk.CTkFrame(self.profile_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=15, pady=10)
            
            # Label
            field_label = ctk.CTkLabel(
                field_frame,
                text=field,
                font=("Arial", 14),
                text_color="#555555",
                anchor="w"
            )
            field_label.pack(side="left")
            
            # Value
            value_label = ctk.CTkLabel(
                field_frame,
                text=value,
                font=("Arial", 14),
                text_color="#333333",
                anchor="e"
            )
            value_label.pack(side="right")
            
            # Store reference to value label for updating later
            self.field_widgets[field] = value_label
        
        # Edit profile button
        self.edit_button = ctk.CTkButton(
            self,
            text="Edit Profile",
            command=self.edit_profile,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            corner_radius=5,
            font=("Arial", 16),
            height=40,
            width=350
        )
        self.edit_button.pack(pady=(0, 20))
    
    def get_past_orders(self):
        """Get past orders from database."""
        user_id = self.controller.user_id
        if not user_id:
            return []
            
        query = """
            SELECT o.OrderID, o.TotalAmount, o.OrderDate, r.Name as restaurant
            FROM `Order` o
            JOIN Restaurant r ON o.RestaurantID = r.RestaurantID
            WHERE o.UserID = %s
            ORDER BY o.OrderDate DESC
            LIMIT 3
        """
        
        return execute_query(query, (user_id,), fetch=True) or []
    
    def create_order_card(self, order, row, column):
        """Create a card for a past order with placeholder for restaurant image."""
        # Card frame
        card = ctk.CTkFrame(self.orders_container, fg_color="white", corner_radius=10)
        card.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
        
        # Restaurant image frame
        image_frame = ctk.CTkFrame(card, width=60, height=60, fg_color="#e0e0e0")
        image_frame.pack(side="left", padx=10, pady=10)
        
        # Try to load restaurant image
        try:
            # Fetch restaurant ID based on restaurant name
            restaurant_query = "SELECT RestaurantID FROM Restaurant WHERE Name = %s"
            restaurant_result = execute_query(restaurant_query, (order['restaurant'],), fetch=True)
            
            if restaurant_result:
                restaurant_id = restaurant_result[0]['RestaurantID']
                image_filename = f"restaurant_{restaurant_id}.png"
                image_path = self.controller.get_image_path(image_filename)
                
                if image_path:
                    image = ctk.CTkImage(
                        light_image=Image.open(image_path),
                        size=(60, 60)
                    )
                    image_label = ctk.CTkLabel(
                        image_frame, 
                        image=image, 
                        text=""
                    )
                    image_label.pack(expand=True, fill="both")
                else:
                    raise FileNotFoundError("Restaurant image not found")
            else:
                raise FileNotFoundError("Restaurant not found")
        except Exception as e:
            # Fallback to text placeholder if image loading fails
            placeholder_label = ctk.CTkLabel(
                image_frame,
                text="Rest",
                font=("Arial", 12),
                text_color="#888888"
            )
            placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Restaurant name
        restaurant = ctk.CTkLabel(
            card,
            text=order.get("restaurant", "Restaurant"),
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        restaurant.pack(anchor="w", padx=15, pady=(10, 2))
        
        # Order date
        date_str = str(order.get("OrderDate", "2025-01-01"))
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except Exception:
            formatted_date = date_str
        
        date = ctk.CTkLabel(
            card,
            text=f"Order Date: {formatted_date}",
            font=("Arial", 12),
            text_color="#555555"
        )
        date.pack(anchor="w", padx=15, pady=(0, 2))
        
        # Total amount
        total_amount = order.get("TotalAmount", 0.00)
        total = ctk.CTkLabel(
            card,
            text=f"${total_amount:.2f}",
            font=("Arial", 14, "bold"),
            text_color="#4CAF50"
        )
        total.pack(anchor="w", padx=15, pady=(2, 10))
        
        # Reorder button
        reorder = ctk.CTkButton(
            card,
            text="Reorder",
            command=lambda o=order: self.reorder(o),
            fg_color="#FF9800",
            hover_color="#F57C00",
            corner_radius=5,
            font=("Arial", 14),
            height=35,
            width=card.winfo_width() - 30
        )
        reorder.pack(fill="x", padx=15, pady=(0, 10))
    
    def reorder(self, order):
        """Process reorder of a past order."""
        # Get order items
        order_id = order.get("OrderID")
        if not order_id:
            CTkMessagebox(
                title="Reorder Error",
                message="Could not find order details.",
                icon="cancel",
                option_1="OK"
            )
            return
            
        query = """
            SELECT oi.MenuID, m.ItemName, m.Price, oi.Quantity
            FROM OrderItem oi
            JOIN Menu m ON oi.MenuID = m.MenuID
            WHERE oi.OrderID = %s
        """
        
        items = execute_query(query, (order_id,), fetch=True)
        
        if not items:
            CTkMessagebox(
                title="Reorder Error",
                message="No items found in this order.",
                icon="cancel",
                option_1="OK"
            )
            return
            
        # Clear current cart
        self.controller.cart = []
        
        # Add items to cart
        for item in items:
            self.controller.cart.append({
                "MenuID": item["MenuID"],
                "ItemName": item["ItemName"],
                "Price": float(item["Price"]),
                "Quantity": item["Quantity"]
            })
        
        # Show confirmation
        CTkMessagebox(
            title="Reorder",
            message=f"Items from your previous order at {order.get('restaurant', 'Restaurant')} have been added to your cart.",
            icon="info",
            option_1="OK"
        )
        
        # Go to cart
        self.controller.show_frame("cart")
    
    def edit_profile(self):
        """Open profile editing modal window."""
        # Create modal window
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Edit Profile")
        self.edit_window.geometry("500x650")
        self.edit_window.resizable(False, False)
        
        # Calculate center position
        screen_width = self.edit_window.winfo_screenwidth()
        screen_height = self.edit_window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 650) // 2
        self.edit_window.geometry(f"500x650+{x}+{y}")
        
        # Make it modal (block until closed)
        self.edit_window.transient(self.master)
        self.edit_window.grab_set()
        
        # Add a title
        title_label = ctk.CTkLabel(
            self.edit_window,
            text="Edit Your Profile",
            font=("Arial", 20, "bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(20, 30))
        
        # Create form
        form_frame = ctk.CTkFrame(self.edit_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Ensure user_data dict is initialized
        if not hasattr(self, 'user_data') or self.user_data is None:
            self.user_data = {}
        
        # Form fields
        first_name_label = ctk.CTkLabel(form_frame, text="First Name:", anchor="w")
        first_name_label.pack(anchor="w", pady=(0, 5))
        
        first_name_entry = ctk.CTkEntry(form_frame, width=440)
        first_name_entry.pack(anchor="w", pady=(0, 15))
        first_name_entry.insert(0, str(self.user_data.get("FirstName", "")))
        
        last_name_label = ctk.CTkLabel(form_frame, text="Last Name:", anchor="w")
        last_name_label.pack(anchor="w", pady=(0, 5))
        
        last_name_entry = ctk.CTkEntry(form_frame, width=440)
        last_name_entry.pack(anchor="w", pady=(0, 15))
        last_name_entry.insert(0, str(self.user_data.get("LastName", "")))
        
        email_label = ctk.CTkLabel(form_frame, text="Email:", anchor="w")
        email_label.pack(anchor="w", pady=(0, 5))
        
        email_entry = ctk.CTkEntry(form_frame, width=440)
        email_entry.pack(anchor="w", pady=(0, 15))
        email_entry.insert(0, str(self.user_data.get("Email", "")))
        
        phone_label = ctk.CTkLabel(form_frame, text="Phone:", anchor="w")
        phone_label.pack(anchor="w", pady=(0, 5))
        
        phone_entry = ctk.CTkEntry(form_frame, width=440)
        phone_entry.pack(anchor="w", pady=(0, 15))
        # Convert None to empty string to avoid tkinter error
        phone_entry.insert(0, str(self.user_data.get("Phone", "")))
        
        address_label = ctk.CTkLabel(form_frame, text="Address:", anchor="w")
        address_label.pack(anchor="w", pady=(0, 5))
        
        address_entry = ctk.CTkEntry(form_frame, width=440)
        address_entry.pack(anchor="w", pady=(0, 15))
        address_entry.insert(0, str(self.user_data.get("Address", "")))

        # Delivery instructions (new field)
        delivery_label = ctk.CTkLabel(form_frame, text="Delivery Instructions (optional):", anchor="w")
        delivery_label.pack(anchor="w", pady=(0, 5))
        
        delivery_instructions = ctk.CTkTextbox(form_frame, width=440, height=80)
        delivery_instructions.pack(anchor="w", pady=(0, 15))
        # Convert None to empty string for delivery instructions
        delivery_instructions.insert("1.0", str(self.user_data.get("DeliveryInstructions", "")))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.edit_window, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.edit_window.destroy,
            fg_color="#e0e0e0",
            text_color="#333333",
            hover_color="#d0d0d0",
            width=150
        )
        cancel_button.pack(side="left", padx=(70, 10))
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Changes",
            command=lambda: self.save_profile_changes(
                first_name_entry.get(),
                last_name_entry.get(),
                email_entry.get(),
                phone_entry.get(),
                address_entry.get(),
                delivery_instructions.get("1.0", "end-1c")
            ),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=150
        )
        save_button.pack(side="right", padx=(10, 70))

    def save_profile_changes(self, first_name, last_name, email, phone, address, delivery_instructions=None):
        """Save profile changes to database and update UI."""
        # Validate inputs
        if not first_name or not last_name or not email:
            CTkMessagebox(
                title="Validation Error",
                message="First name, last name and email are required fields.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            CTkMessagebox(
                title="Validation Error",
                message="Please enter a valid email address.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Validate that email is not already in use by another active user
        if email != self.user_data.get("Email", ""):
            check_query = """
                SELECT UserID FROM User 
                WHERE Email = %s AND UserID != %s AND IsActive = True AND DeletedAt IS NULL
            """
            result = execute_query(check_query, (email, self.controller.user_id), fetch=True)
            if result and len(result) > 0:
                CTkMessagebox(
                    title="Validation Error",
                    message="This email is already in use by another account.",
                    icon="cancel",
                    option_1="OK"
                )
                return
        
        # Update database
        try:
            query = """
                UPDATE User 
                SET FirstName = %s, LastName = %s, Email = %s, Phone = %s, 
                    Address = %s, DeliveryInstructions = %s, UpdatedAt = NOW()
                WHERE UserID = %s AND IsActive = True
            """
            
            execute_query(
                query, 
                (first_name, last_name, email, phone, address, delivery_instructions, self.controller.user_id),
                fetch=False
            )
            
            # Update local user data
            self.user_data["FirstName"] = first_name
            self.user_data["LastName"] = last_name
            self.user_data["Email"] = email
            self.user_data["Phone"] = phone
            self.user_data["Address"] = address
            self.user_data["DeliveryInstructions"] = delivery_instructions
            
            # Update the controller's user_data
            self.controller.user_data = self.user_data
            
            # Update displayed values
            self.field_widgets["Name:"].configure(text=f"{first_name} {last_name}")
            self.field_widgets["Email:"].configure(text=email)
            self.field_widgets["Phone:"].configure(text=phone)
            self.field_widgets["Address:"].configure(text=address)
            
            # Close the edit window
            self.edit_window.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Profile Updated",
                message="Your profile has been updated successfully.",
                icon="check",
                option_1="OK"
            )
            
        except Exception as e:
            print(f"Error updating profile: {e}")
            CTkMessagebox(
                title="Update Error",
                message="There was an error updating your profile. Please try again.",
                icon="cancel",
                option_1="OK"
            )

class SettingsFrame(ctk.CTkFrame):
    """Settings screen with application settings."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Settings container
        self.settings_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.settings_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Settings options
        settings = [
            ("Notifications", True),
            ("Dark Mode", False),
            ("Auto-Save Address", True),
            ("Save Payment Info", False)
        ]
        
        self.setting_switches = {}  # Store references to switches
        
        for setting, value in settings:
            # Setting container
            setting_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
            setting_frame.pack(fill="x", padx=15, pady=10)
            
            # Setting label
            setting_label = ctk.CTkLabel(
                setting_frame,
                text=setting,
                font=("Arial", 14),
                text_color="#333333",
                anchor="w"
            )
            setting_label.pack(side="left", fill="y")
            
            # Setting switch
            switch_var = ctk.BooleanVar(value=value)
            setting_switch = ctk.CTkSwitch(
                setting_frame,
                text="",
                variable=switch_var,
                command=lambda s=setting: self.toggle_setting(s),
                switch_width=46,
                switch_height=24,
                fg_color="#CCCCCC",
                progress_color="#4CAF50",
                button_color="#FFFFFF",
                button_hover_color="#EEEEEE"
            )
            setting_switch.pack(side="right")
            
            # Store reference to switch
            self.setting_switches[setting] = (switch_var, setting_switch)
        
        # Account section
        self.account_label = ctk.CTkLabel(
            self,
            text="Account",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.account_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Account options
        account_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        account_container.pack(fill="x", padx=15, pady=(0, 20))
        
        account_options = [
            ("Change Password", self.show_change_password_modal),
            ("Update Address", self.show_update_address_modal),
            ("Sign Out", self.controller.sign_out)
        ]
        
        for option_text, command in account_options:
            option_button = ctk.CTkButton(
                account_container,
                text=option_text,
                command=command,
                fg_color="transparent",
                hover_color="#f0f0f0",
                text_color="#333333",
                anchor="w",
                font=("Arial", 14),
                height=40
            )
            option_button.pack(fill="x", padx=5, pady=2)
    
    def toggle_setting(self, setting):
        """Handle toggling a setting."""
        switch_var, _ = self.setting_switches.get(setting, (None, None))
        if switch_var:
            is_enabled = switch_var.get()
            print(f"Setting '{setting}' is now {'enabled' if is_enabled else 'disabled'}")
            
            # Show confirmation toast
            CTkMessagebox(
                title="Setting Updated",
                message=f"{setting} {'enabled' if is_enabled else 'disabled'}.",
                icon="info",
                option_1="OK"
            )
    
    def show_change_password_modal(self):
        """Show modal window for changing password."""
        # Create modal window
        self.password_window = ctk.CTkToplevel(self)
        self.password_window.title("Change Password")
        self.password_window.geometry("500x450")
        self.password_window.resizable(False, False)
        
        # Calculate center position
        screen_width = self.password_window.winfo_screenwidth()
        screen_height = self.password_window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 450) // 2
        self.password_window.geometry(f"500x450+{x}+{y}")
        
        # Make it modal (block until closed)
        self.password_window.transient(self.master)
        self.password_window.grab_set()
        
        # Add a title
        title_label = ctk.CTkLabel(
            self.password_window,
            text="Change Your Password",
            font=("Arial", 20, "bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(20, 30))
        
        # Create form
        form_frame = ctk.CTkFrame(self.password_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Form fields
        current_pwd_label = ctk.CTkLabel(form_frame, text="Current Password:", anchor="w")
        current_pwd_label.pack(anchor="w", pady=(0, 5))
        
        current_pwd_entry = ctk.CTkEntry(form_frame, width=440, show="•")
        current_pwd_entry.pack(anchor="w", pady=(0, 15))
        
        new_pwd_label = ctk.CTkLabel(form_frame, text="New Password:", anchor="w")
        new_pwd_label.pack(anchor="w", pady=(0, 5))
        
        new_pwd_entry = ctk.CTkEntry(form_frame, width=440, show="•")
        new_pwd_entry.pack(anchor="w", pady=(0, 5))
        
        # Password requirements text
        pwd_req_label = ctk.CTkLabel(
            form_frame, 
            text="Password must be at least 8 characters with numbers and special characters.",
            font=("Arial", 10),
            text_color="#888888",
            anchor="w"
        )
        pwd_req_label.pack(anchor="w", pady=(0, 15))
        
        confirm_pwd_label = ctk.CTkLabel(form_frame, text="Confirm New Password:", anchor="w")
        confirm_pwd_label.pack(anchor="w", pady=(0, 5))
        
        confirm_pwd_entry = ctk.CTkEntry(form_frame, width=440, show="•")
        confirm_pwd_entry.pack(anchor="w", pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.password_window, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.password_window.destroy,
            fg_color="#e0e0e0",
            text_color="#333333",
            hover_color="#d0d0d0",
            width=150
        )
        cancel_button.pack(side="left", padx=(70, 10))
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Update Password",
            command=lambda: self.update_password(
                current_pwd_entry.get(),
                new_pwd_entry.get(),
                confirm_pwd_entry.get()
            ),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=150
        )
        save_button.pack(side="right", padx=(10, 70))
    
    def update_password(self, current_password, new_password, confirm_password):
        """Validate and update the user's password."""
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            CTkMessagebox(
                title="Missing Information",
                message="Please fill in all password fields.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            CTkMessagebox(
                title="Password Mismatch",
                message="New password and confirm password do not match.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Validate password strength
        import re
        
        # At least 8 characters, contains number and special character
        password_pattern = r'^(?=.*[0-9])(?=.*[!@#$%^&*])(.{8,})$'
        if not re.match(password_pattern, new_password):
            CTkMessagebox(
                title="Weak Password",
                message="Password must be at least 8 characters and include numbers and special characters.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Verify current password
        try:
            import bcrypt
            
            # Get current password hash from database
            query = "SELECT Password FROM User WHERE UserID = %s"
            result = execute_query(query, (self.controller.user_id,), fetch=True)
            
            if not result:
                raise Exception("User not found")
                
            stored_hash = result[0]["Password"]
            
            # Check if current password matches
            if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
                CTkMessagebox(
                    title="Incorrect Password",
                    message="Current password is incorrect.",
                    icon="cancel",
                    option_1="OK"
                )
                return
            
            # Hash new password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update password in database
            update_query = "UPDATE User SET Password = %s WHERE UserID = %s"
            execute_query(update_query, (new_hash, self.controller.user_id), fetch=False)
            
            # Close window
            self.password_window.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Password Updated",
                message="Your password has been updated successfully.",
                icon="check",
                option_1="OK"
            )
            
        except Exception as e:
            print(f"Error updating password: {e}")
            CTkMessagebox(
                title="Update Error",
                message="There was an error updating your password. Please try again.",
                icon="cancel",
                option_1="OK"
            )
    
    def show_update_address_modal(self):
        """Show modal window for updating address."""
        # Create modal window
        self.address_window = ctk.CTkToplevel(self)
        self.address_window.title("Update Address")
        self.address_window.geometry("500x600")
        self.address_window.resizable(False, False)
        
        # Calculate center position
        screen_width = self.address_window.winfo_screenwidth()
        screen_height = self.address_window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 600) // 2
        self.address_window.geometry(f"500x600+{x}+{y}")
        
        # Make it modal (block until closed)
        self.address_window.transient(self.master)
        self.address_window.grab_set()
        
        # Add a title
        title_label = ctk.CTkLabel(
            self.address_window,
            text="Update Your Address",
            font=("Arial", 20, "bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(20, 30))
        
        # Get current user data
        user_query = "SELECT * FROM User WHERE UserID = %s"
        user_data = execute_query(user_query, (self.controller.user_id,), fetch=True)
        current_address = user_data[0].get("Address", "") if user_data else ""
        
        # Create form
        form_frame = ctk.CTkFrame(self.address_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Form fields
        street_label = ctk.CTkLabel(form_frame, text="Street Address:", anchor="w")
        street_label.pack(anchor="w", pady=(0, 5))
        
        street_entry = ctk.CTkEntry(form_frame, width=440)
        street_entry.pack(anchor="w", pady=(0, 15))
        
        # Parse address and fill in fields if available
        address_parts = current_address.split(',') if current_address else []
        street = address_parts[0].strip() if len(address_parts) > 0 else ""
        city = address_parts[1].strip() if len(address_parts) > 1 else ""
        
        # Extract state and zip if available
        state_zip = ""
        if len(address_parts) > 2:
            state_zip_parts = address_parts[2].strip().split()
            state = state_zip_parts[0] if len(state_zip_parts) > 0 else ""
            zip_code = state_zip_parts[1] if len(state_zip_parts) > 1 else ""
        else:
            state = ""
            zip_code = ""
        
        street_entry.insert(0, street)
        
        city_label = ctk.CTkLabel(form_frame, text="City:", anchor="w")
        city_label.pack(anchor="w", pady=(0, 5))
        
        city_entry = ctk.CTkEntry(form_frame, width=440)
        city_entry.pack(anchor="w", pady=(0, 15))
        city_entry.insert(0, city)
        
        # State and ZIP row
        state_zip_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        state_zip_frame.pack(fill="x", pady=(0, 15))
        
        # State
        state_label = ctk.CTkLabel(state_zip_frame, text="State:", anchor="w")
        state_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        state_entry = ctk.CTkEntry(state_zip_frame, width=200)
        state_entry.grid(row=1, column=0, sticky="w", padx=(0, 10))
        state_entry.insert(0, state)
        
        # ZIP
        zip_label = ctk.CTkLabel(state_zip_frame, text="ZIP Code:", anchor="w")
        zip_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        zip_entry = ctk.CTkEntry(state_zip_frame, width=200)
        zip_entry.grid(row=1, column=1, sticky="w")
        zip_entry.insert(0, zip_code)
        
        # Additional notes
        notes_label = ctk.CTkLabel(form_frame, text="Delivery Instructions (optional):", anchor="w")
        notes_label.pack(anchor="w", pady=(10, 5))
        
        notes_entry = ctk.CTkTextbox(form_frame, width=440, height=80)
        notes_entry.pack(anchor="w", pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.address_window, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.address_window.destroy,
            fg_color="#e0e0e0",
            text_color="#333333",
            hover_color="#d0d0d0",
            width=150
        )
        cancel_button.pack(side="left", padx=(70, 10))
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Update Address",
            command=lambda: self.save_address(
                street_entry.get(),
                city_entry.get(),
                state_entry.get(),
                zip_entry.get(),
                notes_entry.get("1.0", "end-1c")
            ),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=150
        )
        save_button.pack(side="right", padx=(10, 70))
    
    def save_address(self, street, city, state, zip_code, notes):
        """Save address to database."""
        # Validate inputs
        if not street or not city or not state or not zip_code:
            CTkMessagebox(
                title="Missing Information",
                message="Please fill in all required address fields.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Validate zip code format
        import re
        zip_pattern = r'^\d{5}(-\d{4})?$'
        if not re.match(zip_pattern, zip_code):
            CTkMessagebox(
                title="Invalid ZIP Code",
                message="Please enter a valid 5-digit ZIP code or ZIP+4 format.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Format complete address
        formatted_address = f"{street}, {city}, {state} {zip_code}"
        
        # Add notes to delivery_instructions field if provided
        if notes:
            delivery_instructions = notes
        else:
            delivery_instructions = ""
        
        try:
            # Update address in database
            query = """
                UPDATE User 
                SET Address = %s, DeliveryInstructions = %s
                WHERE UserID = %s
            """
            execute_query(query, (formatted_address, delivery_instructions, self.controller.user_id), fetch=False)
            
            # Close window
            self.address_window.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Address Updated",
                message="Your delivery address has been updated successfully.",
                icon="check",
                option_1="OK"
            )
        
        except Exception as e:
            print(f"Error updating address: {e}")
            CTkMessagebox(
                title="Update Error",
                message="There was an error updating your address. Please try again.",
                icon="cancel",
                option_1="OK"
            )