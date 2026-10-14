-- =====================================================
-- MboaLift Database Schema
-- Database: douala_rideshare
-- Designed for Douala Urban Mobility Coding Challenge
-- =====================================================

CREATE DATABASE IF NOT EXISTS douala_rideshare
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE douala_rideshare;

-- =====================================================
-- USERS TABLE
-- Stores registered riders (passengers)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- DRIVERS TABLE
-- Stores registered drivers (Bendskin Moto, Yellow Cabs, Comfort)
-- =====================================================
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    vehicle_info VARCHAR(100) DEFAULT NULL,
    vehicle_type ENUM('bendskin', 'taxi', 'comfort') NOT NULL DEFAULT 'taxi',
    -- Current area in Douala (driver selects a known location e.g. Akwa, Ndokoti)
    current_location VARCHAR(50) DEFAULT NULL,
    -- free = available for rides, busy = on a trip
    availability ENUM('free', 'busy') NOT NULL DEFAULT 'free',
    status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- ADMINS TABLE
-- Stores admin accounts
-- =====================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- RIDES TABLE
-- Stores ride requests
-- vehicle_type: bendskin (moto), taxi (yellow cab), comfort (private car)
-- =====================================================
CREATE TABLE IF NOT EXISTS rides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    driver_id INT DEFAULT NULL,
    pickup VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    passengers INT NOT NULL DEFAULT 1,
    vehicle_type ENUM('bendskin', 'taxi', 'comfort') NOT NULL DEFAULT 'taxi',
    fare DECIMAL(10, 2) NOT NULL,
    status ENUM('PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
        NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- RIDE_PARTICIPANTS TABLE
-- Stores users who join a shared ride
-- =====================================================
CREATE TABLE IF NOT EXISTS ride_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ride_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_participant (ride_id, user_id),
    FOREIGN KEY (ride_id) REFERENCES rides(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- PAYMENTS TABLE
-- Stores Mobile Money (MTN MoMo & Orange Money) transactions
-- =====================================================
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ride_id INT NOT NULL,
    user_id INT NOT NULL,
    transaction_reference VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    operator VARCHAR(20) NOT NULL DEFAULT 'MOMO',
    status ENUM('PENDING', 'SUCCESSFUL', 'FAILED', 'CANCELLED')
        NOT NULL DEFAULT 'PENDING',
    gateway_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ride_id) REFERENCES rides(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- RATINGS TABLE
-- Stores ride ratings and comments (1 to 5 stars)
-- =====================================================
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ride_id INT NOT NULL,
    user_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_rating (ride_id, user_id),
    FOREIGN KEY (ride_id) REFERENCES rides(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- DEFAULT ADMIN ACCOUNT
-- The Flask app creates the admin automatically on first run:
--   Username: admin
--   Password: admin123
-- (see init_admin() in app.py)
-- =====================================================
