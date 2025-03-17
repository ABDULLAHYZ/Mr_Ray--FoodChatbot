CREATE DATABASE IF NOT EXISTS `Mr_Ray` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */;
USE `Mr_Ray`;

-- Table for food items
DROP TABLE IF EXISTS `food_items`;
CREATE TABLE `food_items` (
  `item_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Inserting specified menu items
INSERT INTO `food_items` (name, price) VALUES
('Pizza', 8.00),
('Samosa', 5.00),
('Gol Gappay', 6.00),
('Shawarma', 7.00),
('Doodh Patti Chai', 3.00),
('Karak Chai', 4.00),
('Kashmiri Chai (Pink Tea)', 5.50),
('Adrak Chai', 4.50),
('Peshawari Kahwa', 5.00),
('Green Tea (Sabz Chai)', 4.00),
('Mango Shake', 6.00),
('Banana Shake', 5.50),
('Lemonade (Shikanjabeen)', 4.50),
('Sugarcane Juice (Ganne Ka Juice)', 5.50),
('Strawberry Smoothie', 6.50);

-- Table for orders
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `order_id` INT AUTO_INCREMENT PRIMARY KEY,
  `item_id` INT NOT NULL,
  `quantity` INT DEFAULT 1,
  `total_price` DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (`item_id`) REFERENCES `food_items`(`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table for order tracking
DROP TABLE IF EXISTS `order_tracking`;
CREATE TABLE `order_tracking` (
  `order_id` INT NOT NULL,
  `status` VARCHAR(255) DEFAULT 'pending',
  PRIMARY KEY (`order_id`),
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table for reservations
DROP TABLE IF EXISTS `reservations`;
CREATE TABLE `reservations` (
  `reservation_id` INT AUTO_INCREMENT PRIMARY KEY,
  `customer_name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `reservation_date` DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table for FAQs
DROP TABLE IF EXISTS `faqs`;
CREATE TABLE `faqs` (
  `faq_id` INT AUTO_INCREMENT PRIMARY KEY,
  `question` TEXT NOT NULL,
  `answer` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table for chatbot conversations
DROP TABLE IF EXISTS `conversations`;
CREATE TABLE `conversations` (
  `conversation_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_message` TEXT NOT NULL,
  `bot_response` TEXT NOT NULL,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- User Data
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (name, email, phone) VALUES
('Muhammad Abdullah', 'muhammadabdullah14127@gmail.com', '+92 3339846454');
