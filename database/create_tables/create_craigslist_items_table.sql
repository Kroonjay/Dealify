CREATE TABLE CraigslistItems (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name NVARCHAR(90),
    price INT,
    search_id INT,
    source_url NVARCHAR(250),
    tags JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_id VARCHAR(50) NOT NULL UNIQUE,
    posted_at DATETIME,
    is_deleted BOOLEAN,
    has_image BOOLEAN,
    last_updated DATETIME,
    repost_of NVARCHAR(255),
    item_location NVARCHAR(90),
    CONSTRAINT fkSearchId_clitem
    FOREIGN KEY (search_id)
        REFERENCES DealifySearches(search_id)
        ON DELETE SET NULL
)