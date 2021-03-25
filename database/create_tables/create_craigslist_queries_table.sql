CREATE TABLE CraigslistQueries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    query_status INT NOT NULL DEFAULT 0,
    search_id INT,
    query NVARCHAR(250) NOT NULL,
    interval_mins INT NOT NULL DEFAULT 1440,
    site_id INT NOT NULL,
    area NVARCHAR(20),
    category NVARCHAR(20),
    search_titles BOOLEAN NOT NULL DEFAULT FALSE,
    require_image BOOLEAN NOT NULL DEFAULT FALSE,
    posted_today BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_execution_at DATETIME NOT NULL DEFAULT '2000-04-20 07:10:00',
    next_execution_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fkSearchId
    FOREIGN KEY (search_id)
        REFERENCES DealifySearches(search_id)
        ON DELETE CASCADE,
    CONSTRAINT fkSiteId
    FOREIGN KEY (site_id)
        REFERENCES CraigslistSites(site_id)
        ON DELETE CASCADE
);