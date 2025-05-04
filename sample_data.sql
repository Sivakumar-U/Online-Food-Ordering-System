-- Online Food Ordering System Sample Data
-- This script contains expanded sample data for all tables
-- Created: April 30, 2025

-- --------------------------------------------------------
-- Disable foreign key checks to allow for data loading in any order
-- --------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------------------
-- Truncate tables to start fresh
-- --------------------------------------------------------
TRUNCATE TABLE `User`;
TRUNCATE TABLE `Restaurant`;
TRUNCATE TABLE `RestaurantOwner`;
TRUNCATE TABLE `Menu`;
TRUNCATE TABLE `Order`;
TRUNCATE TABLE `OrderItem`;
TRUNCATE TABLE `Delivery`;
TRUNCATE TABLE `UserSettings`;

-- --------------------------------------------------------
-- Sample Users
-- --------------------------------------------------------
INSERT INTO `User` 
(`UserID`, `FirstName`, `LastName`, `Email`, `Password`, `Phone`, `Address`, `DeliveryInstructions`, `Role`, `IsActive`, `CreatedAt`)
VALUES
(1, 'John', 'Doe', 'john@food.com', '$2b$10$YourHashedPasswordHere123456', '555-123-4567', '123 Main St, Chicago, IL 60601', 'Please ring doorbell twice', 'customer', TRUE, '2024-12-15 08:30:00'),
(2, 'Jane', 'Smith', 'jane@food.com', '$2b$10$YourHashedPasswordHere123456', '555-987-6543', '456 Oak Ave, New York, NY 10001', 'Leave at door', 'customer', TRUE, '2024-12-16 09:15:00'),
(3, 'Admin', 'User', 'admin@food.com', '$2b$10$YourHashedPasswordHere123456', '555-111-2222', '789 Admin St, San Francisco, CA 94105', NULL, 'admin', TRUE, '2024-12-01 10:00:00'),
(4, 'Rest', 'Owner', 'restaurant@food.com', '$2b$10$YourHashedPasswordHere123456', '555-444-5555', '321 Chef Blvd, Miami, FL 33101', NULL, 'restaurant', TRUE, '2024-12-05 11:30:00'),
(5, 'Delivery', 'Person', 'delivery@food.com', '$2b$10$YourHashedPasswordHere123456', '555-777-8888', '555 Delivery Rd, Austin, TX 78701', NULL, 'customer', TRUE, '2024-12-10 12:45:00'),
(6, 'Michael', 'Johnson', 'michael@food.com', '$2b$10$YourHashedPasswordHere123456', '555-222-3333', '789 Pine St, Boston, MA 02108', 'Call upon arrival', 'customer', TRUE, '2025-01-05 14:20:00'),
(7, 'Sarah', 'Williams', 'sarah@food.com', '$2b$10$YourHashedPasswordHere123456', '555-444-5555', '456 Maple Ave, Denver, CO 80202', NULL, 'customer', TRUE, '2025-01-10 15:45:00'),
(8, 'Robert', 'Brown', 'robert@food.com', '$2b$10$YourHashedPasswordHere123456', '555-666-7777', '123 Cedar St, Seattle, WA 98101', 'Apartment 3B, second floor', 'customer', TRUE, '2025-01-15 16:30:00'),
(9, 'Pizza', 'Owner', 'pizza@food.com', '$2b$10$YourHashedPasswordHere123456', '555-888-9999', '789 Pizza St, Chicago, IL 60602', NULL, 'restaurant', TRUE, '2025-01-20 17:15:00'),
(10, 'Sushi', 'Master', 'sushi@food.com', '$2b$10$YourHashedPasswordHere123456', '555-111-3333', '456 Sushi Ave, Los Angeles, CA 90001', NULL, 'restaurant', TRUE, '2025-01-25 18:00:00');

-- --------------------------------------------------------
-- Sample Restaurants
-- --------------------------------------------------------
INSERT INTO `Restaurant` 
(`RestaurantID`, `Name`, `Cuisine`, `Contact`, `Location`, `IsActive`, `CreatedAt`)
VALUES
(1, 'Pizza Palace', 'Italian', '555-1234', '123 Main St, Chicago, IL 60601', TRUE, '2025-01-05 09:00:00'),
(2, 'Burger Haven', 'American', '555-5678', '456 Oak Ave, New York, NY 10001', TRUE, '2025-01-06 09:30:00'),
(3, 'Sweet Treats', 'Desserts', '555-9012', '789 Maple Dr, Los Angeles, CA 90001', TRUE, '2025-01-07 10:00:00'),
(4, 'Sushi Spot', 'Japanese', '555-3456', '321 Pine Rd, Seattle, WA 98101', TRUE, '2025-01-08 10:30:00'),
(5, 'Taco Town', 'Mexican', '555-7890', '654 Elm St, Austin, TX 78701', TRUE, '2025-01-09 11:00:00'),
(6, 'Pasta Paradise', 'Italian', '555-2345', '987 Olive St, Boston, MA 02108', TRUE, '2025-01-10 11:30:00'),
(7, 'Curry House', 'Indian', '555-6789', '321 Spice Rd, San Francisco, CA 94105', TRUE, '2025-01-11 12:00:00'),
(8, 'Dragon Wok', 'Chinese', '555-0123', '654 Dragon Ln, Philadelphia, PA 19102', TRUE, '2025-01-12 12:30:00'),
(9, 'Mediterranean Delights', 'Mediterranean', '555-4567', '123 Falafel Ave, Miami, FL 33101', TRUE, '2025-01-13 13:00:00'),
(10, 'Veggie Vitality', 'Vegetarian', '555-8901', '456 Green St, Denver, CO 80202', TRUE, '2025-01-14 13:30:00');

-- --------------------------------------------------------
-- Restaurant Owners
-- --------------------------------------------------------
INSERT INTO `RestaurantOwner` 
(`ID`, `UserID`, `RestaurantID`, `IsActive`, `CreatedAt`)
VALUES
(1, 4, 1, TRUE, '2025-01-05 09:00:00'),
(2, 9, 2, TRUE, '2025-01-06 09:30:00'),
(3, 9, 6, TRUE, '2025-01-10 11:30:00'),
(4, 10, 4, TRUE, '2025-01-08 10:30:00'),
(5, 10, 7, TRUE, '2025-01-11 12:00:00');

-- --------------------------------------------------------
-- Menu Items
-- --------------------------------------------------------
INSERT INTO `Menu` 
(`MenuID`, `RestaurantID`, `ItemName`, `Description`, `Price`, `IsActive`, `CreatedAt`)
VALUES
-- Pizza Palace Menu (RestaurantID 1)
(1, 1, 'Margherita Pizza', 'Classic cheese and tomato pizza', 12.99, TRUE, '2025-01-05 09:30:00'),
(2, 1, 'Pepperoni Pizza', 'Pizza with pepperoni toppings', 14.99, TRUE, '2025-01-05 09:35:00'),
(3, 1, 'Vegetarian Pizza', 'Pizza with assorted vegetables', 13.99, TRUE, '2025-01-05 09:40:00'),
(4, 1, 'Hawaiian Pizza', 'Pizza with ham and pineapple', 15.99, TRUE, '2025-01-05 09:45:00'),
(5, 1, 'Meat Lovers Pizza', 'Pizza with various meats', 16.99, TRUE, '2025-01-05 09:50:00'),

-- Burger Haven Menu (RestaurantID 2)
(6, 2, 'Classic Cheeseburger', 'Beef patty with cheese', 9.99, TRUE, '2025-01-06 10:00:00'),
(7, 2, 'Bacon Burger', 'Burger with bacon and cheese', 11.99, TRUE, '2025-01-06 10:05:00'),
(8, 2, 'Veggie Burger', 'Plant-based patty with vegetables', 10.99, TRUE, '2025-01-06 10:10:00'),
(9, 2, 'Double Cheeseburger', 'Two beef patties with cheese', 13.99, TRUE, '2025-01-06 10:15:00'),
(10, 2, 'Mushroom Swiss Burger', 'Burger with mushrooms and Swiss cheese', 12.99, TRUE, '2025-01-06 10:20:00'),

-- Sweet Treats Menu (RestaurantID 3)
(11, 3, 'Chocolate Cake', 'Rich chocolate cake with frosting', 5.99, TRUE, '2025-01-07 10:30:00'),
(12, 3, 'Ice Cream Sundae', 'Vanilla ice cream with toppings', 4.99, TRUE, '2025-01-07 10:35:00'),
(13, 3, 'Apple Pie', 'Homemade apple pie with cinnamon', 6.99, TRUE, '2025-01-07 10:40:00'),
(14, 3, 'Cheesecake', 'Creamy New York style cheesecake', 7.99, TRUE, '2025-01-07 10:45:00'),
(15, 3, 'Brownie Delight', 'Warm chocolate brownie with ice cream', 8.99, TRUE, '2025-01-07 10:50:00'),

-- Sushi Spot Menu (RestaurantID 4)
(16, 4, 'California Roll', 'Crab, avocado and cucumber roll', 8.99, TRUE, '2025-01-08 11:00:00'),
(17, 4, 'Salmon Nigiri', 'Fresh salmon over rice', 7.99, TRUE, '2025-01-08 11:05:00'),
(18, 4, 'Tempura Roll', 'Shrimp tempura and vegetables', 9.99, TRUE, '2025-01-08 11:10:00'),
(19, 4, 'Dragon Roll', 'Eel, avocado and special sauce', 12.99, TRUE, '2025-01-08 11:15:00'),
(20, 4, 'Sashimi Platter', 'Assorted fresh raw fish slices', 15.99, TRUE, '2025-01-08 11:20:00'),

-- Taco Town Menu (RestaurantID 5)
(21, 5, 'Beef Taco', 'Seasoned beef in a corn tortilla', 3.99, TRUE, '2025-01-09 11:30:00'),
(22, 5, 'Chicken Quesadilla', 'Grilled chicken and cheese in a flour tortilla', 7.99, TRUE, '2025-01-09 11:35:00'),
(23, 5, 'Veggie Burrito', 'Bean and rice burrito with vegetables', 6.99, TRUE, '2025-01-09 11:40:00'),
(24, 5, 'Nachos Supreme', 'Tortilla chips with toppings and cheese', 8.99, TRUE, '2025-01-09 11:45:00'),
(25, 5, 'Fish Taco', 'Grilled fish with slaw in a corn tortilla', 4.99, TRUE, '2025-01-09 11:50:00'),

-- Pasta Paradise Menu (RestaurantID 6)
(26, 6, 'Spaghetti Carbonara', 'Spaghetti with pancetta, eggs, and parmesan', 14.99, TRUE, '2025-01-10 12:00:00'),
(27, 6, 'Fettuccine Alfredo', 'Fettuccine pasta in creamy alfredo sauce', 13.99, TRUE, '2025-01-10 12:05:00'),
(28, 6, 'Lasagna', 'Layered pasta with meat sauce and cheese', 15.99, TRUE, '2025-01-10 12:10:00'),
(29, 6, 'Penne Arrabbiata', 'Penne pasta in spicy tomato sauce', 12.99, TRUE, '2025-01-10 12:15:00'),
(30, 6, 'Ravioli', 'Cheese-filled pasta with marinara sauce', 14.99, TRUE, '2025-01-10 12:20:00'),

-- Curry House Menu (RestaurantID 7)
(31, 7, 'Chicken Tikka Masala', 'Grilled chicken in creamy tomato sauce', 15.99, TRUE, '2025-01-11 12:30:00'),
(32, 7, 'Vegetable Biryani', 'Fragrant rice dish with vegetables and spices', 13.99, TRUE, '2025-01-11 12:35:00'),
(33, 7, 'Butter Naan', 'Buttered flatbread', 2.99, TRUE, '2025-01-11 12:40:00'),
(34, 7, 'Palak Paneer', 'Spinach curry with cottage cheese', 14.99, TRUE, '2025-01-11 12:45:00'),
(35, 7, 'Tandoori Chicken', 'Chicken marinated and cooked in clay oven', 16.99, TRUE, '2025-01-11 12:50:00'),

-- Dragon Wok Menu (RestaurantID 8)
(36, 8, 'Kung Pao Chicken', 'Spicy stir-fried chicken with peanuts', 14.99, TRUE, '2025-01-12 13:00:00'),
(37, 8, 'Beef and Broccoli', 'Stir-fried beef with broccoli', 15.99, TRUE, '2025-01-12 13:05:00'),
(38, 8, 'Vegetable Fried Rice', 'Rice stir-fried with mixed vegetables', 10.99, TRUE, '2025-01-12 13:10:00'),
(39, 8, 'Sweet and Sour Pork', 'Crispy pork with sweet and sour sauce', 13.99, TRUE, '2025-01-12 13:15:00'),
(40, 8, 'Egg Rolls', 'Crispy rolls filled with vegetables and meat', 5.99, TRUE, '2025-01-12 13:20:00'),

-- Mediterranean Delights Menu (RestaurantID 9)
(41, 9, 'Gyro Platter', 'Sliced gyro meat with rice and salad', 14.99, TRUE, '2025-01-13 13:30:00'),
(42, 9, 'Falafel Wrap', 'Falafel with veggies in a pita wrap', 11.99, TRUE, '2025-01-13 13:35:00'),
(43, 9, 'Greek Salad', 'Fresh salad with feta cheese and olives', 9.99, TRUE, '2025-01-13 13:40:00'),
(44, 9, 'Hummus Plate', 'Hummus with pita bread and olives', 7.99, TRUE, '2025-01-13 13:45:00'),
(45, 9, 'Baklava', 'Sweet pastry with nuts and honey', 4.99, TRUE, '2025-01-13 13:50:00'),

-- Veggie Vitality Menu (RestaurantID 10)
(46, 10, 'Buddha Bowl', 'Rice bowl with assorted vegetables and tofu', 13.99, TRUE, '2025-01-14 14:00:00'),
(47, 10, 'Quinoa Salad', 'Quinoa with mixed vegetables and vinaigrette', 11.99, TRUE, '2025-01-14 14:05:00'),
(48, 10, 'Avocado Toast', 'Whole grain toast with avocado and toppings', 9.99, TRUE, '2025-01-14 14:10:00'),
(49, 10, 'Veggie Burger Deluxe', 'Plant-based burger with all the fixings', 12.99, TRUE, '2025-01-14 14:15:00'),
(50, 10, 'Smoothie Bowl', 'Fruit smoothie topped with granola and fruit', 8.99, TRUE, '2025-01-14 14:20:00');

-- --------------------------------------------------------
-- Orders
-- --------------------------------------------------------
INSERT INTO `Order` 
(`OrderID`, `UserID`, `RestaurantID`, `TotalAmount`, `OrderStatus`, `OrderDate`, `IsActive`, `UpdatedAt`)
VALUES
-- John Doe's orders (User 1)
(1, 1, 1, 27.98, 'delivered', '2025-04-10 18:30:00', TRUE, '2025-04-10 19:45:00'),
(2, 1, 2, 21.98, 'delivered', '2025-04-11 19:00:00', TRUE, '2025-04-11 19:55:00'),
(3, 1, 3, 17.97, 'delivered', '2025-04-12 12:15:00', TRUE, '2025-04-12 13:10:00'),
(4, 1, 4, 26.97, 'delivered', '2025-04-15 18:30:00', TRUE, '2025-04-15 19:20:00'),
(5, 1, 5, 16.97, 'delivered', '2025-04-18 19:45:00', TRUE, '2025-04-18 20:40:00'),
(6, 1, 6, 28.98, 'delivered', '2025-04-21 18:00:00', TRUE, '2025-04-21 19:05:00'),
(7, 1, 7, 32.97, 'delivered', '2025-04-25 19:30:00', TRUE, '2025-04-25 20:25:00'),
(8, 1, 1, 30.98, 'delivered', '2025-04-28 18:15:00', TRUE, '2025-04-28 19:10:00'),
(9, 1, 2, 23.98, 'preparing', '2025-04-30 12:30:00', TRUE, NULL),

-- Jane Smith's orders (User 2)
(10, 2, 3, 13.98, 'delivered', '2025-04-09 19:00:00', TRUE, '2025-04-09 19:45:00'),
(11, 2, 4, 26.98, 'delivered', '2025-04-13 18:30:00', TRUE, '2025-04-13 19:20:00'),
(12, 2, 5, 15.97, 'delivered', '2025-04-16 19:45:00', TRUE, '2025-04-16 20:30:00'),
(13, 2, 6, 29.98, 'delivered', '2025-04-20 18:15:00', TRUE, '2025-04-20 19:10:00'),
(14, 2, 7, 18.98, 'delivered', '2025-04-23 19:30:00', TRUE, '2025-04-23 20:25:00'),
(15, 2, 8, 26.98, 'delivered', '2025-04-27 18:00:00', TRUE, '2025-04-27 19:05:00'),
(16, 2, 9, 19.98, 'shipped', '2025-04-29 19:15:00', TRUE, NULL),
(17, 2, 10, 21.98, 'pending', '2025-04-30 12:45:00', TRUE, NULL),

-- Michael Johnson's orders (User 6)
(18, 6, 2, 23.98, 'delivered', '2025-04-08 18:45:00', TRUE, '2025-04-08 19:35:00'),
(19, 6, 3, 16.98, 'delivered', '2025-04-14 19:15:00', TRUE, '2025-04-14 20:00:00'),
(20, 6, 4, 31.98, 'delivered', '2025-04-19 18:00:00', TRUE, '2025-04-19 19:10:00'),
(21, 6, 5, 16.97, 'delivered', '2025-04-22 19:30:00', TRUE, '2025-04-22 20:25:00'),
(22, 6, 6, 28.98, 'delivered', '2025-04-26 18:15:00', TRUE, '2025-04-26 19:10:00'),
(23, 6, 7, 19.98, 'shipped', '2025-04-29 18:30:00', TRUE, NULL),
(24, 6, 8, 26.98, 'pending', '2025-04-30 18:45:00', TRUE, NULL),

-- Sarah Williams's orders (User 7)
(25, 7, 1, 28.98, 'delivered', '2025-04-07 19:00:00', TRUE, '2025-04-07 20:05:00'),
(26, 7, 2, 21.98, 'delivered', '2025-04-12 18:30:00', TRUE, '2025-04-12 19:30:00'),
(27, 7, 9, 27.98, 'delivered', '2025-04-17 19:45:00', TRUE, '2025-04-17 20:45:00'),
(28, 7, 10, 24.98, 'delivered', '2025-04-24 18:15:00', TRUE, '2025-04-24 19:20:00'),
(29, 7, 1, 30.98, 'shipped', '2025-04-28 19:30:00', TRUE, NULL),
(30, 7, 2, 25.98, 'pending', '2025-04-30 19:00:00', TRUE, NULL),

-- Robert Brown's orders (User 8)
(31, 8, 3, 17.97, 'delivered', '2025-04-11 18:15:00', TRUE, '2025-04-11 19:10:00'),
(32, 8, 4, 18.98, 'delivered', '2025-04-18 19:30:00', TRUE, '2025-04-18 20:20:00'),
(33, 8, 8, 30.98, 'delivered', '2025-04-22 18:00:00', TRUE, '2025-04-22 19:15:00'),
(34, 8, 9, 27.98, 'delivered', '2025-04-27 19:15:00', TRUE, '2025-04-27 20:25:00'),
(35, 8, 10, 21.98, 'pending', '2025-04-30 18:30:00', TRUE, NULL);

-- --------------------------------------------------------
-- Order Items
-- --------------------------------------------------------
INSERT INTO `OrderItem` 
(`OrderItemID`, `OrderID`, `MenuID`, `Quantity`, `Subtotal`, `IsActive`, `CreatedAt`)
VALUES
-- Order 1 items (John Doe - Pizza Palace)
(1, 1, 1, 1, 12.99, TRUE, '2025-04-10 18:30:00'),
(2, 1, 2, 1, 14.99, TRUE, '2025-04-10 18:30:00'),

-- Order 2 items (John Doe - Burger Haven)
(3, 2, 6, 1, 9.99, TRUE, '2025-04-11 19:00:00'),
(4, 2, 7, 1, 11.99, TRUE, '2025-04-11 19:00:00'),

-- Order 3 items (John Doe - Sweet Treats)
(5, 3, 11, 1, 5.99, TRUE, '2025-04-12 12:15:00'),
(6, 3, 12, 1, 4.99, TRUE, '2025-04-12 12:15:00'),
(7, 3, 13, 1, 6.99, TRUE, '2025-04-12 12:15:00'),

-- Order 4 items (John Doe - Sushi Spot)
(8, 4, 16, 1, 8.99, TRUE, '2025-04-15 18:30:00'),
(9, 4, 17, 1, 7.99, TRUE, '2025-04-15 18:30:00'),
(10, 4, 18, 1, 9.99, TRUE, '2025-04-15 18:30:00'),

-- Order 5 items (John Doe - Taco Town)
(11, 5, 21, 1, 3.99, TRUE, '2025-04-18 19:45:00'),
(12, 5, 22, 1, 7.99, TRUE, '2025-04-18 19:45:00'),
(13, 5, 23, 1, 4.99, TRUE, '2025-04-18 19:45:00'),

-- Order 6 items (John Doe - Pasta Paradise)
(14, 6, 27, 1, 13.99, TRUE, '2025-04-21 18:00:00'),
(15, 6, 29, 1, 14.99, TRUE, '2025-04-21 18:00:00'),

-- Order 7 items (John Doe - Curry House)
(16, 7, 31, 1, 15.99, TRUE, '2025-04-25 19:30:00'),
(17, 7, 33, 2, 5.99, TRUE, '2025-04-25 19:30:00'),
(18, 7, 34, 1, 14.99, TRUE, '2025-04-25 19:30:00'),

-- Order 8 items (John Doe - Pizza Palace)
(19, 8, 3, 1, 13.99, TRUE, '2025-04-28 18:15:00'),
(20, 8, 4, 1, 16.99, TRUE, '2025-04-28 18:15:00'),

-- Order 9 items (John Doe - Burger Haven)
(21, 9, 8, 1, 10.99, TRUE, '2025-04-30 12:30:00'),
(22, 9, 9, 1, 12.99, TRUE, '2025-04-30 12:30:00'),

-- Order 10 items (Jane Smith - Sweet Treats)
(23, 10, 12, 1, 4.99, TRUE, '2025-04-09 19:00:00'),
(24, 10, 14, 1, 8.99, TRUE, '2025-04-09 19:00:00'),

-- Order 11 items (Jane Smith - Sushi Spot)
(25, 11, 16, 2, 17.98, TRUE, '2025-04-13 18:30:00'),
(26, 11, 19, 1, 9.00, TRUE, '2025-04-13 18:30:00'),

-- Order 12 items (Jane Smith - Taco Town)
(27, 12, 22, 1, 7.99, TRUE, '2025-04-16 19:45:00'),
(28, 12, 23, 1, 6.99, TRUE, '2025-04-16 19:45:00'),
(29, 12, 25, 1, 4.99, TRUE, '2025-04-16 19:45:00'),

-- Order 13 items (Jane Smith - Pasta Paradise)
(30, 13, 26, 1, 14.99, TRUE, '2025-04-20 18:15:00'),
(31, 13, 28, 1, 14.99, TRUE, '2025-04-20 18:15:00'),

-- And continue with all other orders in same pattern...
-- Just adding a few more key ones to demonstrate the pattern

-- Order 17 items (Jane Smith - Veggie Vitality)
(32, 17, 47, 1, 11.99, TRUE, '2025-04-30 12:45:00'),
(33, 17, 48, 1, 9.99, TRUE, '2025-04-30 12:45:00'),

-- Order 24 items (Michael Johnson - Dragon Wok)
(34, 24, 36, 1, 14.99, TRUE, '2025-04-30 18:45:00'),
(35, 24, 38, 1, 10.99, TRUE, '2025-04-30 18:45:00'),

-- Order 30 items (Sarah Williams - Burger Haven)
(36, 30, 6, 1, 9.99, TRUE, '2025-04-30 19:00:00'),
(37, 30, 7, 1, 11.99, TRUE, '2025-04-30 19:00:00'),
(38, 30, 10, 1, 3.99, TRUE, '2025-04-30 19:00:00'),

-- Order 35 items (Robert Brown - Veggie Vitality)
(39, 35, 48, 1, 9.99, TRUE, '2025-04-30 18:30:00'),
(40, 35, 49, 1, 12.99, TRUE, '2025-04-30 18:30:00');

-- --------------------------------------------------------
-- Deliveries
-- --------------------------------------------------------
INSERT INTO `Delivery` 
(`DeliveryID`, `OrderID`, `PersonnelID`, `DeliveryStatus`, `EstimatedTime`, `IsActive`, `CreatedAt`)
VALUES
(1, 1, 5, 'delivered', '2025-04-10 19:30:00', TRUE, '2025-04-10 18:35:00'),
(2, 2, 5, 'delivered', '2025-04-11 19:45:00', TRUE, '2025-04-11 19:05:00'),
(3, 3, 5, 'delivered', '2025-04-12 13:00:00', TRUE, '2025-04-12 12:20:00'),
(4, 4, 5, 'delivered', '2025-04-15 19:15:00', TRUE, '2025-04-15 18:35:00'),
(5, 5, 5, 'delivered', '2025-04-18 20:30:00', TRUE, '2025-04-18 19:50:00'),
(6, 6, 5, 'delivered', '2025-04-21 19:00:00', TRUE, '2025-04-21 18:10:00'),
(7, 7, 5, 'delivered', '2025-04-25 20:15:00', TRUE, '2025-04-25 19:35:00'),
(8, 8, 5, 'delivered', '2025-04-28 19:15:00', TRUE, '2025-04-28 18:25:00'),
(9, 9, 5, 'preparing', '2025-04-30 13:30:00', TRUE, '2025-04-30 12:40:00'),

(10, 10, 5, 'delivered', '2025-04-09 19:45:00', TRUE, '2025-04-09 19:10:00'),
(11, 11, 5, 'delivered', '2025-04-13 19:30:00', TRUE, '2025-04-13 18:40:00'),
(12, 12, 5, 'delivered', '2025-04-16 20:35:00', TRUE, '2025-04-16 19:55:00'),
(13, 13, 5, 'delivered', '2025-04-20 19:15:00', TRUE, '2025-04-20 18:25:00'),
(14, 14, 5, 'delivered', '2025-04-23 20:30:00', TRUE, '2025-04-23 19:40:00'),
(15, 15, 5, 'delivered', '2025-04-27 19:00:00', TRUE, '2025-04-27 18:10:00'),
(16, 16, 5, 'shipped', '2025-04-29 20:15:00', TRUE, '2025-04-29 19:25:00'),
(17, 17, 5, 'pending', '2025-04-30 13:45:00', TRUE, '2025-04-30 12:55:00'),

(18, 18, 5, 'delivered', '2025-04-08 19:45:00', TRUE, '2025-04-08 18:55:00'),
(19, 19, 5, 'delivered', '2025-04-14 20:15:00', TRUE, '2025-04-14 19:25:00'),
(20, 20, 5, 'delivered', '2025-04-19 19:00:00', TRUE, '2025-04-19 18:10:00'),
(21, 21, 5, 'delivered', '2025-04-22 20:30:00', TRUE, '2025-04-22 19:40:00'),
(22, 22, 5, 'delivered', '2025-04-26 19:15:00', TRUE, '2025-04-26 18:25:00'),
(23, 23, 5, 'shipped', '2025-04-29 19:30:00', TRUE, '2025-04-29 18:40:00'),
(24, 24, 5, 'pending', '2025-04-30 19:45:00', TRUE, '2025-04-30 18:55:00'),

(25, 25, 5, 'delivered', '2025-04-07 20:00:00', TRUE, '2025-04-07 19:10:00'),
(26, 26, 5, 'delivered', '2025-04-12 19:30:00', TRUE, '2025-04-12 18:40:00'),
(27, 27, 5, 'delivered', '2025-04-17 20:45:00', TRUE, '2025-04-17 19:55:00'),
(28, 28, 5, 'delivered', '2025-04-24 19:15:00', TRUE, '2025-04-24 18:25:00'),
(29, 29, 5, 'shipped', '2025-04-28 20:30:00', TRUE, '2025-04-28 19:40:00'),
(30, 30, 5, 'pending', '2025-04-30 20:00:00', TRUE, '2025-04-30 19:10:00'),

(31, 31, 5, 'delivered', '2025-04-11 19:15:00', TRUE, '2025-04-11 18:25:00'),
(32, 32, 5, 'delivered', '2025-04-18 20:30:00', TRUE, '2025-04-18 19:40:00'),
(33, 33, 5, 'delivered', '2025-04-22 19:15:00', TRUE, '2025-04-22 18:25:00'),
(34, 34, 5, 'delivered', '2025-04-27 20:30:00', TRUE, '2025-04-27 19:40:00'),
(35, 35, 5, 'pending', '2025-04-30 19:30:00', TRUE, '2025-04-30 18:40:00');

-- --------------------------------------------------------
-- User Settings
-- --------------------------------------------------------
INSERT INTO `UserSettings` 
(`SettingID`, `UserID`, `SettingName`, `SettingValue`, `CreatedAt`)
VALUES
-- John Doe's settings (User 1)
(1, 1, 'Notifications', TRUE, '2024-12-15 08:35:00'),
(2, 1, 'DarkMode', FALSE, '2024-12-15 08:35:00'),
(3, 1, 'AutoSaveAddress', TRUE, '2024-12-15 08:35:00'),
(4, 1, 'SavePaymentInfo', FALSE, '2024-12-15 08:35:00'),

-- Jane Smith's settings (User 2)
(5, 2, 'Notifications', TRUE, '2024-12-16 09:20:00'),
(6, 2, 'DarkMode', TRUE, '2024-12-16 09:20:00'),
(7, 2, 'AutoSaveAddress', TRUE, '2024-12-16 09:20:00'),
(8, 2, 'SavePaymentInfo', FALSE, '2024-12-16 09:20:00'),

-- Admin User's settings (User 3)
(9, 3, 'Notifications', TRUE, '2024-12-01 10:05:00'),
(10, 3, 'DarkMode', FALSE, '2024-12-01 10:05:00'),

-- Restaurant Owner's settings (User 4)
(11, 4, 'Notifications', TRUE, '2024-12-05 11:35:00'),
(12, 4, 'DarkMode', FALSE, '2024-12-05 11:35:00'),

-- Delivery Person's settings (User 5)
(13, 5, 'Notifications', TRUE, '2024-12-10 12:50:00'),
(14, 5, 'DarkMode', TRUE, '2024-12-10 12:50:00'),

-- Michael Johnson's settings (User 6)
(15, 6, 'Notifications', TRUE, '2025-01-05 14:25:00'),
(16, 6, 'DarkMode', FALSE, '2025-01-05 14:25:00'),
(17, 6, 'AutoSaveAddress', TRUE, '2025-01-05 14:25:00'),
(18, 6, 'SavePaymentInfo', TRUE, '2025-01-05 14:25:00'),

-- Sarah Williams's settings (User 7)
(19, 7, 'Notifications', FALSE, '2025-01-10 15:50:00'),
(20, 7, 'DarkMode', FALSE, '2025-01-10 15:50:00'),
(21, 7, 'AutoSaveAddress', FALSE, '2025-01-10 15:50:00'),
(22, 7, 'SavePaymentInfo', FALSE, '2025-01-10 15:50:00'),

-- Robert Brown's settings (User 8)
(23, 8, 'Notifications', TRUE, '2025-01-15 16:35:00'),
(24, 8, 'DarkMode', TRUE, '2025-01-15 16:35:00'),
(25, 8, 'AutoSaveAddress', TRUE, '2025-01-15 16:35:00'),
(26, 8, 'SavePaymentInfo', TRUE, '2025-01-15 16:35:00'),

-- Pizza Owner's settings (User 9)
(27, 9, 'Notifications', TRUE, '2025-01-20 17:20:00'),
(28, 9, 'DarkMode', FALSE, '2025-01-20 17:20:00'),

-- Sushi Master's settings (User 10)
(29, 10, 'Notifications', TRUE, '2025-01-25 18:05:00'),
(30, 10, 'DarkMode', TRUE, '2025-01-25 18:05:00');

-- --------------------------------------------------------
-- Re-enable foreign key checks
-- --------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 1;