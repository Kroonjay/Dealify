CREATE TABLE DealifySearches(
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    search_status INT NOT NULL DEFAULT 4,
    search_name NVARCHAR(90) NOT NULL UNIQUE,
    sources JSON,
    search_config JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);