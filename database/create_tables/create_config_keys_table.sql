CREATE TABLE ConfigKeys (
    key_id INT AUTO_INCREMENT PRIMARY KEY,
    key_name NVARCHAR(90) NOT NULL UNIQUE,
    config_value JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME NOT NULL DEFAULT '2000-04-20 07:10:00',
    last_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);