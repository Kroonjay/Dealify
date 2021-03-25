DELIMITER //
CREATE PROCEDURE ReadCraigslistSiteIdsByCountry (
    IN country_param NVARCHAR(90)
) BEGIN
SELECT site_id FROM CraigslistSites WHERE country LIKE country_param FOR UPDATE;
UPDATE CraigslistSites SET last_searched_at = CURRENT_TIMESTAMP;
END //