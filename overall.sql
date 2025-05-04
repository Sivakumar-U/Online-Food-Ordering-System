-- ------------------------
-- Database: Online Food Ordering System
-- ------------------------

--  USER TABLE
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

--  RESTAURANT TABLE
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

--  RESTAURANT OWNER TABLE
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

--  MENU TABLE
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

--  ORDER TABLE
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

--  ORDER ITEM TABLE
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

--  DELIVERY TABLE
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

--  USER SETTINGS TABLE
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

-- --------------------------------------------------------
-- Sample Data Inserts
-- --------------------------------------------------------

-- Sample Users
INSERT INTO User (FirstName, LastName, Email, Password, Phone, Address, Role)
VALUES
('John', 'Doe', 'john@example.com', 'Password123!', '555-123-4567', '123 Main St, Chicago, IL 60601', 'customer'),
('Jane', 'Smith', 'jane@example.com', 'Password123!', '555-987-6543', '456 Oak Ave, New York, NY 10001', 'customer'),
('Admin', 'User', 'admin@example.com', 'Password123!', '555-111-2222', '789 Admin St, San Francisco, CA 94105', 'admin'),
('Rest', 'Owner', 'restaurant@example.com', 'Password123!', '555-444-5555', '321 Chef Blvd, Miami, FL 33101', 'restaurant'),
('Delivery', 'Person', 'delivery@example.com', 'Password123!', '555-777-8888', '555 Delivery Rd, Austin, TX 78701', 'customer');

-- Sample User Settings
INSERT INTO UserSettings (UserID, SettingName, SettingValue)
VALUES
(1, 'Notifications', TRUE),
(1, 'DarkMode', FALSE),
(1, 'AutoSaveAddress', TRUE),
(1, 'SavePaymentInfo', FALSE),
(2, 'Notifications', TRUE),
(2, 'DarkMode', FALSE),
(2, 'AutoSaveAddress', TRUE),
(2, 'SavePaymentInfo', FALSE);

-- Sample Restaurants
INSERT INTO Restaurant (Name, Cuisine, Contact, Location)
VALUES
('Pizza Palace', 'Italian', '555-1234', '123 Main St'),
('Burger Haven', 'American', '555-5678', '456 Oak Ave'),
('Sweet Treats', 'Desserts', '555-9012', '789 Maple Dr'),
('Sushi Spot', 'Japanese', '555-3456', '321 Pine Rd'),
('Taco Town', 'Mexican', '555-7890', '654 Elm St');

-- Link Restaurant Owner
INSERT INTO RestaurantOwner (UserID, RestaurantID) VALUES (4, 1); -- Rest Owner ➜ Pizza Palace

-- Sample Menu Items
INSERT INTO Menu (RestaurantID, ItemName, Description, Price) VALUES
(1, 'Margherita Pizza', 'Classic cheese and tomato pizza', 12.99),
(1, 'Pepperoni Pizza', 'Pizza with pepperoni toppings', 14.99),
(1, 'Vegetarian Pizza', 'Pizza with assorted vegetables', 13.99),
(2, 'Classic Cheeseburger', 'Beef patty with cheese', 9.99),
(2, 'Bacon Burger', 'Burger with bacon and cheese', 11.99),
(2, 'Veggie Burger', 'Plant-based patty with vegetables', 10.99),
(3, 'Chocolate Cake', 'Rich chocolate cake with frosting', 5.99),
(3, 'Ice Cream Sundae', 'Vanilla ice cream with toppings', 4.99),
(3, 'Apple Pie', 'Homemade apple pie with cinnamon', 6.99),
(4, 'California Roll', 'Crab, avocado and cucumber roll', 8.99),
(4, 'Salmon Nigiri', 'Fresh salmon over rice', 7.99),
(4, 'Tempura Roll', 'Shrimp tempura and vegetables', 9.99),
(5, 'Beef Taco', 'Seasoned beef in a corn tortilla', 3.99),
(5, 'Chicken Quesadilla', 'Grilled chicken and cheese', 7.99),
(5, 'Veggie Burrito', 'Bean and rice burrito with vegetables', 6.99);

-- Sample Orders
INSERT INTO `Order` (UserID, RestaurantID, TotalAmount, OrderStatus, OrderDate) VALUES
(1, 1, 27.98, 'delivered', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 2, 21.98, 'delivered', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 3, 17.97, 'preparing', NOW());

-- Get last order IDs dynamically if needed.

-- Sample Order Items
INSERT INTO OrderItem (OrderID, MenuID, Quantity, Subtotal) VALUES
(1, 1, 1, 12.99), (1, 2, 1, 14.99),
(2, 4, 1, 9.99), (2, 5, 1, 11.99),
(3, 7, 1, 5.99), (3, 8, 1, 4.99), (3, 9, 1, 6.99);

-- Sample Deliveries
INSERT INTO Delivery (OrderID, PersonnelID, DeliveryStatus, EstimatedTime) VALUES
(1, 5, 'delivered', '2025-04-12 15:30:00'),
(2, 5, 'delivered', '2025-04-13 18:45:00'),
(3, 5, 'pending', '2025-04-14 19:30:00');
