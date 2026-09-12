CREATE DATABASE solar_optimizer;
USE solar_optimizer;

CREATE TABLE sensor_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    light_intensity INT,
    temperature FLOAT,
    dust_level FLOAT,
    actual_power FLOAT,
    predicted_power FLOAT, -- Calculated by your AI
    efficiency_gap FLOAT   -- Predicted - Actual
);
