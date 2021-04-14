DELIMITER //
CREATE PROCEDURE ReadCraigslistSiteById(
    IN site_id_param INT
)
BEGIN
SELECT * FROM CraigslistSites WHERE site_id = site_id_param LIMIT 1;
END //