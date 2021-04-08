DELIMITER //
CREATE PROCEDURE ReadCraigslistSiteIdsByCity (
    IN city_param NVARCHAR(90)
) BEGIN
SELECT site_id FROM CraigslistSites WHERE city LIKE city_param;
END //