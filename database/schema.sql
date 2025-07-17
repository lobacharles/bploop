-- Create the database
CREATE DATABASE IF NOT EXISTS pasig_business_analytics;
USE pasig_business_analytics;

-- Drop the old businesses table if it exists
DROP TABLE IF EXISTS businesses;

-- Create the new businesses table for simple business listing with map pins
CREATE TABLE IF NOT EXISTS businesses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    business_trade_name VARCHAR(255) NOT NULL,
    business_address VARCHAR(255) NOT NULL,
    barangay VARCHAR(100) NOT NULL,
    line_of_business VARCHAR(255) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Business categories table
CREATE TABLE IF NOT EXISTS business_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business metrics table (for analytics)
CREATE TABLE IF NOT EXISTS business_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    business_id INT NOT NULL,
    metric_date DATE NOT NULL,
    revenue DECIMAL(15, 2),
    employee_count INT,
    customer_count INT,
    FOREIGN KEY (business_id) REFERENCES businesses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business predictions table
CREATE TABLE IF NOT EXISTS business_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    business_id INT NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_revenue DECIMAL(15, 2),
    confidence_score DECIMAL(5, 2),
    prediction_model VARCHAR(50) NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_business_location ON businesses(latitude, longitude);
CREATE INDEX idx_barangay ON businesses(barangay);
CREATE INDEX idx_metrics_date ON business_metrics(metric_date);
CREATE INDEX idx_predictions_date ON business_predictions(prediction_date); 