CREATE TABLE CraigslistSites (
    site_id INT AUTO_INCREMENT PRIMARY KEY,
    subdomain NVARCHAR(90) NOT NULL UNIQUE,
    site_name NVARCHAR(90) NOT NULL,
    site_url NVARCHAR(250) NOT NULL,
    city NVARCHAR(90),
    state_code NVARCHAR(90),
    country NVARCHAR(90),
    latitude FLOAT(10,6),
    longitude FLOAT(10,6),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_searched_at DATETIME NOT NULL DEFAULT '2000-04-20 07:10:00',
    last_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    areas JSON
);